"""Generate the world-SQL update that adds the Alliance Illidari (race 31).

Clones the Horde Illidari (race 30) and gives it the Alliance side of the donor's pair:
Stormwind faction, Common, displays 60026/60027, and the Night Elf start (Teldrassil) so the
race learns the Night Elf class kit, its quests and its action bars.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
PENDING = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world"
RACE = 31
SOURCE_RACE = 30
HOST_RACE = 4          # Night Elf: same faction and the closest thing to an Illidari start
RACE_BIT = 1 << (RACE - 1)
HOST_BIT = 1 << (HOST_RACE - 1)
WEAPON_SKILLS = {0: 44, 1: 172, 2: 45, 3: 46, 4: 54, 5: 160, 6: 229, 7: 43, 8: 55,
                 10: 136, 13: 473, 15: 173, 16: 176, 18: 226, 19: 228, 20: 356}
ARMOR_SKILLS = {1: 415, 2: 414, 3: 413, 4: 293, 6: 433}
ITEM_FIELDS = ", ".join(f"ItemID_{index}" for index in range(1, 25))


def mysql(query: str) -> list[list[str]]:
    result = subprocess.run(
        ["docker", "exec", "ac-database", "mysql", "-uroot", "-ppassword", "-N", "-e", query],
        capture_output=True, text=True, check=True,
    )
    return [line.split("\t") for line in result.stdout.strip().splitlines() if line]


def outfit_skill_grants() -> list[str]:
    """Skills demanded by the outfit rows race 31 inherits from race 30."""
    rows = mysql(
        f"SELECT ClassID, {ITEM_FIELDS} FROM acore_world.charstartoutfit_dbc WHERE RaceID = {SOURCE_RACE};"
    )
    outfits: dict[int, set[int]] = {}
    for row in rows:
        klass = int(row[0])
        if klass == 0:
            continue
        outfits.setdefault(klass, set()).update(int(value) for value in row[1:] if int(value) > 0)
    granted = {
        (int(race_mask), int(class_mask), int(skill))
        for race_mask, class_mask, skill in (
            (a, b, c) for a, b, c in mysql(
                "SELECT raceMask, classMask, skill FROM acore_world.playercreateinfo_skills;"
            )
        )
    }
    statements: list[str] = []
    for klass, items in sorted(outfits.items()):
        ids = ",".join(str(value) for value in sorted(items))
        needed: set[int] = set()
        for entry, item_class, subclass in (
            (int(a), int(b), int(c)) for a, b, c in mysql(
                f"SELECT entry, class, subclass FROM acore_world.item_template WHERE entry IN ({ids});"
            )
        ):
            skill = WEAPON_SKILLS.get(subclass) if item_class == 2 else ARMOR_SKILLS.get(subclass) if item_class == 4 else None
            if not skill:
                continue
            if any((race_mask & RACE_BIT or race_mask & HOST_BIT) and (class_mask == 0 or class_mask & (1 << (klass - 1))) and row_skill == skill
                   for race_mask, class_mask, row_skill in granted):
                continue
            needed.add(skill)
        for skill in sorted(needed):
            statements.append(
                "INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) "
                f"VALUES ({RACE_BIT}, {1 << (klass - 1)}, {skill}, 0, 'race {RACE} class {klass}: starting outfit');"
            )
    return statements


def main() -> None:
    lines = [
        f"-- Alliance Illidari (race {RACE}): the donor ships two Illidari races (its 24 is the",
        "-- Night Elf/Alliance one, its 27 the Blood Elf/Horde one) and only the Horde half was",
        f"-- ported. This clones race {SOURCE_RACE} onto the Alliance side so both factions show the",
        "-- same number of races in the creator. Client half:",
        "-- `add_alliance_illidari_client.py` (ChrRaces, CreatureDisplayInfo, CharBaseInfo,",
        "-- CharSections/CharHairGeosets/CharacterFacialHairStyles, CharStartOutfit in Patch-Y).",
        "",
        "-- 1. ChrRaces: clone 30, Alliance faction, Common, new display rows",
        "CREATE TEMPORARY TABLE `tmp_chrraces` AS SELECT * FROM `chrraces_dbc` WHERE `ID` = 30;",
        "UPDATE `tmp_chrraces` SET",
        f"    `ID` = {RACE}, `FactionID` = 1, `Alliance` = 0, `BaseLanguage` = 7,",
        "    `MaleDisplayId` = 60026, `FemaleDisplayId` = 60027;",
        f"DELETE FROM `chrraces_dbc` WHERE `ID` = {RACE};",
        "INSERT INTO `chrraces_dbc` SELECT * FROM `tmp_chrraces`;",
        "DROP TEMPORARY TABLE `tmp_chrraces`;",
        "",
        "-- 2. CreatureDisplayInfo rows 60026/60027 (same models as the Horde Illidari)",
        "CREATE TEMPORARY TABLE `tmp_display` AS SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (60024, 60025);",
        "UPDATE `tmp_display` SET `ID` = `ID` + 2;",
        "DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (60026, 60027);",
        "INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_display`;",
        "DROP TEMPORARY TABLE `tmp_display`;",
        "",
        "-- 3. Starting outfit rows",
        "CREATE TEMPORARY TABLE `tmp_outfit` AS SELECT * FROM `charstartoutfit_dbc` WHERE `RaceID` = 30;",
        "UPDATE `tmp_outfit` SET `ID` = `ID` + 10000, `RaceID` = 31;",
        "DELETE FROM `charstartoutfit_dbc` WHERE `RaceID` = 31;",
        "INSERT INTO `charstartoutfit_dbc` SELECT * FROM `tmp_outfit`;",
        "DROP TEMPORARY TABLE `tmp_outfit`;",
        "",
        "-- 4. Spawn points: the Night Elf start, same faction, Teldrassil",
        "CREATE TEMPORARY TABLE `tmp_pci` AS SELECT * FROM `playercreateinfo` WHERE `race` = 4;",
        "UPDATE `tmp_pci` SET `race` = 31;",
        "DELETE FROM `playercreateinfo` WHERE `race` = 31;",
        "INSERT INTO `playercreateinfo` SELECT * FROM `tmp_pci`;",
        "DROP TEMPORARY TABLE `tmp_pci`;",
        "",
        "-- 5. Class kit, action bars and auto-cast spells from the Night Elf block",
        "INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`)",
        f"SELECT {RACE_BIT}, `classMask`, `skill`, `rank`, CONCAT('race {RACE} inherits Night Elf: ', COALESCE(`comment`, ''))",
        "FROM `playercreateinfo_skills`",
        f"WHERE (`raceMask` & {HOST_BIT}) <> 0;",
        "",
        "INSERT IGNORE INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`)",
        f"SELECT {RACE_BIT}, `classmask`, `Spell`, `Note` FROM `playercreateinfo_spell_custom`",
        f"WHERE (`racemask` & {HOST_BIT}) <> 0;",
        "",
        "INSERT IGNORE INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)",
        "SELECT 31, `class`, `button`, `action`, `type` FROM `playercreateinfo_action` WHERE `race` = 4;",
        "",
        "INSERT IGNORE INTO `playercreateinfo_cast_spell` (`raceMask`, `classMask`, `spell`, `note`)",
        f"SELECT {RACE_BIT}, `classMask`, `spell`, `note` FROM `playercreateinfo_cast_spell`",
        f"WHERE (`raceMask` & {HOST_BIT}) <> 0;",
        "",
        "-- 6. Skills demanded by the cloned starting outfit",
    ]
    lines += outfit_skill_grants()
    lines += [
        "",
        "-- 7. Quests: the race takes Night Elf quests (Teldrassil/druidic chains included)",
        "UPDATE `quest_template`",
        f"SET `AllowableRaces` = `AllowableRaces` | {RACE_BIT}",
        f"WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & {HOST_BIT}) <> 0;",
        "",
        "-- 8. Skill/skill-spell masks so LearnDefaultSkill() and the client accept the race",
        "UPDATE `skillraceclassinfo_dbc` SET `RaceMask` = `RaceMask` | 0x40000000 WHERE `RaceMask` <> 0;",
        "UPDATE `skilllineability_dbc` SET `RaceMask` = `RaceMask` | 0x40000000 WHERE `RaceMask` <> 0;",
        "",
    ]
    PENDING.mkdir(parents=True, exist_ok=True)
    target = PENDING / "rev_1787850000015_alliance_illidari.sql"
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {target} ({len(lines)} lines, {len(outfit_skill_grants())} outfit skill grants)")


if __name__ == "__main__":
    main()
