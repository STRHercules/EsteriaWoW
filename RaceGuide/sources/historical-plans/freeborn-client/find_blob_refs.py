"""Find every DWORD anywhere in Wow.exe that points into the character-creation name blob,
and classify the referencing section -- reveals how the client stores Lua binding names."""

import struct
import sys

exe, lo_s, hi_s = sys.argv[1], sys.argv[2], sys.argv[3]
lo, hi = int(lo_s, 16), int(hi_s, 16)
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
    return None, None


def cstr(off, limit=120):
    if not (0 <= off < len(data)):
        return ""
    end = data.find(b"\0", off, off + limit)
    if end < 0:
        return ""
    raw = data[off:end]
    if not raw or any(b < 0x20 or b > 0x7E for b in raw):
        return ""
    return raw.decode("ascii")


print(f"scanning for DWORDs in [{lo:#x},{hi:#x})")
found = []
for i in range(0, len(data) - 4):
    v = struct.unpack_from("<I", data, i)[0]
    if lo <= v < hi:
        sec, va = which(i)
        found.append((i, v, sec, va))
print(f"total refs: {len(found)}")
from collections import Counter

print("by referencing section:", Counter(f[2] for f in found))
for off, v, sec, va in found[:60]:
    print(f"  file {off:#09x} ({sec} {va:#x}) -> {v:#x} {cstr(which(v)[1] and 0 or 0)}")
    # resolve the target string
    tf = None
    for name, sva, svs, srp, srs in secs:
        if sva <= v < sva + max(svs, srs):
            tf = srp + (v - sva)
    print(f"        target string: {cstr(tf)!r}" if tf is not None else "        (unmapped)")
