"""Point the channel lookups at the character's PvP side.

ChannelMgr::forTeam returns nullptr for anything that is not Alliance or Horde, so without this a
Freeborn simply has no custom channels at all. The mapping is the identity for Alliance and Horde.

Usage:  python map_channel_team.py            # dry run
        python map_channel_team.py --apply
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGETS = (ROOT / "src/server/game/Handlers/ChannelHandler.cpp",)
BEFORE = "ChannelMgr::forTeam(GetPlayer()->GetTeamId())"
AFTER = "ChannelMgr::forTeam(PvpSideOf(GetPlayer()))"
INCLUDE = '#include "PlayerTeamSide.h"'


def main() -> int:
    apply = "--apply" in sys.argv
    total = 0

    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        count = text.count(BEFORE)
        if not count:
            print(f"  {path.name}: nothing to change")
            continue
        text = text.replace(BEFORE, AFTER)
        if INCLUDE not in text:
            lines = text.splitlines()
            last = max(i for i, l in enumerate(lines) if l.startswith("#include"))
            lines.insert(last + 1, INCLUDE)
            text = "\n".join(lines) + "\n"
        if apply:
            path.write_text(text, encoding="utf-8", newline="\n")
        print(f"  {path.name}: {count} lookup(s) mapped")
        total += count

    print(f"total: {total}  " + ("APPLIED" if apply else "DRY RUN (nothing written)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
