import hashlib
import subprocess
import sys
sys.path.insert(0, r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")
import earthen_race_pack as e
import mechagnome_race_pack as db

report = e.p.load_json(e.STAGE / "last-install.json")
for name, digest in report["installed_hashes"].items():
    assert e.p.sha256(e.p.CLIENT_DEFAULT / name) == digest, name
assert e.p.sha256(e.p.CLIENT_DEFAULT / "Wow.exe") == report["preserved_exe_sha256"]
paths = ["/azerothcore/env/dist/data/dbc/" + name + ".dbc" for name in e.p.SERVER_DBC_TABLES]
lines = subprocess.check_output(["docker", "exec", "ac-worldserver", "sha256sum", *paths], text=True)
mounted = {line.split()[1].rsplit("/", 1)[1][:-4]: line.split()[0] for line in lines.splitlines()}
assert mounted == report["installed_server_hashes"]
for table, digest in report["unrelated_world_hashes"].items():
    field = "RaceID" if table == "player_totem_model" else "race"
    rows = sorted(db.sql(f"SELECT * FROM `{table}` WHERE `{field}` NOT IN (48,49);").splitlines())
    assert hashlib.sha256("\n".join(rows).encode()).hexdigest() == digest, table
classes = db.sql("SELECT race,class FROM playercreateinfo WHERE race IN (48,49) ORDER BY race,class;")
expected = "\n".join(f"{r}\t{c}" for r in (48,49) for c in (1,2,3,4,5,6,7,8,9,11))
assert classes.strip() == expected
skills = db.sql("SELECT race,skill FROM custom_race_start_skill WHERE race IN (48,49) ORDER BY race,skill;")
assert skills.strip() == "48\t98\n48\t111\n49\t109"
spells = db.sql("SELECT race,spell FROM custom_race_start_spell WHERE race IN (48,49) ORDER BY race,spell;")
assert spells.strip() == "48\t668\n48\t672\n49\t669"
receipt = db.sql("SELECT hash,state FROM updates WHERE name='rev_20261001100000000.sql';").strip()
assert receipt == report["migration_receipt_sha1"] + "\tPENDING"
acceptance = e.p.load_json(e.ROOT / "integration/acceptance.json")
for service, before in acceptance["preserved_services"].items():
    name = "ac-authserver" if service == "authserver_id" else "ac-database"
    after = subprocess.check_output(["docker", "inspect", name, "--format", "{{.Id}}"], text=True).strip()
    assert before == after, name
image = subprocess.check_output(["docker", "inspect", "ac-worldserver", "--format", "{{.Image}}"], text=True).strip()
assert image != report["previous_worldserver_image"]
logs = subprocess.check_output(["docker", "logs", "ac-worldserver"], text=True, encoding="utf-8",
                               errors="replace", stderr=subprocess.STDOUT)
(e.STAGE / "installed-worldserver.log").write_text(logs, encoding="utf-8")
assert "WORLD: World Initialized" in logs or "World initialized" in logs or "World initialized in" in logs
acceptance.update(status="installed_server_ready_awaiting_live_acceptance", installed=True,
                  compiled_worldserver=True, compiled_native=True, worldserver_image=image,
                  installed_verification="PASS: all client and mounted server hashes, scoped migration, startup data, preserved services",
                  live_acceptance="pending user testing", migration_receipt_sha1=report["migration_receipt_sha1"])
acceptance["required_next_steps"] = ["Fresh-client live acceptance for both genders/factions and existing races"]
e.save(e.ROOT / "integration/acceptance.json", acceptance)
report["status"] = "installed_server_ready_awaiting_live_acceptance"
report["worldserver_image"] = image
e.save(e.STAGE / "last-install.json", report)
e.save(e.Path(report["backup"]) / "install-report.json", report)
print("Earthen installed verification PASS: hashes, language/start data, scoped receipt, unrelated rows/services preserved")
print("Worldserver image:", image)
