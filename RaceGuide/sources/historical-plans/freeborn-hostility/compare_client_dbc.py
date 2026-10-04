import struct, sys, hashlib
from pathlib import Path
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
from cars_mount_pack import Storm, DLL_DEFAULT

def parse(data):
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', data, 0)
    assert magic == b'WDBC'
    rows = {}
    for i in range(recs):
        r = struct.unpack_from('<%dI' % fields, data, 20 + i*recsize)
        rows[r[0]] = r
    return fields, recsize, rows

storm = Storm(DLL_DEFAULT)
data_dir = Path(r'G:\3.3.5a - Dev\Data')
out = {}
for arc, name in (('Patch-F.MPQ','Patch-F'), ('PATCH-A.MPQ','PATCH-A')):
    h = storm.open_archive(data_dir / arc)
    try:
        blob = storm.read(h, 'DBFilesClient\\FactionTemplate.dbc')
    finally:
        storm.dll.SFileCloseArchive(h)
    out[name] = (blob, parse(blob))
mod = Path(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc').read_bytes()
print('module file sha', hashlib.sha256(mod).hexdigest()[:16], len(mod))
for name in ('Patch-F','PATCH-A'):
    blob, (fields, recsize, rows) = out[name]
    print('%s sha=%s fields=%d recsize=%d rows=%d maxid=%d' % (name, hashlib.sha256(blob).hexdigest()[:16], fields, recsize, len(rows), max(rows)))

frows = out['Patch-F'][1][2]
arows = out['PATCH-A'][1][2]
ids = sorted(set(frows) | set(arows))
diff = [i for i in ids if frows.get(i) != arows.get(i)]
print('rows differing between Patch-F and PATCH-A:', len(diff))
for i in diff[:40]:
    print('  id %-5d F=%s' % (i, frows.get(i)))
    print('           A=%s' % (arows.get(i),))
print()
print('=== notable NPC/player rows in Patch-F (effective) ===')
for i in (1,2,3,4,5,6,8,10,11,12,14,16,29,35,55,57,68,72,79,80,84,85,104,105,115,116,120,121,149,150,1610,1629,1732,1733,1734,1735,1801,1802,1891,1892,1920,2189,2190,2191):
    r = frows.get(i)
    if r:
        print('  %5d faction=%-6d flags=%-6d our=%-3d friend=%-3d hostile=%-3d en=%s fr=%s' % (i, r[1], r[2], r[3], r[4], r[5], [x for x in r[6:10] if x], [x for x in r[10:14] if x]))
