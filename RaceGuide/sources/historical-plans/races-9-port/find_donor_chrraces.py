"""Find ChrRaces.dbc anywhere in the donor client."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm

ROOT = Path(r"G:\Eunoia\Client")
DONOR = ROOT / "data"


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    candidates = sorted(DONOR.rglob("*.mpq")) + sorted(DONOR.rglob("*.MPQ"))
    seen = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                listing = storm.list_files(handle)
            except Exception:
                listing = []
            hits = [entry[0] for entry in listing if "chrraces" in entry[0].lower()]
            if hits:
                print(f"{path.relative_to(ROOT)}: {hits}")
        finally:
            storm.dll.SFileCloseArchive(handle)
    print("--- loose files")
    for path in ROOT.rglob("*"):
        if path.is_file() and "chrraces" in path.name.lower():
            print(path)


if __name__ == "__main__":
    main()
