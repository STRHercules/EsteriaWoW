"""Disassemble a window of a PE image: python disasm_at.py <exe> <hex-address> [length]."""

from __future__ import annotations

import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

from find_lua_api import sections


def main() -> None:
    data = Path(sys.argv[1]).read_bytes()
    address = int(sys.argv[2], 16)
    length = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x100
    base, secs = sections(data)
    raw = None
    for name, virtual, _vsize, raw_start, raw_size in secs:
        if base + virtual <= address < base + virtual + raw_size:
            raw = raw_start + (address - base - virtual)
            print(f"# section {name} raw={raw:#x}")
    if raw is None:
        raise SystemExit("address is not inside a mapped section")
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    for ins in decoder.disasm(data[raw : raw + length], address):
        print(f"{ins.address:#010x}: {ins.mnemonic} {ins.op_str}")


if __name__ == "__main__":
    main()
