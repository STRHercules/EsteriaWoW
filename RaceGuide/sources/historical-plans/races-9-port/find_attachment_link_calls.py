"""What attachment ids does the client link item components to?"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")
HELPERS = (0x4EAA70, 0x4F2880, 0x4E9D50)


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)
    text = [entry for entry in secs if entry[0] == ".text"][0]
    _name, virtual, _vsize, raw_start, raw_size = text
    code = data[raw_start : raw_start + raw_size]
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)

    def va_to_raw(address: int):
        for _n, virt, _vs, raw, rsize in secs:
            if base + virt <= address < base + virt + rsize:
                return raw + (address - base - virt)
        return None

    for helper in HELPERS:
        print(f"=== calls to {helper:#x}")
        for index in range(len(code) - 5):
            if code[index] != 0xE8:
                continue
            target = base + virtual + index + 5 + struct.unpack_from("<i", code, index + 1)[0]
            if target != helper:
                continue
            call_va = base + virtual + index
            raw = va_to_raw(call_va - 0x30)
            window = data[raw:raw + 0x35]
            instructions = list(decoder.disasm(window, call_va - 0x30))[-6:]
            print(f"  {call_va:#010x}: " + " | ".join(f"{i.mnemonic} {i.op_str}" for i in instructions))


if __name__ == "__main__":
    main()
