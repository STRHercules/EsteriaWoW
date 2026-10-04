"""Generate the two world-SQL updates that give the custom races a stock race's start.

Every custom race adopts the starting zone it uses, so it inherits that zone's stock race:

    Orc (2)        <- 14 Broken, 16 Eredar, 20 Vulpera, 22 Zandalari, 28 Dracthyr   (Durotar)
    Blood Elf (10) <- 17 Nightborne, 30 Illidari                                    (Eversong)
    Human (1)      <- 18 Pandaren, 19 Void Elf                                      (Elwynn)
    Draenei (11)   <- 21 Lightforged Draenei                                        (Azuremyst)
    Dwarf (3)      <- 23 Dark Iron Dwarf, 29 Kul Tiran                              (Dun Morogh)

Rows copied: `playercreateinfo_skills` (weapon/armor/class skill lines - this is what
`Player::CanUseItem()` needs before an item can be equipped), `playercreateinfo_spell_custom`
(class abilities and proficiency spells, only for the three races that had almost none),
`playercreateinfo_action` (starter action bars) and `playercreateinfo_cast_spell`.

The quest update widens `quest_template.AllowableRaces` with the custom race's bit for every
quest its host race can take, which is what lets a Vulpera Hunter pick up the Valley of Trials
quests.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
PENDING = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world"

HOSTS = (
    ("Orc", 2, (14, 16, 20, 22, 28)),
    ("Blood Elf", 10, (17, 30)),
    ("Human", 1, (18, 19)),
    ("Draenei", 11, (21,)),
    ("Dwarf", 3, (23, 29)),
)
# Races that had almost no playercreateinfo_spell_custom rows at all.
SPARSE_SPELLS = (14, 18, 20)


def bits(race: int) -> int:
    return 1 << (race - 1)


def skills_sql() -> str:
    lines = [
        "-- Starter skills, spells, action bars and auto-cast spells for every custom race.",
        "-- Each race takes the block of the stock race that shares its starting zone, so the",
        "-- weapon and armour skill lines `Player::CanUseItem()` checks exist before the first",
        "-- item is equipped (Vulpera Hunters need Axes 44 / Bows 45, for example).",
        "",
    ]
    for name, host, races in HOSTS:
        for race in races:
            lines.append(f"-- race {race} <- {name} ({host})")
            lines.append("INSERT IGNORE INTO `playercreateinfo_skills`")
            lines.append("    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)")
            lines.append("SELECT")
            lines.append(f"    {bits(race)}, `classMask`, `skill`, `rank`,")
            lines.append(f"    CONCAT('race {race} inherits {name}: ', COALESCE(`comment`, ''))")
            lines.append("FROM `playercreateinfo_skills`")
            lines.append(f"WHERE (`raceMask` & {bits(host)}) <> 0;")
            lines.append("")
            lines.append("INSERT IGNORE INTO `playercreateinfo_action`")
            lines.append("    (`race`, `class`, `button`, `action`, `type`)")
            lines.append("SELECT")
            lines.append(f"    {race}, `class`, `button`, `action`, `type`")
            lines.append("FROM `playercreateinfo_action`")
            lines.append(f"WHERE `race` = {host};")
            lines.append("")
            lines.append("INSERT IGNORE INTO `playercreateinfo_cast_spell`")
            lines.append("    (`raceMask`, `classMask`, `spell`, `note`)")
            lines.append("SELECT")
            lines.append(f"    {bits(race)}, `classMask`, `spell`, `note`")
            lines.append("FROM `playercreateinfo_cast_spell`")
            lines.append(f"WHERE (`raceMask` & {bits(host)}) <> 0;")
            lines.append("")
            if race in SPARSE_SPELLS:
                lines.append("INSERT IGNORE INTO `playercreateinfo_spell_custom`")
                lines.append("    (`racemask`, `classmask`, `Spell`, `Note`)")
                lines.append("SELECT")
                lines.append(f"    {bits(race)}, `classmask`, `Spell`, `Note`")
                lines.append("FROM `playercreateinfo_spell_custom`")
                lines.append(f"WHERE (`racemask` & {bits(host)}) <> 0;")
                lines.append("")
    return "\n".join(lines) + "\n"


def quests_sql() -> str:
    lines = [
        "-- Let every custom race take the quests of the stock race that shares its start zone.",
        "-- `quest_template.AllowableRaces` is the same mask the client is sent, so widening it for",
        "-- the host race's quests is what opens the Valley of Trials / Eversong / Elwynn / Azuremyst",
        "-- / Dun Morogh starter chains to the ported races. Rows with mask 0 are unrestricted.",
        "",
    ]
    for name, host, races in HOSTS:
        for race in races:
            lines.append(f"-- race {race} <- {name} ({host})")
            lines.append("UPDATE `quest_template`")
            lines.append(f"SET `AllowableRaces` = `AllowableRaces` | {bits(race)}")
            lines.append(f"WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & {bits(host)}) <> 0;")
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    PENDING.mkdir(parents=True, exist_ok=True)
    skills = PENDING / "rev_1787850000012_race_start_skills.sql"
    quests = PENDING / "rev_1787850000013_race_start_quests.sql"
    skills.write_text(skills_sql(), encoding="utf-8")
    quests.write_text(quests_sql(), encoding="utf-8")
    print(f"wrote {skills}")
    print(f"wrote {quests}")


if __name__ == "__main__":
    main()
