"""Dump NUL-separated string blobs from Wow.exe (binding names, cvar names)."""

import sys

exe = sys.argv[1]
lo = int(sys.argv[2], 16)
hi = int(sys.argv[3], 16)
data = open(exe, "rb").read()
region = data[lo:hi]
parts = region.split(b"\0")
out = []
for p in parts:
    if len(p) >= 2 and all(0x20 <= c <= 0x7E for c in p):
        out.append(p.decode("ascii"))
print(f"{len(out)} printable strings in [0x{lo:x},0x{hi:x}):")
for s in out:
    print("   ", s)
