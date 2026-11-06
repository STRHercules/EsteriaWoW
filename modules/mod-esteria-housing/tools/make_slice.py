"""Generate the Phase 1 slice data from one list: the world SQL (catalog, GameObject templates, display rows, steward,
room template, map 35 overrides) and the dev client patch that carries the same 20 GameObjectDisplayInfo rows.

    python make_slice.py --map-dbc Map.dbc --client "G:/3.3.5a - Dev" --out <staging dir>

Map.dbc is the server's copy (docker cp ac-worldserver:/azerothcore/env/dist/data/dbc/Map.dbc). The client's winning
GameObjectDisplayInfo.dbc is read from the highest patch MPQ that holds it and written, with the 20 rows appended, to
<out>/Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZHousingDev.MPQ (sorts above Patch-ZZZZZZZZZZZZZZZZZZZZZZZZCoA.MPQ). Nothing is
installed. Every decor model is retail-origin: dev only (docs/housing/README.md).
"""
import argparse
import csv
import math
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
STORMLIB = Path(r"R:\Users\Zach\Documents\GitHub\wowdecomp\Tools\MountStudio\runtime\backend\StormLib.dll")
PATCH_NAME = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZHousingDev.MPQ"
DBC_NAME = r"DBFilesClient\GameObjectDisplayInfo.dbc"
MAP_DBC_NAME = r"DBFilesClient\Map.dbc"

DISPLAY_BASE, GO_BASE, STEWARD = 60000, 9500000, 9500100
STEWARD_MODEL_FROM = 6740  # copy the Stormwind innkeeper's display
# Retail housing maps (docs/housing/maps-recon.md). Rows are cloned from map 35's in Map.dbc and given the retail
# directory, so World\Maps\<id>\<id>.wdt resolves through Data/Retail aliases to the retail WDT (RetailTerrain.cpp).
TEMPLATE_MAP = 35
HOUSE_MAP, NEIGHBORHOOD_MAP = 2783, 2735
MAPS = {  # id: directory, name, InstanceType (1 party: one copy per house; 0 world), MaxPlayers
    HOUSE_MAP: ("2783", "Home Interior", 1, 40),
    NEIGHBORHOOD_MAP: ("2735", "Founder's Point", 0, 0),
}
MAP_FDIDS = {HOUSE_MAP: 5890928, NEIGHBORHOOD_MAP: 5660542}  # Map.db2 WdtFileDataID
# NeighborhoodMap 1 (Founder's Point): entry position and facing; the steward stands there.
NEIGHBORHOOD_ENTRY = (3807.76, -160.427, 194.111, 2.852)

