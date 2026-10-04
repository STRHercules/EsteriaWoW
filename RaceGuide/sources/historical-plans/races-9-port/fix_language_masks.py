"""Let the client recognise the ported races' language skills.

`GetNumLanguages()` (Wow.exe 0x500760) walks `Languages.dbc` and for each row asks
`0x6e0640(player, languageId, &out)`. That helper resolves the language's spell id,
finds the `SkillLineAbility.dbc` row for that spell (`0x812410`, records at
`0xad45b4`, stride 0x38), and then looks for the row's *SkillLine* id in the
player's skill table. `0x812410` refuses rows whose `RaceMask` does not contain the
player's race, so a custom race is simply never counted - the client reports zero
languages and refuses to send chat ("You don't know that language").

Esteria already patched exactly these masks for their own custom races: Common 668
carries mask 7245 (races 1,3,4,7,11,12,13) and Orcish 669 mask 25522 (races
2,5,6,8,9,10,14,15). Our nine ported races plus Pandaren/Vulpera are in none of
them. This ORs those races into every language row that has a non-zero mask.

The mask only gates recognition - a character still has to *have* the skill - so
widening it cannot hand anybody a language they were not granted.
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
KEY = "DBFilesClient\\SkillLineAbility.dbc"

# SkillLine ids that are languages (98 Common, 109 Orcish, 111 Dwarvish, 113 Darnassian,
# 115 Taurahe, 137 Thalassian, 313 Gnomish, 315 Troll, 673 Goblin).
LANGUAGE_SKILLS = (98, 109, 111, 113, 115, 137, 313, 315, 673)
# Every custom playable race: 16,17,18,19,20,21,22,23,28,29,30,31 -> bits 15..22, 27..30.
RACE_BITS = 0x787F8000


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
    print(f"{KEY} <- {source}: fields={table.fields} record={table.record_size} rows={len(table.rows)}")
    changed = 0
    for row in table.rows:
        if row[1] not in LANGUAGE_SKILLS:
            continue
        if row[3] == 0:
            print(f"  row {row[0]} skill {row[1]} spell {row[2]}: mask 0 (unrestricted), left alone")
            continue
        if row[3] & RACE_BITS == RACE_BITS:
            continue
        print(f"  row {row[0]} skill {row[1]} spell {row[2]}: mask {row[3]:#x} -> {row[3] | RACE_BITS:#x}")
        row[3] |= RACE_BITS
        changed += 1
    if not changed:
        raise SystemExit("nothing to change")

    entries = {KEY: pack(table.rows, table.fields, table.record_size, table.strings)}
    if args.dry_run:
        print(f"dry run - {changed} rows would change, Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-language-masks-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(PATCH_Y, entries)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), rows changed: {changed}, backup {backup}")


if __name__ == "__main__":
    main()
