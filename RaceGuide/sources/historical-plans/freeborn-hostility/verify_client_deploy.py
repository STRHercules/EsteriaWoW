import sys, hashlib, pathlib
sys.path.insert(0, r'R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools')
from cars_mount_pack import Storm, DLL_DEFAULT
import freeborn_faction_pack as M
expected = M.build_rows(M.base_table_bytes(None))[0]
storm = Storm(DLL_DEFAULT)
h = storm.open_archive(pathlib.Path(r'G:\3.3.5a - Dev\Data\patch-Z.MPQ'))
try:
    got = storm.read(h, M.DBC_ENTRY)
finally:
    storm.dll.SFileCloseArchive(h)
print('patch-Z FactionTemplate.dbc bytes', len(got), 'matches generated table:', got == expected)
print('sha256', hashlib.sha256(got).hexdigest())
rows = M.parse_wdbc(got).by_id
print('freeborn row 2237:', rows[2237])
print('nightelf row 4    :', rows[4])
