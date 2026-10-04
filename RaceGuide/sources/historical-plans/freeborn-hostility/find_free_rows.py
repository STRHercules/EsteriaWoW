import struct, pathlib
used = set()
for line in pathlib.Path(r'.agents/plans/freeborn-hostility/ct_factions.txt').read_text().split():
    if line.strip().isdigit(): used.add(int(line))
data = pathlib.Path(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc').read_bytes()
magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', data, 0)
rows = {}
for i in range(recs):
    r = struct.unpack_from('<%dI' % fields, data, 20 + i*recsize)
    rows[r[0]] = r
print('creature_template uses %d distinct faction templates' % len(used))
missing = sorted(x for x in used if x not in rows)
print('used by creatures but absent from DBC:', missing[:20], '...' if len(missing)>20 else '')
unused = sorted(x for x in rows if x not in used)
print('rows in DBC but unused by creature_template: %d' % len(unused))
# candidates: ourMask has bit 8, hostile has bit 1, friendly 0
print('--- candidate rows: ourMask & 8, hostileMask & 1, friendlyMask == 0, id<=2100 ---')
for i in unused:
    r = rows[i]
    if (r[3] & 8) and (r[5] & 1) and r[4] == 0 and i <= 2100:
        print('  %5d faction=%-6d flags=%-6d our=%-3d friend=%-3d hostile=%-3d' % (i, r[1], r[2], r[3], r[4], r[5]))
print('--- rows 2185..2246 ---')
for i in sorted(rows):
    if 2180 <= i <= 2246:
        r = rows[i]
        print('  %5d faction=%-6d flags=%-6d our=%-3d friend=%-3d hostile=%-3d used_by_creature=%s' % (i, r[1], r[2], r[3], r[4], r[5], i in used))
print('highest ids in DBC:', sorted(rows)[-8:])
