"""Locate race-prefix strings and ObjectComponents references in the client binaries."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
TARGETS = ["Wow.exe", "WarcraftXL.dll"]
NEEDLES = [b"ObjectComponents", b"ITEM\\ObjectComponents",
           b"Hu\x00Or\x00Dw\x00Ni\x00Sc\x00Ta\x00Gn\x00Tr",
           b"Character\\%s\\%s\\%s%s.m2"]


def main() -> None:
    for name in TARGETS:
        path = CLIENT / name
        if not path.is_file():
            print(f"{name}: missing")
            continue
        data = path.read_bytes()
        print(f"== {name} ({len(data)} bytes)")
        for needle in NEEDLES:
            start = 0
            offsets = []
            while True:
                index = data.find(needle, start)
                if index < 0:
                    break
                offsets.append(index)
                start = index + 1
                if len(offsets) > 12:
                    break
            print(f"   {needle!r}: {[hex(o) for o in offsets]}")

        for stem in [b"Helm_Cloth_A_01", b"_%c%c.m2", b"%s_%s%c.m2", b"%s%s.m2"]:
            start = 0
            offsets = []
            while True:
                index = data.find(stem, start)
                if index < 0:
                    break
                offsets.append(index)
                start = index + 1
                if len(offsets) > 8:
                    break
            print(f"   {stem!r}: {[hex(o) for o in offsets]}")


if __name__ == "__main__":
    main()
