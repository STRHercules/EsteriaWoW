"""Point Pandaren and Vulpera's client ChrRaces rows at the display ids the server sends.

The nine ported races work because `ChrRaces` and the world DB agree on the display id:
the client can map the player's display back to the race, which is what gives it a portrait
and a language list. Pandaren (18) and Vulpera (20) still disagree - the client says
141687/141688 and 141254/141255 while the server sends 60004-60007 - so both still render as
plain creatures with no portrait and no known languages.

This is the `align_vulpera_pandaren.py` change without the extras links: display rows
60004-60007 already carry `ExtendedDisplayInfoID = 0` and no bogus string offsets, the state
every working race uses. Revert with `revert_vulpera_pandaren.py` if it turns bad.
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
KEY = "DBFilesClient\\ChrRaces.dbc"

ALIGN = {18: (60004, 60005), 20: (60006, 60007)}


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--race", type=int, action="append", help="limit to one race id (default: both)")
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
        want = ALIGN.get(row[0])
        if args.race and row[0] not in args.race:
            continue
        if not want or (row[4], row[5]) == want:
            continue
        print(f"  race {row[0]} {table.text(row[11])}: display {row[4]}/{row[5]} -> {want[0]}/{want[1]}")
        row[4], row[5] = want
        changed += 1
    if not changed:
        raise SystemExit("nothing to change")

    entry = pack(table.rows, table.fields, table.record_size, table.strings)
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-legacy-align-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {KEY: entry})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), races changed: {changed}, backup {backup}")


if __name__ == "__main__":
    main()
