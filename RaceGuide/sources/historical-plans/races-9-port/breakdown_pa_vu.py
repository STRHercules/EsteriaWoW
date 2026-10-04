"""Break the donor's Pa/Vu head files down by kind."""
from __future__ import annotations

import collections
import ctypes
import re
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

DONOR = Path(r"G:\Eunoia\Client\data")
DONOR_ORDER = ("common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq")
CLIENT = REPO / "3.3.5a - Dev/Data"
OUR_ORDER = ("common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ")
HEAD = "item\\objectcomponents\\head\\"


def names(root: Path, order, pattern: str) -> dict[str, int]:
    storm = Storm(DLL_DEFAULT)
    out: dict[str, int] = {}
    regex = re.compile(pattern, re.IGNORECASE)
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
                listing = []
        finally:
            storm.dll.SFileCloseArchive(handle)
        for entry in listing:
            lower = entry[0].lower()
            if lower.startswith(HEAD) and regex.search(entry[0][len(HEAD):]):
                out[entry[0]] = max(out.get(entry[0], 0), entry[1])
    return out


def main() -> None:
    donor = names(DONOR, DONOR_ORDER, r"_(Pa|Vu)[MF][0-9]*\.(m2|skin|mdx)$")
    ours = names(CLIENT, OUR_ORDER, r"_Hu[MF][0-9]*\.(m2|skin|mdx)$")
    for label, table in (("donor Pa/Vu", donor), ("ours Hu", ours)):
        kinds = collections.Counter()
        stems = set()
        total = 0
        for name, size in table.items():
            tail = name[len(HEAD):]
            kind = "m2" if tail.lower().endswith(".m2") else (
                "skin" + tail[-8:-5].strip("-") if ".skin" in tail.lower() else "other")
            kinds[re.sub(r"_[^_]*$", "", tail) and kind] += 1
            stems.add(re.sub(r"_[MF]\d*\.(m2|skin|mdx)$", "", tail, flags=re.IGNORECASE))
            total += size
        print(f"{label}: {len(table)} files, {len(stems)} stems, {total / 1048576:.1f} MB")
        for kind, count in sorted(kinds.items()):
            print(f"    {kind}: {count}")


if __name__ == "__main__":
    main()
