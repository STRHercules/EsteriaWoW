"""Dump the glue name-validation message table.

0x006B0F40 maps a validation code to a message via the string-pointer table at 0x00AD91F0
(valid for codes 1..103). 0x006B0F90 returns `validator(...) + 0x57`, so code 0x57 means the
validator returned 0 (accepted) and codes 0x58.. are the distinct rejection reasons.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from wow_xref import Pe  # noqa: E402

EXE = Path(r"G:\3.3.5a - Dev\Wow.exe")
TABLE_VA = 0x00AD91F0


def safe(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def main() -> int:
    pe = Pe(EXE)
    for code in range(0x50, 0x6E):
        raw = pe.read_va(TABLE_VA + code * 4, 4)
        if len(raw) < 4:
            print(f"{code:#04x}: <unreadable>")
            continue
        pointer = struct.unpack("<I", raw)[0]
        text = safe(pe.cstring(pointer, 160)) if 0x401000 <= pointer < 0x01000000 else "<non-code ptr>"
        print(f"{code:#04x} -> {pointer:#010x} {text!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
