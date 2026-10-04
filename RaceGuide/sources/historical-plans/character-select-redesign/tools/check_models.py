"""Check which race MODEL directories the client actually ships.

ECS resolves a race by finding a token as a SUBSTRING of the normalised background
model path (`S.GetRaceByModel`), returns the FIRST token that matches, and takes its
`artKey`. So two things are worth checking against the real client, neither of which
any offline Lua test can see:

  * a model directory that carries art but that no token can reach (its rows fall
    back to "Unknown Race" with no portrait);
  * a more specific variant that a broader token swallows first - e.g. if the client
    ships `DarkfallenHorde` and `Darkfallen`, the single `DARKFALLEN` token claims
    both and the Horde variant gets Alliance art.

Usage:
    python .agents/plans/character-select-redesign/tools/check_models.py
"""

from __future__ import annotations

import ctypes
import re
from collections import defaultdict
from pathlib import Path

import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents" / "plans" / "elvui-glue-reskin"))

from cars_mount_pack import FindData, Storm, DLL_DEFAULT  # noqa: E402

DATA = Path(r"G:\3.3.5a - Dev\Data")
ARCHIVES = [DATA / "patch-Z.MPQ", DATA / "patch-A.MPQ", DATA / "enUS" / "patch-enUS-Z.MPQ"]

if not any(a.exists() for a in ARCHIVES):
    raise SystemExit(f"client archives not found under {DATA}")

storm = Storm(DLL_DEFAULT)
dirs: dict[str, set[str]] = defaultdict(set)

for archive in ARCHIVES:
    if not archive.exists():
        continue
    handle = storm.open_archive(archive)
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(handle, b"*", ctypes.byref(data), None)
    if not finder:
        continue
    try:
        while True:
            name = data.cFileName.split(b"\0", 1)[0].decode("latin-1")
            match = re.match(r"^Character\\([^\\]+)\\\.?.*\.(mdx|m2)$", name, re.IGNORECASE)
            if match:
                dirs[match.group(1).casefold()].add(match.group(1))
            if not storm.dll.SFileFindNextFile(finder, ctypes.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)

# Only the race directories matter here; the class/creature ones just add noise.
INTERESTING = re.compile(
    r"zandalari|darkfallen|illidari|demonhunter|sethrak|forsaken|scourge|vulpera|"
    r"nightborne|voidelf|lightforged|darkiron|kultiran|dracthyr|eredar|broken|high",
    re.IGNORECASE,
)

names = sorted({next(iter(v)) for k, v in dirs.items() if INTERESTING.search(k)})
print(f"race-ish model directories in the client: {len(names)}")
for name in names:
    print(f"  {name}")
