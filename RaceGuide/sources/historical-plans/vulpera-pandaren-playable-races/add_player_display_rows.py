"""Clone Pandaren/Vulpera display rows into the 16-bit player display range."""

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

SOURCE_TO_TARGET = {
    141687: 60004,  # Pandaren male
    141688: 60005,  # Pandaren female
    141254: 60006,  # Vulpera male
    141255: 60007,  # Vulpera female
}


def find_entry(archive: Path, wanted: str) -> str:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        matches = [
            name for name, *_ in storm.list_files(handle) if name.casefold() == wanted.casefold()
        ]
    finally:
        storm.dll.SFileCloseArchive(handle)
    if len(matches) != 1:
        raise ValueError(f"expected one entry for {wanted}, found {matches}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    name = find_entry(args.patch_c, "dbfilesclient\\CreatureDisplayInfo.dbc")
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        payload = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)
    table = RawWdbc(payload)
    rows = {int.from_bytes(r[:4], "little"): r for r in table.records}

    records = list(table.records)
    for source_id, target_id in SOURCE_TO_TARGET.items():
        if target_id in rows:
            print(f"{target_id} already present")
            continue
        source = rows.get(source_id)
        if source is None:
            raise ValueError(f"source display {source_id} not found")
        records.append(target_id.to_bytes(4, "little") + source[4:])
    # WDBC lookups assume id order, so keep the cloned rows inline.
    records.sort(key=lambda record: int.from_bytes(record[:4], "little"))
    updated = table.build(records)
    print(f"CreatureDisplayInfo: {table.count} -> {RawWdbc(updated).count} rows")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, {name: updated})
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    handle = storm.open_archive(staged)
    try:
        names = {entry.casefold(): entry for entry, *_ in storm.list_files(handle)}
        verify = RawWdbc(storm.read(handle, names[name.casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    rows = {int.from_bytes(r[:4], "little"): r for r in verify.records}
    for source_id, target_id in SOURCE_TO_TARGET.items():
        model = int.from_bytes(rows[target_id][4:8], "little")
        source_model = int.from_bytes(rows[source_id][4:8], "little")
        print(f"   {target_id}: model={model} (source {source_id} model={source_model})")
        if model != source_model:
            raise SystemExit("clone mismatch")


if __name__ == "__main__":
    main()
