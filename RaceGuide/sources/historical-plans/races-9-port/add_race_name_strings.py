"""Give the custom races their names in the creator's race lists.

`CharacterCreate.lua` builds the race list with `_G["RACE_" .. raceID]`, which only exists for
the stock races, so the custom ones have been listed as "Race 16" and so on. This appends the
missing globals to Patch-Y's copy of that file.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import shutil
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
KEY = "Interface\\GlueXML\\CharacterCreate.lua"
NAMES = {
    14: "Broken", 15: "Sethrak", 16: "Eredar", 17: "Nightborne", 18: "Pandaren",
    19: "Void Elf", 20: "Vulpera", 21: "Lightforged Draenei", 22: "Zandalari Troll",
    23: "Dark Iron Dwarf", 28: "Dracthyr", 29: "Kul Tiran", 30: "Illidari", 31: "Illidari",
}
MARKER = "-- custom race names"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0x100, ctypes.byref(handle)):
        raise SystemExit("cannot open Patch-Y")
    try:
        payload = storm.read(handle, KEY)
    finally:
        storm.dll.SFileCloseArchive(handle)
    text = payload.decode("latin1")
    if MARKER in text:
        raise SystemExit("names already present")
    block = ["", MARKER]
    for race, name in sorted(NAMES.items()):
        block.append(f'if not _G["RACE_{race}"] then _G["RACE_{race}"] = "{name}" end')
    text = text.rstrip("\n") + "\n" + "\n".join(block) + "\n"
    print("\n".join(block[:4]) + f"\n... {len(NAMES)} names")
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-race-names-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {KEY: text.encode("latin1")})
    print(f"Patch-Y updated, backup {backup}")


if __name__ == "__main__":
    main()
