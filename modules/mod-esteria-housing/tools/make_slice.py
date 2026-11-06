"""Generate the Phase 1 slice data from one list: the world SQL (catalog, GameObject templates, display rows, steward,
room template, map 35 overrides) and the dev client patch that carries the same 20 GameObjectDisplayInfo rows.

    python make_slice.py --map-dbc Map.dbc --client "G:/3.3.5a - Dev" --out <staging dir>

Map.dbc is the server's copy (docker cp ac-worldserver:/azerothcore/env/dist/data/dbc/Map.dbc). The client's winning
GameObjectDisplayInfo.dbc is read from the highest patch MPQ that holds it and written, with the 20 rows appended, to
<out>/Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZHousingDev.MPQ (sorts above Patch-ZZZZZZZZZZZZZZZZZZZZZZZZCoA.MPQ). Nothing is
installed. Every decor model is retail-origin: dev only (docs/housing/README.md).
"""
import argparse
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
STORMLIB = Path(r"R:\Users\Zach\Documents\GitHub\wowdecomp\Tools\MountStudio\runtime\backend\StormLib.dll")
PATCH_NAME = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZHousingDev.MPQ"
DBC_NAME = r"DBFilesClient\GameObjectDisplayInfo.dbc"

DISPLAY_BASE, GO_BASE, STEWARD = 60000, 9500000, 9500100
STEWARD_MODEL_FROM = 6740  # copy the Stormwind innkeeper's display
MAP_ID, MAP_MAX_PLAYERS = 35, 40
# Areatrigger 107 "Stormwind Vault Entrance" (acore_world.areatrigger_teleport) lands here.
VAULT_ENTRY = (-0.91, 40.57, -24.23, 0.0)

# Phase 2a: retail HouseRoom 1 "Square Room (Small)" (RoomWmoData 5, box +-11.5 x +-11.5 x 0..11), built from its
# RoomComponent rows (wowdecomp docs/housing/room-components.tsv) as type-14 GameObjects showing retail\<fdid>.wmo.
# shortcut: 30 yd above the vault entry so the retail floor is the only floor and a missing floor is a short fall;
# move to map 2783 (docs/housing/maps-recon.md) once terrain loads.
ROOM_ORIGIN = (VAULT_ENTRY[0], VAULT_ENTRY[1], VAULT_ENTRY[2] + 30.0)
ROOM_DISPLAY_BASE, ROOM_GO_BASE = DISPLAY_BASE + 50, GO_BASE + 50
ROOM_MODELS = [6431804, 6431855, 6431794, 6431786]  # floor, wall, corner, ceiling
# RoomComponent.ID, model FileDataID, OffsetPos, OffsetRot z (degrees)
ROOM_PIECES = [
    (25, 6431804, (0.0, 0.0, 0.0), 0.0),
    (26, 6431855, (-12.0, 0.0, 0.0), 0.0),
    (27, 6431855, (0.0, 12.0, 0.0), 90.0),
    (28, 6431855, (0.0, -12.0, 0.0), -90.0),
    (29, 6431855, (12.0, 0.0, 0.0), -180.0),
    (30, 6431794, (-11.495, 11.5, 0.0), -90.0),
    (31, 6431794, (11.5, 11.5, 0.0), 0.0),
    (32, 6431794, (11.495, -11.5, 0.0), 90.0),
    (33, 6431794, (-11.5, -11.495, 0.0), -180.0),
    (64, 6431786, (0.0, 0.0, 7.0), 0.0),
]
ENTRY = (ROOM_ORIGIN[0], ROOM_ORIGIN[1], ROOM_ORIGIN[2] + 0.5, 0.0)
# Decor stays inside the room box (RoomWmoData 5), measured from the floor at the origin.
BOUNDS_HALF = (11.0, 11.0)
BOUNDS_Z = (-0.5, 11.0)
MAX_DECOR = 50

CATEGORY = {"Misc": 0, "Furniture": 1, "Accents": 2, "Lighting": 3, "Nature": 4, "Structural": 5}
SURFACE = {"floor": 0, "wall": 1, "ceiling": 2, "on-decor": 3}

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
]


def q(text):
    return "'" + str(text).replace("\\", "\\\\").replace("'", "''") + "'"