# Retail room kit: 12 generic HouseRoom kinds and their RoomComponent pieces (data/room_kit.tsv, written by wowdecomp
# docs/housing/tools/phase3/make_kit.py). Each distinct WMO becomes a GameObjectDisplayInfo row retail\<fdid>.wmo and a
# type-14 gameobject_template; the module lays rooms out from the template origin (HousingRooms.h).
# NeighborhoodMap 7 puts Home Interior's entry at (-1000, -1000, 0.1): rooms stand on z 0, 2 yd above its flat terrain.
ROOM_ORIGIN = (-1000.0, -1000.0, 0.0)
ROOM_DISPLAY_BASE, ROOM_GO_BASE, ROOM_SLOTS = DISPLAY_BASE + 200, GO_BASE + 200, 600
KIT = list(csv.DictReader((MODULE / "data/room_kit.tsv").open(encoding="utf-8"), delimiter="\t"))
# The same pieces in retail's other mesh themes (make_kit.py's second output); rooms pick one per walls/floor/ceiling.
KIT_THEMES = list(csv.DictReader((MODULE / "data/room_kit_themes.tsv").open(encoding="utf-8"), delimiter="\t"))
THEME_NAMES = {1: "Folk", 2: "Rugged", 3: "Generic", 4: "Bel'ameth", 5: "Silvermoon"}  # HouseTheme.Name_lang
MODEL_COLUMNS = ("solid", "door", "wide", "door_frame", "wide_frame")
# Every staircase variant in every theme (make_kit.py's third output); the module picks one by what is above and below.
KIT_STAIRS = list(csv.DictReader((MODULE / "data/room_kit_stairs.tsv").open(encoding="utf-8"), delimiter="\t"))
# An early Human-style stairwell wall no RoomComponent uses (12ph_room_w_staircase_s / _door_s / _threshold_s, 23 x 12 yd
# like the stairwell walls): offered as a wall style that only stairwells have.
HUMAN_STAIRWELL_THEME, HUMAN_STAIRWELL = 100, {"solid": 5562205, "door": 5562206, "door_frame": 5562207}
THEME_NAMES[HUMAN_STAIRWELL_THEME] = "Human (stairwells)"
STAIRWELL_KINDS = {"10", "50", "48"}
for r in KIT:
    if r["kind"] in STAIRWELL_KINDS and r["type"] == "1":
        socket = r["door"] != "0"
        KIT_THEMES.append({"kind": r["kind"], "piece": r["piece"], "theme": str(HUMAN_STAIRWELL_THEME),
                           "solid": str(HUMAN_STAIRWELL["solid"]), "door": str(HUMAN_STAIRWELL["door"]) if socket else "0",
                           "wide": "0", "door_frame": str(HUMAN_STAIRWELL["door_frame"]) if socket else "0", "wide_frame": "0"})
ROOM_MODELS = sorted({int(r[k]) for r in KIT + KIT_THEMES for k in MODEL_COLUMNS if r[k] != "0"}
                     | {int(r["fdid"]) for r in KIT_STAIRS})
assert len(ROOM_MODELS) <= ROOM_SLOTS, f"{len(ROOM_MODELS)} room models, {ROOM_SLOTS} display slots"
ENTRY = (ROOM_ORIGIN[0], ROOM_ORIGIN[1], ROOM_ORIGIN[2] + 0.5, 0.0)

# Founder's Point plots and the default small Human House (data/plots.tsv, data/exterior.tsv from wowdecomp
# docs/housing/tools/phase3/make_plots.py). Each plot gets a permanent cornerstone (retail 12ph_plotsalesign01, a
# clickable GameObject the module scripts); a claimed plot's exterior pieces are type-14 GameObjects the module saves.
PLOTS = list(csv.DictReader((MODULE / "data/plots.tsv").open(encoding="utf-8"), delimiter="\t"))
EXTERIOR = list(csv.DictReader((MODULE / "data/exterior.tsv").open(encoding="utf-8"), delimiter="\t"))
EXTERIOR_MODELS = sorted({int(r["fdid"]) for r in EXTERIOR})
CORNERSTONE_FDID = 6935310  # GameObjects 527268 "Cornerstone - Plot 0" -> GameObjectDisplayInfo 110660
EXTERIOR_DISPLAY_BASE, EXTERIOR_GO_BASE = DISPLAY_BASE + 100, GO_BASE + 150
CORNERSTONE_DISPLAY, CORNERSTONE_GO = EXTERIOR_DISPLAY_BASE + 99, EXTERIOR_GO_BASE + 49
FRONT_DOOR_DISPLAY, FRONT_DOOR_GO = EXTERIOR_DISPLAY_BASE + 98, EXTERIOR_GO_BASE + 48
CORNERSTONE_GUID_BASE = 9500000  # gameobject guids 9500000 + plot; checked free in acore_world (max 5.7M)
# The template's min_z is the floor the module builds rooms on (RoomTemplate::Origin); x/y bounds are per room now.
BOUNDS_HALF = (11.0, 11.0)
BOUNDS_Z = (-0.5, 11.0)
MAX_DECOR = 200

