import re, pathlib
targets = [r'G:\3.3.5a - Dev\WarcraftXL.dll', r'G:\3.3.5a - Dev\Wow.exe', r'G:\3.3.5a - Dev\wxl-hub.exe']
needles = [b'FactionTemplate', b'ChrRaces', b'CreatureDisplayInfo', b'dbc-continuations', b'DBFilesClient', b'extended-dbc', b'.dbc1', b'Faction.dbc']
for t in targets:
    p = pathlib.Path(t)
    data = p.read_bytes()
    print('===', p.name, len(data))
    for n in needles:
        idx = data.find(n)
        cnt = data.count(n)
        print('   %-24s count=%-4d first=0x%X' % (n.decode(), cnt, idx if idx>=0 else -1))
