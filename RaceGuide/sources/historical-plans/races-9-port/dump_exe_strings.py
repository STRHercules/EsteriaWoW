"""Dump the ASCII strings in a window of Wow.exe."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PATH = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Wow.exe")


def main() -> None:
    start = int(sys.argv[1], 16)
    end = int(sys.argv[2], 16)
    data = PATH.read_bytes()[start:end]
    for match in re.finditer(rb"[\x20-\x7e]{3,}", data):
        print(f"{start + match.start():#08x}  {match.group().decode('latin1')}")


if __name__ == "__main__":
    main()
