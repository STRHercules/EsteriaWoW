"""What codes exist for the stems the donor has no Pa/Vu model for?"""
from __future__ import annotations

import ctypes
import re
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
OUR_ORDER = ("common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ")
STEMS = ["Helm_Eyepatch_A_02", "Helm_Goggles_B_04", "Helm_Leather_B_06", "Helm_Cloth_A_01"]


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    found: dict[str, set[str]] = {}
    for archive in OUR_ORDER:
        path = CLIENT / archive
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                listing = storm.list_files(handle)
            except Exception:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
        for entry in listing:
            if not entry[0].lower().startswith("item\\objectcomponents\\head\\"):
                continue
            tail = entry[0].split("\\")[-1]
            for stem in STEMS:
                if tail.lower().startswith(stem.lower() + "_"):
                    found.setdefault(stem, set()).add(f"{tail}  [{archive}]")
    for stem in STEMS:
        entries = sorted(found.get(stem, ()))
        print(f"=== {stem}: {len(entries)}")
        for entry in entries[:40]:
            print(f"    {entry}")


if __name__ == "__main__":
    main()
