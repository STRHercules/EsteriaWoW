"""Dev Menu - bake dressed NPCs so they show without the Dev Menu module.

Dressed NPCs (Create an NPC) use the Mirror Image trick, which needs the module on the server. This tool turns the
dressed NPCs of a Share as SQL export into normal baked NPC models, the way Blizzard ships its own dressed NPCs:
  <export>_baked.sql   the export without the module table, plus the baked models (run it on the world database)
  patch-ZZZZZZ.MPQ     the client patch: model rows + one skin texture per NPC look (players put it in Data/)

Skin textures are painted from the client's own files (classic 3.3.5 character layout). A client that renders some
races differently (HD faces) can supply ready textures with --capture <folder> (files look_<race>_<sex>_<skin>_<face>_
<hair>_<haircolor>_<facialhair>_<11 item display ids>.raw (BGRA, square) or .blp).

Needs Python 3.8+ with Pillow (pip install pillow) and the mysql command-line client.

Example:
  python bake.py --data "../WoW/Data" --exports "../server/devmenu_sql" --user root --password root
"""
import argparse, glob, io, os, re, struct, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mpq
from PIL import Image

BS = chr(92)
MIRROR = 16   # UNIT_FLAG2_MIRROR_IMAGE
# 3.3.5 character texture regions on a 256x256 layout (scaled to the real skin size)
REG = {'ArmUpper': (0, 0, 128, 64), 'ArmLower': (0, 64, 128, 64), 'Hand': (0, 128, 128, 32), 'FaceUpper': (0, 160, 128, 32),
       'FaceLower': (0, 192, 128, 64), 'TorsoUpper': (128, 0, 128, 64), 'TorsoLower': (128, 64, 128, 32),
       'LegUpper': (128, 96, 128, 64), 'LegLower': (128, 160, 128, 64), 'Foot': (128, 224, 128, 32)}
ITEM_REG = ['ArmUpper', 'ArmLower', 'Hand', 'TorsoUpper', 'TorsoLower', 'LegUpper', 'LegLower', 'Foot']
# NPCItemDisplay order: head shoulder shirt chest belt legs boots wrist gloves tabard cape -> paint order (bottom first)
PAINT = [2, 5, 6, 3, 4, 7, 8, 9]

ap = argparse.ArgumentParser(description='Bake the dressed NPCs of a Dev Menu SQL export (no module needed to show them).')
ap.add_argument('--data', required=True, help='the client Data folder (with the MPQ archives)')
ap.add_argument('--export', help='the exported .sql file (default: newest in --exports)')
ap.add_argument('--exports', default='devmenu_sql', help='folder of the exports (devmenu_sql next to worldserver)')
ap.add_argument('--mysql', default='mysql', help='mysql client executable')
ap.add_argument('--defaults-file', help='mysql option file with the login (instead of --user/--password)')
ap.add_argument('--host', default='127.0.0.1'); ap.add_argument('--port', default='3306')
ap.add_argument('--user', default='acore'); ap.add_argument('--password', default='acore')
ap.add_argument('--database', default='acore_world')
ap.add_argument('--capture', help='folder of ready skin textures (look_*.raw / .blp)')
ap.add_argument('--patch-name', default='patch-ZZZZZZ.MPQ', help='name of the client patch (must load after the other patches)')
args = ap.parse_args()

MYSQL = [args.mysql] + (['--defaults-file=' + args.defaults_file] if args.defaults_file else
                        ['-h', args.host, '-P', str(args.port), '-u', args.user]) + ['-N', '-B', args.database]
ENV = dict(os.environ)
if not args.defaults_file:
    ENV['MYSQL_PWD'] = args.password


def sql(q):
    r = subprocess.run(MYSQL + ['-e', q], capture_output=True, text=True, env=ENV)
    if r.returncode:
        sys.exit('MySQL error: ' + r.stderr.strip())
    return [l.split('\t') for l in r.stdout.splitlines()]


