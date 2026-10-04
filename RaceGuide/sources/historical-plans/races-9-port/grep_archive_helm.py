"""Grep archive listfiles for a substring (default: helmet model stems)."""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm

CLIENT = REPO / "3.3.5a - Dev/Data"
DONOR = Path(r"G:\Eunoia\Client\data")
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
PATTERNS = ["helm_leather_b_06", "helm_cloth_a_01", "helm_plate_d_02"]


def scan(storm: Storm, root: Path, order, label: str) -> None:
    for name in order:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                listing = storm.list_files(handle)
            except Exception:
                listing = []
            hits = [entry[0] for entry in listing
                    if any(pattern in entry[0].lower() for pattern in PATTERNS)]
            print(f"[{label}] {name}: {len(listing)} listed, {len(hits)} hits")
            for hit in hits[:25]:
                print(f"      {hit}")
        finally:
            storm.dll.SFileCloseArchive(handle)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    scan(storm, CLIENT, OUR_ORDER, "ours")
    scan(storm, DONOR, sorted(p.name for p in DONOR.glob("*.mpq")), "donor")


if __name__ == "__main__":
    main()
