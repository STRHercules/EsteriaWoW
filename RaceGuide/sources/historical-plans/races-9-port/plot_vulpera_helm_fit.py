"""Plot the Vulpera head-region vertices and the attached helm's vertices.

The helm is a rigid model: its rest-pose vertices plus the attachment pivot give its
position.  Drawing both as point clouds answers where the client will put it.
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
TARGET = REPO / ".agents/plans/races-9-port/debug-vulpera-helm-fit.png"
VULPERA = "character\\vulpera\\male\\vulperamale.m2"
HELMETS = {
    "Vu": "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2",
    "Hu": "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2",
}
HEAD_ATTACH = (-0.116, 0.0, 1.089)


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


def vertex_cloud(payload: bytes, stride: int, limit: int | None = None):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    points = []
    step = 1
    if limit and count > limit:
        step = count // limit
    for index in range(0, count, step):
        point = struct.unpack_from("<3f", payload, offset + index * stride)
        if all(abs(value) < 100 for value in point):
            points.append(point)
    return count, offset, points


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    source, vulpera = load(storm, VULPERA)
    print(f"vulpera [{source}] size={len(vulpera):,}")
    for stride in (40, 48, 52):
        count, offset, points = vertex_cloud(vulpera, stride, 4000)
        if not points:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        print(f"  stride {stride}: {count} verts at {offset:#x} "
              f"x[{min(xs):+.2f},{max(xs):+.2f}] y[{min(ys):+.2f},{max(ys):+.2f}] "
              f"z[{min(zs):+.2f},{max(zs):+.2f}]")

    stride = 48
    _count, _offset, body = vertex_cloud(vulpera, stride, 6000)
    head = [p for p in body if 0.85 <= p[2] <= 1.45]
    print(f"  head-region points: {len(head)}")

    helms = {}
    for label, key in HELMETS.items():
        source, payload = load(storm, key)
        _count, _offset, points = vertex_cloud(payload, stride)
        helms[label] = points
        print(f"  helm {label} [{source}]: {len(points)} points")

    scale = 420
    origin_z, origin_x = 1.45, -0.45
    canvas = Image.new("RGB", (760, 620), (18, 18, 22))
    draw = ImageDraw.Draw(canvas)

    def project(point, shift=(0.0, 0.0, 0.0)):
        x = point[0] + shift[0]
        z = point[2] + shift[2]
        screen_x = int((x - origin_x) * scale)
        screen_y = int((origin_z - z) * scale) + 20
        return screen_x, screen_y

    for point in head:
        x, y = project(point)
        draw.point((x, y), fill=(220, 220, 220))
    for label, points in helms.items():
        colour = (255, 90, 90) if label == "Vu" else (90, 200, 255)
        for point in points:
            x, y = project(point, HEAD_ATTACH)
            draw.point((x, y), fill=colour)
    canvas.save(TARGET)
    print("wrote", TARGET)


if __name__ == "__main__":
    main()
