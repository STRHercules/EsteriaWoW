"""Vertex bounding box of item component models (where is the geometry authored?)."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
DONOR = Path(r"G:\Eunoia\Client\data")
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
FILES = [
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_BeM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_DrM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_PaM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_KtM.m2",
    "character\\vulpera\\male\\vulperamale.m2",
]


def open_all(storm: Storm, root: Path, order):
    handles = []
    for name in order:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    return handles


def read(storm: Storm, handles, key: str):
    for name, handle in reversed(handles):
        try:
            return name, storm.read(handle, key)
        except Exception:
            continue
    return None, None


def vertex_box(payload: bytes, stride: int = 48):
    size = len(payload)
    best = None
    for slot in range(0x40, 0x200, 8):
        count, offset = struct.unpack_from("<II", payload, slot)
        if not (100 <= count <= 400000) or offset == 0:
            continue
        if offset + count * stride > size:
            continue
        if best is None or count > best[1]:
            best = (slot, count, offset)
    if best is None:
        return None
    slot, count, offset = best
    lo = [1e9, 1e9, 1e9]
    hi = [-1e9, -1e9, -1e9]
    step = max(1, count // 4000)
    sampled = 0
    for index in range(0, count, step):
        point = struct.unpack_from("<3f", payload, offset + index * stride)
        if any(abs(value) > 1000 for value in point):
            continue
        sampled += 1
        for axis in range(3):
            lo[axis] = min(lo[axis], point[axis])
            hi[axis] = max(hi[axis], point[axis])
    if not sampled:
        return None
    return slot, count, offset, lo, hi, sampled


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = open_all(storm, CLIENT, OUR_ORDER)
    donor = open_all(storm, DONOR, DONOR_ORDER)
    try:
        for key in FILES:
            for tag, handles in (("ours", ours), ("donor", donor)):
                source, payload = read(storm, handles, key)
                if payload is None:
                    continue
                for stride in (48, 52):
                    found = vertex_box(payload, stride)
                    if found is None:
                        continue
                    slot, count, offset, lo, hi, sampled = found
                    print(f"{key.split(chr(92))[-1]:<34} [{tag} <- {source:<12} stride {stride}] "
                          f"{count:>6} verts at {offset:#08x}: "
                          f"x[{lo[0]:+.3f},{hi[0]:+.3f}] y[{lo[1]:+.3f},{hi[1]:+.3f}] "
                          f"z[{lo[2]:+.3f},{hi[2]:+.3f}] (sampled {sampled})")
                    break
    finally:
        for _name, handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
