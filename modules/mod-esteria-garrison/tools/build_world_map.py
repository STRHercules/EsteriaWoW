"""Zone names and the world map for the six garrison maps, added to the garrison client patch without changing any row.

    python build_world_map.py [--client "G:/3.3.5a - Dev"]      # run after build_client_dbc.py

- AreaTable: the area IDs the retail garrison terrain carries (MCNK areaId: tier areas 7085/7086/7211 Alliance,
  7096/7103/7210 Horde, and the Shadowmoon/Frostfire subzones around them), so the zone text is right. Retail names
  the tier areas "$n's Garrison", which 3.3.5 cannot fill in; they are named Lunarfall / Frostwall. Retail's Frostwall
  (7004) is CoA's Cathedral Park in Esteria, so Frostwall gets the first free ID from 7079.
- WorldMapArea: one orphan zone per tier map (AreaID set, map not a continent), which CGWorldMap::SetMapToCurrentZone
  shows inside the instance, bounded by retail UiMapAssignment 582 (Lunarfall) / 590 (Frostwall).
- Interface\\WorldMap\\<name>\\<name>1..12.blp: retail UiMapArtTile, same 1002x668 layout of 4x3 256px tiles.
  Taken from the installed retail client (retail_assets.py), CDN second.
Writes sql/world/garrison_worldmap_world.sql for the server's areatable_dbc / worldmaparea_dbc.
"""
import argparse
import csv
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_client_dbc as b  # noqa: E402
import retail_assets as ra  # noqa: E402

REF = Path(r"G:\garrison-build\ref")  # wago.tools CSVs at the installed client's build (garrison_skins.py fetches)
CACHE = Path(r"G:\garrison-build\retail-originals")
SERVER_DBC = Path(r"G:\garrison-build\server-dbc")
SQL_OUT = b.MODULE / "sql" / "world" / "garrison_worldmap_world.sql"
AREA_STRINGS = list(range(11, 27))
# map: (faction, tier, UiMapArtID)
MAPS = {1158: ("Lunarfall", 1, 602), 1331: ("Lunarfall", 2, 603), 1159: ("Lunarfall", 3, 604),
        1152: ("Frostwall", 1, 613), 1330: ("Frostwall", 2, 614), 1153: ("Frostwall", 3, 626)}
