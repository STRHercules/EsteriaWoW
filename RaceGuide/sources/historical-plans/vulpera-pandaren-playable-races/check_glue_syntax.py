"""Structural checks on the live GlueParent.lua (missing commas, guard, BROKEN)."""

from __future__ import annotations

import re
from pathlib import Path

PATH = (
    Path(__file__).resolve().parent / "pc-verify3" / "GlueParent.lua"
)


def main() -> None:
    text = PATH.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    bad = []
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if re.fullmatch(r'\["[A-Z_]+"\] = [^,{}\[\]\s]+\s*', stripped) and lines[
            index + 1
        ].strip().startswith("["):
            bad.append((index + 1, line))
    print(f"missing-comma patterns: {bad}")
    print(f"ambience guard present: {'if ( ambienceTrack ) then' in text}")
    print(f'BROKEN in horde table: {chr(91) + chr(34) + "BROKEN" + chr(34) + chr(93) + " = true," in text}')
    print(f'BROKEN ambience entry: {"GlueAmbienceTracks" + chr(91) + chr(34) + "BROKEN" in text}')
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
