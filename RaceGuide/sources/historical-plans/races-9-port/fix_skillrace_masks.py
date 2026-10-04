"""Let the client accept race 20 (Vulpera) wherever its tables say "all races".

The client's language check resolves every language through `SkillRaceClassInfo.dbc`:
`0x812410` finds the `SkillLineAbility` row for the language's spell and then calls
`0x810ed0(skill, race, class)`, which walks this table's records (stride 0x20) and requires
`raceMask & (1 << (race - 1))`. Almost every stock row carries `0xFFF7FFFF` - the "all races"
mask with **bit 19 cleared, i.e. race 20 excluded** - because race 20 is an NPC race in the
stock table. Our playable Vulpera *is* race 20, so every one of its language lookups fails and
the client ends up with an empty language list: `/say` then reports "You cannot speak that
language". This is why Vulpera is the only ported race that cannot chat.

This ORs bit 19 back into every `0xFFF7FFFF` row and ships the patched table in `Patch-Y`.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402
from inspect_client_races import DATA, ORDER  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
KEY = "DBFilesClient\\SkillRaceClassInfo.dbc"
ALL_RACES_MASK = 0xFFF7FFFF
RACE_20_BIT = 0x00080000


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def read_highest(key: str) -> tuple[bytes, str]:
    storm = Storm(DLL_DEFAULT)
    payload = None
    source = None
    for name in ORDER:
        path = DATA / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            payload = storm.read(handle, key)
            source = name
        except Exception:
            continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    if payload is None or source is None:
        raise SystemExit(f"{key}: not found")
    return payload, source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload, source = read_highest(KEY)
    table = Wdbc(payload)
    print(f"{KEY} <- {source}: rows={len(table.rows)} fields={table.fields}")
    changed = 0
    language_rows = 0
    for row in table.rows:
        if row[2] != ALL_RACES_MASK:
            continue
        row[2] |= RACE_20_BIT
        changed += 1
        if row[1] in (98, 109, 111, 113, 115, 137, 313, 315, 673, 674):
            language_rows += 1
    print(f"rows widened: {changed} (of which language skills: {language_rows})")
    if not changed:
        raise SystemExit("nothing to change")

    entry = pack(table.rows, table.fields, table.record_size, table.strings)
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-skillrace-masks-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(PATCH_Y, {KEY: entry})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
