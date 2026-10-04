import struct, pathlib
used = set(int(x) for x in pathlib.Path(r'.agents/plans/freeborn-hostility/ct_factions.txt').read_text().split() if x.strip().isdigit())
data = pathlib.Path(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc').read_bytes()
magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', data, 0)
rows = {}
for i in range(recs):
    r = struct.unpack_from('<%dI' % fields, data, 20 + i*recsize)
    rows[r[0]] = r
# faction ids referenced by other templates (identity collisions)
fc = {}
for i, r in rows.items(): fc.setdefault(r[1], []).append(i)
print('--- rows: (ourMask & 9) == 9 and (hostileMask & 9) == 9 and friendlyMask == 0 ---')
for i in sorted(rows):
    r = rows[i]
    if (r[3] & 9) == 9 and (r[5] & 9) == 9 and r[4] == 0:
        print('  %5d faction=%-6d flags=%-6d our=%-3d friend=%-3d hostile=%-3d used_by_creature=%-5s same_faction_rows=%s' % (i, r[1], r[2], r[3], r[4], r[5], i in used, fc[r[1]]))
print()
print('--- rows: our has 1|8, hostile has 1 and 8, any friendly, unused ---')
for i in sorted(rows):
    r = rows[i]
    if i in used: continue
    if (r[3] & 9) == 9 and (r[5] & 1) and (r[5] & 8):
        print('  %5d faction=%-6d flags=%-6d our=%-3d friend=%-3d hostile=%-3d same_faction_rows=%s' % (i, r[1], r[2], r[3], r[4], r[5], fc[r[1]]))
print()
print('--- unused factions (no template row uses them) sample of Faction.dbc ids with reputationListID<0 ---')
