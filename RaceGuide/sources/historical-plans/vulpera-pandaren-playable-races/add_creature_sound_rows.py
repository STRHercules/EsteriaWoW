"""Add CreatureSoundData rows for the Vulpera/Pandaren player models.

CreatureModelData.SoundID points at CreatureSoundData. Rows 6278/6279 (Vulpera)
and 4012/4080 (Pandaren) came from the Ascension donor and are absent from this
client, which leaves the world unit-sound lookup empty. Copy stock player rows
whose SoundEntries all exist locally.
"""

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

# target id -> stock source id (Goblin male/female, Tauren male/female)
COPIES = {6278: 1128, 6279: 294, 4012: 59, 4080: 60}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        name = names["dbfilesclient\\creaturesounddata.dbc"]
        payload = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    table = RawWdbc(payload)
    records = list(table.records)
    by_id = {RawWdbc._value(record, 0, 4): record for record in records}

    added = 0
    for target, source in COPIES.items():
        if target in by_id:
            print(f"   {target}: already present, skipping")
            continue
        source_record = by_id.get(source)
        if source_record is None:
            raise SystemExit(f"source row {source} missing")
        records.append(RawWdbc._replace(source_record, 0, 4, target))
        added += 1
        print(f"   {target}: copied from {source}")
    records.sort(key=lambda record: RawWdbc._value(record, 0, 4))
    updated = table.build(records)
    print(f"rows {table.count} -> {len(records)} (added {added})")

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
    ids = [RawWdbc._value(record, 0, 4) for record in verify.records]
    print(f"verified rows={verify.count} sorted={ids == sorted(ids)}")
    for target in COPIES:
        print(f"   {target}: present={target in ids}")


if __name__ == "__main__":
    main()
