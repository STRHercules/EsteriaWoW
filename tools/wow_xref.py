"""Read-only xref/disassembly helper for Wow.exe (capstone based)."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from capstone.x86 import X86_OP_MEM


class Pe:
    def __init__(self, path: Path) -> None:
        self.data = path.read_bytes()
        pe = struct.unpack_from("<I", self.data, 0x3C)[0]
        file_header = pe + 4
        _, section_count, _, _, _, optional_size, _ = struct.unpack_from(
            "<HHIIIHH", self.data, file_header)
        optional = file_header + 20
        self.image_base = struct.unpack_from("<I", self.data, optional + 28)[0]
        section_table = optional + optional_size
        self.sections = []
        for index in range(section_count):
            section = section_table + index * 40
            name = self.data[section : section + 8].split(b"\0", 1)[0].decode()
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", self.data, section + 8)
            self.sections.append((name, virtual_address, virtual_size, raw_size, raw_offset))

    def read_va(self, va: int, size: int) -> bytes:
        rva = va - self.image_base
        for _, virtual_address, virtual_size, raw_size, raw_offset in self.sections:
            if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
                return self.data[raw_offset + rva - virtual_address :][:size]
        return b""

    def cstring(self, va: int, limit: int = 120) -> str:
        return self.read_va(va, limit).split(b"\0", 1)[0].decode("ascii", "replace")

    def xrefs(self, target: int, sections: tuple[str, ...] = (".text", ".data", ".rdata")) -> list[str]:
        pattern = struct.pack("<I", target)
        found = []
        for name, virtual_address, _, raw_size, raw_offset in self.sections:
            if name not in sections:
                continue
            blob = self.data[raw_offset : raw_offset + raw_size]
            start = 0
            while True:
                hit = blob.find(pattern, start)
                if hit < 0:
                    break
                found.append(f"{name} 0x{self.image_base + virtual_address + hit:08X}")
                start = hit + 1
        return found

    def calls_to(self, target: int) -> list[str]:
        found = []
        for name, virtual_address, _, raw_size, raw_offset in self.sections:
            if name != ".text":
                continue
            blob = self.data[raw_offset : raw_offset + raw_size]
            for off in range(len(blob) - 5):
                if blob[off] != 0xE8:
                    continue
                rel = struct.unpack_from("<i", blob, off + 1)[0]
                if self.image_base + virtual_address + off + 5 + rel == target:
                    found.append(hex(self.image_base + virtual_address + off))
        return found

    def disasm(self, va: int, count: int) -> list[str]:
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True
        out = []
        for insn in md.disasm(self.read_va(va, count * 16), va):
            note = ""
            for operand in insn.operands:
                if operand.type == X86_OP_MEM and operand.mem.base == 0 and operand.mem.index == 0:
                    address = operand.mem.disp
                    if 0x400000 <= address < 0x10000000:
                        text = self.cstring(address, 40)
                        if text.isprintable() and 2 < len(text) < 40:
                            note = f"  ; {text!r}"
            out.append(f"0x{insn.address:08X}  {insn.mnemonic:<8}{insn.op_str}{note}")
            if len(out) >= count:
                break
        return out


def main() -> int:
    pe = Pe(Path(sys.argv[1]))
    mode = sys.argv[2]
    if mode == "xref":
        for target in sys.argv[3:]:
            address = int(target, 16)
            print(f"xrefs to 0x{address:08X} ({pe.cstring(address, 60)!r}): {pe.xrefs(address)}")
    elif mode == "calls":
        for target in sys.argv[3:]:
            address = int(target, 16)
            print(f"calls to 0x{address:08X}: {pe.calls_to(address)}")
    elif mode == "disasm":
        for line in pe.disasm(int(sys.argv[3], 16), int(sys.argv[4])):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
