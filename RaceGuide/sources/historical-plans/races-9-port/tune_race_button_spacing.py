"""Tighten the character creator's race-button grid.

`CharacterCreate_PositionRaceButtons()` lays the faction race buttons out in a
two-column grid (`columnSpacing = 118`, `rowSpacing = 100`) starting 120 units
from the top-left/top-right corner. With the ported race list that step leaves
too much air between the icons, so it is reduced here.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
LUA_KEY = "Interface\\GlueXML\\CharacterCreate.lua"
COLUMN_SPACING = 100
ROW_SPACING = 80


def tighten(lua: str) -> tuple[str, list[str]]:
    changes = []
    for name, value in (("columnSpacing", COLUMN_SPACING), ("rowSpacing", ROW_SPACING)):
        pattern = re.compile(rf"local {name} = \d+")
        match = pattern.search(lua)
        if match is None:
            raise SystemExit(f"local {name} not found in the creator Lua")
        if match.group(0) != f"local {name} = {value}":
            changes.append(f"{match.group(0)} -> local {name} = {value}")
            lua = pattern.sub(f"local {name} = {value}", lua, count=1)
    return lua, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(PATCH_Y)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        live_name = names.get(LUA_KEY.casefold())
        if live_name is None:
            raise SystemExit("CharacterCreate.lua not in Patch-Y")
        original = storm.read(handle, live_name).decode("utf-8")
    finally:
        storm.dll.SFileCloseArchive(handle)
    lua, changes = tighten(original)
    for line in changes:
        print(line)
    if not changes:
        print("spacing already applied")
        return
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return
    storm.replace_archive_entries(PATCH_Y, {live_name: lua.encode("utf-8")})
    print(f"Patch-Y updated: columnSpacing={COLUMN_SPACING} rowSpacing={ROW_SPACING}")


if __name__ == "__main__":
    main()
