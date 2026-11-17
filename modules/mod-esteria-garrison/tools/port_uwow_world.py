"""Port the UWoW garrison world (TDB 6.03 + UWoW sql/uwow, staged in tdb6_world/tdb6_hotfixes) to AzerothCore.

Writes data/sql/db-world/garrison_uwow_world.sql and the CreatureDisplayInfo / CreatureModelData /
GameObjectDisplayInfo rows (server DBC + client garrison patch). Display ids keep their retail value unless
the id is already taken by a different model, in which case they move to DISPLAY_REMAP + id.
"""
from __future__ import annotations

import csv
import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path

import mysql.connector

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(HERE))
from make_residents import (  # noqa: E402
    CLIENT, CREATURE_DISPLAY_DBC, CREATURE_MODEL_DBC, GO_DISPLAY_DBC, MAP_DBC, PATCH_NAME, SERVER_DBC_DIRS,
    STORMLIB, Storm, append_string, f32, read_wdbc, write_wdbc,
)

REF = Path(r"G:\risServer\_ref")
OUT_SQL = MODULE / "data" / "sql" / "db-world" / "garrison_uwow_world.sql"
MAP_JSON = HERE / "garrison_display_map.json"
MAPS = (1152, 1330, 1153, 1158, 1331, 1159)
CGUID_BASE = 5100000
OGUID_BASE = 5100000
DISPLAY_REMAP = 800000
SCRIPT_NAMES: set[str] = set()   # TC script names the module implements keep their ScriptName

# 38 building and 39 plot are WMO displays. 3.3.5 type 5 loads that path as an M2 and
# draws Spells\ErrorCube.mdx. Type 14 is a map object: no M2, the WMO is placed as a building.
WOD_TYPE_TO_335 = {38: 14, 39: 14, 45: 10}


def connect(db):
    return mysql.connector.connect(host="127.0.0.1", user="acore", password="acore", database=db, charset="utf8mb4")


def rows(conn, sql, args=()):
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, args)
    return cur.fetchall()


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, (bytes, bytearray)):
        v = v.decode("utf-8", "replace")
    if isinstance(v, str):
        return "'" + v.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r") + "'"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def insert(table, cols, values_rows, chunk=400):
    out = []
    for i in range(0, len(values_rows), chunk):
        body = ",\n".join("(" + ",".join(q(v) for v in r) + ")" for r in values_rows[i:i + chunk])
        out.append(f"INSERT INTO `{table}` (`" + "`,`".join(cols) + f"`) VALUES\n{body};")
    return out


def in_list(ids):
    ids = sorted({int(i) for i in ids})
    return ",".join(map(str, ids)) if ids else "NULL"


def load_csv(name, key="ID"):
    with (REF / name).open(encoding="utf-8", newline="") as f:
        return {int(r[key]): r for r in csv.DictReader(f)}


def dbc_rows(path: Path):
    fields, size, rs, blob = read_wdbc(path.read_bytes())
    return fields, size, {struct.unpack_from("<I", r)[0]: r for r in rs}, blob


def dbc_string(blob, off):
    end = blob.find(b"\0", off)
    return bytes(blob[off:end]).decode("utf-8", "replace")


def listfile_ext(fdids: set[int]) -> dict[int, str]:
    want = {str(i) for i in fdids}
    out = {}
    with (REF / "community-listfile.csv").open(encoding="utf-8", errors="replace") as f:
        for line in f:
            fid, _, name = line.rstrip("\n").partition(";")
            if fid in want:
                out[int(fid)] = name.rsplit(".", 1)[-1].lower()
    return out


