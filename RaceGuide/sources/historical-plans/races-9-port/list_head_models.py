"""All distinct Item\\ObjectComponents\\Head file names in ours vs donor."""
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
PREFIX = "item\\objectcomponents\\head\\"
SUFFIX = re.compile(r"^(.*?)(_([a-z]{2})([mf]))?(_?[0-9]{2})?\.(m2|skin|mdx)$", re.I)


def collect(storm: Storm, root: Path, order) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
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
            if not lower.startswith(PREFIX):
                continue
            short = entry[0][len(PREFIX):]
            if not short.lower().endswith((".m2", ".mdx")):
                continue
            result.setdefault(short[:-3], set()).add(name)
    return result


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = collect(storm, CLIENT, OUR_ORDER)
    donor = collect(storm, DONOR, sorted(p.name for p in DONOR.glob("*.mpq")))
    keys = sorted(set(ours) | set(donor))
    print(f"{len(keys)} distinct model stems")
    for key in keys:
        print(f"  {key:<46} ours={len(ours.get(key, ()))} donor={len(donor.get(key, ()))}")


if __name__ == "__main__":
    main()
