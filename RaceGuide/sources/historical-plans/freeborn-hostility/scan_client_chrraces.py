import struct, sys, hashlib, pathlib
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
from cars_mount_pack import Storm, DLL_DEFAULT
data_dir = pathlib.Path(r'G:\3.3.5a - Dev\Data')
keys = ['DBFilesClient\\ChrRaces.dbc', 'DBFilesClient\\Faction.dbc', 'DBFilesClient\\FactionGroup.dbc']
archives = ['Patch-C.MPQ','Patch-D.MPQ','Patch-E.MPQ','Patch-F.MPQ','Patch-G.MPQ','Patch-Y.MPQ','patch-Z.MPQ','enUS\\patch-enUS-Z.MPQ','PATCH-A.MPQ']
storm = Storm(DLL_DEFAULT)

def parse(blob):
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', blob, 0)
    rows = {}
    for i in range(recs):
        rows[struct.unpack_from('<I', blob, 20+i*recsize)[0]] = struct.unpack_from('<%dI' % fields, blob, 20 + i*recsize)
    return fields, recsize, rows

for name in archives:
    p = data_dir / name
    if not p.exists(): continue
    try:
        h = storm.open_archive(p)
    except Exception as e:
        print('%-24s open failed' % name); continue
    try:
        found = []
        for k in keys:
            try:
                blob = storm.read(h, k)
                found.append((k.split('\\')[-1], len(blob), hashlib.sha256(blob).hexdigest()[:12], blob))
            except OSError:
                pass
        if found:
            print('%-24s %s' % (name, ', '.join('%s(%d,%s)' % (n, l, s) for n, l, s, _ in found)))
            for n, l, s, blob in found:
                if n == 'ChrRaces.dbc':
                    f, rs, rows = parse(blob)
                    for rid in (1,2,4,15,16):
                        r = rows.get(rid)
                        if r: print('      race %-3d FactionID=%-6d TeamID=%-3d' % (rid, r[2], r[7]))
    finally:
        storm.dll.SFileCloseArchive(h)
