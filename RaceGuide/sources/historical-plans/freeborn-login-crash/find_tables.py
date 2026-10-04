"""Find switch jump tables in the exe that point into a function, and decode them."""
import struct
import sys

import disasm


def find_tables(pe, lo, hi, min_entries=4):
    out = []
    for name, sva, vsize, rawptr, rawsize in pe.sections:
        if name not in ('.rdata', '.data'):
            continue
        blob = pe.data[rawptr:rawptr + rawsize]
        base = pe.image_base + sva
        i = 0
        while i <= len(blob) - 4:
            val, = struct.unpack_from('<I', blob, i)
            if lo <= val <= hi:
                j = i
                count = 0
                while j <= len(blob) - 4:
                    v, = struct.unpack_from('<I', blob, j)
                    if not (lo <= v <= hi):
                        break
                    count += 1
                    j += 4
                if count >= min_entries:
                    entries = [struct.unpack_from('<I', blob, i + k * 4)[0]
                               for k in range(count)]
                    out.append((base + i, entries))
                    i = j
                    continue
            i += 4
    return out


def find_refs(pe, table_va):
    refs = []
    for name, sva, vsize, rawptr, rawsize in pe.sections:
        if name != '.text':
            continue
        blob = pe.data[rawptr:rawptr + rawsize]
        pat = struct.pack('<I', table_va)
        start = 0
        while True:
            k = blob.find(pat, start)
            if k < 0:
                break
            refs.append(pe.image_base + sva + k)
            start = k + 1
    return refs


if __name__ == '__main__':
    pe = disasm.Pe(disasm.EXE)
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    tables = find_tables(pe, lo, hi)
    print(f'{len(tables)} tables into {lo:#x}-{hi:#x}')
    for va, entries in tables:
        fatal = [i for i, e in enumerate(entries) if lo <= e < lo + 8 or e == 0x50ad91]
        print(f'\ntable at {va:#x}: {len(entries)} entries')
        print('  unique targets:', sorted({hex(e) for e in entries}))
        refs = find_refs(pe, va)
        print('  referenced from:', [hex(r) for r in refs])
        if fatal:
            print('  entries == 0x50ad91 (fatal thunk) at indices:', fatal)
