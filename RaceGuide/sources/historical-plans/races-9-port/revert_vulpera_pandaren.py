"""Revert the Vulpera/Pandaren client changes (they crash the client on Foxbow).

Restores the state that was stable before the alignment: the races point back at their
141xxx display rows, the display->extra links are cleared again and ExplorationSoundID
returns to 0. The nine ported races keep their 60008-60025 alignment and extras.
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
RACES_KEY = "DBFilesClient\\ChrRaces.dbc"
DISPLAY_KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"

OLD_DISPLAY_IDS = {18: (141687, 141688), 20: (141254, 141255)}
CLEAR_EXTRA_DISPLAYS = (60004, 60005, 60006, 60007)


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    entries = load_entries(storm)

    races = Wdbc(entries[RACES_KEY])
    for row in races.rows:
        old = OLD_DISPLAY_IDS.get(row[0])
        if not old:
            continue
        if (row[4], row[5]) != old:
            print(f"  race {row[0]} {races.text(row[11])}: display {row[4]}/{row[5]} -> {old[0]}/{old[1]}")
            row[4], row[5] = old
        if row[3] != 0:
            print(f"  race {row[0]} {races.text(row[11])}: ExplorationSoundID {row[3]} -> 0")
            row[3] = 0
    entries[RACES_KEY] = pack(races.rows, races.fields, races.record_size, races.strings)

    displays = Wdbc(entries[DISPLAY_KEY])
    for row in displays.rows:
        if row[0] in CLEAR_EXTRA_DISPLAYS and row[3]:
            print(f"  display {row[0]}: extra {row[3]} -> 0")
            row[3] = 0
    entries[DISPLAY_KEY] = pack(displays.rows, displays.fields, displays.record_size, displays.strings)

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-vulpera-revert-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {RACES_KEY: entries[RACES_KEY], DISPLAY_KEY: entries[DISPLAY_KEY]})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
