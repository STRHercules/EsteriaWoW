import struct, pathlib
def parse(path):
    d = pathlib.Path(path).read_bytes()
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', d, 0)
    rows = {}
    for i in range(recs):
        rows[struct.unpack_from('<I', d, 20+i*recsize)[0]] = struct.unpack_from('<%dI' % fields, d, 20 + i*recsize)
    strbase = 20 + recs*recsize
    return rows, d, strbase
cr, dcr, scr = parse(r'.agents/plans/freeborn-hostility/ChrRaces.server.dbc')
def s(off):
    if off == 0: return ''
    e = dcr.find(b'\0', scr+off); return dcr[scr+off:e].decode('utf-8','replace')
print('=== deployed server ChrRaces: race -> FactionID / TeamID / alliance ===')
factions = {}
for rid in sorted(cr):
    r = cr[rid]
    factions.setdefault(r[2], []).append(rid)
    print('  race %-3d FactionID=%-6d TeamID=%-3d alliance=%-2d name=%s' % (rid, r[2], r[7], r[13], s(r[14])))
print()
print('distinct FactionIDs used by races:', sorted(factions.items()))
ft, dft, sft = parse(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc')
print()
print('=== do those FactionIDs exist in the deployed FactionTemplate.dbc? ===')
for fid in sorted(factions):
    print('  FactionID %-6d present_in_server_FactionTemplate=%s' % (fid, fid in ft))
