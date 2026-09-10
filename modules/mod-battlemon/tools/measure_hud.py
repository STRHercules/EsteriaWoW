#!/usr/bin/env python3
"""Report where the painted plate sits inside a HUD .tga.

The battle HUD anchors text by pixel offset against artwork with transparent
padding, so "inside the plate" is a property of the image, not of the frame.
Prints, in frame coordinates (y measured downward from the top like SetPoint),
the first and last opaque row and the opaque span of a few sample rows.

Usage:
    python tools/measure_hud.py <file.tga> <frame_w> <frame_h>
"""

import struct
import sys


def read_tga(path):
    with open(path, "rb") as fh:
        data = fh.read()
    id_len, cmap_type, img_type = data[0], data[1], data[2]
    w, h = struct.unpack_from("<HH", data, 12)
    depth = data[16]
    descriptor = data[17]
    if img_type != 2 or depth != 32:
        raise SystemExit("expected uncompressed 32-bit TGA, got type %d depth %d"
                         % (img_type, depth))
    off = 18 + id_len
    if cmap_type:
        raise SystemExit("colour-mapped TGA not supported")
    px = data[off:off + w * h * 4]
    top_down = bool(descriptor & 0x20)
    rows = []
    for y in range(h):
        src = y if top_down else (h - 1 - y)
        start = src * w * 4
        rows.append(px[start:start + w * 4])
    return w, h, rows


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    path, fw, fh = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    w, h, rows = read_tga(path)
    sx, sy = fw / w, fh / h
    print("%s  image %dx%d  drawn at %gx%g  (scale %.3f, %.3f)"
          % (path, w, h, fw, fh, sx, sy))

    spans = []
    for y, row in enumerate(rows):
        first = last = None
        for x in range(w):
            if row[x * 4 + 3] > 40:
                if first is None:
                    first = x
                last = x
        spans.append((first, last))

    opaque = [y for y, (f, _) in enumerate(spans) if f is not None]
    if not opaque:
        raise SystemExit("image is fully transparent")
    top, bottom = opaque[0], opaque[-1]
    print("painted rows %d..%d of %d  ->  frame y %.1f..%.1f"
          % (top, bottom, h, -top * sy, -(bottom + 1) * sy))

    print("\n  frame y | painted x span (frame units)")
    for frac in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        y = int(top + (bottom - top) * frac)
        f, l = spans[y]
        if f is None:
            continue
        print("  %7.1f | %6.1f .. %6.1f" % (-y * sy, f * sx, (l + 1) * sx))


if __name__ == "__main__":
    main()
