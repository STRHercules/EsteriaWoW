"""Repair the live Patch-Y: background scene keys, model paths, starting outfits.

Three fixes, all written back into `3.3.5a - Dev/Data/Patch-Y.MPQ`:

1. `CharacterCreate.lua` gains `RACE_BACKGROUND_KEYS` entries for the nine
   ported races. Without them `SetBackgroundModel` is handed a race key with no
   `UI_<Race>.m2` scene, the customize scene fails to build, and the character
   renders as the placeholder cube for every class except Death Knight (whose
   key resolves to the stock `UI_DeathKnight` scene).
2. `CreatureModelData` paths for those races are pointed at the models we ship,
   so Eredar stops looking for Eunoia's `Race_EredarMale.m2`.
3. `CharStartOutfit` rows for the races are rebuilt from Vulpera's rows with the
   gear left in place (the previous diagnostic build blanked every item slot,
   which is why the previews came up naked).
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402
sys.path.insert(0, str(REPO / ".agents/plans/races-9-port"))
from inspect_client_races import Client  # noqa: E402

DATA = REPO / "3.3.5a - Dev/Data"
PATCH_Y = DATA / "Patch-Y.MPQ"
PLAN = REPO / ".agents/plans/races-9-port"
BACKUP_ROOT = REPO / "3.3.5a - Dev/Backups"
# filestring -> stock background key (faction-correct, matches the Vulpera/Pandaren fix)
BACKGROUND_KEYS = {
    "EREDAR": "ORC",
    "NIGHTBORNE": "ORC",
    "ZANDALARITROLL": "ORC",
    "DRACTHYR": "ORC",
    "ILLIDARI": "ORC",
    "VOIDELF": "HUMAN",
    "LIGHTFORGEDDRAENEI": "HUMAN",
    "DARKIRONDWARF": "HUMAN",
    "KULTIRAN": "HUMAN",
}
RACES = [16, 17, 19, 21, 22, 23, 28, 29, 30]
OUTFIT_TEMPLATE_RACE = 20


def load_entries(storm: Storm) -> dict[str, bytes]:
    handle = storm.open_archive(PATCH_Y)
    try:
        entries = {}
        for name, *_ in storm.list_files(handle):
            if name.startswith("("):
                continue
            try:
                entries[name] = storm.read(handle, name)
            except Exception:  # noqa: BLE001
                pass
        return entries
    finally:
        storm.dll.SFileCloseArchive(handle)


def pack(rows: list[list[int]], fields: int, record: int, pool: bytes) -> bytes:
    body = b"".join(struct.pack(f"<{fields}I", *(value & 0xFFFFFFFF for value in row)) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, record, len(pool)) + body + pool


def pool_add(pool: bytearray, value: str) -> int:
    offset = len(pool)
    pool.extend(value.encode("utf-8") + b"\0")
    return offset


# Donor race in Eunoia's tables for each of ours.
DONOR_RACE = {16: 16, 17: 13, 19: 15, 21: 20, 22: 18, 23: 29, 28: 17, 29: 31, 30: 27}
EUNOIA_DBC = REPO / ".agents/plans/vulpera-pandaren-playable-races/eunoia-dbc"
# ChrRaces fields 65-67: facial-hair customisation x2, hair customisation.
CUSTOMISATION_FIELDS = (65, 66, 67)
CUSTOMISATION = {
    16: ("NORMAL", "NORMAL", "NORMAL"),
    17: ("NORMAL", "EARRINGS", "NORMAL"),
    19: ("NORMAL", "EARRINGS", "NORMAL"),
    21: ("NORMAL", "HORNS", "NORMAL"),
    22: ("TUSKS", "TUSKS", "NORMAL"),
    23: ("NORMAL", "PIERCINGS", "NORMAL"),
    28: ("NORMAL", "NORMAL", "NORMAL"),
    29: ("NORMAL", "EARRINGS", "NORMAL"),
    30: ("NORMAL", "NORMAL", "NORMAL"),
}


def patch_customisation_strings(entries: dict[str, bytes]) -> list[str]:
    """The port copied Vulpera's customisation strings onto every race.

    Those strings pick which geoset family the creator drives for a race
    (earrings, tusks, horns, piercings); Vulpera's values on a Void Elf or
    Zandalari leave the ear/tusk geosets unselected.
    """

    key = "DBFilesClient\\ChrRaces.dbc"
    table = Wdbc(entries[key])
    pool = bytearray(table.strings)
    changes = []
    for race, values in CUSTOMISATION.items():
        row = next((r for r in table.rows if r[0] == race), None)
        if row is None:
            continue
        before = [table.text(row[field]) if row[field] else "" for field in CUSTOMISATION_FIELDS]
        if before == list(values):
            continue
        for field, value in zip(CUSTOMISATION_FIELDS, values):
            row[field] = pool_add(pool, value)
        changes.append(f"race {race}: customisation {before} -> {list(values)}")
    entries[key] = pack(table.rows, table.fields, table.record_size, bytes(pool))
    return changes


def patch_facial_hair_styles(entries: dict[str, bytes]) -> list[str]:
    """Copy the donor race's facial-hair/earring/tusk geoset rows."""

    key = "DBFilesClient\\CharacterFacialHairStyles.dbc"
    ours = Wdbc(entries[key])
    donor = Wdbc((EUNOIA_DBC / "CharacterFacialHairStyles.dbc").read_bytes())
    rows = [list(row) for row in ours.rows if row[0] not in RACES]
    changes = []
    for race, donor_race in DONOR_RACE.items():
        picked = [list(row) for row in donor.rows if row[0] == donor_race]
        for row in picked:
            row[0] = race
        rows.extend(picked)
        changes.append(f"race {race}: {len(picked)} facial-feature rows from donor {donor_race}")
    rows.sort(key=lambda row: (row[0], row[1], row[2]))
    entries[key] = pack(rows, ours.fields, ours.record_size, ours.strings)
    return changes


