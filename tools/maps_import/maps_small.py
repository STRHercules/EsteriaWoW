"""Island-Project, SceneGaming and Morza/CustomMaps: client assets + DBC rows + server SQL/data."""

from __future__ import annotations

import struct
from pathlib import Path

import closure
import dbcdelta
import lib
import sqlgen
from ctx import SRC, Ctx, Tele, closure_report, filter_assets
from dbcdelta import spec_from_src

ISLAND_MAP, ISLAND_AREA, ISLAND_WMA = 1405, 30010, 1100
SCENE_MAPS = {725: 1410, 726: 1411, 727: 1412}                       # TheForestArena, TheBlackForest, TheCityofKarma
SCENE_AREAS = {5000: 30001, 5001: 30002, 5200: 30003, 5300: 30004, 5301: 30005, 5302: 30006, 5303: 30007}
SCENE_WSL = {1800: 1801, 1801: 1802, 1802: 1803}
MORZA_MAP, MORZA_WSL_OLD, MORZA_WSL = 5000, 1721, 1800
CREATURE_GUID0 = 9700001
GO_GUID0 = 9700001
TELE_ID0 = 2000


def read_pack(mpq: Path) -> dict[str, bytes]:
    h = lib.open_ro(mpq)
    out = {}
    for n, _ in lib.list_archive(h):
        if n.startswith("("):
            continue
        b = lib.read_member(h, n)
        if b is not None:
            out[n.replace("/", "\\")] = b
    return out


def trs_lines(pack: dict[str, bytes], dirname: str) -> list[str]:
    """Lines for one minimap directory out of a pack's md5translate.trs (the pack's full file is never installed)."""
    blob = next((v for k, v in pack.items() if k.lower().replace("/", "\\") == "textures\minimap\md5translate.trs"), b"")
    keep = [f"dir: {dirname}"]
    for line in blob.decode("utf-8", "replace").splitlines():
        if line.lower().startswith(dirname.lower() + "\\"):
            keep.append(line.strip())
    return keep if len(keep) > 1 else []


def _sound_ok(ctx: Ctx, table: str, rid: int) -> bool:
    return rid == 0 or (table in ctx.client and ctx.client[table].get(rid) is not None)


def make_area(ctx: Ctx, src: lib.Dbc, row: list[int], new_id: int, new_map: int, parent: int) -> list:
    """Re-id an AreaTable row, keep only sound/light references that exist in Esteria's tables."""
    sp = spec_from_src("AreaTable", src, row)
    sp[0], sp[1], sp[2] = new_id, new_map, parent
    old_bit = row[3]
    if old_bit == 0 or old_bit in ctx.used_bits:
        sp[3] = ctx.new_bit() if old_bit else 0
    else:
        sp[3] = old_bit
        ctx.used_bits.add(old_bit)
    for col, table in ((5, "SoundProviderPreferences"), (6, "SoundProviderPreferences"), (7, "SoundAmbience"),
                       (8, "ZoneMusic"), (9, "ZoneIntroMusicTable")):
        if not _sound_ok(ctx, table, sp[col]):
            sp[col] = 0
    sp[35] = 0  # Light rows are per-map; custom ones are not imported for these maps
    return sp


# ------------------------------------------------------------------------------------------ Island

def do_island(ctx: Ctx) -> None:
    root = SRC / "Island-Project-main"
    pack = read_pack(root / "Patch-I.mpq")
    src_map = lib.Dbc((root / "DBFilesClient" / "Map.dbc").read_bytes())
    src_wma = lib.Dbc((root / "DBFilesClient" / "WorldMapArea.dbc").read_bytes())
    scene_area = lib.Dbc((SRC / "SceneGaming" / "Scene Gaming" / "patchfiles" / "DBFilesClient" / "AreaTable.dbc").read_bytes())

    # AreaTable: Island ships no AreaTable; its ADTs use IDs (5006-5018) from the source server that collide with
    # Morza's. Collapse them all into one new zone, cloned from a plain outdoor row.
    tmpl = scene_area.get(5000)
    sp = make_area(ctx, scene_area, tmpl, ISLAND_AREA, ISLAND_MAP, 0)
    sp[11] = "Experience Island"
    ctx.delta.add("AreaTable", sp)

    row = src_map.get(ISLAND_MAP)
    sp = spec_from_src("Map", src_map, row)
    sp[22] = ISLAND_AREA
    if not ctx.exists_in("LoadingScreens", sp[57]):
        sp[57] = 0
    ctx.delta.add("Map", sp)

    wrow = src_wma.get(610)
    sp = spec_from_src("WorldMapArea", src_wma, wrow)
    sp[0], sp[2], sp[10] = ISLAND_WMA, ISLAND_AREA, 0
    ctx.delta.add("WorldMapArea", sp)

    adts = []
    for p in list(pack):
        if p.lower().endswith(".adt"):
            pack[p] = closure.patch_adt_areas(pack[p], lambda a: ISLAND_AREA if a else 0)
            adts.append((p, pack[p]))
    filter_assets(ctx, "Island", pack, always_ship_prefixes=("world/maps/expisland/",))
    closure_report(ctx, "Island", adts)
    ctx.trs_lines += trs_lines(pack, "expisland")
    ctx.teles.append(Tele("expisland", ISLAND_MAP, 6006.94, 1534.93, 34.5823, 0, "Island-Project README"))


