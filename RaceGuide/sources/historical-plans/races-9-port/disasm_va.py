"""Disassemble a VA range of Wow.exe."""
from __future__ import annotations

import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

sys.path.insert(0, str(Path(__file__).parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)
    start = int(sys.argv[1], 16)
    length = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x100

    def va_to_raw(address: int) -> int | None:
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if base + virtual <= address < base + virtual + raw_size:
                return raw_start + (address - base - virtual)
        return None

    raw = va_to_raw(start)
    code = data[raw : raw + length]
    for insn in Cs(CS_ARCH_X86, CS_MODE_32).disasm(code, start):
        print(f"{insn.address:#010x}  {insn.bytes.hex():<18}{insn.mnemonic:<8}{insn.op_str}")


if __name__ == "__main__":
    main()
