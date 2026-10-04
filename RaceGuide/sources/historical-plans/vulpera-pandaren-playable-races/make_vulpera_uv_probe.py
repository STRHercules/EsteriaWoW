"""Replace the Vulpera body skin textures with a UV probe grid.

Column encodes hue (8 hues), row encodes brightness (8 levels), palette index is
row*8+col. Reading the colours off a screenshot tells which texture cell each
body part samples, and which cells the client overwrites with the armour sleeve.
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

GRID = 8
PALETTE_OFFSET = 148
PALETTE_ENTRIES = 256
BRIGHTNESS = (1.0, 0.86, 0.72, 0.58, 0.45, 0.34, 0.24, 0.15)
HUES = (0.0, 1 / 8, 2 / 8, 3 / 8, 4 / 8, 5 / 8, 6 / 8, 7 / 8)


def build_palette() -> bytes:
    palette = bytearray(PALETTE_ENTRIES * 4)
    for row in range(GRID):
        for col in range(GRID):
            r, g, b = colorsys.hsv_to_rgb(HUES[col], 0.95, BRIGHTNESS[row])
            index = row * GRID + col
            palette[index * 4 + 0] = int(b * 255)  # B
            palette[index * 4 + 1] = int(g * 255)  # G
            palette[index * 4 + 2] = int(r * 255)  # R
            palette[index * 4 + 3] = 0xFF          # A
    return bytes(palette)


def probe_pixels(width: int, height: int) -> bytes:
    out = bytearray(width * height)
    for y in range(height):
        row = min(GRID - 1, y * GRID // height)
        for x in range(width):
            col = min(GRID - 1, x * GRID // width)
            out[y * width + x] = row * GRID + col
    return bytes(out)


def rewrite(data: bytes, palette: bytes) -> bytes:
    if data[:4] != b"BLP2":
        raise ValueError("not BLP2")
    compression = data[4]
    if compression != 1:
        raise ValueError(f"unsupported compression {compression}")
    width, height = struct.unpack_from("<II", data, 12)
    offsets = struct.unpack_from("<16I", data, 20)
    sizes = struct.unpack_from("<16I", data, 84)
    out = bytearray(data)
    out[PALETTE_OFFSET : PALETTE_OFFSET + PALETTE_ENTRIES * 4] = palette
    for level, (offset, size) in enumerate(zip(offsets, sizes)):
        if not size or not offset:
            continue
        mip_w = max(1, width >> level)
        mip_h = max(1, height >> level)
        pixels = probe_pixels(mip_w, mip_h)
        if len(pixels) != size:
            raise ValueError(f"mip {level}: size {size} != {len(pixels)}")
        out[offset : offset + size] = pixels
    return bytes(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        entries = [name for name, *_ in storm.list_files(handle)]
        targets = sorted(
            name
            for name in entries
            if name.casefold().startswith("character\\vulpera\\")
            and name.casefold().endswith(".blp")
            and "skin" in name.rsplit("\\", 1)[-1].casefold()
            and not name.rsplit("\\", 1)[-1].casefold().startswith("vulpera")
        )
        targets = sorted(
            name
            for name in entries
            if name.casefold().startswith("character\\vulpera\\")
            and name.rsplit("\\", 1)[-1].casefold().startswith(("vulperamaleskin", "vulperafemaleskin"))
        )
        if not targets:
            raise SystemExit("no vulpera skin textures found")
        palette = build_palette()
        updates = {}
        for name in targets:
            data = storm.read(handle, name)
            updates[name] = rewrite(data, palette)
        print(f"rewrote {len(updates)} vulpera skin textures")
    finally:
        storm.dll.SFileCloseArchive(handle)

    reference = args.reference
    reference.parent.mkdir(parents=True, exist_ok=True)
    width = height = 512
    pixels = probe_pixels(width, height)
    from PIL import Image  # noqa: E402

    image = Image.new("RGB", (width, height))
    rgb = []
    for index in pixels:
        row, col = divmod(index, GRID)
        r, g, b = colorsys.hsv_to_rgb(HUES[col], 0.95, BRIGHTNESS[row])
        rgb.append((int(r * 255), int(g * 255), int(b * 255)))
    image.putdata(rgb)
    image.save(reference)
    print(f"reference probe image -> {reference}")

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
        width, height = struct.unpack_from("<II", data, 12)
        offsets = struct.unpack_from("<16I", data, 20)
        first = offsets[0]
        # top-left cell must be palette index 0, bottom-right 63
        print(f"   verify {sample}: {width}x{height} tl={data[first]} br={data[first + width*height - 1]}")
        if data[first] != 0 or data[first + width * height - 1] != GRID * GRID - 1:
            raise SystemExit("probe verification failed")
    finally:
        check.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
