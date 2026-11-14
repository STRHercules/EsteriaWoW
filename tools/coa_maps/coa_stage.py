"""CoA custom maps -> Esteria, phase 1: terrain, client assets, DBC rows, server DBCs, teleports, graveyards.

Source: the CoA client (G:\\CoAClient\\Client) and CoA's live world dump loaded as `coa_live_world`.
Baselines: the Dev client's effective files (Esteria) and the Live worldserver's DBCs.
Rules (user, 2026-11-12): keep CoA ids where Esteria has them free, remap only collisions, never replace an Esteria
row or file. CoA's map-0 zones (Druk'Thar, Pale Reach, Shadewell) become the standalone map NEW0_MAP.

Writes only under G:\\CoAMapsPort\\stage. Never touches the client folders, the database or containers.

    python -I coa_stage.py
"""

from __future__ import annotations

import collections
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "maps_import"))
import closure  # noqa: E402
import ctx as C  # noqa: E402
import dbcdelta  # noqa: E402
import lib  # noqa: E402
import sqlgen  # noqa: E402
from dbcdelta import spec_from_src  # noqa: E402

WORK = Path(r"G:\CoAMapsPort")
STAGE = WORK / "stage"
COA_DATA = Path(r"G:\CoAClient\Client\Data")
COA_DB = "coa_live_world"

MAPS = [178, 535, 666, 800, 806, 808, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 900, 901, 904,
        907, 908, 909, 910, 921, 927, 928, 929, 930, 933, 934, 936, 937, 938, 939, 940, 941, 951, 959, 960, 961, 967,
        972, 1171, 1199, 1200, 1201, 1758, 1760, 1761, 1762, 1763, 1764, 1765, 1766, 1767, 1768, 1769, 1770, 1771]
NEW0_MAP, NEW0_DIR, NEW0_NAME, NEW0_TEMPLATE = 1820, "DrukThar", "Druk'Thar", 959
NEW0_ROOTS = (10292, 10302, 10305)          # Druk'Thar, Pale Reach, Shadewell (CoA AreaTable)
NEW0_EXTRA = set(range(10195, 10204))      # CoA's reworked Northshire/Coldridge pieces inside the same tiles
AREA_BASE, WSL_BASE, TRIGGER_BASE, LIGHT_BASE, PARAMS_BASE = 32000, 3000, 9000, 6000, 3000
TELE_BASE = 2300
DBC_ARCHIVE = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZZZZCoAMapsDbc.MPQ"   # 27 Z: after the maps-import DBC archive (26 Z)
ASSET_ARCHIVE = "Patch-ZzzzzzzzzzCoAMaps-{:03d}.MPQ"
ARCHIVE_LIMIT = 1_500_000_000
TRS = "Textures\\Minimap\\md5translate.trs"
FIX_STR = {"LiquidType": [1, 15, 16, 17, 18, 19, 20]}

C.CLIENT_TABLES += ["LiquidType"]
C.SERVER_TABLES += ["LiquidType"]
dbcdelta.STR_COLS.update(FIX_STR)
C.STAGE = STAGE                              # filter_assets writes its kept-existing reports here


def coa_sql(sql: str) -> list[list[str]]:
    return [l.split("\t") for l in sqlgen.mysql(sql, COA_DB).splitlines() if l and not l.startswith("ERROR")]


