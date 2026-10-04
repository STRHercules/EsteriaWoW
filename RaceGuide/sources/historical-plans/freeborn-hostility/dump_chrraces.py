import struct, pathlib
def parse(path):
    d = pathlib.Path(path).read_bytes()
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', d, 0)
    rows = {}
    for i in range(recs):
        rows[struct.unpack_from('<I', d, 20+i*recsize)[0]] = struct.unpack_from('<%dI' % fields, d, 20 + i*recsize)
    strbase = 20 + recs*recsize
    return rows, d, strbase

ft, dft, sft = parse(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc')
print('--- FactionTemplate rows whose enemyFaction list contains a player faction id (1..9,914,927,1145) ---')
PLAYER_FACTIONS = {1,2,3,4,5,6,8,9,914,927,1145}
for i in sorted(ft):
    r = ft[i]
    en = [x for x in r[6:10] if x]
    if en and (set(en) & PLAYER_FACTIONS):
        print('   row %-5d faction=%-6d flags=%-6d our=%-3d fr=%-3d h=%-3d enemy=%s friendly=%s used_by_creature=%s' % (i, r[1], r[2], r[3], r[4], r[5], en, [x for x in r[10:14] if x], ''))
print()
cr, dcr, scr = parse(r'.agents/plans/freeborn-hostility/ChrRaces.server.dbc')
def s(off):
    if off == 0: return ''
    e = dcr.find(b'\0', scr+off); return dcr[scr+off:e].decode('utf-8','replace')
print('--- ChrRaces (server, deployed): race -> FactionID (field 3?) / TeamID (field 7?) ---')
for rid in sorted(cr):
    r = cr[rid]
    print('   race %-3d factionID=%-6d teamID=%-3d name=%s' % (rid, r[3], r[7], s(r[17]) if len(r) > 17 else ''))
