"""Is the portrait circle FRAMED consistently across the client's race plates?

Every row shows its portrait at the same size, so if the plates disagree about how
much of their 64x64 frame the circle occupies, the faces on screen come out at
different sizes from row to row. That is the one quality property a regenerated set
can guarantee and the shipped plates may not: masking from the 130x130 sources
inscribes an identical circle in every portrait.

Usage:
    python .agents/plans/character-select-redesign/tools/check_framing.py
"""

from __future__ import annotations

import ctypes
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # .../character-select-redesign
REPO = ROOT.parents[2]                  # .../EsteriaWoW
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / ".agents" / "plans" / "elvui-glue-reskin"))

from blp import decode_blp  # noqa: E402
from cars_mount_pack import DLL_DEFAULT, FindData, Storm  # noqa: E402

DATA = Path(r"G:\3.3.5a - Dev\Data")
PREFIX = "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-"
SUFFIX = re.compile(r"^(?!Gender)[A-Za-z0-9_]+(Male|Female)\.blp$", re.IGNORECASE)

storm = Storm(DLL_DEFAULT)
plates: dict[str, tuple[str, object]] = {}
for archive in (DATA / "patch-Z.MPQ", DATA / "patch-A.MPQ", DATA / "enUS" / "patch-enUS-Z.MPQ"):
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
            if name.casefold().startswith(PREFIX.casefold()) and name.casefold().endswith(".blp"):
                suffix = name[len(PREFIX):]
                if SUFFIX.match(suffix):
                    plates.setdefault(suffix.casefold(), (name, handle))
            if not storm.dll.SFileFindNextFile(finder, ctypes.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)

rows = []
for key, (name, handle) in sorted(plates.items()):
    try:
        img = decode_blp(storm.read(handle, name)).convert("RGBA")
    except OSError:
        continue
    if (img.width, img.height) != (64, 64):
        continue
    alpha = img.getchannel("A")
    histogram = alpha.histogram()
    opaque_ratio = histogram[255] / float(img.width * img.height)
    rows.append((name[len(PREFIX):], opaque_ratio))

if not rows:
    raise SystemExit("no 64x64 race plates found")

ratios = sorted(r for _, r in rows)
low, high = ratios[0], ratios[-1]
mean = sum(ratios) / len(ratios)
print(f"plates measured            : {len(rows)}")
print(f"opaque-area ratio (the face's share of the frame):")
print(f"  min  {low:.3f}   max  {high:.3f}   mean {mean:.3f}   spread {high - low:.3f}")
print()
print("most loosely framed (smallest face in frame):")
for name, ratio in sorted(rows, key=lambda r: r[1])[:6]:
    print(f"  {name:<34} {ratio:.3f}")
print("most tightly framed (largest face in frame):")
for name, ratio in sorted(rows, key=lambda r: -r[1])[:6]:
    print(f"  {name:<34} {ratio:.3f}")
