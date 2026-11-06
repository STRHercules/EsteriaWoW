"""Every item the held-item rules know about must exist in the item catalog and be obtainable from the shop.

    python tests/test_helditems_data.py ["<Battlemon addon dir>"]

With an addon directory it also checks that the addon's HOLDABLE list (what the item picker offers) is exactly the
server's table, so the picker never offers something the server refuses, nor hides something it accepts.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import SQL, parse_row

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
header = open(os.path.join(ROOT, 'src', 'BattlemonHeldItems.h'), encoding='utf-8').read()
held = re.findall(r'\{"(\w+)", Kind::\w+,', header)
assert len(held) == len(set(held)) > 30, held

catalog = set()
for line in open(os.path.join(SQL, '2026_08_13_03_battlemon_catalog_items.sql'), encoding='utf-8'):
    if re.match(r"\(\d+, '", line):
        catalog.add(parse_row(line.strip())[1])
shop = set()
for path in glob.glob(os.path.join(SQL, '*shop*.sql')):
    shop |= set(re.findall(r"^\('(\w+)',\s*\d+,\s*\d+\)", open(path, encoding='utf-8').read(), re.M))

missing = [n for n in held if n not in catalog]
assert not missing, 'held items not in the catalog: %s' % missing
unobtainable = [n for n in held if n not in shop]
assert not unobtainable, 'held items nobody can buy: %s' % unobtainable

if len(sys.argv) > 1:
    lua = open(os.path.join(sys.argv[1], 'UI', 'ItemPicker.lua'), encoding='utf-8').read()
    block = re.search(r'local HOLDABLE = \{(.*?)\n\}', lua, re.S).group(1)
    client = re.findall(r'\b([A-Z]+) = true', block)
    assert sorted(client) == sorted(held), (sorted(set(client) ^ set(held)))
print('ok', len(held), 'held items')
