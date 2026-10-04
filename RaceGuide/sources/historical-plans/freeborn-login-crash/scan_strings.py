"""Scan a VA range for pushed/moved immediate operands that point at strings."""
import struct
import sys

import capstone

import disasm


def scan(pe, lo, hi):
    blob = pe.read(lo, hi - lo)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = False
    for insn in md.disasm(blob, lo):
        for imm in _imms(insn):
            if 0x90000 + disasm.IMAGE_BASE <= imm < 0xd00000 + disasm.IMAGE_BASE:
                s = pe.cstr(imm, 200)
                if s and len(s) > 3 and any(c.isalpha() for c in s):
                    print(f'{insn.address:#010x}  {insn.mnemonic} {insn.op_str}')
                    print(f'            -> {imm:#x}: {s!r}')


def _imms(insn):
    ops = insn.op_str
    out = []
    for tok in ops.replace(',', ' ').split():
        if tok.startswith('0x'):
            try:
                v = int(tok, 16)
            except ValueError:
                continue
            if v > 0xffff:
                out.append(v)
        elif tok.startswith('0x') is False and tok.rsplit(' ', 1)[0].startswith('0x'):
            pass
    return out


if __name__ == '__main__':
    pe = disasm.Pe(disasm.EXE)
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    scan(pe, lo, hi)
