import struct, sys, pathlib

def read_dbc(path):
    data = pathlib.Path(path).read_bytes()
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', data, 0)
    assert magic == b'WDBC', magic
    base = 20
    rows = []
    for i in range(recs):
        off = base + i*recsize
        rows.append(struct.unpack_from('<%dI' % fields, data, off))
    strbase = base + recs*recsize
    strings = data[strbase:strbase+strsize]
    return fields, rows, strings

def s(strings, off):
    if off == 0: return ''
    end = strings.find(b'\0', off)
    return strings[off:end].decode('utf-8', 'replace')

ft = r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc'
fields, rows, strings = read_dbc(ft)
print('FactionTemplate.dbc fields=%d rows=%d' % (fields, len(rows)))
byid = {r[0]: r for r in rows}
print('--- player-ish rows (1-6, 8, 115, 116, 1610, 1629) and neighbours ---')
for i in [1,2,3,4,5,6,8,115,116,1610,1629,1801,1802]:
    r = byid.get(i)
    if r: print(i, 'faction=%d flags=%d our=%d friend=%d hostile=%d enemies=%s friends=%s' % (r[1],r[2],r[3],r[4],r[5],[x for x in r[6:10] if x],[x for x in r[10:14] if x]))

fa = r'modules/mod-Faction-Free/dbc/Faction.dbc'
fields2, rows2, strings2 = read_dbc(fa)
print()
print('Faction.dbc fields=%d rows=%d' % (fields2, len(rows2)))
for r in rows2:
    if r[0] in (1,2,3,4,5,6,115,116,1610,1629,72,69,67,469):
        print('  Faction', r[0], repr(s(strings2, r[1])), 'repListId=%d' % r[2], 'flags=%d' % r[3] if len(r)>3 else '')
print()
print('--- max ID and all rows whose hostileMask has both 2 and 4 ---')
print('max id', max(byid))
for i in sorted(byid):
    r = byid[i]
    if (r[5] & 2) and (r[5] & 4):
        print('  %5d faction=%-5d flags=%-5d our=%-3d friend=%-3d hostile=%-3d %s' % (i, r[1], r[2], r[3], r[4], r[5], repr(s(strings2, 0))))
