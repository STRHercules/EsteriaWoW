"""Point the remaining custom races' client rows at the display ids the server sends.

Broken (race 14) works: client `ChrRaces` says 60002/60003 and the server sends exactly
that. Vulpera and Pandaren use 141254/141255 and 141687/141688 in the client while the
server sends 60006/60007 and 60004/60005, so the client never maps the player's display id
back to a race - no portrait, and no known languages (the chat gate). This aligns them, the
same way the nine ported races were aligned, and re-links the extras the port dropped.
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

# race -> (male, female) display ids the server sends
ALIGN = {18: (60004, 60005), 20: (60006, 60007)}
# display -> extra rows created by the original Vulpera/Pandaren work
EXTRA_LINKS = {60004: 45441, 60005: 45442, 60006: 45443, 60007: 45444}


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
        want = ALIGN.get(row[0])
        if not want:
            continue
        if (row[4], row[5]) != want:
            print(f"  race {row[0]} {races.text(row[11])}: display {row[4]}/{row[5]} -> {want[0]}/{want[1]}")
            row[4], row[5] = want
    entries[RACES_KEY] = pack(races.rows, races.fields, races.record_size, races.strings)

    displays = Wdbc(entries[DISPLAY_KEY])
    for row in displays.rows:
        target = EXTRA_LINKS.get(row[0])
        if target and row[3] != target:
            print(f"  display {row[0]}: extra {row[3]} -> {target}")
            row[3] = target
    entries[DISPLAY_KEY] = pack(displays.rows, displays.fields, displays.record_size, displays.strings)

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-vulpera-pandaren-align-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {RACES_KEY: entries[RACES_KEY], DISPLAY_KEY: entries[DISPLAY_KEY]})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
