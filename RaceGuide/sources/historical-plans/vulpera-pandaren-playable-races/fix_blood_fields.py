"""Normalise blood fields on the custom player display rows to stock player values."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc, _stage_archive_updates  # noqa: E402

TARGETS = {60004, 60005, 60006, 60007, 141687, 141688, 141254, 141255}
BLOOD_LEVEL = 0
BLOOD_ID = 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        name = names["dbfilesclient\\creaturedisplayinfo.dbc"]
        payload = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    table = RawWdbc(payload)
    records = []
    changed = 0
    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id in TARGETS:
            values = bytearray(record)
            values[9 * 4 : 10 * 4] = BLOOD_LEVEL.to_bytes(4, "little")
            values[10 * 4 : 11 * 4] = BLOOD_ID.to_bytes(4, "little")
            record = bytes(values)
            changed += 1
        records.append(record)
    updated = table.build(records)
    print(f"normalised blood fields on {changed} display rows")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, {name: updated})
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    check = Storm(DLL_DEFAULT)
    handle = check.open_archive(staged)
    try:
        verify = RawWdbc(check.read(handle, name))
    finally:
        check.dll.SFileCloseArchive(handle)
    for record in verify.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id in (60004, 60006):
            print(
                f"   {row_id}: bloodLevel={int.from_bytes(record[36:40], 'little')} "
                f"bloodId={int.from_bytes(record[40:44], 'little')}"
            )


if __name__ == "__main__":
    main()
