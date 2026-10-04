"""Add an Alliance Illidari (race 31) to the client's Patch-Y by cloning race 30.

Eunoia ships two Illidari races - 24 "Illidari NightElf" (Alliance, Common) and 27
"Illidari Blood Elf" (Horde, Orcish) - but only the Blood Elf one was ported, which is why
Alliance shows 12 races against Horde's 13 in the creator. The client builds the creator's
race list from `ChrRaces.alliance` plus `CharBaseInfo`, so a cloned row with `alliance = 0`
puts the new race on the Alliance side with no Lua changes.

Cloned per table:
  * `ChrRaces`              - race 30 -> 31, faction 1, alliance 0, Common, displays 60026/60027
  * `CreatureDisplayInfo`   - display rows 60024/60025 -> 60026/60027 (same model ids)
  * `CharBaseInfo`          - every (30, class) -> (31, class)
  * `CharSections`, `CharHairGeosets`, `CharacterFacialHairStyles` - race 30 rows -> 31
  * `CharStartOutfit`       - race 30 rows -> 31 (the packed race byte inside field 1)
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

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

PATCH_Y = REPO / "3.3.5a - Dev/Data/Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
SOURCE_RACE = 30
TARGET_RACE = 31
SOURCE_DISPLAYS = (60024, 60025)
TARGET_DISPLAYS = (60026, 60027)
TABLES = {
    "ChrRaces": "DBFilesClient\\ChrRaces.dbc",
    "CreatureDisplayInfo": "DBFilesClient\\CreatureDisplayInfo.dbc",
    "CharBaseInfo": "DBFilesClient\\CharBaseInfo.dbc",
    "CharSections": "DBFilesClient\\CharSections.dbc",
    "CharHairGeosets": "DBFilesClient\\CharHairGeosets.dbc",
    "CharacterFacialHairStyles": "DBFilesClient\\CharacterFacialHairStyles.dbc",
    "CharStartOutfit": "DBFilesClient\\CharStartOutfit.dbc",
}


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = H()
    if not storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0x100, ctypes.byref(handle)):
        raise SystemExit("cannot open Patch-Y")
    payloads: dict[str, bytes] = {}
    try:
        for key in TABLES.values():
            payloads[key] = storm.read(handle, key)
    finally:
        storm.dll.SFileCloseArchive(handle)

    updates: dict[str, bytes] = {}

    # --- ChrRaces -----------------------------------------------------------------
    key = TABLES["ChrRaces"]
    table = Wdbc(payloads[key])
    source = next(row for row in table.rows if row[0] == SOURCE_RACE)
    clone = list(source)
    clone[0] = TARGET_RACE
    clone[2] = 1          # faction = Stormwind (Alliance)
    clone[4], clone[5] = TARGET_DISPLAYS
    clone[7] = 7          # BaseLanguage = Common
    clone[13] = 0         # alliance flag
    rows = [row for row in table.rows if row[0] != TARGET_RACE] + [clone]
    rows.sort(key=lambda row: row[0])
    updates[key] = pack(rows, table.fields, table.record_size, table.strings)
    print(f"ChrRaces: race {TARGET_RACE} cloned from {SOURCE_RACE} "
          f"(file {table.text(clone[11])!r}, displays {clone[4]}/{clone[5]}, language {clone[7]})")

    # --- CreatureDisplayInfo ------------------------------------------------------
    key = TABLES["CreatureDisplayInfo"]
    table = Wdbc(payloads[key])
    rows = [row for row in table.rows if row[0] not in TARGET_DISPLAYS]
    for source_id, target_id in zip(SOURCE_DISPLAYS, TARGET_DISPLAYS):
        origin = next(row for row in table.rows if row[0] == source_id)
        new_row = list(origin)
        new_row[0] = target_id
        rows.append(new_row)
        print(f"CreatureDisplayInfo: display {target_id} cloned from {source_id} (model {origin[1]})")
    rows.sort(key=lambda row: row[0])
    updates[key] = pack(rows, table.fields, table.record_size, table.strings)

    # --- CharBaseInfo (two byte fields per record) --------------------------------
    key = TABLES["CharBaseInfo"]
    data = payloads[key]
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data, 0)
    records = [data[20 + index * record_size : 20 + (index + 1) * record_size] for index in range(count)]
    classes = [record[1] for record in records if record[0] == SOURCE_RACE]
    records = [record for record in records if record[0] != TARGET_RACE]
    for klass in classes:
        records.append(bytes((TARGET_RACE, klass)))
    records.sort(key=lambda record: (record[0], record[1]))
    body = b"".join(records)
    pool = data[20 + count * record_size : 20 + count * record_size + string_size]
    # CharBaseInfo declares one pool byte and has no string fields; if a previous run already
    # truncated it, pad back to the declared size instead of copying the damage forward.
    pool = pool.ljust(string_size, b"\x00")
    updates[key] = struct.pack("<4s4I", magic, len(records), fields, record_size, string_size) + body + pool
    print(f"CharBaseInfo: race {TARGET_RACE} added for classes {classes}")

    # --- per-race tables ----------------------------------------------------------
    # Column layout matters: CharSections and CharHairGeosets carry an ID in field 0 and the
    # race in field 1, while CharacterFacialHairStyles has the race in field 0 and no id. Cloning
    # the wrong column is what left race 31 without skin/face/hair rows.
    for name, race_field, id_field in (
        ("CharSections", 1, 0),
        ("CharHairGeosets", 1, 0),
        ("CharacterFacialHairStyles", 0, None),
    ):
        key = TABLES[name]
        table = Wdbc(payloads[key])
        clones = [list(row) for row in table.rows if row[race_field] == SOURCE_RACE]
        if id_field is not None:
            next_id = max(row[id_field] for row in table.rows) + 1
            for row in clones:
                row[id_field] = next_id
                next_id += 1
        for row in clones:
            row[race_field] = TARGET_RACE
        rows = [row for row in table.rows if row[race_field] != TARGET_RACE] + clones
        rows.sort(key=lambda row: row[0])
        updates[key] = pack(rows, table.fields, table.record_size, table.strings)
        print(f"{name}: {len(clones)} rows cloned to race {TARGET_RACE} (race column {race_field})")

    # --- CharStartOutfit (race packed into byte 0 of the second dword) ------------
    key = TABLES["CharStartOutfit"]
    data = payloads[key]
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data, 0)
    pool = data[20 + count * record_size : 20 + count * record_size + string_size]
    # The DBC declares 77 fields but the record is 296 bytes, so the tail is byte-packed;
    # keep the raw record and only patch the id and the packed race byte.
    records = [bytearray(data[20 + index * record_size : 20 + (index + 1) * record_size]) for index in range(count)]
    clones = []
    for record in records:
        record_id, packed = struct.unpack_from("<II", record, 0)
        if (packed & 0xFF) != SOURCE_RACE:
            continue
        clone_record = bytearray(record)
        struct.pack_into("<I", clone_record, 0, record_id + 10000)
        struct.pack_into("<I", clone_record, 4, (packed & 0xFFFFFF00) | TARGET_RACE)
        clones.append(clone_record)
    records = [record for record in records if (struct.unpack_from("<I", record, 4)[0] & 0xFF) != TARGET_RACE] + clones
    records.sort(key=lambda record: struct.unpack_from("<I", record, 0)[0])
    body = b"".join(bytes(record) for record in records)
    updates[key] = struct.pack("<4s4I", magic, len(records), fields, record_size, string_size) + body + pool
    print(f"CharStartOutfit: {len(clones)} outfit rows cloned to race {TARGET_RACE}")

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-alliance-illidari-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, updates)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
