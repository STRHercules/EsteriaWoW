"""Zoomed side-view fit plot: Vulpera head vertices vs the two helm models at the pivot."""
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
TARGET = REPO / ".agents/plans/races-9-port/debug-vulpera-head-fit-zoom.png"
VULPERA = "character\\vulpera\\male\\vulperamale.m2"
HELMETS = {
    "Vu": ("Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2", (255, 80, 80)),
    "Hu": ("Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2", (80, 180, 255)),
}
PIVOT = (-0.116, 0.0, 1.089)
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


def cloud(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    points = []
    step = max(1, count // 20000)
    for index in range(0, count, step):
        point = struct.unpack_from("<3f", payload, offset + index * STRIDE)
        if all(abs(value) < 100 for value in point):
            points.append(point)
    return points


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    _source, vulpera = load(storm, VULPERA)
    body = cloud(vulpera)
    head = [p for p in body if 0.90 <= p[2] <= 1.45 and -0.55 <= p[0] <= 0.25]
    print(f"head region points: {len(head)} (of {len(body)})")

    canvas = Image.new("RGB", (900, 700), (16, 16, 20))
    draw = ImageDraw.Draw(canvas)
    window = dict(x0=-0.55, x1=0.30, z0=0.80, z1=1.50)
    scale_x = canvas.width / (window["x1"] - window["x0"])
    scale_z = canvas.height / (window["z1"] - window["z0"])

    def project(point, shift=(0.0, 0.0, 0.0)):
        x = point[0] + shift[0]
        z = point[2] + shift[2]
        return int((x - window["x0"]) * scale_x), int((window["z1"] - z) * scale_z)

    for point in head:
        px, py = project(point)
        draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill=(235, 235, 235))

    for label, (key, colour) in HELMETS.items():
        _source, payload = load(storm, key)
        for point in cloud(payload):
            px, py = project(point, PIVOT)
            draw.ellipse((px, py, px + 1, py + 1), fill=colour)

    px, py = project(PIVOT, (0, 0, 0))
    draw.ellipse((px - 4, py - 4, px + 4, py + 4), outline=(255, 255, 0), width=2)
    canvas.save(TARGET)
    print("wrote", TARGET)


if __name__ == "__main__":
    main()
