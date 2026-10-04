"""Check which glue-available bindings exist for a CVar / addon-message based Freeborn channel.

If GlueXML can call SetCVar, a Freeborn choice can be persisted client-side and applied by an
in-world addon after login, which needs no Wow.exe patch and no name token.
"""

from __future__ import annotations

import re
from pathlib import Path

EXE = Path(r"G:\3.3.5a - Dev\Wow.exe")
STEMS = (
    "SetCVar",
    "GetCVar",
    "SendAddonMessage",
    "RegisterAddonMessagePrefix",
    "SendChatMessage",
    "SetSavedVariables",
)


def main() -> int:
    data = EXE.read_bytes()
    names = {m.group().decode("ascii") for m in re.finditer(rb"[\x20-\x7e]{3,}", data)}
    for stem in STEMS:
        hits = sorted(n for n in names if stem in n)
        print(f"--- {stem}: {len(hits)}")
        for hit in hits[:10]:
            print("   ", hit[:110])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
