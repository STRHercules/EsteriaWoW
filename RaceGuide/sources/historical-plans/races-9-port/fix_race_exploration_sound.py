"""Set ChrRaces.ExplorationSoundID (field 3) on the ported races.

Perfect correlation across the client's table: races 1-15 all carry a non-zero
ExplorationSoundID (4140-4147) and render portraits / know their languages, while races
16-30 - including Vulpera and Pandaren - carry 0 and do neither. Broken (14, 4141) is the
user-confirmed working case. Copy a same-faction stock race's value.
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

HORDE_SOUND = 4141      # Orc's ExplorationSoundID
ALLIANCE_SOUND = 4140   # Human's ExplorationSoundID
HORDE_RACES = (16, 17, 20, 22, 28, 30)
ALLIANCE_RACES = (18, 19, 21, 23, 29)


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

    changed = 0
    for row in races.rows:
        want = HORDE_SOUND if row[0] in HORDE_RACES else (ALLIANCE_SOUND if row[0] in ALLIANCE_RACES else None)
        if want is None or row[3] == want:
            continue
        print(f"  race {row[0]:>2} {races.text(row[11]):<22} ExplorationSoundID {row[3]} -> {want}")
        row[3] = want
        changed += 1
    entries[RACES_KEY] = pack(races.rows, races.fields, races.record_size, races.strings)
    print(f"rows updated: {changed}")

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-exploration-sound-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {RACES_KEY: entries[RACES_KEY]})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
