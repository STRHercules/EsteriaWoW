"""Stage the Ogre (Horde, race 60) and Furbolg (Alliance, race 61) player races.

Focused, two-race builder. It refreshes the read-only preflight evidence, repairs the
proven donor model defects on staged copies, resolves the pinned shared dependencies,
normalizes the donor appearance selectors, converts the supplied portrait PNGs, and
generates staged client/server DBCs, Glue edits and a dedicated SQL revision.

It never installs anything: ``stage`` writes every artifact below the staging root and
``validate`` re-reads the staged output. Installation is a separate, explicitly
authorized step (see ``.agents/plans/ogre-furbolg-deepseek``).

The live client Z archives remain the merge base for every table. Donor rows are
selected and remapped; unrelated rows and string pools are preserved verbatim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "modules" / "mod-classless-wildcard" / "client-patch"))

import race_portrait_pack as portraits  # noqa: E402
import retroported_race_pack as p  # noqa: E402
import ctypes as c  # noqa: E402
from cars_mount_pack import Storm  # noqa: E402
from wod_model_migration import order_charsections_entry  # noqa: E402
from lib.clientfs import ClientFiles  # noqa: E402
from wod_model_migration import rebuild_archive_streaming  # noqa: E402

CLIENT_DEFAULT = Path(r"G:\3.3.5a - Dev")
DONOR_ROOT = ROOT / "Harvested" / "Playable_Races_Isolated_2026-10-04"
READY = DONOR_ROOT / "ReadyToPort"
DONOR_ARCHIVE = Path(r"G:\Downloads\HDWoWModels\Project Reforged\Data\patch-Z.MPQ")
CONFIG_ROOT = ROOT / "data" / "retroported-races"
ALLOCATION_PATH = CONFIG_ROOT / "allocation.json"
SERVER_DBC_ROOT = ROOT / "modules" / "mod-custom-server" / "data" / "dbc" / "retroported-races"
SQL_PENDING = ROOT / "data" / "sql" / "updates" / "pending_db_world"
STAGE_DEFAULT = Path(r"C:\Users\Zach\.codex\tmp\ogre-furbolg-20261004")
PICTURES = Path(r"R:\Users\Zach\Pictures\Portraits")

GLOBAL_ARCHIVE_REL = Path("Data") / "patch-Z.MPQ"
LOCALE_ARCHIVE_REL = Path("Data") / "enUS" / "patch-enUS-Z.MPQ"
ASSET_ARCHIVE_REL = Path("Data") / "Patch-T.MPQ"
DBC_ROOT = "DBFilesClient\\"
GLUE_ROOT = "Interface\\GlueXML\\"

# Pinned shared dependencies omitted by the isolation harvest (probe_missing_payload.py).
PINNED_DEPENDENCIES = {
    "Character\\Jinyu\\Male\\JinyuMaleLower_alpha.blp":
        "ff0901265c4b74debb1a8a258ef1c37543145be4662276beacc6802f686785a6",
    "Creature\\Furbolg\\FurbolgStuffRed.blp":
        "e5451e85255b5241cf2dd3a83d701ce669eed8e160547c33eb9992886ecf637b",
    "Creature\\Furbolg\\FurbolgStuffTransparent.blp":
        "03910da15fae5caeb002fac0847d33181353d5c8a477b331ea8e51c6d65bb4aa",
}

# Furbolg sequences 48/49/106/110 have embedded keyframes but a cleared embedded flag.
FURBOLG_EMBEDDED_SEQUENCES = {48: 0x20, 49: 0xA1, 106: 0xA1, 110: 0x20}
FURBOLG_ANIM_STEM = "Character\\Furbolg\\furbolgrace.m2"

RACE_SPECS = (
    {
        "slug": "ogre",
        "race_id": 60,
        "enum": "RACE_OGRE_HORDE",
        "faction": "horde",
        "donor_race_id": 25,
        "client_file_string": "OgreHorde",
        "prefix": "Og",
        "name": "Ogre",
        "start_profile": "durotar",
        "legacy_mask_race": 2,
        "visual_base_race": 2,
        "base_language": 1,
        "alliance_flag": 1,
        "class_compat": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11],
        "donor_start_race": 2,
        "donor_totem_race": 2,
        "portraits": {
            "male": PICTURES / "Horde/Charactercreate-races_ogre-male_horde.png",
            "female": PICTURES / "Horde/Charactercreate-races_ogre-female_horde.png",
        },
    },
    {
        "slug": "furbolg",
        "race_id": 61,
        "enum": "RACE_FURBOLG_ALLIANCE",
        "faction": "alliance",
        "donor_race_id": 18,
        "client_file_string": "Furbolg",
        "prefix": "Fu",
        "name": "Furbolg",
        "start_profile": "teldrassil",
        "legacy_mask_race": 4,
        "visual_base_race": 4,
        "base_language": 7,
        "alliance_flag": 0,
        "class_compat": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11],
        "donor_start_race": 4,
        "donor_totem_race": 11,
        "portraits": {
            "male": PICTURES / "Alliance/Charactercreate-races_furbolg-male_alliance.png",
            "female": PICTURES / "Alliance/Charactercreate-races_furbolg-male_alliance.png",
        },
    },
)

# Identity allocation (see section 3 of the handoff).
MODELS = {
    "ogre": {
        "male": {"model_id": 120062, "display_id": 60053, "donor_model_id": 10009, "donor_display_id": 50013,
                 "path": "Character\\Ogre\\Male\\ogremale.m2"},
        "female": {"model_id": 120063, "display_id": 60054, "donor_model_id": 10010, "donor_display_id": 50014,
                   "path": "Character\\Ogre\\Female\\ogreFemale.m2"},
    },
    "furbolg": {
        "male": {"model_id": 120064, "display_id": 60055, "donor_model_id": 60003, "donor_display_id": 60591,
                 "path": "Character\\Furbolg\\furbolgrace.m2"},
        "female": {"model_id": 120065, "display_id": 60056, "donor_model_id": 60004, "donor_display_id": 60592,
                   "path": "Character\\Furbolg\\furbolgrace.m2"},
    },
}

# Normalized appearance contract (section 5). donor value -> dense saved value.
APPEARANCE = {
    "ogre": {
        0: {  # gender
            "skin": {"colors": [0, 1, 2, 3, 4, 5]},
            "face": {"styles": [0, 1, 2, 3, 4], "colors": [0, 1, 2, 3, 4, 5]},
            "hair": {"styles": [0, 1, 2, 3, 4], "colors": [0, 1, 2, 3, 4]},
            "facial": {"styles": [0, 1, 2, 4, 5], "colors": [0, 1, 2, 3, 4]},
            "underwear": {"colors": [0, 1, 2, 3, 4, 5]},
        },
        1: {
            "skin": {"colors": [0, 1, 2, 3, 4, 5]},
            "face": {"styles": [0, 1, 2, 3, 4], "colors": [0, 1, 2, 3, 4, 5]},
            "hair": {"styles": [0, 1, 2, 3, 4, 5], "colors": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "facial": {"styles": [0, 1, 2, 4, 5, 6, 7, 8, 9, 10], "colors": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            "underwear": {"colors": [0, 1, 2, 3, 4, 5]},
        },
    },
    "furbolg": {
        0: {
            "skin": {"colors": [0, 1, 2, 3, 4, 5, 6]},
            "face": {"styles": [0], "colors": [0, 1, 2, 3, 4, 5, 6]},
            "hair": {"styles": [0], "colors": [0]},
            "facial": {"styles": [0, 1, 2, 3, 4, 5, 6], "colors": [0]},
            "underwear": {"colors": [0, 1, 2, 3, 4, 5, 6]},
        },
        1: {
            "skin": {"colors": [0, 1, 2, 3, 4, 5, 6]},
            "face": {"styles": [0], "colors": [0, 1, 2, 3, 4, 5, 6]},
            "hair": {"styles": [0], "colors": [0]},
            "facial": {"styles": [0, 1, 2, 3, 4, 5, 6], "colors": [0]},
            "underwear": {"colors": [0, 1, 2, 3, 4, 5, 6]},
        },
    },
}

# CharHairGeosets rows written for each race/gender: (variation, geoset, is_bald).
HAIR_GEOSETS = {
    "ogre": {
        0: [(0, 0, 1), (1, 1, 0), (2, 2, 0), (3, 3, 0), (4, 4, 0)],
        1: [(0, 2, 0), (1, 3, 0), (2, 4, 0), (3, 5, 0), (4, 6, 0), (5, 7, 0)],
    },
    "furbolg": {
        0: [(0, 0, 0)],
        1: [(0, 0, 0)],
    },
}

# Donor CharacterFacialHairStyles variation -> geoset tuple per gender.
FACIAL_GEOSET_DONORS = {
    "ogre": {
        0: {0: (2, 2, 2, 0, 0), 1: (1, 3, 3, 0, 0), 2: (1, 4, 4, 0, 0), 4: (2, 1, 1, 0, 0),
            5: (3, 5, 5, 0, 0), 6: (3, 0, 0, 0, 0), 7: (4, 1, 1, 0, 0), 8: (5, 2, 2, 0, 0),
            9: (5, 3, 3, 0, 0)},
        1: {0: (2, 2, 2, 0, 0), 1: (3, 3, 3, 0, 0), 2: (0, 4, 4, 0, 0), 4: (6, 6, 6, 0, 0),
            5: (2, 2, 2, 0, 0), 6: (3, 3, 3, 0, 0), 7: (4, 4, 4, 0, 0), 8: (5, 5, 5, 0, 0),
            9: (6, 6, 6, 0, 0), 10: (4, 4, 4, 0, 0)},
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def spec(slug: str) -> dict:
    for entry in RACE_SPECS:
        if entry["slug"] == slug:
            return entry
    raise KeyError(slug)


def load_allocation() -> dict:
    return json.loads(ALLOCATION_PATH.read_text(encoding="utf-8"))


def _read_archive_entry(storm: Storm, archive: Path, name: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)


def _effective(client_data: Path, entry: str) -> bytes:
    files = ClientFiles(str(client_data), "enUS")
    try:
        return files.find(entry)[0]
    finally:
        files.close()


def _full_table(client_data: Path, name: str) -> bytes:
    return _effective(client_data, f"{DBC_ROOT}{name}.dbc")


def _donor_tables() -> dict[str, bytes]:
    result = {}
    for path in (READY / "Shared").rglob("*.dbc"):
        name = next((n for n in p.WDBC_LAYOUTS if n.casefold() == path.stem.casefold()), path.stem)
        result[name] = path.read_bytes()
    return result

# --------------------------------------------------------------------------------------
# model repairs (staged copies only)
# --------------------------------------------------------------------------------------

def repair_furbolg_sequences(data: bytes) -> tuple[bytes, dict]:
    """Set the embedded flag only on the four proven embedded sequences."""
    seq_count, seq_offset = struct.unpack_from("<II", data, 0x1C)
    record_size = 0x40
    end = seq_offset + seq_count * record_size
    if not (0 < seq_offset and end <= len(data)):
        raise ValueError("furbolg sequence array runs past the model end")
    patched = bytearray(data)
    report = {}
    for index in range(seq_count):
        base = seq_offset + index * record_size
        sequence_id, variation = struct.unpack_from("<HH", data, base)
        flags_offset = base + 12
        flags = struct.unpack_from("<I", data, flags_offset)[0]
        expected = FURBOLG_EMBEDDED_SEQUENCES.get(sequence_id)
        if expected is None:
            continue
        if variation != 0:
            raise ValueError(f"furbolg sequence {sequence_id} variation {variation} is unexpected")
        if flags != (expected & 0x9F) and flags != expected:
            raise ValueError(f"furbolg sequence {sequence_id} flags {flags:#x} are not the audited value")
        struct.pack_into("<I", patched, flags_offset, expected)
        report[sequence_id] = {"index": index, "offset": flags_offset, "before": flags, "after": expected}
    if set(report) != set(FURBOLG_EMBEDDED_SEQUENCES):
        raise ValueError(f"furbolg embedded repair did not find every audited sequence: {sorted(report)}")
    return bytes(patched), report


def repair_ogre_female_skin(data: bytes, expected_max: int = 66) -> tuple[bytes, dict]:
    """Rewrite the oversized bone_count_max declaration when the palettes prove it safe."""
    if len(data) < 48:
        raise ValueError("ogre female skin header is truncated")
    declared = struct.unpack_from("<I", data, 0x2C)[0]
    submesh_count, submesh_offset = struct.unpack_from("<II", data, 0x1C)
    largest = 0
    for index in range(submesh_count):
        base = submesh_offset + index * 48
        if base + 48 > len(data):
            raise ValueError("ogre female submesh table runs past the skin end")
        largest = max(largest, struct.unpack_from("<H", data, base + 0x0C)[0])
    if largest != expected_max:
        raise ValueError(f"ogre female largest palette is {largest}, expected {expected_max}")
    if declared <= largest:
        return data, {"declared": declared, "largest": largest, "written": declared, "changed": False}
    patched = bytearray(data)
    struct.pack_into("<I", patched, 0x2C, largest)
    return bytes(patched), {"declared": declared, "largest": largest, "written": largest, "changed": True}


# --------------------------------------------------------------------------------------
# pinned dependencies
# --------------------------------------------------------------------------------------

def resolve_dependencies(storm: Storm, report: dict) -> dict[str, bytes]:
    resolved = {}
    for entry, expected in PINNED_DEPENDENCIES.items():
        payload = _read_archive_entry(storm, DONOR_ARCHIVE, entry)
        actual = digest(payload)
        if actual != expected:
            raise ValueError(f"pinned dependency {entry} hashes to {actual}, expected {expected}")
        resolved[entry] = payload
        report[entry] = {"bytes": len(payload), "sha256": actual, "source": str(DONOR_ARCHIVE)}
    return resolved


# --------------------------------------------------------------------------------------
# DBC merge
# --------------------------------------------------------------------------------------

def _records_by_id(data: bytes) -> dict[int, bytes]:
    table = p.RawWdbc(data)
    return {p._value(row, 0): row for row in table.records}, table


def _set_string_field(row: bytes, field: int, pool: bytearray, value: str) -> bytes:
    return p._set_string(row, field, pool, value)


def merge_chr_races(base: bytes, donor: bytes, spec_entry: dict) -> bytes:
    table = p.RawWdbc(base)
    donor_table = p.RawWdbc(donor)
    pool = bytearray(table.strings)
    records = list(table.records)
    existing = {p._value(row, 0): index for index, row in enumerate(records)}
    row = next((r for r in donor_table.records if p._value(r, 0) == spec_entry["donor_race_id"]), None)
    if row is None:
        raise ValueError(f"donor ChrRaces row {spec_entry['donor_race_id']} is missing")
    clone = p._clone_strings("ChrRaces", donor_table, row, pool)
    models = MODELS[spec_entry["slug"]]
    clone = p._replace(clone, 0, 4, spec_entry["race_id"])
    clone = p._replace(clone, 1 * 4, 4, 14)
    clone = _set_string_field(clone, 6, pool, spec_entry["prefix"])
    clone = p._replace(clone, 7 * 4, 4, spec_entry["base_language"])
    clone = _set_string_field(clone, 11, pool, spec_entry["client_file_string"])
    clone = p._replace(clone, 12 * 4, 4, 0)
    clone = p._replace(clone, 13 * 4, 4, spec_entry["alliance_flag"])
    clone = p._replace(clone, 4 * 4, 4, models["male"]["display_id"])
    clone = p._replace(clone, 5 * 4, 4, models["female"]["display_id"])
    for field in (*range(14, 30), *range(31, 47), *range(48, 64)):
        clone = _set_string_field(clone, field, pool, spec_entry["name"])
    if spec_entry["race_id"] in existing:
        records[existing[spec_entry["race_id"]]] = clone
    else:
        records.append(clone)
    return table.build(records, bytes(pool))


def _merge_row(base: bytes, donor: bytes, donor_id: int, target_id: int, pool: bytearray,
               changes: dict[int, int] | None = None, strings: dict[int, str] | None = None) -> bytes:
    donor_table = p.RawWdbc(donor)
    row = next((r for r in donor_table.records if p._value(r, 0) == donor_id), None)
    if row is None:
        raise ValueError(f"donor row {donor_id} is missing")
    clone = p._clone_strings(_table_name(donor_table), donor_table, row, pool)
    clone = p._replace(clone, 0, 4, target_id)
    for field, value in (changes or {}).items():
        clone = p._replace(clone, field * 4, 4, value)
    for field, value in (strings or {}).items():
        clone = _set_string_field(clone, field, pool, value)
    return clone


def _table_name(table) -> str:
    for name, layout in p.WDBC_LAYOUTS.items():
        if layout.record_size == table.record_size and layout.fields == table.fields:
            return name
    raise ValueError("unknown table layout")


def merge_creature_model_data(base: bytes, donor: bytes, spec_entry: dict) -> bytes:
    table = p.RawWdbc(base)
    pool = bytearray(table.strings)
    records = list(table.records)
    existing = {p._value(row, 0): index for index, row in enumerate(records)}
    for gender, model in MODELS[spec_entry["slug"]].items():
        clone = _merge_row(base, donor, model["donor_model_id"], model["model_id"], pool,
                           strings={2: model["path"]})
        if model["model_id"] in existing:
            records[existing[model["model_id"]]] = clone
        else:
            existing[model["model_id"]] = len(records)
            records.append(clone)
    return table.build(records, bytes(pool))


def merge_creature_display_info(base: bytes, donor: bytes, spec_entry: dict) -> bytes:
    table = p.RawWdbc(base)
    pool = bytearray(table.strings)
    records = list(table.records)
    existing = {p._value(row, 0): index for index, row in enumerate(records)}
    for gender, model in MODELS[spec_entry["slug"]].items():
        clone = _merge_row(base, donor, model["donor_display_id"], model["display_id"], pool,
                           changes={1: model["model_id"]})
        # Player batches read body/hair/facial textures through CharSections. Clear the
        # donor DragonSkin filler strings in fields 6-8.
        for field in (6, 7, 8):
            clone = p._replace(clone, field * 4, 4, 0)
        if model["display_id"] in existing:
            records[existing[model["display_id"]]] = clone
        else:
            existing[model["display_id"]] = len(records)
            records.append(clone)
    return table.build(records, bytes(pool))


SECTION_TYPES = {"skin": 0, "face": 1, "hair": 2, "facial": 3, "underwear": 4}


def _donor_section_rows(donor: bytes) -> dict:
    table = p.RawWdbc(donor)
    grouped = {}
    for row in table.records:
        race, gender, kind, t1, t2, t3, flags, style, color = struct.unpack_from(
            "<9I", row, 4)
        if not (flags & 1) or (flags & 4):
            continue
        grouped.setdefault((gender, kind, style, color), row)
        grouped.setdefault((gender, kind, style, None), row)
    return table, grouped


def build_char_sections(base: bytes, donor: bytes, allocation: dict, spec_entry: dict) -> tuple[bytes, dict]:
    table = p.RawWdbc(base)
    pool = bytearray(table.strings)
    records = list(table.records)
    donor_table, donor_rows = _donor_section_rows(donor)
    ids = p._allocated_sequence(allocation, spec_entry["slug"], "CharSections", 0)
    bounds = allocation["race_allocations"][spec_entry["slug"]]["CharSections"]
    next_id = bounds[0]
    appearance = APPEARANCE[spec_entry["slug"]]
    mapping = {}

    def append_row(gender: int, kind: int, style: int, color: int, source: bytes, flags: int) -> None:
        nonlocal next_id
        row = bytearray(40)
        struct.pack_into("<10I", row, 0, next_id, spec_entry["race_id"], gender, kind, 0, 0, 0, flags,
                         style, color)
        row = p._replace(bytes(row), 4 * 4, 4, p._append_string(pool, _row_string(donor_table, source, 4)))
        row = _set_string_field(row, 5, pool, _row_string(donor_table, source, 5))
        if _row_string(donor_table, source, 6):
            row = _set_string_field(row, 6, pool, _row_string(donor_table, source, 6))
        records.append(row)
        next_id += 1

    for gender in (0, 1):
        plan = appearance[gender]
        for name in ("skin", "face", "hair", "facial", "underwear"):
            kind = SECTION_TYPES[name]
            entry = plan[name]
            if name in ("skin", "underwear"):
                styles = [0]
            else:
                styles = entry["styles"]
            colors = entry["colors"]
            mapping[f"{gender}:{name}"] = {"styles": list(styles), "colors": list(colors)}
            for dense_style, donor_style in enumerate(styles):
                for dense_color, donor_color in enumerate(colors):
                    source = donor_rows.get((gender, kind, donor_style, donor_color))
                    if source is None:
                        source = donor_rows.get((gender, kind, donor_style, None))
                    if source is None:
                        fallback = sorted(style for (g, k, style, color) in donor_rows
                                          if g == gender and k == kind and color == donor_color)
                        if not fallback:
                            raise ValueError(f"donor has no {name} texture for gender {gender} color {donor_color}")
                        source = donor_rows[(gender, kind, fallback[0], donor_color)]
                    append_row(gender, kind, dense_style, dense_color, source, 0x01)

    if next_id - 1 > bounds[1]:
        raise ValueError(f"CharSections allocation {bounds} overflowed at {next_id - 1}")
    return table.build(records, bytes(pool)), mapping


def _row_string(table, row: bytes, field: int) -> str:
    offset = p._value(row, field * 4)
    if not offset:
        return ""
    return p._string(table.strings, offset).decode("utf-8", "replace")


def build_char_hair_geosets(base: bytes, allocation: dict, spec_entry: dict) -> bytes:
    table = p.RawWdbc(base)
    pool = bytearray(table.strings)
    records = list(table.records)
    next_id = allocation["race_allocations"][spec_entry["slug"]]["CharHairGeosets"][0]
    for gender, rows in sorted(HAIR_GEOSETS[spec_entry["slug"]].items()):
        for variation, geoset, bald in rows:
            row = bytearray(24)
            struct.pack_into("<6I", row, 0, next_id, spec_entry["race_id"], gender, variation, geoset, bald)
            records.append(bytes(row))
            next_id += 1
    return table.build(records, bytes(pool))


def build_facial_geosets(base: bytes, allocation: dict, spec_entry: dict) -> bytes:
    table = p.RawWdbc(base)
    pool = bytearray(table.strings)
    records = list(table.records)
    appearance = APPEARANCE[spec_entry["slug"]]
    donors = FACIAL_GEOSET_DONORS.get(spec_entry["slug"], {})
    for gender in (0, 1):
        styles = appearance[gender]["facial"]["styles"]
        for dense, donor_style in enumerate(styles):
            geosets = donors.get(gender, {}).get(donor_style, (0, 0, 0, 0, 0))
            row = bytearray(32)
            struct.pack_into("<8I", row, 0, spec_entry["race_id"], gender, dense, *geosets)
            records.append(bytes(row))
    return table.build(records, bytes(pool))


def clone_race_rows(base: bytes, table_name: str, allocation: dict, spec_entry: dict,
                    donor_race: int) -> tuple[bytes, int]:
    table = p.RawWdbc(base)
    layout = p.WDBC_LAYOUTS[table_name]
    pool = bytearray(table.strings)
    records = list(table.records)

    def race_of(row: bytes) -> int:
        if layout.race_width == 1:
            return row[layout.race_offset]
        return struct.unpack_from("<I", row, layout.race_offset)[0]

    donors = [row for row in table.records if race_of(row) == donor_race]
    if not donors:
        raise ValueError(f"live {table_name} has no rows for donor race {donor_race}")
    bounds = allocation["race_allocations"][spec_entry["slug"]][table_name]
    next_id = bounds[0]
    for row in donors:
        clone = _clone_and_rebase(table_name, table, row, pool)
        if layout.race_width == 1:
            clone = clone[:layout.race_offset] + bytes([spec_entry["race_id"]]) + clone[layout.race_offset + 1:]
        else:
            clone = p._replace(clone, layout.race_offset, layout.race_width, spec_entry["race_id"])
        if table_name != "CharacterFacialHairStyles":
            clone = p._replace(clone, 0, 4, next_id)
            next_id += 1
        records.append(clone)
    if table_name != "CharacterFacialHairStyles" and next_id - 1 > bounds[1]:
        raise ValueError(f"{table_name} allocation {bounds} overflowed at {next_id - 1}")
    return table.build(records, bytes(pool)), len(donors)


def _clone_and_rebase(table_name: str, table, row: bytes, pool: bytearray) -> bytes:
    clone = _rewrite_strings(table_name, table, row, pool)
    return clone


def _rewrite_strings(table_name: str, table, row: bytes, pool: bytearray) -> bytes:
    fields = p.STRING_FIELDS.get(table_name, ())
    data = row
    for field in fields:
        offset = p._value(data, field * 4)
        if not offset:
            continue
        data = p._set_string(data, field, pool, p._string(table.strings, offset).decode("utf-8", "replace"))
    return data


def clone_race_rows_unique_id(base: bytes, table_name: str, allocation: dict, spec_entry: dict,
                              donor_race: int) -> tuple[bytes, int]:
    return clone_race_rows(base, table_name, allocation, spec_entry, donor_race)


# --------------------------------------------------------------------------------------
# Glue edits
# --------------------------------------------------------------------------------------

import re  # noqa: E402

EXACT_RACE_LINES = (
    '    [60] = { glueString="OGREHORDE", name="Ogre", faction="Horde", fileString="OgreHorde" },\n',
    '    [61] = { glueString="FURBOLG", name="Furbolg", faction="Alliance", fileString="Furbolg" },\n',
)

RACE_INFO_BLOCKS = (
    '\ndo local info = {};\nfor key,value in pairs(RaceInfoByFileString.ORC or {}) do info[key]=value; end\n'
    'info.Name="Ogre";\nRaceInfoByFileString.OGREHORDE=info; end\n',
    '\ndo local info = {};\nfor key,value in pairs(RaceInfoByFileString.NIGHTELF or {}) do info[key]=value; end\n'
    'info.Name="Furbolg";\nRaceInfoByFileString.FURBOLG=info; end\n',
)

FOG_LINES = (
    '\nCharModelFogInfo["OGREHORDE"]=CharModelFogInfo["ORC"];\n\n'
    'CharModelGlowInfo["OGREHORDE"]=CharModelGlowInfo["ORC"];\n\n'
    'GlueAmbienceTracks["OGREHORDE"]=GlueAmbienceTracks["ORC"];\n',
    '\nCharModelFogInfo["FURBOLG"]=CharModelFogInfo["HUMAN"];\n\n'
    'CharModelGlowInfo["FURBOLG"]=CharModelGlowInfo["HUMAN"];\n\n'
    'GlueAmbienceTracks["FURBOLG"]=GlueAmbienceTracks["HUMAN"];\n',
)


def _insert_once(text: str, anchor: str, payload: str, label: str) -> str:
    if payload.strip() and payload.strip() in text:
        return text
    if anchor not in text:
        raise ValueError(f"Glue anchor for {label} is missing")
    return text.replace(anchor, anchor + payload, 1)


def patch_character_info(text: str) -> str:
    anchor = '    [59] = { glueString="THINHUMANHORDE", name="Forgotten", faction="Horde", fileString="ThinHumanHorde" },\n'
    text = _insert_once(text, anchor, "".join(EXACT_RACE_LINES), "CharacterInfo.EXACT_RACE_DATA")
    anchor = 'info.Name="Forgotten";\nRaceInfoByFileString.THINHUMANHORDE=info; end\n'
    if "RaceInfoByFileString.OGREHORDE" not in text:
        text = text.replace(anchor, anchor + "".join(RACE_INFO_BLOCKS), 1)
    if "RaceInfoByFileString.OGREHORDE" not in text or "RaceInfoByFileString.FURBOLG" not in text:
        raise ValueError("CharacterInfo race info blocks were not installed")
    return text


def patch_character_create(text: str) -> str:
    anchor = "RACE_ICON_TEXTURES = {\n"
    payload = (
        '    ["OGREHORDE_MALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-OgreHordeMale",\n'
        '    ["OGREHORDE_FEMALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-OgreHordeFemale",\n'
        '    ["FURBOLG_MALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-FurbolgMale",\n'
        '    ["FURBOLG_FEMALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-FurbolgFemale",\n'
    )
    return _insert_once(text, anchor, payload, "CharacterCreate.RACE_ICON_TEXTURES")


def patch_glue_strings(text: str) -> str:
    anchor = 'THINHUMANHORDE="Forgotten"; THINHUMANHORDE_MALE=THINHUMANHORDE; THINHUMANHORDE_FEMALE=THINHUMANHORDE;\n'
    payload = ('OGREHORDE="Ogre"; OGREHORDE_MALE=OGREHORDE; OGREHORDE_FEMALE=OGREHORDE;\n'
               'FURBOLG="Furbolg"; FURBOLG_MALE=FURBOLG; FURBOLG_FEMALE=FURBOLG;\n')
    return _insert_once(text, anchor, payload, "GlueStrings")


def patch_glue_parent(text: str) -> str:
    text = _insert_once(text, '        ["THINHUMAN"] = true,\n',
                        '        ["FURBOLG"] = true,\n', "GlueParent.allianceRaces")
    text = _insert_once(text, '        ["THINHUMANHORDE"] = true,\n',
                        '        ["OGREHORDE"] = true,\n', "GlueParent.hordeRaces")
    anchor = 'GlueAmbienceTracks["THINHUMANHORDE"]=GlueAmbienceTracks["ORC"];\n'
    return _insert_once(text, anchor, "".join(FOG_LINES), "GlueParent fog/ambience")


def patch_character_select(text: str) -> str:
    if 'raceModel == "OGREHORDE"' in text:
        return text
    anchor = 'raceModel == "THINHUMAN" )'
    if text.count(anchor) != 1:
        raise ValueError("CharacterSelect raceModel chain anchor is missing or ambiguous")
    return text.replace(anchor, 'raceModel == "THINHUMAN" or raceModel == "OGREHORDE"'
                                ' or raceModel == "FURBOLG" )', 1)


def patch_ecs_schema(text: str) -> str:
    text = _insert_once(text, '    [55] = {name="Tuskarr", faction=1, artKey="Tuskarr"},\n',
                        '    [60] = {name="Ogre", faction=2, artKey="OgreHorde"},\n'
                        '    [61] = {name="Furbolg", faction=1, artKey="Furbolg"},\n',
                        "ECS_Schema.RaceOverride")
    text = _insert_once(text, '    { "TUSKARR", { name = "Tuskarr", faction = 1, artKey = "Tuskarr" } },\n',
                        '    { "OGREHORDE", { name = "Ogre", faction = 2, artKey = "OgreHorde" } },\n'
                        '    { "FURBOLG", { name = "Furbolg", faction = 1, artKey = "Furbolg" } },\n',
                        "ECS_Schema name table")
    return _insert_once(text, "S.PortraitArtKeys = {\n",
                        "    OgreHorde=true, Furbolg=true,\n", "ECS_Schema.PortraitArtKeys")


def patch_ecs_integrate(text: str) -> str:
    marker = "(race >= 54 and race <= 59)"
    if marker not in text:
        if "(race >= 54 and race <= 61)" in text:
            return text
        raise ValueError("ECS_Integrate race range anchor is missing")
    return text.replace(marker, "(race >= 54 and race <= 61)", 1)


GLUE_PATCHERS = {
    "CharacterCreate.lua": patch_character_create,
    "CharacterInfo.lua": patch_character_info,
    "GlueStrings.lua": patch_glue_strings,
    "GlueParent.lua": patch_glue_parent,
    "CharacterSelect.lua": patch_character_select,
    "ECS_Schema.lua": patch_ecs_schema,
    "ECS_Integrate.lua": patch_ecs_integrate,
}


def build_glue(original: dict[str, bytes]) -> dict[str, bytes]:
    result = {}
    for name, patcher in GLUE_PATCHERS.items():
        source = original[name].decode("utf-8-sig")
        result[name] = patcher(source).encode("utf-8")
    return result


# --------------------------------------------------------------------------------------
# portraits
# --------------------------------------------------------------------------------------

CREATOR_ICON_ROOT = "Interface\\Glues\\CharacterCreate\\"
CHARACTER_FRAME_ROOT = "Interface\\CharacterFrame\\"
ECS_PORTRAIT_ROOT = "Interface\\Glues\\CharacterSelect\\"


def build_portraits(client: Path, spec_entry: dict) -> tuple[dict[str, bytes], dict]:
    storm = Storm(p.DLL_DEFAULT)
    handle = storm.open_archive(client / GLOBAL_ARCHIVE_REL)
    try:
        template = storm.read(handle, portraits.ICON_TEMPLATE_ENTRY)
        ring = portraits.ring_layer(portraits.decode_client_blp(storm.read(handle, portraits.RING_ENTRY)))
    finally:
        storm.dll.SFileCloseArchive(handle)
    mask = portraits.circular_mask()
    entries = {}
    report = {}
    for gender in ("male", "female"):
        source = spec_entry["portraits"][gender]
        if not source.is_file():
            raise FileNotFoundError(f"portrait source is missing: {source}")
        art = portraits.portrait_bytes(source, mask)
        plain = portraits.encode_portrait(art, template)
        bordered_img = portraits.compose_race_icon(art, ring)
        icon = portraits.encode_portrait(bordered_img, template)
        portraits.validate_portrait(plain, source)
        portraits.validate_portrait(icon, source)
        sex = gender.capitalize()
        token = spec_entry["client_file_string"]
        art_key = "OgreHorde" if spec_entry["slug"] == "ogre" else "Furbolg"
        entries[f"{CREATOR_ICON_ROOT}UI-CharacterCreate-{art_key}{sex}.blp"] = icon
        stem = f"{CHARACTER_FRAME_ROOT}TemporaryPortrait-{sex}-{token}"
        entries[stem] = plain
        entries[stem + ".blp"] = plain
        entries[f"{ECS_PORTRAIT_ROOT}ECS-Portrait-{art_key}{sex}.blp"] = plain
        report[gender] = {
            "source": str(source),
            "source_sha256": sha256(source),
            "art_key": art_key,
            "creator_icon_sha256": digest(icon),
            "portrait_sha256": digest(plain),
        }
    return entries, report


# --------------------------------------------------------------------------------------
# SQL
# --------------------------------------------------------------------------------------

SQL_TEMPLATE = """-- {name} ({race}), {faction}; generated by tools/ogre_furbolg_race_pack.py.

