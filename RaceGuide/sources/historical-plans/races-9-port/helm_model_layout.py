"""Header descriptors + vertex box for the three helm models."""
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
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_BeM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_PaM.m2",
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


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for key in FILES:
        source, payload = load(storm, key)
        print(f"== {key.split(chr(92))[-1]} [{source}] size={len(payload):,} "
              f"version={struct.unpack_from('<I', payload, 4)[0]}")
        for slot in range(0x40, 0x140, 8):
            count, offset = struct.unpack_from("<II", payload, slot)
            if not count or offset > len(payload):
                continue
            for stride in (32, 40, 48, 52, 56):
                if offset + count * stride <= len(payload):
                    print(f"   slot {slot:#05x}: count={count:>5} offset={offset:#08x} "
                          f"fits stride {stride}")
                    break
            else:
                print(f"   slot {slot:#05x}: count={count:>5} offset={offset:#08x} (no stride)")
        # vertex candidate: the array with the most elements that fits 48-byte records
        best = None
        for slot in range(0x40, 0x140, 8):
            count, offset = struct.unpack_from("<II", payload, slot)
            if count >= 50 and offset and offset + count * 48 <= len(payload):
                if best is None or count > best[1]:
                    best = (slot, count, offset)
        if best:
            slot, count, offset = best
            lo = [1e9] * 3
            hi = [-1e9] * 3
            for index in range(count):
                point = struct.unpack_from("<3f", payload, offset + index * 48)
                if any(abs(v) > 1000 for v in point):
                    continue
                for axis in range(3):
                    lo[axis] = min(lo[axis], point[axis])
                    hi[axis] = max(hi[axis], point[axis])
            print(f"   vertices slot {slot:#x}: {count} at {offset:#x} "
                  f"x[{lo[0]:+.3f},{hi[0]:+.3f}] y[{lo[1]:+.3f},{hi[1]:+.3f}] "
                  f"z[{lo[2]:+.3f},{hi[2]:+.3f}]")
        print()


if __name__ == "__main__":
    main()
