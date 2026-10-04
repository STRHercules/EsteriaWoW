import struct, pathlib
p = pathlib.Path(r'G:\3.3.5a - Dev\WarcraftXL.dll'); d = p.read_bytes()
e = struct.unpack_from('<I', d, 0x3C)[0]
assert d[e:e+4] == b'PE\0\0'
coff = e+4
nsec, = struct.unpack_from('<H', d, coff+2)
optsize, = struct.unpack_from('<H', d, coff+16)
opt = coff+20
magic, = struct.unpack_from('<H', d, opt)
ddoff = opt + (96 if magic == 0x10b else 112)
exp_rva, exp_size = struct.unpack_from('<II', d, ddoff)
secs = []
sec = opt+optsize
for i in range(nsec):
    off = sec + i*40
    name = d[off:off+8].rstrip(b'\0').decode()
    vsize, va, rawsize, rawptr = struct.unpack_from('<IIII', d, off+8)
    secs.append((name, va, vsize, rawptr, rawsize))
def r2o(rva):
    for name, va, vsize, rawptr, rawsize in secs:
        if va <= rva < va+max(vsize, rawsize): return rawptr + (rva-va)
    return None
print('export dir rva', hex(exp_rva))
if exp_rva:
    o = r2o(exp_rva)
    nnames, = struct.unpack_from('<I', d, o+24)
    names_rva, = struct.unpack_from('<I', d, o+32)
    no = r2o(names_rva)
    out = []
    for i in range(min(nnames, 300)):
        nrva, = struct.unpack_from('<I', d, no+i*4)
        so = r2o(nrva); end = d.find(b'\0', so)
        out.append(d[so:end].decode('ascii','replace'))
    print(len(out), 'exports')
    print([x for x in out if any(k in x.lower() for k in ('dbc','file','hook','patch','init','load'))][:40])
    print(out[:25])