CATEGORY = {"Misc": 0, "Furniture": 1, "Accents": 2, "Lighting": 3, "Nature": 4, "Structural": 5}
SURFACE = {"floor": 0, "wall": 1, "ceiling": 2, "on-decor": 3}
# The clickable front door on a bought plot: an M2 on the porch, since 3.3.5 cannot click a WMO GameObject (only types
# 11/14/15/33/35 draw WMOs, and none of them can be used). Retail 12ph_general_doormat01.
FRONT_DOOR_FDID = 7506135

# decor_id, model FileDataID, name, category, surface. Each FDID passed RetailAssetProbe on 2026-11-05
# (docs/housing/README.md lists the three swaps).
SLICE = [
    (498, 6375820, "Folk Rug", "Furniture", "floor"),
    (1044, 6390440, "Folk Round Rug", "Furniture", "floor"),
    (496, 6373543, "Folk Table", "Furniture", "floor"),
    (497, 6373544, "Folk Long Table", "Furniture", "floor"),
    (494, 6372825, "Folk Chair", "Furniture", "floor"),
    (1991, 6390428, "Folk Stool", "Furniture", "floor"),
    (495, 6373411, "Folk Bed", "Furniture", "floor"),
    (373, 6008928, "Folk Tall Shelf", "Furniture", "floor"),
    (374, 6008929, "Folk Wall Shelf", "Furniture", "wall"),
    (390, 6046867, "Folk Bookcase", "Accents", "floor"),
    (379, 6008935, "Folk Food Plate", "Accents", "on-decor"),
    (1123, 6390444, "Folk Barrel", "Accents", "floor"),
    (12215, 7338177, "Folk Crate", "Accents", "floor"),
    (383, 6008939, "Folk Standing Lamp", "Lighting", "floor"),
    (15287, 7338170, "Folk Wall Lamp", "Lighting", "wall"),
    (377, 6008933, "Folk Chandelier", "Lighting", "ceiling"),
    (81, 6033664, "Rugged Fireplace", "Lighting", "floor"),
    (388, 6008944, "Folk Wall Decor", "Structural", "wall"),
    (520, 6383338, "Folk Rose Pot", "Nature", "on-decor"),
    (1701, 6390442, "Folk Pillow", "Misc", "floor"),
    # Newer than the Phase 0 inventory; both load from the CDN (RetailAssetProbe, 2026-11-06).
    (23709, 7834756, "Modular Stair Segment", "Structural", "floor"),
    (23710, 7834757, "Modular Spiral Stair Segment", "Structural", "floor"),
]

# The rest of the retail player-housing catalog: every 12ph M2 the Phase 0 inventory checked loads ("ok"), named from
# its file (12ph_folk_tallshelf01.m2 -> "Folk Tallshelf"). Retail doors (..._door01, ..._frontdoor01) become exits.
INVENTORY = Path(r"R:\Users\Zach\Documents\GitHub\wowdecomp\docs\housing\existing-assets.tsv")
DECOR_DISPLAY_BASE, DECOR_GO_BASE, DECOR_SLOTS = 61000, 9501000, 1000
EXIT_DOOR = re.compile(r"_(front)?door\d+\.m2$")


def decor_name(path):
    stem = re.sub(r"\d+$", "", path.rsplit("\\", 1)[-1][:-3]).removeprefix("12ph_")
    return " ".join(w.capitalize() for w in stem.split("_") if w)


def surface_of(name):
    lower = name.lower()
    if "wall" in lower or "painting" in lower or "banner" in lower:
        return "wall"
    if "chandelier" in lower or "ceiling" in lower or "hanging" in lower:
        return "ceiling"
    return "floor"


