"""Grant every custom race/class the skills its own starting outfit needs.

The outfits were rebuilt from the old Vulpera rows and do not match the host race's weapon
kit: a Vulpera Hunter starts with a two-handed axe (12282) and a crossbow (23347) while the
Orc block gives Axes (44) and Bows (45); a Dark Iron Warrior starts with a two-handed sword
(49778) while the Dwarf block gives Axes (44), Guns (46), Two-Handed Axes (172) and Maces.
`Player::CanUseItem()` and the client both want the matching skill line, so this walks the
outfit rows in `charstartoutfit_dbc`, maps each item's class/subclass to its skill, and adds
the missing `playercreateinfo_skills` rows for that race and class only.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
PENDING = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world"

CUSTOM_RACES = (14, 16, 17, 18, 19, 20, 21, 22, 23, 28, 29, 30)
ITEM_FIELDS = ", ".join(f"ItemID_{index}" for index in range(1, 25))

# item subclass -> skill line (weapons, item class 2)
WEAPON_SKILLS = {
    0: 44,    # one-handed axe
    1: 172,   # two-handed axe
    2: 45,    # bow
    3: 46,    # gun
    4: 54,    # one-handed mace
    5: 160,   # two-handed mace
    6: 229,   # polearm
    7: 43,    # one-handed sword
    8: 55,    # two-handed sword
    10: 136,  # staff
    13: 473,  # fist weapon
    15: 173,  # dagger
    16: 176,  # thrown
    18: 226,  # crossbow
    19: 228,  # wand
    20: 356,  # fishing pole
}
# item subclass -> skill line (armour, item class 4); ids from SharedDefines.h
ARMOR_SKILLS = {
    1: 415,  # SKILL_CLOTH
    2: 414,  # SKILL_LEATHER
    3: 413,  # SKILL_MAIL
    4: 293,  # SKILL_PLATE_MAIL
    6: 433,  # SKILL_SHIELD
}


def mysql(query: str) -> list[list[str]]:
    result = subprocess.run(
        ["docker", "exec", "ac-database", "mysql", "-uroot", "-ppassword", "-N", "-e", query],
        capture_output=True, text=True, check=True,
    )
    return [line.split("\t") for line in result.stdout.strip().splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = mysql(
        f"SELECT RaceID, ClassID, {ITEM_FIELDS} FROM acore_world.charstartoutfit_dbc "
        f"WHERE RaceID IN ({','.join(str(race) for race in CUSTOM_RACES)});"
    )
    outfits: dict[tuple[int, int], set[int]] = {}
    for row in rows:
        race, klass = int(row[0]), int(row[1])
        if klass == 0:
            continue
        items = {int(value) for value in row[2:] if value and int(value) > 0}
        outfits.setdefault((race, klass), set()).update(items)

    granted_rows = mysql("SELECT raceMask, classMask, skill FROM acore_world.playercreateinfo_skills;")
    granted = [(int(a), int(b), int(c)) for a, b, c in granted_rows]

    def has(race: int, klass: int, skill: int) -> bool:
        race_bit, class_bit = 1 << (race - 1), 1 << (klass - 1)
        return any(
            (race_mask & race_bit) and (class_mask == 0 or (class_mask & class_bit)) and row_skill == skill
            for race_mask, class_mask, row_skill in granted
        )

    statements: list[str] = []
    for (race, klass), items in sorted(outfits.items()):
        needed: set[int] = set()
        detail: list[str] = []
        ids = ",".join(str(value) for value in sorted(items))
        for entry, name, item_class, subclass in (
            (int(a), b, int(c), int(d))
            for a, b, c, d in mysql(
                f"SELECT entry, name, class, subclass FROM acore_world.item_template WHERE entry IN ({ids});"
            )
        ):
            skill = WEAPON_SKILLS.get(subclass) if item_class == 2 else ARMOR_SKILLS.get(subclass) if item_class == 4 else None
            if not skill or has(race, klass, skill):
                continue
            needed.add(skill)
            detail.append(f"{name} ({entry}) -> skill {skill}")
        for skill in sorted(needed):
            statements.append(
                "INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) "
                f"VALUES ({1 << (race - 1)}, {1 << (klass - 1)}, {skill}, 0, "
                f"'race {race} class {klass}: starting outfit needs skill {skill}');"
            )
        if detail:
            print(f"race {race} class {klass}: " + "; ".join(detail))

    print(f"\ngrants to add: {len(statements)}")
    if not statements:
        return
    header = [
        "-- Skills demanded by each custom race's own starting outfit.",
        "-- The outfits came from the old Vulpera rows, so a race can start with a weapon its",
        "-- host race's skill block does not cover (Vulpera Hunter: two-handed axe + crossbow;",
        "-- Dark Iron Warrior: two-handed sword). These rows are per race *and* class.",
        "",
    ]
    target = PENDING / "rev_1787850000014_race_starter_outfit_skills.sql"
    target.write_text("\n".join(header + statements) + "\n", encoding="utf-8")
    print(f"wrote {target}")
    if args.write:
        for statement in statements:
            mysql(f"USE acore_world; {statement}")
        print("applied to the live world DB")


if __name__ == "__main__":
    main()
