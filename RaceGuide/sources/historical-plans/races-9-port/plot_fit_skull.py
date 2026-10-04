"""Fit view restricted to the skull and ear vertices (by dominant bone weight)."""
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
HEAD_BONES = {56, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82,
              83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 195, 196, 197, 198, 199}
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


def head_vertices(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    out = []
    for index in range(count):
        record = offset + index * STRIDE
        point = struct.unpack_from("<3f", payload, record)
        weights = payload[record + 12:record + 16]
        bones = payload[record + 16:record + 20]
        if any(abs(value) > 100 for value in point):
            continue
        dominant = max(range(4), key=lambda slot: weights[slot])
        if weights[dominant] and bones[dominant] in HEAD_BONES:
            out.append(point)
    return out


def helm_vertices(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    out = []
    for index in range(count):
        point = struct.unpack_from("<3f", payload, offset + index * STRIDE)
        if all(abs(value) < 100 for value in point):
            out.append(point)
    return out


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    _source, vulpera = load(storm, VULPERA)
    head = head_vertices(vulpera)
    xs = [p[0] for p in head]
    ys = [p[1] for p in head]
    zs = [p[2] for p in head]
    print(f"skull vertices: {len(head)}")
    print(f"  x[{min(xs):+.3f},{max(xs):+.3f}] y[{min(ys):+.3f},{max(ys):+.3f}] "
          f"z[{min(zs):+.3f},{max(zs):+.3f}]")

    helms = {}
    for label, (key, colour) in HELMETS.items():
        _source, payload = load(storm, key)
        helms[label] = (helm_vertices(payload), colour)
        print(f"helm {label}: {len(helms[label][0])} verts")

    view = dict(x0=-0.55, x1=0.30, z0=0.80, z1=1.60)
    for anchor_name, anchor in (("current", (-0.119, 0.0, 1.294)),
                                ("centre", (-0.090, 0.0, 1.190)),
                                ("neck", (-0.116, 0.0, 1.089))):
        canvas = Image.new("RGB", (760, 620), (16, 16, 20))
        draw = ImageDraw.Draw(canvas)

        def project(point, shift=(0.0, 0.0, 0.0), colour=(255, 255, 255), radius=1):
            horizontal = point[0] + shift[0]
            vertical = point[2] + shift[2]
            if not (view["x0"] <= horizontal <= view["x1"] and view["z0"] <= vertical <= view["z1"]):
                return
            px = int((horizontal - view["x0"]) / (view["x1"] - view["x0"]) * 760)
            py = int((view["z1"] - vertical) / (view["z1"] - view["z0"]) * 620)
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=colour)

        for point in head:
            project(point, radius=2)
        for label, (points, colour) in helms.items():
            for point in points:
                project(point, anchor, colour, radius=2)
        target = REPO / f".agents/plans/races-9-port/fit2-{anchor_name}.png"
        canvas.save(target)
        print("wrote", target)


if __name__ == "__main__":
    main()