def read_wdbc(data):
    assert data[:4] == b"WDBC", "not a WDBC file"
    count, fields, size, strings = struct.unpack_from("<4I", data, 4)
    rows = [data[20 + i * size:20 + (i + 1) * size] for i in range(count)]
    return fields, size, rows, data[20 + count * size:20 + count * size + strings]


def map_row(path):
    fields, size, rows, strings = read_wdbc(Path(path).read_bytes())
    assert fields == 66, f"Map.dbc has {fields} fields, expected 66 (3.3.5a)"
    text = {1} | set(range(5, 21)) | set(range(23, 39)) | set(range(40, 56))
    floats = {58, 60, 61}
    for row in rows:
        values = list(struct.unpack("<66I", row))
        signed = struct.unpack("<66i", row)  # TimeOfDayOverride and friends are -1 when unset
        if values[0] != MAP_ID:
            continue
        out = []
        for i, v in enumerate(values):
            if i in text:
                out.append(q(strings[v:strings.index(b"\0", v)].decode("utf-8")))
            elif i in floats:
                out.append(repr(struct.unpack("<f", struct.pack("<I", v))[0]))
            else:
                out.append(str(signed[i]))
        out[2] = "1"                    # InstanceType: party, so MapInstanced gives each house its own copy
        out[65] = str(MAP_MAX_PLAYERS)  # MaxPlayers: MapDifficulty row 9 says 0, which would make every instance full
        return out
    raise SystemExit(f"map {MAP_ID} not in {path}")


def world_sql(map_values):
    lo = tuple(round(v, 2) for v in (ENTRY[0] - BOUNDS_HALF[0], ENTRY[1] - BOUNDS_HALF[1], ENTRY[2] + BOUNDS_Z[0]))
    hi = tuple(round(v, 2) for v in (ENTRY[0] + BOUNDS_HALF[0], ENTRY[1] + BOUNDS_HALF[1], ENTRY[2] + BOUNDS_Z[1]))
    lines = [
        "-- Generated by modules/mod-esteria-housing/tools/make_slice.py. Do not edit; change SLICE and regenerate.",
        "-- Dev world DB only (housing_dev_world). Rollback: housing_world_rollback.sql.",
        "",
        (MODULE / "sql/world/housing_world_tables.sql").read_text(encoding="utf-8").strip(),
        "",
        f"DELETE FROM `housing_decor_catalog`;",
        f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {GO_BASE} AND {GO_BASE + 99};",
        f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {DISPLAY_BASE} AND {DISPLAY_BASE + 99};",
    ]
    for i, (decor, fdid, name, category, surface) in enumerate(SLICE):
        display, entry = DISPLAY_BASE + i, GO_BASE + i
        lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                     f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(f'retail\\{fdid}.m2')}, -1, -1, 0, 1, 1, 2);")
        lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                     f"VALUES ({entry}, 5, {display}, {q(name)}, 1);")
        lines.append(f"INSERT INTO `housing_decor_catalog` (`decor_id`, `model_fdid`, `display_id`, `gameobject_entry`, `name`, "
                     f"`category`, `surface`, `origin`, `enabled`) VALUES ({decor}, {fdid}, {display}, {entry}, {q(name)}, "
                     f"{CATEGORY[category]}, {SURFACE[surface]}, 'retail', 1);")
    lines += ["", "DELETE FROM `housing_room_piece` WHERE `room_template_id` = 1;"]
    for i, fdid in enumerate(ROOM_MODELS):
        display, entry = ROOM_DISPLAY_BASE + i, ROOM_GO_BASE + i
        lines.append(f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                     f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(f'retail\\{fdid}.wmo')}, -12, -12, 0, 12, 12, 11);")
        lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                     f"VALUES ({entry}, 14, {display}, {q(f'Room piece {fdid}')}, 1);")
    for piece, fdid, offset, degrees in ROOM_PIECES:
        pos = [round(ROOM_ORIGIN[a] + offset[a], 3) for a in range(3)]
        yaw = round(math.radians(degrees) % (2 * math.pi), 6)
        lines.append(f"INSERT INTO `housing_room_piece` VALUES (1, {piece}, {ROOM_GO_BASE + ROOM_MODELS.index(fdid)}, "
                     f"{pos[0]}, {pos[1]}, {pos[2]}, {yaw});")
    lines += [
        "",
        f"DELETE FROM `housing_room_template` WHERE `room_template_id` = 1;",
        f"INSERT INTO `housing_room_template` VALUES (1, {MAP_ID}, {ENTRY[0]}, {ENTRY[1]}, {ENTRY[2]}, {ENTRY[3]}, "
        f"{lo[0]}, {lo[1]}, {lo[2]}, {hi[0]}, {hi[1]}, {hi[2]}, {MAX_DECOR}, 'Stormwind Vault (slice)');",
        "",
        f"DELETE FROM `creature_template` WHERE `entry` = {STEWARD};",
        f"DELETE FROM `creature_template_model` WHERE `CreatureID` = {STEWARD};",
        f"INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, "
        f"`unit_class`, `unit_flags`, `type`, `ScriptName`) VALUES ({STEWARD}, 'Housing Steward', 'Esteria Housing', 80, 80, 35, 1, "
        f"1, 2, 7, 'npc_esteria_housing_steward');",
        f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) "
        f"SELECT {STEWARD}, 0, `CreatureDisplayID`, 1, 1 FROM `creature_template_model` WHERE `CreatureID` = {STEWARD_MODEL_FROM} AND `Idx` = 0;",
        "",
        f"-- Map {MAP_ID} (Stormwind Vault, unused) becomes a party instance on this realm only. The client's Map.dbc keeps type 0.",
        f"DELETE FROM `instance_template` WHERE `map` = {MAP_ID};",
        f"INSERT INTO `instance_template` (`map`, `parent`, `script`, `allowMount`) VALUES ({MAP_ID}, 0, '', 0);",
        f"DELETE FROM `map_dbc` WHERE `ID` = {MAP_ID};",
        f"INSERT INTO `map_dbc` VALUES ({', '.join(map_values)});",
        "",
    ]
    return "\n".join(lines)


