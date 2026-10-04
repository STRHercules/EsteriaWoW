"""Install the corrected Vulpera creator/material graph with a guarded v1-to-v2 appearance migration."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import mechagnome_race_pack as db
import vulpera_race_pack as v
import vulpera_migration as old
import test_vulpera_creator
import test_vulpera_models

MIGRATION = v.p.ROOT / "data/sql/updates/pending_db_characters/rev_20261002220000000.sql"


def prepare():
    checkpoint = v.p.load_json(v.STAGE / "repair-checkpoint.json")
    backup = Path(checkpoint["backup"])
    previous = v.p.load_json(backup / "codec-v1.json")
    profiles = v.audit()
    before = old.snapshot()
    rows = [list(map(int, line.split())) for line in before.splitlines()]
    changes, statements, rollback = [], [], []
    for row in rows:
        if row[1] != 20:
            continue
        guid, _, character_class, gender = row[:4]
        sex = "female" if gender else "male"
        choices = v.decode(previous[sex], row[4:9])
        source_ids = {o["id"]: o["choices"][choice]["ID"]
                      for o, choice in zip(previous[sex]["options"], choices, strict=True)}
        selected = []
        for option in profiles[sex]["options"]:
            if option["id"] not in source_ids:
                selected.append(0)
            else:
                selected.append(next(i for i, c in enumerate(option["choices"])
                                     if c["ID"] == source_ids[option["id"]]))
        fields = v.encode(profiles[sex], selected)
        predicates = " AND ".join(f"`{key}`={value}" for key, value in zip(
            ("skin", "face", "hairStyle", "hairColor", "facialStyle"), row[4:9], strict=True))
        statements.append(f"UPDATE `characters` SET `hairColor`={fields[3]}, `facialStyle`={fields[4]}\n"
            f"WHERE `guid`={guid} AND `race`=20 AND `class`={character_class} AND `gender`={gender}\n    AND "
            + predicates.replace(" AND ", "\n    AND ") + " AND `extraAppearance`=0;")
        rollback.append(f"UPDATE `characters` SET `hairColor`={row[7]}, `facialStyle`={row[8]} "
                        f"WHERE `guid`={guid} AND `race`=20;")
        changes.append({"guid": guid, "old": row[4:], "new": fields + [0], "source_choices": source_ids})
    MIGRATION.write_text("-- Vulpera codec v2: preserve source choices while adding all authored eye palettes/styles.\n"
        + "\n".join(statements) + "\n", encoding="utf-8", newline="\n")
    updates = v.glue()
    checks = [test_vulpera_creator.check(updates[v.p.GLUE_ROOT + "CharacterCreate.lua"].decode(),
                                       updates[v.p.GLUE_ROOT + "CharacterInfo.lua"].decode())]
    test_vulpera_models.main()
    for test in ("TestNativeAppearance.exe", "TestHighmountainMaterials.exe", "TestCustomizationChoices.exe"):
        subprocess.run([str(v.STAGE / test), str(v.STAGE / "EsteriaAppearance.dll")], check=True)
    stage = v.p.load_json(v.STAGE / "build-report.json")
    stage["companion_hashes"]["EsteriaAppearance.dll"] = v.p.sha256(v.STAGE / "EsteriaAppearance.dll")
    v.save(v.STAGE / "build-report.json", stage)
    v.validate()
    files = {name: str(v.STAGE / "pack" / name) for name in stage["stage_hashes"]}
    files.update({name: str(v.STAGE / name) for name in stage["companion_hashes"]})
    for name, digest in checkpoint["client_before"].items():
        if v.p.sha256(v.p.CLIENT_DEFAULT / name) != digest:
            raise ValueError("Live client changed during repair: " + name)
    if {name: v.p.sha256(v.p.SERVER_DBC_ROOT / (name + ".dbc")) for name in v.p.SERVER_DBC_TABLES} \
            != checkpoint["server_before"]:
        raise ValueError("Live server DBCs changed during repair")
    report = {**checkpoint, "stage": stage, "files": files, "before_characters": before, "changes": changes,
              "migration": str(MIGRATION), "migration_sha256": v.p.sha256(MIGRATION),
              "rollback_sql": "\n".join(rollback) + "\n", "checks": checks}
    shutil.copy2(MIGRATION, backup / MIGRATION.name)
    (backup / "rollback-codec-v2.sql").write_text(report["rollback_sql"], encoding="utf-8", newline="\n")
    v.save(v.STAGE / "repair-plan.json", report)
    v.save(backup / "repair-plan.json", report)
    return {"status": "ready", "characters": changes, "checks": checks}


def install():
    report = v.p.load_json(v.STAGE / "repair-plan.json")
    backup = Path(report["backup"])
    if subprocess.check_output(["docker", "inspect", "ac-worldserver", "--format", "{{.State.Running}}"],
                               text=True).strip() != "false":
        raise ValueError("Stop only worldserver for the matching codec migration")
    processes = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True).lower()
    if "wow.exe" in processes or "eclipse.exe" in processes:
        raise ValueError("Close WoW/Eclipse before replacing the checked package")
    if old.snapshot() != report["before_characters"] or v.p.sha256(MIGRATION) != report["migration_sha256"]:
        raise ValueError("Saved appearances or guarded migration changed")
    for name, digest in report["client_before"].items():
        if v.p.sha256(v.p.CLIENT_DEFAULT / name) != digest:
            raise ValueError("Live client changed: " + name)
    for name, digest in report["server_before"].items():
        if v.p.sha256(v.p.SERVER_DBC_ROOT / (name + ".dbc")) != digest:
            raise ValueError("Live server DBC changed: " + name)
    for name, source in report["files"].items():
        digest = report["stage"]["stage_hashes"].get(name, report["stage"]["companion_hashes"].get(name))
        if v.p.sha256(Path(source)) != digest:
            raise ValueError("Validated stage changed: " + name)
    receipt = hashlib.sha1(MIGRATION.read_bytes()).hexdigest().upper()
    try:
        db.sql("START TRANSACTION;\n" + MIGRATION.read_text() +
               f"\nDELETE FROM updates WHERE name='{MIGRATION.name}';\n"
               f"INSERT INTO updates (name,hash,state) VALUES ('{MIGRATION.name}','{receipt}','PENDING');\nCOMMIT;",
               "acore_characters")
        for name, source in report["files"].items():
            target = v.p.CLIENT_DEFAULT / name
            temporary = target.with_suffix(target.suffix + ".vulpera-next")
            shutil.copy2(source, temporary)
            if v.p.sha256(temporary) != v.p.sha256(Path(source)):
                raise ValueError("Copy differs: " + name)
            os.replace(temporary, target)
        for name in v.p.SERVER_DBC_TABLES:
            source = v.STAGE / "server-dbc" / (name + ".dbc")
            target = v.p.SERVER_DBC_ROOT / source.name
            shutil.copy2(source, target)
            if v.p.sha256(source) != v.p.sha256(target):
                raise ValueError("Server DBC copy differs: " + name)
        expected = {int(line.split()[0]): list(map(int, line.split()))
                    for line in report["before_characters"].splitlines()}
        for row in report["changes"]:
            expected[row["guid"]][4:] = row["new"]
        if {int(line.split()[0]): list(map(int, line.split())) for line in old.snapshot().splitlines()} != expected:
            raise ValueError("Character readback differs from the scoped source-choice migration")
    except Exception:
        for name in report["client_before"]:
            shutil.copy2(backup / "client" / name, v.p.CLIENT_DEFAULT / name)
        for name in v.p.SERVER_DBC_TABLES:
            shutil.copy2(backup / "server-dbc" / (name + ".dbc"), v.p.SERVER_DBC_ROOT / (name + ".dbc"))
        db.sql("START TRANSACTION;\n" + report["rollback_sql"] +
               f"DELETE FROM updates WHERE name='{MIGRATION.name}';\nCOMMIT;", "acore_characters")
        raise
    receipt_report = v.p.load_json(v.STAGE / "last-install.json")
    receipt_report.update(backup=str(backup), codec_version=2, repair=report,
        stage_hashes=report["stage"]["stage_hashes"],
        companion_hashes=report["stage"]["companion_hashes"], files=report["files"],
        installed_hashes={n: v.p.sha256(v.p.CLIENT_DEFAULT / n) for n in report["files"]},
        installed_server_hashes={n: v.p.sha256(v.p.SERVER_DBC_ROOT / (n + ".dbc")) for n in v.p.SERVER_DBC_TABLES},
        status="repaired_awaiting_worldserver_recreation", live_client_test="not_performed_after_repair")
    v.save(v.STAGE / "last-install.json", receipt_report)
    v.save(backup / "install-report.json", receipt_report)
    return {"status": receipt_report["status"], "backup": str(backup)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "install"))
    print(json.dumps(globals()[parser.parse_args().action](), indent=2))
