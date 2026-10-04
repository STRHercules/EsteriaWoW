"""Locate Wow.exe's Script_CreateCharacter and check whether it validates the name.

The glue binding tables are arrays of {name, function} pairs, so the dword after the
"CreateCharacter" string pointer is the handler. We then look for a space/whitespace test in
the handler, which would reject the trailing-space Freeborn token before it is ever sent.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from wow_xref import Pe  # noqa: E402

NAME_FILE_OFFSET = 0x005F43B0  # file offset of the "CreateCharacter" string


def safe(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def offset_to_va(pe: Pe, file_offset: int) -> int:
    for _, virtual_address, _, raw_size, raw_offset in pe.sections:
        if raw_offset <= file_offset < raw_offset + raw_size:
            return pe.image_base + virtual_address + (file_offset - raw_offset)
    raise ValueError(f"file offset 0x{file_offset:X} is not inside any section")


def main() -> int:
    pe = Pe(Path(r"G:\3.3.5a - Dev\Wow.exe"))
    name_va = offset_to_va(pe, NAME_FILE_OFFSET)
    print(f"name VA: 0x{name_va:08X} string: {safe(pe.cstring(name_va, 40))!r}")

    for site in pe.xrefs(name_va):
        section, address_text = site.split()
        address = int(address_text, 16)
        raw = pe.read_va(address, 32)
        dwords = struct.unpack_from("<8I", raw)
        print(f"\nxref in {section} at 0x{address:08X}")
        print("  surrounding dwords:", [f"0x{v:08X}" for v in dwords])

        # The binding table entry: [name ptr][handler ptr].
        neighbours = [value for value in dwords if 0x00401000 <= value < 0x01000000 and value != name_va]
        for candidate in neighbours[:2]:
            print(f"\n  --- candidate handler 0x{candidate:08X} ---")
            for line in pe.disasm(candidate, 45):
                print("   ", safe(line))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
