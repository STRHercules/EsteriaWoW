"""Sample shoulder component names."""
from __future__ import annotations

import ctypes
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
SLOT = "item\\objectcomponents\\shoulder\\"


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    shown = 0
    for archive in ORDER:
        path = CLIENT / archive
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            listing = storm.list_files(handle)
        except Exception:
            listing = []
        finally:
            storm.dll.SFileCloseArchive(handle)
        names = [entry[0] for entry in listing if entry[0].lower().startswith(SLOT)]
        if names:
            print(f"{archive}: {len(names)} shoulder files, e.g.")
            for name in sorted(names)[:6]:
                print(f"   {name}")
            shown += 1
        if shown >= 4:
            break


if __name__ == "__main__":
    main()