class Port:
    def __init__(self) -> None:
        scratch = WORK / "scratch"
        self.ctx = C.build_ctx(scratch)
        self.coa = lib.ClientFiles(COA_DATA, scratch).open()
        self.src: dict[str, lib.Dbc] = {}
        self.area: dict[int, int] = {0: 0}            # CoA area id -> Esteria id
        self.bits: dict[int, int] = {0: 0}
        self.maps: dict[int, int] = {m: m for m in MAPS}
        self.maps[0] = NEW0_MAP                       # only for rows taken from the map-0 zones
        self.wsl: dict[int, int] = {}
        self.trigger: dict[int, int] = {}
        self.light: dict[int, int] = {}
        self.params: dict[int, int] = {}
        # path -> bytes, or a source read when needed: ("adt", coa key) | ("coa", coa key) | ("any", path).
        # Holding every file's bytes at once ran the PC out of memory (62k files, >10 GB).
        self.pack: dict[str, object] = {}
        self.adts: list[str] = []
        self.ship: list[str] = []
        self.sounds: list[str] = []
        self.skies: list[str] = []
        self.ids_report: dict[str, dict] = collections.defaultdict(dict)
        self.dirs_done: set[str] = set()
        trs = (self.ctx.cf.read(TRS) or b"").decode("utf-8", "replace")
        self.est_trs_dirs = {l.split(":", 1)[1].strip().lower() for l in trs.splitlines() if l.lower().startswith("dir:")}

    # ------------------------------------------------------------------------------------------- helpers
    def read_any(self, p: str) -> bytes | None:
        """CoA's file, else Esteria's (CoA streams many retail-era models from outside its MPQs; Esteria's client
        ships them). Probes unlisted members too. Empty files count as missing (CoA has 0-byte M2s)."""
        for cf in (self.coa, self.ctx.cf):
            b = cf.read(p)
            if not b:
                key = lib.winkey(p)
                for _path, h in reversed(cf.handles):
                    b = lib.read_member(h, key)
                    if b:
                        break
            if b:
                return b
        return None

    def t(self, name: str) -> lib.Dbc:
        if name not in self.src:
            self.src[name] = lib.Dbc(self.coa.read(f"DBFilesClient\\{name}.dbc"))
            self.src[name].idx = {r[0]: r for r in self.src[name].rows}
        return self.src[name]

    def row(self, name: str, rid: int):
        return self.t(name).idx.get(rid)

    def log(self, msg: str) -> None:
        self.ctx.log(msg)

    def place(self, table: str, row, start: int, fix=None) -> int:
        """Esteria id for a CoA row: same id when Esteria's row is identical, CoA's id when free, else a new id."""
        ctx = self.ctx
        spec = spec_from_src(table, self.t(table), row)
        if fix:
            fix(spec)
        sid = row[0]
        for sp in ctx.delta.rows.get(table, []):       # already placed in this run
            if sp[1:] == spec[1:] and self.ids_report[table].get(sid) == sp[0]:
                return sp[0]
        base = ctx.client.get(table)
        cur = base.idx.get(sid) if base is not None and hasattr(base, "idx") else (base.get(sid) if base else None)
        if cur is not None and spec_from_src(table, base, cur)[1:] == spec[1:]:
            return sid
        used = ctx.used_ids(table)
        new = sid if (cur is None and sid not in used) else next(i for i in range(start, 10**8) if i not in used)
        spec[0] = new
        ctx.delta.add(table, spec)
        self.ids_report[table][sid] = new
        return new

    def sound(self, sid: int) -> int:
        if not sid:
            return 0
        if self.ctx.exists_in("SoundEntries", sid):
            return sid                                   # stock id: Esteria's own sound
        r = self.row("SoundEntries", sid)
        if r is None:
            return 0
        se = self.t("SoundEntries")
        d = se.text(r[23])
        self.sounds += [(d + "\\" + se.text(r[c])) if d else se.text(r[c]) for c in range(3, 13) if se.text(r[c])]
        return self.place("SoundEntries", r, 70000)

    def chain(self, table: str, rid: int, start: int, cols: list[int]) -> int:
        if not rid:
            return 0
        if self.ctx.exists_in(table, rid):
            return rid
        r = self.row(table, rid)
        if r is None:
            return 0
        return self.place(table, r, start, fix=lambda s: [s.__setitem__(c, self.sound(s[c])) for c in cols])

    # ------------------------------------------------------------------------------------------- areas
    def area_id(self, a: int, cont: int) -> int:
        """Esteria id for a CoA area referenced on map `cont` (CoA continent). Imports the row (and parents) when
        Esteria lacks it or names that id differently."""
        if a in self.area:
            return self.area[a]
        r = self.row("AreaTable", a)
        est = self.ctx.client["AreaTable"].get(a)
        if r is None:
            self.area[a] = a if est is not None else 0
            return self.area[a]
        at = self.t("AreaTable")
        if est is not None and lib.best_loc(self.ctx.client["AreaTable"], est, 11) == lib.best_loc(at, r, 11) \
                and (r[1] not in self.maps or r[1] == 0):
            self.area[a] = a                             # stock area Esteria has too (reused by CoA's copies)
            return a
        used = self.ctx.used_ids("AreaTable") | set(self.area.values())
        new = a if a not in used else next(i for i in range(AREA_BASE, 10**7) if i not in used)
        self.area[a] = new
        parent = self.area_id(r[2], r[1]) if r[2] else 0
        if r[3] not in self.bits:
            self.bits[r[3]] = self.ctx.new_bit()
        sp = spec_from_src("AreaTable", at, r)
        sp[0], sp[1], sp[2], sp[3] = new, self.maps.get(r[1], r[1]), parent, self.bits[r[3]]
        for c in (5, 6):
            if sp[c] and not self.ctx.exists_in("SoundProviderPreferences", sp[c]):
                sp[c] = 0
        sp[7] = self.chain("SoundAmbience", r[7], 1000, [1, 2])
        sp[8] = self.chain("ZoneMusic", r[8], 1000, [6, 7])
        sp[9] = self.chain("ZoneIntroMusicTable", r[9], 1000, [2])
        for c in range(29, 33):
            sp[c] = self.liquid(r[c])
        sp[35] = self.light.get(r[35], 0) if r[35] else 0
        self.ctx.delta.add("AreaTable", sp)
        return new

    def liquid(self, lid: int) -> int:
        if not lid or self.ctx.exists_in("LiquidType", lid):
            return lid
        r = self.row("LiquidType", lid)
        return self.place("LiquidType", r, 200) if r else 0

    # ------------------------------------------------------------------------------------------- lights
    def lights(self, src_map: int, new_map: int, keep=None) -> None:
        ib, fb = self.t("LightIntBand").idx, self.t("LightFloatBand").idx
        cib, cfb = self.ctx.client["LightIntBand"], self.ctx.client["LightFloatBand"]
        for r in [r for r in self.t("Light").rows if r[1] == src_map and (keep is None or keep(r))]:
            spec = list(r)
            spec[1] = new_map
            for i in range(7, 15):
                p = r[i]
                if p and p not in self.params:
                    pr = self.row("LightParams", p)
                    if pr is None:
                        self.params[p] = 0
                    else:
                        def pfix(s, pr=pr):
                            s[2] = self.sky(pr[2])
                        new = self.place("LightParams", pr, PARAMS_BASE, fix=pfix)
                        self.params[p] = new
                        if new != p or not self.ctx.exists_in("LightParams", p):
                            for k in range(18):
                                s_id, d_id = p * 18 - 17 + k, new * 18 - 17 + k
                                if ib.get(s_id) and cib.get(d_id) is None and d_id not in self.ctx.delta.ids("LightIntBand"):
                                    self.ctx.delta.add("LightIntBand", [d_id] + list(ib[s_id][1:]))
                            for k in range(6):
                                s_id, d_id = p * 6 - 5 + k, new * 6 - 5 + k
                                if fb.get(s_id) and cfb.get(d_id) is None and d_id not in self.ctx.delta.ids("LightFloatBand"):
                                    self.ctx.delta.add("LightFloatBand", [d_id] + list(fb[s_id][1:]))
                spec[i] = self.params.get(p, 0) if p else 0
            used = self.ctx.used_ids("Light")
            nid = r[0] if r[0] not in used else next(i for i in range(LIGHT_BASE, 10**7) if i not in used)
            spec[0] = nid
            self.light[r[0]] = nid
            self.ctx.delta.add("Light", spec)

    def sky(self, sid: int) -> int:
        if not sid:
            return 0
        r = self.row("LightSkybox", sid)
        if r is None:
            return 0
        name = self.t("LightSkybox").text(r[1])
        m2 = name.rsplit(".", 1)[0] + ".m2" if name.lower().endswith(".mdx") else name
        if m2 and not self.ctx.cf.probe(m2):
            if not self.read_any(m2):
                return 0    # model in neither client (CoA streams it): a skybox that cannot load crashed map 907
            self.skies.append(m2)
        return self.place("LightSkybox", r, 700)

    # ------------------------------------------------------------------------------------------- one map
    def do_map(self, src: int, new: int, new_dir: str, tiles: set[str] | None = None, area_ok=None) -> None:
        mrow = self.row("Map", src if src else NEW0_TEMPLATE)
        # CoA's Map.dbc stores "Azeroth" at string offset 0, which reads back as empty
        old_dir = self.t("Map").text(self.row("Map", src)[1]) if src else "Azeroth"
        self.lights(src, new, keep=None if src else (lambda r: not self.ctx.exists_in("Light", r[0])))
        # terrain
        prefix = f"world/maps/{old_dir.lower()}/"
        shared = old_dir.lower() in self.dirs_done and src != 0      # 901/910 share one terrain folder
        self.dirs_done.add(old_dir.lower())
        files = [] if shared else [k for k in self.coa.index if k.startswith(prefix)]
        chunk_areas: set[int] = set()
        adt_n = 0
        for k in files:
            name = self.coa.names[k].replace("/", "\\").split("\\")[-1]
            if tiles is not None and k.endswith(".adt") and name.lower() not in tiles:
                continue
            if tiles is not None and not k.endswith(".adt"):
                continue                                   # the copy gets its own WDT
            if k.endswith(".adt"):
                chunk_areas |= closure.adt_area_ids(self.coa.read(k))
                self.adts.append(k)
                adt_n += 1
            new_name = name if src else name.replace(old_dir, new_dir, 1) if name.startswith(old_dir) else \
                new_dir + name[len(old_dir):]
            self.pack[f"World\\Maps\\{new_dir}\\{new_name}"] = ("adt" if k.endswith(".adt") else "coa", k)
        for a in sorted(chunk_areas):
            if area_ok is None or area_ok(a):
                self.area_id(a, src)
        zone_rows = [r[0] for r in self.t("AreaTable").rows if r[1] == src and (area_ok is None or area_ok(r[0]))]
        for a in zone_rows:
            self.area_id(a, src)
        if src == 0:
            self.pack[f"World\\Maps\\{new_dir}\\{new_dir}.wdt"] = make_wdt(self.coa.read("World\\Maps\\Azeroth\\Azeroth.wdt"), tiles)
        # map row
        ls = self.row("LoadingScreens", mrow[57]) if mrow[57] else None
        ls_new = self.place("LoadingScreens", ls, 300) if ls else 0
        if ls:
            lp = self.t("LoadingScreens").text(ls[2])
            for p in (lp, lp.replace(".blp", "WIDE.blp").replace(".BLP", "WIDE.BLP")):
                b = self.coa.read(p)
                if b is not None:
                    self.pack[p] = b
        sp = spec_from_src("Map", self.t("Map"), mrow)
        sp[0], sp[1] = new, new_dir
        if src == 0:
            sp[5] = NEW0_NAME
        sp[22] = self.area_id(mrow[22], src) if mrow[22] else 0
        if src == 0:
            sp[22] = self.area[NEW0_ROOTS[0]]
        sp[57] = ls_new
        sp[59] = self.maps.get(mrow[59], mrow[59]) if mrow[59] not in (0, 0xFFFFFFFF) else mrow[59]
        if self.ctx.client["Map"].get(new) is not None:
            raise RuntimeError(f"map id {new} is taken in Esteria")
        self.ctx.delta.add("Map", sp)
        # world map, POIs, safe locations, triggers
        self.world_map(src, new, area_ok)
        for r in [r for r in self.t("WorldSafeLocs").rows if r[1] == src and (src or self.in_tiles(r, tiles))]:
            sp = spec_from_src("WorldSafeLocs", self.t("WorldSafeLocs"), r)
            sp[1] = new
            used = self.ctx.used_ids("WorldSafeLocs")
            if sp[0] in used:
                sp[0] = next(i for i in range(WSL_BASE, 10**7) if i not in used)
            self.wsl[r[0]] = sp[0]
            self.ctx.delta.add("WorldSafeLocs", sp)
        for r in [r for r in self.t("AreaTrigger").rows if r[1] == src and (src or self.in_tiles(r, tiles))]:
            sp = list(r)
            sp[1] = new
            used = self.ctx.used_ids("AreaTrigger")
            if sp[0] in used:
                sp[0] = next(i for i in range(TRIGGER_BASE, 10**7) if i not in used)
            self.trigger[r[0]] = sp[0]
            self.ctx.delta.add("AreaTrigger", sp)
        # minimap
        trs = (self.coa.read(TRS) or b"").decode("utf-8", "replace")
        lines = [f"dir: {new_dir}"]
        if shared or new_dir.lower() in self.est_trs_dirs:
            trs = ""                                               # Esteria already lists this minimap folder
        for line in trs.splitlines():
            if line.lower().startswith(old_dir.lower() + "\\") and "\t" in line:
                k, v = line.strip().split("\t", 1)
                tile = k.split("\\", 1)[1]
                if tiles is not None:
                    xy = tile.lower().replace("map", "").replace(".blp", "")
                    if f"{old_dir.lower()}_{xy}.adt" not in tiles:
                        continue
                if self.coa.has("Textures\\Minimap\\" + v):
                    lines.append(f"{new_dir}\\{tile}\t{v}")
                    self.pack["Textures\\Minimap\\" + v] = ("coa", lib.norm("Textures/Minimap/" + v))
        if len(lines) > 1:
            self.ctx.trs_lines += lines
        self.log(f"[{new} {new_dir}] tiles {adt_n}, chunk areas {len(chunk_areas)}, zone rows {len(zone_rows)}, "
                 f"minimap {len(lines) - 1}")

    @staticmethod
    def in_tiles(r, tiles) -> bool:
        x, y = lib.u2f(r[2]), lib.u2f(r[3])
        tx, ty = int(32 - y / 533.33333), int(32 - x / 533.33333)
        return f"azeroth_{tx}_{ty}.adt" in tiles

    def world_map(self, src: int, new: int, area_ok) -> None:
        wma, wmo, poi = self.t("WorldMapArea"), self.t("WorldMapOverlay"), self.t("AreaPOI")
        rows = [r for r in wma.rows if r[1] == src and (area_ok is None or area_ok(r[2]))]
        wma_new = {}
        for r in sorted(rows, key=lambda r: r[10] != 0):
            used = self.ctx.used_ids("WorldMapArea")
            nid = r[0] if r[0] not in used else next(i for i in range(1200, 10**7) if i not in used)
            sp = spec_from_src("WorldMapArea", wma, r)
            sp[0], sp[1], sp[2] = nid, new, self.area.get(r[2], r[2])
            sp[8] = new if r[8] == src and src else r[8]
            sp[10] = wma_new.get(r[10], 0) if src == 0 else (wma_new.get(r[10], r[10]))
            wma_new[r[0]] = nid
            self.ctx.delta.add("WorldMapArea", sp)
            art = wma.text(r[3])
            for k in [k for k in self.coa.index if k.startswith(f"interface/worldmap/{art.lower()}/")]:
                self.pack[self.coa.names[k].replace("/", "\\")] = ("coa", k)
        for r in [r for r in wmo.rows if r[1] in wma_new]:
            sp = spec_from_src("WorldMapOverlay", wmo, r)
            used = self.ctx.used_ids("WorldMapOverlay")
            if sp[0] in used:
                sp[0] = next(i for i in range(4000, 10**7) if i not in used)
            sp[1] = wma_new[r[1]]
            for k in range(2, 6):
                sp[k] = self.area.get(r[k], r[k])
            self.ctx.delta.add("WorldMapOverlay", sp)
        for r in [r for r in poi.rows if r[15] == src and (area_ok is None or area_ok(r[17]))]:
            sp = spec_from_src("AreaPOI", poi, r)
            sp[15], sp[17] = new, self.area.get(r[17], r[17])
            used = self.ctx.used_ids("AreaPOI")
            if sp[0] in used:
                sp[0] = next(i for i in range(3000, 10**7) if i not in used)
            self.ctx.delta.add("AreaPOI", sp)

    # ------------------------------------------------------------------------------------------- map 0 zones
    def new0_tiles(self) -> tuple[set[str], set[int]]:
        at = self.t("AreaTable")
        kids = collections.defaultdict(list)
        for r in at.rows:
            kids[r[2]].append(r[0])
        family = set(NEW0_EXTRA)
        todo = list(NEW0_ROOTS)
        while todo:
            a = todo.pop()
            if a not in family:
                family.add(a)
                todo += kids[a]
        tiles = set()
        stock = {"common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq", "patch-2.mpq", "patch-3.mpq"}
        for k in self.coa.index:
            if k.startswith("world/maps/azeroth/") and k.endswith(".adt") and self.coa.provider(k).lower() not in stock:
                if closure.adt_area_ids(self.coa.read(k)) & family:
                    tiles.add(k.rsplit("/", 1)[1])
        return tiles, family

    # ------------------------------------------------------------------------------------------- server SQL
    def server_sql(self, family: set[int], tiles: set[str]) -> None:
        sql = self.ctx.sql.setdefault("coa_maps_world.sql", ["-- CoA custom maps: graveyards, area trigger teleports, teleports"])
        ids = ",".join(map(str, self.wsl)) or "0"
        gys = coa_sql(f"SELECT ID, Map, x, y, z, Comment FROM game_graveyard WHERE ID IN ({ids})")
        rows = [{"ID": self.wsl[int(g[0])], "Map": self.maps.get(int(g[1]), int(g[1])), "x": g[2], "y": g[3], "z": g[4],
                 "Comment": g[5]} for g in gys]
        if rows:
            sql.append(f"DELETE FROM `game_graveyard` WHERE `ID` IN ({','.join(str(r['ID']) for r in rows)});")
            sql.append(sqlgen.emit("game_graveyard", rows))
        gz = coa_sql(f"SELECT ID, GhostZone, Faction, Comment FROM graveyard_zone WHERE ID IN ({ids})")
        rows = [{"ID": self.wsl[int(g[0])], "GhostZone": self.area.get(int(g[1]), int(g[1])), "Faction": g[2], "Comment": g[3]}
                for g in gz]
        if rows:
            sql.append(f"DELETE FROM `graveyard_zone` WHERE `ID` IN ({','.join(str(r['ID']) for r in rows)});")
            sql.append(sqlgen.emit("graveyard_zone", rows))
        # area trigger teleports on the imported triggers, and stock-map triggers that lead into these maps
        maps = ",".join(map(str, MAPS))
        at = coa_sql(f"SELECT ID, Name, target_map, target_position_x, target_position_y, target_position_z, "
                     f"target_orientation FROM areatrigger_teleport WHERE ID IN ({','.join(map(str, self.trigger)) or 0}) "
                     f"OR target_map IN ({maps})")
        rows = []
        for a in at:
            tid = int(a[0])
            if tid not in self.trigger:                 # a trigger on another map that leads into these maps
                r = self.row("AreaTrigger", tid)
                if r is None:
                    continue
                est = self.ctx.client["AreaTrigger"].get(tid)
                if est is not None and list(est[1:]) == list(r[1:]):
                    self.trigger[tid] = tid             # same trigger in Esteria; its teleport row is checked below
                else:
                    sp = list(r)
                    used = self.ctx.used_ids("AreaTrigger")
                    if sp[0] in used:
                        sp[0] = next(i for i in range(TRIGGER_BASE, 10**7) if i not in used)
                    self.ctx.delta.add("AreaTrigger", sp)
                    self.trigger[tid] = sp[0]
            tm = int(a[2])
            if tm == 0 and self.in_tiles([0, 0, lib.f2u(float(a[3])), lib.f2u(float(a[4]))], tiles):
                tm = NEW0_MAP
            rows.append({"ID": self.trigger[tid], "Name": a[1], "target_map": self.maps.get(tm, tm) if tm else tm,
                         "target_position_x": a[3], "target_position_y": a[4], "target_position_z": a[5],
                         "target_orientation": a[6]})
        live = sqlgen.live_ids("areatrigger_teleport", "ID", [r["ID"] for r in rows])
        rows = [r for r in rows if r["ID"] not in live]
        if rows:
            sql.append(sqlgen.emit("areatrigger_teleport", rows))
        self.log(f"areatrigger_teleport rows: {len(rows)}")
        # dungeon/raid maps need instance_template, or the core rejects every teleport and trigger into them
        sql.append(f"INSERT IGNORE INTO `instance_template` (`map`, `parent`, `script`, `allowMount`) SELECT `map`, `parent`, "
                   f"`script`, `allowMount` FROM `{COA_DB}`.`instance_template` WHERE `map` IN ({maps});")
        # teleports: everything CoA has on these maps, plus the map-0 zone points
        tele = coa_sql(f"SELECT name, map, position_x, position_y, position_z, orientation FROM game_tele "
                       f"WHERE map IN ({maps}) OR map = 0 ORDER BY id")
        live_names = {n.lower() for n in sqlgen.mysql("SELECT name FROM game_tele;").split("\n")}
        out = []
        for name, m, x, y, z, o in tele:
            m = int(m)
            if m == 0:
                if not self.in_tiles([0, 0, lib.f2u(float(x)), lib.f2u(float(y))], tiles):
                    continue
                m = NEW0_MAP
            if name.lower() in live_names:
                continue
            live_names.add(name.lower())
            out.append(C.Tele(name, m, float(x), float(y), float(z), float(o), "CoA game_tele"))
        self.ctx.teles = out
        self.log(f"teleports: {len(out)}")

    # ------------------------------------------------------------------------------------------- lazy files
    def resolve(self, v) -> bytes | None:
        if isinstance(v, (bytes, bytearray)):
            return bytes(v)
        kind, key = v
        if kind == "adt":
            return closure.patch_adt_areas(self.coa.read(key), lambda a: self.area.get(a, a))
        if kind == "coa":
            return self.coa.read(key)
        return self.read_any(key)

    def closure(self) -> tuple[set[str], set[str]]:
        """closure.compute without keeping file bytes: walk ADT/M2/WMO references, return (found, missing)."""
        found, missing, seen, todo = set(), set(), set(), []

        def want(p: str) -> None:
            k = p.replace("/", "\\")
            if k.lower() not in seen:
                todo.append(k)

        for s in self.skies:
            want(s)
        for k in self.adts:
            tex, mdx, wmo = closure.adt_refs(self.coa.read(k))
            for x in tex + wmo:
                want(x)
            for x in tex:   # terrain specular/height companions: without _s the layer drew solid green in game
                for suf in ("_s.blp", "_h.blp"):
                    if self.read_any(x[:-4] + suf):
                        want(x[:-4] + suf)
            for m in mdx:
                want(m.rsplit(".", 1)[0] + ".m2")
        while todo:
            p = todo.pop()
            lk = p.lower()
            if lk in seen:
                continue
            seen.add(lk)
            blob = self.read_any(p)
            if blob is None:
                missing.add(p)
                continue
            found.add(p)
            if lk.endswith(".m2") and blob[:4] == b"MD20" and len(blob) >= 72:
                for x in closure.m2_refs(blob)[0] + closure.m2_skins(p, blob):
                    want(x)
            elif lk.endswith(".wmo"):
                base = lk.rsplit(".", 1)[0]
                tex, doodads, groups = closure.wmo_root_refs(blob)
                if groups and not (base[-4:-3] == "_" and base[-3:].isdigit()):
                    for x in tex:
                        want(x)
                    for d in doodads:
                        want(d.rsplit(".", 1)[0] + ".m2")
                    orig = p.rsplit(".", 1)[0]
                    for g in range(groups):
                        want(f"{orig}_{g:03d}.wmo")
        return found, missing

    def filter_assets(self) -> None:
        """Ship only paths new to Esteria's client; same bytes are dropped, different bytes keep Esteria's file."""
        cf = self.ctx.cf
        same = diff = 0
        kept = []
        for path, v in self.pack.items():
            k = lib.norm(path)
            if k.rsplit("/", 1)[-1] in ("thumbs.db", "(listfile)", "(attributes)") or k.startswith("dbfilesclient/") \
                    or k.endswith(".trs"):
                continue
            if not cf.has(path):
                self.ship.append(path)
                continue
            cur, data = cf.read(path), self.resolve(v)
            if cur == data:
                same += 1
            else:
                diff += 1
                kept.append(f"{path}  esteria={len(cur or b'')}B  coa={len(data or b'')}B")
        (STAGE / "reports" / "kept-existing-CoA.txt").write_text("\n".join(kept) + "\n", encoding="utf-8")
        self.log(f"[CoA] ships {len(self.ship)} files; dropped identical {same}, kept-existing(different) {diff}")

    # ------------------------------------------------------------------------------------------- run
    def run(self) -> None:
        self.log(f"CoA archives open: {len(self.coa.handles)}")
        tiles, family = self.new0_tiles()
        self.log(f"map-0 zones: {len(tiles)} tiles, {len(family)} CoA areas -> map {NEW0_MAP} '{NEW0_DIR}'")
        if self.ctx.client["Map"].get(NEW0_MAP) is not None or self.row("Map", NEW0_MAP) is not None:
            raise RuntimeError(f"map {NEW0_MAP} is taken")
        dirs_done: dict[str, int] = {}
        for m in MAPS:
            d = self.t("Map").text(self.row("Map", m)[1])
            self.do_map(m, m, d)
            dirs_done.setdefault(d.lower(), m)
        self.do_map(0, NEW0_MAP, NEW0_DIR, tiles={t.lower() for t in tiles}, area_ok=lambda a: a in family)
        self.server_sql(family, {t.lower() for t in tiles})
        # dependency closure from every ADT (CoA effective client), then sounds and skyboxes
        found, missing = self.closure()
        for p in found:
            self.pack.setdefault(p, ("any", p))
        for f in sorted(set(self.sounds)):
            if self.coa.has(f):
                self.pack.setdefault(f, ("coa", lib.norm(f)))
        self.log(f"closure: {len(found)} files, unresolved {len(missing)}")
        (STAGE / "reports").mkdir(parents=True, exist_ok=True)
        (STAGE / "reports" / "unresolved.txt").write_text("\n".join(sorted(missing)) + "\n", encoding="utf-8")
        self.filter_assets()
        ids = {"area": self.area, "wsl": self.wsl, "trigger": self.trigger, "light": self.light, "params": self.params,
               "maps": {str(k): v for k, v in self.maps.items()}, "tables": self.ids_report, "new0_tiles": sorted(tiles)}
        (STAGE / "reports" / "idmap.json").write_text(json.dumps(ids, indent=1, default=str), encoding="utf-8")
        write(self.ctx, self)
        write_extract(self.ctx, self)