SET @RACE := {race};
SET @DONOR := {donor};

DELETE FROM `playercreateinfo` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @RACE, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @RACE;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @RACE, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @RACE, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @RACE, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = {totem};

DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@RACE, 0, {spell}, '{language}');

DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@RACE, 0, {skill}, 0, '{language}');

"""

CHRRACES_TEMPLATE = """DELETE FROM `chrraces_dbc` WHERE `ID` = {race};
INSERT INTO `chrraces_dbc` (`ID`, `Flags`, `FactionID`, `MaleDisplayId`, `FemaleDisplayId`, `ClientPrefix`,
    `BaseLanguage`, `ClientFilestring`, `Alliance`, `Name_Lang_enUS`)
VALUES ({race}, 14, {faction_template}, {male_display}, {female_display}, '{prefix}', {base_language},
    '{file_string}', {alliance}, '{name}');

"""


def build_sql(spec_entry: dict) -> str:
    text = SQL_TEMPLATE.format(
        name=spec_entry["name"], race=spec_entry["race_id"], faction=spec_entry["faction"],
        donor=spec_entry["donor_start_race"], totem=spec_entry["donor_totem_race"],
        spell=669 if spec_entry["faction"] == "horde" else 668,
        skill=109 if spec_entry["faction"] == "horde" else 98,
        language="Language Orcish" if spec_entry["faction"] == "horde" else "Language Common",
    )
    return text


def build_chrraces_sql(spec_entry: dict) -> str:
    models = MODELS[spec_entry["slug"]]
    return CHRRACES_TEMPLATE.format(
        race=spec_entry["race_id"],
        faction_template=2 if spec_entry["faction"] == "horde" else 4,
        male_display=models["male"]["display_id"], female_display=models["female"]["display_id"],
        prefix=spec_entry["prefix"], base_language=spec_entry["base_language"],
        file_string=spec_entry["client_file_string"], alliance=spec_entry["alliance_flag"],
        name=spec_entry["name"],
    )


def realm_class_set(table) -> list[int]:
    """The realm's active class set, read from an extended playable race's packed pairs."""
    import collections
    counts = collections.Counter(row[0] for row in table.records)
    for race, pairs in sorted(counts.items()):
        if pairs >= 10:
            return sorted(row[1] for row in table.records if row[0] == race)
    raise ValueError("live CharBaseInfo has no extended race carrying the realm class set")


def clone_char_base_info(base: bytes, spec_entry: dict) -> bytes:
    table = p.RawWdbc(base)
    classes = realm_class_set(table)
    if classes != sorted(spec_entry["class_compat"]):
        raise ValueError(f"realm class set {classes} does not match the declared contract "
                         f"{sorted(spec_entry['class_compat'])}")
    records = [row for row in table.records if row[0] != spec_entry["race_id"]]
    for class_id in classes:
        records.append(bytes([spec_entry["race_id"], class_id]))
    return table.build(records, table.strings)


def clone_char_start_outfit(base: bytes, spec_entry: dict) -> bytes:
    table = p.RawWdbc(base)
    records = [row for row in table.records]
    donors = [row for row in table.records if row[4] == spec_entry["donor_start_race"]]
    if not donors:
        raise ValueError(f"live CharStartOutfit has no rows for donor race {spec_entry['donor_start_race']}")
    for row in donors:
        records.append(row[:4] + bytes([spec_entry["race_id"]]) + row[5:])
    return table.build(records, table.strings)


def clone_namegen(base: bytes, allocation: dict, spec_entry: dict) -> tuple[bytes, int]:
    table = p.RawWdbc(base)
    pool = bytearray(table.strings)
    records = list(table.records)
    bounds = allocation["race_allocations"][spec_entry["slug"]]["NameGen"]
    next_id = bounds[0]
    donors = [row for row in table.records if p._value(row, 2 * 4) == spec_entry["donor_start_race"]]
    if not donors:
        raise ValueError(f"live NameGen has no rows for donor race {spec_entry['donor_start_race']}")
    for row in donors:
        clone = _rewrite_strings("NameGen", table, row, pool)
        clone = p._replace(clone, 0, 4, next_id)
        clone = p._replace(clone, 2 * 4, 4, spec_entry["race_id"])
        records.append(clone)
        next_id += 1
    if next_id - 1 > bounds[1]:
        raise ValueError("NameGen allocation overflowed")
    return table.build(records, bytes(pool)), len(donors)


def clone_barber(base: bytes, allocation: dict, spec_entry: dict) -> tuple[bytes, int]:
    table = p.RawWdbc(base)
    pool = bytearray(table.strings)
    records = list(table.records)
    bounds = allocation["race_allocations"][spec_entry["slug"]]["BarberShopStyle"]
    next_id = bounds[0]
    donors = [row for row in table.records if p._value(row, 37 * 4) == spec_entry["donor_start_race"]]
    for row in donors:
        clone = _rewrite_strings("BarberShopStyle", table, row, pool)
        clone = p._replace(clone, 0, 4, next_id)
        clone = p._replace(clone, 37 * 4, 4, spec_entry["race_id"])
        records.append(clone)
        next_id += 1
    if next_id - 1 > bounds[1]:
        raise ValueError("BarberShopStyle allocation overflowed")
    return table.build(records, bytes(pool)), len(donors)


def build_tables(client_data: Path, allocation: dict) -> tuple[dict[str, bytes], dict]:
    donor = _donor_tables()
    evidence = {"tables": {}, "counts": {}}
    output = {}
    for name in ("ChrRaces", "CreatureModelData", "CreatureDisplayInfo", "CharSections",
                 "CharHairGeosets", "CharacterFacialHairStyles", "CharBaseInfo", "CharStartOutfit",
                 "NameGen", "BarberShopStyle"):
        output[name] = _full_table(client_data, name)
    for spec_entry in RACE_SPECS:
        slug = spec_entry["slug"]
        output["ChrRaces"] = merge_chr_races(output["ChrRaces"], donor["ChrRaces"], spec_entry)
        output["CreatureModelData"] = merge_creature_model_data(
            output["CreatureModelData"], donor["CreatureModelData"], spec_entry)
        output["CreatureDisplayInfo"] = merge_creature_display_info(
            output["CreatureDisplayInfo"], donor["CreatureDisplayInfo"], spec_entry)
        output["CharSections"], mapping = build_char_sections(
            output["CharSections"], donor["CharSections"], allocation, spec_entry)
        output["CharHairGeosets"] = build_char_hair_geosets(
            output["CharHairGeosets"], allocation, spec_entry)
        output["CharacterFacialHairStyles"] = build_facial_geosets(
            output["CharacterFacialHairStyles"], allocation, spec_entry)
        output["CharBaseInfo"] = clone_char_base_info(output["CharBaseInfo"], spec_entry)
        output["CharStartOutfit"] = clone_char_start_outfit(output["CharStartOutfit"], spec_entry)
        output["NameGen"], names = clone_namegen(output["NameGen"], allocation, spec_entry)
        output["BarberShopStyle"], barber = clone_barber(output["BarberShopStyle"], allocation, spec_entry)
        evidence["tables"][slug] = {
            "appearance_mapping": mapping,
            "namegen_rows": names,
            "barbershop_rows": barber,
        }
    for name, data in output.items():
        table = p.RawWdbc(data)
        evidence["counts"][name] = table.count
        if name in ("CharStartOutfit", "CharBaseInfo"):
            # Packed/composite tables whose first column is not a unique row id.
            continue
        if name == "CharacterFacialHairStyles":
            # Composite key (race, gender, variation) with no independent row id. The live
            # table already carries pre-existing duplicates, so only the new races are checked.
            keys = [tuple(struct.unpack_from("<3I", row, 0)) for row in table.records
                    if struct.unpack_from("<I", row, 0)[0] in (60, 61)]
            duplicates = {k for k in keys if keys.count(k) > 1}
            if duplicates:
                raise ValueError(f"{name} has duplicate composite keys for 60/61: {sorted(duplicates)[:10]}")
            continue
        ids = [p._value(row, 0) for row in table.records]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{name} has duplicate first-column IDs")
    return output, evidence


def counts_for_race(tables: dict[str, bytes], race_id: int) -> dict:
    result = {}
    for name in ("CharSections", "CharHairGeosets", "CharacterFacialHairStyles", "CharBaseInfo",
                 "CharStartOutfit", "NameGen", "BarberShopStyle"):
        layout = p.WDBC_LAYOUTS[name]
        table = p.RawWdbc(tables[name])
        total = 0
        for row in table.records:
            if layout.race_width == 1:
                value = row[layout.race_offset]
            else:
                value = p._value(row, layout.race_offset)
            if value == race_id:
                total += 1
        result[name] = total
    return result


# --------------------------------------------------------------------------------------
# staging / validation / plan
# --------------------------------------------------------------------------------------

def asset_entries(storm: Storm, spec_entry: dict) -> dict[str, bytes]:
    entries = {}
    for group in ("Ogre", "Furbolg"):
        root = READY / group
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            name = str(path.relative_to(root))
            if path.suffix.casefold() == ".dbc":
                continue
            entries[name] = path.read_bytes()
    if spec_entry["slug"] != "furbolg":
        # assets are shared across both races; only add once
        pass
    return entries


def model_entries(spec_entry: dict) -> tuple[dict[str, bytes], dict]:
    entries = {}
    report = {}
    for group in ("Furbolg",):
        root = READY / group
        for path in root.rglob("*.m2"):
            name = str(path.relative_to(root))
            payload = path.read_bytes()
            if name.casefold() == FURBOLG_ANIM_STEM.casefold():
                payload, detail = repair_furbolg_sequences(payload)
                report[name] = {"repair": "furbolg_sequences", "detail": detail}
            entries[name] = payload
    for group in ("Ogre",):
        root = READY / group
        for path in root.rglob("*.m2"):
            name = str(path.relative_to(root))
            payload = path.read_bytes()
            entries[name] = payload
    skin_path = READY / "Ogre/Character/Ogre/Female/ogrefemale00.skin"
    payload, detail = repair_ogre_female_skin(skin_path.read_bytes())
    entries[str(skin_path.relative_to(READY / "Ogre"))] = payload
    report[str(skin_path.relative_to(READY / "Ogre"))] = {"repair": "ogre_female_skin", "detail": detail}
    return entries, report


H = c.c_void_p


def rebuild_archive_replacing(storm: Storm, source_path: Path, target_path: Path,
                              replacements: dict[str, bytes], *, compress: bool = True) -> dict:
    """Single-pass streaming rebuild that substitutes entries by case-insensitive name."""
    if target_path.exists():
        target_path.unlink()
    wanted = {name.casefold(): (name, payload) for name, payload in replacements.items()}
    used: set[str] = set()
    source = storm.open_archive(source_path)
    target = H()
    written = 0
    added: list[str] = []
    try:
        source_entries = [name for name, *_ in storm.list_files(source)
                          if name.casefold() not in {"(listfile)", "(attributes)"}]
        if not storm.dll.SFileCreateArchive(str(target_path), 0x00100000 | 0x00200000,
                                            len(source_entries) + len(replacements) + 64, c.byref(target)):
            raise OSError(f"SFileCreateArchive failed: {target_path} ({c.get_last_error()})")

        def write(name: str, payload: bytes) -> None:
            nonlocal written
            handle = H()
            if not storm.dll.SFileCreateFile(target, name.encode("ascii"), 0, len(payload), 0,
                                             0x00000200 if compress else 0,
                                             c.byref(handle)):
                raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
            finished = False
            try:
                buffer = c.create_string_buffer(payload or b"\0")
                if not storm.dll.SFileWriteFile(handle, buffer, len(payload), 0x00000002):
                    raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
                if not storm.dll.SFileFinishFile(handle):
                    raise OSError(f"SFileFinishFile failed: {name} ({c.get_last_error()})")
                finished = True
            finally:
                if not finished:
                    storm.dll.SFileCloseFile(handle)
            written += 1

        for name in source_entries:
            key = name.casefold()
            if key in wanted:
                payload = order_charsections_entry(name, wanted[key][1])
                used.add(key)
            else:
                payload = order_charsections_entry(name, storm.read(source, name))
            write(name, payload)
        for key, (name, payload) in wanted.items():
            if key not in used:
                write(name, order_charsections_entry(name, payload))
                added.append(name)
    finally:
        if target:
            storm.dll.SFileCloseArchive(target)
        storm.dll.SFileCloseArchive(source)
    return {"entries_written": written, "added": sorted(added)}


def stage(client: Path) -> dict:
    allocation = load_allocation()
    donor = _donor_tables()
    storm = Storm(p.DLL_DEFAULT)
    stage_root = STAGE_DEFAULT
    if stage_root.exists():
        shutil.rmtree(stage_root)
    (stage_root / "client/Data/enUS").mkdir(parents=True, exist_ok=True)
    (stage_root / "server/dbc").mkdir(parents=True, exist_ok=True)
    (stage_root / "sql").mkdir(parents=True, exist_ok=True)

    dep_report: dict = {}
    dependencies = resolve_dependencies(storm, dep_report)
    tables, table_evidence = build_tables(client / "Data", allocation)

    assets = {}
    for spec_entry in RACE_SPECS:
        for name, payload in asset_entries(storm, spec_entry).items():
            assets.setdefault(name, payload)
    model_report = {}
    for spec_entry in RACE_SPECS:
        models, detail = model_entries(spec_entry)
        assets.update(models)
        model_report.update(detail)
    assets.update(dependencies)

    portrait_report = {}
    for spec_entry in RACE_SPECS:
        entries, detail = build_portraits(client, spec_entry)
        assets.update(entries)
        portrait_report[spec_entry["slug"]] = detail

    original_glue = {}
    for name in GLUE_PATCHERS:
        original_glue[name] = _effective(client / "Data", f"{GLUE_ROOT}{name}")
    glue = build_glue(original_glue)

    dbc_entries = {f"{DBC_ROOT}{name}.dbc": data for name, data in tables.items()}
    glue_entries = {f"{GLUE_ROOT}{name}": data for name, data in glue.items()}

    # Patch-T: new, non-shadowing archive for every new asset and the repaired models.
    patch_t = stage_root / "client" / ASSET_ARCHIVE_REL
    storm.create_archive(patch_t, assets)

    # Root Z: rebuild (it sits within 20 MiB of the 2 GiB ceiling) then merge the DBCs.
    def stage_archive(relative: Path, replacements: dict[str, bytes]) -> dict:
        live = client / relative
        target = stage_root / "client" / relative
        # The live Z sits just under the 2 GiB classic ceiling and MPQ cannot overwrite a
        # block in place: appending a replacement doubles the archive. Rebuild the staged
        # copy in one streaming pass with fresh compression and the replacements merged in.
        before = live.stat().st_size
        merge = rebuild_archive_replacing(storm, live, target, replacements, compress=True)
        after = target.stat().st_size
        if after >= 0x80000000:
            raise ValueError(f"{relative} exceeds the 2 GiB classic MPQ ceiling at {after} bytes")
        return {"original_bytes": before, "staged_bytes": after, "rebuilt": True, **merge}

    root_merge = stage_archive(GLOBAL_ARCHIVE_REL, dbc_entries)
    locale_merge = stage_archive(LOCALE_ARCHIVE_REL, {**dbc_entries, **glue_entries})

    for name in ("ChrRaces", "CharStartOutfit", "CharSections", "BarberShopStyle",
                 "CreatureDisplayInfo", "CreatureModelData"):
        (stage_root / "server" / "dbc" / f"{name}.dbc").write_bytes(tables[name])

    sql = ["-- Ogre (Horde, race 60) and Furbolg (Alliance, race 61) startup, stats, "
           "language, totems and chrraces overlay.",
           "-- Generated by tools/ogre_furbolg_race_pack.py; one revision per race pair.", ""]
    for spec_entry in RACE_SPECS:
        sql.append(build_sql(spec_entry))
    for spec_entry in RACE_SPECS:
        sql.append(build_chrraces_sql(spec_entry))
    (stage_root / "sql" / "ogre_furbolg_race_start.sql").write_text("\n".join(sql), encoding="utf-8", newline="\n")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "client": str(client),
        "client_source_hashes": {
            str(GLOBAL_ARCHIVE_REL): sha256(client / GLOBAL_ARCHIVE_REL),
            str(LOCALE_ARCHIVE_REL): sha256(client / LOCALE_ARCHIVE_REL),
        },
        "staged_hashes": {
            str(ASSET_ARCHIVE_REL): sha256(patch_t),
            str(GLOBAL_ARCHIVE_REL): sha256(stage_root / "client" / GLOBAL_ARCHIVE_REL),
            str(LOCALE_ARCHIVE_REL): sha256(stage_root / "client" / LOCALE_ARCHIVE_REL),
        },
        "staged_sizes": {
            str(ASSET_ARCHIVE_REL): patch_t.stat().st_size,
            str(GLOBAL_ARCHIVE_REL): (stage_root / "client" / GLOBAL_ARCHIVE_REL).stat().st_size,
            str(LOCALE_ARCHIVE_REL): (stage_root / "client" / LOCALE_ARCHIVE_REL).stat().st_size,
        },
        "archive_merge": {"root": root_merge, "locale": locale_merge},
        "table_evidence": table_evidence,
        "race_counts": {spec_entry["slug"]: counts_for_race(tables, spec_entry["race_id"])
                        for spec_entry in RACE_SPECS},
        "dependencies": dep_report,
        "models": model_report,
        "portraits": portrait_report,
        "asset_count": len(assets),
        "glue": {name: digest(data) for name, data in glue.items()},
    }
    (stage_root / "stage-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def plan(client: Path) -> dict:
    allocation = load_allocation()
    tables, evidence = build_tables(client / "Data", allocation)
    counts = {spec_entry["slug"]: counts_for_race(tables, spec_entry["race_id"]) for spec_entry in RACE_SPECS}
    for slug, expected in (("ogre", 294), ("furbolg", 58)):
        actual = counts[slug]["CharSections"]
        if actual != expected:
            raise ValueError(f"{slug} CharSections normalized count is {actual}, expected {expected}")
    return {
        "client": str(client),
        "race_ids": {spec_entry["slug"]: spec_entry["race_id"] for spec_entry in RACE_SPECS},
        "tables": evidence["counts"],
        "race_counts": counts,
        "appearance_mapping": {spec_entry["slug"]: evidence["tables"][spec_entry["slug"]]["appearance_mapping"]
                               for spec_entry in RACE_SPECS},
    }


def validate(client: Path) -> dict:
    stage_root = STAGE_DEFAULT
    report = json.loads((stage_root / "stage-report.json").read_text(encoding="utf-8"))
    storm = Storm(p.DLL_DEFAULT)
    patch_t = stage_root / "client" / ASSET_ARCHIVE_REL
    handle = storm.open_archive(patch_t)
    try:
        names = {name.casefold() for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)
    missing = [name for name in report["dependencies"] if name.casefold() not in names]
    if missing:
        raise ValueError(f"Patch-T is missing pinned dependencies: {missing}")
    flags = repair_furbolg_sequences(_read_archive_entry(storm, patch_t, FURBOLG_ANIM_STEM))[1]
    if {k: v["after"] for k, v in flags.items()} != FURBOLG_EMBEDDED_SEQUENCES:
        raise ValueError("staged furbolg sequence flags are wrong")
    skin = _read_archive_entry(storm, patch_t, "Character\\Ogre\\Female\\ogrefemale00.skin")
    if struct.unpack_from("<I", skin, 0x2C)[0] != 66:
        raise ValueError("staged ogre female skin bone_count_max is not 66")
    for archive_rel in (GLOBAL_ARCHIVE_REL, LOCALE_ARCHIVE_REL):
        archive = stage_root / "client" / archive_rel
        for name in ("ChrRaces", "CharSections", "CharHairGeosets", "CharacterFacialHairStyles",
                     "CreatureModelData", "CreatureDisplayInfo"):
            table = p.RawWdbc(_read_archive_entry(storm, archive, f"{DBC_ROOT}{name}.dbc"))
            if name == "ChrRaces":
                ids = {p._value(row, 0) for row in table.records}
                if not {60, 61} <= ids:
                    raise ValueError(f"staged {archive_rel} ChrRaces is missing 60/61")
        for name in GLUE_PATCHERS:
            _read_archive_entry(storm, archive if archive_rel == LOCALE_ARCHIVE_REL else archive,
                                f"{GLUE_ROOT}{name}")
    return {"ok": True, "patch_t_entries": len(names), "report": str(stage_root / "stage-report.json")}


def update_allocation(allocation: dict) -> dict:
    """Reserve the new table ranges and per-race allocations (idempotent)."""
    ranges = allocation["dbc_ranges"]
    ranges["CreatureDisplayInfo"] = [60030, max(60056, ranges["CreatureDisplayInfo"][1])]
    ranges["CharSections"] = [450000, max(1100999, ranges["CharSections"][1])]
    ranges["CharHairGeosets"] = [450000, max(1100999, ranges["CharHairGeosets"][1])]
    ranges["CharHairTextures"] = [450000, max(1100999, ranges["CharHairTextures"][1])]
    ranges["BarberShopStyle"] = [450000, max(1100999, ranges["BarberShopStyle"][1])]
    ranges["CharStartOutfit"] = [21000, max(22039, ranges["CharStartOutfit"][1])]
    ranges["NameGen"] = [22000, max(65999, ranges["NameGen"][1])]
    allocation["race_ids"]["ogre"] = [60]
    allocation["race_ids"]["furbolg"] = [61]
    allocation["race_allocations"]["ogre"] = {
        "CreatureModelData": {"male": 120062, "female": 120063},
        "CreatureDisplayInfo": {"male": 60053, "female": 60054},
        "CharSections": [1100000, 1100699],
        "CharHairGeosets": [1100000, 1100699],
        "CharHairTextures": [1100000, 1100699],
        "BarberShopStyle": [1100000, 1100699],
        "CharStartOutfit": [22000, 22019],
        "NameGen": [60000, 62999],
    }
    allocation["race_allocations"]["furbolg"] = {
        "CreatureModelData": {"male": 120064, "female": 120065},
        "CreatureDisplayInfo": {"male": 60055, "female": 60056},
        "CharSections": [1100700, 1100999],
        "CharHairGeosets": [1100700, 1100999],
        "CharHairTextures": [1100700, 1100999],
        "BarberShopStyle": [1100700, 1100999],
        "CharStartOutfit": [22020, 22039],
        "NameGen": [63000, 65999],
    }
    return allocation


def update_registry() -> dict:
    path = ROOT / "modules/mod-custom-server/data/races/race_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    playable = registry["playable"]
    existing = {entry["id"] for entry in playable}
    additions = [
        {"id": 60, "species_key": "ogre", "display_name": "Ogre", "faction": "horde",
         "asset_owner": "retroporter_ogre_furbolg", "legacy_mask_race": 2, "visual_base_race": 2,
         "start_profile": "durotar", "supported_genders": [0, 1], "species_selection": False},
        {"id": 61, "species_key": "furbolg", "display_name": "Furbolg", "faction": "alliance",
         "asset_owner": "retroporter_ogre_furbolg", "legacy_mask_race": 4, "visual_base_race": 4,
         "start_profile": "teldrassil", "supported_genders": [0, 1], "species_selection": False},
    ]
    for entry in additions:
        if entry["id"] not in existing:
            playable.append(entry)
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8", newline="\n")
    return registry


def write_manifest(spec_entry: dict) -> dict:
    slug = spec_entry["slug"]
    models = MODELS[slug]
    equipment = {
        "ogre": {"geosets": "player glove/sleeve/boot/robe groups present",
                 "attachments": "male inventory narrower than female; verify weapons separately",
                 "helmet": "no fitted _OgM/_OgF helmet library in the selected payload"},
        "furbolg": {"geosets": "three batches, all geoset 0 (texture types 1, 6, 8)",
                    "attachments": "no helmet point 11 and no left shoulder point 27",
                    "helmet": "no fitted _FuM/_FuF helmet library in the selected payload",
                    "body": "shared male/female body, no separate female mesh"},
    }[slug]
    manifest = {
        "schema_version": 1,
        "slug": slug,
        "race_id": spec_entry["race_id"],
        "enum": spec_entry["enum"],
        "faction": spec_entry["faction"],
        "client_file_string": spec_entry["client_file_string"],
        "glue_token": "OGREHORDE" if slug == "ogre" else "FURBOLG",
        "helmet_prefix": spec_entry["prefix"],
        "name": spec_entry["name"],
        "legacy_mask_race": spec_entry["legacy_mask_race"],
        "visual_base_race": spec_entry["visual_base_race"],
        "donor_race_id": spec_entry["donor_race_id"],
        "donor_source": "Harvested/Playable_Races_Isolated_2026-10-04/ReadyToPort (patch-ZZ preferred, patch-Z fallback)",
        "donor_race_identity": {
            "18": "Esteria Pandaren", "23": "Dark Iron Dwarf", "25": "Forsaken",
            "note": "donor IDs are unusable directly; this pack remaps 25->60 and 18->61",
        },
        "start_profile": spec_entry["start_profile"],
        "donor_start_race": spec_entry["donor_start_race"],
        "donor_totem_race": spec_entry["donor_totem_race"],
        "base_language": spec_entry["base_language"],
        "alliance_flag": spec_entry["alliance_flag"],
        "creature_type": 7,
        "expansion": 0,
        "cinematic": 0,
        "models": {gender: dict(model) for gender, model in models.items()},
        "appearance_mapping": APPEARANCE[slug],
        "hair_geosets": {str(gender): rows for gender, rows in HAIR_GEOSETS[slug].items()},
        "facial_geoset_donors": {str(g): {str(k): list(v) for k, v in rows.items()}
                                 for g, rows in FACIAL_GEOSET_DONORS.get(slug, {}).items()},
        "class_compatibility": spec_entry["class_compat"],
        "portraits": {gender: str(path) for gender, path in spec_entry["portraits"].items()},
        "equipment_limits": equipment,
        "dependencies": sorted(PINNED_DEPENDENCIES),
        "table_allocations": {
            "CharSections": [1100000, 1100699] if slug == "ogre" else [1100700, 1100999],
            "CharHairGeosets": [1100000, 1100699] if slug == "ogre" else [1100700, 1100999],
            "BarberShopStyle": [1100000, 1100699] if slug == "ogre" else [1100700, 1100999],
            "CharStartOutfit": [22000, 22019] if slug == "ogre" else [22020, 22039],
            "NameGen": [60000, 62999] if slug == "ogre" else [63000, 65999],
        },
    }
    path = CONFIG_ROOT / f"{slug}.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def apply_config() -> None:
    allocation = update_allocation(load_allocation())
    ALLOCATION_PATH.write_text(json.dumps(allocation, indent=2) + "\n", encoding="utf-8", newline="\n")
    update_registry()
    for spec_entry in RACE_SPECS:
        write_manifest(spec_entry)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "stage", "validate", "configure"))
    parser.add_argument("--client", type=Path, default=CLIENT_DEFAULT)
    args = parser.parse_args()
    if args.command == "plan":
        result = plan(args.client)
    elif args.command == "configure":
        apply_config()
        result = {"ok": True, "allocation": str(ALLOCATION_PATH)}
    elif args.command == "stage":
        result = stage(args.client)
    else:
        result = validate(args.client)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())