"""Read C strings at given VAs in Wow.exe."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)
    for argument in sys.argv[1:]:
        va = int(argument, 16)
        for _name, virtual, _vsize, raw_start, raw_size in secs:
            if base + virtual <= va < base + virtual + raw_size:
                raw = raw_start + (va - base - virtual)
                end = data.find(b"\0", raw)
                print(f"{va:#x}: {data[raw:end].decode('latin1')!r}")
                break
        else:
            print(f"{va:#x}: unmapped")


if __name__ == "__main__":
    main()
