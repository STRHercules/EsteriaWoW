"""Find the client code that builds Item\\ObjectComponents\\Head paths.

Usage: python trace_helm_path_code.py <raw-offset-of-string> [window]
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

sys.path.insert(0, str(Path(__file__).parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)
    raw = int(sys.argv[1], 16)
    window = int(sys.argv[2]) if len(sys.argv) > 2 else 160

    va = None
    for _name, virtual, _vsize, raw_start, raw_size in secs:
        if raw_start <= raw < raw_start + raw_size:
            va = base + virtual + (raw - raw_start)
    print(f"string raw={raw:#x} va={va:#x}")

    def raw_to_va(offset: int) -> int | None:
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if raw_start <= offset < raw_start + raw_size:
                return base + virtual + (offset - raw_start)
        return None

    def va_to_raw(address: int) -> int | None:
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if base + virtual <= address < base + virtual + raw_size:
                return raw_start + (address - base - virtual)
        return None

    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    pattern = struct.pack("<I", va)
    start = 0
    refs = []
    while True:
        index = data.find(pattern, start)
        if index < 0:
            break
        start = index + 1
        refs.append(index)
    print(f"{len(refs)} references")
    for index in refs:
        ref_va = raw_to_va(index)
        print(f"\n--- ref raw={index:#x} va={ref_va:#x}")
        begin = max(0, index - window)
        code = data[begin : index + window]
        for insn in decoder.disasm(code, raw_to_va(begin)):
            marker = "  <== " if insn.address <= (ref_va or 0) < insn.address + insn.size else "      "
            print(f"{marker}{insn.address:#010x}  {insn.mnemonic:<8}{insn.op_str}")


if __name__ == "__main__":
    main()
