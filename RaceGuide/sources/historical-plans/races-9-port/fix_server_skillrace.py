"""Let the ported races inherit their host race's rows in the server's SkillRaceClassInfo.dbc.

`Player::LearnDefaultSkill()` (Player.cpp) starts with
`SkillRaceClassInfoEntry const* rcInfo = GetSkillRaceClassInfo(skill, race, class); if (!rcInfo) return;`
so a skill listed in `playercreateinfo_skills` is only actually applied when this DBC has a row
whose RaceMask/ClassMask match. The stock rows stop at race 14 (masks 16383 / 14592 / ...), so
every custom race silently learned nothing: a Vulpera Hunter ends up without Axes (44) or Bows
(45), and `Player::CanUseItem()` reports EQUIP_ERR_NO_REQUIRED_PROFICIENCY
(`GetSkillValue(proto->RequiredSkill) == 0`) when they try to equip their starting gear.

Each custom race inherits the rows of the stock race whose starting zone it uses:

    14 Broken, 16 Eredar, 20 Vulpera, 22 Zandalari, 28 Dracthyr  ->  2 Orc      (Durotar)
    17 Nightborne, 30 Illidari                                    -> 10 Blood Elf (Eversong)
    18 Pandaren, 19 Void Elf                                      ->  1 Human    (Elwynn)
    21 Lightforged Draenei                                        -> 11 Draenei (Azuremyst)
    23 Dark Iron Dwarf, 29 Kul Tiran                              ->  3 Dwarf    (Dun Morogh)

Run with --dry-run to see the row deltas, or --write to copy the patched file into the
worldserver's data volume (a backup of the original is kept next to this script).
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
HERE = Path(__file__).resolve().parent
OURS = HERE / "server-SkillRaceClassInfo.dbc"
KEEP = REPO / "modules/mod-custom-server/data/dbc/SkillRaceClassInfo.dbc"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
CONTAINER = "ac-worldserver"
CONTAINER_PATH = "/azerothcore/env/dist/data/dbc/SkillRaceClassInfo.dbc"

# custom race -> stock race whose starting zone it uses
HOSTS = {
    14: 2, 16: 2, 20: 2, 22: 2, 28: 2,
    17: 10, 30: 10,
    18: 1, 19: 1,
    21: 11,
    23: 3, 29: 3,
    31: 4,
}


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not (args.dry_run or args.write):
        raise SystemExit("pass --dry-run or --write")

    data = OURS.read_bytes()
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data, 0)
    if magic != b"WDBC" or record_size != fields * 4:
        raise SystemExit("unexpected DBC layout")
    rows = [list(struct.unpack_from(f"<{fields}I", data, 20 + index * record_size)) for index in range(count)]
    pool = data[20 + count * record_size : 20 + count * record_size + string_size]

    changed = 0
    # Every non-zero mask gets the custom race bits. The starting outfits do not follow the
    # host race's kit (a Vulpera Hunter carries a crossbow the Orc block never grants), and the
    # skill list itself is already decided per race/class by `playercreateinfo_skills`, so the
    # permissive mask is what makes those rows apply.
    for row in rows:
        before = row[2]
        if row[2]:
            for race in HOSTS:
                row[2] |= 1 << (race - 1)
        if row[2] != before:
            changed += 1
            if changed <= 12:
                print(f"  skill {row[1]:>4}: raceMask {before:#010x} -> {row[2]:#010x}")
    print(f"rows widened: {changed}")
    payload = pack(rows, fields, record_size, pool)

    KEEP.parent.mkdir(parents=True, exist_ok=True)
    KEEP.write_bytes(payload)
    print(f"patched copy written to {KEEP}")
    if args.dry_run:
        print("dry run - worldserver data volume untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"server-dbc-before-skillrace-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OURS, backup / "SkillRaceClassInfo.dbc")
    subprocess.run(["docker", "cp", str(KEEP), f"{CONTAINER}:{CONTAINER_PATH}"], check=True)
    print(f"copied into {CONTAINER}:{CONTAINER_PATH}, original backed up to {backup}")


if __name__ == "__main__":
    main()
