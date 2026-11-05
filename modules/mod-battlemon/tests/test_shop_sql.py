"""Every battlemon_shop entry must name an item in battlemon_items, and a shop row's pocket must be one the
Center menu can list (src/BattlemonCenter.cpp PocketName: 2 medicine, 3 balls, 5 berries, 7 battle items)."""
import glob
import os
import re

SQL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sql', 'db-world', 'base')
items = {}
for path in glob.glob(os.path.join(SQL, '*catalog_items.sql')):
    for name, pocket in re.findall(r"^\(\d+, '(\w+)', '(?:[^']|'')*', (?:'(?:[^']|'')*'|NULL), (\d+|NULL), ",
                                   open(path, encoding='utf-8').read(), re.M):
        items[name] = pocket
assert len(items) > 600, len(items)

shop = {}
for path in sorted(glob.glob(os.path.join(SQL, '*shop*.sql'))):
    text = open(path, encoding='utf-8').read()
    for name, cost in re.findall(r"^\('(\w+)',\s*(\d+),\s*\d+\)", text, re.M):
        shop[name] = int(cost)
assert len(shop) > 20, len(shop)
for name, cost in shop.items():
    assert name in items, name
    assert items[name] in ('2', '3', '5', '7'), (name, items[name])
    assert cost > 0, name
print('ok', len(shop))
