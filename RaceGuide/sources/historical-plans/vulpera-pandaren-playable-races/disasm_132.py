"""Disassemble around the #132 faulting instruction."""

from __future__ import annotations

from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")
IMAGE_BASE = 0x400000
FAULT = 0x6DC86A


def main() -> None:
    data = EXE.read_bytes()
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    start = FAULT - IMAGE_BASE - 0x60
    code = data[start : start + 0x120]
    for instruction in md.disasm(code, IMAGE_BASE + start):
        marker = "   <== FAULT" if instruction.address == FAULT else ""
        print(f"{instruction.address:#010x}: {instruction.mnemonic} {instruction.op_str}{marker}")


if __name__ == "__main__":
    main()
