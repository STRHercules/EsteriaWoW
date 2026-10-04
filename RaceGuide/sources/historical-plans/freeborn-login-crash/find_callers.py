"""Find call/jmp sites to a VA inside Wow.exe and print the function that contains them."""
import struct
import sys

import capstone

import disasm


def scan_calls(pe, target, opcodes=(0xE8, 0xE9)):
    out = []
    for name, sva, vsize, rawptr, rawsize in pe.sections:
        if name != '.text':
            continue
        blob = pe.data[rawptr:rawptr + rawsize]
        for i in range(len(blob) - 5):
            if blob[i] in opcodes:
                rel, = struct.unpack_from('<i', blob, i + 1)
                site = pe.image_base + sva + i
                if site + 5 + rel == target:
                    out.append((site, blob[i]))
    return out


def show_call_context(pe, site, back=40, fwd=24):
    start = disasm.find_func_start(pe, site) or (site - back)
    disasm.disasm_from(pe, start, count=400, stop_at=site)
    print('   ...')
    disasm.disasm_from(pe, site, count=fwd)


if __name__ == '__main__':
    pe = disasm.Pe(disasm.EXE)
    target = int(sys.argv[1], 16)
    sites = scan_calls(pe, target)
    print(f'call sites to {target:#x}: {[hex(s) for s, _ in sites]}')
    for s, _op in sites:
        print(f'--- context for {s:#x} (func {disasm.find_func_start(pe, s):#x}) ---')
        show_call_context(pe, s)
