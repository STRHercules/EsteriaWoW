"""Give the ported races a full class spell set (weapon skills, stances, language).

The nine ported races only carried ~31 hand-written rows in
`playercreateinfo_spell_custom`, so a new character missed the weapon-skill spells
(One-Handed Swords/Axes/..., Defense, Bows, Guns, ...) and the language spell, even
though `playercreateinfo_skills` already hands out Defense/Unarmed/Cloth and one
class tab. Copying a faction-appropriate stock race's class blocks fixes both.

Runs read-only against the live DB and writes
`rev_1787850000005_race_start_spells.sql`; pass --apply to also run it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
OUT = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000005_race_start_spells.sql"

# target race -> donor race (same faction; flavour-appropriate where one exists)
DONORS = {
    16: 10,  # Eredar            <- Blood Elf
    17: 10,  # Nightborne        <- Blood Elf
    19: 4,   # Void Elf          <- Night Elf
    21: 11,  # Lightforged       <- Draenei
    22: 8,   # Zandalari Troll   <- Troll
    23: 3,   # Dark Iron Dwarf   <- Dwarf
    28: 2,   # Dracthyr          <- Orc
}
# Kul Tiran (29) and Illidari (30) were already cloned from Dwarf / Blood Elf.
CLASSMASKS = (1, 2, 4, 8, 16, 64, 128, 256, 1024)  # every class except Death Knight


def mysql(sql: str) -> list[tuple[str, ...]]:
    proc = subprocess.run(
        ["docker", "exec", "ac-database", "mysql", "-uroot", "-ppassword", "acore_world", "-N", "-e", sql],
        capture_output=True,
        text=True,
        check=True,
    )
    rows = []
    for line in proc.stdout.splitlines():
        if line.strip():
            rows.append(tuple(part.strip() for part in line.split("\t")))
    return rows


def mask(race: int) -> int:
    return 1 << (race - 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    class_list = ", ".join(str(m) for m in CLASSMASKS)
    statements = [
        "-- Full class spell sets for the ported races: weapon skills, stances and the",
        "-- faction language spell are copied from a same-faction stock race.",
        "-- Death Knight rows (classmask 32) are left untouched.",
        "",
    ]
    summary = []
    for race, donor in DONORS.items():
        rows = mysql(
            "SELECT classmask, Spell, Note FROM playercreateinfo_spell_custom "
            f"WHERE racemask = {mask(donor)} AND classmask IN ({class_list}) ORDER BY classmask, Spell;"
        )
        if not rows:
            raise SystemExit(f"donor race {donor} has no spell rows")
        statements.append(f"DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = {mask(race)} AND `classmask` IN ({class_list});")
        values = ",\n".join(
            "({}, {}, {}, {})".format(mask(race), cm, spell, "'" + note.replace("'", "''") + "'" if note else "''")
            for cm, spell, note in rows
        )
        statements.append(
            "INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES\n" + values + ";"
        )
        statements.append("")
        summary.append((race, donor, len(rows)))

    OUT.write_text("\n".join(statements), encoding="utf-8")
    for race, donor, count in summary:
        print(f"race {race:>2} <- donor {donor:>2}: {count} spell rows")
    print(f"wrote {OUT.relative_to(REPO)} ({OUT.stat().st_size:,} bytes)")

    if args.apply:
        proc = subprocess.run(
            ["docker", "exec", "-i", "ac-database", "mysql", "-uroot", "-ppassword", "acore_world"],
            input="\n".join(statements),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise SystemExit(f"apply failed: {proc.stderr}")
        print("applied to acore_world")


if __name__ == "__main__":
    main()
