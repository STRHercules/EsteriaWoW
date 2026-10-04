"""Point the client's ChrRaces rows at the same 16-bit display ids the server sends."""

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

DISPLAYS = {18: (60004, 60005), 20: (60006, 60007)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        name = names["dbfilesclient\\chrraces.dbc"]
        payload = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    table = RawWdbc(payload)
    records = []
    for record in table.records:
        race = int.from_bytes(record[:4], "little")
        if race in DISPLAYS:
            male, female = DISPLAYS[race]
            values = bytearray(record)
            values[16:20] = male.to_bytes(4, "little")
            values[20:24] = female.to_bytes(4, "little")
            record = bytes(values)
        records.append(record)
    updated = table.build(records)

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
        race = int.from_bytes(record[:4], "little")
        if race in DISPLAYS:
            print(
                f"   race {race}: display="
                f"{int.from_bytes(record[16:20], 'little')}/"
                f"{int.from_bytes(record[20:24], 'little')}"
            )


if __name__ == "__main__":
    main()
