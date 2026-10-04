"""Lift the dark fur band off the Vulpera forearm in the body skin textures.

The probe run showed the "bracers" are painted into the race's own skin texture:
a warm, saturated dark band on the forearm strip (columns 1-2 of the atlas).
Desaturated darks (paw pads, nose) and bright fur are left alone, so the paws
keep their pads and the rest of the body is untouched.
"""

from __future__ import annotations

import argparse
import colorsys
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates  # noqa: E402
from PIL import Image  # noqa: E402

# The band is a warm, saturated fur: dark value plus non-trivial saturation.
# Both thresholds feed a smooth weight, so nothing is edited with a hard edge.
VALUE_FULL = 0.50     # w = 1 at or below this value
VALUE_NONE = 0.68     # w = 0 at or above this value
SAT_FULL = 0.42       # w = 1 at or above this saturation
SAT_NONE = 0.20       # w = 0 at or below this saturation
STRENGTH = 1.00
GAMMA = 0.55


def decode(data: bytes):
    if data[:4] != b"BLP2" or data[4] != 1:
        raise ValueError("expected palettised BLP2")
    width, height = struct.unpack_from("<II", data, 12)
    offsets = struct.unpack_from("<16I", data, 20)
    sizes = struct.unpack_from("<16I", data, 84)
    palette = data[148:148 + 1024]
    pal = []
    lookup = []
    for i in range(256):
        b, g, r, a = palette[i * 4:i * 4 + 4]
        pal.extend((r, g, b))
        lookup.append((r, g, b))
    indices = data[offsets[0]:offsets[0] + width * height]
    return bytearray(indices), lookup, width, height, offsets, sizes, pal, data


def lift(indices: bytearray, lookup, width: int, height: int) -> int:
    # palette lookup cache on a 5-bit-per-channel grid
    cache = {}
    def nearest(rgb):
        key = (rgb[0] >> 3, rgb[1] >> 3, rgb[2] >> 3)
        hit = cache.get(key)
        if hit is None:
            hit = min(range(256), key=lambda i: sum((lookup[i][k] - rgb[k]) ** 2 for k in range(3)))
            cache[key] = hit
        return hit
    changed = 0
    # Mirror the upper-arm fur (column 0) across the forearm columns, so the arm
    # keeps real fur detail instead of a levelled or painted-over patch.
    for y in range(160, 512):
        for x in range(64, 192):
            source = 63 - ((x - 64) % 64)
            pos = y * width + x
            new_index = indices[y * width + source]
            if new_index != indices[pos]:
                indices[pos] = new_index
                changed += 1
    return changed


def encode(indices: bytearray, palette: list, template: bytes, width: int, height: int,
           offsets, sizes) -> bytes:
    out = bytearray(template)
    out[148:148 + 1024] = bytes(b for i in range(256) for b in (palette[i * 3 + 2], palette[i * 3 + 1], palette[i * 3], 0xFF))
    for level, (offset, size) in enumerate(zip(offsets, sizes)):
        if not size or not offset:
            continue
        mip_w = max(1, width >> level)
        mip_h = max(1, height >> level)
        mip_indices = bytearray(mip_w * mip_h)
        step = 1 << level
        for y in range(mip_h):
            row = min(height - 1, y * step)
            for x in range(mip_w):
                mip_indices[y * mip_w + x] = indices[row * width + min(width - 1, x * step)]
        if len(mip_indices) != size:
            raise ValueError(f"mip {level}: {len(mip_indices)} != {size}")
        out[offset:offset + size] = mip_indices
    return bytes(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        entries = [name for name, *_ in storm.list_files(handle)]
        targets = sorted(
            name for name in entries
            if name.casefold().startswith("character\\vulpera\\")
            and name.rsplit("\\", 1)[-1].casefold().startswith(("vulperamaleskin", "vulperafemaleskin"))
        )
        if not targets:
            raise SystemExit("no vulpera skin textures found")
        updates = {}
        total = 0
        for name in targets:
            data = storm.read(handle, name)
            indices, lookup, width, height, offsets, sizes, pal, template = decode(data)
            before = bytes(indices)
            total += lift(indices, lookup, width, height)
            updates[name] = encode(indices, pal, template, width, height, offsets, sizes)
            if args.preview and name.casefold().endswith("vulperamaleskin00_00.blp"):
                args.preview.parent.mkdir(parents=True, exist_ok=True)
                def to_image(buf):
                    img = Image.frombytes("P", (width, height), bytes(buf))
                    img.putpalette(pal)
                    return img.convert("RGB")
                side = Image.new("RGB", (512, 512))
                side.paste(to_image(before).crop((0, 0, 256, 512)), (0, 0))
                side.paste(to_image(indices).crop((0, 0, 256, 512)), (256, 0))
                side.resize((1024, 1024), Image.NEAREST).save(args.preview)
        print(f"repainted {len(updates)} textures ({total} pixels lifted)")
    finally:
        storm.dll.SFileCloseArchive(handle)

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    check = Storm(DLL_DEFAULT)
    handle = check.open_archive(staged)
    try:
        names = {name.casefold(): name for name, *_ in check.list_files(handle)}
        sample = names[targets[0].casefold()]
        data = check.read(handle, sample)
        indices, lookup, width, height, offsets, sizes, pal, _ = decode(data)
        print(f"   verify {sample}: {width}x{height} palette preserved, sample (128,300)={lookup[indices[300 * width + 128]]}")
    finally:
        check.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