def patch_dbc(client):
    sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))
    from cars_mount_pack import Storm
    storm = Storm(STORMLIB)
    data_dir = Path(client) / "Data"
    archives = sorted({p.name.lower(): p for p in data_dir.iterdir() if p.suffix.lower() == ".mpq"
                       and p.name.lower().startswith("patch-")}.values(), key=lambda p: p.name.lower(), reverse=True)
    for archive in archives:
        if archive.name.lower() == PATCH_NAME.lower():
            continue  # never build on our own earlier output
        handle = storm.open_archive(archive)
        try:
            original = storm.read(handle, DBC_NAME)
        except OSError:
            continue
        finally:
            storm.dll.SFileCloseArchive(handle)
        break
    else:
        raise SystemExit("no patch MPQ holds " + DBC_NAME)
    fields, size, rows, strings = read_wdbc(original)
    assert (fields, size) == (19, 76), f"GameObjectDisplayInfo.dbc layout {fields}x{size}, expected 19x76"
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    strings = bytearray(strings)
    added = []
    models = [(DISPLAY_BASE + i, f"retail\\{fdid}.m2", (-1, -1, 0, 1, 1, 2)) for i, (_, fdid, *_rest) in enumerate(SLICE)]
    models += [(ROOM_DISPLAY_BASE + i, f"retail\\{fdid}.wmo", (-12, -12, 0, 12, 12, 11)) for i, fdid in enumerate(ROOM_MODELS)]
    for display, name, box in models:
        assert display not in taken, f"display {display} already used in {archive.name}"
        offset = len(strings)
        strings += name.encode("ascii") + b"\0"
        added.append(struct.pack("<2I10I6fI", display, offset, *([0] * 10), *box, 0))
    rows += added
    out = b"WDBC" + struct.pack("<4I", len(rows), fields, size, len(strings)) + b"".join(rows) + bytes(strings)
    return storm, archive, out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-dbc", required=True)
    parser.add_argument("--client", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sql = MODULE / "sql/world/housing_world.sql"
    sql.write_text(world_sql(map_row(args.map_dbc)), encoding="utf-8", newline="\n")
    print("wrote", sql)

    storm, source, dbc = patch_dbc(args.client)
    target = out / PATCH_NAME
    if target.exists():
        target.unlink()
    storm.create_archive(target, {DBC_NAME: dbc})
    handle = storm.open_archive(target)
    try:
        assert storm.read(handle, DBC_NAME) == dbc, "read-back mismatch"
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"wrote {target} ({len(SLICE) + len(ROOM_MODELS)} rows on top of {source.name}'s GameObjectDisplayInfo.dbc)")


if __name__ == "__main__":
    main()
