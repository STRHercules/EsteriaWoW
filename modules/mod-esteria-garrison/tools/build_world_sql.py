"""Build sql/world/garrison_world.sql from the UWoW port inputs in sql/source, so it overwrites nothing in Esteria.

1. Clone acore_world's schema (no rows) into a scratch database and load sql/source there.
2. Every creature/gameobject template whose entry already exists in acore_world moves to a garrison-owned entry
   (creatures 9603000+, gameobjects 9604000+) and every reference follows. The ledger ships as garrison_entry_remap.
3. Fail if any row of a shared table still has a primary key that acore_world uses.
4. Write the result: module tables are created if missing and refilled; shared tables get REPLACE rows whose keys
   were just proven free, and no DELETE touches a row the module did not write.

Run on the host that has the ac-database container:  python tools/build_world_sql.py [--live acore_world]
"""
import argparse
import struct
import subprocess
import sys
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
SOURCE = MODULE / "sql" / "source"
OUT = MODULE / "sql" / "world" / "garrison_world.sql"
SCRATCH = "garrison_scratch"
# garrison_uwow_templates.sql is left out: an older placeholder import ("Garrison Object <entry>", displays 7xxxxx that
# no DBC has) of the same 91 creatures and 86 objects garrison_uwow_world.sql ports properly.
ORDER = [
    "garrison_db2.sql", "garrison_world.sql", "garrison_uwow_world.sql",
    "garrison_uwow_map_spawns.sql", "garrison_uwow_building_spawns.sql", "garrison_buildings_world.sql",
    "garrison_creature_model_info.sql", "garrison_residents_models.sql", "garrison_residents_world.sql",
]
CREATURE_BASE, GAMEOBJECT_BASE = 9603000, 9604000
# (table, column, extra condition) that hold a creature_template / gameobject_template entry
CREATURE_REFS = [
    ("creature_template", "entry", ""), ("creature_template_model", "CreatureID", ""),
    ("creature_template_addon", "entry", ""), ("creature_template_movement", "CreatureId", ""),
    ("creature_equip_template", "CreatureID", ""), ("creature_text", "CreatureID", ""),
    ("creature_default_trainer", "CreatureId", ""), ("npc_vendor", "entry", ""),
    ("smart_scripts", "entryorguid", "AND t.source_type = 0"), ("creature", "id", ""),
    ("garrison_map_creature", "entry", ""), ("garrison_building_creature", "id", ""),
    ("garrison_creature_npcflag2", "entry", ""), ("garrison_shipment", "NpcEntry", ""),
]
GAMEOBJECT_REFS = [
    ("gameobject_template", "entry", ""), ("gameobject_template_addon", "entry", ""),
    ("smart_scripts", "entryorguid", "AND t.source_type = 1"), ("gameobject", "id", ""),
    ("garrison_map_gameobject", "entry", ""), ("garrison_building_gameobject", "id", ""),
    ("garrison_gameobject_wod_type", "entry", ""), ("garrison_plot_finalize_info", "hordeGameObjectId", ""),
    ("garrison_plot_finalize_info", "allianceGameObjectId", ""),
]
DOCKER = ["docker", "exec", "-i", "-e", "MYSQL_PWD=password", "ac-database"]


def mysql(sql, db="", force=False):
    cmd = DOCKER + ["mysql", "-uroot", "-N", "-B"] + (["--force"] if force else []) + ([db] if db else [])
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8")
    if r.returncode and not force:
        raise SystemExit(r.stderr)
    if r.stderr.strip():
        print(r.stderr.strip(), file=sys.stderr)
    return [line.split("\t") for line in r.stdout.splitlines() if line]


def load(live):
    mysql(f"DROP DATABASE IF EXISTS {SCRATCH}; CREATE DATABASE {SCRATCH};")
    clone = mysql(f"SELECT CONCAT('CREATE TABLE {SCRATCH}.`',table_name,'` LIKE {live}.`',table_name,'`;') "
                  f"FROM information_schema.tables WHERE table_schema='{live}' AND table_type='BASE TABLE'")
    mysql("\n".join(r[0] for r in clone))
    for name in ORDER:
        text = (SOURCE / name).read_text(encoding="utf-8")
        # garrison vendors copy stock vendor lists; read those from the live world, not the empty clone
        text = text.replace("FROM `npc_vendor`", f"FROM {live}.`npc_vendor`")
        # UWoW rows carry WoD values (creature family > 127) that a strict session rejects; they are fixed below
        mysql("SET SESSION sql_mode='';\n" + text, SCRATCH)