def catalog():
    out, seen_decor, seen_fdid, names = list(SLICE), {r[0] for r in SLICE}, {r[1] for r in SLICE}, {r[2] for r in SLICE}
    for r in csv.DictReader(INVENTORY.open(encoding="utf-8"), delimiter="\t"):
        decor, fdid = int(r["decor_id"]), int(r["model_fdid"])
        if r["status"] != "ok" or r["ext"] != "m2" or "playerhousing" not in r["model_path"]:
            continue
        if decor in seen_decor or fdid in seen_fdid:
            continue
        name = decor_name(r["model_path"])
        base, n = name, 2
        while name in names:
            name, n = f"{base} {n}", n + 1
        out.append((decor, fdid, name, r["category"] if r["category"] in CATEGORY else "Misc", surface_of(name)))
        seen_decor.add(decor); seen_fdid.add(fdid); names.add(name)
    return out


def is_exit(fdid):
    return any(EXIT_DOOR.search(r["model_path"]) for r in INVENTORY_ROWS if int(r["model_fdid"]) == fdid)


INVENTORY_ROWS = list(csv.DictReader(INVENTORY.open(encoding="utf-8"), delimiter="\t"))
CATALOG = catalog()
assert len(CATALOG) <= DECOR_SLOTS, f"{len(CATALOG)} decor, {DECOR_SLOTS} slots"


def q(text):
    return "'" + str(text).replace("\\", "\\\\").replace("'", "''") + "'"


def read_wdbc(data):
    assert data[:4] == b"WDBC", "not a WDBC file"
    count, fields, size, strings = struct.unpack_from("<4I", data, 4)
    rows = [data[20 + i * size:20 + (i + 1) * size] for i in range(count)]
    return fields, size, rows, data[20 + count * size:20 + count * size + strings]


MAP_TEXT = {1} | set(range(5, 21)) | set(range(23, 39)) | set(range(40, 56))
MAP_FLOATS = {58, 60, 61}


def map_rows(data):
    """The MAPS rows as 66 raw words each plus their new strings, cloned from TEMPLATE_MAP's row."""
    fields, size, rows, strings = read_wdbc(data)
    assert (fields, size) == (66, 264), f"Map.dbc layout {fields}x{size}, expected 66x264 (3.3.5a)"
    base = next((list(struct.unpack("<66I", r)) for r in rows if struct.unpack_from("<I", r)[0] == TEMPLATE_MAP), None)
    assert base, f"map {TEMPLATE_MAP} not in Map.dbc"
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    out = []
    for map_id, (directory, name, instance_type, max_players) in MAPS.items():
        assert map_id not in taken, f"map {map_id} already in Map.dbc"
        row = list(base)
        row[0], row[2], row[22], row[65] = map_id, instance_type, 0, max_players  # AreaTableID 0: no retail areas
        out.append((row, {1: directory, 5: name}))
    return strings, out


def map_sql_values(strings, row, texts):
    values = []
    for i, v in enumerate(row):
        if i in texts:
            values.append(q(texts[i]))
        elif i in MAP_TEXT:
            values.append(q(strings[v:strings.index(b"\0", v)].decode("utf-8")))
        elif i in MAP_FLOATS:
            values.append(repr(struct.unpack("<f", struct.pack("<I", v))[0]))
        else:
            values.append(str(struct.unpack("<i", struct.pack("<I", v))[0]))  # -1 for unset words
    return values


