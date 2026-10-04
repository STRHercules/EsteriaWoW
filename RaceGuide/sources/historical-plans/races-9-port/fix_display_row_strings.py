"""Clear the donor string offsets that leaked into the ported races' player display rows.

`CreatureDisplayInfo.TextureVariation_1/2/3` and `PortraitTextureName` are *string* offsets
into the DBC's own string pool. Every stock player row, every one of Esteria's working custom
rows (Broken 60002/60003, Sethrak 60000/60001) and the donor's own player rows for these races
carry 0 there. The ported rows 60008-60025 instead carry ``51`` in all four fields, because the
rows were re-keyed from donor *NPC* rows whose offsets only resolve against the donor's pool -
in our pool offset 51 lands inside "HumanMaleCitizenLow", i.e. it is not a string at all.

The same four fields are garbage on the older Vulpera/Pandaren player rows
(141254/141255, 141687/141688), which is why those two never had portraits either.

This zeroes field 3 (`ExtendedDisplayInfoID`), fields 6-8 (`TextureVariation_*`) and field 9
(`PortraitTextureName`) on those rows, matching the server DB (`creaturedisplayinfo_dbc`) and
the player-row shape every working race uses.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm, Wdbc  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"

ROWS = tuple(range(60004, 60026)) + (141254, 141255, 141687, 141688)
CLEAR_FIELDS = (3, 6, 7, 8, 9)


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    archive = storm.open_archive(PATCH_Y)
    try:
        payload = storm.read(archive, KEY)
    finally:
        storm.dll.SFileCloseArchive(archive)
    table = Wdbc(payload)
    changed = 0
    for row in table.rows:
        if row[0] not in ROWS:
            continue
        before = [row[index] for index in CLEAR_FIELDS]
        if not any(before):
            continue
        for index in CLEAR_FIELDS:
            row[index] = 0
        changed += 1
        print(f"  display {row[0]}: cleared {before} -> {[row[index] for index in CLEAR_FIELDS]}")
    if not changed:
        raise SystemExit("nothing to change")

    entry = pack(table.rows, table.fields, table.record_size, table.strings)
    if args.dry_run:
        print(f"dry run - {changed} rows would change, Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-display-strings-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {KEY: entry})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), rows changed: {changed}, backup {backup}")


if __name__ == "__main__":
    main()
