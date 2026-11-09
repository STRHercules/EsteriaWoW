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
HOUSE_MAP, NEIGHBORHOOD_MAP, RAZORWIND_MAP = 2783, 2735, 2736
# Every map is a party instance (InstanceType 1): one copy per house, and one per neighborhood (an account's or a
# guild's; the module picks the instance), so 40 players never fill one.
MAPS = {  # id: directory, name, InstanceType, MaxPlayers
    HOUSE_MAP: ("2783", "Home Interior", 1, 40),
    NEIGHBORHOOD_MAP: ("2735", "Founder's Point", 1, 40),
    RAZORWIND_MAP: ("2736", "Razorwind Shores", 1, 40),
}
NEIGHBORHOOD_MAPS = (NEIGHBORHOOD_MAP, RAZORWIND_MAP)
MAP_FDIDS = {HOUSE_MAP: 5890928, NEIGHBORHOOD_MAP: 5660542, RAZORWIND_MAP: 5660543}  # Map.db2 WdtFileDataID
# The world map: an AreaTable row naming each map (16105 is retail's Founder's Point) and an orphan WorldMapArea for it,
# which 3.3.5 shows on any map that is not a continent (as for battlegrounds). Both use retail's painted Founder's
# Point map (UiMap 2401, data/worldmap from wowdecomp docs/housing/tools/ui/make_worldmap.py), whose world bounds are
# UiMapAssignment's region; inside a house the player lies outside them, so the map shows without an arrow.
AREAS = {NEIGHBORHOOD_MAP: (16105, "Founder's Point"), HOUSE_MAP: (16300, "Home Interior"),
         RAZORWIND_MAP: (15524, "Razorwind Shores")}  # retail AreaTable IDs
AREA_TEMPLATE = 12  # Elwynn Forest: flags, ambience and music
# Founder's Point's subzones (retail AreaTable, ParentAreaID 16105). The client keeps a terrain chunk's retail area ID
# when AreaTable has it (wowdecomp RetailTerrain), so these name the minimap's zone text.
SUBZONES = {16376: "Brumewood Hollow", 16377: "Gilded Oaks", 16378: "The Outer Banks", 16588: "Town Center",
            16700: "Faldir's Torch", 16701: "Morgan's Rest", 16704: "Breakwater Bight", 16709: "Crescent Cove",
            16818: "Stoneveil Ridge"}
# Razorwind Shores' (ParentAreaID 15524; DurotarMain_Housing is retail's own placeholder name, left out).
RAZORWIND_SUBZONES = {16226: "Cragthorn Highlands", 16228: "Runetotem's Bounty", 16229: "Saltfang Shoals",
                      16589: "The Common", 16687: "Four Sisters", 16688: "Ragewater Springs", 16690: "Scorchsong Isle",
                      16753: "The Bloom"}
SUBZONES_OF = {NEIGHBORHOOD_MAP: SUBZONES, RAZORWIND_MAP: RAZORWIND_SUBZONES}
SUBZONE_TEMPLATE = 87  # Goldshire: a subzone's sounds
# Exploration bits under 4096 (the server's PLAYER_EXPLORED_ZONES holds 128 x 32 and logs any bit past it), free in the
# client's AreaTable, the server's AreaTable.dbc and acore_world.areatable_dbc (checked 2026-11-07).
AREA_BITS = {16105: 4095, 16300: 4094, **{area: 4093 - i for i, area in enumerate(SUBZONES)},
             15524: 4083, **{area: 4082 - i for i, area in enumerate(RAZORWIND_SUBZONES)}}
