"""Diff Patch-Y ChrRaces against the backup: only field 6 should move."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_DIR = REPO / "3.3.5a - Dev/Backups"
KEY = "DBFilesClient\\ChrRaces.dbc"


def read_archive(path: Path, key: str) -> bytes:
    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
        raise SystemExit(f"cannot open {path}")
    try:
        return storm.read(handle, key)
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    backups = sorted(BACKUP_DIR.glob("patch-y-before-item-component-prefixes-*/Patch-Y.MPQ"))
    if not backups:
        raise SystemExit("no backup found")
    backup = backups[-1]
    print(f"backup: {backup}")
    before = Wdbc(read_archive(backup, KEY))
    after = Wdbc(read_archive(PATCH_Y, KEY))
    assert before.record_size == after.record_size == 276
    assert len(before.rows) == len(after.rows) == 30
    differences = 0
    for old, new in zip(before.rows, after.rows):
        for field, (left, right) in enumerate(zip(old, new)):
            if left != right:
                differences += 1
                if field != 6:
                    print(f"  UNEXPECTED race {old[0]} field {field}: {left} -> {right}")
                else:
                    print(f"  race {new[0]:>2}: prefix {before.text(left)!r} -> {after.text(right)!r}")
    print(f"{differences} field differences (all should be field 6)")
    assert differences == 11, differences

    ids = [row[0] for row in after.rows]
    print("race ids:", ids)
    for row in after.rows:
        prefix = after.text(row[6])
        if prefix:
            assert len(prefix) == 2 or prefix == "Bk", (row[0], prefix)
    print("all non-empty prefixes are two characters")


if __name__ == "__main__":
    main()