# ------------------------------------------------------------------------------------------ Scene

def _f(v: int) -> float:
    return lib.u2f(v)


def do_scene(ctx: Ctx) -> None:
    root = SRC / "SceneGaming" / "Scene Gaming"
    dbc = root / "patchfiles" / "DBFilesClient"
    pack = read_pack(root / "patch-4.MPQ")
    s_map = lib.Dbc((dbc / "Map.dbc").read_bytes())
    s_area = lib.Dbc((dbc / "AreaTable.dbc").read_bytes())
    s_wsl = lib.Dbc((dbc / "WorldSafeLocs.dbc").read_bytes())
    s_trg = lib.Dbc((dbc / "AreaTrigger.dbc").read_bytes())

    for old, new in SCENE_MAPS.items():
        sp = spec_from_src("Map", s_map, s_map.get(old))
        sp[0] = new
        sp[22] = SCENE_AREAS[sp[22]]
        if not ctx.exists_in("LoadingScreens", sp[57]):
            sp[57] = 0
        ctx.delta.add("Map", sp)
    for old, new in SCENE_AREAS.items():
        r = s_area.get(old)
        parent = SCENE_AREAS.get(r[2], 0)
        ctx.delta.add("AreaTable", make_area(ctx, s_area, r, new, SCENE_MAPS[r[1]], parent))
    gy = []
    for old, new in SCENE_WSL.items():
        r = s_wsl.get(old)
        sp = spec_from_src("WorldSafeLocs", s_wsl, r)
        sp[0], sp[1] = new, SCENE_MAPS[r[1]]
        ctx.delta.add("WorldSafeLocs", sp)
        gy.append((new, sp[1], _f(r[2]), _f(r[3]), _f(r[4]), sp[5]))
    t = s_trg.get(6000)
    sp = spec_from_src("AreaTrigger", s_trg, t)
    sp[1] = SCENE_MAPS[t[1]]
    ctx.delta.add("AreaTrigger", sp)

    adts = []
    for p in list(pack):
        if p.lower().endswith(".adt"):
            pack[p] = closure.patch_adt_areas(pack[p], lambda a: SCENE_AREAS.get(a, a))
            adts.append((p, pack[p]))
    filter_assets(ctx, "Scene", pack, always_ship_prefixes=("world/maps/",))
    closure_report(ctx, "Scene", adts)

    # --- server SQL
    sql = ctx.sql.setdefault("scenegaming_world.sql", [])
    sql.append("-- SceneGaming (maps 1410-1412, renumbered from 725-727; AreaTable ids 30001-30007; graveyards 1801-1803)")
    sql.append("DELETE FROM `game_graveyard` WHERE `ID` IN (1801, 1802, 1803);")
    sql.append(sqlgen.emit("game_graveyard", [{"ID": i, "Map": m, "x": x, "y": y, "z": z, "Comment": f"SceneGaming {n}"}
                                              for i, m, x, y, z, n in gy]))
    sql.append("DELETE FROM `graveyard_zone` WHERE `ID` IN (1801, 1802, 1803);")
    gz = [(1801, 5000), (1801, 5001), (1802, 5200), (1803, 5300), (1803, 5301), (1803, 5302), (1803, 5303)]
    sql.append(sqlgen.emit("graveyard_zone", [{"ID": g, "GhostZone": SCENE_AREAS[z], "Faction": 0, "Comment": f"SceneGaming {z}"}
                                              for g, z in gz]))
    # one Spirit Healer (stock 6491) per map at its graveyard, from the pack's creature.sql positions
    spawns = [(1410, -1861.11, -1904.55, 0.0000458434, 3.13538), (1411, -2010.52, -1990.85, 0.000112, 1.88811),
              (1412, 11431.5, 11667.2, 0.000765, 3.34991)]
    rows = [{"guid": CREATURE_GUID0 + 900 + i, "id": 6491, "map": m, "zoneId": 0, "areaId": 0, "spawnMask": 1, "phaseMask": 1,
             "equipment_id": 0, "position_x": x, "position_y": y, "position_z": z, "orientation": o, "spawntimesecs": 300,
             "wander_distance": 0, "currentwaypoint": 0, "curhealth": 4121, "curmana": 0, "MovementType": 0, "npcflag": 0,
             "unit_flags": 0, "dynamicflags": 0, "ScriptName": "", "VerifiedBuild": 0} for i, (m, x, y, z, o) in enumerate(spawns)]
    sql.append(f"DELETE FROM `creature` WHERE `guid` BETWEEN {CREATURE_GUID0 + 900} AND {CREATURE_GUID0 + 902};")
    sql.append(sqlgen.emit("creature", rows))
    names = {1410: "forestarena", 1411: "blackforest", 1412: "cityofkarma"}
    for (i, m, x, y, z, _n) in gy:
        ctx.teles.append(Tele(names[m], m, x, y, z + 1.0, 0, "graveyard position from WorldSafeLocs"))