SANCTUARY, REST_HORDE, REST_ALLIANCE = 0x800, 0x400000, 0x800000
# Founder's Point is a sanctuary; a house is one too and rests whoever is inside, as retail's do.
AREA_FLAGS = {NEIGHBORHOOD_MAP: SANCTUARY, RAZORWIND_MAP: SANCTUARY, HOUSE_MAP: SANCTUARY | REST_HORDE | REST_ALLIANCE}
# Each map's world map: its tiles (data/worldmap/<name>) and bounds, left (max y), right (min y), top (max x), bottom
# (min x). Razorwind Shores is UiMap 2402 (Horde Housing District, art 2057) over UiMapAssignment's region for 2736.
WORLD_MAPS = {NEIGHBORHOOD_MAP: ("FoundersPoint", (2935.42, -2454.17, 4762.5, 1168.75)),
              HOUSE_MAP: ("FoundersPoint", (2935.42, -2454.17, 4762.5, 1168.75)),
              RAZORWIND_MAP: ("RazorwindShores", (3870.83, -2956.25, 4339.58, -212.5))}
AREA_DBC_NAME, WORLD_MAP_DBC_NAME = r"DBFilesClient\AreaTable.dbc", r"DBFilesClient\WorldMapArea.dbc"
# Retail's loading screens (LoadingScreens.MainImageFileDataID 7377860 and 7367528, data/loadscreens from wowdecomp
# docs/housing/tools/ui/make_loadscreen.py): Map.dbc's LoadingScreenID names a LoadingScreens row, whose file has a Wide
# twin for widescreen.
LOADING_SCREENS = {NEIGHBORHOOD_MAP: (900, "FoundersPoint", "LoadScreenFoundersPoint"),
                   HOUSE_MAP: (901, "HomeInterior", "LoadScreenHomeInterior"),
                   RAZORWIND_MAP: (902, "RazorwindShores", "LoadScreenRazorwindShores")}  # retail 672, 7490877
LOADING_DBC_NAME = r"DBFilesClient\LoadingScreens.dbc"
# NeighborhoodMap 1 (Founder's Point): entry position and facing; the steward stands there.
NEIGHBORHOOD_ENTRY = (3807.76, -160.427, 194.111, 2.852)
ENTRIES = {NEIGHBORHOOD_MAP: NEIGHBORHOOD_ENTRY, RAZORWIND_MAP: (2053.6, 175.468, 175.12, 3.4558)}  # NeighborhoodMap 2: 198 deg

# Retail room kit: 12 generic HouseRoom kinds and their RoomComponent pieces (data/room_kit.tsv, written by wowdecomp
# docs/housing/tools/phase3/make_kit.py). Each distinct WMO becomes a GameObjectDisplayInfo row retail\<fdid>.wmo and a
# type-14 gameobject_template; the module lays rooms out from the template origin (HousingRooms.h).
# NeighborhoodMap 7 puts Home Interior's entry at (-1000, -1000, 0.1): rooms stand on z 0, 2 yd above its flat terrain.
# Raised 100 yd above Home Interior's flat terrain (z about -2) so basements have room below the ground floor.
ROOM_ORIGIN = (-1000.0, -1000.0, 100.0)
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
# Razorwind Shores' (tools/neighborhood_plots.py, NeighborhoodMap 2)
PLOTS_OF = {NEIGHBORHOOD_MAP: PLOTS,
            RAZORWIND_MAP: list(csv.DictReader((MODULE / "data/plots_razorwind.tsv").open(encoding="utf-8"), delimiter="\t"))}
