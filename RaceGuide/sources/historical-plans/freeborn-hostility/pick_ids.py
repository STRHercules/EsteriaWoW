import struct, pathlib
def parse(path):
    d = pathlib.Path(path).read_bytes()
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', d, 0)
    rows = {}
    for i in range(recs):
        rows[struct.unpack_from('<I', d, 20+i*recsize)[0]] = struct.unpack_from('<%dI' % fields, d, 20 + i*recsize)
    return rows
ft = parse(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc')
fa = parse(r'modules/mod-Faction-Free/dbc/Faction.dbc')
used_rows = set()
for f in (r'.agents/plans/freeborn-hostility/ct_factions.txt', r'.agents/plans/freeborn-hostility/go_factions.txt'):
    p = pathlib.Path(f)
    if p.exists():
        used_rows |= {int(x) for x in p.read_text().split() if x.strip().isdigit()}
row_factions = {}
for rid, r in ft.items():
    row_factions.setdefault(r[1], []).append(rid)
# Faction ids referenced by any template row
referenced_factions = set(row_factions)
print('spare Faction.dbc ids (repListID<0, not used by any FactionTemplate row):')
spares = []
for fid in sorted(fa):
    r = fa[fid]
    rep = struct.unpack('<i', struct.pack('<I', r[1]))[0]
    if rep < 0 and fid not in referenced_factions:
        spares.append((fid, r[18]))
for s in spares[:20]:
    print('   faction id %-6d team=%d' % s)
print('total spare faction ids:', len(spares))
print()
print('candidate rows to host the Freeborn template (unused by creature/gameobject template):')
for rid in sorted(ft):
    if rid in used_rows:
        continue
    r = ft[rid]
    print('   row %-5d faction=%-6d flags=%-6d our=%-3d friend=%-3d hostile=%-3d' % (rid, r[1], r[2], r[3], r[4], r[5]))