def world_sql(map_dbc):
    lo = tuple(round(v, 2) for v in (ENTRY[0] - BOUNDS_HALF[0], ENTRY[1] - BOUNDS_HALF[1], ENTRY[2] + BOUNDS_Z[0]))
    hi = tuple(round(v, 2) for v in (ENTRY[0] + BOUNDS_HALF[0], ENTRY[1] + BOUNDS_HALF[1], ENTRY[2] + BOUNDS_Z[1]))
    lines = [
        "-- Generated by modules/mod-esteria-housing/tools/make_slice.py. Do not edit; change SLICE and regenerate.",
        "-- Dev world DB only (housing_dev_world). Rollback: housing_world_rollback.sql.",
        "",
        (MODULE / "sql/world/housing_world_tables.sql").read_text(encoding="utf-8").strip(),
        "",
        f"DELETE FROM `housing_decor_catalog`;",
        f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {GO_BASE} AND {ROOM_GO_BASE + ROOM_SLOTS - 1};",
        f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {DISPLAY_BASE} AND {ROOM_DISPLAY_BASE + ROOM_SLOTS - 1};",
    ]
    lines += [f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {DECOR_GO_BASE} AND {DECOR_GO_BASE + DECOR_SLOTS - 1};",
              f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {DECOR_DISPLAY_BASE} AND {DECOR_DISPLAY_BASE + DECOR_SLOTS - 1};"]
    for i, (decor, fdid, name, category, surface) in enumerate(CATALOG):
        display, entry = DECOR_DISPLAY_BASE + i, DECOR_GO_BASE + i
        lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                     f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(f'retail\\{fdid}.m2')}, -1, -1, 0, 1, 1, 2);")
        if is_exit(fdid):  # type 10 (goober): clicking it runs the script's gossip hello, which leaves the house
            lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`) "
                         f"VALUES ({entry}, 10, {display}, {q(name + ' (exit)')}, 1, 'go_esteria_housing_exit');")
        else:
            lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                         f"VALUES ({entry}, 5, {display}, {q(name)}, 1);")
        lines.append(f"INSERT INTO `housing_decor_catalog` (`decor_id`, `model_fdid`, `display_id`, `gameobject_entry`, `name`, "
                     f"`category`, `surface`, `origin`, `enabled`) VALUES ({decor}, {fdid}, {display}, {entry}, {q(name)}, "
                     f"{CATEGORY[category]}, {SURFACE[surface]}, 'retail', 1);")
    lines += ["", "DELETE FROM `housing_room_kit`;", "DELETE FROM `housing_room_kind`;"]
    for i, fdid in enumerate(ROOM_MODELS):
        display, entry = ROOM_DISPLAY_BASE + i, ROOM_GO_BASE + i
        lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                     f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(f'retail\\{fdid}.wmo')}, -12, -12, 0, 12, 12, 11);")
        lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                     f"VALUES ({entry}, 14, {display}, {q(f'Room piece {fdid}')}, 1);")
    entry_of = {fdid: ROOM_GO_BASE + i for i, fdid in enumerate(ROOM_MODELS)}
    go = lambda fdid: entry_of.get(int(fdid), 0)  # noqa: E731 (0 = no such variant)
    for kind in sorted({(int(r["kind"]), r["name"], *(r[k] for k in ("min_x", "min_y", "min_z", "max_x", "max_y", "max_z")))
                        for r in KIT}):
        lines.append(f"INSERT INTO `housing_room_kind` VALUES ({kind[0]}, {q(kind[1])}, {', '.join(kind[2:])});")
    for theme, name in THEME_NAMES.items():
        lines.append(f"INSERT INTO `housing_room_theme` VALUES ({theme}, {q(name)});")
    for r in KIT_STAIRS:
        lines.append(f"INSERT INTO `housing_room_stairs` VALUES ({r['kind']}, {r['piece']}, {r['theme']}, {r['variant']}, "
                     f"{go(r['fdid'])});")
    for r in KIT_THEMES:
        lines.append(f"INSERT INTO `housing_room_kit_theme` VALUES ({r['kind']}, {r['piece']}, {r['theme']}, "
                     f"{', '.join(str(go(r[k])) for k in MODEL_COLUMNS)});")
    for r in KIT:
        lines.append(f"INSERT INTO `housing_room_kit` VALUES ({r['kind']}, {r['piece']}, {r['type']}, {r['x']}, {r['y']}, "
                     f"{r['z']}, {r['rot_deg']}, {go(r['solid'])}, {go(r['door'])}, {go(r['wide'])}, {r['width']}, "
                     f"{go(r['door_frame'])}, {go(r['wide_frame'])});")
    lines += [
        "",
        f"DELETE FROM `housing_room_template` WHERE `room_template_id` = 1;",
        f"INSERT INTO `housing_room_template` VALUES (1, {HOUSE_MAP}, {ENTRY[0]}, {ENTRY[1]}, {ENTRY[2]}, {ENTRY[3]}, "
        f"{lo[0]}, {lo[1]}, {lo[2]}, {hi[0]}, {hi[1]}, {hi[2]}, {MAX_DECOR}, 'Home Interior');",
        "",
        f"DELETE FROM `creature_template` WHERE `entry` = {STEWARD};",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` = {STEWARD};",
        f"INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, "
        f"`unit_class`, `unit_flags`, `type`, `ScriptName`) VALUES ({STEWARD}, 'Housing Steward', 'Esteria Housing', 80, 80, 35, 1, "
        f"1, 2, 7, 'npc_esteria_housing_steward');",
        f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) "
        f"SELECT {STEWARD}, 0, `CreatureDisplayID`, 1, 1 FROM `creature_template_model` WHERE `CreatureID` = {STEWARD_MODEL_FROM} AND `Idx` = 0;",
        "",
        f"-- Phases 1-3a borrowed map {TEMPLATE_MAP} (Stormwind Vault); stock acore_world has no rows for it.",
        f"DELETE FROM `instance_template` WHERE `map` = {TEMPLATE_MAP};",
        f"DELETE FROM `map_dbc` WHERE `ID` = {TEMPLATE_MAP};",
        "",
        "-- Retail housing maps; the client gets the same Map.dbc rows from the dev patch.",
        f"DELETE FROM `map_dbc` WHERE `ID` IN ({', '.join(map(str, MAPS))});",
    ]
    strings, rows = map_rows(map_dbc)
    for row, texts in rows:
        lines.append(f"INSERT INTO `map_dbc` VALUES ({', '.join(map_sql_values(strings, row, texts))});")
    lines += [
        f"DELETE FROM `instance_template` WHERE `map` = {HOUSE_MAP};",
        f"INSERT INTO `instance_template` (`map`, `parent`, `script`, `allowMount`) VALUES ({HOUSE_MAP}, 0, '', 0);",
        # MapMgr::PlayerCannotEnter refuses a party map with no MapDifficulty row; 40 players so visits never fill it.
        f"DELETE FROM `mapdifficulty_dbc` WHERE `ID` = {HOUSE_MAP};",
        f"INSERT INTO `mapdifficulty_dbc` (`ID`, `MapID`, `Difficulty`, `Message_Lang_Mask`, `RaidDuration`, `MaxPlayers`) "
        f"VALUES ({HOUSE_MAP}, {HOUSE_MAP}, 0, 16712188, 0, {MAPS[HOUSE_MAP][3]});",
        "",
        "-- Plots: a cornerstone on each, and the exterior recipe the module builds a claimed plot's house from.",
        "DELETE FROM `housing_plot`;",
        "DELETE FROM `housing_exterior_piece`;",
        # Only the cornerstones: saved house exteriors get guids from the same counter, right after them.
        f"DELETE FROM `gameobject` WHERE `id` = {CORNERSTONE_GO};",
        f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, "
        f"`GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({CORNERSTONE_DISPLAY}, {q(f'retail\\{CORNERSTONE_FDID}.m2')}, -1, -1, 0, 1, 1, 3);",
        # Type 2 (questgiver) with no quests: using it opens the script's gossip, as stock signposts and books do.
        f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`) VALUES "
        f"({CORNERSTONE_GO}, 2, {CORNERSTONE_DISPLAY}, 'Cornerstone', 1, 'go_esteria_housing_cornerstone');",
    ]
    for i, fdid in enumerate(EXTERIOR_MODELS):
        display, entry = EXTERIOR_DISPLAY_BASE + i, EXTERIOR_GO_BASE + i
        lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                     f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(f'retail\\{fdid}.wmo')}, -12, -12, 0, 12, 12, 15);")
        lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                     f"VALUES ({entry}, 14, {display}, {q(f'House piece {fdid}')}, 1);")
    lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                 f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({FRONT_DOOR_DISPLAY}, {q(f'retail\\{FRONT_DOOR_FDID}.m2')}, "
                 f"-1, -1, 0, 1, 1, 1);")
    lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`) VALUES "
                 f"({FRONT_DOOR_GO}, 10, {FRONT_DOOR_DISPLAY}, 'Front Door', 1, 'go_esteria_housing_front_door');")
    lines.append(f"INSERT INTO `housing_exterior_piece` (`role`, `gameobject_entry`, `pos_x`, `pos_y`, `pos_z`, `rot_deg`) "
                 f"VALUES ('front_door', {FRONT_DOOR_GO}, 0, 0, 0, 0);")
    for r in EXTERIOR:
        lines.append(f"INSERT INTO `housing_exterior_piece` (`role`, `gameobject_entry`, `pos_x`, `pos_y`, `pos_z`, `rot_deg`) "
                     f"VALUES ({q(r['role'])}, {EXTERIOR_GO_BASE + EXTERIOR_MODELS.index(int(r['fdid']))}, {r['x']}, {r['y']}, "
                     f"{r['z']}, {r['rot_deg']});")
    for p in PLOTS:
        lines.append(f"INSERT INTO `housing_plot` VALUES ({NEIGHBORHOOD_MAP}, {p['plot']}, {p['house_x']}, {p['house_y']}, "
                     f"{p['house_z']}, {p['house_yaw']}, {p['corner_x']}, {p['corner_y']}, {p['corner_z']}, {p['corner_o']}, "
                     f"{p['exit_x']}, {p['exit_y']}, {p['exit_z']});")
        # The retail sign model faces its -x: facing the street takes CornerstoneRotation turned half way round.
        o = (float(p["corner_o"]) + math.pi) % (2 * math.pi)
        lines.append(f"INSERT INTO `gameobject` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, "
                     f"`position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, "
                     f"`animprogress`, `state`) VALUES ({CORNERSTONE_GUID_BASE + int(p['plot'])}, {CORNERSTONE_GO}, "
                     f"{NEIGHBORHOOD_MAP}, 1, 1, {p['corner_x']}, {p['corner_y']}, {p['corner_z']}, {o}, 0, 0, "
                     f"{round(math.sin(o / 2), 6)}, {round(math.cos(o / 2), 6)}, 0, 100, 1);")
    lines += [
        "",
        f"-- A steward at Founder's Point's entry takes players home.",
        f"DELETE FROM `creature` WHERE `guid` = {STEWARD};",
        f"INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, "
        f"`orientation`, `spawntimesecs`) VALUES ({STEWARD}, {STEWARD}, {NEIGHBORHOOD_MAP}, 1, 1, "
        f"{', '.join(map(str, NEIGHBORHOOD_ENTRY))}, 300);",
        "",
    ]
    return "\n".join(lines)


