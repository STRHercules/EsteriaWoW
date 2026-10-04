"""Dump the per-race pointer table the item-component path builder indexes."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")
TABLE = 0xADAA14


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)

    def va_to_raw(address: int) -> int | None:
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if base + virtual <= address < base + virtual + raw_size:
                return raw_start + (address - base - virtual)
        return None

    def read_string(address: int) -> str:
        raw = va_to_raw(address)
        if raw is None:
            return "<unmapped>"
        end = data.find(b"\0", raw)
        return data[raw:end].decode("latin1", "replace")

    table = va_to_raw(TABLE)
    print(f"table raw={table:#x}")
    for race in range(0, 40):
        entry = struct.unpack_from("<I", data, table + race * 4)[0]
        print(f"  race {race:>2}: ptr={entry:#010x} -> {read_string(entry)!r}")


if __name__ == "__main__":
    main()
