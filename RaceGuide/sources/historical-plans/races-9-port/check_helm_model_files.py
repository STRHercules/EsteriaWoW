"""Which archive (if any) serves a helmet model file, ours vs donor.

Usage: python check_helm_model_files.py [name ...]
Defaults to the three models the item trace resolved.
"""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
OUR_ORDER = [
    "common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ",
    "patch.MPQ", "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq",
    "PATCH-A.MPQ", "Patch-B.MPQ", "Patch-C.MPQ", "Patch-D.MPQ",
    "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ", "Patch-O.mpq",
    "PATCH-X.MPQ", "Patch-Y.MPQ",
]
DONOR = Path(r"G:\Eunoia\Client\data")
PREFIXES = ["Item\\ObjectComponents\\Head\\", "Item\\ObjectComponents\\", ""]

DEFAULT_NAMES = ["Helm_Leather_B_06.mdx", "Helm_Cloth_A_01.mdx", "Helm_Plate_D_02.mdx"]


def lookup(storm: Storm, root: Path, order, key: str):
    """Return (archive_name, size) for the highest-priority archive holding key."""
    hit = None
    for name in order:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, key)
                hit = (name, len(payload))
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return hit


def main() -> None:
    names = sys.argv[1:] or DEFAULT_NAMES
    storm = Storm(DLL_DEFAULT)
    donor_order = sorted(p.name for p in DONOR.glob("*.mpq"))
    for name in names:
        print(f"=== {name}")
        for prefix in PREFIXES:
            key = prefix + name
            ours = lookup(storm, CLIENT, OUR_ORDER, key)
            donor = lookup(storm, DONOR, donor_order, key)
            print(f"   {key:<48} ours={ours} donor={donor}")


if __name__ == "__main__":
    main()
