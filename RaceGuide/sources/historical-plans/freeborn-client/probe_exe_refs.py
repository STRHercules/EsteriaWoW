"""Probe how Wow.exe references Lua binding-name strings (validates the VA mapping)."""

import struct
import sys

exe = sys.argv[1]
data = open(exe, "rb").read()
pe = struct.unpack_from("<I", data, 0x3C)[0]
imgbase = struct.unpack_from("<I", data, pe + 0x34)[0]
nsec = struct.unpack_from("<H", data, pe + 0x06)[0]
optsz = struct.unpack_from("<H", data, pe + 0x14)[0]
sec_off = pe + 0x18 + optsz
secs = []
for i in range(nsec):
    b = sec_off + i * 40
    name = data[b : b + 8].rstrip(b"\0").decode()
    vs, va, rs, rp = struct.unpack_from("<IIII", data, b + 8)
    secs.append((name, va, vs, rp, rs))
    print(f"{name:10s} VA {va:#010x} vsize {vs:#08x} raw {rp:#08x} rsize {rs:#08x}  va-raw={va-rp:#x}")
print("image base", hex(imgbase))


def off2va(o):
    for n, va, vs, rp, rs in secs:
        if rp <= o < rp + rs:
            return va + (o - rp)
    return None


def va2off(v):
    for n, va, vs, rp, rs in secs:
        if va <= v < va + max(vs, rs):
            return rp + (v - va)
    return None


for name in [
    b"SetCharacterCreateFacing\0",
    b"GetCharacterCreateFacing\0",
    b"CreateCharacter\0",
    b"DeleteCharacter\0",
    b"Usage: SetCVar",
    b"GetCharacterInfo\0",
    b"SetCVar\0",
]:
    offs = []
    s = 0
    while True:
        h = data.find(name, s)
        if h < 0:
            break
        offs.append(h)
        s = h + 1
    print(f"\n{name!r}: {len(offs)} occurrence(s) {[hex(x) for x in offs[:5]]}")
    for o in offs[:3]:
        va = off2va(o)
        rva = va - imgbase if va else None
        for lbl, t in (("VA", va), ("RVA", rva), ("FILEOFF", o)):
            if t is None:
                continue
            p = struct.pack("<I", t)
            print(f"    {lbl} {t:#010x}: {data.count(p)} refs")
