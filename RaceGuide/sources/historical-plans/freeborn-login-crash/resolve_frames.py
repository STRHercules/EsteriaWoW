"""Given a WoW crash stack (return addresses), resolve the call/jmp before each one."""
import struct
import sys

import disasm

FRAMES = [0x008889CE, 0x0050ADA2, 0x0050C3AF, 0x0050EBCE, 0x0063202E,
          0x006324CE, 0x00633568, 0x00464BF3, 0x0047DC4C, 0x0047F29A,
          0x0047F2E1, 0x0040B7D8]


def resolve(pe, ret_addr):
    b = pe.read(ret_addr - 5, 5)
    if not b or b[0] not in (0xE8, 0xE9):
        return None
    rel, = struct.unpack_from('<i', b, 1)
    return ret_addr - 5, ret_addr - 5 + 5 + rel, b[0]


def main():
    pe = disasm.Pe(disasm.EXE)
    frames = [int(a, 16) for a in sys.argv[1:]] or FRAMES
    for ret in frames:
        r = resolve(pe, ret)
        print('=' * 70)
        print(f'return address {ret:#010x}')
        if not r:
            b = pe.read(ret - 8, 8)
            print(f'  no call/jmp immediately before; bytes: {b.hex()}')
            continue
        site, target, op = r
        print(f'  call at {site:#010x} -> {"call" if op == 0xE8 else "jmp"} {target:#010x}')
        print(f'  target function start guess: {disasm.find_func_start(pe, target):#010x}')
        disasm.disasm_from(pe, site - 6 * 8, count=10, stop_at=site)


if __name__ == '__main__':
    main()