def remap(live):
    sql = [f"USE {SCRATCH};", "SET SESSION sql_mode='';",
           "DROP TABLE IF EXISTS garrison_entry_remap;",
           "CREATE TABLE garrison_entry_remap (kind CHAR(2) NOT NULL, retail_entry INT UNSIGNED NOT NULL, "
           "esteria_entry INT UNSIGNED NOT NULL, PRIMARY KEY (kind, retail_entry)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"]
    for kind, table, base, refs in (("CT", "creature_template", CREATURE_BASE, CREATURE_REFS),
                                    ("GO", "gameobject_template", GAMEOBJECT_BASE, GAMEOBJECT_REFS)):
        sql += [f"SET @n := {base - 1};",
                f"INSERT INTO garrison_entry_remap SELECT '{kind}', s.entry, (@n := @n + 1) FROM {table} s "
                f"JOIN {live}.{table} l ON l.entry = s.entry ORDER BY s.entry;"]
        for t, col, cond in refs:
            sql.append(f"UPDATE `{t}` t JOIN garrison_entry_remap m ON m.kind = '{kind}' AND t.`{col}` = m.retail_entry "
                       f"{cond} SET t.`{col}` = m.esteria_entry;")
    # 3.3.5 knows creature families up to 46
    sql.append("UPDATE creature_template SET family = 0 WHERE family > 46 OR family < 0;")
    # The client draws a WMO gameobject only as a map object (14) or building (33); a generic (5) one with a WMO display
    # shows the error cube (the empty plot pads 229501/232143/...). Displays from the UWoW port's GameObjectDisplayInfo.
    data = (MODULE / "data" / "client_dbc_source" / "GameObjectDisplayInfo.dbc").read_bytes()
    count, _fields, size, _strings = struct.unpack_from("<4I", data, 4)
    blob = 20 + count * size
    wmo = [struct.unpack_from("<I", data, 20 + i * size)[0] for i in range(count)
           if data[blob + struct.unpack_from("<I", data, 20 + i * size + 4)[0]:].split(b"\0", 1)[0].lower().endswith(b".wmo")]
    sql.append(f"UPDATE gameobject_template SET type = 14 WHERE type = 5 AND displayId IN ({','.join(map(str, wmo))});")
    # Retail's garrison plot objects (GameObjects type 39: empty plot pads, the Mine, Garden, Fishing Shack, Menagerie)
    # that the UWoW spawn import missed; without the Mine the cliff keeps the hole its WMO fills. Garrison::UpdatePlotPad
    # finds a pad by entry within 8 yards of its plot, so a pad counts as spawned only if one stands within 5 yards.
    sql += ["SET @g := (SELECT GREATEST(MAX(guid), 5100799) FROM gameobject WHERE guid BETWEEN 5100000 AND 5199999);",
            "INSERT INTO gameobject (guid, id, map, zoneId, areaId, spawnMask, phaseMask, position_x, position_y, position_z, "
            "orientation, rotation0, rotation1, rotation2, rotation3, spawntimesecs, animprogress, state, ScriptName, VerifiedBuild, Comment) "
            "SELECT (@g := @g + 1), d.id, d.owner_id, 0, 0, 1, 1, d.pos_0, d.pos_1, d.pos_2, 2 * ATAN2(d.rot_2, d.rot_3), "
            "d.rot_0, d.rot_1, d.rot_2, d.rot_3, 300, 0, 1, '', 0, CONCAT('garrison plot object: ', d.name) "
            "FROM db2_game_objects d JOIN gameobject_template t ON t.entry = d.id "
            "WHERE d.type_id = 39 AND d.owner_id IN (1152, 1153, 1158, 1159, 1330, 1331) AND NOT EXISTS (SELECT 1 FROM gameobject g "
            "WHERE g.id = d.id AND g.map = d.owner_id AND POW(g.position_x - d.pos_0, 2) + POW(g.position_y - d.pos_1, 2) < 25) "
            "ORDER BY d.owner_id, d.id;"]
    mysql("\n".join(sql))
    print(f"{mysql(f'SELECT COUNT(*) FROM {SCRATCH}.gameobject_template WHERE type = 14')[0][0]} gameobject templates draw as map objects")
    for kind, n in mysql(f"SELECT kind, COUNT(*) FROM {SCRATCH}.garrison_entry_remap GROUP BY kind"):
        print(f"remapped {n} {kind} entries")


