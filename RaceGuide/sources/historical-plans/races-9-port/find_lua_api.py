"""Locate a Lua API registration entry (name -> handler) inside a WoW client executable.

Usage: python find_lua_api.py <exe> <api-name> [<api-name> ...]
Prints the registration record, the raw handler dword and a disassembly window.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs


def sections(data: bytes) -> tuple[int, list[tuple[str, int, int, int, int]]]:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    optional = pe + 24
    base = struct.unpack_from("<I", data, optional + 28)[0]
    table = optional + struct.unpack_from("<H", data, pe + 20)[0]
    result = []
    for index in range(count):
        offset = table + index * 40
        name = data[offset : offset + 8].rstrip(b"\x00").decode("latin1")
        virtual_size, virtual, raw_size, raw = struct.unpack_from("<IIII", data, offset + 8)
        result.append((name, virtual, virtual_size, raw, raw_size))
    return base, result


def main() -> None:
    path = Path(sys.argv[1])
    data = path.read_bytes()
    base, secs = sections(data)

    def raw_to_va(raw: int) -> int | None:
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if raw_start <= raw < raw_start + raw_size:
                return base + virtual + (raw - raw_start)
        return None

    def va_to_raw(va: int) -> int | None:
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if base + virtual <= va < base + virtual + raw_size:
                return raw_start + (va - base - virtual)
        return None

    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    for api in sys.argv[2:]:
        needle = api.encode()
        index = data.find(needle)
        if index < 0:
            print(f"{api}: string not found")
            continue
        va = raw_to_va(index)
        pattern = struct.pack("<I", va)
        print(f"\n== {api} string raw={index:#x} va={va:#x}")
        start = 0
        while True:
            ref = data.find(pattern, start)
            if ref < 0:
                break
            start = ref + 1
            pair = struct.unpack_from("<2I", data, ref)
            print(f"   ref raw={ref:#x} name={pair[0]:#x} handler={pair[1]:#x}")
            handler = pair[1]
            raw = va_to_raw(handler)
            if raw is None:
                print("      handler not inside a section")
                continue
            print(f"      handler bytes: {data[raw:raw+16].hex(' ')}")
            for ins in decoder.disasm(data[raw : raw + 0x60], handler):
                print(f"      {ins.address:#010x}: {ins.mnemonic} {ins.op_str}")


if __name__ == "__main__":
    main()
