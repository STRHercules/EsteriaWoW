"""Inventory donor per-race item component models (Head, Shoulder) for codes we lack."""
from __future__ import annotations

import ctypes
import re
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
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
CODES = ["Pa", "Vu", "Kt", "Za", "Bk", "Se", "Er", "Nb", "Ve", "Lf", "Di", "Il"]
SUFFIX = re.compile(r"_([A-Za-z]{2})([MF])\.(m2|skin|mdx)$", re.I)
SLOTS = ("head", "shoulder")


def inventory(storm: Storm, root: Path, order, label: str):
    totals: dict[str, dict[str, list[int]]] = {}
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
        finally:
            storm.dll.SFileCloseArchive(handle)
        for entry in listing:
            lower = entry[0].lower()
            for slot in SLOTS:
                prefix = f"item\\objectcomponents\\{slot}\\"
                if not lower.startswith(prefix):
                    continue
                match = SUFFIX.search(entry[0])
                if not match:
                    continue
                code = match.group(1).lower()
                if code not in {c.lower() for c in CODES}:
                    continue
                bucket = totals.setdefault(code, {}).setdefault(slot, [0, 0, set()])
                bucket[0] += 1
                bucket[1] = max(bucket[1], entry[1])
                bucket[2].add(name)
    print(f"== {label}")
    for code in CODES:
        key = code.lower()
        if key not in totals:
            print(f"   {code}: none")
            continue
        parts = []
        for slot in SLOTS:
            if slot in totals[key]:
                count, largest, archives = totals[key][slot]
                parts.append(f"{slot}: {count} files, max {largest / 1024:.0f} KB, in {sorted(archives)}")
        print(f"   {code}: " + " | ".join(parts) if parts else f"   {code}: none")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    inventory(storm, DONOR, DONOR_ORDER, "donor")
    inventory(storm, CLIENT, OUR_ORDER, "ours")


if __name__ == "__main__":
    main()