def tables(live):
    rows = mysql(f"""SELECT s.table_name, l.table_name IS NOT NULL FROM information_schema.tables s
        LEFT JOIN information_schema.tables l ON l.table_schema='{live}' AND l.table_name=s.table_name
        WHERE s.table_schema='{SCRATCH}' ORDER BY s.table_name""")
    shared, owned = [], []
    for name, is_shared in rows:
        if int(mysql(f"SELECT COUNT(*) FROM {SCRATCH}.`{name}`")[0][0]) or is_shared == "0":
            (shared if is_shared == "1" else owned).append(name)
    shared = [t for t in shared if int(mysql(f"SELECT COUNT(*) FROM {SCRATCH}.`{t}`")[0][0])]
    return shared, owned


def check(live, shared):
    bad = []
    for t in shared:
        pk = [c for (c,) in mysql(f"""SELECT column_name FROM information_schema.key_column_usage WHERE table_schema='{live}'
            AND table_name='{t}' AND constraint_name='PRIMARY' ORDER BY ordinal_position""")]
        if not pk:
            raise SystemExit(f"{t} has no primary key; cannot prove its rows are free")
        on = " AND ".join(f"s.`{c}` <=> l.`{c}`" for c in pk)
        hit = int(mysql(f"SELECT COUNT(*) FROM {SCRATCH}.`{t}` s JOIN {live}.`{t}` l ON {on}")[0][0])
        if hit:
            bad.append(f"{t}: {hit}")
    if bad:
        raise SystemExit("rows still collide with " + live + ": " + ", ".join(bad))
    for kind, table, spawn, col in (("CT", "creature_template", "creature", "id"),
                                    ("GO", "gameobject_template", "gameobject", "id")):
        n = int(mysql(f"""SELECT COUNT(*) FROM {SCRATCH}.{spawn} c LEFT JOIN {SCRATCH}.{table} t ON t.entry = c.{col}
            LEFT JOIN {live}.{table} l ON l.entry = c.{col} WHERE t.entry IS NULL AND l.entry IS NULL""")[0][0])
        if n:
            raise SystemExit(f"{n} {spawn} rows name a template that exists nowhere")


def dump(args):
    r = subprocess.run(DOCKER + ["mysqldump", "-uroot", "--compact", "--complete-insert", "--skip-tz-utc",
                                 "--default-character-set=utf8mb4"] + args, capture_output=True)
    if r.returncode:
        raise SystemExit(r.stderr.decode())
    return r.stdout.decode("utf-8")


def write(live, shared, owned):
    parts = [
        "-- Generated by modules/mod-esteria-garrison/tools/build_world_sql.py from sql/source. Do not edit by hand.",
        f"-- Checked against {live}: no row below reuses a primary key Esteria already has. Safe to re-run.",
        "-- Module-owned tables are created if missing and refilled. Shared tables only receive garrison-owned keys.",
        "SET NAMES utf8mb4;", "",
    ]
    for t in owned:
        create = dump(["--no-data", SCRATCH, t]).replace("CREATE TABLE `", "CREATE TABLE IF NOT EXISTS `")
        parts += [create.strip(), f"DELETE FROM `{t}`;", dump(["--no-create-info", SCRATCH, t]).strip(), ""]
    for t in shared:
        parts += [f"-- {t}", dump(["--no-create-info", "--replace", SCRATCH, t]).strip(), ""]
    text = "\n".join(p for p in parts if p is not None)
    # mysqldump --compact still emits session-variable guards; keep the file readable
    text = "\n".join(line for line in text.splitlines() if not line.startswith("/*!40101 SET"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB): {len(owned)} module tables, {len(shared)} shared tables")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", default="acore_world")
    ap.add_argument("--keep", action="store_true", help="leave the scratch database for inspection")
    a = ap.parse_args()
    load(a.live)
    remap(a.live)
    shared, owned = tables(a.live)
    check(a.live, shared)
    write(a.live, shared, owned)
    if not a.keep:
        mysql(f"DROP DATABASE {SCRATCH};")


if __name__ == "__main__":
    main()
