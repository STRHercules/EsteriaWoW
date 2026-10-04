import sys, pathlib
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
from cars_mount_pack import Storm, DLL_DEFAULT
from pathlib import Path
data = Path(r'G:\3.3.5a - Dev\Data')
key = 'DBFilesClient\\FactionTemplate.dbc'
archives = ['patch.MPQ','patch-2.MPQ','patch-3.MPQ','patch-4.mpq','PATCH-A.MPQ','Patch-B.MPQ','Patch-C.MPQ','Patch-D.MPQ','Patch-E.MPQ','Patch-F.MPQ','Patch-G.MPQ','Patch-Housing.MPQ','patch-K.mpq','Patch-O.mpq','PATCH-V.mpq','PATCH-X.MPQ','Patch-Y.MPQ','patch-Z.MPQ','enUS\\patch-enUS-Z.MPQ']
print('dll', DLL_DEFAULT, DLL_DEFAULT.exists())
storm = Storm(DLL_DEFAULT)
import hashlib
for name in archives:
    p = data / name
    if not p.exists():
        print('%-28s MISSING' % name); continue
    try:
        h = storm.open_archive(p)
    except Exception as e:
        print('%-28s open failed %s' % (name, e)); continue
    try:
        try:
            blob = storm.read(h, key)
        except OSError:
            print('%-28s no FactionTemplate.dbc' % name); continue
        print('%-28s FactionTemplate.dbc %d bytes sha=%s' % (name, len(blob), hashlib.sha256(blob).hexdigest()[:16]))
    finally:
        storm.dll.SFileCloseArchive(h)
