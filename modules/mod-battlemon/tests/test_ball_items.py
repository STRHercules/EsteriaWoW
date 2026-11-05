"""The generated Poke Ball item SQL must match the constants and rules in src/BattlemonBall.h."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
header = open(os.path.join(ROOT, 'src', 'BattlemonBall.h'), encoding='utf-8').read()
base = int(re.search(r'ITEM_BASE = (\d+)', header).group(1))
shiny = int(re.search(r'ITEM_SHINY_OFFSET = (\d+)', header).group(1))

sql = open(os.path.join(ROOT, 'data', 'sql', 'db-world', 'base', '2026_11_05_05_battlemon_ball_items.sql'),
           encoding='utf-8').read()
rows = re.findall(r"^\((\d+), 15, 0, '((?:[^']|'')*)', \d+, (\d+), (\d+), 1, 0, 0, 0, 1, \d+, 0, 0, -1, '(?:[^']|'')*', "
                  r"'(\w+)', \d+\)", sql, re.M)
assert len(rows) == len(re.findall(r'^\(\d+,', sql, re.M)) > 2000, 'unparsed rows'
seen = set()
for entry, name, quality, flags, script in rows:
    entry = int(entry)
    assert entry not in seen, entry
    seen.add(entry)
    is_shiny = entry - base >= shiny
    species = entry - base - (shiny if is_shiny else 0)
    assert 0 < species < shiny, entry
    assert name.startswith('Shiny ') == is_shiny, name        # the name is what the auction house searches
    assert int(quality) == (3 if is_shiny else 1), name
    assert int(flags) & 0x20, name                              # ITEM_FLAG_NO_USER_DESTROY
    assert script == 'item_battlemon_ball', name                # must match the ItemScript in BattlemonBall.cpp
assert 'item_battlemon_ball' in open(os.path.join(ROOT, 'src', 'BattlemonBall.cpp'), encoding='utf-8').read()
print('ok', len(seen))
