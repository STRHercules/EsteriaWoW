"""Grant the remaining server-side languages (Draconic/Demonic/Titan/Kalimag) so any
language id the client sends resolves to a skill the character has."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
WORLD_SQL = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000008_race_languages_full.sql"
CHAR_SQL = REPO / "modules/mod-custom-server/data/sql/db-characters/race_language_backfill_full.sql"

RACES = (16, 17, 19, 21, 22, 23, 28, 29, 30)
CLASSMASKS = (1, 2, 4, 8, 16, 32, 64, 128, 256, 1024)
LANGUAGES = ((814, "Language Draconic"), (815, "Language Demonic"), (816, "Language Titan"), (817, "Language Kalimag"))
SKILLS = ((138, "Draconic"), (139, "Demonic"), (140, "Titan"), (141, "Kalimag"))
RACE_LIST = ", ".join(str(r) for r in RACES)


def run(sql: str, database: str) -> None:
    proc = subprocess.run(
        ["docker", "exec", "-i", "ac-database", "mysql", "-uroot", "-ppassword", database],
        input=sql,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"apply failed on {database}: {proc.stderr}")


def main() -> None:
    rows = []
    for race in RACES:
        mask = 1 << (race - 1)
        for classmask in CLASSMASKS:
            for spell, note in LANGUAGES:
                rows.append(f"({mask}, {classmask}, {spell}, '{note}')")
    world = (
        "-- Remaining server languages (Draconic/Demonic/Titan/Kalimag) for the ported races,\n"
        "-- so every language id the client can send maps to a skill the character learns.\n"
        "INSERT IGNORE INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES\n"
        + ",\n".join(rows)
        + ";\n"
    )
    WORLD_SQL.write_text(world, encoding="utf-8")
    run(world, "acore_world")
    print(f"wrote+applied {WORLD_SQL.relative_to(REPO)} ({len(rows)} rows)")

    spells = ", ".join(str(s) for s, _ in LANGUAGES)
    skills = ", ".join(str(s) for s, _ in SKILLS)
    char = (
        "-- Backfill the remaining languages for existing custom-race characters.\n"
        "INSERT IGNORE INTO `character_spell` (`guid`, `spell`, `specMask`)\n"
        f"SELECT `guid`, s.`spell`, 1 FROM `characters` JOIN ({' UNION ALL '.join(f'SELECT {s} AS `spell`' for s, _ in LANGUAGES)}) s\n"
        f"WHERE `race` IN ({RACE_LIST});\n\n"
        "INSERT IGNORE INTO `character_skills` (`guid`, `skill`, `value`, `max`)\n"
        f"SELECT `guid`, k.`skill`, 300, 300 FROM `characters` JOIN ({' UNION ALL '.join(f'SELECT {s} AS `skill`' for s, _ in SKILLS)}) k\n"
        f"WHERE `race` IN ({RACE_LIST});\n"
    )
    CHAR_SQL.write_text(char, encoding="utf-8")
    run(char, "acore_characters")
    print(f"wrote+applied {CHAR_SQL.relative_to(REPO)}")
    print("languages granted:", [s for s, _ in LANGUAGES], "spells:", spells, "skills:", skills)


if __name__ == "__main__":
    main()