def winning_dbc(storm, client, name):
    """The copy of a DBC the client loads, not counting ours: PatchFiles sorts Data\\patch-*.MPQ and
    Data\\enUS\\patch-enUS-*.MPQ by full path, case-insensitive, and the highest path gets the highest priority
    (wowdecomp WoW/Source/WowServices/PatchFiles.cpp, Client.cpp:1393), so every Data\\Patch-* beats every locale patch."""
    data_dir = Path(client) / "Data"
    found = [(f"data\\{p.name.lower()}", p) for p in data_dir.glob("*") if p.name.lower().startswith("patch-")]
    found += [(f"data\\enus\\{p.name.lower()}", p) for p in (data_dir / "enUS").glob("*")
              if p.name.lower().startswith("patch-enus-")]
    archives = [p for _, p in sorted(found, reverse=True) if p.suffix.lower() == ".mpq"]
    for archive in archives:
        if archive.name.lower() == PATCH_NAME.lower():
            continue  # never build on our own earlier output
        handle = storm.open_archive(archive)
        try:
            return archive, storm.read(handle, name)
        except OSError:
            continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    raise SystemExit("no patch MPQ holds " + name)


def patch_map_dbc(original):
    fields, size, rows, strings = read_wdbc(original)
    strings, new = map_rows(original)
    strings = bytearray(strings)
    for row, texts in new:
        for i, text in texts.items():
            row[i] = len(strings)
            strings += text.encode("utf-8") + b"\0"
        rows.append(struct.pack("<66I", *row))
    return b"WDBC" + struct.pack("<4I", len(rows), fields, size, len(strings)) + b"".join(rows) + bytes(strings)


