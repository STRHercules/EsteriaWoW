from __future__ import annotations

import json
import math
import re
import shutil
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageStat

ROOT = Path(r"G:\New Folder (2)")
DARKFALLEN = ROOT / "Character" / "Darkfallen"
HD = ROOT / "Character" / "BloodElf2"
OUT_ROOT = ROOT / "DarkfallenAttempts"
UPSCALED = OUT_ROOT / "Upscaled"
COLORED = OUT_ROOT / "Colored"


def blp_meta(path: Path) -> dict:
    data = path.read_bytes()[:20]
    if len(data) < 20 or data[:4] != b"BLP2":
        return {"magic": data[:4].decode("ascii", errors="replace")}
    return {
        "magic": "BLP2",
        "type": struct.unpack_from("<I", data, 4)[0],
        "encoding": data[8],
        "alpha_depth": data[9],
        "alpha_encoding": data[10],
        "has_mips": data[11],
        "width": struct.unpack_from("<I", data, 12)[0],
        "height": struct.unpack_from("<I", data, 16)[0],
    }


def _pack_alpha(alpha: np.ndarray, depth: int) -> bytes:
    flat = alpha.astype(np.uint8).ravel()
    if depth == 0:
        return b""
    if depth == 8:
        return flat.tobytes()
    if depth == 4:
        vals = ((flat.astype(np.uint16) * 15 + 127) // 255).astype(np.uint8)
        if len(vals) % 2:
            vals = np.append(vals, 0)
        out = np.empty(len(vals) // 2, dtype=np.uint8)
        out[:] = vals[0::2] | (vals[1::2] << 4)
        return out.tobytes()
    if depth == 1:
        vals = (flat >= 128).astype(np.uint8)
        pad = (-len(vals)) % 8
        if pad:
            vals = np.append(vals, np.zeros(pad, dtype=np.uint8))
        out = np.zeros(len(vals) // 8, dtype=np.uint8)
        for bit in range(8):
            out |= vals[bit::8] << bit
        return out.tobytes()
    raise ValueError(f"Unsupported alpha depth: {depth}")


def save_blp2_paletted(image: Image.Image, path: Path, alpha_depth: int = 0) -> None:
    """Write a client-friendly paletted BLP2 with a full mip chain."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if alpha_depth not in (0, 1, 4, 8):
        alpha_depth = 8 if "A" in image.getbands() else 0

    rgba = image.convert("RGBA")
    rgb = rgba.convert("RGB")

    # One palette is shared by all mip levels in a paletted BLP2.
    quant = rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    palette = quant.getpalette() or []
    palette = palette[: 256 * 3] + [0] * max(0, 256 * 3 - len(palette))

    palette_bytes = bytearray()
    for i in range(256):
        r, g, b = palette[i * 3 : i * 3 + 3]
        palette_bytes.extend((b, g, r, 255))

    mip_payloads: list[bytes] = []
    w, h = rgba.size
    current = rgba
    for _ in range(16):
        current_rgb = current.convert("RGB")
        current_p = current_rgb.quantize(palette=quant, dither=Image.Dither.NONE)
        indices = current_p.tobytes()
        alpha = _pack_alpha(np.asarray(current.getchannel("A")), alpha_depth)
        mip_payloads.append(indices + alpha)
        if current.size == (1, 1):
            break
        nw = max(1, current.width // 2)
        nh = max(1, current.height // 2)
        current = current.resize((nw, nh), Image.Resampling.LANCZOS)

    header_size = 148 + 1024
    offsets = [0] * 16
    sizes = [0] * 16
    cursor = header_size
    for i, payload in enumerate(mip_payloads):
        offsets[i] = cursor
        sizes[i] = len(payload)
        cursor += len(payload)

    out = bytearray()
    out.extend(b"BLP2")
    out.extend(struct.pack("<I", 1))
    out.extend(bytes((1, alpha_depth, 8, 1)))
    out.extend(struct.pack("<II", w, h))
    out.extend(struct.pack("<16I", *offsets))
    out.extend(struct.pack("<16I", *sizes))
    out.extend(palette_bytes)
    for payload in mip_payloads:
        out.extend(payload)

    path.write_bytes(out)


def mean_rgb(path: Path) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    return np.asarray(ImageStat.Stat(im).mean, dtype=np.float32)


def alpha_depth_for_output(target: Path, image: Image.Image) -> int:
    meta = blp_meta(target)
    depth = int(meta.get("alpha_depth", 0))
    if depth in (0, 1, 4, 8):
        return depth
    return 8 if "A" in image.getbands() else 0


def fuse_darkfallen_detail(dark_path: Path, hd_path: Path) -> Image.Image:
    """Preserve Darkfallen art/color while borrowing high-frequency HD Blood Elf detail."""
    dark = Image.open(dark_path).convert("RGBA")
    hd = Image.open(hd_path).convert("RGBA")
    if dark.size != hd.size:
        dark = dark.resize(hd.size, Image.Resampling.LANCZOS)

    d = np.asarray(dark.convert("RGB"), dtype=np.float32)
    h = np.asarray(hd.convert("RGB"), dtype=np.float32)
    h_blur = np.asarray(hd.convert("RGB").filter(ImageFilter.GaussianBlur(radius=1.25)), dtype=np.float32)

    # Luminance-only detail transfer minimizes Blood Elf color contamination.
    delta = h - h_blur
    detail = delta[..., 0] * 0.2126 + delta[..., 1] * 0.7152 + delta[..., 2] * 0.0722
    out = d + detail[..., None] * 0.72

    # Mild local contrast/detail recovery without making compression noise dominant.
    center = np.mean(out, axis=(0, 1), keepdims=True)
    out = center + (out - center) * 1.035
    out = np.clip(out, 0, 255).astype(np.uint8)

    result = Image.fromarray(out, "RGB").convert("RGBA")
    # Exact Darkfallen alpha wins where it exists; otherwise preserve the HD target alpha.
    dark_alpha = dark.getchannel("A")
    if dark_alpha.getextrema() != (255, 255):
        result.putalpha(dark_alpha)
    else:
        result.putalpha(hd.getchannel("A"))
    return result


def apply_channel_scale(image: Image.Image, factors: np.ndarray, strength: float = 1.0) -> Image.Image:
    rgba = image.convert("RGBA")
    arr = np.asarray(rgba.convert("RGB"), dtype=np.float32)
    scaled = arr * factors.reshape((1, 1, 3))
    if strength < 1.0:
        scaled = arr * (1.0 - strength) + scaled * strength
    scaled = np.clip(scaled, 0, 255).astype(np.uint8)
    out = Image.fromarray(scaled, "RGB").convert("RGBA")
    out.putalpha(rgba.getchannel("A"))
    return out


def is_skin_texture(name: str) -> bool:
    n = name.lower()
    return "faceupper" in n or "facelower" in n or "skin" in n


def skin_index(name: str) -> int | None:
    m = re.search(r"_(\d{2,3})(?:_extra)?\.blp$", name, flags=re.IGNORECASE)
    return int(m.group(1)) if m else None


def build_factors() -> dict[str, dict[int, np.ndarray]]:
    refs: dict[str, tuple[str, str]] = {
        "female": (
            "DarkfallenFemaleNakedTorsoSkin00_{:02d}.blp",
            "BLOODELFFEMALENAKEDTORSOSKIN00_{:02d}.blp",
        ),
        "male": (
            "DarkfallenMaleSkin00_{:02d}.blp",
            "BLOODELFMALESKIN00_{:02d}.blp",
        ),
    }
    out: dict[str, dict[int, np.ndarray]] = {"female": {}, "male": {}}
    for sex, (dark_pat, hd_pat) in refs.items():
        dark_dir = DARKFALLEN / sex.capitalize()
        hd_dir = HD / sex
        for i in range(6):
            target = mean_rgb(dark_dir / dark_pat.format(i))
            source = mean_rgb(hd_dir / hd_pat.format(i))
            out[sex][i] = np.clip(target / np.maximum(source, 1.0), 0.25, 2.25)
    return out


def lookup_casefold(directory: Path) -> dict[str, Path]:
    return {p.name.casefold(): p for p in directory.iterdir() if p.is_file()}


def copy_hd_tree(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(HD, dest)


def recolor_eye_glow_red(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    lum = np.asarray(ImageOps.grayscale(rgba.convert("RGB")), dtype=np.float32)
    out = np.zeros((rgba.height, rgba.width, 3), dtype=np.float32)
    out[..., 0] = np.clip(lum * 1.65 + 18.0, 0, 255)
    out[..., 1] = np.clip(lum * 0.18, 0, 255)
    out[..., 2] = np.clip(lum * 0.22, 0, 255)
    result = Image.fromarray(out.astype(np.uint8), "RGB").convert("RGBA")
    result.putalpha(rgba.getchannel("A"))
    return result


def replace_eye_glows(dest: Path) -> list[str]:
    """Use the HD Blood Elf glow masks, recolored red; retain legacy Darkfallen glows as references."""
    changed: list[str] = []
    targets = [
        (HD / "female" / "BloodElfFemaleEyeGlowGreen.blp", dest / "female" / "BloodElfFemaleEyeGlowGreen.blp"),
        (HD / "female" / "DEATHKNIGHTEYEGLOW.BLP", dest / "female" / "DEATHKNIGHTEYEGLOW.BLP"),
        (HD / "male" / "BloodElfFemaleEyeGlowGreen.blp", dest / "male" / "BloodElfFemaleEyeGlowGreen.blp"),
        (HD / "male" / "deathKnightEyeGlow.blp", dest / "male" / "deathKnightEyeGlow.blp"),
    ]
    for src, target in targets:
        if not src.exists() or not target.exists():
            continue
        result = recolor_eye_glow_red(Image.open(src))
        save_blp2_paletted(result, target, alpha_depth=8)
        changed.append(str(target.relative_to(dest)))

    legacy_dir = dest / "_LegacyDarkfallenGlowSources"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    for sex in ("Female", "Male"):
        for src in (DARKFALLEN / sex).glob("*Glow.blp"):
            shutil.copy2(src, legacy_dir / f"{sex}_{src.name}")
    return changed


def create_darkfallen_aliases(dest: Path) -> list[str]:
    """Create HD model/skin/anim filenames that follow the legacy Darkfallen basename convention."""
    created: list[str] = []
    for sex in ("female", "male"):
        directory = dest / sex
        old_prefix = f"bloodelf{sex}2"
        new_prefix = f"Darkfallen{sex.capitalize()}"
        for src in list(directory.iterdir()):
            lower = src.name.lower()
            if not lower.startswith(old_prefix):
                continue
            suffix = src.name[len(old_prefix):]
            target = directory / f"{new_prefix}{suffix}"
            shutil.copy2(src, target)
            created.append(str(target.relative_to(dest)))
    return created


def do_upscaled(factors: dict[str, dict[int, np.ndarray]]) -> dict:
    copy_hd_tree(UPSCALED)
    report: dict = {
        "strategy": "HD Blood Elf geometry/animations + Darkfallen texture fusion with HD detail transfer",
        "fused": [],
        "unmapped_darkfallen": [],
        "fallback_recolored_hd": [],
    }

    for sex in ("female", "male"):
        dark_dir = DARKFALLEN / sex.capitalize()
        hd_dir = HD / sex
        out_dir = UPSCALED / sex
        hd_lookup = lookup_casefold(hd_dir)

        for src in dark_dir.glob("*.blp"):
            if "glow" in src.name.casefold():
                continue
            target_name = src.name.replace(f"Darkfallen{sex.capitalize()}", f"BloodElf{sex.capitalize()}")
            hd_src = hd_lookup.get(target_name.casefold())
            if hd_src is None:
                report["unmapped_darkfallen"].append(str(src.relative_to(DARKFALLEN)))
                continue
            out_target = out_dir / hd_src.name
            result = fuse_darkfallen_detail(src, hd_src)
            save_blp2_paletted(result, out_target, alpha_depth_for_output(hd_src, result))
            report["fused"].append(str(out_target.relative_to(UPSCALED)))

        # HD-only skin layers should not flash back to orange Blood Elf skin if referenced.
        exact_names = {
            p.name.replace(f"Darkfallen{sex.capitalize()}", f"BloodElf{sex.capitalize()}").casefold()
            for p in dark_dir.glob("*.blp")
            if "glow" not in p.name.casefold()
        }
        avg_factor = np.mean(np.stack([factors[sex][i] for i in range(6)]), axis=0)
        for hd_src in hd_dir.glob("*.blp"):
            if not is_skin_texture(hd_src.name) or hd_src.name.casefold() in exact_names:
                continue
            out_target = out_dir / hd_src.name
            im = Image.open(hd_src)
            idx = skin_index(hd_src.name)
            factor = factors[sex].get(idx, avg_factor)
            result = apply_channel_scale(im, factor, strength=0.88)
            save_blp2_paletted(result, out_target, alpha_depth_for_output(hd_src, result))
            report["fallback_recolored_hd"].append(str(out_target.relative_to(UPSCALED)))

    report["eye_glows_replaced"] = replace_eye_glows(UPSCALED)
    report["darkfallen_hd_aliases"] = create_darkfallen_aliases(UPSCALED)
    return report


def do_colored(factors: dict[str, dict[int, np.ndarray]]) -> dict:
    copy_hd_tree(COLORED)
    report: dict = {
        "strategy": "Unmodified WoD Blood Elf HD geometry/animations with Darkfallen-derived skin palette shift",
        "recolored": [],
    }

    for sex in ("female", "male"):
        hd_dir = HD / sex
        out_dir = COLORED / sex
        avg_factor = np.mean(np.stack([factors[sex][i] for i in range(6)]), axis=0)

        for hd_src in hd_dir.glob("*.blp"):
            if not is_skin_texture(hd_src.name):
                continue
            out_target = out_dir / hd_src.name
            im = Image.open(hd_src)
            idx = skin_index(hd_src.name)
            factor = factors[sex].get(idx, avg_factor)
            result = apply_channel_scale(im, factor, strength=1.0)
            save_blp2_paletted(result, out_target, alpha_depth_for_output(hd_src, result))
            report["recolored"].append(str(out_target.relative_to(COLORED)))

    report["eye_glows_replaced"] = replace_eye_glows(COLORED)
    report["darkfallen_hd_aliases"] = create_darkfallen_aliases(COLORED)
    return report


def verify_tree(root: Path) -> dict:
    issues: list[str] = []
    legacy_refs: list[str] = []
    checked = 0
    for path in root.rglob("*.blp"):
        if "_LegacyDarkfallenGlowSources" in path.parts:
            legacy_refs.append(str(path.relative_to(root)))
            continue
        try:
            with Image.open(path) as im:
                im.load()
                if im.width <= 0 or im.height <= 0:
                    issues.append(f"invalid dimensions: {path}")
        except Exception as exc:
            issues.append(f"{path}: {exc}")
        checked += 1
    return {
        "files": sum(1 for p in root.rglob("*") if p.is_file()),
        "blps_checked": checked,
        "legacy_blp_references_not_validated": legacy_refs,
        "blp_issues": issues,
    }


def write_notes(root: Path, report: dict, verification: dict) -> None:
    note = [
        "Darkfallen HD experiment",
        "========================",
        "",
        report["strategy"],
        "",
        "Important:",
        "- The legacy Darkfallen and WoD Blood Elf texture atlases are already mostly the same pixel dimensions.",
        "- The large fidelity difference comes mainly from the WoD Blood Elf 2 model/rig/animation package and newer artwork.",
        "- This attempt therefore uses the WoD HD model package rather than pretending a simple bitmap resize can create HD geometry.",
        "- DarkfallenFemale/DarkfallenMale HD aliases are included beside the original BloodElf2-named model assets.",
        "- Client/DBC integration is still required to point the Darkfallen race at the desired model and CharSections texture rows.",
        "",
        f"BLPs verified: {verification['blps_checked']}",
        f"BLP decode issues: {len(verification['blp_issues'])}",
    ]
    (root / "README_DARKFALLEN_ATTEMPT.txt").write_text("\n".join(note) + "\n", encoding="utf-8")
    (root / "MANIFEST_DARKFALLEN_ATTEMPT.json").write_text(
        json.dumps({"report": report, "verification": verification}, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    if not DARKFALLEN.exists() or not HD.exists():
        raise SystemExit("Missing input directories")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    factors = build_factors()

    print("Building Upscaled attempt...")
    up_report = do_upscaled(factors)
    up_verify = verify_tree(UPSCALED)
    write_notes(UPSCALED, up_report, up_verify)
    print(
        f"Upscaled: fused={len(up_report['fused'])}, fallback_recolored={len(up_report['fallback_recolored_hd'])}, "
        f"unmapped={len(up_report['unmapped_darkfallen'])}, BLP issues={len(up_verify['blp_issues'])}"
    )

    print("Building Colored attempt...")
    color_report = do_colored(factors)
    color_verify = verify_tree(COLORED)
    write_notes(COLORED, color_report, color_verify)
    print(f"Colored: recolored={len(color_report['recolored'])}, BLP issues={len(color_verify['blp_issues'])}")

    print("Done")


if __name__ == "__main__":
    main()
