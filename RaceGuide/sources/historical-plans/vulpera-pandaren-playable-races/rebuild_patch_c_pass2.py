"""Pass 2: stock preview outfits, revert Ascension item rows, restore Broken rows."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import (  # noqa: E402
    RawWdbc,
    _rebase_string_records,
    _stage_archive_updates,
    _start_outfit_display_ids,
)

LEGACY = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\PATCH-A.MPQ")
OUTFIT_SOURCE = {18: 1, 20: 2}
UNION_TABLES = ("CharHairGeosets", "CharHairTextures", "NameGen")


def read_entry(archive: Path, name: str) -> bytes:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)


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


def stock_outfits(data: bytes) -> bytes:
    table = RawWdbc(data)
    source_rows = {
        (record[5], record[6], record[4]): record for record in table.records
    }
    records = []
    replaced = 0
    dropped = 0
    for record in table.records:
        race = record[4]
        donor_race = OUTFIT_SOURCE.get(race)
        if donor_race is None:
            records.append(record)
            continue
        template = source_rows.get((record[5], record[6], donor_race))
        if template is None:
            dropped += 1
            continue
        values = bytearray(template)
        values[0:4] = record[0:4]
        values[4] = race
        records.append(bytes(values))
        replaced += 1
    return table.build(records), replaced, dropped


def revert_item_rows(current: bytes, original: bytes, donor_ids: set[int]) -> tuple[bytes, int, int]:
    table = RawWdbc(current)
    source = {int.from_bytes(r[:4], "little"): r for r in RawWdbc(original).records}
    records = []
    restored = dropped = 0
    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id not in donor_ids:
            records.append(record)
            continue
        replacement = source.get(row_id)
        if replacement is None:
            dropped += 1
            continue
        records.append(replacement)
        restored += 1
    return table.build(records), restored, dropped


def union_rows(current: bytes, legacy: bytes, table_name: str) -> tuple[bytes, int]:
    table = RawWdbc(current)
    old = RawWdbc(legacy)
    existing = {int.from_bytes(r[:4], "little") for r in table.records}
    extras = [r for r in old.records if int.from_bytes(r[:4], "little") not in existing]
    if not extras:
        return current, 0
    rebased, extra_strings = _rebase_string_records(
        table_name, extras, old.strings, len(table.strings)
    )
    return table.build([*table.records, *rebased], table.strings + extra_strings), len(extras)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--stock-item-table", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    updates: dict[str, bytes] = {}

    outfit_name = find_entry(args.patch_c, "dbfilesclient\\CharStartOutfit.dbc")
    outfit_bytes = read_entry(args.patch_c, outfit_name)
    current_outfits = RawWdbc(outfit_bytes)
    new_outfits, replaced, dropped_outfits = stock_outfits(outfit_bytes)
    if replaced != 40:
        raise ValueError(f"expected 40 target outfit rows, replaced {replaced}")
    updates[outfit_name] = new_outfits
    print(
        f"CharStartOutfit: replaced {replaced} rows with stock Human/Orc outfits, "
        f"dropped {dropped_outfits} non-Esteria class rows"
    )

    donor_ids = {
        value
        for value in _start_outfit_display_ids(current_outfits.records)
        if value not in (0, 0xFFFFFFFF)
    }
    item_name = find_entry(args.patch_c, "dbfilesclient\\ItemDisplayInfo.dbc")
    items, restored, dropped = revert_item_rows(
        read_entry(args.patch_c, item_name),
        args.stock_item_table.read_bytes(),
        donor_ids,
    )
    updates[item_name] = items
    print(f"ItemDisplayInfo: restored {restored} rows, dropped {dropped} Ascension-only rows")

    for table_name in UNION_TABLES:
        name = find_entry(args.patch_c, f"dbfilesclient\\{table_name}.dbc")
        merged, added = union_rows(
            read_entry(args.patch_c, name),
            read_entry(LEGACY, name),
            table_name,
        )
        updates[name] = merged
        print(f"{table_name}: restored {added} legacy rows")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(staged)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        verified_outfits = RawWdbc(storm.read(handle, names[outfit_name.casefold()]))
        verified_items = RawWdbc(storm.read(handle, names[item_name.casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    target_ids = {
        int.from_bytes(record[o : o + 4], "little")
        for record in verified_outfits.records
        if record[4] in OUTFIT_SOURCE
        for o in range(104, 200, 4)
    }
    target_ids.discard(0)
    target_ids.discard(0xFFFFFFFF)
    leftover = sorted(target_ids - {int.from_bytes(r[:4], "little") for r in verified_items.records})
    print(f"preview display ids for 18/20: {len(target_ids)} unresolved: {leftover[:8]}")
    if leftover:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