def progress(i, n, what):
    w = 30
    f = int(w * i / max(1, n))
    sys.stdout.write('\r[%s%s] %d/%d %s' % ('#' * f, '.' * (w - f), i, n, what[:40].ljust(40)))
    sys.stdout.flush()


# ------------------------------------------------------------------ client files (the archive that loads last wins)
def load_order(p):
    n = os.path.basename(p).lower()
    loc = os.path.basename(os.path.dirname(p)).lower() != 'data'
    m = re.match(r'patch(?:-[a-z]{4})?(?:-([a-z0-9]+))?\.mpq$', n)
    if not m:
        return (0, loc, n)
    s = m.group(1) or ''
    return (1, 0 if s == '' else 1 if s.isdigit() else 2, s, loc)


ARCS = []
for p in sorted(glob.glob(os.path.join(args.data, '*.MPQ')) + glob.glob(os.path.join(args.data, '*', '*.MPQ')), key=load_order):
    if os.path.basename(p).lower() == args.patch_name.lower():
        continue   # our own output from a previous run
    try:
        ARCS.append(mpq.MPQ(p))
    except Exception:
        pass
if not ARCS:
    sys.exit('No MPQ archives in ' + args.data)


def read(name):
    hit = None
    for m in ARCS:
        if m.has(name):
            hit = m
    return hit.read(name) if hit else None