EXTERIOR = list(csv.DictReader((MODULE / "data/exterior.tsv").open(encoding="utf-8"), delimiter="\t"))
EXTERIOR_MODELS = sorted({int(r["fdid"]) for r in EXTERIOR})
CORNERSTONE_FDID = 6935310  # GameObjects 527268 "Cornerstone - Plot 0" -> GameObjectDisplayInfo 110660
EXTERIOR_DISPLAY_BASE, EXTERIOR_GO_BASE = DISPLAY_BASE + 100, GO_BASE + 150
CORNERSTONE_DISPLAY, CORNERSTONE_GO = EXTERIOR_DISPLAY_BASE + 99, EXTERIOR_GO_BASE + 49
FRONT_DOOR_DISPLAY, FRONT_DOOR_GO = EXTERIOR_DISPLAY_BASE + 98, EXTERIOR_GO_BASE + 48
assert len(EXTERIOR_MODELS) <= 48, f"{len(EXTERIOR_MODELS)} exterior models; entries {EXTERIOR_GO_BASE}+ hold 48 before the front door"
# Every part an owner may swap in (data/fixtures.tsv, fixture_hooks.tsv from make_plots.py). A model the default
# exterior already uses keeps its entry there, so existing houses keep their spawns; the rest get entries of their own.
FIXTURES = list(csv.DictReader((MODULE / "data/fixtures.tsv").open(encoding="utf-8"), delimiter="\t"))
FIXTURE_HOOKS = list(csv.DictReader((MODULE / "data/fixture_hooks.tsv").open(encoding="utf-8"), delimiter="\t"))
FIXTURE_MODELS = sorted({int(r["fdid"]) for r in FIXTURES} - set(EXTERIOR_MODELS))
FIXTURE_DISPLAY_BASE, FIXTURE_GO_BASE, FIXTURE_SLOTS = 62000, 9502000, 1000
assert len(FIXTURE_MODELS) <= FIXTURE_SLOTS, f"{len(FIXTURE_MODELS)} fixture models, {FIXTURE_SLOTS} slots"


def fixture_entry(fdid):
    return EXTERIOR_GO_BASE + EXTERIOR_MODELS.index(fdid) if fdid in EXTERIOR_MODELS else FIXTURE_GO_BASE + FIXTURE_MODELS.index(fdid)


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
THUMBNAILS_LUA = Path(r"R:\Users\Zach\Documents\GitHub\wowdecomp\Addons\EsteriaHousing\Thumbnails.lua")
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

# Retail HouseDecor (wago.tools live, 2026-11-07): real names, placement Type and thumbnails. Catalog slots stay where
# catalog() put them (placed decor and outdoor spawns hold their gameobject entry); only names and surfaces change.
HOUSE_DECOR = {int(r["ID"]): r for r in csv.DictReader((MODULE / "data/house_decor.csv").open(encoding="utf-8"))}
SURFACE_OF_TYPE = {"1": "floor", "2": "wall", "3": "ceiling", "4": "floor"}  # HouseDecor.Type; 4 is rugs


def is_dnt(decor):
    name = HOUSE_DECOR[decor]["Name_lang"] if decor in HOUSE_DECOR else ""
    return "[DNT]" in name or "do not use" in name.lower() or name.lower().startswith("test")


def retail_named(rows):
    out, names = [], set()
    for decor, fdid, name, category, surface in rows:
        r = HOUSE_DECOR.get(decor)
        if r and not is_dnt(decor) and r["Name_lang"].strip():
            name = r["Name_lang"].strip()[:96]
            if surface != "on-decor":  # retail has no such Type; keep SLICE's hand-picked ones
                surface = SURFACE_OF_TYPE.get(r["Type"], surface)
        base, n = name, 2
        while name in names:
            name, n = f"{base} {n}", n + 1
        names.add(name)
        out.append((decor, fdid, name, category, surface))
    return out


# Group 1 (2026-11-07): every real retail decor in our build's inventory that catalog() skipped, i.e. M2s outside
# playerhousing\ and ones Phase 0 flagged against the old MPQ, kept where RetailAssetProbe --batch loaded the model
# from the pinned build. Append-only, so slots never move. Thumbnails: retail's picture of each decor that loaded.
CATALOG2_ROWS = list(csv.DictReader((MODULE / "data/catalog2.tsv").open(encoding="utf-8"), delimiter="\t"))
THUMBNAILS = {int(r["decor_id"]): (int(r["thumb_fdid"]), int(r["width"]))
              for r in csv.DictReader((MODULE / "data/decor_thumbnails.tsv").open(encoding="utf-8"), delimiter="\t")}