# retail UiMapAssignment Region (minX, minY, maxX, maxY) of UiMap 582 / 590
BOUNDS = {"Lunarfall": (1635.416992, -137.5, 2091.666992, 545.833984),
          "Frostwall": (5345.833008, 4183.333008, 5814.583008, 4885.416016)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default=r"G:\3.3.5a - Dev")
    ap.add_argument("--live", default="acore_world")
    a = ap.parse_args()
    storm = b.Storm(b.STORMLIB)
    b.TABLES = {"AreaTable": (AREA_STRINGS, "areatable_dbc"), "WorldMapArea": ([3], "worldmaparea_dbc")}
    win = b.winners(storm, a.client)
    area, wma = b.Dbc(win["AreaTable"][1], AREA_STRINGS), b.Dbc(win["WorldMapArea"][1], [3])
    server = {n: b.Dbc((SERVER_DBC / f"{n}.dbc").read_bytes(), s) for n, s in (("AreaTable", AREA_STRINGS), ("WorldMapArea", [3]))}
    sql_taken = {t: {int(r[0]) for r in b.mysql(f"SELECT ID FROM {a.live}.{t}")} for t in ("areatable_dbc", "worldmaparea_dbc")}

    def free(rid, table, dbc, srv):
        return rid not in dbc.rows and rid not in server[srv].rows and rid not in sql_taken[table]

    retail = {int(r["ID"]): r for r in csv.DictReader((REF / "wago_AreaTable.csv").open(encoding="utf-8"))}
    frostwall = next(i for i in range(7079, 8000) if free(i, "areatable_dbc", area, "AreaTable") and i not in retail)
    # id: (name, parent, continent)
    areas = {6719: ("Shadowmoon Valley", 0, 1158), 6720: ("Frostfire Ridge", 0, 1152),
             7078: ("Lunarfall", 6719, 1158), frostwall: ("Frostwall", 6720, 1152)}
    for i in (7085, 7086, 7211):
        areas[i] = ("Lunarfall", 7078, 1158)
    for i in (7096, 7103, 7210):
        areas[i] = ("Frostwall", frostwall, 1152)
    for i in (6772, 6922, 6796, 7760, 7173):
        areas[i] = (retail[i]["AreaName_lang"], 6719, 1158)
    for i in (6906, 7062):
        areas[i] = (retail[i]["AreaName_lang"], 6720, 1152)
    clash = [i for i in areas if not free(i, "areatable_dbc", area, "AreaTable")]
    assert not clash, f"area ids already used in Esteria: {clash}"

    zone_template, sub_template = area.rows[12], area.rows[9]  # Elwynn Forest, Northshire Valley
    bit = max(max(struct.unpack_from("<i", r, 12)[0] for r in d.rows.values()) for d in (area, server["AreaTable"])) + 1
    new_area = []
    for i, (name, parent, continent) in sorted(areas.items()):
        row = bytearray(zone_template if not parent else sub_template)
        struct.pack_into("<4I", row, 0, i, continent, parent, bit)
        bit += 1
        for f in AREA_STRINGS:
            struct.pack_into("<I", row, f * 4, 0)
        struct.pack_into("<I", row, 11 * 4, len(area.blob))
        area.blob += name.encode("utf-8") + b"\0"
        area.rows[i] = bytes(row)
        area.order.append(i)
        new_area.append(i)

    next_wma = max(max(wma.rows), max(server["WorldMapArea"].rows), max(sql_taken["worldmaparea_dbc"])) + 1
    tiles = {}
    art_tiles = {}
    for r in csv.DictReader((REF / "wago_UiMapArtTile.csv").open(encoding="utf-8")):
        if r["LayerIndex"] == "0":
            art_tiles.setdefault(int(r["UiMapArtID"]), {})[int(r["RowIndex"]) * 4 + int(r["ColIndex"]) + 1] = int(r["FileDataID"])
    new_wma = []
    for map_id, (faction, tier, art) in MAPS.items():
        name = f"Garrison{faction}{tier}"
        min_x, min_y, max_x, max_y = BOUNDS[faction]
        row = bytearray(wma.size)
        struct.pack_into("<3I", row, 0, next_wma, map_id, 7078 if faction == "Lunarfall" else frostwall)
        struct.pack_into("<I", row, 12, len(wma.blob))
        wma.blob += name.encode() + b"\0"
        struct.pack_into("<4f", row, 16, max_y, min_y, max_x, min_x)  # LocLeft, LocRight, LocTop, LocBottom
        struct.pack_into("<3i", row, 32, -1, 0, 0)  # DisplayMapID, DefaultDungeonFloor, ParentWorldMapID
        wma.rows[next_wma] = bytes(row)
        wma.order.append(next_wma)
        new_wma.append(next_wma)
        next_wma += 1
        assert sorted(art_tiles[art]) == list(range(1, 13)), f"art {art} is not 4x3"
        tiles[name] = art_tiles[art]  # tile number 1..12 -> FileDataID

    missing = [f for parts in tiles.values() for f in parts.values() if not (CACHE / f"{f}.bin").exists()]
    if missing:
        work = Path(ra.tempfile.mkdtemp(prefix="garrison_tiles_"))
        (work / "Local.ini").write_text(f"mode=local\npath={ra.INSTALL.as_posix()}\nproduct=wow\nlocale={ra.LOCALE}\n")
        failed = ra.extract(work, "Local.ini", [f"retail/{f}.bin" for f in missing], CACHE)
        if failed:
            failed = ra.extract(ra.ONLINE_DIR, "RetailCasc.ini", failed, CACHE)
        assert not failed, f"map tiles unavailable: {failed}"

    out = Path(a.client) / "Data" / b.PATCH
    handle = storm.open_archive(out)
    try:
        files = {f"DBFilesClient\\{n}.dbc": storm.read(handle, f"DBFilesClient\\{n}.dbc")
                 for n in ("Map", "CreatureDisplayInfo", "CreatureModelData", "GameObjectDisplayInfo")}
    finally:
        storm.dll.SFileCloseArchive(handle)
    # The handoff's Map rows were cloned from The Stockade (AreaTableID 717); with no server terrain the zone falls back to
    # it, so chat joined "General - The Stockade". Point each tier map at its own zone (Map.dbc field 22).
    zone_of = {m: (7078 if faction == "Lunarfall" else frostwall) for m, (faction, _, _) in MAPS.items()}
    map_dbc = bytearray(files["DBFilesClient\\Map.dbc"])
    count, _, size, _ = struct.unpack_from("<4I", map_dbc, 4)
    for i in range(count):
        row = 20 + i * size
        if struct.unpack_from("<I", map_dbc, row)[0] in zone_of:
            struct.pack_into("<I", map_dbc, row + 22 * 4, zone_of[struct.unpack_from("<I", map_dbc, row)[0]])
    files["DBFilesClient\\Map.dbc"] = bytes(map_dbc)
    files["DBFilesClient\\AreaTable.dbc"] = area.bytes()
    files["DBFilesClient\\WorldMapArea.dbc"] = wma.bytes()
    # This client draws world maps from 1024 px DXT tiles with mips (its HD maps, patch-M; housing's make_worldmap.py):
    # 256 px retail tiles without that did not draw. Compose each art's 4x3 tiles, scale by 4, cut 1024 px tiles.
    from PIL import Image
    sys.path.insert(0, r"R:\Users\Zach\Documents\GitHub\wowdecomp\docs\housing\tools\ui")
    from make_worldmap import blp
    for base, parts in tiles.items():
        canvas = Image.new("RGB", (1024, 768))
        for n, fdid in parts.items():
            canvas.paste(Image.open(CACHE / f"{fdid}.bin").convert("RGB"), (((n - 1) % 4) * 256, ((n - 1) // 4) * 256))
        # Past the shown 1002x668 the map is transparent, as housing's are: opaque, it drew a black bar under the map.
        shown = canvas.crop((0, 0, 1002, 668)).resize((4008, 2672), Image.LANCZOS)
        canvas = Image.new("RGBA", (4096, 3072), (0, 0, 0, 0))
        canvas.paste(shown, (0, 0))
        for n in range(1, 13):
            x, y = ((n - 1) % 4) * 1024, ((n - 1) // 4) * 1024
            files[f"Interface\\WorldMap\\{base}\\{base}{n}.blp"] = blp(canvas.crop((x, y, x + 1024, y + 1024)))
    out.unlink()
    storm.create_archive(out, files)
    handle = storm.open_archive(out)
    try:
        for name, data in files.items():
            assert storm.read(handle, name) == data, f"read-back mismatch {name}"
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"{out}: +{len(new_area)} AreaTable rows {new_area} (Frostwall {frostwall}), +{len(new_wma)} WorldMapArea {new_wma}, {12 * len(tiles)} map tiles")

    parts = ["-- Generated by modules/mod-esteria-garrison/tools/build_world_map.py: the garrison client patch's new",
             "-- AreaTable and WorldMapArea rows for the server. Every ID was free in the client DBCs, server DBCs and these tables.", ""]
    for table, dbc, ids in (("areatable_dbc", area, new_area), ("worldmaparea_dbc", wma, new_wma)):
        cols = [(c, t) for c, t in b.mysql(f"SELECT column_name, column_type FROM information_schema.columns WHERE "
                                            f"table_schema='{a.live}' AND table_name='{table}' ORDER BY ordinal_position")]
        assert len(cols) == dbc.fields, f"{table}: {len(cols)} columns, {dbc.fields} fields"
        parts += [b.sql_rows(table, cols, dbc, ids), ""]
    for zone in sorted(set(zone_of.values())):
        maps = ", ".join(str(m) for m, z in sorted(zone_of.items()) if z == zone)
        parts.append(f"UPDATE map_dbc SET AreaTableID = {zone} WHERE ID IN ({maps});")
    SQL_OUT.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    print("wrote", SQL_OUT)


if __name__ == "__main__":
    main()