def make_wdt(azeroth: bytes, tiles: set[str]) -> bytes:
    """Azeroth's WDT with only the copied tiles marked present."""
    keep = set()
    for t in tiles:
        x, y = t.lower().replace("azeroth_", "").replace(".adt", "").split("_")
        keep.add(int(y) * 64 + int(x))
    b = bytearray(azeroth)
    for tag, off, _s in closure.chunks(azeroth):
        if tag == "MAIN":
            for i in range(4096):
                flags = struct.unpack_from("<I", b, off + i * 8)[0]
                struct.pack_into("<I", b, off + i * 8, (flags | 1) if i in keep else (flags & ~1))
    return bytes(b)


class Writer:
    """Streams files into numbered MPQs, starting the next archive at `limit` bytes (MPQ v1 stops at 4 GB)."""

    def __init__(self, path_of, first: int, limit: int, log):
        self.path_of, self.n, self.limit, self.log = path_of, first, limit, log
        self.st = lib.storm()
        self.h = None
        self.size = self.count = 0

    def _open(self) -> None:
        path = self.path_of(self.n)
        path.unlink(missing_ok=True)
        self.h = lib.cmp.H()
        if not self.st.dll.SFileCreateArchive(str(path), 0x1 | 0x2, 131072, lib.c.byref(self.h)):
            raise OSError(f"SFileCreateArchive failed: {path} ({lib.c.get_last_error()})")

    def close(self) -> None:
        if self.h is not None:
            self.st.dll.SFileCloseArchive(self.h)
            self.log(f"packed {self.path_of(self.n).name}: {self.count} files, {self.size / 1e6:.0f} MB")
            self.h, self.size, self.count = None, 0, 0
            self.n += 1

    def add(self, name: str, data: bytes) -> None:
        if self.h is not None and self.size + len(data) > self.limit:
            self.close()
        if self.h is None:
            self._open()
        fh = lib.cmp.H()
        if not self.st.dll.SFileCreateFile(self.h, name.encode("ascii", "replace"), 0, len(data), 0, 0, lib.c.byref(fh)):
            raise OSError(f"SFileCreateFile failed: {name} ({lib.c.get_last_error()})")
        try:
            buf = lib.c.create_string_buffer(data or b"\0")
            if not self.st.dll.SFileWriteFile(fh, buf, len(data), 0x2):
                raise OSError(f"SFileWriteFile failed: {name} ({lib.c.get_last_error()})")
        finally:
            self.st.dll.SFileCloseFile(fh)
        self.size += len(data)
        self.count += 1