DECOR2_DISPLAY_BASE, DECOR2_GO_BASE, DECOR2_SLOTS = 63000, 9503000, 3000
# Groups 2 and 3 (2026-11-07, tools/retail_decor.py): retail decor newer than our build, whose files ship packed
# (patch-RetailDecor-001.MPQ), and the WMO decor our build has; kept where RetailAssetProbe --batch loaded the model.
# Appended to block 2 after catalog2.tsv, so no slot moves.
CATALOG3_ROWS = list(csv.DictReader((MODULE / "data/catalog3.tsv").open(encoding="utf-8"), delimiter="\t"))
WMO_DECOR = {int(r["decor_id"]) for r in CATALOG3_ROWS if r["kind"] == "wmo"}
CATALOG = retail_named(catalog() + [(int(r["decor_id"]), int(r["model_fdid"]), "", r["category"], "floor")
                                    for r in CATALOG2_ROWS + CATALOG3_ROWS])
BLOCK1 = len(CATALOG) - len(CATALOG2_ROWS) - len(CATALOG3_ROWS)
assert BLOCK1 <= DECOR_SLOTS and len(CATALOG2_ROWS) + len(CATALOG3_ROWS) <= DECOR2_SLOTS, \
    f"{BLOCK1} + {len(CATALOG2_ROWS)} + {len(CATALOG3_ROWS)} decor"


def decor_model(decor, fdid):
    """The display's model and geometry box: a WMO decor is a building-sized map object."""
    return (f"retail\\{fdid}.wmo", (-12, -12, 0, 12, 12, 15)) if decor in WMO_DECOR else (f"retail\\{fdid}.m2", (-1, -1, 0, 1, 1, 2))
assert len({r[0] for r in CATALOG}) == len(CATALOG), "a decor ID is in both blocks"


