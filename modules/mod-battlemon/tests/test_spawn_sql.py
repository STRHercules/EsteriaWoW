"""The seeded spawn zones must be valid and must not leave a zone with almost nothing to spawn.

Uses the same rules as src/BattlemonSpawnRules.h: a species lives in a zone if either of its types is listed
(leak 0 = strangers excluded, the strictest setting), and its natural minimum level (real evolution levels, plus
STEP for each evolution that is not level-based) must be reachable at the zone's top level.
"""
import glob
import os
import re

SQL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sql', 'db-world', 'base')
TYPES = {'NORMAL', 'FIRE', 'WATER', 'ELECTRIC', 'GRASS', 'ICE', 'FIGHTING', 'POISON', 'GROUND', 'FLYING', 'PSYCHIC',
         'BUG', 'ROCK', 'GHOST', 'DRAGON', 'DARK', 'STEEL', 'FAIRY'}
MIN_SPECIES = 25   # per zone, strict mode
STEP = 8

def parse_row(line):
    """One SQL VALUES tuple -> list of strings (NULL stays 'NULL'); handles quotes and '' escapes."""
    vals, i, n = [], 1, len(line)
    while i < n:
        if line[i] == "'":
            j, buf = i + 1, []
            while True:
                if line[j] == "'":
                    if j + 1 < n and line[j + 1] == "'":
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(line[j])
                j += 1
            vals.append(''.join(buf))
            i = j + 1
        else:
            j = i
            while j < n and line[j] not in ',)':
                j += 1
            vals.append(line[i:j].strip())
            i = j
        while i < n and line[i] in ', ':
            i += 1
        if i < n and line[i] == ')':
            break
    return vals


species = {}   # id -> (internal, type1, type2, catch rate, evolutions); a later file replaces an earlier row
for path in sorted(glob.glob(os.path.join(SQL, '*catalog_species.sql'))):
    for line in open(path, encoding='utf-8'):
        if re.match(r"\(\d+, '", line):
            v = parse_row(line.strip())
            species[int(v[0])] = (v[1], v[3], '' if v[4] == 'NULL' else v[4], int(v[14]), '' if v[29] == 'NULL' else v[29])
assert len(species) > 800, len(species)

# natural minimum level: follow "who evolves into me" back to the base form, like MinLevel() in the header
by_name = {v[0]: k for k, v in species.items()}
links = {}   # species -> (prevo, evolution level or 0)
for sid, (_, _, _, _, evo) in species.items():
    parts = evo.split(',') if evo else []
    for i in range(0, len(parts) - 2, 3):
        if parts[i] in by_name:
            level = int(parts[i + 2]) if parts[i + 1].startswith('Level') and parts[i + 2].isdigit() else 0
            links.setdefault(by_name[parts[i]], (sid, level))


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
for zid, lo, hi, types, in [(int(a), int(b), int(c), d) for a, b, c, d in zones]:
    assert zid not in seen, zid
    seen.add(zid)
    assert 1 <= lo <= hi <= 100, (zid, lo, hi)
    listed = {}
    for token in types.split(','):
        name, weight = token.split(':')
        assert name in TYPES, (zid, name)
        assert float(weight) > 0, (zid, token)
        listed[name] = float(weight)
    allowed = [sid for sid, (_, t1, t2, _, _) in species.items()
               if (t1 in listed or t2 in listed) and hi >= min_level(sid)]
    if len(allowed) < MIN_SPECIES:
        thin.append((zid, len(allowed)))
assert not thin, 'zones with too few species in strict mode: %s' % thin
print('ok', len(seen), 'zones')