def patch_sections_drop_noneffect(entries: dict[str, bytes]) -> list[str]:
    """Drop the donor's `...EXTRAnoneffect...` skin rows.

    The donor table carries every skin section twice: once with the overlay
    texture (`...skinEXTRA_...`, the glowing runes) and once with
    `...skinEXTRAnoneffect...`. Both copies sit in the same lookup key space,
    so which one the creator ends up on decides whether a race shows its
    overlay at all - that is why the effect kept appearing and disappearing
    between sessions. Keeping only the overlay rows makes it deterministic.
    """

    key = "DBFilesClient\\CharSections.dbc"
    table = Wdbc(entries[key])
    kept = []
    dropped = 0
    for row in table.rows:
        if row[1] in RACES and any(
            "noneffect" in table.text(row[field]).casefold() for field in (4, 5, 6) if row[field]
        ):
            dropped += 1
            continue
        kept.append(row)
    entries[key] = pack(kept, table.fields, table.record_size, table.strings)
    return [f"CharSections: dropped {dropped} noneffect rows, {len(kept)} remain"]


def patch_glue(lua: str) -> tuple[str, int]:
    anchor = '        ["MAGHAR"] = "ORC",\n'
    if anchor not in lua:
        raise SystemExit("RACE_BACKGROUND_KEYS anchor missing")
    additions = "".join(
        f'        ["{key}"] = "{value}",\n' for key, value in BACKGROUND_KEYS.items() if f'["{key}"]' not in lua
    )
    return lua.replace(anchor, anchor + additions, 1), additions.count("\n")


