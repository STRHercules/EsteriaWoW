"""Give the nine ported races the same display -> extra link the working custom races have.

`add_extra_rows.py` from the Vulpera/Pandaren work shows the contract: each custom race's
player display row carries a `DisplayidExtra` that points at a `CreatureDisplayInfoExtra`
row whose RaceID/Gender match the race. Vulpera/Pandaren were built that way (60006 ->
45443, race 20), and their unit frame portraits render. The ported races were shipped with
`DisplayidExtra = 0` (and their dangling references were later cleared), which is why their
portraits come up empty.

This adds extra rows 45445-45462 (race 16..30, male/female) cloned from the Sethrak template
that the working rows use, and links the 60008-60025 display rows to them.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm, Wdbc  # noqa: E402
from fix_patch_y import load_entries  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
EXTRA_KEY = "DBFilesClient\\CreatureDisplayInfoExtra.dbc"
DISPLAY_KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"

TEMPLATE_EXTRA = 45439          # working Sethrak row used as the donor template
FIRST_NEW_EXTRA = 45445
# race -> (male display, female display); extras are assigned in race order, male then female
RACES = (16, 17, 19, 21, 22, 23, 28, 29, 30)
DISPLAYS = {
    16: (60008, 60009), 17: (60010, 60011), 19: (60012, 60013), 21: (60014, 60015),
    22: (60016, 60017), 23: (60018, 60019), 28: (60020, 60021), 29: (60022, 60023),
    30: (60024, 60025),
}


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    entries = load_entries(storm)
    extras = Wdbc(entries[EXTRA_KEY])
    displays = Wdbc(entries[DISPLAY_KEY])

    template = extras.row(TEMPLATE_EXTRA)
    next_id = FIRST_NEW_EXTRA
    links: dict[int, int] = {}
    new_rows: list[list[int]] = []
    for race in RACES:
        for gender, display_id in enumerate(DISPLAYS[race]):
            row = list(template)
            row[0] = next_id
            row[1] = race
            row[2] = gender
            new_rows.append(row)
            links[display_id] = next_id
            print(f"  extra {next_id}: race={race} gender={gender} -> display {display_id}")
            next_id += 1

    existing = {r[0] for r in extras.rows}
    rows = [r for r in extras.rows if r[0] not in {row[0] for row in new_rows}] + new_rows
    rows.sort(key=lambda r: r[0])
    entries[EXTRA_KEY] = pack(rows, extras.fields, extras.record_size, extras.strings)

    linked = 0
    for display in displays.rows:
        target = links.get(display[0])
        if target is None:
            continue
        if display[3] != target:
            print(f"  display {display[0]}: extra {display[3]} -> {target}")
            display[3] = target
            linked += 1
    entries[DISPLAY_KEY] = pack(displays.rows, displays.fields, displays.record_size, displays.strings)
    print(f"extras added: {len(new_rows)} (existing {len(existing)}), display rows linked: {linked}")

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-race-extras-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {EXTRA_KEY: entries[EXTRA_KEY], DISPLAY_KEY: entries[DISPLAY_KEY]})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
