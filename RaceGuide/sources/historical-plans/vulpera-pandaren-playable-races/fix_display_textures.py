"""Clear the corrupted texture overrides on the Pandaren/Vulpera display rows."""

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

TARGET_IDS = {141254, 141255, 141687, 141688, 60004, 60005, 60006, 60007}
TEXTURE_FIELDS = (6, 7, 8)


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
    cleared = 0
    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id in TARGET_IDS:
            values = bytearray(record)
            for field in TEXTURE_FIELDS:
                if int.from_bytes(values[field * 4 : field * 4 + 4], "little") != 0:
                    values[field * 4 : field * 4 + 4] = b"\x00\x00\x00\x00"
                    cleared += 1
            record = bytes(values)
        records.append(record)
    updated = table.build(records)
    print(f"cleared {cleared} texture offsets across {len(TARGET_IDS)} display rows")

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
        if row_id in TARGET_IDS:
            offsets = [
                int.from_bytes(record[f * 4 : f * 4 + 4], "little") for f in TEXTURE_FIELDS
            ]
            print(f"   {row_id}: texture offsets {offsets}")
            if any(offsets):
                raise SystemExit("texture offsets not cleared")


if __name__ == "__main__":
    main()
