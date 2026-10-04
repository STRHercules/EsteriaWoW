"""Hash-compare race model/skin/anim files between donor extraction and Patch-C."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

DONOR = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq")
LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
ROOTS = ("character\\pandaren\\", "character\\vulpera\\")
SUFFIXES = (".m2", ".skin", ".anim")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        entries = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        mismatches = []
        missing = []
        checked = 0
        for path in DONOR.rglob("*"):
            if not path.is_file() or path.suffix.casefold() not in SUFFIXES:
                continue
            relative = str(path.relative_to(DONOR)).replace("/", "\\")
            if not any(relative.casefold().startswith(root) for root in ROOTS):
                continue
            packed = entries.get(relative.casefold())
            if packed is None:
                missing.append(relative)
                continue
            donor_bytes = path.read_bytes()
            packed_bytes = storm.read(handle, packed)
            checked += 1
            if digest(donor_bytes) != digest(packed_bytes) or len(donor_bytes) != len(packed_bytes):
                mismatches.append((relative, len(donor_bytes), len(packed_bytes)))
    finally:
        storm.dll.SFileCloseArchive(handle)

    print(f"checked {checked} model/skin/anim files")
    print(f"missing: {len(missing)}")
    for name in missing[:10]:
        print(f"    MISSING {name}")
    print(f"byte mismatches: {len(mismatches)}")
    for name, donor_size, packed_size in mismatches[:20]:
        print(f"    {name}: donor={donor_size} packed={packed_size}")


if __name__ == "__main__":
    main()
