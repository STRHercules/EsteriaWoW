# Minimal MPQ v1 reader with file-content encryption, FIX_KEY and sector compression (zlib / bzip2 / pkware).
# mpyq refuses encrypted files; Esteria's client archives encrypt every file including (listfile).
import struct, zlib, bz2, os

_ct = [0] * 0x500
_seed = 0x00100001
for _i in range(0x100):
    _idx = _i
    for _j in range(5):
        _seed = (_seed * 125 + 3) % 0x2AAAAB; _t1 = (_seed & 0xFFFF) << 16
        _seed = (_seed * 125 + 3) % 0x2AAAAB; _t2 = _seed & 0xFFFF
        _ct[_idx] = _t1 | _t2; _idx += 0x100

def hsh(s, t):
    s1, s2 = 0x7FED7FED, 0xEEEEEEEE
    for ch in s.upper().replace('/', '\\'):
        v = ord(ch); s1 = _ct[(t << 8) + v] ^ ((s1 + s2) & 0xFFFFFFFF); s2 = (v + s1 + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return s1

def decrypt(data, key):
    n = len(data) // 4
    out = list(struct.unpack('<%dI' % n, data[:n * 4]))
    s = 0xEEEEEEEE
    for i in range(n):
        s = (s + _ct[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        v = out[i] ^ ((key + s) & 0xFFFFFFFF)
        out[i] = v
        key = ((((~key) << 0x15) + 0x11111111) & 0xFFFFFFFF) | (key >> 0x0B)
        s = (v + s + (s << 5) + 3) & 0xFFFFFFFF
    return struct.pack('<%dI' % n, *out) + data[n * 4:]

EXISTS, ENCRYPTED, FIX_KEY, SINGLE, IMPLODE, COMPRESS = 0x80000000, 0x10000, 0x20000, 0x1000000, 0x100, 0x200

def _explode(data):
    import importlib
    return importlib.import_module('pkware_explode').explode(data)

def _decompress(sec):
    mask = sec[0]
    body = sec[1:]
    if mask & 0x10:
        body = bz2.decompress(body); mask &= ~0x10
    if mask & 0x08:
        body = _explode(body); mask &= ~0x08
    if mask & 0x02:
        body = zlib.decompress(body); mask &= ~0x02
    if mask:
        raise ValueError('unsupported compression mask 0x%x' % sec[0])
    return body

class MPQ:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        d = self.f.read(512)
        off = d.find(b'MPQ\x1a')
        while off < 0:
            raise ValueError('no MPQ header in ' + path)
        self.base = off
        _, hsize, asize, ver, bsz, hto, bto, hcount, bcount = struct.unpack_from('<4sIIHHIIII', d, off)
        hi_hto = hi_bto = 0
        if ver >= 1:
            self.f.seek(off + 32)
            ext = self.f.read(12)
            if len(ext) == 12:
                _, hi_hto, hi_bto = struct.unpack('<QHH', ext)
        self.sector = 512 << bsz
        self.f.seek(off + hto + (hi_hto << 32))
        ht = decrypt(self.f.read(hcount * 16), hsh('(hash table)', 3))
        self.hashes = [struct.unpack_from('<IIHHI', ht, i * 16) for i in range(hcount)]
        self.f.seek(off + bto + (hi_bto << 32))
        bt = decrypt(self.f.read(bcount * 16), hsh('(block table)', 3))
        self.blocks = [list(struct.unpack_from('<4I', bt, i * 16)) for i in range(bcount)]
        self.hcount = hcount

    def find(self, name):
        name = name.replace('/', '\\')
        a, b, start = hsh(name, 1), hsh(name, 2), hsh(name, 0) % self.hcount
        i = start
        while True:
            e = self.hashes[i]
            if e[4] == 0xFFFFFFFF:
                return None
            if e[0] == a and e[1] == b and e[4] != 0xFFFFFFFE:
                return e[4]
            i = (i + 1) % self.hcount
            if i == start:
                return None

    def has(self, name):
        bi = self.find(name)
        return bi is not None and self.blocks[bi][3] & EXISTS

    def read(self, name):
        bi = self.find(name)
        if bi is None:
            return None
        pos, csize, size, flags = self.blocks[bi]
        if not flags & EXISTS:
            return None
        self.f.seek(self.base + pos)
        raw = self.f.read(csize)
        key = 0
        if flags & ENCRYPTED:
            key = hsh(name.replace('/', '\\').split('\\')[-1], 3)
            if flags & FIX_KEY:
                key = ((key + pos) ^ size) & 0xFFFFFFFF
        if flags & SINGLE:
            if flags & ENCRYPTED:
                raw = decrypt(raw, key)
            if (flags & COMPRESS) and csize < size:
                return _decompress(raw)
            return raw[:size]
        if not flags & (COMPRESS | IMPLODE):
            out = bytearray()
            for k in range(0, csize, self.sector):
                chunk = raw[k:k + self.sector]
                if flags & ENCRYPTED:
                    chunk = decrypt(chunk, (key + k // self.sector) & 0xFFFFFFFF)
                out += chunk
            return bytes(out[:size])
        nsec = (size + self.sector - 1) // self.sector
        tbl = raw[:(nsec + 1) * 4]
        if flags & ENCRYPTED:
            tbl = decrypt(tbl, (key - 1) & 0xFFFFFFFF)
        offs = struct.unpack('<%dI' % (nsec + 1), tbl)
        out = bytearray()
        for k in range(nsec):
            sec = raw[offs[k]:offs[k + 1]]
            if flags & ENCRYPTED:
                sec = decrypt(sec, (key + k) & 0xFFFFFFFF)
            want = min(self.sector, size - k * self.sector)
            if len(sec) < want:
                sec = _decompress(sec) if flags & COMPRESS else _explode(sec)
            out += sec
        return bytes(out[:size])

    def listfile(self):
        d = self.read('(listfile)')
        if not d:
            return []
        return [l for l in d.decode('utf-8', 'replace').replace('\r', '\n').split('\n') if l.strip()]


def encrypt(data, key):
    n = len(data) // 4
    vals = struct.unpack('<%dI' % n, data[:n * 4])
    out = []
    s = 0xEEEEEEEE
    for v in vals:
        s = (s + _ct[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        out.append(v ^ ((key + s) & 0xFFFFFFFF))
        key = ((((~key) << 0x15) + 0x11111111) & 0xFFFFFFFF) | (key >> 0x0B)
        s = (v + s + (s << 5) + 3) & 0xFFFFFFFF
    return struct.pack('<%dI' % n, *out)


def write(path, files):
    """Write an MPQ v1 archive. files: {archive name: bytes}. Each file is stored zlib-compressed in sectors."""
    files = dict(files)
    files['(listfile)'] = '\r\n'.join(n for n in files if n != '(listfile)').encode() + b'\r\n'
    size = 1
    while size < len(files) * 2:
        size *= 2
    sector = 4096
    body, blocks = bytearray(), []
    base = 32
    for name, data in files.items():
        pos = base + len(body)
        nsec = (len(data) + sector - 1) // sector
        offs, chunks = [], []
        cur = (nsec + 1) * 4
        for i in range(nsec):
            raw = data[i * sector:(i + 1) * sector]
            z = b'\x02' + zlib.compress(raw, 9)
            if len(z) >= len(raw):
                z = raw
            offs.append(cur); chunks.append(z); cur += len(z)
        offs.append(cur)
        body += struct.pack('<%dI' % len(offs), *offs) + b''.join(chunks)
        blocks.append((pos, cur, len(data), 0x80000000 | 0x00000200))   # exists | compressed
    hashes = [(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFF, 0xFFFF, 0xFFFFFFFF)] * size
    for i, name in enumerate(files):
        h = hsh(name, 0) & (size - 1)
        while hashes[h][4] != 0xFFFFFFFF:
            h = (h + 1) & (size - 1)
        hashes[h] = (hsh(name, 1), hsh(name, 2), 0, 0, i)
    ht = b''.join(struct.pack('<IIHHI', *e) for e in hashes)
    bt = b''.join(struct.pack('<IIII', *b) for b in blocks)
    ht_off = base + len(body)
    bt_off = ht_off + len(ht)
    total = bt_off + len(bt)
    head = struct.pack('<4sIIHHIIII', b'MPQ\x1a', 32, total, 0, 3, ht_off, bt_off, size, len(blocks))
    with open(path, 'wb') as f:
        f.write(head + bytes(body) + encrypt(ht, hsh('(hash table)', 3)) + encrypt(bt, hsh('(block table)', 3)))
