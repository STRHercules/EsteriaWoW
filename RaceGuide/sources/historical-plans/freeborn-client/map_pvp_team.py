"""Map every player-team use in the two-sided PvP code through PvpSideOf().

The mapping is the identity for Alliance and Horde, so the only characters whose behaviour can
change are Freeborn -- which is the point: they must never index a two-element store with
TEAM_FREEBORN.

Usage:  python map_pvp_team.py            # dry run, prints every change
        python map_pvp_team.py --apply    # rewrites the files
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INCLUDE = '#include "PlayerTeamSide.h"'

DIRECTORIES = (
    "src/server/game/Battlegrounds",
    "src/server/game/Battlefield",
    "src/server/game/OutdoorPvP",
    "src/server/scripts/Battlegrounds",
    "src/server/scripts/OutdoorPvP",
)

# Receivers that are a Player (or Player*) in these files. Anything else is reported instead of
# being changed, so a Battlefield::GetTeamId() or Battleground::GetTeamId() is never touched.
PLAYER_RECEIVERS = (
    "player", "Player", "killer", "killed", "plr", "newPlayer", "creator", "leader",
    "target", "victim", "owner", "attacker", "source", "Source", "caster", "unit",
)

# X->ToPlayer()->GetTeamId()  and  itr->second->GetTeamId()
TO_PLAYER = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)->ToPlayer\(\)->GetTeamId\(\)")
ITERATOR = re.compile(r"\b(itr->second|itr->first)->GetTeamId\(\)")
DIRECT = re.compile(r"\b(" + "|".join(PLAYER_RECEIVERS) + r")->GetTeamId\(\)")


def is_comment(line: str) -> bool:
    return line.lstrip().startswith("//")


def main() -> int:
    apply = "--apply" in sys.argv
    changed_files: list[Path] = []
    changed_lines: list[tuple[str, int, str, str]] = []
    skipped: list[tuple[str, int, str]] = []
    untouched: list[Path] = []

    for directory in DIRECTORIES:
        base = ROOT / directory
        if not base.is_dir():
            continue
        for path in sorted(list(base.rglob("*.cpp")) + list(base.rglob("*.h"))):
            text = path.read_text(encoding="utf-8")
            if "GetTeamId()" not in text:
                continue

            out_lines = []
            file_changed = False
            for number, line in enumerate(text.splitlines(), start=1):
                if is_comment(line):
                    if "GetTeamId()" in line:
                        skipped.append((str(path.relative_to(ROOT)), number, line.strip()))
                    out_lines.append(line)
                    continue

                new = TO_PLAYER.sub(lambda m: f"PvpSideOf({m.group(1)}->ToPlayer())", line)
                new = ITERATOR.sub(lambda m: f"PvpSideOf({m.group(1)})", new)
                new = DIRECT.sub(lambda m: f"PvpSideOf({m.group(1)})", new)

                if new != line:
                    file_changed = True
                    changed_lines.append((str(path.relative_to(ROOT)), number, line.strip(), new.strip()))
                elif "GetTeamId()" in line and "->GetTeamId" in line and "PvpSideOf" not in line:
                    skipped.append((str(path.relative_to(ROOT)), number, line.strip()))
                out_lines.append(new)

            if not file_changed:
                untouched.append(path)
                continue

            text = "\n".join(out_lines)
            if text and not text.endswith("\n"):
                text += "\n"
            if INCLUDE not in text:
                # after the last #include at the top of the file
                lines = text.splitlines()
                last = max(i for i, l in enumerate(lines) if l.startswith("#include"))
                lines.insert(last + 1, INCLUDE)
                text = "\n".join(lines) + "\n"

            if apply:
                path.write_text(text, encoding="utf-8", newline="\n")
            changed_files.append(path)

    print(f"files to change: {len(changed_files)}   lines: {len(changed_lines)}")
    for name, number, before, after in changed_lines:
        print(f"  {name}:{number}\n      - {before}\n      + {after}")
    print(f"\nleft alone (comments): {len(skipped)}")
    for name, number, line in skipped[:20]:
        print(f"  {name}:{number}: {line}")
    if len(skipped) > 20:
        print(f"  ... and {len(skipped) - 20} more")
    print("\nAPPLIED" if apply else "\nDRY RUN (nothing written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
