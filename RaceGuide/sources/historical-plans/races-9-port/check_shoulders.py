"""Shoulder component coverage per code, ours vs donor."""
from __future__ import annotations

import collections
import ctypes
import re
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

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
SLOT = "item\\objectcomponents\\shoulder\\"
SUFFIX = re.compile(r"_([A-Za-z]{2})[MF]\.(m2|mdx)$", re.IGNORECASE)


def scan(root: Path, order) -> tuple[dict[str, int], int]:
    storm = Storm(DLL_DEFAULT)
    codes: dict[str, int] = collections.Counter()
    total = 0
    for archive in order:
        path = root / archive
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
            name = entry[0]
            if not name.lower().startswith(SLOT):
                continue
            total += 1
            match = SUFFIX.search(name)
            if match:
                codes[match.group(1).lower()] += 1
    return codes, total


def main() -> None:
    ours_codes, ours_total = scan(CLIENT, OUR_ORDER)
    donor_codes, donor_total = scan(DONOR, DONOR_ORDER)
    print(f"shoulder files: ours {ours_total}, donor {donor_total}")
    print("code  ours donor")
    for code in sorted(set(ours_codes) | set(donor_codes)):
        print(f"  {code.upper():<4}{ours_codes.get(code, 0):>6}{donor_codes.get(code, 0):>7}")


if __name__ == "__main__":
    main()
