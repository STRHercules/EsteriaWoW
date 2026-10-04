"""Locate every occurrence of a binding name and show which section it lives in."""

import struct
import sys

exe = sys.argv[1]
needle = sys.argv[2].encode()
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


print(f"needle {needle!r}")
s = 0
n = 0
while True:
    h = data.find(needle, s)
    if h < 0:
        break
    n += 1
    secname, va = which(h)
    ctx = data[max(0, h - 48) : h + 64]
    printable = "".join(chr(c) if 0x20 <= c <= 0x7E else "." for c in ctx)
    print(f"\n[{n}] file {h:#x} section {secname} VA {va:#x}")
    print(f"    ctx: {printable!r}")
    s = h + 1
print(f"\ntotal {n}")

# Structure of the .estria / .wxl sections: packed or plain?
for name in (".wxl", ".estria"):
    for secname, va, vs, rp, rs in secs:
        if secname == name:
            head = data[rp : rp + 64]
            printable = "".join(chr(c) if 0x20 <= c <= 0x7E else "." for c in head)
            ent = sum(1 for c in data[rp : rp + rs] if c == 0) / max(1, rs)
            print(f"\n{name}: VA {va:#x} raw {rp:#x} size {rs:#x} zero-fraction {ent:.2f}")
            print(f"   head: {printable!r}")
