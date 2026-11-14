"""Morza Island server content -> SQL shaped for Esteria's acore_world. Only map-5000 content is imported, nothing
that already exists in the live database is overwritten, and no DELETE from the source files is ever replayed."""

from __future__ import annotations

import sqlgen
from ctx import Ctx
from maps_small import CREATURE_GUID0, GO_GUID0, MORZA_MAP
from morza_analyze import load_all


def _rows(tabs, name):
    """Rows of a source table, first occurrence wins when two source folders define the same key."""
    keys = {"item_template": ("entry",), "quest_template": ("ID",), "creature_template": ("entry",),
            "gameobject_template": ("entry",), "npc_text": ("ID",), "quest_template_addon": ("ID",),
            "quest_offer_reward": ("ID",), "quest_request_items": ("ID",), "gossip_menu": ("MenuID", "TextID"),
            "gossip_menu_option": ("MenuID", "OptionID"), "creature_template_addon": ("entry",)}
    rows = tabs[name].rows if name in tabs else []
    k = keys.get(name)
    if not k:
        return rows
    seen, out = set(), []
    for r in rows:
        key = tuple(r.get(c) for c in k)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def do_morza_server(ctx: Ctx) -> None:
    tabs, problems = load_all()
    for p in problems:
        ctx.log(f"[Morza SQL] source problem: {p}")
    sql = ctx.sql.setdefault("morza_world.sql", [])
    sql.insert(0, "-- Morza Island / CustomMaps (map 5000). Generated from the source SQL; map-5000 content only.")

    ct = _rows(tabs, "creature_template")
    ents = {r["entry"] for r in ct}
    live_ct = sqlgen.live_ids("creature_template", "entry", ents)
    new_ents = sorted(ents - live_ct)
    ctx.log(f"[Morza SQL] creature_template: {len(ents)} in source, {len(live_ct)} already in Esteria (kept as is), "
            f"{len(new_ents)} imported")

    spawns = [r for r in _rows(tabs, "creature") if r["map"] == MORZA_MAP]
    need = {r["id1"] for r in spawns}
    live_need = sqlgen.live_ids("creature_template", "entry", need)
    missing = sorted(need - live_need - set(new_ents))
    if missing:
        ctx.log(f"[Morza SQL] WARNING: spawns use creature entries that exist nowhere: {missing}")
    guid_map = {r["guid"]: CREATURE_GUID0 + i for i, r in enumerate(spawns)}
    if sqlgen.live_scalar(f"SELECT COUNT(*) FROM creature WHERE guid >= {CREATURE_GUID0}") != "0":
        ctx.log("[Morza SQL] WARNING: creature guids >= 9700001 are already in use in the live DB")
    ctx.log(f"[Morza SQL] creature spawns: {len(spawns)} -> guids {CREATURE_GUID0}..{CREATURE_GUID0 + len(spawns) - 1}")

    stmts: list[str] = []
    stmts.append(f"DELETE FROM `creature` WHERE `guid` BETWEEN {CREATURE_GUID0} AND {CREATURE_GUID0 + len(spawns) - 1};")
    crow = []
    for r in spawns:
        d = {k: v for k, v in r.items() if k not in ("id1", "id2", "id3", "guid")}
        d["guid"], d["id"] = guid_map[r["guid"]], r["id1"]
        crow.append(d)
    stmts.append(sqlgen.emit("creature", crow))

    def keyed(table, col, values):
        return [r for r in _rows(tabs, table) if r.get(col) in values]

    ne = set(new_ents)
    # templates and everything keyed by entry
    if ne:
        stmts.append(f"DELETE FROM `creature_template` WHERE `entry` IN ({','.join(map(str, new_ents))});")
        stmts.append(sqlgen.emit("creature_template", [r for r in ct if r["entry"] in ne]))
        for table, col in (("creature_template_model", "CreatureID"), ("creature_template_addon", "entry"),
                           ("creature_template_resistance", "CreatureID"), ("creature_template_spell", "CreatureID"),
                           ("creature_equip_template", "CreatureID"), ("npc_vendor", "entry"), ("npc_trainer", "ID"),
                           ("creature_queststarter", "id"), ("creature_questender", "id")):
            rows = keyed(table, col, ne)
            if rows:
                stmts.append(f"DELETE FROM `{table}` WHERE `{col}` IN ({','.join(map(str, sorted(ne)))});")
                stmts.append(sqlgen.emit(table, rows))
        loot_ids = {r["lootid"] for r in ct if r["entry"] in ne and r.get("lootid")}
        clash = sqlgen.live_ids("creature_loot_template", "Entry", loot_ids)
        rows = [r for r in _rows(tabs, "creature_loot_template") if r["Entry"] in loot_ids and r["Entry"] not in clash]
        if clash:
            ctx.log(f"[Morza SQL] creature loot ids already in Esteria, skipped: {sorted(clash)}")
        if rows:
            stmts.append(f"DELETE FROM `creature_loot_template` WHERE `Entry` IN ({','.join(map(str, sorted({r['Entry'] for r in rows})))});")
            stmts.append(sqlgen.emit("creature_loot_template", rows))

    # per-spawn addon and scripts (guid keyed)
    add = [dict(r, guid=guid_map[r["guid"]]) for r in _rows(tabs, "creature_addon") if r["guid"] in guid_map]
    if add:
        stmts.append(f"DELETE FROM `creature_addon` WHERE `guid` BETWEEN {CREATURE_GUID0} AND {CREATURE_GUID0 + len(spawns) - 1};")
        stmts.append(sqlgen.emit("creature_addon", add))
    ss_rows = []
    for r in _rows(tabs, "smart_scripts"):
        e, st = r["entryorguid"], r["source_type"]
        if st == 0 and e > 0 and e in ne:
            ss_rows.append(r)
        elif st == 0 and e < 0 and -e in guid_map:
            ss_rows.append(dict(r, entryorguid=-guid_map[-e]))
        elif st == 9:
            ss_rows.append(r)
    t9 = {r["entryorguid"] for r in ss_rows if r["source_type"] == 9}
    t9_clash = sqlgen.live_ids("smart_scripts", "entryorguid", t9)
    ss_rows = [r for r in ss_rows if not (r["source_type"] == 9 and r["entryorguid"] in t9_clash)]
    if ss_rows:
        keys = sorted({(r["entryorguid"], r["source_type"]) for r in ss_rows})
        for e, st in keys:
            stmts.append(f"DELETE FROM `smart_scripts` WHERE `entryorguid` = {e} AND `source_type` = {st};")
        stmts.append(sqlgen.emit("smart_scripts", ss_rows))

    # gossip
    menus = {r["MenuID"] for r in _rows(tabs, "gossip_menu")}
    mclash = sqlgen.live_ids("gossip_menu", "MenuID", menus)
    for mid in sorted(menus - mclash):
        stmts.append(f"DELETE FROM `gossip_menu` WHERE `MenuID` = {mid};\nDELETE FROM `gossip_menu_option` WHERE `MenuID` = {mid};")
    stmts.append(sqlgen.emit("gossip_menu", [r for r in _rows(tabs, "gossip_menu") if r["MenuID"] not in mclash]))
    stmts.append(sqlgen.emit("gossip_menu_option", [r for r in _rows(tabs, "gossip_menu_option") if r["MenuID"] not in mclash]))
    if mclash:
        ctx.log(f"[Morza SQL] gossip menus already in Esteria, skipped: {sorted(mclash)}")

    # game objects: templates all already exist in Esteria (stock ids); spawns on map 5000 only
    gos = [r for r in _rows(tabs, "gameobject") if r["map"] == MORZA_MAP]
    gneed = {r["id"] for r in gos}
    gmiss = sorted(gneed - sqlgen.live_ids("gameobject_template", "entry", gneed))
    new_gt = [r for r in _rows(tabs, "gameobject_template") if r["entry"] in gmiss]
    if new_gt:
        stmts.append(f"DELETE FROM `gameobject_template` WHERE `entry` IN ({','.join(str(r['entry']) for r in new_gt)});")
        stmts.append(sqlgen.emit("gameobject_template", new_gt))
    stmts.append(f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {GO_GUID0} AND {GO_GUID0 + len(gos) - 1};")
    stmts.append(sqlgen.emit("gameobject", [dict(r, guid=GO_GUID0 + i) for i, r in enumerate(gos)]))
    ctx.log(f"[Morza SQL] gameobject spawns: {len(gos)}; templates missing from Esteria: {gmiss}")

    # items and quests (custom ids), skipped per id if Esteria already has them
    for table, col, kids in (("item_template", "entry", ()),
                             ("quest_template", "ID", ("quest_template_addon", "quest_offer_reward", "quest_request_items"))):
        rows = _rows(tabs, table)
        ids = {r[col] for r in rows}
        have = sqlgen.live_ids(table, col, ids)
        keep = {r[col] for r in rows} - have
        if have:
            ctx.log(f"[Morza SQL] {table} ids already in Esteria, skipped: {sorted(have)}")
        if keep:
            stmts.append(f"DELETE FROM `{table}` WHERE `{col}` IN ({','.join(map(str, sorted(keep)))});")
            stmts.append(sqlgen.emit(table, [r for r in rows if r[col] in keep]))
            for kt in kids:
                kr = [r for r in _rows(tabs, kt) if r.get("ID") in keep]
                if kr:
                    stmts.append(f"DELETE FROM `{kt}` WHERE `ID` IN ({','.join(map(str, sorted(keep)))});")
                    stmts.append(sqlgen.emit(kt, kr))
    # npc_text, pools
    for table, col in (("npc_text", "ID"), ("pool_template", "entry"), ("pool_quest", "entry")):
        rows = _rows(tabs, table)
        have = sqlgen.live_ids(table, col, {r[col] for r in rows})
        rows = [r for r in rows if r[col] not in have]
        if rows:
            stmts.append(f"DELETE FROM `{table}` WHERE `{col}` IN ({','.join(str(r[col]) for r in rows)});")
            stmts.append(sqlgen.emit(table, rows))
        if have:
            ctx.log(f"[Morza SQL] {table} ids already in Esteria, skipped: {sorted(have)}")
    sql += [s for s in stmts if s]
