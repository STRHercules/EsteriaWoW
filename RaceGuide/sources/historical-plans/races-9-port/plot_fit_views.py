"""Accurate side/front fit view: Vulpera head vertices vs candidate helmets.

Parser validated against the models' own bounding boxes:
  vertices = M2Array at 0x3C, record stride 0x30 (48), bounding box at 0xA0.
"""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
VULPERA = "character\\vulpera\\male\\vulperamale.m2"
HELMETS = {
    "Hu": ("Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2", (90, 170, 255)),
    "Vu": ("Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2", (255, 90, 90)),
}
ANCHORS = [(x * 0.02 - 0.16, 0.0, z * 0.02 + 1.00) for x in range(0) for z in range(0)]
STRIDE = 48


def load(storm: Storm, key: str):
    for name in reversed(ORDER):
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return name, storm.read(handle, key)
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None, None


def vertices(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    out = []
    for index in range(count):
        point = struct.unpack_from("<3f", payload, offset + index * STRIDE)
        if all(abs(value) < 100 for value in point):
            out.append(point)
    return out


def draw_view(draw, viewport, points, colour, shift, radius=1):
    x0, x1, y0, y1, axis = viewport
    width, height = 760, 620
    for point in points:
        if axis == "side":
            horizontal, vertical = point[0] + shift[0], point[2] + shift[2]
        else:
            horizontal, vertical = point[1] + shift[1], point[2] + shift[2]
        if not (x0 <= horizontal <= x1 and y0 <= vertical <= y1):
            continue
        screen_x = int((horizontal - x0) / (x1 - x0) * width)
        screen_y = int((y1 - vertical) / (y1 - y0) * height)
        draw.ellipse((screen_x - radius, screen_y - radius, screen_x + radius, screen_y + radius),
                     fill=colour)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    _source, vulpera = load(storm, VULPERA)
    body = vertices(vulpera)
    head = [p for p in body if 0.95 <= p[2] <= 1.50 and -0.55 <= p[0] <= 0.30]
    print(f"vulpera vertices {len(body)}, head region {len(head)}")
    xs = [p[0] for p in head]
    zs = [p[2] for p in head]
    print(f"head band x[{min(xs):+.3f},{max(xs):+.3f}] z[{min(zs):+.3f},{max(zs):+.3f}]")

    helms = {}
    for label, (key, colour) in HELMETS.items():
        _source, payload = load(storm, key)
        low = struct.unpack_from("<3f", payload, 0xA0)
        high = struct.unpack_from("<3f", payload, 0xAC)
        helms[label] = (vertices(payload), colour, low, high)
        print(f"helm {label}: {len(helms[label][0])} verts, bbox z[{low[2]:+.3f},{high[2]:+.3f}]")

    anchors = {
        "current (Hu, top of skull)": (-0.119, 0.0, 1.294),
        "head centre": (-0.090, 0.0, 1.190),
        "neck (original)": (-0.116, 0.0, 1.089),
    }

    for name, (x0, x1, y0, y1, axis) in {
        "side": (-0.55, 0.35, 0.85, 1.60, "side"),
        "front": (-0.45, 0.45, 0.85, 1.60, "front"),
    }.items():
        for anchor_name, anchor in anchors.items():
            canvas = Image.new("RGB", (760, 620), (16, 16, 20))
            draw = ImageDraw.Draw(canvas)
            viewport = (x0, x1, y0, y1, axis)
            draw_view(draw, viewport, head, (235, 235, 235), (0, 0, 0))
            for label, (points, colour, _low, _high) in helms.items():
                draw_view(draw, viewport, points, colour, anchor, radius=1)
            ax, ay = int((anchor[0] - x0) / (x1 - x0) * 760), int((y1 - anchor[2]) / (y1 - y0) * 620)
            draw.ellipse((ax - 4, ay - 4, ax + 4, ay + 4), outline=(255, 255, 0), width=2)
            target = REPO / f".agents/plans/races-9-port/fit-{name}-{anchor_name.split()[0]}.png"
            canvas.save(target)
            print("wrote", target)


if __name__ == "__main__":
    main()
