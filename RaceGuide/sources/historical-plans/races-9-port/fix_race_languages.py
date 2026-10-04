"""Grant every playable-race language to the ported races.

The client refuses chat with ERR_CANT_SPEAK_LANGAGE and the server answers
LANG_NOT_LEARNED_LANGUAGE ("You don't know that language") because the language id the
client sends has no matching skill on the character. Rather than guess which id the
client picks, give every ported race the full set of playable-race languages.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
OUT = REPO / "modules/mod-custom-server/data/sql/updates/pending_db_world/rev_1787850000007_race_languages.sql"
RACES = (16, 17, 19, 21, 22, 23, 28, 29, 30)
CLASSMASKS = (1, 2, 4, 8, 16, 32, 64, 128, 256, 1024)
LANGUAGES = (
    (668, "Language Common"),
    (669, "Language Orcish"),
    (670, "Language Taurahe"),
    (671, "Language Darnassian"),
    (672, "Language Dwarvish"),
    (7340, "Language Gnomish"),
    (7341, "Language Troll"),
    (813, "Language Thalassian"),
    (17737, "Language Gutterspeak"),
    (29932, "Language Draenei"),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    statements = [
        "-- Every playable-race language for the ported races, so whichever language id the",
        "-- client sends for these races resolves to a skill the character actually has.",
    ]
    total = 0
    for race in RACES:
        mask = 1 << (race - 1)
        values = []
        for classmask in CLASSMASKS:
            for spell, note in LANGUAGES:
                values.append(f"({mask}, {classmask}, {spell}, '{note}')")
        total += len(values)
        statements.append("INSERT IGNORE INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES")
        statements.append(",\n".join(values) + ";")
        statements.append("")
    payload = "\n".join(statements)
    OUT.write_text(payload, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)} ({total} rows)")

    if args.apply:
        proc = subprocess.run(
            ["docker", "exec", "-i", "ac-database", "mysql", "-uroot", "-ppassword", "acore_world"],
            input=payload,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise SystemExit(f"apply failed: {proc.stderr}")
        print("applied to acore_world")


if __name__ == "__main__":
    main()
