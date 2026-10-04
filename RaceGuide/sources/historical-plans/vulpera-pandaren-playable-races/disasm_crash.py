"""Disassemble the crashing frames of Wow.exe to identify the failing code."""

from __future__ import annotations

import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")
IMAGE_BASE = 0x400000
FRAMES = (0x772AB5, 0x8889CE, 0x6D7A9E, 0x725F73, 0x73FEC4, 0x6E82B1, 0x4D64FE)


def file_offset(rva: int) -> int:
    return rva


def main() -> None:
    data = EXE.read_bytes()
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    for address in FRAMES:
        start = file_offset(address - IMAGE_BASE) - 0x30
        code = data[start : start + 0x90]
        print(f"== frame {address:#x} (file offset {start:#x}) ==")
        for instruction in md.disasm(code, IMAGE_BASE + start):
            marker = " <-- frame" if instruction.address == address else ""
            print(f"   {instruction.address:#010x}: {instruction.mnemonic} {instruction.op_str}{marker}")
        print()


if __name__ == "__main__":
    main()