def patch_model_paths(entries: dict[str, bytes], manifest: dict) -> list[str]:
    key = "DBFilesClient\\CreatureModelData.dbc"
    table = Wdbc(entries[key])
    chrraces = Wdbc(entries["DBFilesClient\\ChrRaces.dbc"])
    displays = Wdbc(entries["DBFilesClient\\CreatureDisplayInfo.dbc"])
    pool = bytearray(table.strings)
    changes = []
    for race in RACES:
        row = next((r for r in chrraces.rows if r[0] == race), None)
        if row is None:
            continue
        spec = next((value for value in manifest.values() if value.get("race_id") == race), None)
        if spec is None:
            continue
        for gender, display_id in (("male", row[4]), ("female", row[5])):
            target = spec["target_paths"].get(gender)
            if not target:
                continue
            display = next((r for r in displays.rows if r[0] == display_id), None)
            if display is None:
                continue
            model = next((r for r in table.rows if r[0] == display[1]), None)
            if model is None:
                continue
            want = target.replace(".mdx", ".m2")
            have = table.text(model[2])
            if have.casefold() == want.casefold():
                continue
            offset = len(pool)
            pool.extend(want.encode("utf-8") + b"\0")
            model[2] = offset
            changes.append(f"race {race} {gender} model {model[0]}: {have} -> {want}")
    entries[key] = pack(table.rows, table.fields, table.record_size, bytes(pool))
    return changes


def patch_outfits(entries: dict[str, bytes]) -> list[str]:
    key = "DBFilesClient\\CharStartOutfit.dbc"
    data = entries[key]
    magic, count, fields, record, string_size = struct.unpack_from("<4s4I", data)
    pool = data[20 + count * record : 20 + count * record + string_size]
    rows = [bytearray(data[20 + i * record : 20 + (i + 1) * record]) for i in range(count)]
    templates = [row for row in rows if row[4] == OUTFIT_TEMPLATE_RACE]
    if not templates:
        raise SystemExit("no Vulpera outfit rows to clone")
    rows = [row for row in rows if row[4] not in RACES]
    next_id = max(int.from_bytes(bytes(row[0:4]), "little") for row in rows) + 1
    changes = []
    for race in RACES:
        gear = [row for row in templates]
        for template in gear:
            clone = bytearray(template)
            clone[0:4] = next_id.to_bytes(4, "little")
            clone[4] = race
            rows.append(clone)
            next_id += 1
        classes = sorted({row[5] for row in gear})
        blank = sum(1 for row in gear if bytes(row[8:20]) == b"\xff" * 12)
        changes.append(f"race {race}: {len(gear)} outfit rows from race {OUTFIT_TEMPLATE_RACE} classes={classes} blank={blank}")
    rows.sort(key=lambda row: int.from_bytes(bytes(row[0:4]), "little"))
    body = b"".join(bytes(row) for row in rows)
    entries[key] = struct.pack("<4s4I", magic, len(rows), fields, record, len(pool)) + body + pool
    return changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    storm = Storm(DLL_DEFAULT)
    entries = load_entries(storm)
    manifest = json.loads((PLAN / "port-manifest.json").read_text(encoding="utf-8"))
    race_id_map = {value["race"]: {"race_id": value["race_id"], **value} for value in manifest.values()}

    glue_key = "Interface\\GlueXML\\CharacterCreate.lua"
    glue, added = patch_glue(entries[glue_key].decode("utf-8"))
    entries[glue_key] = glue.encode("utf-8")
    customisation_changes = patch_customisation_strings(entries)
    facial_key = "DBFilesClient\\CharacterFacialHairStyles.dbc"
    if facial_key not in entries:
        payload = Client().find(facial_key)
        if payload is None:
            raise SystemExit("CharacterFacialHairStyles.dbc not found in the client")
        entries[facial_key] = payload
    facial_changes = patch_facial_hair_styles(entries)
    section_changes = patch_sections_drop_noneffect(entries)
    model_changes = patch_model_paths(entries, race_id_map)
    outfit_changes = patch_outfits(entries)

    for line in model_changes:
        print(line)
    for line in outfit_changes:
        print(line)
    for line in customisation_changes:
        print(line)
    for line in facial_changes:
        print(line)
    for line in section_changes:
        print(line)
    print(f"glue: {added} background keys added")
    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-fix-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, entries)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")


if __name__ == "__main__":
    main()
