"""Coverage of Item\\ObjectComponents\\Shoulder and Head per race code, plus byte totals."""
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
SUFFIX = re.compile(r"_([A-Za-z]{2})([MF])\.(m2|skin|mdx)$", re.I)
SLOTS = ("head", "shoulder")


def scan(storm: Storm, root: Path, order):
    per: dict[tuple[str, str], list[int]] = {}
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
                if not lower.startswith(f"item\\objectcomponents\\{slot}\\"):
                    continue
                match = SUFFIX.search(entry[0])
                if not match:
                    continue
                key = (slot, match.group(1).lower())
                bucket = per.setdefault(key, [0, 0, 0])
                bucket[0] += 1
                bucket[1] += entry[1]
                bucket[2] += entry[2]
    return per


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = scan(storm, CLIENT, OUR_ORDER)
    donor = scan(storm, DONOR, DONOR_ORDER)
    codes = sorted({code for _slot, code in list(ours) + list(donor)})
    print(f"  {'code':<5}{'slot':<10}{'ours n':>8}{'ours MB':>10}{'donor n':>9}{'donor MB':>10}")
    for code in codes:
        for slot in SLOTS:
            left = ours.get((slot, code), [0, 0, 0])
            right = donor.get((slot, code), [0, 0, 0])
            if not left[0] and not right[0]:
                continue
            print(f"  {code.upper():<5}{slot:<10}{left[0]:>8}{left[1] / 1048576:>10.1f}"
                  f"{right[0]:>9}{right[1] / 1048576:>10.1f}")


if __name__ == "__main__":
    main()
