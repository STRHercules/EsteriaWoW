"""Minimal PE32 helper + capstone disassembler for Wow.exe 3.3.5a (image base 0x400000).

Usage:
  python disasm.py func <va>          # show the function containing <va>
  python disasm.py range <va> [n]     # disassemble n instructions from <va>
  python disasm.py stack <dump> <esp> # walk the EBP chain in a minidump's memory
"""
import struct
import sys

import capstone

import dump_exception as mdmod

IMAGE_BASE = 0x400000
EXE = r'G:\3.3.5a - Dev\Wow.exe'


class Pe:
    def __init__(self, path):
        self.data = open(path, 'rb').read()
        e_lfanew = struct.unpack_from('<I', self.data, 0x3C)[0]
        assert self.data[e_lfanew:e_lfanew + 4] == b'PE\0\0'
        coff = e_lfanew + 4
        nsec, = struct.unpack_from('<H', self.data, coff + 2)
        opt_size, = struct.unpack_from('<H', self.data, coff + 16)
        opt = coff + 20
        self.image_base, = struct.unpack_from('<I', self.data, opt + 28)
        self.sections = []
        sec = opt + opt_size
        for i in range(nsec):
            off = sec + i * 40
            name = self.data[off:off + 8].rstrip(b'\0').decode()
            vsize, va, rawsize, rawptr = struct.unpack_from('<IIII', self.data, off + 8)
            self.sections.append((name, va, vsize, rawptr, rawsize))

    def read(self, va, size):
        rva = va - self.image_base
        for name, sva, vsize, rawptr, rawsize in self.sections:
            if sva <= rva < sva + max(vsize, rawsize):
                off = rawptr + (rva - sva)
                return self.data[off:off + size]
        return b''

    def cstr(self, va, maxlen=120):
        rva = va - self.image_base
        for name, sva, vsize, rawptr, rawsize in self.sections:
            if sva <= rva < sva + max(vsize, rawsize):
                off = rawptr + (rva - sva)
                end = self.data.find(b'\0', off, off + maxlen)
                raw = self.data[off:end if end > 0 else off + maxlen]
                try:
                    return raw.decode('ascii')
                except UnicodeDecodeError:
                    return None
        return None

    def section_of(self, va):
        rva = va - self.image_base
        for name, sva, vsize, rawptr, rawsize in self.sections:
            if sva <= rva < sva + max(vsize, rawsize):
                return name
        return None


PROLOGUES = (b'\x55\x8b\xec', b'\x55\x89\xe5', b'\x8b\xff\x55\x8b\xec',
             b'\x53\x8b\xdc', b'\x56\x8b\x74\x24', b'\x51', b'\x53', b'\x56',
             b'\x57', b'\x83\xec', b'\x81\xec', b'\x6a')


def find_func_start(pe, va):
    """Walk back over int3/cc padding to the previous function entry."""
    rva = va - pe.image_base
    window = 0x2000
    start = None
    for name, sva, vsize, rawptr, rawsize in pe.sections:
        if sva <= rva < sva + max(vsize, rawsize):
            filepos = rawptr + (rva - sva)
            lo = max(rawptr, filepos - window)
            blob = pe.data[lo:filepos + 8]
            base_va = pe.image_base + (lo - rawptr) + sva
            # find padding runs (0xCC / 0x90) and take the first real byte after
            i = len(blob) - 9
            best = None
            while i >= 1:
                if blob[i] in (0xCC, 0x90) and blob[i - 1] in (0xCC, 0x90, 0x00):
                    # walk forward past padding
                    j = i
                    while j < len(blob) - 1 and blob[j] in (0xCC, 0x90, 0x00):
                        j += 1
                    cand = base_va + j
                    if cand <= va and (best is None or cand > best):
                        best = cand
                    i -= 1
                    continue
                i -= 1
            start = best
            break
    return start


def disasm_from(pe, va, count=40, stop_at=None, show_bytes=True):
    blob = pe.read(va, count * 15 + 32)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    n = 0
    for insn in md.disasm(blob, va):
        mark = '  <== TARGET' if stop_at is not None and insn.address == stop_at else ''
        comment = ''
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                if op.mem.base == capstone.x86.X86_REG_INVALID and op.mem.index == capstone.x86.X86_REG_INVALID:
                    target = op.mem.disp
                    s = pe.cstr(target)
                    if s and len(s) > 2 and all(32 <= ord(c) < 127 for c in s):
                        comment = f'   ; "{s}"'
        print(f'{insn.address:#010x}  {insn.mnemonic:<8} {insn.op_str}{comment}{mark}')
        n += 1
        if n >= count:
            break
        if insn.address + insn.size > va + count * 15:
            break
    return n


def show_stack(dump_path, esp, depth=40):
    md = mdmod.parse(dump_path)
    print(f'--- EBP chain from esp={esp:#010x} in {dump_path} ---')
    for start, size, blob in sorted(md['memory'], key=lambda m: -m[1]):
        if start <= esp < start + size and size > 0x200:
            print(f'  (memory range {start:#010x} size {size:#x} contains esp)')
    eip = int(sys.argv[3], 16) if len(sys.argv) > 3 else None
    cur = esp
    for i in range(depth):
        chunk = mdmod.read_mem(md, cur, 8)
        if not chunk or len(chunk) < 8:
            print(f'  [{i}] {cur:#010x}: <not in dump>')
            break
        val, next_ebp = struct.unpack('<II', chunk)
        print(f'  [{i}] esp={cur:#010x} -> {val:#010x}')
        if next_ebp <= cur or next_ebp - cur > 0x20000:
            break
        cur = next_ebp


if __name__ == '__main__':
    cmd = sys.argv[1]
    pe = Pe(EXE)
    if cmd == 'func':
        va = int(sys.argv[2], 16)
        start = find_func_start(pe, va)
        print(f'function start guess: {start:#010x} (section {pe.section_of(va)})')
        disasm_from(pe, start, count=120, stop_at=va)
    elif cmd == 'range':
        va = int(sys.argv[2], 16)
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 20
        disasm_from(pe, va, count=n)
    elif cmd == 'stack':
        show_stack(sys.argv[2], int(sys.argv[3], 16))
    elif cmd == 'str':
        va = int(sys.argv[2], 16)
        print(repr(pe.cstr(va, 400)))
