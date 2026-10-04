import struct, pathlib
used = set()
for f in (r'.agents/plans/freeborn-hostility/ct_factions.txt', r'.agents/plans/freeborn-hostility/go_factions.txt'):
    p = pathlib.Path(f)
    if p.exists():
        for line in p.read_text().split():
            if line.strip().isdigit(): used.add(int(line))
data = pathlib.Path(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc').read_bytes()
magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', data, 0)
rows = {}
for i in range(recs):
    rows[struct.unpack_from('<I', data, 20+i*recsize)[0]] = struct.unpack_from('<%dI' % fields, data, 20 + i*recsize)
faction_refs = {}
for rid, r in rows.items():
    for x in r[6:14]:
        if x: faction_refs.setdefault(x, []).append(rid)
# spare rows: unused by creature/gameobject, whose faction is referenced by no other row,
# and whose own faction is not a player faction
spare = []
for rid in sorted(rows):
    r = rows[rid]
    if rid in used: continue
    if r[1] in faction_refs and any(x != rid for x in faction_refs[r[1]]): continue
    spare.append((rid, r[1], r[2], r[3], r[4], r[5]))
print('spare template rows (unreferenced faction, unused by creature/gameobject):', len(spare))
for s in spare[:25]:
    print('   id=%-5d faction=%-6d flags=%-6d our=%-3d friend=%-3d hostile=%-3d' % s)
print('base table max id', max(rows))
