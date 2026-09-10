# -*- coding: utf-8 -*-
"""Convert PNG sprites to 256x256 WoW-compatible TGA (power-of-two, 32-bit).

WoW 3.3.5 cannot read PNG, so every sprite the UI shows needs a TGA sibling.

Usage:
    python tools/convert_sprites_tga.py --root "<...>/AddOns/Battlemon/assets" \
        "Front" "Back" "Front shiny" "Back shiny"
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

DEFAULT_FOLDERS = ["Front", "Back", "Front shiny", "Back shiny"]
SIZE = 256


def save_wow_tga(img: Image.Image, path: Path) -> None:
    img = img.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
    w, h = img.size
    try:
        import numpy as np
        arr = np.array(img)
        bgra = arr[:, :, [2, 1, 0, 3]].tobytes()
    except Exception:
        pixels = img.tobytes()
        buf = bytearray(len(pixels))
        for i in range(0, len(pixels), 4):
            buf[i] = pixels[i + 2]
            buf[i + 1] = pixels[i + 1]
            buf[i + 2] = pixels[i]
            buf[i + 3] = pixels[i + 3]
        bgra = bytes(buf)
    header = bytearray(18)
    header[2] = 2
    header[12] = w & 0xFF
    header[13] = (w >> 8) & 0xFF
    header[14] = h & 0xFF
    header[15] = (h >> 8) & 0xFF
    header[16] = 32
    header[17] = 8
    path.write_bytes(bytes(header) + bgra)


def convert_folder(root: Path, folder: str) -> None:
    src_dir = root / folder
    if not src_dir.is_dir():
        print(f"{folder}: missing, skipped")
        return
    files = [p for p in src_dir.iterdir() if p.suffix.lower() == ".png"]
    print(f"{folder}: {len(files)} png")
    written = 0
    for i, src in enumerate(files, 1):
        dest = src.with_suffix(".tga")
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            continue
        im = Image.open(src).convert("RGBA")
        canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        x = (SIZE - im.width) // 2
        y = (SIZE - im.height) // 2
        canvas.paste(im, (x, y), im)
        save_wow_tga(canvas, dest)
        written += 1
        if written % 250 == 0:
            print(f"  {i}/{len(files)}")
    print(f"  done {folder}: {written} written")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="path to the addon assets folder")
    ap.add_argument("folders", nargs="*", default=None)
    args = ap.parse_args()
    for folder in (args.folders or DEFAULT_FOLDERS):
        convert_folder(Path(args.root), folder)


if __name__ == "__main__":
    main()
