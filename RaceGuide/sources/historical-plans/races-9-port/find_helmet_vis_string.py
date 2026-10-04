"""Find the HelmetGeosetVisData string and its references in Wow.exe."""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_lua_api import sections  # noqa: E402

EXE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")


def main() -> None:
    data = EXE.read_bytes()
    base, secs = sections(data)
    for needle in (b"HelmetGeosetVisData", b"HelmetGeosetVis"):
        start = 0
        while True:
            index = data.find(needle, start)
            if index < 0:
                break
            start = index + 1
            va = None
            for _name, virtual, _vsize, raw_start, raw_size in secs:
                if raw_start <= index < raw_start + raw_size:
                    va = base + virtual + (index - raw_start)
            end = data.find(b"\0", index)
            print(f"{needle.decode()} raw={index:#x} va={va:#x}: "
                  f"{data[index:end].decode('latin1')!r}")


if __name__ == "__main__":
    main()
