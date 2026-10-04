"""Search both binaries for geoset/helmet related strings."""
from __future__ import annotations

import re
import sys
from pathlib import Path

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
NEEDLES = (b"HelmetGeosetVis", b"GeosetVis", b"HelmetGeoset", b"geoset", b"Geoset")


def main() -> None:
    for name in ("Wow.exe", "WarcraftXL.dll"):
        data = (CLIENT / name).read_bytes()
        print(f"=== {name} ({len(data):,} bytes)")
        for needle in NEEDLES:
            hits = []
            start = 0
            while len(hits) < 12:
                index = data.find(needle, start)
                if index < 0:
                    break
                hits.append(index)
                start = index + 1
            print(f"  {needle.decode()}: {[hex(h) for h in hits]}")
            for index in hits[:6]:
                match = re.match(rb"[ -~]{4,}", data[index:index + 80])
                if match:
                    print(f"      {index:#x}: {match.group().decode('latin1')!r}")


if __name__ == "__main__":
    main()
