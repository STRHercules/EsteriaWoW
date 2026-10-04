"""Move the nine ported races out of the 900xx display-id band.

AzerothCore stores a player's display id in `PlayerInfo::displayId_m/f`, which is a
`uint16` (src/server/game/Entities/Player/Player.h), while `ChrRaces` itself is
`uint32`. 90004 therefore wrapped to 24468 and the client drew
`Creature\\LasherOrchid\\LasherOrchid.mdx` for a Nightborne. Sethrak (60000/60001),
Broken (60002/60003), Pandaren (60004/60005) and Vulpera (60006/60007) already sit
in the sub-65536 band; this rewrites the client half for the nine ported races into
the free 60008-60025 slots, matching the SQL/DB change made by the same fix.
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

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from fix_patch_y import load_entries  # noqa: E402

DATA = REPO / "3.3.5a - Dev/Data"
PATCH_Y = DATA / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
TABLE = "DBFilesClient\\CreatureDisplayInfo.dbc"

RACE_DISPLAY_IDS = {
    16: (60008, 60009),  # Eredar
    17: (60010, 60011),  # Nightborne
    19: (60012, 60013),  # Void Elf
    21: (60014, 60015),  # Lightforged Draenei
    22: (60016, 60017),  # Zandalari Troll
    23: (60018, 60019),  # Dark Iron Dwarf
    28: (60020, 60021),  # Dracthyr
    29: (60022, 60023),  # Kul Tiran
    30: (60024, 60025),  # Illidari
}
OLD_DISPLAY_IDS = {
    16: (90002, 90003),
    17: (90004, 90005),
    19: (90008, 90009),
    21: (90012, 90013),
    22: (90014, 90015),
    23: (90016, 90017),
    28: (90022, 90023),
    29: (90024, 90025),
    30: (90026, 90027),
}


def rekey(data: bytes) -> tuple[bytes, list[tuple[int, int]]]:
    mapping = {
        old: new
        for race in RACE_DISPLAY_IDS
        for old, new in zip(OLD_DISPLAY_IDS[race], RACE_DISPLAY_IDS[race])
    }
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data)
    if magic != b"WDBC":
        raise SystemExit("not a WDBC payload")
    start = 20
    records = [bytearray(data[start + i * record_size:start + (i + 1) * record_size]) for i in range(count)]
    pool = data[start + count * record_size:start + count * record_size + string_size]
    changes = []
    for record in records:
        row_id = struct.unpack_from("<I", record, 0)[0]
        if row_id in mapping:
            struct.pack_into("<I", record, 0, mapping[row_id])
            changes.append((row_id, mapping[row_id]))
    # the client indexes rows by id, so hand it an ordered table
    records.sort(key=lambda record: struct.unpack_from("<I", record, 0)[0])
    body = b"".join(bytes(record) for record in records)
    return struct.pack("<4s4I", magic, count, fields, record_size, string_size) + body + pool, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    entries = load_entries(storm)
    payload, changes = rekey(entries[TABLE])

    expected = {old for ids in OLD_DISPLAY_IDS.values() for old in ids}
    found = {old for old, _ in changes}
    if found != expected:
        raise SystemExit(f"expected {sorted(expected)}, found {sorted(found)}")

    for old, new in sorted(changes):
        print(f"  {old} -> {new}")
    print(f"{TABLE}: re-keyed {len(changes)} rows")

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-display-id-fix-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {TABLE: payload})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
