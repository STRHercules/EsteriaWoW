"""Inspect the supplied source portrait PNGs.

Answers the questions that decide how to use them: how big they are (a source that
is larger than the 64x64 client plates can be downscaled to a sharper roster
portrait), whether they are already circular, and which race/sex keys they cover
versus the ones ECS references.

Usage:
    python .agents/plans/character-select-redesign/tools/inspect_sources.py
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

SOURCE = Path(r"R:\Users\Zach\Pictures\Portraits")

by_shape: dict[tuple[int, int], int] = {}
rows = []
for path in sorted(SOURCE.rglob("*.png")):
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    by_shape[(w, h)] = by_shape.get((w, h), 0) + 1
    px = img.load()
    corners = [px[0, 0][3], px[w - 1, 0][3], px[0, h - 1][3], px[w - 1, h - 1][3]]
    # alpha a little inside the corner, to tell "fully transparent" from "masked"
    edge = px[int(w * 0.08), int(h * 0.08)][3]
    rows.append((path.parent.name, path.name, (w, h), max(corners), edge))

print("shapes:", {f"{w}x{h}": n for (w, h), n in sorted(by_shape.items())})
print()
print(f"{'side':<9} {'size':<10} {'corner':>7} {'8%in':>6}  name")
for side, name, (w, h), corner, edge in rows:
    print(f"{side:<9} {w}x{h:<6} {corner:>7} {edge:>6}  {name}")

# Which sex suffixes are present, and any duplicate suffixes across sides.
keys: dict[str, list[str]] = {}
for side, name, _, _, _ in rows:
    stem = name[: -len(".png")]
    stem = re.sub(r"^Charactercreate-races_", "", stem, flags=re.IGNORECASE)
    keys.setdefault(stem.casefold(), []).append(side)

dupes = {k: v for k, v in keys.items() if len(v) > 1}
print()
print(f"distinct source keys: {len(keys)}")
print(f"keys present on BOTH sides ({len(dupes)}): {sorted(dupes)}")
