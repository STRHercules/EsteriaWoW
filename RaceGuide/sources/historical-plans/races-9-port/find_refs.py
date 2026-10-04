"""Find code/data references to an absolute address: python find_refs.py <exe> <hex-address> [limit]."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from find_lua_api import sections


def main() -> None:
    data = Path(sys.argv[1]).read_bytes()
    target = int(sys.argv[2], 16)
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    base, secs = sections(data)

    def raw_to_va(raw: int) -> int | None:
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if raw_start <= raw < raw_start + raw_size:
                return base + virtual + (raw - raw_start)
        return None

    pattern = struct.pack("<I", target)
    start = 0
    found = 0
    while found < limit:
        index = data.find(pattern, start)
        if index < 0:
            break
        start = index + 1
        found += 1
        va = raw_to_va(index)
        print(f"ref raw={index:#x} va={va:#x}" if va is not None else f"ref raw={index:#x} va=unmapped")


if __name__ == "__main__":
    main()
