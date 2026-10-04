"""Which DBC objects are passed to the row-lookup helper 0x4cfd90?"""
from __future__ import annotations

import collections
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")
HELPER = 0x4CFD90


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)
    text = [entry for entry in secs if entry[0] == ".text"][0]
    _name, virtual, _vsize, raw_start, raw_size = text
    code = data[raw_start : raw_start + raw_size]
    counts: collections.Counter = collections.Counter()
    for index in range(len(code) - 10):
        if code[index] != 0xB9:
            continue
        immediate = struct.unpack_from("<I", code, index + 1)[0]
        if code[index + 5] != 0xE8:
            continue
        va = base + virtual + index + 5
        target = va + 5 + struct.unpack_from("<i", code, index + 6)[0]
        if target == HELPER:
            counts[immediate] += 1
    print(f"{len(counts)} distinct objects passed to {HELPER:#x}")
    for address, count in sorted(counts.items()):
        print(f"  {address:#010x}  {count} call(s)")


if __name__ == "__main__":
    main()