def write_extract(ctx, port) -> None:
    """Archives for the server extractors: every file the maps need (not only what the client lacks), the merged
    server AreaTable/LiquidType, and a Map.dbc holding only these maps so nothing else is re-extracted.
    Terrain + DBCs in patch-4/patch-5 (the map extractor reads no further); models from patch-6 (the vmap
    extractor scans every patch-N)."""
    keep = set(MAPS) | {NEW0_MAP}
    only = lib.Dbc(ctx.server["Map"].to_bytes())
    only.rows = [r for r in only.rows if r[0] in keep]
    out_dir = STAGE / "extract"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("patch-*.MPQ"):
        old.unlink()
    w = Writer(lambda n: out_dir / f"patch-{n}.MPQ", 4, 3_900_000_000, ctx.log)
    w.add("DBFilesClient\\Map.dbc", only.to_bytes())
    for name in ("AreaTable", "LiquidType"):
        w.add(f"DBFilesClient\\{name}.dbc", ctx.server[name].to_bytes())
    terrain = sorted(p for p in port.pack if p.lower().startswith("world\\maps\\"))
    for p in terrain:
        data = port.resolve(port.pack[p])
        if data:
            w.add(p, data)
    if w.n > 5:
        raise RuntimeError("terrain does not fit patch-4 + patch-5")
    w.close()
    w.n = 6
    for p in sorted(set(port.pack) - set(terrain)):
        data = port.resolve(port.pack[p])
        if data:
            w.add(p, data)
    w.close()


