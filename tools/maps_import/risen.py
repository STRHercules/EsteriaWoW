"""Risen Depths (Sirus map 10001, terrain dir Sirus2) -> Esteria standalone map 1430 'RisenDepths'.

Source of truth is the local Sirus client (effective files, patch order resolved by probing), not the harvested
copy; the harvest is used only as the list of world-map art files. Russian strings are translated below."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import closure
import dbcdelta
import lib
import sqlgen
from ctx import REPO, Ctx, Tele, closure_report, filter_assets
from dbcdelta import spec_from_src
from sirus import Sirus

SRC_MAP, NEW_MAP, NEW_DIR, OLD_DIR = 10001, 1430, "RisenDepths", "Sirus2"
HARVEST = REPO / "Harvested" / "Risen_Depths_Extract_2026-10-04"
TILES = [(x, y) for x in range(28, 37) for y in range(28, 37)]
AREA_NEW_BASE = 30100

# Russian -> English (names are checked against the world-map overlay file names, e.g. FLOODEDRUINS)
EN = {
    "Поднявшиеся глубины": "Risen Depths",
    "Затопленные руины": "Flooded Ruins",
    "Нерестилище": "Spawning Ground",
    "Логово Карибдис": "Lair of Charybdis",
    "Земли Жемчужного Плавника": "Pearlfin Lands",
    "Ржавое ущелье": "Rusty Gorge",
    "Аммонитовый риф": "Ammonite Reef",
    "Молниевая Лагуна": "Lightning Lagoon",
    "Туманная отмель": "Foggy Shoal",
    "Остров Проклятых": "Isle of the Damned",
    "Сердце Мглы": "Heart of the Mist",
    "Остров Кровавого Прилива": "Bloodtide Island",
    "Гряда Аквариона": "Aquarion Ridge",
    "Бездна": "The Abyss",
    "Остров Кораллового Когтя": "Coral Claw Island",
    "Стоянка Элементалей": "Station of the Elementals",
    "Ведьмин остров": "Witch's Isle",
    "Проклятый Корабль": "Cursed Ship",
    "Хищный Риф": "Predatory Reef",
    "Мемориал Кало'теры": "Kalothera Memorial",
    "Храм Тел'серай": "Temple of Tel'serai",
    "Ставка Наместницы": "Viceroy Nezhar's Headquarters",
    "Усыпальница Кракена": "Kraken's Tomb",
    "Руины Хажири": "Khajiri Ruins",
    "Бескрайние глубины": "Boundless Depths",
    "Логово сектантов": "Cultists' Den",
    "Укрытие": "Shelter",
}


def tr(text: str, ctx: Ctx, where: str) -> str:
    t = text.strip()
    if lib.has_cyrillic(t):
        if t not in EN:
            ctx.log(f"  [Risen] UNTRANSLATED {where}: {t!r}")
            return t
        return EN[t]
    return text


def _idx(db: lib.Dbc) -> dict[int, list[int]]:
    return {r[0]: r for r in db.rows}


class Importer:
    """Reuse-or-keep-or-remap for tables whose ids Esteria may already use."""

    def __init__(self, ctx: Ctx, S: Sirus):
        self.ctx, self.S = ctx, S
        self.src: dict[str, lib.Dbc] = {}
        self.idx: dict[str, dict] = {}

    def table(self, name: str) -> lib.Dbc:
        if name not in self.src:
            r = self.S.read(f"DBFilesClient\\{name}.dbc")
            if r is None:
                raise RuntimeError(f"Sirus has no {name}.dbc")
            self.src[name] = lib.Dbc(r)
            self.idx[name] = _idx(self.src[name])
        return self.src[name]

    def row(self, name: str, rid: int):
        self.table(name)
        return self.idx[name].get(rid)

    def place(self, table: str, row: list[int], start: int, fix=None, keep_free: bool = True) -> int:
        """Return the id to use in Esteria for this source row, adding it to the delta when needed."""
        ctx = self.ctx
        spec = spec_from_src(table, self.src[table], row)
        if fix:
            fix(spec)
        sid = row[0]
        base = ctx.client.get(table)
        cur = base.get(sid) if base else None
        if cur is not None:
            if spec_from_src(table, base, cur)[1:] == spec[1:]:
                return sid
        used = ctx.used_ids(table)
        if cur is None and sid not in used and keep_free:
            new = sid
        else:
            new = next(i for i in range(start, start + 10_000_000) if i not in used)
        spec[0] = new
        ctx.delta.add(table, spec)
        return new


def do_risen(ctx: Ctx) -> None:
    S = Sirus()
    I = Importer(ctx, S)
    ctx.log(f"[Risen] Sirus archives open: {len(S.handles)}")

    # ---------------------------------------------------------------- source rows
    amap = I.table("Map")
    mrow = I.row("Map", SRC_MAP)
    at = I.table("AreaTable")
    zone_ids = [r[0] for r in at.rows if r[1] == SRC_MAP]
    ctx.log(f"[Risen] AreaTable rows with ContinentID {SRC_MAP}: {len(zone_ids)}")

    # ---------------------------------------------------------------- sound chain (bottom-up)
    wanted_music = {at_r[8] for at_r in (I.row("AreaTable", z) for z in zone_ids) if at_r[8]}
    wanted_intro = {at_r[9] for at_r in (I.row("AreaTable", z) for z in zone_ids) if at_r[9]}
    wanted_amb = {at_r[7] for at_r in (I.row("AreaTable", z) for z in zone_ids) if at_r[7]}
    sound_files: list[str] = []

    def sound_id(sid: int) -> int:
        if not sid:
            return 0
        row = I.row("SoundEntries", sid)
        if row is None:
            ctx.log(f"  [Risen] SoundEntries {sid} missing in Sirus; reference dropped")
            return 0
        se = I.src["SoundEntries"]
        d = se.text(row[23])
        for c in range(3, 13):
            f = se.text(row[c])
            if f:
                sound_files.append((d + "\\" + f) if d else f)
        return I.place("SoundEntries", row, 60000)

    amb_map = {}
    for a in sorted(wanted_amb):
        r = I.row("SoundAmbience", a)
        amb_map[a] = I.place("SoundAmbience", r, 900, fix=lambda s: s.__setitem__(slice(1, 3), [sound_id(s[1]), sound_id(s[2])])) if r else 0
    mus_map = {}
    for m in sorted(wanted_music):
        r = I.row("ZoneMusic", m)
        mus_map[m] = I.place("ZoneMusic", r, 900, fix=lambda s: s.__setitem__(slice(6, 8), [sound_id(s[6]), sound_id(s[7])])) if r else 0
    intro_map = {}
    for m in sorted(wanted_intro):
        r = I.row("ZoneIntroMusicTable", m)
        intro_map[m] = I.place("ZoneIntroMusicTable", r, 900, fix=lambda s: s.__setitem__(2, sound_id(s[2]))) if r else 0

    # ---------------------------------------------------------------- lighting chain
    sky_ok_cache: dict[str, str] = {}
    sky_needed: list[str] = []   # skybox models only the Sirus client has: shipped with the zone

    def sky_fix(spec):
        name = spec[1]
        if name not in sky_ok_cache:
            # DBC names use the legacy .mdx extension; the client loads the .m2 of the same name
            m2 = name.rsplit(".", 1)[0] + ".m2" if name.lower().endswith(".mdx") else name
            ok = ctx.cf.probe(m2) or S.read(m2) is not None
            if ok:
                sky_ok_cache[name] = name
                if not ctx.cf.probe(m2):
                    sky_needed.append(m2)
            else:
                sub = next((c for c in ("Environments\\Stars\\DeathSkybox.mdx", "Environments\\Stars\\HyjalSmokeSkybox.mdx",
                                        "Environments\\Stars\\NightSkybox.mdx")
                            if ctx.cf.probe(c.rsplit(".", 1)[0] + ".m2")), "")
                ctx.log(f"  [Risen] sky model {name} exists in neither client; substituted {sub or '(none)'}")
                sky_ok_cache[name] = sub
        spec[1] = sky_ok_cache[name]

    lights = [r for r in I.table("Light").rows if r[1] == SRC_MAP]
    param_ids = sorted({p for r in lights for p in r[7:15] if p})
    param_map: dict[int, int] = {}
    ibands, fbands = I.table("LightIntBand"), I.table("LightFloatBand")
    ib, fb = _idx(ibands), _idx(fbands)
    cib = ctx.client.get("LightIntBand")
    cfb = ctx.client.get("LightFloatBand")
    for p in param_ids:
        r = I.row("LightParams", p)
        if r is None:
            ctx.log(f"  [Risen] LightParams {p} missing in Sirus; light reference dropped")
            param_map[p] = 0
            continue
        sky = I.row("LightSkybox", r[2]) if r[2] else None

        def pfix(spec, sky=sky):
            spec[2] = I.place("LightSkybox", sky, 600, fix=sky_fix) if sky else 0

        new = I.place("LightParams", r, 2100, fix=pfix, keep_free=False)
        param_map[p] = new
        if new in ctx.delta.ids("LightParams"):
            # bands are keyed positionally by params id: IDs n*18-17..n*18 (int) and n*6-5..n*6 (float)
            for k in range(18):
                s_id, d_id = p * 18 - 17 + k, new * 18 - 17 + k
                row = ib.get(s_id)
                if row is None:
                    ctx.log(f"  [Risen] LightIntBand {s_id} missing for LightParams {p}")
                    continue
                if cib is not None and cib.get(d_id) is not None:
                    raise RuntimeError(f"LightIntBand {d_id} already exists in Esteria")
                ctx.delta.add("LightIntBand", [d_id] + list(row[1:]))
            for k in range(6):
                s_id, d_id = p * 6 - 5 + k, new * 6 - 5 + k
                row = fb.get(s_id)
                if row is None:
                    ctx.log(f"  [Risen] LightFloatBand {s_id} missing for LightParams {p}")
                    continue
                if cfb is not None and cfb.get(d_id) is not None:
                    raise RuntimeError(f"LightFloatBand {d_id} already exists in Esteria")
                ctx.delta.add("LightFloatBand", [d_id] + list(row[1:]))
    light_new = {}
    for r in lights:
        spec = list(r)
        spec[1] = NEW_MAP
        for i in range(7, 15):
            spec[i] = param_map.get(spec[i], 0) if spec[i] else 0
        used = ctx.used_ids("Light")
        nid = r[0] if r[0] not in used else next(i for i in range(5200, 10**7) if i not in used)
        spec[0] = nid
        light_new[r[0]] = nid
        ctx.delta.add("Light", spec)
    ctx.log(f"[Risen] lights {len(lights)}, light params {len(param_ids)} (reused/new: {param_map}), band rows "
            f"{len(ctx.delta.rows.get('LightIntBand', []))}/{len(ctx.delta.rows.get('LightFloatBand', []))}")

    # ---------------------------------------------------------------- AreaTable
    new_area: dict[int, int] = {0: 0}
    used_a = ctx.used_ids("AreaTable")
    nxt = AREA_NEW_BASE
    for z in zone_ids:
        if z not in used_a:
            new_area[z] = z
            used_a.add(z)
        else:
            while nxt in used_a:
                nxt += 1
            new_area[z] = nxt
            used_a.add(nxt)
    bit_map: dict[int, int] = {0: 0}
    for z in zone_ids:
        r = I.row("AreaTable", z)
        if r[3] not in bit_map:
            bit_map[r[3]] = ctx.new_bit()
        spec = spec_from_src("AreaTable", at, r)
        spec[0], spec[1] = new_area[z], NEW_MAP
        spec[2] = new_area.get(r[2], 0)
        spec[3] = bit_map[r[3]]
        spec[5] = spec[5] if ctx.exists_in("SoundProviderPreferences", spec[5]) or spec[5] == 0 else 0
        spec[6] = spec[6] if ctx.exists_in("SoundProviderPreferences", spec[6]) or spec[6] == 0 else 0
        spec[7], spec[8], spec[9] = amb_map.get(r[7], 0), mus_map.get(r[8], 0), intro_map.get(r[9], 0)
        spec[11] = tr(spec[11], ctx, f"AreaTable {z}")
        spec[35] = light_new.get(r[35], 0) if r[35] else 0
        ctx.delta.add("AreaTable", spec)
    area_by_name = {tr(lib.best_loc(at, I.row("AreaTable", z), 11), ctx, "poi-name"): new_area[z] for z in zone_ids}
    zone_new = new_area[10050]

    # ---------------------------------------------------------------- Map + loading screen
    def ls_fix(spec):
        spec[1] = spec[1]

    ls_row = I.row("LoadingScreens", mrow[57]) if mrow[57] else None
    ls_new = I.place("LoadingScreens", ls_row, 950, fix=ls_fix) if ls_row else 0
    spec = spec_from_src("Map", amap, mrow)
    spec[0], spec[1] = NEW_MAP, NEW_DIR
    spec[5] = tr(spec[5], ctx, "Map name")
    spec[22] = 0
    spec[57] = ls_new
    spec[59] = 0xFFFFFFFF if mrow[59] in (0, 0xFFFFFFFF) else mrow[59]
    ctx.delta.add("Map", spec)

    # ---------------------------------------------------------------- world map area / overlays
    wma = I.table("WorldMapArea")
    wrows = [r for r in wma.rows if r[1] == SRC_MAP]
    used_w = ctx.used_ids("WorldMapArea")
    wma_new = {}
    nw = 1101
    for r in sorted(wrows, key=lambda r: r[10] != 0):   # parents (parent id 0) first
        while nw in used_w:
            nw += 1
        wma_new[r[0]] = nw
        used_w.add(nw)
    for r in wrows:
        sp = spec_from_src("WorldMapArea", wma, r)
        sp[0], sp[1] = wma_new[r[0]], NEW_MAP
        sp[2] = new_area.get(r[2], 0)
        sp[10] = wma_new.get(r[10], 0)
        ctx.delta.add("WorldMapArea", sp)
    wmo = I.table("WorldMapOverlay")
    ovl = [r for r in wmo.rows if r[1] in wma_new]
    for r in ovl:
        sp = spec_from_src("WorldMapOverlay", wmo, r)
        if sp[0] in ctx.used_ids("WorldMapOverlay"):
            sp[0] = next(i for i in range(3300, 10**7) if i not in ctx.used_ids("WorldMapOverlay"))
        sp[1] = wma_new[r[1]]
        for k in range(2, 6):
            sp[k] = new_area.get(r[k], 0)
        ctx.delta.add("WorldMapOverlay", sp)

    # ---------------------------------------------------------------- POIs
    poi = I.table("AreaPOI")
    for r in [r for r in poi.rows if r[15] == SRC_MAP]:
        sp = spec_from_src("AreaPOI", poi, r)
        name_en = tr(sp[18], ctx, f"AreaPOI {r[0]}")
        sp[18], sp[35] = name_en, tr(sp[35], ctx, f"AreaPOI {r[0]} desc")
        sp[15] = NEW_MAP
        sp[17] = area_by_name.get(name_en, zone_new)
        if sp[0] in ctx.used_ids("AreaPOI"):
            sp[0] = next(i for i in range(2500, 10**7) if i not in ctx.used_ids("AreaPOI"))
        ctx.delta.add("AreaPOI", sp)

    # ---------------------------------------------------------------- safe locations, graveyards
    wsl = I.table("WorldSafeLocs")
    gy = []
    for r in [r for r in wsl.rows if r[1] == SRC_MAP]:
        sp = spec_from_src("WorldSafeLocs", wsl, r)
        sp[1] = NEW_MAP
        sp[5] = "Risen Depths Naga Graveyard" if lib.best_loc(wsl, r, 5) == "Naga Graveyard" else tr(sp[5], ctx, "WSL")
        if sp[0] in ctx.used_ids("WorldSafeLocs") or sp[0] in range(1800, 1804):
            sp[0] = next(i for i in range(1850, 10**7) if i not in ctx.used_ids("WorldSafeLocs"))
        ctx.delta.add("WorldSafeLocs", sp)
        gy.append((sp[0], lib.u2f(r[2]), lib.u2f(r[3]), lib.u2f(r[4])))
    sql = ctx.sql.setdefault("risendepths_world.sql", [])
    ids = ",".join(str(g[0]) for g in gy)
    sql += ["-- Risen Depths (map 1430). Graveyards only: the source has no creatures, quests or scripts.",
            f"DELETE FROM `game_graveyard` WHERE `ID` IN ({ids});",
            sqlgen.emit("game_graveyard", [{"ID": g[0], "Map": NEW_MAP, "x": g[1], "y": g[2], "z": g[3],
                                            "Comment": "Risen Depths Naga Graveyard"} for g in gy]),
            f"DELETE FROM `graveyard_zone` WHERE `ID` IN ({ids});",
            sqlgen.emit("graveyard_zone", [{"ID": g[0], "GhostZone": zone_new, "Faction": 0, "Comment": "Risen Depths"}
                                           for g in gy])]
    land = next(g for g in gy if g[3] > 0)
    ctx.teles.append(Tele("risendepths", NEW_MAP, land[1], land[2], land[3] + 1.0, 0, "graveyard position (surface)"))

    # ---------------------------------------------------------------- terrain + dependencies
    pack: dict[str, bytes] = {}
    adts = []
    area_remap = lambda a: new_area.get(a, 0)  # noqa: E731
    for x, y in TILES:
        p = f"World\\Maps\\{OLD_DIR}\\{OLD_DIR}_{x}_{y}.adt"
        data = S.read(p)
        if data is None:
            ctx.log(f"  [Risen] tile {x}_{y} not found in the Sirus client")
            continue
        adts.append((p, data))
        pack[f"World\\Maps\\{NEW_DIR}\\{NEW_DIR}_{x}_{y}.adt"] = closure.patch_adt_areas(data, area_remap)
    for ext in ("wdt", "wdl"):
        d = S.read(f"World\\Maps\\{OLD_DIR}\\{OLD_DIR}.{ext}")
        if d is None:
            ctx.log(f"  [Risen] {OLD_DIR}.{ext} missing")
        else:
            pack[f"World\\Maps\\{NEW_DIR}\\{NEW_DIR}.{ext}"] = d
    ctx.log(f"[Risen] tiles read: {len(adts)}/81")
    found, missing = closure.compute(adts, S.read)
    ctx.log(f"[Risen] dependency closure: {len(found)} files from Sirus, {len(missing)} unresolved")
    for m in sorted(missing):
        ctx.log(f"    unresolved in Sirus: {m}")
    pack.update(found)

    sky_found, sky_missing = closure.compute([], S.read, seed=sky_needed)
    pack.update(sky_found)
    ctx.log(f"[Risen] skybox models from Sirus: {len(sky_needed)} (+{len(sky_found)} files incl. deps, unresolved {sorted(sky_missing)})")

    # minimap tiles: Sirus2 block of the effective translate file, renamed to the new directory
    trs = (S.read("Textures\\Minimap\\md5translate.trs") or b"").decode("utf-8", "replace")
    lines = [f"dir: {NEW_DIR}"]
    for line in trs.splitlines():
        if line.lower().startswith(OLD_DIR.lower() + "\\") and "\t" in line:
            k, v = line.strip().split("\t", 1)
            lines.append(f"{NEW_DIR}\\{k.split(chr(92), 1)[1]}\t{v}")
            b = S.read("Textures\\Minimap\\" + v)
            if b is None:
                ctx.log(f"  [Risen] minimap tile {v} missing")
            else:
                pack["Textures\\Minimap\\" + v] = b
    ctx.trs_lines += lines
    ctx.log(f"[Risen] minimap tiles: {len(lines) - 1}")

    # world map art and loading screen
    art = 0
    for row in csv.DictReader(open(HARVEST / "worldmap_art_manifest.csv", encoding="utf-8")):
        path = row.get("MPQPath") or ""
        if path and path not in pack:
            b = S.read(path)
            if b is not None:
                pack[path] = b
                art += 1
    for p in {"Interface\\WorldMap\\RisingDepths\\RisingDepths" + str(i) + ".blp" for i in range(1, 13)}:
        if p not in pack:
            b = S.read(p)
            if b is not None:
                pack[p] = b
                art += 1
    if ls_row:
        lp = I.src["LoadingScreens"].text(ls_row[2])
        b = S.read(lp)
        if b is not None:
            pack[lp] = b
        else:
            ctx.log(f"  [Risen] loading screen {lp} missing in Sirus")
    # overlays need their art; report which overlay textures resolved
    wma_dir = "Interface\\WorldMap\\RisingDepths\\"
    miss_ovl = [wmo.text(r[8]) for r in ovl if not any(k.lower().startswith((wma_dir + wmo.text(r[8])).lower()) for k in pack)]
    ctx.log(f"[Risen] world-map art files: {art}; overlays without art: {miss_ovl}")
    for f in sorted(set(sound_files)):
        b = S.read(f)
        if b is not None:
            pack[f] = b
        else:
            ctx.log(f"  [Risen] sound file {f} not in Sirus")

    # M2 versions (client reads 264)
    bad = []
    for p, d in pack.items():
        if p.lower().endswith(".m2"):
            v = closure.m2_refs(d)[1]
            if v != 264:
                bad.append((p, v))
    ctx.log(f"[Risen] M2 files not version 264: {bad[:10]} (total {len(bad)})")

    filter_assets(ctx, "Risen", pack, always_ship_prefixes=(f"world/maps/{NEW_DIR.lower()}/",))
    closure_report(ctx, "Risen", adts)
    ctx.log(f"[Risen] id map: map {SRC_MAP}->{NEW_MAP}; zone area {10050}->{zone_new}; areas {new_area}")
    (ctx_dir := REPO / "exports" / "maps-import-20261112" / "reports").mkdir(parents=True, exist_ok=True)
    (ctx_dir / "risen-idmap.json").write_text(json.dumps({"areas": new_area, "wma": wma_new, "lightparams": param_map,
                                                            "lights": light_new}, indent=1))

    # Morza: fill its 7 doodads missing from Esteria's client from the Sirus client, when Sirus has them
    fill = []
    for p in ("WORLD\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\LAMPS\\DARNASSUSSTREELAMP02.m2",
              "WORLD\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\STONERUNES\\KALIDARSTONERUNES01.m2",
              "WORLD\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\STONERUNES\\KALIDARSTONERUNES02.m2",
              "WORLD\\GENERIC\\NIGHTELF\\PASSIVE DOODADS\\STONERUNES\\KALIDARSTONERUNES03.m2",
              "WORLD\\KALIMDOR\\WINTERSPRING\\PASSIVEDOODADS\\WORLDTREEROOTS\\WORLDTREEROOT01.m2",
              "WORLD\\KALIMDOR\\WINTERSPRING\\PASSIVEDOODADS\\WORLDTREEROOTS\\WORLDTREEROOT02.m2",
              "WORLD\\KALIMDOR\\WINTERSPRING\\PASSIVEDOODADS\\WORLDTREEROOTS\\WORLDTREEROOT03.m2"):
        d = S.read(p)
        if d is None:
            ctx.log(f"  [Morza donor] {p} not in Sirus either")
            continue
        deps, miss = closure.compute([], S.read, seed=[p])
        fill.append(p)
        for dp, db in deps.items():
            if not ctx.cf.probe(dp):
                ctx.assets.setdefault("Morza", {})[dp] = db
    ctx.log(f"[Morza donor] doodads filled from Sirus: {len(fill)}")