class DBC:
    def __init__(self, data):
        _, n, self.fc, self.rs, ss = struct.unpack('<4s4I', data[:20])
        self.rows = [list(struct.unpack_from('<%dI' % (self.rs // 4), data, 20 + i * self.rs)) for i in range(n)]
        self.sb = bytearray(data[20 + n * self.rs:]) or bytearray(b'\0')
        self._pool = {}

    def s(self, o):
        return '' if not o or o >= len(self.sb) else bytes(self.sb[o:self.sb.index(0, o)]).decode('utf-8', 'replace')

    def add(self, text):
        if text not in self._pool:
            self._pool[text] = len(self.sb)
            self.sb.extend(text.encode('utf-8') + b'\0')
        return self._pool[text]

    def by_id(self):
        return {r[0]: r for r in self.rows}

    def bytes(self):
        body = b''.join(struct.pack('<%dI' % (self.rs // 4), *[v & 0xFFFFFFFF for v in r]) for r in self.rows)
        return struct.pack('<4s4I', b'WDBC', len(self.rows), self.fc, self.rs, len(self.sb)) + body + bytes(self.sb)


def dbc(n):
    d = read('DBFilesClient' + BS + n + '.dbc')
    if not d:
        sys.exit('The client has no ' + n + '.dbc')
    return DBC(d)


def blp_read(d):
    """first mip of a BLP2 (palette + 0/1/4/8-bit alpha, DXT1/3/5, raw BGRA)"""
    if d[:4] != b'BLP2':
        return Image.open(io.BytesIO(d)).convert('RGBA')
    comp, adepth, atype = d[8], d[9], d[10]
    w, h = struct.unpack_from('<II', d, 12)
    off, ln = struct.unpack_from('<I', d, 20)[0], struct.unpack_from('<I', d, 84)[0]
    px = d[off:off + ln]
    if comp == 2:
        n = 1 if atype == 0 else 2 if atype == 1 else 3
        im = Image.frombytes('RGBA', (w, h), px, 'bcn', n)
        if n == 1 and adepth == 0:
            im.putalpha(255)
        return im
    if comp == 3:
        b, g, r, a = Image.frombytes('RGBA', (w, h), px).split()
        return Image.merge('RGBA', (r, g, b, a))
    pal = struct.unpack_from('<256I', d, 148)
    n = w * h
    out = bytearray(n * 4)
    for i in range(n):
        c = pal[px[i]]
        out[i * 4:i * 4 + 3] = bytes(((c >> 16) & 255, (c >> 8) & 255, c & 255))
        if adepth == 0:
            a = 255
        elif adepth == 8:
            a = px[n + i]
        elif adepth == 1:
            a = 255 if px[n + (i >> 3)] >> (i & 7) & 1 else 0
        else:
            a = ((px[n + (i >> 1)] >> ((i & 1) * 4)) & 15) * 17
        out[i * 4 + 3] = a
    return Image.frombytes('RGBA', (w, h), bytes(out))


def blp_argb(im):
    """BLP2, uncompressed BGRA with a full mip chain"""
    mips, cur = [], im
    while True:
        r, g, b, a = cur.split()
        mips.append(Image.merge('RGBA', (b, g, r, a)).tobytes())
        if (cur.width == 1 and cur.height == 1) or len(mips) == 16:
            break
        cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.LANCZOS)
    off, offs, lens = 148 + 1024, [], []
    for m in mips:
        offs.append(off); lens.append(len(m)); off += len(m)
    offs += [0] * (16 - len(offs)); lens += [0] * (16 - len(lens))
    head = struct.pack('<4sIBBBBII', b'BLP2', 1, 3, 8, 8, 1, im.width, im.height) + struct.pack('<16I', *offs) + struct.pack('<16I', *lens)
    return head + b'\0' * 1024 + b''.join(mips)


def img(path):
    d = read(path)
    return blp_read(d) if d else None


# ------------------------------------------------------------------ painting the skin
cs, idi = dbc('CharSections'), dbc('ItemDisplayInfo')
items = idi.by_id()


def section(race, sex, base, var, color):
    for r in cs.rows:
        if r[1] == race and r[2] == sex and r[3] == base and r[8] == var and r[9] == color:
            return [cs.s(x) for x in r[4:7]]
    return None


def paste(canvas, tex, reg):
    if tex is None:
        return
    s = canvas.width / 256
    x, y, w, h = [int(v * s) for v in REG[reg]]
    canvas.alpha_composite(tex.resize((w, h), Image.LANCZOS), (x, y))


def hd_face(face):
    """HD faces carry an iris swatch at the bottom of the lower face texture; their scalp textures don't fit the layout"""
    k = face.width / 256
    return face.crop((int(127 * k), int(108 * k), int(147 * k), int(126 * k))).convert('L').getextrema()[0] <= 90


def paint(race, sex, skin, face, hair, hcol, facial, npc):
    base = section(race, sex, 0, 0, skin)
    if not base:
        return None
    body = img(base[0])
    if body is None:
        return None
    canvas = Image.new('RGBA', body.size)
    canvas.alpha_composite(body)
    extra = img(base[1]) if base[1] else None
    if extra and extra.size == body.size:
        canvas.alpha_composite(extra)
    hd = False
    f = section(race, sex, 1, face, skin)
    if f:
        lower = img(f[0]) if f[0] else None
        paste(canvas, lower, 'FaceLower')
        paste(canvas, img(f[1]) if f[1] else None, 'FaceUpper')
        hd = lower is not None and hd_face(lower)
    fh = section(race, sex, 2, facial, hcol)
    if fh:
        paste(canvas, img(fh[0]) if fh[0] else None, 'FaceLower')
        paste(canvas, img(fh[1]) if fh[1] else None, 'FaceUpper')
    sc = None if hd else section(race, sex, 3, hair, hcol)
    if sc:
        paste(canvas, img(sc[1]) if sc[1] else None, 'FaceLower')
        paste(canvas, img(sc[2]) if sc[2] else None, 'FaceUpper')
    uw = section(race, sex, 4, 0, skin)
    if uw:
        paste(canvas, img(uw[0]) if uw[0] else None, 'LegUpper')
        paste(canvas, img(uw[1]) if uw[1] else None, 'TorsoUpper')
    for slot in PAINT:
        d = items.get(npc[slot])
        if not d:
            continue
        for i, reg in enumerate(ITEM_REG):
            name = idi.s(d[15 + i])
            if not name:
                continue
            for suf in ('_M' if sex == 0 else '_F', '_U'):
                tex = img(BS.join(['Item', 'TextureComponents', reg + 'Texture', name + suf + '.blp']))
                if tex:
                    paste(canvas, tex, reg)
                    break
    return canvas


def capture(sex, look, npc):
    if not args.capture:
        return None
    want = '_'.join(str(v) for v in [sex] + look + npc)
    best = None
    for f in glob.glob(os.path.join(args.capture, 'look_*')):
        if f.endswith(('.raw', '.blp')) and '_'.join(os.path.basename(f).split('.')[0].split('_')[2:]) == want:
            if best is None or os.path.getmtime(f) > os.path.getmtime(best):
                best = f
    if not best:
        return None
    data = open(best, 'rb').read()
    if best.endswith('.blp'):
        return blp_read(data)
    n = int((len(data) // 4) ** 0.5)
    im = Image.frombytes('RGBA', (n, n), data, 'raw', 'BGRA')
    im.putalpha(255)
    return im


# ------------------------------------------------------------------ the export
src = args.export or max(glob.glob(os.path.join(args.exports, '*.sql')), key=os.path.getmtime, default=None)
if not src or src.endswith('_baked.sql'):
    sys.exit('No export found (press Export SQL in the Dev Menu first, or pass --export)')
text = open(src, encoding='utf-8').read()
base = os.path.splitext(src)[0]
print('Export:', src)

entries = sorted({int(m) for m in re.findall(r"DELETE FROM `coa_npc_outfit` WHERE `entry` = (\d+);", text)})
outfits = {}
for e in entries:
    r = sql('SELECT outfit FROM coa_npc_outfit WHERE entry = %d' % e)
    if r:
        outfits[e] = [int(v) for v in r[0][0].split(',')]
if not outfits:
    sys.exit('This export has no dressed NPCs: share it as it is.')
print(len(outfits), 'dressed NPC types')

ext, cdi, races = dbc('CreatureDisplayInfoExtra'), dbc('CreatureDisplayInfo'), dbc('ChrRaces').by_id()
cdi_by = cdi.by_id()
sql("CREATE TABLE IF NOT EXISTS coa_npc_bake (entry INT UNSIGNED NOT NULL PRIMARY KEY, display INT UNSIGNED NOT NULL, "
    "extra INT UNSIGNED NOT NULL) ENGINE=InnoDB COMMENT='Dev Menu: baked model ids per dressed NPC type'")
known = {int(r[0]): (int(r[1]), int(r[2])) for r in sql('SELECT entry, display, extra FROM coa_npc_bake')}
srv_cdi = int(sql('SELECT IFNULL(MAX(ID), 0) FROM creaturedisplayinfo_dbc')[0][0])
srv_ext = int(sql('SELECT IFNULL(MAX(ID), 0) FROM creaturedisplayinfoextra_dbc')[0][0])
next_cdi = max([r[0] for r in cdi.rows] + [d for d, _ in known.values()] + [srv_cdi]) + 1
next_ext = max([r[0] for r in ext.rows] + [x for _, x in known.values()] + [srv_ext]) + 1


def item_display(item):
    if item <= 0:
        return -item
    r = sql('SELECT displayid FROM item_template WHERE entry = %d' % item)
    return int(r[0][0]) if r else 0


files, baked, painted, skipped = {}, [], 0, []
for i, (entry, o) in enumerate(sorted(outfits.items())):
    progress(i, len(outfits), 'NPC %d' % entry)
    race, sex, skin, face, hair, hcol, facial = o[:7]
    armor = [item_display(v) for v in o[7:18]]
    npc = armor[0:9] + [armor[10], armor[9]]   # Dev Menu slots end back, tabard; the client wants tabard, cape
    rr = races.get(race)
    base_display = (rr[4] if sex == 0 else rr[5]) if rr else 0
    if base_display not in cdi_by:
        skipped.append('%d (race %d is not in this client)' % (entry, race))
        continue
    canvas = capture(sex, [skin, face, hair, hcol, facial], npc)
    if canvas is None:
        canvas = paint(race, sex, skin, face, hair, hcol, facial, npc)
        painted += 1
    if canvas is None:
        skipped.append('%d (no skin texture for race %d)' % (entry, race))
        continue
    disp, xid = known.get(entry, (0, 0))
    if not disp:
        disp, xid = next_cdi, next_ext
        next_cdi += 1; next_ext += 1
        sql('REPLACE INTO coa_npc_bake (entry, display, extra) VALUES (%d, %d, %d)' % (entry, disp, xid))
    name = 'DevMenu%d.blp' % xid
    files[BS.join(['Textures', 'BakedNpcTextures', name])] = blp_argb(canvas.convert('RGBA'))
    erow = [xid, race, sex, skin, face, hair, hcol, facial] + npc + [0, ext.add(name)]
    ext.rows = [r for r in ext.rows if r[0] != xid] + [erow]
    crow = list(cdi_by[base_display]); crow[0], crow[3] = disp, xid
    cdi.rows = [r for r in cdi.rows if r[0] != disp] + [crow]
    baked.append((entry, disp, xid, erow, crow, base_display))
progress(len(outfits), len(outfits), 'done')
print()
if not baked:
    sys.exit('Nothing could be baked: ' + '; '.join(skipped))

files['DBFilesClient' + BS + 'CreatureDisplayInfoExtra.dbc'] = ext.bytes()
files['DBFilesClient' + BS + 'CreatureDisplayInfo.dbc'] = cdi.bytes()
arc = os.path.join(os.path.dirname(os.path.abspath(src)), args.patch_name)
mpq.write(arc, files)
check = mpq.MPQ(arc)
assert all(check.read(n) == d for n, d in files.items()), 'the written patch does not read back'

# server SQL: the export without the module table, plus the baked models
keep = [s for s in re.split(r'(?<=;)\n', text) if 'coa_npc_outfit' not in s]
out = ['\n'.join(keep).rstrip(), '', '-- Dressed NPCs baked into normal models (client patch: %s). No Dev Menu module needed.' % args.patch_name]
ccols = [r[0] for r in sql('SHOW COLUMNS FROM creaturedisplayinfo_dbc')]
for entry, disp, xid, erow, crow, bdisp in baked:
    out.append('DELETE FROM `creaturedisplayinfoextra_dbc` WHERE `ID` = %d;' % xid)
    out.append("INSERT INTO `creaturedisplayinfoextra_dbc` VALUES (%s,'%s');" % (','.join(str(v) for v in erow[:20]), ext.s(erow[20])))
    cv = []
    for k, c in enumerate(ccols):
        lc = c.lower()
        cv.append("''" if 'texture' in lc else repr(struct.unpack('<f', struct.pack('<I', crow[k]))[0]) if lc == 'creaturemodelscale' else str(crow[k]))
    out.append('DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = %d;' % disp)
    out.append('INSERT INTO `creaturedisplayinfo_dbc` (%s) VALUES (%s);' % (', '.join('`%s`' % c for c in ccols), ','.join(cv)))
    mi = sql('SELECT BoundingRadius, CombatReach, Gender FROM creature_model_info WHERE DisplayID = %d' % bdisp)
    br, cr, g = mi[0] if mi else ('0.3', '1.5', str(erow[2]))
    out.append('DELETE FROM `creature_model_info` WHERE `DisplayID` = %d;' % disp)
    out.append('INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) '
               'VALUES (%d, %s, %s, %s, 0);' % (disp, br, cr, g))
    out.append('DELETE FROM `creature_template_model` WHERE `CreatureID` = %d;' % entry)
    out.append('INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) '
               'VALUES (%d, 0, %d, 1, 1);' % (entry, disp))
    out.append('UPDATE `creature_template` SET `unit_flags2` = `unit_flags2` & ~%d WHERE `entry` = %d;' % (MIRROR, entry))
dst = base + '_baked.sql'
open(dst, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')

print('Wrote', dst)
print('Wrote', arc, '(%d KB)' % (os.path.getsize(arc) // 1024))
print('%d baked (%d painted, %d from --capture)' % (len(baked), painted, len(baked) - painted))
for s in skipped:
    print('Skipped', s)
