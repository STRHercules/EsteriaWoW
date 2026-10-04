"""What is inside Patch-Y right now (names only)."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0, ctypes.byref(handle)):
        raise SystemExit("cannot open Patch-Y")
    try:
        listing = storm.list_files(handle)
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"{len(listing)} entries")
    for name, size, _comp, _flags in sorted(listing):
        print(f"   {name}  {size:,}")


if __name__ == "__main__":
    main()
