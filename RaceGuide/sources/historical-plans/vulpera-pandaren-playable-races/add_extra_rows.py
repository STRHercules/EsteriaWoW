"""Add CreatureDisplayInfoExtra rows for Pandaren/Vulpera like the working Sethrak rows."""

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

EXTRA_ROWS = {
    45441: (18, 0),
    45442: (18, 1),
    45443: (20, 0),
    45444: (20, 1),
}
DISPLAY_TO_EXTRA = {60004: 45441, 60005: 45442, 60006: 45443, 60007: 45444}
TEMPLATE = 45439


def entry_name(storm: Storm, archive: Path, wanted: str, handle) -> str:
    names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
    return names[wanted.casefold()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        extra_name = entry_name(storm, args.patch_c, "dbfilesclient\\CreatureDisplayInfoExtra.dbc", handle)
        display_name = entry_name(storm, args.patch_c, "dbfilesclient\\CreatureDisplayInfo.dbc", handle)
        extra_payload = storm.read(handle, extra_name)
        display_payload = storm.read(handle, display_name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    extras = RawWdbc(extra_payload)
    template = next(r for r in extras.records if int.from_bytes(r[:4], "little") == TEMPLATE)
    extra_records = list(extras.records)
    for extra_id, (race, gender) in EXTRA_ROWS.items():
        values = bytearray(template)
        values[0:4] = extra_id.to_bytes(4, "little")
        values[4:8] = race.to_bytes(4, "little")
        values[8:12] = gender.to_bytes(4, "little")
        extra_records.append(bytes(values))
    updated_extras = extras.build(extra_records)
    print(f"CreatureDisplayInfoExtra: {extras.count} -> {RawWdbc(updated_extras).count} rows")

    displays = RawWdbc(display_payload)
    display_records = []
    linked = 0
    for record in displays.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id in DISPLAY_TO_EXTRA:
            values = bytearray(record)
            values[12:16] = DISPLAY_TO_EXTRA[row_id].to_bytes(4, "little")
            record = bytes(values)
            linked += 1
        display_records.append(record)
    updated_displays = displays.build(display_records)
    print(f"CreatureDisplayInfo: linked {linked} rows to their extra rows")

    updates = {extra_name: updated_extras, display_name: updated_displays}
    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    handle = storm.open_archive(staged)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        verify_extras = RawWdbc(storm.read(handle, names[extra_name.casefold()]))
        verify_displays = RawWdbc(storm.read(handle, names[display_name.casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    rows = {int.from_bytes(r[:4], "little"): r for r in verify_extras.records}
    for extra_id, (race, gender) in EXTRA_ROWS.items():
        print(
            f"   extra {extra_id}: race={int.from_bytes(rows[extra_id][4:8], 'little')} "
            f"gender={int.from_bytes(rows[extra_id][8:12], 'little')}"
        )
    displays_by_id = {int.from_bytes(r[:4], "little"): r for r in verify_displays.records}
    for display_id, extra_id in DISPLAY_TO_EXTRA.items():
        value = int.from_bytes(displays_by_id[display_id][12:16], "little")
        print(f"   display {display_id}: extraId={value}")
        if value != extra_id:
            raise SystemExit("link mismatch")


if __name__ == "__main__":
    main()