class World:
    def __init__(self):
        self.tdb = connect("tdb6_world")
        self.hot = connect("tdb6_hotfixes")
        self.ac = connect("acore_world")
        self.sql: list[str] = []
        self.report: dict[str, list] = defaultdict(list)
        self.cdi = load_csv("wago_CreatureDisplayInfo.csv")
        self.cmd = load_csv("wago_CreatureModelData.csv")
        self.godi = load_csv("wago_GameObjectDisplayInfo.csv")
        self.db2go = load_csv("wago_GameObjects.csv")
        dbc_dir = SERVER_DBC_DIRS[0]
        self.srv_cdi = dbc_rows(dbc_dir / "CreatureDisplayInfo.dbc")
        self.srv_cmd = dbc_rows(dbc_dir / "CreatureModelData.dbc")
        self.srv_godi = dbc_rows(dbc_dir / "GameObjectDisplayInfo.dbc")
        self.srv_sound = dbc_rows(dbc_dir / "SoundEntries.dbc")[2].keys()
        self.creature_display: dict[int, int] = {}   # retail CDI -> local
        self.creature_model: dict[int, int] = {}     # retail CMD -> local
        self.go_display: dict[int, int] = {}         # retail GODI -> local

    # ---------------------------------------------------------------- selection
    def select(self):
        m = in_list(MAPS)
        self.c_spawns = rows(self.tdb, f"SELECT * FROM creature WHERE map IN ({m}) ORDER BY guid")
        self.g_spawns = rows(self.tdb, f"SELECT * FROM gameobject WHERE map IN ({m}) ORDER BY guid")
        self.b_creatures = rows(self.tdb, "SELECT * FROM garrison_building_creature ORDER BY idx")
        self.b_objects = rows(self.tdb, "SELECT * FROM garrison_building_gameobject ORDER BY idx")
        self.finalize = rows(self.tdb, "SELECT * FROM garrison_plot_finalize_info")
        self.shipments = rows(self.tdb, "SELECT * FROM garrison_shipment")
        self.mission_lines = rows(self.tdb, "SELECT * FROM garrison_mission_line")
        self.class_spec = rows(self.tdb, "SELECT * FROM garrison_follower_class_spec_abilities")

        c_entries = {r["id"] for r in self.c_spawns} | {r["id"] for r in self.b_creatures} | {r["NpcEntry"] for r in self.shipments}
        g_entries = {r["id"] for r in self.g_spawns} | {r["id"] for r in self.b_objects}
        g_entries |= {r["hordeGameObjectId"] for r in self.finalize} | {r["allianceGameObjectId"] for r in self.finalize}
        for r in self.db2go.values():
            if int(r["TypeID"]) == 39 and int(r["OwnerID"]) in MAPS:
                g_entries.add(int(r["ID"]))
        with (REF / "garr_csv" / "GarrBuilding.csv").open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                g_entries |= {int(r["HordeGameObjectID"]), int(r["AllianceGameObjectID"])}
        with (REF / "garr_csv" / "GarrPlot.csv").open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                g_entries |= {int(r["HordeConstructObjID"]), int(r["AllianceConstructObjID"])}
        g_entries.discard(0)

        self.ct = {r["entry"]: r for r in rows(self.tdb, f"SELECT * FROM creature_template WHERE entry IN ({in_list(c_entries)})")}
        self.gt = {r["entry"]: r for r in rows(self.tdb, f"SELECT * FROM gameobject_template WHERE entry IN ({in_list(g_entries)})")}
        for e in sorted(g_entries - set(self.gt)):
            d = self.db2go.get(e)
            if not d:
                self.report["gameobject template missing everywhere"].append(e)
                continue
            self.gt[e] = {
                "entry": e, "type": int(d["TypeID"]), "displayId": int(d["DisplayID"]), "name": d["Name_lang"],
                "IconName": "", "castBarCaption": "", "unk1": "", "faction": 0, "flags": 0, "size": float(d["Scale"]),
                **{f"Data{i}": (int(d[f"PropValue_{i}"]) if i < 8 else 0) for i in range(33)},
                "AIName": "", "ScriptName": "", "VerifiedBuild": 0, "_db2": True,
            }
        self.report["creature template missing in TDB 6.03"] = sorted(c_entries - set(self.ct))
        self.c_spawns = [r for r in self.c_spawns if r["id"] in self.ct]
        self.b_creatures = [r for r in self.b_creatures if r["id"] in self.ct]
        self.g_spawns = [r for r in self.g_spawns if r["id"] in self.gt]
        self.b_objects = [r for r in self.b_objects if r["id"] in self.gt]

        superseded = set()
        for old in (MODULE / "sql" / "world").glob("*.sql"):
            superseded |= {int(t) for t in re.findall(r"\b\d{5,7}\b", old.read_text(encoding="utf-8", errors="replace"))}
        existing_c = {r["entry"]: r["name"] for r in rows(self.ac, f"SELECT entry, name FROM creature_template WHERE entry IN ({in_list(self.ct)})")}
        existing_g = {r["entry"]: r["name"] for r in rows(self.ac, f"SELECT entry, name FROM gameobject_template WHERE entry IN ({in_list(self.gt)})")}
        existing_c = {e: n for e, n in existing_c.items() if e not in superseded}
        existing_g = {e: n for e, n in existing_g.items() if e not in superseded}
        for e, name in existing_c.items():
            if name.strip().lower() != (self.ct[e]["name"] or "").strip().lower() and not name.startswith("Garrison"):
                self.report["creature entry collides with a different AC creature (kept AC)"].append((e, name, self.ct[e]["name"]))
                del self.ct[e]
        for e, name in existing_g.items():
            if name.strip().lower() != (self.gt[e]["name"] or "").strip().lower() and not name.startswith("Garrison Object"):
                self.report["gameobject entry collides with a different AC object (kept AC)"].append((e, name, self.gt[e]["name"]))
                del self.gt[e]

    # ---------------------------------------------------------------- displays
    def map_display(self, retail_id, srv, retail_tab, model_of, mapping):
        if retail_id in mapping:
            return mapping[retail_id]
        if retail_id not in retail_tab:
            return 0
        fields, size, taken, blob = srv
        local = retail_id
        if retail_id in taken and not model_of(taken[retail_id], blob, retail_id):
            local = DISPLAY_REMAP + retail_id
        mapping[retail_id] = local
        return local

    def creature_display_id(self, retail_cdi):
        if not retail_cdi:
            return 0
        def same(row, blob, rid):
            model_id = struct.unpack_from("<I", row, 4)[0]
            mrow = self.srv_cmd[2].get(model_id)
            want = int(self.cmd.get(int(self.cdi[rid]["ModelID"]), {}).get("FileDataID", 0) or 0)
            return bool(mrow) and dbc_string(self.srv_cmd[3], struct.unpack_from("<I", mrow, 8)[0]).lower() == f"retail\\{want}.m2"
        local = self.map_display(retail_cdi, self.srv_cdi, self.cdi, same, self.creature_display)
        if local:
            model = int(self.cdi[retail_cdi]["ModelID"])
            if model not in self.creature_model and model in self.cmd:
                taken = self.srv_cmd[2]
                want = f"retail\\{self.cmd[model]['FileDataID']}.m2"
                clash = model in taken and dbc_string(self.srv_cmd[3], struct.unpack_from("<I", taken[model], 8)[0]).lower() != want
                self.creature_model[model] = DISPLAY_REMAP + model if clash else model
        return local

    def go_display_id(self, retail_godi):
        if not retail_godi:
            return 0
        def same(row, blob, rid):
            fdid = self.godi[rid]["FileDataID"]
            name = dbc_string(blob, struct.unpack_from("<I", row, 4)[0]).lower()
            return name.startswith(f"retail\\{fdid}.")
        return self.map_display(retail_godi, self.srv_godi, self.godi, same, self.go_display)

    # ---------------------------------------------------------------- SQL
    def cleanup(self):
        m = in_list(MAPS)
        self.sql += [
            "-- Generated by modules/mod-esteria-garrison/tools/port_uwow_world.py from TDB 6.03 + UWoW sql/uwow.",
            "DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9601100 AND 9601999;",
            "DELETE FROM `creature_template` WHERE `entry` BETWEEN 9601100 AND 9601999;",
            "DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9602000 AND 9602999;",
            "DROP TABLE IF EXISTS `garrison_map_creature`, `garrison_map_gameobject`;",
            f"DELETE FROM `creature_addon` WHERE `guid` IN (SELECT `guid` FROM `creature` WHERE `map` IN ({m}));",
            f"DELETE FROM `creature` WHERE `map` IN ({m});",
            f"DELETE FROM `gameobject` WHERE `map` IN ({m});",
            f"DELETE FROM `waypoint_data` WHERE `id` BETWEEN {CGUID_BASE * 10} AND {(CGUID_BASE + 99999) * 10 + 9};",
        ]

    def creature_templates(self):
        ids = in_list(self.ct)
        self.sql += [f"DELETE FROM `creature_template` WHERE `entry` IN ({ids});",
                     f"DELETE FROM `creature_template_model` WHERE `CreatureID` IN ({ids});",
                     f"DELETE FROM `creature_template_addon` WHERE `entry` IN ({ids});",
                     f"DELETE FROM `creature_template_movement` WHERE `CreatureId` IN ({ids});",
                     f"DELETE FROM `creature_equip_template` WHERE `CreatureID` IN ({ids});",
                     "CREATE TABLE IF NOT EXISTS `garrison_creature_npcflag2` (`entry` INT UNSIGNED NOT NULL PRIMARY KEY, `npcflag2` INT UNSIGNED NOT NULL DEFAULT 0) ENGINE=InnoDB;",
                     "DELETE FROM `garrison_creature_npcflag2`;"]
        cols = ["entry", "KillCredit1", "KillCredit2", "name", "subname", "IconName", "gossip_menu_id", "minlevel", "maxlevel",
                "exp", "faction", "npcflag", "speed_walk", "speed_run", "rank", "dmgschool", "DamageModifier", "BaseAttackTime",
                "RangeAttackTime", "BaseVariance", "RangeVariance", "unit_class", "unit_flags", "unit_flags2", "dynamicflags",
                "family", "type", "type_flags", "lootid", "pickpocketloot", "skinloot", "VehicleId", "mingold", "maxgold",
                "AIName", "MovementType", "HoverHeight", "HealthModifier", "ManaModifier", "ArmorModifier", "ExperienceModifier",
                "RacialLeader", "movementId", "RegenHealth", "flags_extra", "ScriptName", "VerifiedBuild"]
        vals, models, movement, npcflag2, mi = [], [], [], [], {}
        for e, t in sorted(self.ct.items()):
            v = dict(t)
            v["minlevel"] = min(int(t["minlevel"]), 100)
            v["maxlevel"] = min(int(t["maxlevel"]), 100)
            v["exp"] = min(int(t["exp"]), 2)
            # WoD rank 5 (trivial) and 6 (minuscule) are past the 3.3.5 client's classification colour table
            v["rank"] = min(int(t["rank"] or 0), 4)
            v["faction"] = t["faction"] or 35
            v["npcflag"] = int(t["npcflag"]) & 0x03FFFFFF
            v["ScriptName"] = t["ScriptName"] if t["ScriptName"] in SCRIPT_NAMES else ""
            v["VerifiedBuild"] = t["VerifiedBuild"] or 0
            vals.append([v[c] for c in cols])
            for idx in range(4):
                retail = int(t[f"modelid{idx + 1}"] or 0)
                local = self.creature_display_id(retail)
                if local:
                    models.append([e, idx, local, float(t["scale"] or 1.0), 1.0, 0])
                    mi[retail] = local
                elif retail:
                    self.report["creature display missing in retail CreatureDisplayInfo"].append((e, retail))
            inhabit = int(t["InhabitType"] or 1)
            movement.append([e, 1 if inhabit & 1 else 0, 1 if inhabit & 2 else 0, 1 if inhabit & 4 else 0, 1 if inhabit & 8 else 0])
            if t.get("npcflag2"):
                npcflag2.append([e, int(t["npcflag2"])])
        self.sql += insert("creature_template", cols, vals)
        self.sql += insert("creature_template_model", ["CreatureID", "Idx", "CreatureDisplayID", "DisplayScale", "Probability", "VerifiedBuild"], models)
        self.sql += insert("creature_template_movement", ["CreatureId", "Ground", "Swim", "Flight", "Rooted"], movement)
        self.sql += insert("garrison_creature_npcflag2", ["entry", "npcflag2"], npcflag2)

        info = {r["DisplayID"]: r for r in rows(self.tdb, f"SELECT * FROM creature_model_info WHERE DisplayID IN ({in_list(mi)})")}
        mrows = []
        for retail, local in sorted(mi.items()):
            r = info.get(retail)
            gender = int(self.cdi[retail].get("Gender", 2) or 2)
            other = r and self.creature_display.get(int(r["DisplayID_Other_Gender"] or 0), 0) or 0
            mrows.append([local, float(r["BoundingRadius"]) if r else 0.5, float(r["CombatReach"]) if r else 1.5, gender, other, 0])
        self.sql.append(f"DELETE FROM `creature_model_info` WHERE `DisplayID` IN ({in_list(mi.values())});")
        self.sql += insert("creature_model_info", ["DisplayID", "BoundingRadius", "CombatReach", "Gender", "DisplayID_Other_Gender", "VerifiedBuild"], mrows)

        addons = rows(self.tdb, f"SELECT * FROM creature_template_addon WHERE entry IN ({ids})")
        self.sql += insert("creature_template_addon", ["entry", "path_id", "mount", "bytes1", "bytes2", "emote", "visibilityDistanceType", "auras"],
                           [[a["entry"], 0, self.creature_display_id(int(a["mount"] or 0)), a["bytes1"], a["bytes2"], a["emote"], 0, ""] for a in addons])
        items = {r["entry"] for r in rows(self.ac, "SELECT entry FROM item_template")}
        equips = []
        for r in rows(self.tdb, f"SELECT * FROM creature_equip_template WHERE CreatureID IN ({ids})"):
            got = [i if i in items else 0 for i in (r["ItemID1"], r["ItemID2"], r["ItemID3"])]
            if any(got):
                equips.append([r["CreatureID"], r["ID"], *got, 0])
            if got != [r["ItemID1"], r["ItemID2"], r["ItemID3"]]:
                self.report["equipment items missing in 3.3.5 item_template"].append((r["CreatureID"], r["ItemID1"], r["ItemID2"], r["ItemID3"]))
        self.equip_ids = {(e[0], e[1]) for e in equips}
        self.sql += insert("creature_equip_template", ["CreatureID", "ID", "ItemID1", "ItemID2", "ItemID3", "VerifiedBuild"], equips)

    def gameobject_templates(self):
        ids = in_list(self.gt)
        self.sql += [f"DELETE FROM `gameobject_template` WHERE `entry` IN ({ids});",
                     f"DELETE FROM `gameobject_template_addon` WHERE `entry` IN ({ids});",
                     "CREATE TABLE IF NOT EXISTS `garrison_gameobject_wod_type` (`entry` INT UNSIGNED NOT NULL PRIMARY KEY, `type` TINYINT UNSIGNED NOT NULL, "
                     "`Data0` INT NOT NULL DEFAULT 0, `Data1` INT NOT NULL DEFAULT 0, `Data2` INT NOT NULL DEFAULT 0, `Data3` INT NOT NULL DEFAULT 0) ENGINE=InnoDB;",
                     "DELETE FROM `garrison_gameobject_wod_type`;"]
        cols = ["entry", "type", "displayId", "name", "IconName", "castBarCaption", "unk1", "size"] + [f"Data{i}" for i in range(24)] + ["AIName", "ScriptName", "VerifiedBuild"]
        vals, addon, wod = [], [], []
        for e, t in sorted(self.gt.items()):
            wtype = int(t["type"])
            ltype = WOD_TYPE_TO_335.get(wtype, wtype if wtype <= 35 else 5)
            data = [int(t[f"Data{i}"] or 0) for i in range(24)]
            if ltype != wtype:
                wod.append([e, wtype, *[int(t[f"Data{i}"] or 0) for i in range(4)]])
                data = [0] * 24
            display = self.go_display_id(int(t["displayId"] or 0))
            if t["displayId"] and not display:
                self.report["gameobject display missing in retail GameObjectDisplayInfo"].append((e, t["displayId"]))
            vals.append([e, ltype, display, t["name"] or "", t["IconName"] or "", t["castBarCaption"] or "", t["unk1"] or "",
                         float(t["size"] or 1.0), *data, t["AIName"] or "", t["ScriptName"] if t["ScriptName"] in SCRIPT_NAMES else "", t["VerifiedBuild"] or 0])
            if t.get("faction") or t.get("flags"):
                addon.append([e, int(t["faction"] or 0), int(t["flags"] or 0), 0, 0, 0, 0, 0, 0])
        self.sql += insert("gameobject_template", cols, vals)
        self.sql += insert("gameobject_template_addon", ["entry", "faction", "flags", "mingold", "maxgold", "artkit0", "artkit1", "artkit2", "artkit3"], addon)
        self.sql += insert("garrison_gameobject_wod_type", ["entry", "type", "Data0", "Data1", "Data2", "Data3"], wod)

    def spawns(self):
        self.cguid = {r["guid"]: CGUID_BASE + i for i, r in enumerate(self.c_spawns)}
        self.oguid = {r["guid"]: OGUID_BASE + i for i, r in enumerate(self.g_spawns)}
        addons = {r["guid"]: r for r in rows(self.tdb, f"SELECT * FROM creature_addon WHERE guid IN ({in_list(self.cguid)})")}
        paths = {}
        for old, a in addons.items():
            if a["path_id"]:
                paths[a["path_id"]] = self.cguid[old] * 10
        cvals, avals = [], []
        for r in self.c_spawns:
            new = self.cguid[r["guid"]]
            equip = r["equipment_id"] if (r["id"], r["equipment_id"]) in self.equip_ids else 0
            movement = r["MovementType"]
            a = addons.get(r["guid"])
            if movement == 2 and not (a and a["path_id"] in paths):
                movement = 0
            cvals.append([new, r["id"], r["map"], r["zoneId"], r["areaId"], 1, 1, equip, r["position_x"], r["position_y"], r["position_z"],
                          r["orientation"], r["spawntimesecs"], r["spawndist"], 0, 1, 0, movement, 0, 0, 0, "", 0, 0,
                          f"UWoW garrison guid {r['guid']}"])
            if a:
                avals.append([new, paths.get(a["path_id"], 0), self.creature_display_id(int(a["mount"] or 0)), a["bytes1"], a["bytes2"], a["emote"], 0, ""])
        self.sql += insert("creature", ["guid", "id", "map", "zoneId", "areaId", "spawnMask", "phaseMask", "equipment_id", "position_x", "position_y",
                                        "position_z", "orientation", "spawntimesecs", "wander_distance", "currentwaypoint", "curhealth", "curmana",
                                        "MovementType", "npcflag", "unit_flags", "dynamicflags", "ScriptName", "VerifiedBuild", "CreateObject", "Comment"], cvals)
        self.sql += insert("creature_addon", ["guid", "path_id", "mount", "bytes1", "bytes2", "emote", "visibilityDistanceType", "auras"], avals)
        wps = rows(self.tdb, f"SELECT * FROM waypoint_data WHERE id IN ({in_list(paths)}) ORDER BY id, point")
        self.sql += insert("waypoint_data", ["id", "point", "position_x", "position_y", "position_z", "orientation", "velocity", "delay",
                                             "smoothTransition", "move_type", "action", "action_chance", "wpguid"],
                           [[paths[w["id"]], w["point"], w["position_x"], w["position_y"], w["position_z"], w["orientation"], 0, w["delay"], 0,
                             w["move_type"], 0, 100, 0] for w in wps])
        # WoD type 38 is the finished building. The garrison script spawns it when the player builds
        # the plot. A static copy sits on the empty plot as if the barracks were already there.
        def placeable_building(row):
            template = self.gt.get(row["id"])
            return template is not None and int(template["type"]) == 38
        skipped = [r for r in self.g_spawns if placeable_building(r)]
        self.report["building spawns left to the garrison script"] = len(skipped)
        gvals = [[self.oguid[r["guid"]], r["id"], r["map"], r["zoneId"], r["areaId"], 1, 1, r["position_x"], r["position_y"], r["position_z"],
                  r["orientation"], r["rotation0"], r["rotation1"], r["rotation2"], r["rotation3"], r["spawntimesecs"], r["animprogress"],
                  r["state"], "", 0, f"UWoW garrison guid {r['guid']}"] for r in self.g_spawns if not placeable_building(r)]
        self.sql += insert("gameobject", ["guid", "id", "map", "zoneId", "areaId", "spawnMask", "phaseMask", "position_x", "position_y",
                                          "position_z", "orientation", "rotation0", "rotation1", "rotation2", "rotation3", "spawntimesecs",
                                          "animprogress", "state", "ScriptName", "VerifiedBuild", "Comment"], gvals)

    def garrison_tables(self):
        self.sql += [
            "DROP TABLE IF EXISTS `garrison_building_creature`, `garrison_building_gameobject`, `garrison_plot_finalize_info`, "
            "`garrison_mission_line`, `garrison_shipment`, `garrison_follower_class_spec_abilities`;",
            "CREATE TABLE `garrison_building_creature` (`plotID` MEDIUMINT UNSIGNED NOT NULL, `BuildID` MEDIUMINT UNSIGNED NOT NULL, "
            "`id` MEDIUMINT UNSIGNED NOT NULL DEFAULT 0, `map` SMALLINT UNSIGNED NOT NULL DEFAULT 0, `position_x` FLOAT NOT NULL DEFAULT 0, "
            "`position_y` FLOAT NOT NULL DEFAULT 0, `position_z` FLOAT NOT NULL DEFAULT 0, `orientation` FLOAT NOT NULL DEFAULT 0, "
            "`building` SMALLINT UNSIGNED NOT NULL DEFAULT 0, `idx` INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (`idx`)) ENGINE=InnoDB COMMENT='Garrison building spawn System';",
            "CREATE TABLE `garrison_building_gameobject` (`plotID` MEDIUMINT UNSIGNED NOT NULL, `BuildID` MEDIUMINT UNSIGNED NOT NULL, "
            "`id` MEDIUMINT UNSIGNED NOT NULL DEFAULT 0, `map` SMALLINT UNSIGNED NOT NULL DEFAULT 0, `position_x` FLOAT NOT NULL DEFAULT 0, "
            "`position_y` FLOAT NOT NULL DEFAULT 0, `position_z` FLOAT NOT NULL DEFAULT 0, `orientation` FLOAT NOT NULL DEFAULT 0, "
            "`rotation0` FLOAT NOT NULL DEFAULT 0, `rotation1` FLOAT NOT NULL DEFAULT 0, `rotation2` FLOAT NOT NULL DEFAULT 0, "
            "`rotation3` FLOAT NOT NULL DEFAULT 0, `building` TINYINT UNSIGNED NOT NULL DEFAULT 0, `idx` INT NOT NULL AUTO_INCREMENT, "
            "PRIMARY KEY (`idx`)) ENGINE=InnoDB COMMENT='Garrison building spawn System';",
            "CREATE TABLE `garrison_plot_finalize_info` (`garrPlotInstanceId` INT UNSIGNED NOT NULL, `hordeGameObjectId` INT UNSIGNED NOT NULL DEFAULT 0, "
            "`hordeX` FLOAT NOT NULL DEFAULT 0, `hordeY` FLOAT NOT NULL DEFAULT 0, `hordeZ` FLOAT NOT NULL DEFAULT 0, `hordeO` FLOAT NOT NULL DEFAULT 0, "
            "`allianceGameObjectId` INT UNSIGNED NOT NULL DEFAULT 0, `allianceX` FLOAT NOT NULL DEFAULT 0, `allianceY` FLOAT NOT NULL DEFAULT 0, "
            "`allianceZ` FLOAT NOT NULL DEFAULT 0, `allianceO` FLOAT NOT NULL DEFAULT 0, PRIMARY KEY (`garrPlotInstanceId`)) ENGINE=InnoDB;",
            "CREATE TABLE `garrison_mission_line` (`ID` INT UNSIGNED NOT NULL, `NextMission` INT UNSIGNED NOT NULL DEFAULT 0, "
            "`ReqGarrFollowerID` INT UNSIGNED NOT NULL DEFAULT 0, `IsRandom` TINYINT(1) NOT NULL DEFAULT 0, `Comment` VARCHAR(40) NOT NULL DEFAULT '', "
            "PRIMARY KEY (`ID`)) ENGINE=InnoDB;",
            "CREATE TABLE `garrison_shipment` (`SiteID` INT NOT NULL DEFAULT 2, `ContainerID` INT NOT NULL, `NpcEntry` INT UNSIGNED NOT NULL, "
            "`ShipmentID` INT UNSIGNED NOT NULL, `comment` VARCHAR(100) DEFAULT NULL, PRIMARY KEY (`NpcEntry`, `ContainerID`), KEY `ContainerID` (`ContainerID`)) ENGINE=InnoDB;",
            "CREATE TABLE `garrison_follower_class_spec_abilities` (`classSpecId` INT UNSIGNED NOT NULL DEFAULT 0, `abilityId` INT UNSIGNED NOT NULL DEFAULT 0, "
            "PRIMARY KEY (`classSpecId`, `abilityId`)) ENGINE=InnoDB;",
        ]
        bc = ["plotID", "BuildID", "id", "map", "position_x", "position_y", "position_z", "orientation", "building"]
        self.sql += insert("garrison_building_creature", bc, [[r[c] for c in bc] for r in self.b_creatures])
        bg = bc[:8] + ["rotation0", "rotation1", "rotation2", "rotation3", "building"]
        self.sql += insert("garrison_building_gameobject", bg, [[r[c] for c in bg] for r in self.b_objects])
        for table, data in (("garrison_plot_finalize_info", self.finalize), ("garrison_mission_line", self.mission_lines),
                            ("garrison_shipment", self.shipments), ("garrison_follower_class_spec_abilities", self.class_spec)):
            if data:
                cols = list(data[0].keys())
                self.sql += insert(table, cols, [[r[c] for c in cols] for r in data])

    def texts_and_scripts(self):
        entries = set(self.ct)
        g_entries = set(self.gt)
        neg = {-old: -new for old, new in self.cguid.items()}
        gneg = {-old: -new for old, new in self.oguid.items()}
        smart = rows(self.tdb, f"SELECT * FROM smart_scripts WHERE (source_type=0 AND (entryorguid IN ({in_list(entries)}) OR entryorguid IN ({in_list(neg) if neg else 'NULL'}))) "
                               f"OR (source_type=1 AND (entryorguid IN ({in_list(g_entries)}) OR entryorguid IN ({in_list(gneg) if gneg else 'NULL'})))")
        lists = {int(r["action_param1"]) for r in smart if r["action_type"] == 80}
        lists |= {int(r[p]) for r in smart if r["action_type"] in (87, 88) for p in ("action_param1", "action_param2", "action_param3", "action_param4", "action_param5", "action_param6") if r[p]}
        if lists:
            smart += rows(self.tdb, f"SELECT * FROM smart_scripts WHERE source_type=9 AND entryorguid IN ({in_list(lists)})")
        sc = ["entryorguid", "source_type", "id", "link", "event_type", "event_phase_mask", "event_chance", "event_flags", "event_param1", "event_param2",
              "event_param3", "event_param4", "event_param5", "event_param6", "action_type", "action_param1", "action_param2", "action_param3", "action_param4",
              "action_param5", "action_param6", "target_type", "target_param1", "target_param2", "target_param3", "target_param4", "target_x", "target_y",
              "target_z", "target_o", "comment"]
        svals = []
        for r in smart:
            eog = r["entryorguid"]
            if r["source_type"] == 0 and eog < 0:
                eog = neg.get(eog, eog)
            if r["source_type"] == 1 and eog < 0:
                eog = gneg.get(eog, eog)
            svals.append([eog, r["source_type"], r["id"], r["link"], r["event_type"], r["event_phase_mask"], r["event_chance"], r["event_flags"],
                          r["event_param1"], r["event_param2"], r["event_param3"], r["event_param4"], 0, 0, r["action_type"], r["action_param1"],
                          r["action_param2"], r["action_param3"], r["action_param4"], r["action_param5"], r["action_param6"], r["target_type"],
                          r["target_param1"], r["target_param2"], r["target_param3"], 0, r["target_x"], r["target_y"], r["target_z"], r["target_o"], r["comment"]])
        keys = {(v[0], v[1]) for v in svals}
        for eog, st in sorted(keys):
            self.sql.append(f"DELETE FROM `smart_scripts` WHERE `entryorguid`={eog} AND `source_type`={st};")
        self.sql += insert("smart_scripts", sc, svals)

        texts = rows(self.tdb, f"SELECT * FROM creature_text WHERE entry IN ({in_list(entries)})")
        bt_ids = {int(t["BroadcastTextId"] or 0) for t in texts}
        self.sql.append(f"DELETE FROM `creature_text` WHERE `CreatureID` IN ({in_list(entries)});")
        self.sql += insert("creature_text", ["CreatureID", "GroupID", "ID", "Text", "Type", "Language", "Probability", "Emote", "Duration", "Sound",
                                             "BroadcastTextId", "TextRange", "comment"],
                           [[t["entry"], t["groupid"], t["id"], t["text"], t["type"], t["language"], t["probability"], t["emote"], t["duration"],
                             t["sound"] if t["sound"] in self.srv_sound else 0, t["BroadcastTextId"], t["TextRange"], t["comment"]] for t in texts])

        menus = {int(t["gossip_menu_id"]) for t in self.ct.values() if t["gossip_menu_id"]}
        menus |= {int(r["action_param1"]) for r in smart if r["event_type"] == 62}
        all_menus, all_opts, frontier = set(), [], set(menus)
        while frontier:
            all_menus |= frontier
            opts = rows(self.tdb, f"SELECT * FROM gossip_menu_option WHERE menu_id IN ({in_list(frontier)})")
            all_opts += opts
            frontier = {int(o["action_menu_id"]) for o in opts if o["action_menu_id"]} - all_menus
        # Menu 0 is the core's default menu and OptionType 22 (GOSSIP_OPTION_GARRISON_SHIPMENT) is unknown to 3.3.5:
        # the module adds those options itself from garrison_gossip_shipment_option.
        ship_opts = rows(self.tdb, f"SELECT * FROM gossip_menu_option WHERE option_id = 22 AND menu_id IN ({in_list(all_menus | {0})})")
        all_menus.discard(0)
        all_opts = [o for o in all_opts if int(o["menu_id"]) != 0 and int(o["option_id"]) != 22]
        self.sql += ["DROP TABLE IF EXISTS `garrison_gossip_shipment_option`;",
                     "CREATE TABLE `garrison_gossip_shipment_option` (`MenuID` INT UNSIGNED NOT NULL, `OptionID` SMALLINT UNSIGNED NOT NULL, "
                     "`OptionIcon` TINYINT UNSIGNED NOT NULL DEFAULT 0, `OptionText` TEXT, `OptionBroadcastTextID` INT NOT NULL DEFAULT 0, "
                     "PRIMARY KEY (`MenuID`, `OptionID`)) ENGINE=InnoDB;"]
        self.sql += insert("garrison_gossip_shipment_option", ["MenuID", "OptionID", "OptionIcon", "OptionText", "OptionBroadcastTextID"],
                           [[o["menu_id"], o["id"], o["option_icon"], o["option_text"] or "", o["OptionBroadcastTextID"] or 0] for o in ship_opts])
        gm = rows(self.tdb, f"SELECT * FROM gossip_menu WHERE entry IN ({in_list(all_menus)})")
        npc = rows(self.tdb, f"SELECT * FROM npc_text WHERE ID IN ({in_list(g['text_id'] for g in gm)})")
        for n in npc:
            bt_ids |= {int(n[f"BroadcastTextID{i}"] or 0) for i in range(8)}
        bt_ids |= {int(o["OptionBroadcastTextID"] or 0) for o in all_opts + ship_opts} | {int(o["BoxBroadcastTextID"] or 0) for o in all_opts}
        bt_ids.discard(0)
        bts = {r["ID"]: r for r in rows(self.hot, f"SELECT * FROM broadcast_text WHERE ID IN ({in_list(bt_ids)})")} if bt_ids else {}
        locs = rows(self.hot, f"SELECT * FROM broadcast_text_locale WHERE ID IN ({in_list(bts)})") if bts else []

        self.sql.append(f"DELETE FROM `gossip_menu` WHERE `MenuID` IN ({in_list(all_menus)});")
        self.sql += insert("gossip_menu", ["MenuID", "TextID"], [[g["entry"], g["text_id"]] for g in gm])
        self.sql.append(f"DELETE FROM `gossip_menu_option` WHERE `MenuID` IN ({in_list(all_menus)});")
        self.sql += insert("gossip_menu_option", ["MenuID", "OptionID", "OptionIcon", "OptionText", "OptionBroadcastTextID", "OptionType", "OptionNpcFlag",
                                                  "ActionMenuID", "ActionPoiID", "BoxCoded", "BoxMoney", "BoxText", "BoxBroadcastTextID", "VerifiedBuild"],
                           [[o["menu_id"], o["id"], o["option_icon"], o["option_text"] or "", o["OptionBroadcastTextID"] or 0, o["option_id"],
                             int(o["npc_option_npcflag"]) & 0x03FFFFFF, o["action_menu_id"], o["action_poi_id"], o["box_coded"], o["box_money"],
                             o["box_text"] or "", o["BoxBroadcastTextID"] or 0, 0] for o in all_opts])
        ntc = ["ID"]
        for i in range(8):
            ntc += [f"text{i}_0", f"text{i}_1", f"BroadcastTextID{i}", f"lang{i}", f"Probability{i}"] + [f"em{i}_{k}" for k in range(6)]
        ntc.append("VerifiedBuild")
        nvals = []
        for n in npc:
            v = [n["ID"]]
            for i in range(8):
                b = bts.get(int(n[f"BroadcastTextID{i}"] or 0))
                bcols = list(b.keys()) if b else []
                male = b and (b.get("MaleText") or b.get("Text")) or ""
                female = b and (b.get("FemaleText") or b.get("Text1")) or ""
                lang = b and int(b.get("Language", b.get("LanguageID", 0)) or 0) or 0
                v += [male, female, int(n[f"BroadcastTextID{i}"] or 0), lang, float(n[f"Probability{i}"] or 0)] + [0] * 6
            v.append(0)
            nvals.append(v)
        self.sql.append(f"DELETE FROM `npc_text` WHERE `ID` IN ({in_list(n['ID'] for n in npc)});")
        self.sql += insert("npc_text", ntc, nvals)

        if bts:
            have = {r["ID"] for r in rows(self.ac, f"SELECT ID FROM broadcast_text WHERE ID IN ({in_list(bts)})")}
            new = [b for i, b in bts.items() if i not in have]
            sample = next(iter(bts.values()))
            self.report["broadcast_text columns (tdb6)"] = list(sample.keys())
            self.sql += insert("broadcast_text", ["ID", "LanguageID", "MaleText", "FemaleText", "EmoteID1", "EmoteID2", "EmoteID3", "EmoteDelay1",
                                                  "EmoteDelay2", "EmoteDelay3", "SoundEntriesId", "EmotesID", "Flags", "VerifiedBuild"],
                               [[b["ID"], int(b.get("Language", 0) or 0), b.get("MaleText") or "", b.get("FemaleText") or "",
                                 int(b.get("EmoteID1", 0) or 0), int(b.get("EmoteID2", 0) or 0), int(b.get("EmoteID3", 0) or 0),
                                 int(b.get("EmoteDelay1", 0) or 0), int(b.get("EmoteDelay2", 0) or 0), int(b.get("EmoteDelay3", 0) or 0),
                                 0, 0, 0, 0] for b in new])
            locale_rows = [[l["ID"], l["locale"], l.get("MaleText_lang") or "", l.get("FemaleText_lang") or "", 0] for l in locs if l["ID"] not in have]
            if locale_rows:
                self.sql += insert("broadcast_text_locale", ["ID", "locale", "MaleText", "FemaleText", "VerifiedBuild"], locale_rows)

        conds = rows(self.tdb, f"SELECT * FROM conditions WHERE (SourceTypeOrReferenceId IN (14,15) AND SourceGroup IN ({in_list(all_menus)})) "
                               f"OR (SourceTypeOrReferenceId=22 AND SourceEntry IN ({in_list(entries | g_entries)}))")
        if conds:
            cc = list(conds[0].keys())
            for c in conds:
                self.sql.append(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId`={c['SourceTypeOrReferenceId']} AND `SourceGroup`={c['SourceGroup']} "
                                f"AND `SourceEntry`={c['SourceEntry']} AND `SourceId`={c['SourceId']} AND `ElseGroup`={c['ElseGroup']} "
                                f"AND `ConditionTypeOrReference`={c['ConditionTypeOrReference']} AND `ConditionValue1`={c['ConditionValue1']};")
            self.sql += insert("conditions", cc, [[c[k] for k in cc] for c in conds])

    # ---------------------------------------------------------------- DBC
    def dbc_rows(self):
        go_fdids = {int(self.godi[r]["FileDataID"]) for r in self.go_display}
        ext = listfile_ext(go_fdids)
        cmd_rows, cdi_rows, godi_rows = [], [], []
        mf, ms, mtaken, mblob = self.srv_cmd
        donor = next(iter(mtaken.values()))
        for retail, local in sorted(self.creature_model.items()):
            if local in mtaken:
                continue
            r = self.cmd[retail]
            cmd_rows.append((local, f"retail\\{r['FileDataID']}.m2", donor, r))
        for retail, local in sorted(self.creature_display.items()):
            if local in self.srv_cdi[2]:
                continue
            cdi_rows.append((local, retail))
        for retail, local in sorted(self.go_display.items()):
            if local in self.srv_godi[2]:
                continue
            r = self.godi[retail]
            fdid = int(r["FileDataID"])
            godi_rows.append((local, f"retail\\{fdid}.{ 'wmo' if ext.get(fdid) == 'wmo' else 'm2'}", r))
        return cmd_rows, cdi_rows, godi_rows

    def patch_dbc(self, model_dbc: bytes, display_dbc: bytes, go_dbc: bytes, cmd_rows, cdi_rows, godi_rows):
        mf, ms, mrows, mblob = read_wdbc(model_dbc)
        df, ds, drows, dblob = read_wdbc(display_dbc)
        gf, gs, grows, gblob = read_wdbc(go_dbc)
        mtaken = {struct.unpack_from("<I", r)[0] for r in mrows}
        dtaken = {struct.unpack_from("<I", r)[0] for r in drows}
        gtaken = {struct.unpack_from("<I", r)[0] for r in grows}
        for local, path, donor, r in cmd_rows:
            if local in mtaken:
                continue
            row = bytearray(donor)
            struct.pack_into("<I", row, 0, local)
            struct.pack_into("<I", row, 8, append_string(mblob, path))
            struct.pack_into("<I", row, 12, int(r["SizeClass"] or 0))
            struct.pack_into("<I", row, 16, f32(float(r["ModelScale"] or 1.0)))
            struct.pack_into("<2I", row, 56, f32(float(r["CollisionWidth"] or 0.5)), f32(float(r["CollisionHeight"] or 1.0)))
            struct.pack_into("<I", row, 64, f32(float(r["MountHeight"] or 0)))
            struct.pack_into("<6I", row, 68, *[f32(float(r[f"GeoBox_{i}"] or 0)) for i in range(6)])
            mrows.append(bytes(row))
            mtaken.add(local)
        for local, retail in cdi_rows:
            if local in dtaken:
                continue
            r = self.cdi[retail]
            model_local = self.creature_model.get(int(r["ModelID"]), 0)
            texs = [append_string(dblob, f"{r[f'TextureVariationFileDataID_{i}']}.blp") if int(r[f"TextureVariationFileDataID_{i}"] or 0) else 0 for i in range(3)]
            extra = (0x80000000 | retail) if int(r["ExtendedDisplayInfoID"] or 0) else 0
            row = bytearray(ds)
            # ID, ModelID, SoundID, ExtendedDisplayInfoID, CreatureModelScale, CreatureModelAlpha
            struct.pack_into("<6I", row, 0, local, model_local, 0, extra, f32(float(r["CreatureModelScale"] or 1.0)), int(r["CreatureModelAlpha"] or 255))
            struct.pack_into("<3I", row, 24, *texs)
            drows.append(bytes(row))
            dtaken.add(local)
        for local, path, r in godi_rows:
            if local in gtaken:
                continue
            geo = [float(r[f"GeoBox_{i}"] or 0) for i in range(6)]
            grows.append(struct.pack("<2I10I6fI", local, append_string(gblob, path), *([0] * 10), *geo, 0))
            gtaken.add(local)
        return write_wdbc(mf, ms, mrows, mblob), write_wdbc(df, ds, drows, dblob), write_wdbc(gf, gs, grows, gblob)

    def write_dbc(self):
        cmd_rows, cdi_rows, godi_rows = self.dbc_rows()
        for d in SERVER_DBC_DIRS:
            if not d.exists():
                continue
            for name in ("CreatureModelData.dbc", "CreatureDisplayInfo.dbc", "GameObjectDisplayInfo.dbc"):
                bak = d / f"{name}.pre_uwow_port"
                if not bak.exists():
                    bak.write_bytes((d / name).read_bytes())
            m, c, g = self.patch_dbc((d / "CreatureModelData.dbc").read_bytes(), (d / "CreatureDisplayInfo.dbc").read_bytes(),
                                     (d / "GameObjectDisplayInfo.dbc").read_bytes(), cmd_rows, cdi_rows, godi_rows)
            (d / "CreatureModelData.dbc").write_bytes(m)
            (d / "CreatureDisplayInfo.dbc").write_bytes(c)
            (d / "GameObjectDisplayInfo.dbc").write_bytes(g)
            print(f"server dbc {d}: +{len(cmd_rows)} models, +{len(cdi_rows)} creature displays, +{len(godi_rows)} object displays")

        storm = Storm(STORMLIB)
        own = CLIENT / "Data" / PATCH_NAME
        pending = Path(str(own) + ".new")
        source = pending if pending.exists() else own
        files: dict[str, bytes] = {}
        handle = storm.open_archive(source)
        try:
            for name in (MAP_DBC, GO_DISPLAY_DBC, CREATURE_DISPLAY_DBC, CREATURE_MODEL_DBC):
                try:
                    files[name] = storm.read(handle, name)
                except OSError:
                    pass
        finally:
            storm.dll.SFileCloseArchive(handle)
        srv = SERVER_DBC_DIRS[0]
        for name, fallback in ((GO_DISPLAY_DBC, "GameObjectDisplayInfo.dbc.pre_uwow_port"), (CREATURE_DISPLAY_DBC, "CreatureDisplayInfo.dbc.pre_uwow_port"),
                               (CREATURE_MODEL_DBC, "CreatureModelData.dbc.pre_uwow_port")):
            files.setdefault(name, (srv / fallback).read_bytes())
        m, c, g = self.patch_dbc(files[CREATURE_MODEL_DBC], files[CREATURE_DISPLAY_DBC], files[GO_DISPLAY_DBC], cmd_rows, cdi_rows, godi_rows)
        files[CREATURE_MODEL_DBC], files[CREATURE_DISPLAY_DBC], files[GO_DISPLAY_DBC] = m, c, g
        if pending.exists():
            pending.unlink()
        storm.create_archive(pending, files)
        try:
            if own.exists():
                own.unlink()
            pending.replace(own)
            print("wrote", own)
        except OSError as err:
            print(f"wrote {pending} (swap later, {own.name} is locked: {err})")

    def run(self):
        self.select()
        self.cleanup()
        self.creature_templates()
        self.gameobject_templates()
        self.spawns()
        self.garrison_tables()
        self.texts_and_scripts()
        OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
        OUT_SQL.write_text("\n".join(self.sql) + "\n", encoding="utf-8", newline="\n")
        MAP_JSON.write_text(json.dumps({"creature_display": self.creature_display, "creature_model": self.creature_model,
                                        "go_display": self.go_display}, indent=1), encoding="utf-8")
        print(f"wrote {OUT_SQL}: {len(self.ct)} creature templates, {len(self.gt)} object templates, "
              f"{len(self.c_spawns)} creature + {len(self.g_spawns)} object spawns, {len(self.b_creatures)}+{len(self.b_objects)} building spawns")
        print(f"displays: {len(self.creature_display)} creature ({sum(1 for k, v in self.creature_display.items() if k != v)} remapped), "
              f"{len(self.go_display)} object ({sum(1 for k, v in self.go_display.items() if k != v)} remapped)")
        for k, v in self.report.items():
            print(f"-- {k}: {len(v)}  {v[:12]}")
        if "--dbc" in sys.argv:
            self.write_dbc()


if __name__ == "__main__":
    World().run()
