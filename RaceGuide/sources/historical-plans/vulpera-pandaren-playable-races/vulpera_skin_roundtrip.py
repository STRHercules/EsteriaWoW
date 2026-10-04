"""Export the Vulpera body skins to PNG and import painted PNGs back to Patch-C.

export: writes one PNG per BLP next to a manifest (plain RGB, 512x512).
import: quantises each PNG back to a 256-colour palette BLP, keeping the
        original header/mip layout, and stages a replacement archive.
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(HERE))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates  # noqa: E402
from PIL import Image  # noqa: E402

PREFIX = ("vulperamaleskin", "vulperafemaleskin")


def targets(storm: Storm, handle) -> list[str]:
    return sorted(
        name for name, *_ in storm.list_files(handle)
        if name.casefold().startswith("character\\vulpera\\")
        and name.rsplit("\\", 1)[-1].casefold().startswith(PREFIX)
    )


def export(args) -> None:
    storm = Storm(DLL_DEFAULT)
    args.in_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    handle = storm.open_archive(args.patch_c)
    try:
        for name in targets(storm, handle):
            data = storm.read(handle, name)
            width, height = struct.unpack_from("<II", data, 12)
            offsets = struct.unpack_from("<16I", data, 20)
            palette = data[148:148 + 1024]
            pal = []
            for i in range(256):
                b, g, r, a = palette[i * 4:i * 4 + 4]
                pal.extend((r, g, b))
            image = Image.frombytes("P", (width, height), data[offsets[0]:offsets[0] + width * height])
            image.putpalette(pal)
            flat = name.replace("\\", "_")
            image.convert("RGB").save(args.in_dir / f"{flat}.png")
            manifest.append({"entry": name, "png": f"{flat}.png", "size": [width, height]})
    finally:
        storm.dll.SFileCloseArchive(handle)
    (args.in_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"exported {len(manifest)} textures -> {args.in_dir}")


def import_pngs(args) -> None:
    storm = Storm(DLL_DEFAULT)
    manifest = json.loads((args.in_dir / "manifest.json").read_text(encoding="utf-8"))
    handle = storm.open_archive(args.patch_c)
    try:
        updates = {}
        for item in manifest:
            png = args.in_dir / item["png"]
            if not png.is_file():
                continue
            data = storm.read(handle, item["entry"])
            width, height = struct.unpack_from("<II", data, 12)
            offsets = struct.unpack_from("<16I", data, 20)
            sizes = struct.unpack_from("<16I", data, 84)
            image = Image.open(png).convert("RGB")
            if image.size != (width, height):
                raise SystemExit(f"{png.name}: {image.size} != {(width, height)}")
            quantised = image.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
            palette = quantised.getpalette()[: 256 * 3]
            out = bytearray(data)
            for i in range(256):
                r = palette[i * 3] if i * 3 < len(palette) else 0
                g = palette[i * 3 + 1] if i * 3 + 1 < len(palette) else 0
                b = palette[i * 3 + 2] if i * 3 + 2 < len(palette) else 0
                out[148 + i * 4 + 0] = b
                out[148 + i * 4 + 1] = g
                out[148 + i * 4 + 2] = r
                out[148 + i * 4 + 3] = 0xFF
            for level, (offset, size) in enumerate(zip(offsets, sizes)):
                if not size or not offset:
                    continue
                mip_w = max(1, width >> level)
                mip_h = max(1, height >> level)
                if level == 0:
                    mip_indices = quantised.tobytes()
                else:
                    mip = image.resize((mip_w, mip_h), Image.BOX)
                    mip_indices = mip.quantize(palette=quantised, dither=Image.NONE).tobytes()
                if len(mip_indices) != size:
                    raise SystemExit(f"{png.name}: mip {level} size mismatch")
                out[offset:offset + size] = mip_indices
            updates[item["entry"]] = bytes(out)
        if not updates:
            raise SystemExit("nothing to import")
        staging = args.out / "staged"
        if staging.exists():
            shutil.rmtree(staging)
        staged = _stage_archive_updates(staging, args.patch_c, updates)
        print(f"imported {len(updates)} textures -> {staged} ({staged.stat().st_size} bytes)")
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("export", export), ("import", import_pngs)):
        p = sub.add_parser(name)
        p.add_argument("--patch-c", type=Path, required=True)
        p.add_argument("--in-dir", type=Path, required=True)
        p.add_argument("--out", type=Path, default=None)
        p.set_defaults(func=fn)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
