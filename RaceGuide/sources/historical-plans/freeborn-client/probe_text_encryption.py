"""Is the on-disk .text of Wow.exe plain x86, or encrypted by the loader?

Counts DWORDs in .text that point into .rdata (string/const data).  A normal MSVC binary has
thousands; an encrypted-on-disk .text has ~none.
"""

import struct
import sys

exe = sys.argv[1]
data = open(exe, "rb").read()
pe = struct.unpack_from("<I", data, 0x3C)[0]
nsec = struct.unpack_from("<H", data, pe + 0x06)[0]
optsz = struct.unpack_from("<H", data, pe + 0x14)[0]
sec_off = pe + 0x18 + optsz
secs = {}
order = []
for i in range(nsec):
    b = sec_off + i * 40
    name = data[b : b + 8].rstrip(b"\0").decode()
    vs, va, rs, rp = struct.unpack_from("<IIII", data, b + 8)
    secs[name] = (va, vs, rp, rs)
    order.append(name)

text_va, text_vs, text_rp, text_rs = secs[".text"]
rdata_va, rdata_vs, rdata_rp, rdata_rs = secs[".rdata"]
print(f".text  VA {text_va:#x} size {text_vs:#x}")
print(f".rdata VA {rdata_va:#x} size {rdata_vs:#x} -> [{rdata_va:#x},{rdata_va+rdata_vs:#x})")

blob = data[text_rp : text_rp + text_rs]
hits = 0
samples = []
for i in range(0, len(blob) - 4, 1):
    v = struct.unpack_from("<I", blob, i)[0]
    if rdata_va <= v < rdata_va + rdata_vs:
        hits += 1
        if len(samples) < 5:
            samples.append((hex(text_va + i), hex(v)))
print(f"pointers into .rdata found in .text: {hits}")
for s in samples:
    print("   ", s)

# also: how much of .text looks like push/lea/call opcodes (a crude plain-code sanity check)
opcodes = {0xE8: 0, 0xFF: 0, 0x8D: 0, 0x68: 0, 0x83: 0}
for b in blob[:200000]:
    if b in opcodes:
        opcodes[b] += 1
print("opcode byte frequencies in first 200KB of .text:", {hex(k): v for k, v in opcodes.items()})
