#!/usr/bin/env python3
"""Fail if the CoA import would replace anything Esteria owns.

The CoA files are additive: every key they DELETE before inserting must be a key
nothing else in Esteria defines. This reads the keys each generated CoA file
clears (IN lists and BETWEEN ranges) and checks them against

  * every other SQL file in the repository (base dumps, updates, custom, modules),
  * the server Spell/CreatureDisplayInfo/CreatureModelData DBCs,
  * the target client's winning tables, ignoring the CoA archive itself,
  * an optional list of spell_dbc ids taken from the world database before CoA.

  python tools/coa_overwrite_audit.py --target-client "G:/3.3.5a - Dev" [--world-spell-ids ids.txt]

Exit 1 and list the collisions if any.
"""
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(MODULE, "..", ".."))
sys.path.insert(0, os.path.join(MODULE, "client-patch"))
sys.path.insert(0, os.path.join(MODULE, "data", "sql", "generators"))
from lib import coa  # noqa: E402
from gen_coa_import import Dbc  # noqa: E402

DB_WORLD = os.path.join(MODULE, "data", "sql", "db-world")
COA_FILES = ["cw_spells_coa.sql"] + [os.path.basename(p) for p in glob.glob(os.path.join(DB_WORLD, "cw_coa_*.sql"))]
# the module's own tables: CoA owns them outright
OWN_TABLES = {"cw_coa_classes", "cw_coa_tabs", "cw_coa_entries", "cw_coa_taught", "cw_coa_spell_scaling", "cw_coa_automatic"}
# client tables that share a key space with a server table
CLIENT_TABLE = {"gameobjectdisplayinfo_dbc": "GameObjectDisplayInfo", "spell_dbc": "Spell", "talent_dbc": "Talent", "talenttab_dbc": "TalentTab",
                "creaturedisplayinfo_dbc": "CreatureDisplayInfo", "creaturemodeldata_dbc": "CreatureModelData",
                "spellitemenchantment_dbc": "SpellItemEnchantment"}
SERVER_DBC = os.path.join(REPO, "modules", "mod-custom-server", "data", "dbc", "retroported-races")
# rows keyed by a spell: the spell itself must be CoA's
SPELL_KEYED = {"spell_script_names", "spell_proc", "spell_bonus_data", "spell_custom_attr", "spell_linked_spell",
               "spell_ranks"}

DELETE = re.compile(r"DELETE FROM `(\w+)` WHERE (?:ABS\()?`(\w+)`\)? (?:IN \(([\d,\s-]+)\)|BETWEEN (\d+) AND (\d+))", re.I)
INSERT = re.compile(r"(?:INSERT(?:\s+IGNORE)?|REPLACE)\s+INTO\s+`?(\w+)`?\s*(\([^)]*\))?\s*VALUES", re.I)
TUPLE_KEY = re.compile(r"\(\s*'?(-?\d+)'?\s*,")


def coa_claims():
    """table -> (set of keys, list of (lo, hi) ranges)"""
    claims = {}
    for name in COA_FILES:
        text = open(os.path.join(DB_WORLD, name), encoding="utf-8").read()
        for m in DELETE.finditer(text):
            table = m.group(1).lower()
            keys, ranges = claims.setdefault(table, (set(), []))
            if m.group(3):
                keys.update(int(x) for x in m.group(3).replace(" ", "").split(",") if x)
            else:
                ranges.append((int(m.group(4)), int(m.group(5))))
    return claims


def esteria_sql_keys(tables):
    """Keys every non-CoA SQL file inserts, by table (first column of each tuple)."""
    owned = {t: {} for t in tables}
    skip = {os.path.normcase(os.path.join(DB_WORLD, n)) for n in COA_FILES}
    roots = [os.path.join(REPO, "data", "sql"), os.path.join(REPO, "modules")]
    for root in roots:
        for path in glob.iglob(os.path.join(root, "**", "*.sql"), recursive=True):
            if os.path.normcase(path) in skip or os.sep + "uninstall" + os.sep in path:
                continue
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for m in INSERT.finditer(text):
                table = m.group(1).lower()
                if table not in owned:
                    continue
                end = text.find(";\n", m.end())
                body = text[m.end():end if end > 0 else len(text)]
                for k in TUPLE_KEY.findall(body):
                    owned[table].setdefault(int(k), os.path.relpath(path, REPO))
    return owned


def dbc_keys(data):
    return set(Dbc(data).index) if data else set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-client", required=True)
    ap.add_argument("--world-spell-ids", help="spell_dbc ids from the world database before CoA was applied")
    args = ap.parse_args()

    claims = coa_claims()
    tables = set(claims) - OWN_TABLES
    owned = esteria_sql_keys(tables)

    archives = coa.target_archives(args.target_client)
    for table, client in CLIENT_TABLE.items():
        if table not in tables:
            continue
        _where, data = coa.winning_file(archives, "DBFilesClient" + coa.SEP + client + ".dbc")
        for k in dbc_keys(data):
            owned[table].setdefault(k, "client " + client + ".dbc")
        server = os.path.join(SERVER_DBC, client + ".dbc")
        if os.path.isfile(server):
            for k in dbc_keys(open(server, "rb").read()):
                owned[table].setdefault(k, "server " + client + ".dbc")
    if args.world_spell_ids and "spell_dbc" in owned:
        for x in open(args.world_spell_ids).read().split():
            owned["spell_dbc"].setdefault(int(x), "world spell_dbc before CoA")

    coa_spells = claims.get("spell_dbc", (set(), []))[0]
    bad = []
    for table in sorted(tables):
        keys, ranges = claims[table]
        for k, src in owned[table].items():
            if k in keys or any(lo <= k <= hi for lo, hi in ranges):
                bad.append((table, k, src))
        if table in SPELL_KEYED:
            # a script, proc or coefficient row on a spell CoA does not import touches Esteria's spell
            for k in sorted(keys - coa_spells):
                bad.append((table, k, "spell not imported by CoA"))
    for table, k, src in sorted(bad):
        print("%-28s %-9d %s" % (table, k, src))
    print("%d collision(s) across %d table(s)" % (len(bad), len(tables)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
