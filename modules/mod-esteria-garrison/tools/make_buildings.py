"""Write garrison building WMO display/GO rows and rebuild the garrison client patch.

Display IDs 67000+buildingId*2(+1 horde). GO entries 9510000+buildingId*2(+1 horde).
Scaffold displays 66500+garrPlot*2(+1 horde). Scaffold GO 9525000+garrPlot*2(+1 horde).
Model paths are retail\\<FileDataID>.wmo from the community listfile (6hu_/6or_ garrison roots).
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
sys.path.insert(0, str(MODULE.parents[1] / "tools"))
from cars_mount_pack import Storm  # noqa: E402

CLIENT = Path(r"G:\risServer\Esteria - Client")
STORMLIB = CLIENT / "StormLib.dll"
PATCH_NAME = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZZGarrison.MPQ"
MAP_DBC = r"DBFilesClient\Map.dbc"
DISPLAY_DBC = r"DBFilesClient\GameObjectDisplayInfo.dbc"

# buildingId: (alliance_fdid, horde_fdid). Root WMO only (no _000 / lod / snow).
MODELS = {
    # warmill / bunker
    8: (902298, 961052),
    9: (902301, 961685),
    10: (902305, 961915),
    # barn
    24: (879991, 962501),
    25: (879994, 962504),
    133: (968495, 986287),
    # barracks
    26: (879793, 962632),
    27: (879796, 963162),
    28: (879799, 963165),
    # herb garden
    29: (902309, 962050),
    136: (892927, 962053),
    137: (1035307, 1035429),
    # inn / tavern
    34: (879932, 962202),
    35: (879936, 962205),
    36: (879947, 962208),
    # mage / spirit
    37: (892813, 963168),
    38: (892816, 963171),
    39: (892819, 963174),
    # lumber mill
    40: (879802, 940410),
    41: (879805, 940413),
    138: (1020699, 1030815),
    # menagerie
    42: (902388, 963177),
    167: (901737, 959785),
    168: (1020697, 967782),
    # storehouse / salvage
    51: (1044666, 1033917),
    142: (1044781, 1033916),
    143: (1044781, 1033915),  # alliance has no distinct rank3 WMO
    52: (1044795, 1033920),
    140: (1044800, 1033919),
    141: (1044800, 1033918),
    # forge
    60: (952024, 985196),
    117: (952028, 985199),
    118: (952028, 979195),
    # mine
    61: (903865, 968146),
    62: (916349, 968152),
    63: (916235, 968160),
    # fishing
    64: (984308, 984331),
    134: (984434, 984334),
    135: (984311, 984337),
    # stables
    65: (880196, 953679),
    66: (880199, 953682),
    67: (880202, 955807),
    # alchemy
    76: (951907, 984480),
    119: (951910, 984483),
    120: (951910, 979185),
    # tannery
    90: (951928, 977206),
    121: (951931, 977185),
    122: (951931, 977097),
    # engineering
    91: (951914, 985216),
    123: (951925, 985219),
    124: (951925, 979212),
    # enchanting
    93: (952016, 985206),
    125: (952001, 985211),
    126: (952001, 979203),
    # tailoring
    94: (951994, 985389),
    127: (951954, 985418),
    128: (951954, 979217),
    # inscription
    95: (952004, 974786),
    129: (951991, 974790),
    130: (951991, 974794),
    # jewelcrafting
    96: (951917, 980117),
    131: (951920, 980121),
    132: (951920, 980124),
    # trading post
    111: (901755, 960892),
    144: (892786, 960895),
    145: (1020778, 974942),
    # gladiator (alliance infirmary; no dedicated orc WMO in listfile)
    159: (880023, 880023),
    160: (880026, 880026),
    161: (880031, 880031),
    # workshop / gearworks
    162: (892725, 987022),
    163: (892728, 995741),
    164: (892731, 983931),
}

# GarrPlot ConstructObj models (ip_foundation / mine_v0 / specialty v0).
# Key is GarrPlot.ID used by PlotDef.garrPlot.
SCAFFOLDS = {
    12: (1020781, 1021175),  # small
    13: (999762, 996079),    # medium
    14: (1000466, 996231),   # large
    28: (939272, 968142),    # mine
    29: (1035305, 1035423),  # herb (no ConstructObj — gardenhouse_v0)
    31: (984301, 984321),    # fishing rank0
    42: (1035312, 1035435),  # menagerie_v0
}

NAMES = {
    8: "War Mill", 9: "War Mill", 10: "War Mill",
    24: "Barn", 25: "Barn", 133: "Barn",
    26: "Barracks", 27: "Barracks", 28: "Barracks",
    29: "Herb Garden", 136: "Herb Garden", 137: "Herb Garden",
    34: "Inn", 35: "Inn", 36: "Inn",
    37: "Mage Tower", 38: "Mage Tower", 39: "Mage Tower",
    40: "Lumber Mill", 41: "Lumber Mill", 138: "Lumber Mill",
    42: "Menagerie", 167: "Menagerie", 168: "Menagerie",
    51: "Storehouse", 142: "Storehouse", 143: "Storehouse",
    52: "Salvage Yard", 140: "Salvage Yard", 141: "Salvage Yard",
    60: "The Forge", 117: "The Forge", 118: "The Forge",
    61: "Mine", 62: "Mine", 63: "Mine",
    64: "Fishing Shack", 134: "Fishing Shack", 135: "Fishing Shack",
    65: "Stables", 66: "Stables", 67: "Stables",
    76: "Alchemy Lab", 119: "Alchemy Lab", 120: "Alchemy Lab",
    90: "The Tannery", 121: "The Tannery", 122: "The Tannery",
    91: "Engineering Works", 123: "Engineering Works", 124: "Engineering Works",
    93: "Enchanter's Study", 125: "Enchanter's Study", 126: "Enchanter's Study",
    94: "Tailoring Emporium", 127: "Tailoring Emporium", 128: "Tailoring Emporium",
    95: "Scribe's Quarters", 129: "Scribe's Quarters", 130: "Scribe's Quarters",
    96: "Gem Boutique", 131: "Gem Boutique", 132: "Gem Boutique",
    111: "Trading Post", 144: "Trading Post", 145: "Trading Post",
    159: "Gladiator's Sanctum", 160: "Gladiator's Sanctum", 161: "Gladiator's Sanctum",
    162: "Workshop", 163: "Workshop", 164: "Workshop",
}

SCAFFOLD_NAMES = {
    12: "Small Scaffold",
    13: "Medium Scaffold",
    14: "Large Scaffold",
    28: "Mine Scaffold",
    29: "Garden Scaffold",
    31: "Fishing Scaffold",
    42: "Menagerie Scaffold",
}


def display_id(building_id, horde):
    return 67000 + building_id * 2 + (1 if horde else 0)


def go_entry(building_id, horde):
    return 9510000 + building_id * 2 + (1 if horde else 0)


def scaffold_display_id(garr_plot, horde):
    return 66500 + garr_plot * 2 + (1 if horde else 0)


def scaffold_go_entry(garr_plot, horde):
    return 9525000 + garr_plot * 2 + (1 if horde else 0)


def q(text):
    return "'" + str(text).replace("\\", "\\\\").replace("'", "''") + "'"


def read_wdbc(data):
    assert data[:4] == b"WDBC"
    count, fields, size, strings = struct.unpack_from("<4I", data, 4)
    rows = [data[20 + i * size:20 + (i + 1) * size] for i in range(count)]
    blob = data[20 + count * size:20 + count * size + strings]
    return fields, size, rows, blob


def winning(storm, name, skip=PATCH_NAME):
    data_dir = CLIENT / "Data"
    found = [(f"data\\{p.name.lower()}", p) for p in data_dir.glob("patch-*") if p.suffix.lower() == ".mpq"]
    found += [(f"data\\enus\\{p.name.lower()}", p) for p in (data_dir / "enUS").glob("patch-enus-*")
              if p.suffix.lower() == ".mpq"]
    for _, archive in sorted(found, reverse=True):
        if archive.name.lower() == skip.lower():
            continue
        handle = storm.open_archive(archive)
        try:
            return archive, storm.read(handle, name)
        except OSError:
            continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    raise SystemExit("no patch MPQ holds " + name)


def append_display(original):
    fields, size, rows, strings = read_wdbc(original)
    assert (fields, size) == (19, 76), f"display layout {fields}x{size}"
    taken = {struct.unpack_from("<I", r)[0] for r in rows}
    strings = bytearray(strings)
    added = []

    def add_row(display, fdid):
        nonlocal strings
        assert display not in taken, f"display {display} already used"
        model = f"retail\\{fdid}.wmo"
        offset = len(strings)
        strings += model.encode("ascii") + b"\0"
        added.append(struct.pack("<2I10I6fI", display, offset, *([0] * 10), -12, -12, 0, 12, 12, 15, 0))
        taken.add(display)

    for building_id, (a_fdid, h_fdid) in MODELS.items():
        for horde, fdid in ((0, a_fdid), (1, h_fdid)):
            add_row(display_id(building_id, horde), fdid)
    for garr_plot, (a_fdid, h_fdid) in SCAFFOLDS.items():
        for horde, fdid in ((0, a_fdid), (1, h_fdid)):
            add_row(scaffold_display_id(garr_plot, horde), fdid)

    rows += added
    return b"WDBC" + struct.pack("<4I", len(rows), fields, size, len(strings)) + b"".join(rows) + bytes(strings)


def world_sql():
    building_displays = sorted({display_id(b, h) for b in MODELS for h in (0, 1)})
    building_entries = sorted({go_entry(b, h) for b in MODELS for h in (0, 1)})
    scaffold_displays = sorted({scaffold_display_id(p, h) for p in SCAFFOLDS for h in (0, 1)})
    scaffold_entries = sorted({scaffold_go_entry(p, h) for p in SCAFFOLDS for h in (0, 1)})
    lines = [
        "-- Generated by modules/mod-esteria-garrison/tools/make_buildings.py",
        "-- Draenor garrison building WMOs as type-33 destructible buildings (retail/<fdid>.wmo).",
        "",
        f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {min(building_displays)} AND {max(building_displays)};",
        f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {min(scaffold_displays)} AND {max(scaffold_displays)};",
        f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {min(building_entries)} AND {max(building_entries)};",
        f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {min(scaffold_entries)} AND {max(scaffold_entries)};",
    ]
    for building_id, (a_fdid, h_fdid) in sorted(MODELS.items()):
        name = NAMES[building_id]
        for horde, fdid in ((0, a_fdid), (1, h_fdid)):
            display = display_id(building_id, horde)
            entry = go_entry(building_id, horde)
            model = f"retail\\{fdid}.wmo"
            side = "Horde" if horde else "Alliance"
            lines.append(
                f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(model)}, -12, -12, 0, 12, 12, 15);"
            )
            lines.append(
                f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                f"VALUES ({entry}, 33, {display}, {q(f'{name} ({side})')}, 1);"
            )
    for garr_plot, (a_fdid, h_fdid) in sorted(SCAFFOLDS.items()):
        name = SCAFFOLD_NAMES[garr_plot]
        for horde, fdid in ((0, a_fdid), (1, h_fdid)):
            display = scaffold_display_id(garr_plot, horde)
            entry = scaffold_go_entry(garr_plot, horde)
            model = f"retail\\{fdid}.wmo"
            side = "Horde" if horde else "Alliance"
            lines.append(
                f"INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
                f"`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`) VALUES ({display}, {q(model)}, -12, -12, 0, 12, 12, 15);"
            )
            lines.append(
                f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`) "
                f"VALUES ({entry}, 33, {display}, {q(f'{name} ({side})')}, 1);"
            )
    return "\n".join(lines) + "\n"


def main():
    storm = Storm(STORMLIB)
    # Keep Map.dbc from the previous garrison patcher output if present, else rebuild from housing.
    map_source, map_dbc = winning(storm, MAP_DBC)
    own = CLIENT / "Data" / PATCH_NAME
    if own.exists():
        handle = storm.open_archive(own)
        try:
            map_dbc = storm.read(handle, MAP_DBC)
            map_source = own
        except OSError:
            pass
        finally:
            storm.dll.SFileCloseArchive(handle)

    display_source, display_dbc = winning(storm, DISPLAY_DBC)
    patched_display = append_display(display_dbc)

    sql_path = MODULE / "sql" / "world" / "garrison_buildings_world.sql"
    sql_path.write_text(world_sql(), encoding="utf-8", newline="\n")
    print("wrote", sql_path)

    files = {MAP_DBC: map_dbc, DISPLAY_DBC: patched_display}
    if own.exists():
        own.unlink()
    storm.create_archive(own, files)
    handle = storm.open_archive(own)
    try:
        assert storm.read(handle, DISPLAY_DBC) == patched_display
        assert storm.read(handle, MAP_DBC) == map_dbc
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"wrote {own} (Map.dbc from {map_source.name}; displays on top of {display_source.name})")
    print(f"{len(MODELS) * 2} building displays, {len(SCAFFOLDS) * 2} scaffold displays")


if __name__ == "__main__":
    main()
