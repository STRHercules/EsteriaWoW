"""Find call sites of two DBC helpers and show the surrounding push constants."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")
HELPERS = (0x4CFBB0, 0x4CFD90)


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)

    def raw_to_va(offset: int):
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if raw_start <= offset < raw_start + raw_size:
                return base + virtual + (offset - raw_start)
        return None

    def va_to_raw(address: int):
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if base + virtual <= address < base + virtual + raw_size:
                return raw_start + (address - base - virtual)
        return None

    text = [entry for entry in secs if entry[0] == ".text"][0]
    _name, virtual, _vsize, raw_start, raw_size = text
    code = data[raw_start : raw_start + raw_size]
    for helper in HELPERS:
        print(f"=== calls to {helper:#x}")
        for index in range(len(code) - 5):
            if code[index] != 0xE8:
                continue
            target = (base + virtual + index) + 5 + struct.unpack_from("<i", code, index + 1)[0]
            if target != helper:
                continue
            va = base + virtual + index
            back = data[va_to_raw(va - 0x28) : va_to_raw(va) + 5]
            instructions = list(decoder.disasm(back, va - 0x28))
            tail = " | ".join(f"{i.mnemonic} {i.op_str}" for i in instructions[-5:])
            print(f"  {va:#010x}: {tail}")


if __name__ == "__main__":
    main()
