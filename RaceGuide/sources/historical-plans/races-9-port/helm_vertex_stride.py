"""Find the vertex stride for the helm models by matching their bounding box."""
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
FILES = [
    ("symbol", "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2"),
    ("texture", "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2"),
]


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


def box(payload: bytes, stride: int, count: int, offset: int):
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for index in range(count):
        point = struct.unpack_from("<3f", payload, offset + index * stride)
        if any(abs(value) > 100 for value in point):
            return None
        for axis in range(3):
            lo[axis] = min(lo[axis], point[axis])
            hi[axis] = max(hi[axis], point[axis])
    return lo, hi


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in FILES:
        source, payload = load(storm, key)
        print(f"== {label} [{source}] size={len(payload):,}")
        count, offset = struct.unpack_from("<II", payload, 0x3C)
        print(f"   header vertices descriptor: count={count} offset={offset:#x}")
        for slot in range(0x40, 0xE0, 4):
            value = struct.unpack_from("<I", payload, slot)[0]
            if 50 <= value <= 5000:
                nxt = struct.unpack_from("<I", payload, slot + 4)[0]
                if 0 < nxt < len(payload):
                    print(f"   slot {slot:#05x}: {value} @ {nxt:#x}")
        for stride in (32, 36, 40, 44, 48, 52, 56, 64):
            result = box(payload, stride, count, offset)
            if result is None:
                print(f"   stride {stride}: out of range values")
                continue
            lo, hi = result
            print(f"   stride {stride}: x[{lo[0]:+.3f},{hi[0]:+.3f}] y[{lo[1]:+.3f},{hi[1]:+.3f}] "
                  f"z[{lo[2]:+.3f},{hi[2]:+.3f}]")


if __name__ == "__main__":
    main()
