import pathlib, re
d = pathlib.Path(r'G:\3.3.5a - Dev\Extensions\wxl-extended-dbc\wxl-extended-dbc.dll').read_bytes()
low = d.lower()
for n in [b'factiontempl', b'factiontemplate', b'chrraces', b'skillraceclassinfo', b'areatable', b'creaturedisplayinfo']:
    idx = low.find(n)
    print('%-24s index=0x%X' % (n.decode(), idx if idx>=0 else -1))
# show context around 'FactionGroup'
i = d.find(b'FactionGroup')
print('context around FactionGroup:')
print(repr(d[max(0,i-260):i+260]))
i = d.find(b'CreatureDisplayInfo')
print('context around CreatureDisplayInfo:')
print(repr(d[max(0,i-60):i+120]))
