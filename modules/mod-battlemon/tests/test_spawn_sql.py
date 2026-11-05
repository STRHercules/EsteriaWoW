"""The seeded spawn zones must be valid and must not leave a zone with almost nothing to spawn.

Uses the same rules as src/BattlemonSpawnRules.h: a species lives in a zone if either of its types is listed
(leak 0 = strangers excluded, the strictest setting), and its natural minimum level (real evolution levels, plus
STEP for each evolution that is not level-based) must be reachable at the zone's top level.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog import SQL, evolution_links, load_species

TYPES = {'NORMAL', 'FIRE', 'WATER', 'ELECTRIC', 'GRASS', 'ICE', 'FIGHTING', 'POISON', 'GROUND', 'FLYING', 'PSYCHIC',
         'BUG', 'ROCK', 'GHOST', 'DRAGON', 'DARK', 'STEEL', 'FAIRY'}
MIN_SPECIES = 25   # per zone, strict mode
STEP = 8

species = load_species()
links = evolution_links(species)
assert len(species) > 800, len(species)


def min_level(sid):
    chain = []
    while sid in links and len(chain) < 8:
        chain.append(links[sid])
        sid = links[sid][0]
    level = 1
    for _, evo_level in reversed(chain):
        level = max(level, evo_level) if evo_level else level + STEP
    return min(level, 100)


# the data really does carry the evolution levels the rule relies on
assert min_level(2) == 16 and min_level(3) == 32, (min_level(2), min_level(3))   # Ivysaur, Venusaur
assert min_level(25) <= 12, min_level(25)   # Pikachu: a baby's happiness evolution must not hold it back

text = open(os.path.join(SQL, '2026_11_05_08_battlemon_spawns.sql'), encoding='utf-8').read()
zones = re.findall(r"^\((\d+), (\d+), (\d+), '([A-Z0-9:,.]*)', '(?:[^']|'')*'\)", text, re.M)
assert len(zones) > 50, len(zones)
seen = set()
thin = []
for zid, lo, hi, types in [(int(a), int(b), int(c), d) for a, b, c, d in zones]:
    assert zid not in seen, zid
    seen.add(zid)
    assert 1 <= lo <= hi <= 100, (zid, lo, hi)
    listed = {}
    for token in types.split(','):
        name, weight = token.split(':')
        assert name in TYPES, (zid, name)
        assert float(weight) > 0, (zid, token)
        listed[name] = float(weight)
    allowed = [sid for sid, s in species.items()
               if (s['type1'] in listed or s['type2'] in listed) and hi >= min_level(sid)]
    if len(allowed) < MIN_SPECIES:
        thin.append((zid, len(allowed)))
assert not thin, 'zones with too few species in strict mode: %s' % thin
print('ok', len(seen), 'zones')
