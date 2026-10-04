"""Dump the glue Lua binding names near the character-creation setters in Wow.exe.

If the customized client exposed a Lua-controllable outfit/team/create field, its binding
name would sit in the same string table as SetSelectedRace / SetSelectedSex. Absence here
is evidence that no such binding exists.
"""

from __future__ import annotations

import re
from pathlib import Path

WOW_EXE = Path(r"G:\3.3.5a - Dev\Wow.exe")

# Keyword stems that would indicate a Lua-settable create field.
STEMS = (
    "Selected",
    "Create",
    "Character",
    "Team",
    "Faction",
    "Outfit",
    "Freeborn",
    "Glue",
)

ASCII_RUN = re.compile(rb"[\x20-\x7e]{3,}")


def main() -> int:
    data = WOW_EXE.read_bytes()
    runs = [(m.start(), m.group().decode("ascii")) for m in ASCII_RUN.finditer(data)]

    anchors = [index for index, (_, text) in enumerate(runs) if text == "SetSelectedSex"]
    print(f"SetSelectedSex anchor count: {len(anchors)}")

    for anchor in anchors:
        print(f"\n=== neighbourhood around run #{anchor} (offset {runs[anchor][0]}) ===")
        for index in range(max(0, anchor - 45), min(len(runs), anchor + 45)):
            offset, text = runs[index]
            print(f"  {offset:#010x} {text[:110]}")
        break

    print("\n=== any binding name containing an outfit/team/freeborn stem ===")
    found = False
    for offset, text in runs:
        low = text.lower()
        if any(stem in text for stem in STEMS) and any(
            key in low for key in ("outfit", "freeborn", "team", "playerteam")
        ):
            print(f"  {offset:#010x} {text[:130]}")
            found = True
    if not found:
        print("  (none)")

    print("\n=== SetSelected* / GetSelected* binding names with usage strings ===")
    for offset, text in runs:
        if text.startswith(("SetSelected", "GetSelected")) or text.startswith("Usage: SetSelected"):
            print(f"  {offset:#010x} {text[:130]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
