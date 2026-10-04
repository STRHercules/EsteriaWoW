"""Resolve the glue create routine's name validation.

0x004E0380 (CGCharacterCreation::CreateCharacter) calls 0x6b0f90(name) and only continues when
the result is 0x57; anything else shows a dialog built from a code via 0x6b0f40. If that check
rejects a space, the trailing-space token never reaches the wire.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from wow_xref import Pe  # noqa: E402

EXE = Path(r"G:\3.3.5a - Dev\Wow.exe")


def safe(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def main() -> int:
    pe = Pe(EXE)
    for va, label in ((0x009F3D94, "dialog string"),):
        print(f"{label} 0x{va:08X}: {safe(pe.cstring(va, 120))!r}")

    print("\n=== 0x6B0F90 (name check) ===")
    for line in pe.disasm(0x6B0F90, 70):
        print(" ", safe(line))

    print("\n=== callers of 0x6B0F90 ===")
    print(" ", pe.calls_to(0x6B0F90))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
