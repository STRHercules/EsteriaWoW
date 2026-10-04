"""Read-only scan of the dev client binaries for glue/Lua binding names and packet fields.

Extracts printable ASCII runs and reports the ones matching character-creation,
team/faction, or outfit keywords. Used to determine whether a Freeborn selection can
reach CMSG_CHAR_CREATE without patching Wow.exe.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CLIENT_ROOT = Path(r"G:\3.3.5a - Dev")

TARGETS = ("Wow.exe", "Client.dll", "WarcraftXL.dll")

PATTERNS = (
    "SetSelected",
    "GetSelected",
    "CreateCharacter",
    "Outfit",
    "outfit",
    "SetCharacter",
    "GetCharacter",
    "TeamId",
    "teamId",
    "Freeborn",
    "FREEBORN",
    "FactionForRace",
    "CharCreate",
    "CharacterCreate",
)

ASCII_RUN = re.compile(rb"[\x20-\x7e]{4,}")


def scan(path: Path) -> dict[str, list[str]]:
    data = path.read_bytes()
    hits: dict[str, set[str]] = {pattern: set() for pattern in PATTERNS}
    for match in ASCII_RUN.finditer(data):
        text = match.group().decode("ascii")
        for pattern in PATTERNS:
            if pattern in text:
                # Keep the interesting tail rather than huge blobs.
                hits[pattern].add(text[:160])
    return {pattern: sorted(values) for pattern, values in hits.items() if values}


def main() -> int:
    for name in TARGETS:
        path = CLIENT_ROOT / name
        if not path.is_file():
            print(f"### {name}: MISSING")
            continue
        print(f"### {name} ({path.stat().st_size} bytes)")
        for pattern, values in scan(path).items():
            print(f"  -- {pattern}: {len(values)}")
            for value in values[:40]:
                print(f"     {value}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
