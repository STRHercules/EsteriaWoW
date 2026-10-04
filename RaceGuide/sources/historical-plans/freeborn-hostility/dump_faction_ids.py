import struct, pathlib
def parse(path):
    d = pathlib.Path(path).read_bytes()
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', d, 0)
    rows = {}
    for i in range(recs):
        r = struct.unpack_from('<%dI' % fields, d, 20 + i*recsize)
        rows[r[0]] = r
    strbase = 20 + recs*recsize
    return fields, rows, d, strbase, strsize
f, rows, d, sb, ss = parse(r'modules/mod-Faction-Free/dbc/Faction.dbc')
print('Faction.dbc fields', f, 'rows', len(rows))
for i in (1,2,3,4,5,6,8,9,14,21,67,69,72,469,914,927,1145):
    r = rows.get(i)
    if r: print('  id=%-5d reputationListID=%-6d team=%-6d r3=%s' % (i, struct.unpack('<i', struct.pack('<I', r[1]))[0], r[18], r[2:6]))
