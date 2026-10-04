"""Compare each custom race's starting outfit with the weapon skills it is granted.

The server's `CharStartOutfit.dbc` (data volume, not the client's copy) drives the items a new
character receives; `Player::CanUseItem()` refuses anything whose `RequiredSkill` the character
has no value in, so an outfit the race's skill block was not written for produces "you are not
proficient" on the character's own starting weapon.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
HERE = Path(__file__).resolve().parent
OUTFIT = HERE / "server-CharStartOutfit.dbc"
CUSTOM_RACES = (14, 16, 17, 18, 19, 20, 21, 22, 23, 28, 29, 30)
MAX_ITEMS = 24
CLASS_NAMES = {1: "Warrior", 2: "Paladin", 3: "Hunter", 4: "Rogue", 5: "Priest",
               6: "DeathKnight", 7: "Shaman", 8: "Mage", 9: "Warlock", 11: "Druid"}


def mysql(query: str) -> list[list[str]]:
    result = subprocess.run(
        ["docker", "exec", "ac-database", "mysql", "-uroot", "-ppassword", "-N", "-e", query],
        capture_output=True, text=True, check=True,
    )
    return [line.split("\t") for line in result.stdout.strip().splitlines() if line]


def outfits() -> dict[tuple[int, int], list[int]]:
    data = OUTFIT.read_bytes()
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data, 0)
    assert magic == b"WDBC"
    result: dict[tuple[int, int], list[int]] = {}
    for index in range(count):
        base = 20 + index * record_size
        packed = struct.unpack_from("<I", data, base + 4)[0]
        race = packed & 0xFF
        klass = (packed >> 8) & 0xFF
        if race not in CUSTOM_RACES:
            continue
        items = [value for value in struct.unpack_from(f"<{MAX_ITEMS}I", data, base + 8)
                 if 0 < value < 0xFFFFFFFF]
        result[(race, klass)] = items
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql", action="store_true", help="emit the fix statements")
    args = parser.parse_args()

    table = outfits()
    skill_rows = mysql(
        "SELECT raceMask, classMask, skill FROM acore_world.playercreateinfo_skills;"
    )
    all_rows = [(int(a), int(b), int(c)) for a, b, c in skill_rows]

    def granted(race: int, klass: int) -> set[int]:
        race_bit = 1 << (race - 1)
        class_bit = 1 << (klass - 1)
        return {
            skill for race_mask, class_mask, skill in all_rows
            if (race_mask & race_bit) and (class_mask == 0 or (class_mask & class_bit))
        }

    fixes = []
    with_problems = 0
    for (race, klass), items in sorted(table.items()):
        ids = ",".join(str(value) for value in items)
        rows = mysql(
            f"SELECT entry, name, RequiredSkill, RequiredSkillRank, RequiredSpell, AllowableRace, AllowableClass "
            f"FROM acore_world.item_template WHERE entry IN ({ids});"
        )
        missing_by_class: dict[tuple[int, int], set[int]] = {}
        problems = []
        for entry, name, req_skill, req_rank, req_spell, allow_race, allow_class in (
            (int(a), b, int(c), int(d), int(e), int(f), int(g)) for a, b, c, d, e, f, g in rows
        ):
            race_allowed = allow_race == -1 or (allow_race & (1 << (race - 1)))
            class_allowed = allow_class == -1 or (allow_class & (1 << (klass - 1)))
            notes = []
            if not race_allowed:
                notes.append(f"AllowableRace {allow_race} excludes race {race}")
            if not class_allowed:
                notes.append(f"AllowableClass {allow_class} excludes class {klass}")
            if req_skill and req_skill not in granted(race, klass):
                missing_by_class.setdefault((race, klass), set()).add(req_skill)
                notes.append(f"needs skill {req_skill} (rank {req_rank})")
            if req_spell:
                notes.append(f"needs spell {req_spell}")
            if notes:
                problems.append((entry, name, notes))
        if problems:
            with_problems += 1
            print(f"race {race} {CLASS_NAMES.get(klass, klass)} (items {ids}):")
            for entry, name, notes in problems:
                print(f"    {entry} {name!r}: " + "; ".join(notes))
            for (r, k), skills in missing_by_class.items():
                for skill in sorted(skills):
                    fixes.append((r, k, skill))

    print(f"\noutfits with problems: {with_problems}; missing skill grants: {len(fixes)}")
    if args.sql:
        lines = ["-- Starter skills demanded by each custom race's own starting outfit.", ""]
        for race, klass, skill in fixes:
            lines.append(
                "INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) "
                f"VALUES ({1 << (race - 1)}, {1 << (klass - 1)}, {skill}, 0, "
                f"'race {race} class {klass}: needed by starting outfit');"
            )
        print("\n".join(lines))
        (HERE / "starter_skill_fixes.sql").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
