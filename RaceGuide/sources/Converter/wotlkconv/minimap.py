"""Minimap tiles, where 3.3.5a looks for them.

Retail keeps a map's minimap at ``World\\Minimaps\\<map>\\mapXX_YY.blp`` and a
WMO's at ``World\\Minimaps\\WMO\\<path>\\<name>_NNN_XX_YY.blp``.  3.3.5a does
not look there.  It reads ``Textures\\Minimap\\md5translate.trs``, which maps
each of those names to a file in ``Textures\\Minimap`` named by a hash::

    dir: Azeroth
    Azeroth\\map32_48.blp<TAB>1fcd95d6d410e7557d6b62081c5e87b5.blp

So each minimap tile is written under a hashed name and the index is built to
match.  Blizzard hashed the file's contents; any stable unique name does, so
the name is hashed instead, which lets a tile's destination be known before it
is converted.  Retail's ``noliquid_`` variants have no 3.3.5a counterpart and
are left where they are.

The index replaces the client's own, so it lists every minimap in the build,
not just the ones a narrowed run happens to convert.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Iterable

from .listfile import normalise

TRANSLATE_PATH = "textures\\minimap\\md5translate.trs"
HASHED_FOLDER = "textures\\minimap\\"

_MAP_TILE = re.compile(r"map\d{2}_\d{2}\.blp")
_WMO_TILE = re.compile(r".+_\d{3}_\d{2}_\d{2}\.blp")


def minimap_entry(game_path: str) -> tuple[str, str] | None:
    """``(directory, name)`` as md5translate.trs lists a minimap tile, or None."""
    parts = normalise(game_path).split("\\")
    if len(parts) < 4 or parts[0] != "world" or parts[1] != "minimaps":
        return None
    name = parts[-1]
    if parts[2] == "wmo":
        if len(parts) < 5 or not _WMO_TILE.fullmatch(name):
            return None
        directory = "wmo\\" + "\\".join(parts[3:-1])
    elif len(parts) == 4 and _MAP_TILE.fullmatch(name):
        directory = parts[2]
    else:
        return None
    return directory, f"{directory}\\{name}"


def hashed_path(entry_name: str) -> str:
    """Where a minimap tile is written: ``textures\\minimap\\<md5>.blp``."""
    digest = hashlib.md5(entry_name.lower().encode("latin-1")).hexdigest()
    return f"{HASHED_FOLDER}{digest}.blp"


def relocated_path(game_path: str) -> str | None:
    entry = minimap_entry(game_path)
    return hashed_path(entry[1]) if entry else None


def build_translate(game_paths: Iterable[str],
                    directories: dict[str, str] | None = None) -> bytes:
    """The md5translate.trs text for these minimap tiles.

    ``directories`` maps a lower-case map directory to the spelling Map.dbc
    uses, which the index follows; WMO paths are written ``WMO\\...``.
    """
    directories = directories or {}
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for path in game_paths:
        entry = minimap_entry(path)
        if entry is None:
            continue
        directory, name = entry
        if directory.startswith("wmo\\"):
            shown = "WMO" + directory[3:]
        else:
            shown = directories.get(directory, directory)
        grouped[shown].append((shown + name[len(directory):],
                               hashed_path(name)[len(HASHED_FOLDER):]))
    lines = []
    for directory in sorted(grouped, key=str.lower):
        lines.append(f"dir: {directory}")
        for name, hashed in sorted(set(grouped[directory]), key=lambda e: e[0].lower()):
            lines.append(f"{name}\t{hashed}")
    return "".join(line + "\r\n" for line in lines).encode("latin-1")
