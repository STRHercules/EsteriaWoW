"""The generated level-up and egg-move SQL must be all-or-nothing, batched, and keep the row order the server needs.

The server picks a Pokemon's moves from battlemon_species_moves in id order, so within a species the levels must
ascend, and the numbering (@bm_base + n) must run straight through every batch.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import SQL

MAX_ROWS = 1000

for name in ('2026_11_05_04_battlemon_levelup_moves.sql', '2026_11_05_02_battlemon_egg_moves.sql'):
    text = open(os.path.join(SQL, name), encoding='utf-8').read()
    assert text.count('START TRANSACTION;') == 1 and text.rstrip().endswith('COMMIT;'), name
    assert text.index('START TRANSACTION;') < text.index('DELETE FROM'), name
    inserts = re.findall(r'^INSERT INTO .*?;$', text, re.S | re.M)
    assert len(inserts) >= 2, name
    for stmt in inserts:
        assert stmt.count('\n(') <= MAX_ROWS, (name, stmt.count('\n('))

text = open(os.path.join(SQL, '2026_11_05_04_battlemon_levelup_moves.sql'), encoding='utf-8').read()
rows = [(int(n), int(sid), int(lv), mv) for n, sid, lv, mv in
        re.findall(r"^\(@bm_base \+ (\d+), (\d+), (\d+), '(\w+)'\)", text, re.M)]
assert len(rows) > 10000, len(rows)
assert [r[0] for r in rows] == list(range(1, len(rows) + 1)), 'numbering must be contiguous across batches'
by_species = {}
for _, sid, lv, mv in rows:
    levels = by_species.setdefault(sid, [])
    assert not levels or lv >= levels[-1], 'levels must ascend within species %d' % sid
    levels.append(lv)
deleted = {int(x) for x in re.search(r'WHERE `species_id` IN \(([^)]*)\)', text).group(1).replace(' ', '').split(',')}
assert deleted == set(by_species), 'every species deleted is re-inserted, and no others'
print('ok', len(rows), 'rows,', len(by_species), 'species')
