"""Compare donor/staged per-race item component models against stock codes by hash."""
from __future__ import annotations

import ctypes
import hashlib
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm

DONOR = Path(r"G:\Eunoia\Client\data")
CLIENT = REPO / "3.3.5a - Dev/Data"
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
STEMS = ["Helm_Cloth_A_01", "Helm_Plate_D_02", "Helm_Leather_B_06", "Helm_Cloth_B_01"]
CODES = ["Pa", "Vu", "Kt", "Za", "Ta", "Gn", "Hu", "Ni", "Tr", "Bk"]


def open_all(storm: Storm, root: Path, order):
    handles = []
    for name in order:
        path = root / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    return handles


def read(storm: Storm, handles, key: str):
    for name, handle in reversed(handles):
        try:
            return name, storm.read(handle, key)
        except Exception:
            continue
    return None, None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    donor = open_all(storm, DONOR, DONOR_ORDER)
    ours = open_all(storm, CLIENT, OUR_ORDER)
    try:
        for stem in STEMS:
            for sex in ("M", "F"):
                print(f"--- {stem}_{sex}")
                for code in CODES:
                    key = f"Item\\ObjectComponents\\Head\\{stem}_{code}{sex}.m2"
                    donor_name, donor_bytes = read(storm, donor, key)
                    our_name, our_bytes = read(storm, ours, key)
                    mark = f"donor={donor_name}" if donor_bytes else "donor=MISSING"
                    mark += f" ours={our_name}" if our_bytes else " ours=MISSING"
                    digest = hashlib.sha1(donor_bytes).hexdigest()[:12] if donor_bytes else "-"
                    print(f"    {code}: {mark:<44} sha1={digest} size="
                          f"{len(donor_bytes) if donor_bytes else '-'}")
    finally:
        for _name, handle in donor + ours:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
