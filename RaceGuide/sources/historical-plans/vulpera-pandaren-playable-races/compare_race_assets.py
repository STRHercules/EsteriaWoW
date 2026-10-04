"""Compare Vulpera/Pandaren asset coverage between the donor extraction and Patch-C."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

DONOR = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq")
LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
ROOTS = ("Character\\Pandaren\\", "Character\\vulpera\\")


def suffix_counts(names: list[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for name in names:
        counts[Path(name).suffix.casefold() or "<none>"] += 1
    return counts


def main() -> None:
    donor_names = [
        str(path.relative_to(DONOR)).replace("/", "\\")
        for path in DONOR.rglob("*")
        if path.is_file() and path.suffix.casefold() != ".mpq"
    ]
    donor = [n for n in donor_names if any(n.casefold().startswith(root.casefold()) for root in ROOTS)]

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        archive = [name for name, *_ in storm.list_files(handle)]
    finally:
        storm.dll.SFileCloseArchive(handle)
    packed = [n for n in archive if any(n.casefold().startswith(root.casefold()) for root in ROOTS)]

    print(f"donor files: {len(donor)}  Patch-C files: {len(packed)}")
    print(f"donor by extension: {dict(suffix_counts(donor))}")
    print(f"Patch-C by extension: {dict(suffix_counts(packed))}")

    packed_index = {n.casefold() for n in packed}
    missing = sorted(n for n in donor if n.casefold() not in packed_index)
    print(f"donor files missing from Patch-C: {len(missing)}")
    for name in missing[:20]:
        print(f"    {name}")


if __name__ == "__main__":
    main()
