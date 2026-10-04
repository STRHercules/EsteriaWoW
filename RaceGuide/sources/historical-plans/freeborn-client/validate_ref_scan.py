"""Sanity-check: resolve what the DWORDs found in .text actually point at."""

import struct
import sys

exe = sys.argv[1]
data = open(exe, "rb").read()
pe = struct.unpack_from("<I", data, 0x3C)[0]
nsec = struct.unpack_from("<H", data, pe + 0x06)[0]
optsz = struct.unpack_from("<H", data, pe + 0x14)[0]
sec_off = pe + 0x18 + optsz
secs = []
for i in range(nsec):
    b = sec_off + i * 40
    name = data[b : b + 8].rstrip(b"\0").decode()
    vs, va, rs, rp = struct.unpack_from("<IIII", data, b + 8)
    secs.append((name, va, vs, rp, rs))


def which(off):
    for name, va, vs, rp, rs in secs:
        if rp <= off < rp + rs:
            return name, va + (off - rp)
    return "?", None


def va2off(v):
    for name, va, vs, rp, rs in secs:
        if va <= v < va + max(vs, rs):
            return rp + (v - va)
    return None


def cstr(off, limit=100):
    if off is None or not (0 <= off < len(data)):
        return None
    end = data.find(b"\0", off, off + limit)
    if end < 0:
        return None
    raw = data[off:end]
    if not raw or any(b < 0x20 or b > 0x7E for b in raw):
        return None
    return raw.decode("ascii")


# Take the first 12 refs found in .text into .rdata and resolve them.
text = [s for s in secs if s[0] == ".text"][0]
rdata = [s for s in secs if s[0] == ".rdata"][0]
blob = data[text[3] : text[3] + text[4]]
shown = 0
print("sample .text -> .rdata references and what they resolve to:")
for i in range(0, len(blob) - 4):
    v = struct.unpack_from("<I", blob, i)[0]
    if rdata[1] <= v < rdata[1] + rdata[2]:
        tgt = va2off(v)
        s = cstr(tgt)
        at = which(text[3] + i)
        print(f"  {at[1]:#x} -> {v:#x} : {s!r}" if s else f"  {at[1]:#x} -> {v:#x} : (non-string)")
        shown += 1
        if shown >= 12:
            break

# And the reverse question: is ANY DWORD in the whole image equal to a usage-string VA?
for probe in (0x5F560C, 0x5F5BD0, 0x5F3020):
    p = struct.pack("<I", probe)
    hits = []
    s = 0
    while True:
        h = data.find(p, s)
        if h < 0:
            break
        hits.append(h)
        s = h + 1
    print(f"\nDWORD {probe:#x}: {len(hits)} refs at {[hex(x) for x in hits]}")
    for h in hits:
        print(f"    from {which(h)}")
