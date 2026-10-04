"""Verify the staged variants really carry the intended vertex shift."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
HEAD = "Item\\ObjectComponents\\Head\\"
STRIDE = 48
ANCHOR = (-0.103, 0.0, 1.171)


def box(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for index in range(count):
        point = struct.unpack_from("<3f", payload, offset + index * STRIDE)
        for axis in range(3):
            lo[axis] = min(lo[axis], point[axis])
            hi[axis] = max(hi[axis], point[axis])
    return lo, hi


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0x100, ctypes.byref(handle)):
        raise SystemExit("cannot open Patch-Y")
    try:
        base = storm.read(handle, f"{HEAD}Helm_Leather_B_06_VuM.m2")
        base_box = box(base)
        print(f"base helm   x[{base_box[0][0]:+.3f},{base_box[1][0]:+.3f}] "
              f"z[{base_box[0][2]:+.3f},{base_box[1][2]:+.3f}]")
        for label in "ABCDEFG":
            payload = storm.read(handle, f"{HEAD}HelmCal{label}_VuM.m2")
            low, high = box(payload)
            print(f"  {label}: shift (dx {low[0] - base_box[0][0]:+.3f}, "
                  f"dz {low[2] - base_box[0][2]:+.3f})  world x[{ANCHOR[0] + low[0]:+.3f},"
                  f"{ANCHOR[0] + high[0]:+.3f}] z[{ANCHOR[2] + low[2]:+.3f},"
                  f"{ANCHOR[2] + high[2]:+.3f}]")
    finally:
        storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
