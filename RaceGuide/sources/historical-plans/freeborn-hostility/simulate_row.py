import struct, pathlib, collections

def parse(path):
    d = pathlib.Path(path).read_bytes()
    magic, recs, fields, recsize, strsize = struct.unpack_from('<4sIIII', d, 0)
    rows = {}
    for i in range(recs):
        rows[struct.unpack_from('<I', d, 20+i*recsize)[0]] = struct.unpack_from('<%dI' % fields, d, 20 + i*recsize)
    return rows

ft = parse(r'modules/mod-Faction-Free/dbc/FactionTemplate.dbc')
fa = parse(r'modules/mod-Faction-Free/dbc/Faction.dbc')

def rep_capable(faction_id):
    r = fa.get(faction_id)
    if r is None: return False
    return struct.unpack('<i', struct.pack('<I', r[1]))[0] >= 0

def hostile(a, b):
    """a.IsHostileTo(b) with the enemy/friend ID lists then masks."""
    A, B = a, b
    if B[1]:
        for x in A[6:10]:
            if x == B[1]: return True
        for x in A[10:14]:
            if x == B[1]: return False
    return bool(A[5] & B[3])

def friendly(a, b):
    if a[1] == b[1]: return True
    if b[1]:
        for x in a[6:10]:
            if x == b[1]: return False
        for x in a[10:14]:
            if x == b[1]: return True
    return bool((a[4] & b[3]) or (a[3] & b[4]))

def rank(a, b):
    if hostile(a, b): return 'HOSTILE'
    if friendly(a, b): return 'friendly'
    if a[2] & 0x2000: return 'HOSTILE'   # HATES_ALL_EXCEPT_FRIENDS
    return 'neutral'

# candidate Freeborn row
def make_row(id_, faction, flags, our, friend, hostile_):
    return (id_, faction, flags, our, friend, hostile_, 0,0,0,0, 0,0,0,0)

CANDS = {
 'proposed our9/h9': make_row(2237, 0, 72, 9, 0, 9),
 'our9/h15':         make_row(2237, 0, 72, 9, 0, 15),
 'our9/h7':          make_row(2237, 0, 72, 9, 0, 7),
 'our15/h15(f1945-like)': make_row(2237, 0, 72, 15, 0, 15),
}
alliance = ft[4]      # Night Elf player template
horde    = ft[2]      # Orc player template
human    = ft[1]
orc      = ft[2]
monster  = ft[14]
guard    = ft[11]     # Stormwind guard
civilian = ft[12]     # Stormwind civilian
bb       = ft[121]    # Booty Bay bruiser

counts = {}
for line in pathlib.Path(r'.agents/plans/freeborn-hostility/ct_faction_counts.txt').read_text().split('\n'):
    p = line.split()
    if len(p) == 2 and p[0].isdigit(): counts[int(p[0])] = int(p[1])

for name, F in CANDS.items():
    print('=== %s (row %s)' % (name, F))
    for label, other in (('NightElf player', alliance), ('Orc player', horde), ('monster', monster), ('Stormwind guard', guard), ('Stormwind civilian', civilian), ('Booty Bay', bb), ('Freeborn(self)', F)):
        print('   F -> %-18s %-8s | %-18s -> F %s' % (label, rank(F, other), label, rank(other, F)))
    # how many creature templates would treat the Freeborn as hostile (ignoring reputation path)
    nc = sum(c for fid, c in counts.items() if fid in ft and rank(ft[fid], F) == 'HOSTILE')
    nf = sum(c for fid, c in counts.items() if fid in ft and rank(F, ft[fid]) == 'HOSTILE')
    tot = sum(counts.values())
    print('   creature TEMPLATES whose mask reaction to F is hostile: %d/%d (spawn entries %d/%d)' % (
        sum(1 for fid in counts if fid in ft and rank(ft[fid], F)=='HOSTILE'), len(counts), nc, tot))
    print('   creature templates F would see hostile: %d/%d (spawn entries %d)' % (
        sum(1 for fid in counts if fid in ft and rank(F, ft[fid])=='HOSTILE'), len(counts), nf))
    print('   of the hostile-to-F ones, rep-capable (server/client use reputation instead): %d' % (
        sum(1 for fid in counts if fid in ft and rank(ft[fid], F)=='HOSTILE' and rep_capable(ft[fid][1]))))
