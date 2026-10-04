"""Locate every injected Freeborn revision in a deployed CharacterCreate.lua.

The first shipped revision predated the managed-block sentinels, so re-running the packer appended
a second copy instead of replacing it. This reports the boundaries precisely so the canonicaliser
can be sure it removes all of them.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TARGETS = (
    Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\.agents\plans\freeborn-client\verify2\CharacterCreate.lua"),
)

MARKERS = (
    ">>> freeborn-third-team",
    "<<< freeborn-third-team",
    "-- Freeborn third player team",
    "if not CharacterFreeborn_Init then",
    "CharacterFreeborn_Init = true;",
    "CharacterFreeborn_CreateName",
    "GetText() .. \" \"",
    "CreateCharacter(CharacterFreeborn_CreateName",
)

for path in TARGETS:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"=== {path.name}: {len(lines)} lines ===")
    for marker in MARKERS:
        hits = [n for n, line in enumerate(lines, 1) if marker in line]
        print(f"  {marker!r:48} x{len(hits)} {hits}")

    # Every line where a function that the stock file also defines gets redefined.
    redefined = [
        (n, line.strip())
        for n, line in enumerate(lines, 1)
        if re.match(r"^\s*function (CharacterCreate_CreateGenderButtonTextures|"
                    r"CharacterCreate_PositionGenderButtons|CharacterCreate_UpdateButtonCheckedStates|"
                    r"CharacterCreate_OnShow|CharacterCreate_Okay)\b", line)
    ]
    print("  redefinitions of stock functions:")
    for number, line in redefined:
        print(f"    L{number}: {line}")
