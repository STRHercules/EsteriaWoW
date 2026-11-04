#!/usr/bin/env python3
"""The CoA creature and gameobject rows the imported spells and ported scripts need.

  python coa_creature_slice.py --coa-core R:/.../azerothcore-wotlk-coa

CoA's summons (minions, devices, totems, gates, ...) are rows its world updates
add: creature_template and friends, plus the display rows (creaturedisplayinfo_dbc
and its model and extra rows) a custom model needs. This replays those updates into
a scratch schema built from Esteria's own table definitions, then keeps

  * creature entries named by an imported spell's summon effect or written as a
    number in the ported source (src/coa), and
  * gameobject entries the same way,

with the display rows they point at. An entry that already exists in Esteria and
did not come from this tool's previous output is a collision: it is reported and
left out, never overwritten.

Writes data/sql/db-world/cw_coa_creatures.sql and client-patch/coa_creatures_manifest.json.
Needs the ac-database container (docker exec); the scratch schema is dropped.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
SCRATCH = "coa_cslice"

# table -> key column; a row belongs to the entry in that column
CREATURE_TABLES = {
    "creature_template": "entry",
    "creature_template_model": "CreatureID",
    "creature_template_addon": "entry",
    "creature_template_resistance": "CreatureID",
    "creature_template_movement": "CreatureId",
    "creature_template_spell": "CreatureID",
    "creature_equip_template": "CreatureID",
    "creature_text": "CreatureID",
}
GAMEOBJECT_TABLES = {
    "gameobject_template": "entry",
    "gameobject_template_addon": "entry",
}
DISPLAY_TABLES = ("creaturedisplayinfo_dbc", "creaturemodeldata_dbc", "creaturedisplayinfoextra_dbc",
                  "gameobjectdisplayinfo_dbc")
REPLAYED = (set(CREATURE_TABLES) | set(GAMEOBJECT_TABLES) | set(DISPLAY_TABLES) |
            {"smart_scripts", "creature_model_info"})
# a display with no creature_model_info row cannot spawn here ("has no model ... can't load"); CoA's core spawns
# it anyway. Rows CoA does not have get these values (stock defaults for a man-sized model).
DEFAULT_MODEL_INFO = (0.5, 1.5, 2)
# displays whose model neither client ships (CoA draws nothing for them either) -> a stock stand-in
DISPLAY_SUBSTITUTES = {
    416909: 24256,   # Oil Spill Pylon: Cataclysm oil tower -> oil drum
    28830: 22720,    # MY GREATEST INVENTION: Cataclysm GnomeCopter -> gyrocopter
    30616: 158,      # Gravebound Champion: Northrend skeleton -> skeletal warrior
    30300: 158,      # Icebound Champion (its 0.5 scale kept): Northrend skeleton -> skeletal warrior
}
# creature entries CoA's data names but its SQL never defines: (entry, name, display)
SEED_CREATURES = (
    (500153, "Rouge Dread Raven Hatchling", 945408),
    (506015, "Unstable Chronoglass", 24868),
)
STATEMENT = re.compile(r"^\s*(?:DELETE\s+FROM|INSERT\s+INTO|REPLACE\s+INTO|UPDATE)\s+`?(\w+)`?", re.I)
# spell effects whose miscvalue is a creature or gameobject entry
# (effect 112 is not a summon here: CoA's Tinker augmentations use it to apply a weapon enchant, MiscValue =
# a SpellItemEnchantment id)
CREATURE_EFFECTS = (28, 56)
GAMEOBJECT_EFFECTS = (50, 76, 104, 105, 106, 107)


def mysql(sql, database=""):
    cmd = ["docker", "exec", "-i", "ac-database", "sh", "-c",
           'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" --force -N %s' % database]
    return subprocess.run(cmd, input=sql.encode("utf-8"), capture_output=True)


def query(sql, database=""):
    r = mysql(sql, database)
    if r.returncode:
        sys.exit(r.stderr.decode())
    return [line.split("\t") for line in r.stdout.decode().split("\n") if line]


def statements(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    text = "\n".join(line for line in text.split("\n") if not line.lstrip().startswith("--"))
    for stmt in re.split(r";\s*\n", text):
        m = STATEMENT.match(stmt)
        if m and m.group(1).lower() in REPLAYED:
            yield stmt.strip() + ";"
        elif re.match(r"^\s*SET\s+@", stmt, re.I):
            yield stmt.strip() + ";"     # a variable a following row uses


def dump(table, where):
    r = subprocess.run(
        ["docker", "exec", "ac-database", "sh", "-c",
         'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --no-create-info --skip-triggers --compact '
         '--skip-lock-tables --skip-extended-insert --where="%s" %s %s' % (where, SCRATCH, table)],
        capture_output=True)
    return [line for line in r.stdout.decode("utf-8").split("\n") if line.startswith("INSERT")]


def source_numbers():
    found = set()
    coa = os.path.join(MODULE, "src", "coa")
    for name in os.listdir(coa):
        if name.endswith((".cpp", ".h")):
            text = open(os.path.join(coa, name), encoding="utf-8", errors="replace").read()
            found.update(int(n) for n in re.findall(r"\b(\d{5,7})\b", text))
    return found


def previous_entries(path):
    """Entries the last run wrote: those are ours to rewrite, not collisions."""
    if not os.path.exists(path):
        return set(), set()
    text = open(path, encoding="utf-8").read()
    head = r"^INSERT INTO `%s` (?:\([^)]*\) )?VALUES \((\d+),"
    creatures = {int(m) for m in re.findall(head % "creature_template", text, re.M)}
    objects = {int(m) for m in re.findall(head % "gameobject_template", text, re.M)}
    return creatures, objects


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coa-core", required=True)
    args = ap.parse_args()
    out_sql = os.path.join(MODULE, "data", "sql", "db-world", "cw_coa_creatures.sql")
    out_manifest = os.path.join(MODULE, "client-patch", "coa_creatures_manifest.json")

    # Read this batch, not the previous live deployment.
    manifest = json.load(open(os.path.join(MODULE, "client-patch", "coa_manifest.json"), encoding="utf-8"))
    summoned_creatures = set(manifest["summoned_creatures"])
    summoned_objects = set(manifest["summoned_objects"])
    numbers = source_numbers()

    tables = list(CREATURE_TABLES) + list(GAMEOBJECT_TABLES) + list(DISPLAY_TABLES) + ["smart_scripts",
                                                                                   "creature_model_info"]
    setup = "DROP DATABASE IF EXISTS %s; CREATE DATABASE %s;\n" % (SCRATCH, SCRATCH)
    setup += "".join("CREATE TABLE %s.%s LIKE acore_world.%s;\n" % (SCRATCH, t, t) for t in tables)
    r = mysql(setup)
    if r.returncode:
        sys.exit(r.stderr.decode())

    replay = []
    root = os.path.join(args.coa_core, "data", "sql", "updates")
    for folder in ("db_world", "pending_db_world"):
        for name in sorted(os.listdir(os.path.join(root, folder))):
            if name.endswith(".sql"):
                replay += statements(os.path.join(root, folder, name))
    r = mysql("\n".join(replay), SCRATCH)
    errors = [line for line in r.stderr.decode().split("\n") if line.startswith("ERROR")]
    print("replayed %d statements, %d failed on Esteria's schema" % (len(replay), len(errors)))
    for line in sorted({re.sub(r" at line \d+", "", e) for e in errors})[:8]:
        print("  " + line[:180])

    # Summons CoA's SQL does not define but its data names. The collection table
    # (AscensionCollectionModelData.h: { 500153, 945408, "Rouge Dread Raven Hatchling" }) gives the raven's
    # name and display; the hourglass is the community creature cache's (hertigservices/ascension-data), and CoA's
    # own client has display 24868 as the Caverns of Time hourglass. The rest follows CoA's companion rows
    # (rev_20261023_04_coa_collection_companion_creatures.sql): a neutral level 1 critter.
    for entry, name, display in SEED_CREATURES:
        mysql("INSERT INTO creature_template (entry, name, minlevel, maxlevel, faction, unit_class, type, "
              "BaseAttackTime, RangeAttackTime) VALUES (%d, '%s', 1, 1, 35, 1, 12, 2000, 2000);\n"
              "INSERT INTO creature_template_model (CreatureID, Idx, CreatureDisplayID, DisplayScale, Probability) "
              "VALUES (%d, 0, %d, 1, 1);" % (entry, name, entry, display), SCRATCH)
    mysql("UPDATE creature_template_model SET CreatureDisplayID = CASE CreatureDisplayID %s END "
          "WHERE CreatureDisplayID IN (%s);" % (" ".join("WHEN %d THEN %d" % kv for kv in DISPLAY_SUBSTITUTES.items()),
                                                ",".join(str(k) for k in DISPLAY_SUBSTITUTES)), SCRATCH)
    coa_creatures = {int(x[0]) for x in query("SELECT entry FROM creature_template", SCRATCH)}
    coa_objects = {int(x[0]) for x in query("SELECT entry FROM gameobject_template", SCRATCH)}
    # a number in the source is also a spell id, and CoA's spell and creature ids overlap: such a match
    # counts only for a creature that is not a trainer, vendor or other NPC
    plain = {int(x[0]) for x in query("SELECT entry FROM creature_template WHERE npcflag = 0", SCRATCH)}
    wanted_creatures = (summoned_creatures & coa_creatures) | (numbers & coa_creatures & plain) | \
        {entry for entry, _name, _display in SEED_CREATURES}
    wanted_objects = (summoned_objects | numbers) & coa_objects
    print("creatures: %d summoned by imported spells, %d defined by CoA, %d kept"
          % (len(summoned_creatures), len(summoned_creatures & coa_creatures), len(wanted_creatures)))
    print("summoned creatures CoA's data does not define: %s"
          % sorted(summoned_creatures - coa_creatures)[:40])

    # entries Esteria already has, and did not get from this tool, stay as they are
    mine_c, mine_o = previous_entries(out_sql)
    have_c = {int(x[0]) for x in query("SELECT entry FROM creature_template", "acore_world")} - mine_c
    have_o = {int(x[0]) for x in query("SELECT entry FROM gameobject_template", "acore_world")} - mine_o
    clash_c, clash_o = wanted_creatures & have_c, wanted_objects & have_o
    if clash_c or clash_o:
        print("left out, the ID is already in use here: creatures %s gameobjects %s"
              % (sorted(clash_c), sorted(clash_o)))
    wanted_creatures -= clash_c
    wanted_objects -= clash_o

    creature_ids = ",".join(str(i) for i in sorted(wanted_creatures)) or "0"
    object_ids = ",".join(str(i) for i in sorted(wanted_objects)) or "0"
    lines = ["-- mod-classless-wildcard: CoA creatures and gameobjects the imported spells summon, generated by",
             "-- tools/coa_creature_slice.py from the CoA core's world updates. Do not hand-edit.", ""]
    counts = {}

    def emit(table, key, ids, extra=""):
        rows = dump(table, "%s IN (%s)%s" % (key, ids, extra))
        counts[table] = len(rows)
        if rows:
            lines.append("DELETE FROM `%s` WHERE `%s` IN (%s)%s;" % (table, key, ids, extra))
            lines.extend(rows)
            lines.append("")
        return rows

    for table, key in CREATURE_TABLES.items():
        emit(table, key, creature_ids)
    emit("smart_scripts", "entryorguid", creature_ids, " AND source_type = 0")
    for table, key in GAMEOBJECT_TABLES.items():
        emit(table, key, object_ids)

    # the displays those rows point at, where CoA defines them (a stock display needs no row)
    display_ids = {int(x[0]) for x in query(
        "SELECT CreatureDisplayID FROM creature_template_model WHERE CreatureID IN (%s)" % creature_ids, SCRATCH)}
    object_displays = {int(x[0]) for x in query(
        "SELECT displayId FROM gameobject_template WHERE entry IN (%s)" % object_ids, SCRATCH)}
    shown = {int(x[0]) for x in query("SELECT ID FROM creaturedisplayinfo_dbc", SCRATCH)}
    kept_displays = sorted(display_ids & shown)
    ids = ",".join(str(i) for i in kept_displays) or "0"
    model_ids = {int(x[0]) for x in query("SELECT ModelID FROM creaturedisplayinfo_dbc WHERE ID IN (%s)" % ids, SCRATCH)}
    extra_ids = {int(x[0]) for x in query(
        "SELECT ExtendedDisplayInfoID FROM creaturedisplayinfo_dbc WHERE ID IN (%s) AND ExtendedDisplayInfoID > 0" % ids,
        SCRATCH)}
    emit("creaturedisplayinfo_dbc", "ID", ids)
    emit("creaturemodeldata_dbc", "ID", ",".join(str(i) for i in sorted(model_ids)) or "0")
    emit("creaturedisplayinfoextra_dbc", "ID", ",".join(str(i) for i in sorted(extra_ids)) or "0")
    kept_object_displays = sorted(object_displays & {int(x[0]) for x in query(
        "SELECT ID FROM gameobjectdisplayinfo_dbc", SCRATCH)})
    emit("gameobjectdisplayinfo_dbc", "ID", ",".join(str(i) for i in kept_object_displays) or "0")

    # model info for every display used; INSERT IGNORE keeps any row Esteria already has
    coa_info = {int(x[0]): x[1:4] for x in query(
        "SELECT DisplayID, BoundingRadius, CombatReach, Gender FROM creature_model_info", SCRATCH)}
    info_rows = ["(%d, %s, %s, %s, 0)" % ((d,) + tuple(coa_info.get(d, DEFAULT_MODEL_INFO)))
                 for d in sorted(display_ids)]
    counts["creature_model_info"] = len(info_rows)
    if info_rows:
        lines.append("INSERT IGNORE INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, "
                     "`Gender`, `DisplayID_Other_Gender`) VALUES")
        lines.append(",\n".join(info_rows) + ";")
        lines.append("")

    for table, n in counts.items():
        print("%-30s %d row(s)" % (table, n))
    print("displays: %d used, %d defined by CoA (%d model rows, %d extra rows), %d gameobject displays"
          % (len(display_ids), len(kept_displays), len(model_ids), len(extra_ids), len(kept_object_displays)))
    mysql("DROP DATABASE IF EXISTS %s;" % SCRATCH)

    with open(out_sql, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    with open(out_manifest, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"creatures": sorted(wanted_creatures), "gameobjects": sorted(wanted_objects),
                   "creature_displays_used": sorted(display_ids),
                   "creature_displays": kept_displays, "creature_models": sorted(model_ids),
                   "creature_extras": sorted(extra_ids), "gameobject_displays": kept_object_displays,
                   "gameobject_displays_used": sorted(object_displays)},
                  f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
