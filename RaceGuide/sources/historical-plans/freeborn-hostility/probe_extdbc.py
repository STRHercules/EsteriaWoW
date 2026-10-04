import pathlib
p = pathlib.Path(r'G:\3.3.5a - Dev\Extensions\wxl-extended-dbc\wxl-extended-dbc.dll')
d = p.read_bytes()
print('size', len(d))
for n in [b'dbc-continuations', b'.dbc1', b'FactionTemplate', b'ChrRaces', b'CreatureDisplayInfo', b'DBFilesClient', b'manifest', b'.dbc']:
    print('%-22s count=%d' % (n.decode(), d.count(n)))
# print printable strings containing "dbc" or "continu"
import re
strs = re.findall(rb'[\x20-\x7e]{6,}', d)
hits = [s.decode() for s in strs if (b'dbc' in s.lower() or b'continu' in s.lower() or b'Faction' in s)]
print('--- strings with dbc/continu/Faction ---')
for s in hits[:60]: print('  ', s)
