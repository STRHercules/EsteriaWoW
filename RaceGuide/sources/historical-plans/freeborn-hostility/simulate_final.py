import struct, pathlib
def parse(path):
    d = pathlib.Path(path).read_bytes()
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', d, 0)
    rows = {}
    for i in range(recs):
        rows[struct.unpack_from('<I', d, 20+i*recsize)[0]] = struct.unpack_from('<%dI' % fields, d, 20 + i*recsize)
    return rows
ft = parse(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc')
fa = parse(r'modules/mod-Faction-Free/dbc/Faction.dbc')
def rep_cap(fid):
    r = fa.get(fid)
    return r is not None and struct.unpack('<i', struct.pack('<I', r[1]))[0] >= 0
def mask_hostile(a, b):
    if b[1]:
        for x in a[6:10]:
            if x == b[1]: return True
        for x in a[10:14]:
            if x == b[1]: return False
    return bool(a[5] & b[3])
def mask_friendly(a, b):
    if a[1] == b[1]: return True
    if b[1]:
        for x in a[6:10]:
            if x == b[1]: return False
        for x in a[10:14]:
            if x == b[1]: return True
    return bool((a[4] & b[3]) or (a[3] & b[4]))

# final design: V=16 added to player ourMask; F row
V = 16
def patched_player(r):
    r = list(r); r[3] |= V; return tuple(r)
PLAYER_IDS = [1,2,3,4,5,6,115,116,1610,1629]
players = {i: patched_player(ft[i]) for i in PLAYER_IDS}
F = (2237, 9001, 0x48, 9, 6, 24, 0,0,0,0, 0,0,0,0)

counts = {}
for line in pathlib.Path(r'.agents/plans/freeborn-hostility/ct_faction_counts.txt').read_text().split('\n'):
    p = line.split()
    if len(p) == 2 and p[0].isdigit(): counts[int(p[0])] = int(p[1])
tot = sum(counts.values())

print('=== F (row %s): our=9 friend=6 hostile=24 ===' % F[0])
for label, other in (('NightElf player(patched)', players[4]), ('Orc player(patched)', players[2]),
                     ('monster 14', ft[14]), ('guard 11', ft[11]), ('civilian 12', ft[12]),
                     ('Booty Bay 121', ft[121]), ('escortee 231', ft[231]), ('Freeborn', F),
                     ('Blood Elf player(patched)', players[1610])):
    fwd = 'HOSTILE' if mask_hostile(F, other) else ('friendly' if mask_friendly(F, other) else 'neutral')
    rev = 'HOSTILE' if mask_hostile(other, F) else ('friendly' if mask_friendly(other, F) else 'neutral')
    print('   F -> %-26s %-8s | %-26s -> F %s' % (label, fwd, label, rev))

# collateral: NPC (non-player) templates the mask would call hostile to F, split by rep
groups = {'side-alliance':0,'side-horde':0,'monster':0,'neutral/other':0}
spawns = dict(groups)
bad = []
for fid, c in counts.items():
    t = ft.get(fid)
    if t is None: continue
    if mask_hostile(t, F):
        # server/client use reputation when the faction can hold reputation
        if rep_cap(t[1]): continue
        if t[3] & 8: k = 'monster'
        elif t[3] & 2: k = 'side-alliance'
        elif t[3] & 4: k = 'side-horde'
        else: k = 'neutral/other'
        groups[k] += 1; spawns[k] += c
        if k != 'monster': bad.append((fid, t[1], t[3], t[5], c))
print()
print('non-rep NPC factions whose mask calls F hostile (i.e. would aggro):')
for k in ('monster','neutral/other','side-alliance','side-horde'):
    print('   %-14s %4d templates  %6d spawn entries' % (k, groups[k], spawns[k]))
print()
print('non-monster ones (the ones that would be a regression):')
for b in sorted(bad, key=lambda x: -x[4])[:15]:
    print('   tpl %-6d faction %-6d our=%-3d hostile=%-3d spawns=%d' % b)
print()
# how many player rows does F end up hostile to, and monsters to F
print('F hostile to patched players:', [i for i,p in players.items() if mask_hostile(F, p)])
print('patched players hostile to F:', [i for i,p in players.items() if mask_hostile(p, F)])
print('player -> player hostile (should be empty):', [(a,b) for a,p in players.items() for b,q in players.items() if a!=b and mask_hostile(p,q)])
