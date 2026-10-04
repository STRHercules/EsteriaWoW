import pathlib
def u16(s): return s.encode('utf-16-le')
needles16 = ['FactionTemplate','ChrRaces','CreatureDisplayInfo','dbc-continuations','.dbc1','DBFilesClient','extended-dbc','Spell.dbc']
for t in [r'G:\3.3.5a - Dev\WarcraftXL.dll', r'G:\3.3.5a - Dev\Wow.exe', r'G:\3.3.5a - Dev\Client.dll']:
    p = pathlib.Path(t); data = p.read_bytes()
    print('===', p.name, len(data))
    for n in needles16:
        print('   utf16 %-24s count=%d' % (n, data.count(u16(n))))
    # short ascii 'dbc' occurrences
    print('   ascii "dbc" count', data.count(b'dbc'), ' "DBC" count', data.count(b'DBC'))
