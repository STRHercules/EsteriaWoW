"""Fix the ported races' camera data, portrait displays and chat language in Patch-Y.

1. CreatureModelData: every one of the 18 race model rows was written as a clone of one
   template (collision 2.03/1.00, bounding box maxZ 1.568) instead of the model's own
   numbers, so the camera framed the character around the waist or knees. Copy the values
   Eunoia ships for the same model files.
2. CreatureDisplayInfo: display rows 33070/32902 (Nightborne) and 33174 (Void Elf male)
   carried `DisplayidExtra` references that no client we own can satisfy; every stock race
   ships 0 there. Drop back to 0 and retire the leftover extra row.
3. ChrRaces: Void Elf/Lightforged/Dark Iron carried the donor's Horde language (1) while
   the server says Alliance/Common (7/0); align the client rows.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm, Wdbc  # noqa: E402
from fix_patch_y import load_entries  # noqa: E402
from inspect_client_races import Client  # noqa: E402

DATA = REPO / "3.3.5a - Dev/Data"
PATCH_Y = DATA / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
EUNOIA_MODELS = REPO / ".agents/plans/vulpera-pandaren-playable-races/eunoia-dbc/CreatureModelData.dbc"

MODEL_KEY = "DBFilesClient\\CreatureModelData.dbc"
DISPLAY_KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"
EXTRA_KEY = "DBFilesClient\\CreatureDisplayInfoExtra.dbc"
RACES_KEY = "DBFilesClient\\ChrRaces.dbc"

MODEL_ROWS = list(range(3632, 3658))
# our staged path -> Eunoia model row (the donor file is named differently)
MODEL_ALIASES = {"character\\eredar\\male\\eredarmale.m2": 17309}
DROP_EXTRA_DISPLAYS = (33070, 32902, 33174)
RETIRED_EXTRAS = (22002,)
LANGUAGE_FIXES = {19: (7, 0), 21: (7, 0), 23: (7, 0)}  # race -> (BaseLanguage, Alliance)
PORTED_RACES = (16, 17, 19, 21, 22, 23, 28, 29, 30)

# the display ids the server actually sends (see rev_1787850000004); pointing the
# client's ChrRaces at the same rows keeps one id space on both sides
SERVER_DISPLAY_IDS = {
    16: (60008, 60009), 17: (60010, 60011), 19: (60012, 60013), 21: (60014, 60015),
    22: (60016, 60017), 23: (60018, 60019), 28: (60020, 60021), 29: (60022, 60023),
    30: (60024, 60025),
}
# stock rows and the working Vulpera/Pandaren rows only fill the first name slot; the
# port filled all 48 and clobbered the two name-flag slots (30 and 46)
NAME_SLOTS = tuple(range(15, 62))


def norm(path: str) -> str:
    return path.replace(".mdx", ".m2").casefold()


def slug(path: str) -> str:
    return Path(path.replace("\\", "/")).stem.casefold()


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(v & 0xFFFFFFFF for v in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    client = Client()
    eunoia_model = Wdbc(EUNOIA_MODELS.read_bytes())
    entries = load_entries(storm)

    # ---- 1. camera / collision data -------------------------------------------------
    models = Wdbc(entries[MODEL_KEY])
    by_path = {norm(eunoia_model.text(r[2])): r for r in eunoia_model.rows}
    by_slug = {slug(eunoia_model.text(r[2])): r for r in eunoia_model.rows}
    updated = 0
    for row in models.rows:
        if row[0] not in MODEL_ROWS:
            continue
        path = models.text(row[2])
        donor = by_path.get(norm(path)) or by_slug.get(slug(path))
        alias = MODEL_ALIASES.get(norm(path))
        if donor is None and alias:
            donor = eunoia_model.row(alias)
        if donor is None:
            print(f"  model {row[0]} {path}: NO EUNOIA ROW")
            continue
        for index in range(1, len(row)):
            if index != 2:
                row[index] = donor[index]
        updated += 1
    print(f"CreatureModelData: {updated} rows updated from Eunoia")
    entries[MODEL_KEY] = pack(models.rows, models.fields, models.record_size, models.strings)

    # ---- 2. portrait display rows ---------------------------------------------------
    displays = Wdbc(entries[DISPLAY_KEY])
    for row in displays.rows:
        if row[0] in DROP_EXTRA_DISPLAYS and len(row) > 3 and row[3]:
            print(f"  display {row[0]}: extra {row[3]} -> 0")
            row[3] = 0
    entries[DISPLAY_KEY] = pack(displays.rows, displays.fields, displays.record_size, displays.strings)

    effective_extras = Wdbc(client.find(EXTRA_KEY))
    referenced = {r[3] for r in displays.rows if len(r) > 3 and r[3]}
    rows = [r for r in effective_extras.rows if r[0] not in RETIRED_EXTRAS or r[0] in referenced]
    if len(rows) != len(effective_extras.rows):
        entries[EXTRA_KEY] = pack(rows, effective_extras.fields, effective_extras.record_size, effective_extras.strings)
        print(f"  {EXTRA_KEY}: retired {len(effective_extras.rows) - len(rows)} unreferenced extra row(s)")

    # ---- 3. client-side language / faction for the Alliance races -------------------
    races = Wdbc(entries[RACES_KEY])
    for row in races.rows:
        if row[0] not in PORTED_RACES:
            continue
        fix = LANGUAGE_FIXES.get(row[0])
        if fix and (row[7], row[13]) != fix:
            print(f"  race {row[0]} {races.text(row[11])}: BaseLanguage {row[7]}->{fix[0]}, Alliance {row[13]}->{fix[1]}")
            row[7], row[13] = fix
        want_male, want_female = SERVER_DISPLAY_IDS[row[0]]
        if (row[4], row[5]) != (want_male, want_female):
            print(f"  race {row[0]} {races.text(row[11])}: display {row[4]}/{row[5]} -> {want_male}/{want_female}")
            row[4], row[5] = want_male, want_female
        filled = [index for index in NAME_SLOTS if row[index]]
        if filled:
            print(f"  race {row[0]} {races.text(row[11])}: clearing {len(filled)} extra name slots")
            for index in NAME_SLOTS:
                row[index] = 0
    entries[RACES_KEY] = pack(races.rows, races.fields, races.record_size, races.strings)

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-race-visuals-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, {k: entries[k] for k in (MODEL_KEY, DISPLAY_KEY, EXTRA_KEY, RACES_KEY)})
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