def patch_dbc(storm, client):
    archive, original = winning_dbc(storm, client, DBC_NAME)
    fields, size, rows, strings = read_wdbc(original)
    assert (fields, size) == (19, 76), f"GameObjectDisplayInfo.dbc layout {fields}x{size}, expected 19x76"
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    strings = bytearray(strings)
    added = []
    models = [(DECOR_DISPLAY_BASE + i, f"retail\\{fdid}.m2", (-1, -1, 0, 1, 1, 2)) for i, (_, fdid, *_rest) in enumerate(CATALOG)]
    models += [(ROOM_DISPLAY_BASE + i, f"retail\\{fdid}.wmo", (-12, -12, 0, 12, 12, 11)) for i, fdid in enumerate(ROOM_MODELS)]
    models += [(EXTERIOR_DISPLAY_BASE + i, f"retail\\{fdid}.wmo", (-12, -12, 0, 12, 12, 15)) for i, fdid in enumerate(EXTERIOR_MODELS)]
    models.append((CORNERSTONE_DISPLAY, f"retail\\{CORNERSTONE_FDID}.m2", (-1, -1, 0, 1, 1, 3)))
    models.append((FRONT_DOOR_DISPLAY, f"retail\\{FRONT_DOOR_FDID}.m2", (-1, -1, 0, 1, 1, 1)))
    for display, name, box in models:
        assert display not in taken, f"display {display} already used in {archive.name}"
        offset = len(strings)
        strings += name.encode("ascii") + b"\0"
        added.append(struct.pack("<2I10I6fI", display, offset, *([0] * 10), *box, 0))
    rows += added
    out = b"WDBC" + struct.pack("<4I", len(rows), fields, size, len(strings)) + b"".join(rows) + bytes(strings)
    return archive, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-dbc", required=True)
    parser.add_argument("--client", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sql = MODULE / "sql/world/housing_world.sql"
    sql.write_text(world_sql(Path(args.map_dbc).read_bytes()), encoding="utf-8", newline="\n")
    print("wrote", sql)

    sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))
    from cars_mount_pack import Storm
    storm = Storm(STORMLIB)
    source, dbc = patch_dbc(storm, args.client)
    map_source, map_original = winning_dbc(storm, args.client, MAP_DBC_NAME)
    files = {DBC_NAME: dbc, MAP_DBC_NAME: patch_map_dbc(map_original)}
    target = out / PATCH_NAME
    if target.exists():
        target.unlink()
    storm.create_archive(target, files)
    handle = storm.open_archive(target)
    try:
        for name, data in files.items():
            assert storm.read(handle, name) == data, f"read-back mismatch: {name}"
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"wrote {target} ({len(CATALOG) + len(ROOM_MODELS) + len(EXTERIOR_MODELS) + 2} display rows on top of {source.name}; "
          f"maps {', '.join(map(str, MAPS))} on top of {map_source.name}'s Map.dbc)")
    # The client finds each map's WDT through these aliases (Data/Retail/RetailCasc.ini aliases=).
    for map_id, fdid in MAP_FDIDS.items():
        print(f"alias: {fdid};World\\Maps\\{MAPS[map_id][0]}\\{MAPS[map_id][0]}.wdt")


if __name__ == "__main__":
    main()
