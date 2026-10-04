"""Map the remaining team uses that are an index, a switch, or a PvP decision.

These are outside the battleground directories but have the same two properties: a Freeborn could
index a two-element store with TEAM_FREEBORN, or a Freeborn is silently on no side at all. The
mapping is the identity for Alliance and Horde, so nothing changes for any other character.

Usage:  python map_other_team.py            # dry run
        python map_other_team.py --apply
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INCLUDE = '#include "PlayerTeamSide.h"'

# (file, [(before, after, expected_count)])
RULES = {
    "src/server/game/DungeonFinding/LFGMgr.cpp": [
        ("RaidBrowserStore[player->GetTeamId()]", "RaidBrowserStore[PvpSideOf(player)]", 1),
        ("RBUsedDungeonsStore[player->GetTeamId()]", "RBUsedDungeonsStore[PvpSideOf(player)]", 1),
        ("RBSearchersStore[p->GetTeamId()]", "RBSearchersStore[PvpSideOf(p)]", 1),
        ("RBCacheStore[player->GetTeamId()]", "RBCacheStore[PvpSideOf(player)]", 2),
    ],
    "src/server/game/Achievements/AchievementMgr.cpp": [
        ("uint8(GetPlayer()->GetTeamId())", "uint8(PvpSideOf(GetPlayer()))", 1),
    ],
    "src/server/game/Entities/Player/PlayerUpdates.cpp": [
        ("ChannelMgr::forTeam(GetTeamId())", "ChannelMgr::forTeam(PvpSideOf(this))", 2),
    ],
    "src/server/game/Handlers/ChatHandler.cpp": [
        ("ChannelMgr::forTeam(sender->GetTeamId())", "ChannelMgr::forTeam(PvpSideOf(sender))", 1),
    ],
    "src/server/scripts/Northrend/zone_wintergrasp.cpp": [
        ("GetControlTeamId() == player->GetTeamId()", "GetControlTeamId() == PvpSideOf(player)", 2),
    ],
    "src/server/scripts/Spells/spell_quest.cpp": [
        ("switch (caster->GetTeamId())", "switch (PvpSideOf(caster))", 1),
    ],
    "src/server/scripts/Events/love_in_air.cpp": [
        ("(player->GetTeamId() == TEAM_ALLIANCE ?", "(PvpSideOf(player) == TEAM_ALLIANCE ?", 1),
    ],
}


def main() -> int:
    apply = "--apply" in sys.argv
    total = 0
    problems = []

    for name, rules in RULES.items():
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        for before, after, expected in rules:
            found = text.count(before)
            if found != expected:
                problems.append(f"{name}: expected {expected} of {before!r}, found {found}")
                continue
            text = text.replace(before, after)
            total += found
        if INCLUDE not in text:
            lines = text.splitlines()
            last = max(i for i, l in enumerate(lines) if l.startswith("#include"))
            lines.insert(last + 1, INCLUDE)
            text = "\n".join(lines) + "\n"
        if apply:
            path.write_text(text, encoding="utf-8", newline="\n")

    print(f"replacements: {total}  " + ("APPLIED" if apply else "DRY RUN (nothing written)"))
    for problem in problems:
        print("  PROBLEM: " + problem)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
