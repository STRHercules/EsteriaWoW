"""Guard the two existing Vulpera appearances while rebasing their authored Retail features."""

import hashlib
from pathlib import Path

import mechagnome_race_pack as db
import vulpera_race_pack as v

MIGRATION = v.p.ROOT / "data/sql/updates/pending_db_characters/rev_20261002200000000.sql"
QUERY = "SELECT guid,race,class,gender,skin,face,hairStyle,hairColor,facialStyle,extraAppearance " \
        "FROM characters ORDER BY guid;"


def snapshot():
    return db.sql(QUERY, "acore_characters")


def prepare():
    profiles = v.audit()
    before = snapshot()
    expected = {423: [423, 20, 2, 0, 6, 1, 1, 5, 52, 0],
                499: [499, 20, 2, 0, 10, 5, 1, 0, 31, 0]}
    original = [list(map(int, row.split())) for row in before.splitlines() if int(row.split()[1]) == 20]
    if {r[0]: r for r in original} != expected:
        raise ValueError("Existing Vulpera characters changed; review their semantic migration")
    # Position-set comparison against the source proves legacy earrings102..107 ->3501..3506 and
    # snouts302..307 ->4102..4107. Legacy mixed ear/ring combinations were not all Retail-authored.
    selections = {
        423: {"Fur Color": 6, "Pattern": 0, "Face": 1, "Snout": 1, "Ears": 3,
              "Eye Color": 5, "Earrings": 1, "Eyesight": 0, "Hair Style": 0},
        499: {"Fur Color": 2, "Pattern": 1, "Face": 5, "Snout": 2, "Ears": 2,
              "Eye Color": 0, "Earrings": 1, "Eyesight": 0, "Hair Style": 0},
    }
    columns = ("skin", "face", "hairStyle", "hairColor", "facialStyle", "extraAppearance")
    sql, rollback, mappings = [], [], []
    for guid, old in expected.items():
        profile = profiles["male"]
        selected = selections[guid]
        fields = v.encode(profile, [selected[o["label"]] for o in profile["options"]]) + [0]
        predicate = " AND ".join(f"`{name}`={value}" for name, value in zip(columns, old[4:], strict=True))
        update = ", ".join(f"`{name}`={value}" for name, value in zip(columns, fields, strict=True))
        predicate = predicate.replace(" AND ", "\n    AND ")
        sql.append(f"UPDATE `characters`\nSET {update}\nWHERE `guid`={guid} AND `race`=20\n    AND {predicate};")
        undo = ", ".join(f"`{name}`={value}" for name, value in zip(columns, old[4:], strict=True))
        rollback.append(f"UPDATE `characters` SET {undo} WHERE `guid`={guid} AND `race`=20;")
        mappings.append({"guid": guid, "old": old[4:], "new": fields, "choices": selected})
    MIGRATION.write_text("-- Vulpera Retail five-byte codec; guarded against changed saved appearances.\n"
        "-- Legacy ring/ear mismatches become the matching authored Retail accessory combination.\n"
        + "\n".join(sql) + "\n", encoding="utf-8", newline="\n")
    report = {"before": before, "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
              "characters": mappings, "rollback_sql": "\n".join(rollback) + "\n",
              "migration": str(MIGRATION), "migration_sha256": v.p.sha256(MIGRATION),
              "legacy_gaps": ["GUID423 legacy ear selector0 has no authored player option; its piercing style "
                              "matches Retail Rakish ears.", "GUID499 independent legacy ring style differs "
                              "from its ears; preserve Sharp ears and use their authored pierced accessory."]}
    v.save(v.STAGE / "migration-plan.json", report)
    return {"characters": mappings, "legacy_gaps": report["legacy_gaps"]}


if __name__ == "__main__":
    print(prepare())