def write(ctx, port) -> None:
    S = STAGE
    for sub in ("client", "client-dbc/DBFilesClient", "server/dbc", "server/sql"):
        (S / sub).mkdir(parents=True, exist_ok=True)
    ctx.delta.dump(S / "reports" / "dbc-delta.json")
    entries: dict[str, bytes] = {}
    done = dbcdelta.apply_delta(ctx.delta, ctx.client)
    for t in done:
        data = ctx.client[t].to_bytes()
        (S / "client-dbc" / "DBFilesClient" / f"{t}.dbc").write_bytes(data)
        entries[f"DBFilesClient\\{t}.dbc"] = data
    sdone = dbcdelta.apply_delta(ctx.delta, ctx.server, only=set(C.SERVER_TABLES))
    for t in sdone:
        (S / "server" / "dbc" / f"{t}.dbc").write_bytes(ctx.server[t].to_bytes())
    ctx.log(f"client DBC rows added: {done}")
    ctx.log(f"server DBC rows added: {sdone}")
    if ctx.trs_lines:
        cur = (ctx.cf.read(TRS) or b"").decode("utf-8", "replace")
        have = {l.strip().lower() for l in cur.splitlines() if l.lower().startswith("dir:")}
        clash = [l for l in ctx.trs_lines if l.lower().startswith("dir:") and l.strip().lower() in have]
        if clash:
            raise RuntimeError(f"minimap dirs already in the client: {clash}")
        entries[TRS] = (cur.rstrip("\r\n") + "\r\n" + "\r\n".join(ctx.trs_lines) + "\r\n").encode("utf-8")
    st = lib.storm()
    for old in (S / "client").glob("*.MPQ"):
        old.unlink()
    st.create_archive(S / "client" / DBC_ARCHIVE, entries)
    w = Writer(lambda n: S / "client" / ASSET_ARCHIVE.format(n), 1, ARCHIVE_LIMIT, ctx.log)
    for p in sorted(port.ship):
        data = port.resolve(port.pack[p])
        if data:
            w.add(p, data)
    w.close()
    ids = list(range(TELE_BASE, TELE_BASE + len(ctx.teles)))
    taken = sqlgen.live_ids("game_tele", "id", ids)
    if taken:
        raise RuntimeError(f"game_tele ids taken: {sorted(taken)[:10]}")
    rows = [{"id": i, "position_x": t.x, "position_y": t.y, "position_z": t.z, "orientation": t.o, "map": t.map, "name": t.name}
            for i, t in zip(ids, ctx.teles)]
    if rows:
        ctx.sql["coa_maps_world.sql"] += [f"DELETE FROM `game_tele` WHERE `id` BETWEEN {ids[0]} AND {ids[-1]};",
                                          sqlgen.emit("game_tele", rows)]
    for name, parts in ctx.sql.items():
        (S / "server" / "sql" / name).write_text("\n".join(p for p in parts if p) + "\n", encoding="utf-8")
    (S / "reports" / "stage-report.txt").write_text("\n".join(ctx.report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    Port().run()
