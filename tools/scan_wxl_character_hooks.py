"""Scan deployed WarcraftXL extension DLLs for character/customization hook strings."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(r"G:\3.3.5a - Dev\Extensions")
TERMS = (
    "CharCreateBaseTexture",
    "CharSetSkinColor",
    "CharLoadBaseVariation",
    "CharGeosetRenderPrep",
    "CharValidateComponentData",
    "CharAllocComponent",
    "CharRenderPrep",
    "CycleCharCustomization",
    "RandomizeCharCustomization",
    "Customization",
    "CharSections",
    "CharHair",
    "FacialHair",
    "ReadSkinTextureUnits",
    "ReadTextures",
    "SetupBatchTextures",
)


def ascii_strings(data: bytes) -> list[str]:
    return [item.decode("ascii", errors="ignore") for item in re.findall(rb"[ -~]{5,}", data)]


def main() -> int:
    for dll in sorted(ROOT.rglob("*.dll"), key=lambda path: str(path).casefold()):
        try:
            strings = ascii_strings(dll.read_bytes())
        except OSError:
            continue
        hits = sorted({line for line in strings if any(term.casefold() in line.casefold() for term in TERMS)})
        if hits:
            print(dll)
            for hit in hits:
                print(f"  {hit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