# ------------------------------------------------------------------------------------------ Morza

def do_morza_client(ctx: Ctx) -> None:
    root = SRC / "Morza-Island-Araxia-Server-main"
    dbc = root / "Patch-Z-(MPQ)" / "DBFilesClient"
    pack = read_pack(root / "patch-Z.mpq")
    m_map = lib.Dbc((dbc / "Map.dbc").read_bytes())
    m_area = lib.Dbc((dbc / "AreaTable.dbc").read_bytes())
    m_wsl = lib.Dbc((dbc / "WorldSafeLocs.dbc").read_bytes())
    m_snd = lib.Dbc((dbc / "SoundEntries.dbc").read_bytes())

    sp = spec_from_src("Map", m_map, m_map.get(MORZA_MAP))
    if not ctx.exists_in("LoadingScreens", sp[57]):
        ctx.log(f"[Morza] Map LoadingScreenID {sp[57]} is not in Esteria's LoadingScreens; set to 0")
        sp[57] = 0
    ctx.delta.add("Map", sp)

    base_ids = ctx.client["AreaTable"].ids() | ctx.server["AreaTable"].ids()
    new_rows = [r for r in m_area.rows if r[0] not in base_ids]
    for r in new_rows:
        ctx.delta.add("AreaTable", make_area(ctx, m_area, r, r[0], MORZA_MAP, r[2]))
    ctx.log(f"[Morza] AreaTable: {len(new_rows)} new rows keep their source ids (4988-5012 range)")

    r = m_wsl.get(MORZA_WSL_OLD)
    sp = spec_from_src("WorldSafeLocs", m_wsl, r)
    sp[0] = MORZA_WSL
    ctx.delta.add("WorldSafeLocs", sp)
    ctx.sql.setdefault("morza_world.sql", [])
    gy = (MORZA_WSL, 5000, _f(r[2]), _f(r[3]), _f(r[4]))
    ctx.sql["morza_world.sql"] += [
        f"DELETE FROM `game_graveyard` WHERE `ID` = {MORZA_WSL};",
        sqlgen.emit("game_graveyard", [{"ID": gy[0], "Map": gy[1], "x": gy[2], "y": gy[3], "z": gy[4], "Comment": "Morza Island GY"}]),
        f"DELETE FROM `graveyard_zone` WHERE `ID` = {MORZA_WSL};",
        sqlgen.emit("graveyard_zone", [{"ID": MORZA_WSL, "GhostZone": 4988, "Faction": 0, "Comment": "Morza Island"}]),
    ]

    # concert songs: only SoundEntries rows whose ID Esteria does not have
    base_snd = ctx.client["SoundEntries"]
    new_snd = [x for x in m_snd.rows if x[0] not in base_snd.ids()]
    for x in new_snd:
        ctx.delta.add("SoundEntries", spec_from_src("SoundEntries", m_snd, x))
    clash = [x[0] for x in m_snd.rows if x[0] in base_snd.ids() and m_snd.text(x[2]) != base_snd.text(base_snd.get(x[0])[2])
             and m_snd.text(x[2]) and "Concert" in m_snd.text(x[2])]
    ctx.log(f"[Morza] SoundEntries: {len(new_snd)} new rows; same-id-different-name concert rows: {clash}")

    known = {sp[0] for sp in ctx.delta.rows["AreaTable"] if sp[1] == MORZA_MAP}
    stray: dict[int, int] = {}

    def fix_area(a: int) -> int:
        # chunks that name AreaTable ids the pack's own DBC never defined would show unrelated Esteria areas
        if a == 0 or a < 4000 or a in known:
            return a
        stray[a] = stray.get(a, 0) + 1
        return 4988

    for p in list(pack):
        if p.lower().endswith(".adt"):
            pack[p] = closure.patch_adt_areas(pack[p], fix_area)
    ctx.log(f"[Morza] ADT chunks with undefined area ids remapped to Morza Island (4988): {stray}")
    adts = [(p, d) for p, d in pack.items() if p.lower().endswith(".adt")]
    filter_assets(ctx, "Morza", pack, always_ship_prefixes=("world/maps/custommaps/", "sound/concert/"))
    closure_report(ctx, "Morza", adts)
    ctx.trs_lines += trs_lines(pack, "CustomMaps")
    ctx.teles.append(Tele("morza", MORZA_MAP, -13950, 2877, 9, 0, "Morza README"))
    ctx.teles.append(Tele("valleyofbetrayal", MORZA_MAP, 10461, -9574, 22, 0, "Morza README (WIP area)"))

    # prebuilt server data shipped with the pack
    side = root / "Add To Server Side"
    for p in side.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".map", ".mmap", ".mmtile", ".vmtile", ".vmtree", ".vmo"):
            ctx.server_files[f"data/{p.parent.name.lower()}/{p.name}"] = p.read_bytes()
    for p in (root / "Lua Scripts").glob("*.lua"):
        ctx.server_files[f"lua_scripts/morza/{p.name}"] = p.read_bytes()
