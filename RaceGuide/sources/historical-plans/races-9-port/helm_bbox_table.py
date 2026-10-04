"""Bounding boxes of the same helm across race codes (offset 0xA0 in these files)."""
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
CODES = ["Hu", "Gn", "Dw", "Be", "Dr", "Ni", "Ta", "Tr", "Sc", "Or", "Vu", "Pa", "Bk"]
STEM = "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_"


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
    print(f"{'code':<5}{'source':<14}{'size':>9}   bbox")
    for code in CODES:
        for sex in ("M",):
            key = f"{STEM}{code}{sex}.m2"
            source, payload = load(storm, key)
            if payload is None:
                print(f"{code:<5}MISSING")
                continue
            low = struct.unpack_from("<3f", payload, 0xA0)
            high = struct.unpack_from("<3f", payload, 0xAC)
            span = [high[i] - low[i] for i in range(3)]
            print(f"{code:<5}{source:<14}{len(payload):>9,}   "
                  f"x[{low[0]:+.3f},{high[0]:+.3f}] y[{low[1]:+.3f},{high[1]:+.3f}] "
                  f"z[{low[2]:+.3f},{high[2]:+.3f}]  span=({span[0]:.3f},{span[1]:.3f},{span[2]:.3f})")


if __name__ == "__main__":
    main()
