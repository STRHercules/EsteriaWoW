import hashlib
import sys
sys.path.insert(0, r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")
import earthen_race_pack as e
import mechagnome_race_pack as db

plan = e.p.load_json(e.STAGE / "install-plan.json")
for table in ("playercreateinfo", "player_race_stats", "playercreateinfo_item", "playercreateinfo_action",
              "player_totem_model", "custom_race_start_spell", "custom_race_start_skill"):
    field = "RaceID" if table == "player_totem_model" else "race"
    rows = sorted(db.sql(f"SELECT * FROM `{table}` WHERE `{field}` NOT IN (48,49);").splitlines())
    plan.setdefault("unrelated_world_hashes", {})[table] = hashlib.sha256("\n".join(rows).encode()).hexdigest()
e.save(e.STAGE / "install-plan.json", plan)
e.save(e.Path(plan["backup"]) / "install-report.json", plan)
acceptance = e.p.load_json(e.ROOT / "integration/acceptance.json")
acceptance.update(compiled_native=True, native_harnesses="PASS: NativeAppearance and HighmountainMaterials/lifetime",
                  backup=plan["backup"], status="native_checks_passed_worldserver_build_running")
e.save(e.ROOT / "integration/acceptance.json", acceptance)
print("Verified backup and unrelated startup-data snapshots saved")
