"""Rewrite GlueFontStyles.xml into the ElvUI 6.09 text palette.

The stock glue font styles are built around gold (1.0, 0.78, 0.0) text with
NORMAL_FONT_COLOR = (1.0, 0.82, 0). That gold is the "stock Warcraft" text colour
visible on the login, realm-list and dialog screens.

This keeps every font NAME and every inherits/justifyH/outline/spacing attribute
intact (other glue files inherit them) and only swaps colours, so nothing can
break from a missing font definition.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# The WINNING GlueFontStyles.xml is patch-enUS-2.MPQ's (retail-interface fork):
# it still uses gold text and defines extra fonts the stock file lacks
# (GlueFontNormalExtraSmall, OptionsFont*, CharacterCreateTooltipFont).
LIVE = HERE / "live" / "enUS2" / "Interface" / "GlueXML" / "GlueFontStyles.xml"
STOCK = HERE / "extracted" / "stock-locale" / "GlueFontStyles.xml"
OUT_DIR = HERE / "staging" / "locale" / "Interface" / "GlueXML"
OUT = OUT_DIR / "GlueFontStyles.xml"

# ElvUI 6.09 palette
TEXT = (0.898, 0.890, 0.890)     # light grey body text
WHITE = (1.000, 1.000, 1.000)
DISABLED = (0.420, 0.420, 0.420)
GOOD = (0.290, 0.680, 0.290)     # unitframe GOOD
BAD = (0.780, 0.250, 0.250)      # unitframe BAD
NEUTRAL = (0.850, 0.770, 0.360)  # unitframe NEUTRAL
ACCENT = (0.990, 0.480, 0.170)   # valuecolor #FD7A2B
MUTED = (0.560, 0.560, 0.560)

# Fonts that should keep semantic colours
GLOBAL_SCRIPT = {
    "NORMAL_FONT_COLOR": TEXT,
    "HIGHLIGHT_FONT_COLOR": WHITE,
    "GRAY_FONT_COLOR": (0.500, 0.500, 0.500),
    "GREEN_FONT_COLOR": GOOD,
    "RED_FONT_COLOR": BAD,
    "BLUE_FONT_COLOR": (0.000, 0.749, 0.953),
}


def colour_for(name: str) -> tuple[float, float, float] | None:
    """Map a glue font name to its ElvUI colour. None = leave untouched."""
    low = name.casefold()

    # explicit semantic families first
    if "realmdown" in low:
        return MUTED
    if "realminvalid" in low:
        return BAD
    if "realmcharacters" in low:
        return GOOD
    if "realmnocharacters" in low:
        return NEUTRAL

    if "disable" in low:
        return DISABLED
    if "green" in low:
        return GOOD
    if "red" in low:
        return BAD
    if "lightyellow" in low:
        return NEUTRAL
    if "highlight" in low:
        return WHITE
    if low.startswith("numberfont"):
        return WHITE
    if low == "tosfont":
        return WHITE
    if low == "glueeditboxfont":
        return WHITE
    if low == "dialogbuttonnormaltext":
        return TEXT
    if "normal" in low:
        return TEXT
    return None


COLOR_RE = re.compile(r"<Color\s+r=\"([0-9.]+)\"\s+g=\"([0-9.]+)\"\s+b=\"([0-9.]+)\"\s*/>")
FONT_OPEN_RE = re.compile(r"<Font\s+name=\"([^\"]+)\"")


def fmt(colour: tuple[float, float, float]) -> str:
    return f'<Color r="{colour[0]}" g="{colour[1]}" b="{colour[2]}"/>'


def transform(text: str) -> tuple[str, list[str]]:
    out: list[str] = []
    current: str | None = None
    changes: list[str] = []

    for line in text.splitlines():
        match = FONT_OPEN_RE.search(line)
        if match:
            current = match.group(1)
            out.append(line)
            if line.rstrip().endswith("/>"):
                current = None
            continue

        if current and COLOR_RE.search(line):
            target = colour_for(current)
            if target is not None:
                new_line = COLOR_RE.sub(fmt(target), line, count=1)
                if new_line != line:
                    changes.append(f"  {current}: {line.strip()} -> {new_line.strip()}")
                out.append(new_line)
                continue

        # the inline <Script> colour block
        handled = False
        for key, colour in GLOBAL_SCRIPT.items():
            if re.match(rf"\s*{key}\s*=", line):
                new_line = re.sub(
                    r"\{r=[0-9.]+, g=[0-9.]+, b=[0-9.]+\}",
                    "{{r={0}, g={1}, b={2}}}".format(*colour),
                    line,
                    count=1,
                )
                if new_line != line:
                    changes.append(f"  {key}: {line.strip()} -> {new_line.strip()}")
                out.append(new_line)
                handled = True
                break
        if handled:
            continue

        if "</Font>" in line:
            current = None
        out.append(line)

    return "\n".join(out) + "\n", changes


def main() -> int:
    source_path = LIVE if LIVE.exists() else STOCK
    if not source_path.exists():
        print(f"missing source: {source_path}")
        return 1
    print(f"source: {source_path}")
    source = source_path.read_text(encoding="utf-8")
    result, changes = transform(source)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(result, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(result)} bytes)")
    print(f"{len(changes)} colour changes:")
    for line in changes:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
