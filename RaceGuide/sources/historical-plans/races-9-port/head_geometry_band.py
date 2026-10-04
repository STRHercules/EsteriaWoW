"""Where is the Vulpera's head geometry, and where does an attached helm land?"""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
VULPERA = "character\\vulpera\\male\\vulperamale.m2"
HUMAN = "character\\human\\male\\humanmale.m2"
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


def band(payload: bytes, low: float, high: float):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    points = []
    for index in range(count):
        point = struct.unpack_from("<3f", payload, offset + index * STRIDE)
        if all(abs(value) < 10 for value in point) and low <= point[2] <= high:
            points.append(point)
    return points


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key, low, high in (("vulpera", VULPERA, 0.95, 1.35),
                                  ("human", HUMAN, 1.75, 2.15)):
        source, payload = load(storm, key)
        points = band(payload, low, high)
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        print(f"== {label} [{source}] verts in z[{low},{high}]: {len(points)}")
        print(f"   x[{min(xs):+.3f},{max(xs):+.3f}] y[{min(ys):+.3f},{max(ys):+.3f}] "
              f"z[{min(zs):+.3f},{max(zs):+.3f}]")
        print(f"   centroid=({sum(xs) / len(xs):+.3f}, {sum(ys) / len(ys):+.3f}, "
              f"{sum(zs) / len(zs):+.3f})")


if __name__ == "__main__":
    main()