def decor_slot(i):
    """Display and gameobject entry of CATALOG[i]: block 1 (catalog()) then block 2 (catalog2.tsv)."""
    return (DECOR_DISPLAY_BASE + i, DECOR_GO_BASE + i) if i < BLOCK1 else \
        (DECOR2_DISPLAY_BASE + i - BLOCK1, DECOR2_GO_BASE + i - BLOCK1)


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
        # AreaTableID: the zone the server gives a player on this map (it has no area data for it), and so the zone
        # character select names
        row[0], row[2], row[22], row[65] = map_id, instance_type, AREAS[map_id][0], max_players
        row[57] = LOADING_SCREENS[map_id][0]
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
              f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {DECOR_DISPLAY_BASE} AND {DECOR_DISPLAY_BASE + DECOR_SLOTS - 1};",
              f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {DECOR2_GO_BASE} AND {DECOR2_GO_BASE + DECOR2_SLOTS - 1};",
              f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {DECOR2_DISPLAY_BASE} AND "
              f"{DECOR2_DISPLAY_BASE + DECOR2_SLOTS - 1};"]
    for i, (decor, fdid, name, category, surface) in enumerate(CATALOG):
        display, entry = decor_slot(i)
        model, box = decor_model(decor, fdid)
        lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                     f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(model)}, {', '.join(map(str, box))});")
        if is_exit(fdid):  # type 10 (goober): clicking it runs the script's gossip hello, which leaves the house
            lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`) "
                         f"VALUES ({entry}, 10, {display}, {q(name + ' (exit)')}, 1, 'go_esteria_housing_exit');")
        else:  # 5 generic M2; 14 map object, the type 3.3.5 draws a WMO for
            lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                         f"VALUES ({entry}, {14 if decor in WMO_DECOR else 5}, {display}, {q(name)}, 1);")
        # model_fdid is what the client previews (ghost, chest model): a WMO's with the high bit set (wowdecomp Housing.cpp
        # WmoDecorBit), so it previews that as a map object
        lines.append(f"INSERT INTO `housing_decor_catalog` (`decor_id`, `model_fdid`, `display_id`, `gameobject_entry`, `name`, "
                     f"`category`, `surface`, `min_scale`, `max_scale`, `origin`, `enabled`) VALUES ({decor}, "
                     f"{fdid | 0x80000000 if decor in WMO_DECOR else fdid}, {display}, "
                     f"{entry}, {q(name)}, {CATEGORY[category]}, {SURFACE[surface]}, 0.5, 2, 'retail', {int(not is_dnt(decor))});")
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
    # The server's AreaTable lacks the zones map_dbc's AreaTableID names (Founder's Point, Home Interior): their rows,
    # as the client's (subzones need no row; without area data the server never places anyone in one).
    zones = [(area, map_id, name) for map_id, (area, name) in AREAS.items()]
    lines.append(f"DELETE FROM `areatable_dbc` WHERE `ID` IN ({', '.join(str(a) for a, _, _ in zones)});")
    for area, map_id, name in zones:
        lines.append(f"INSERT INTO `areatable_dbc` (`ID`, `ContinentID`, `ParentAreaID`, `AreaBit`, `Flags`, `SoundProviderPref`, "
                     f"`SoundProviderPrefUnderwater`, `AmbienceID`, `ZoneMusic`, `IntroSound`, `ExplorationLevel`, `AreaName_Lang_enUS`, "
                     f"`AreaName_Lang_enGB`, `AreaName_Lang_koKR`, `AreaName_Lang_frFR`, `AreaName_Lang_deDE`, `AreaName_Lang_enCN`, "
                     f"`AreaName_Lang_zhCN`, `AreaName_Lang_enTW`, `AreaName_Lang_zhTW`, `AreaName_Lang_esES`, `AreaName_Lang_esMX`, "
                     f"`AreaName_Lang_ruRU`, `AreaName_Lang_ptPT`, `AreaName_Lang_ptBR`, `AreaName_Lang_itIT`, `AreaName_Lang_Unk`, "
                     f"`AreaName_Lang_Mask`, `FactionGroupMask`, `LiquidTypeID_1`, `LiquidTypeID_2`, `LiquidTypeID_3`, `LiquidTypeID_4`, "
                     f"`MinElevation`, `Ambient_Multiplier`, `Lightid`) VALUES ({area}, {map_id}, 0, {AREA_BITS[area]}, "
                     f"{AREA_FLAGS[map_id]}, 0, 0, 0, 0, 0, 0, {q(name)}, {', '.join(['' + chr(39) * 2] * 15)}, 16712190, 6, 0, 0, 0, 0, "
                     f"-500, 0, 0);")
    lines += [
        f"DELETE FROM `instance_template` WHERE `map` IN ({', '.join(map(str, MAPS))});",
        *[f"INSERT INTO `instance_template` (`map`, `parent`, `script`, `allowMount`) VALUES ({m}, 0, '', {int(m != HOUSE_MAP)});"
          for m in MAPS],
        # MapMgr::PlayerCannotEnter refuses a party map with no MapDifficulty row; 40 players so visits never fill it.
        f"DELETE FROM `mapdifficulty_dbc` WHERE `ID` IN ({', '.join(map(str, MAPS))});",
        *[f"INSERT INTO `mapdifficulty_dbc` (`ID`, `MapID`, `Difficulty`, `Message_Lang_Mask`, `RaidDuration`, `MaxPlayers`) "
          f"VALUES ({m}, {m}, 0, 16712188, 0, {MAPS[m][3]});" for m in MAPS],
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
    lines.append(f"INSERT INTO `housing_exterior_piece` (`style`, `role`, `gameobject_entry`, `pos_x`, `pos_y`, `pos_z`, "
                 f"`rot_deg`) VALUES (0, 'front_door', {FRONT_DOOR_GO}, 0, 0, 0, 0);")
    lines += [f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {FIXTURE_GO_BASE} AND {FIXTURE_GO_BASE + FIXTURE_SLOTS - 1};",
              f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {FIXTURE_DISPLAY_BASE} AND "
              f"{FIXTURE_DISPLAY_BASE + FIXTURE_SLOTS - 1};"]
    for i, fdid in enumerate(FIXTURE_MODELS):
        display, entry = FIXTURE_DISPLAY_BASE + i, FIXTURE_GO_BASE + i
        lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                     f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(f'retail\\{fdid}.wmo')}, -12, -12, 0, 12, 12, 15);")
        lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                     f"VALUES ({entry}, 14, {display}, {q(f'House piece {fdid}')}, 1);")
    for r in FIXTURES:
        lines.append(f"INSERT INTO `housing_exterior_fixture` VALUES ({r['component']}, {r['theme']}, {r['type']}, {r['size']}, "
                     f"{r['parent']}, {r['is_default']}, {fixture_entry(int(r['fdid']))}, {q(r['name'])}, {r['mat_x']}, {r['mat_z']});")
    for r in FIXTURE_HOOKS:
        lines.append(f"INSERT INTO `housing_exterior_fixture_hook` (`component`, `type`, `pos_x`, `pos_y`, `pos_z`, `rot_deg`) "
                     f"VALUES ({r['component']}, {r['type']}, {r['x']}, {r['y']}, {r['z']}, {r['rot_deg']});")
    lines.append("DELETE FROM `housing_exterior_style`;")
    for style, name in sorted({(int(r["style"]), r["name"]) for r in EXTERIOR}):
        lines.append(f"INSERT INTO `housing_exterior_style` VALUES ({style}, {q(name)});")
    for r in EXTERIOR:
        lines.append(f"INSERT INTO `housing_exterior_piece` (`style`, `role`, `gameobject_entry`, `pos_x`, `pos_y`, `pos_z`, "
                     f"`rot_deg`, `mat_x`, `mat_z`) VALUES ({r['style']}, {q(r['role'])}, "
                     f"{EXTERIOR_GO_BASE + EXTERIOR_MODELS.index(int(r['fdid']))}, {r['x']}, {r['y']}, {r['z']}, {r['rot_deg']}, "
                     f"{r['mat_x']}, {r['mat_z']});")
    for map_id, p in ((m, p) for m in NEIGHBORHOOD_MAPS for p in PLOTS_OF[m]):
        lines.append(f"INSERT INTO `housing_plot` VALUES ({map_id}, {p['plot']}, {p['house_x']}, {p['house_y']}, "
                     f"{p['house_z']}, {p['house_yaw']}, {p['corner_x']}, {p['corner_y']}, {p['corner_z']}, {p['corner_o']}, "
                     f"{p['exit_x']}, {p['exit_y']}, {p['exit_z']});")
        # The retail sign model faces its -x: facing the street takes CornerstoneRotation turned half way round.
        o = (float(p["corner_o"]) + math.pi) % (2 * math.pi)
        lines.append(f"INSERT INTO `gameobject` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, "
                     f"`position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, "
                     f"`animprogress`, `state`) VALUES ({CORNERSTONE_GUID_BASE + 100 * NEIGHBORHOOD_MAPS.index(map_id) + int(p['plot'])}, "
                     f"{CORNERSTONE_GO}, {map_id}, 1, 1, {p['corner_x']}, {p['corner_y']}, {p['corner_z']}, {o}, 0, 0, "
                     f"{round(math.sin(o / 2), 6)}, {round(math.cos(o / 2), 6)}, 0, 100, 1);")
    lines += [
        "",
        f"-- A steward at each neighborhood's entry takes players home.",
        f"DELETE FROM `creature` WHERE `guid` IN ({STEWARD}, {STEWARD + 1});",
        *[f"INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, "
          f"`orientation`, `spawntimesecs`) VALUES ({STEWARD + i}, {STEWARD}, {m}, 1, 1, {', '.join(map(str, ENTRIES[m]))}, 300);"
          for i, m in enumerate(NEIGHBORHOOD_MAPS)],
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


def append_rows(original, fields, size, new):
    """WDBC original plus rows given as (words, {field: text}); words are packed as uint32 unless float."""
    count, f, sz, _ = struct.unpack_from("<4I", original, 4)
    assert (f, sz) == (fields, size), f"layout {f}x{sz}, expected {fields}x{size}"
    _, _, rows, strings = read_wdbc(original)
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    strings = bytearray(strings)
    for words, texts in new:
        assert words[0] not in taken, f"row {words[0]} already there"
        words = list(words)
        for i, text in texts.items():
            words[i] = len(strings)
            strings += text.encode("utf-8") + b"\0"
        rows.append(b"".join(struct.pack("<f" if isinstance(w, float) else "<i" if w < 0 else "<I", w) for w in words))
    return b"WDBC" + struct.pack("<4I", len(rows), fields, size, len(strings)) + b"".join(rows) + bytes(strings)


def patch_world_map(storm, client):
    """AreaTable.dbc and WorldMapArea.dbc with the housing maps, and the world map's tiles."""
    _, areas = winning_dbc(storm, client, AREA_DBC_NAME)
    _, _, rows, _ = read_wdbc(areas)
    row_of = lambda id: next(list(struct.unpack("<36I", r)) for r in rows if struct.unpack_from("<I", r)[0] == id)  # noqa: E731
    bit = max(struct.unpack_from("<I", r, 12)[0] for r in rows)
    places = [(area, map_id, 0, name, AREA_TEMPLATE) for map_id, (area, name) in AREAS.items()]
    places += [(area, m, AREAS[m][0], name, SUBZONE_TEMPLATE) for m, zones in SUBZONES_OF.items() for area, name in zones.items()]
    taken = {struct.unpack_from("<I", r, 12)[0] for r in rows}
    new = []
    for area, map_id, parent, name, template in places:
        assert AREA_BITS[area] not in taken, f"AreaBit {AREA_BITS[area]} is used in this client's AreaTable"
        words = row_of(template)
        words[0], words[1], words[2], words[3], words[4] = area, map_id, parent, AREA_BITS[area], AREA_FLAGS[map_id]
        new.append((words, {11: name}))  # enUS name; the other locales keep the template's
    files = {AREA_DBC_NAME: append_rows(areas, 36, 144, new)}

    _, world = winning_dbc(storm, client, WORLD_MAP_DBC_NAME)
    _, _, rows, _ = read_wdbc(world)
    next_id = max(struct.unpack_from("<I", r)[0] for r in rows)
    new = []
    for map_id, (area, _name) in AREAS.items():
        next_id += 1
        name, bounds = WORLD_MAPS[map_id]
        new.append(([next_id, map_id, area, 0, *[float(v) for v in bounds], -1, 0, 0], {3: name}))
    files[WORLD_MAP_DBC_NAME] = append_rows(world, 11, 44, new)

    _, screens = winning_dbc(storm, client, LOADING_DBC_NAME)
    screen_dir = "Interface\\Glues\\LoadingScreens\\"
    new = [([screen, 0, 0, 1], {1: name, 2: f"{screen_dir}{stem}.blp"}) for screen, name, stem in LOADING_SCREENS.values()]
    files[LOADING_DBC_NAME] = append_rows(screens, 4, 16, new)
    for _, _, stem in LOADING_SCREENS.values():
        for suffix in ("", "Wide"):
            files[f"{screen_dir}{stem}{suffix}.blp"] = (MODULE / "data/loadscreens" / f"{stem}{suffix}.blp").read_bytes()

    for name in sorted({name for name, _ in WORLD_MAPS.values()}):
        for blp in sorted((MODULE / "data/worldmap" / name).glob("*.blp")):
            files[f"Interface\\WorldMap\\{name}\\{blp.name}"] = blp.read_bytes()
        assert sum(1 for f in files if f"\\{name}\\" in f) == 12, f"the {name} world map needs its 12 tiles"
    return files


def patch_dbc(storm, client):
    archive, original = winning_dbc(storm, client, DBC_NAME)
    fields, size, rows, strings = read_wdbc(original)
    assert (fields, size) == (19, 76), f"GameObjectDisplayInfo.dbc layout {fields}x{size}, expected 19x76"
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    strings = bytearray(strings)
    added = []
    models = [(decor_slot(i)[0], *decor_model(decor, fdid)) for i, (decor, fdid, *_rest) in enumerate(CATALOG)]
    models += [(ROOM_DISPLAY_BASE + i, f"retail\\{fdid}.wmo", (-12, -12, 0, 12, 12, 11)) for i, fdid in enumerate(ROOM_MODELS)]
    models += [(EXTERIOR_DISPLAY_BASE + i, f"retail\\{fdid}.wmo", (-12, -12, 0, 12, 12, 15)) for i, fdid in enumerate(EXTERIOR_MODELS)]
    models += [(FIXTURE_DISPLAY_BASE + i, f"retail\\{fdid}.wmo", (-12, -12, 0, 12, 12, 15)) for i, fdid in enumerate(FIXTURE_MODELS)]
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
    files = {DBC_NAME: dbc, MAP_DBC_NAME: patch_map_dbc(map_original), **patch_world_map(storm, args.client)}
    # section 3 (make_adventure.py): its client rows, and sql/world/housing_adventure_world.sql
    import make_adventure
    display_of = {decor: (decor_slot(i)[0], fdid) for i, (decor, fdid, *_rest) in enumerate(CATALOG)}
    files.update(make_adventure.patch_files(winning_dbc, append_rows, storm, args.client, display_of))
    # section 5 (make_household.py): the House Hearthstone's rows, and sql/world/housing_household_world.sql
    import make_household
    files.update(make_household.patch_files(winning_dbc, append_rows, storm, args.client, display_of, files))
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
    print(f"wrote {target} ({len(CATALOG) + len(ROOM_MODELS) + len(EXTERIOR_MODELS) + len(FIXTURE_MODELS) + 2} display rows on top of {source.name}; "
          f"maps {', '.join(map(str, MAPS))} on top of {map_source.name}'s Map.dbc)")
    thumbs = sorted((decor, *THUMBNAILS[decor]) for decor, *_ in CATALOG if decor in THUMBNAILS and not is_dnt(decor))
    pow2 = lambda v: 1 << (v - 1).bit_length()  # noqa: E731 (the client pads 400 x 400 into 512 x 512: CascSource.cpp)
    THUMBNAILS_LUA.write_text("-- Generated by EsteriaWoW mod-esteria-housing/tools/make_slice.py. Do not edit.\n"
                              "-- decorId = { retail HouseDecor.ThumbnailFileDataID, share of the padded texture the picture fills }\n"
                              "EsteriaHousingUI = EsteriaHousingUI or {}\nEsteriaHousingUI.THUMBNAILS = {\n"
                              + "".join(f"  [{d}] = {{ {t}, {w / pow2(w):g} }},\n" for d, t, w in thumbs) + "}\n", encoding="utf-8", newline="\n")
    print(f"wrote {THUMBNAILS_LUA} ({len(thumbs)} thumbnails)")
    # The client finds each map's WDT through these aliases (Data/Retail/RetailCasc.ini aliases=).
    for map_id, fdid in MAP_FDIDS.items():
        print(f"alias: {fdid};World\\Maps\\{MAPS[map_id][0]}\\{MAPS[map_id][0]}.wdt")


if __name__ == "__main__":
    main()
