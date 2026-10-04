"""Build, validate, and install Esteria retroported-race client/server packs.

Phase 1 intentionally starts with Mag'har Orc but keeps the build machinery manifest-driven.
The live Esteria Z archives are always treated as the merge base. Install is transactional:
back up and hash-verify both live Z archives, validate staged output, then replace them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PureWindowsPath

from PIL import Image
from wotlkconv.blp import Blp
from wotlkconv.blp.blp import BLP_COMPRESSION_PALETTE
from wotlkconv.blp.image import Image as BlpImage
from wotlkconv.blp.quantize import PaletteMapper, build_palette

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "modules" / "mod-classless-wildcard" / "client-patch"))

from cars_mount_pack import (  # noqa: E402
    DBC_STRING_FIELDS,
    DLL_DEFAULT,
    Storm,
    Wdbc,
    build_wdbc,
    merge_wdbc_continuations,
)
from derive_playable_race_portraits import encode_portrait, validate_portrait  # noqa: E402
from lib.clientfs import ClientFiles  # noqa: E402
from playable_race_pack import RawWdbc, STRING_FIELDS, WDBC_LAYOUTS  # noqa: E402
from wod_model_migration import rebuild_archive_streaming  # noqa: E402

CLIENT_DEFAULT = Path(r"G:\3.3.5a - Dev")
CONFIG_ROOT = ROOT / "data" / "retroported-races"
ALLOCATION_PATH = CONFIG_ROOT / "allocation.json"
SERVER_DBC_ROOT = ROOT / "modules" / "mod-custom-server" / "data" / "dbc" / "retroported-races"
SERVER_CONTINUATION_ROOT = ROOT / "modules" / "mod-custom-server" / "data" / "dbc-continuations"
MAGHAR_SPELL_SQL = ROOT / "modules" / "mod-custom-server" / "data" / "sql" / "db-world" / "updates" / "dbc" / "spell_dbc.sql"
RUNTIME_EXTENSION_REL = Path("Extensions") / "z-darkfallen-character-select"
RUNTIME_EXTENSION_DLL = RUNTIME_EXTENSION_REL / "z-darkfallen-character-select.dll"
RUNTIME_EXTENSION_MANIFEST = RUNTIME_EXTENSION_REL / "wxl.json"
RUNTIME_BUILD_DEFAULT = ROOT / "wxl-races-patcher" / "darkfallen-character-select.next.dll"

GLOBAL_ARCHIVE_REL = Path("Data") / "patch-Z.MPQ"
ASSET_ARCHIVE_REL = Path("Data") / "Patch-R.MPQ"
LOCALE_ARCHIVE_REL = Path("Data") / "enUS" / "patch-enUS-Z.MPQ"
DBC_ROOT = "DBFilesClient\\"
GLUE_ROOT = "Interface\\GlueXML\\"
CHARACTER_FRAME_ROOT = "Interface\\CharacterFrame\\"

SERVER_DBC_TABLES = (
    "ChrRaces",
    "CharStartOutfit",
    "CharSections",
    "BarberShopStyle",
    "CreatureDisplayInfo",
    "CreatureModelData",
    "Spell",
)

SPELL_STRING_FIELDS = (
    tuple(range(136, 152))
    + tuple(range(153, 169))
    + tuple(range(170, 186))
    + tuple(range(187, 203))
)
SPELL_FLOAT_FIELDS = frozenset(
    (47,)
    + tuple(range(77, 80))
    + tuple(range(101, 104))
    + tuple(range(119, 122))
    + tuple(range(226, 229))
)


@dataclass(frozen=True)
class BuildPaths:
    root: Path
    global_archive: Path
    asset_archive: Path
    locale_archive: Path
    server_dbc_dir: Path
    report: Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_path(slug: str) -> Path:
    return CONFIG_ROOT / f"{slug}.json"


def load_manifest(slug: str) -> dict:
    path = manifest_path(slug)
    if not path.is_file():
        raise FileNotFoundError(f"race manifest does not exist: {path}")
    return load_json(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _value(record: bytes, offset: int, width: int = 4) -> int:
    return int.from_bytes(record[offset : offset + width], "little")


def _replace(record: bytes, offset: int, width: int, value: int) -> bytes:
    if value < 0 or value >= (1 << (width * 8)):
        raise ValueError(f"value {value} does not fit in {width} bytes")
    output = bytearray(record)
    output[offset : offset + width] = value.to_bytes(width, "little")
    return bytes(output)


def _string(pool: bytes, offset: int) -> bytes:
    if not offset:
        return b""
    end = pool.find(b"\0", offset)
    if end < 0:
        raise ValueError("unterminated WDBC string")
    return pool[offset:end]


def _append_string(pool: bytearray, value: str | bytes) -> int:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    offset = len(pool)
    pool.extend(raw)
    pool.append(0)
    return offset


def _set_string(record: bytes, field: int, pool: bytearray, value: str) -> bytes:
    return _replace(record, field * 4, 4, _append_string(pool, value))


def _clone_strings(table_name: str, source: RawWdbc, record: bytes, pool: bytearray) -> bytes:
    output = record
    for field in STRING_FIELDS.get(table_name, ()):
        offset = _value(record, field * 4)
        if offset:
            output = _replace(output, field * 4, 4, _append_string(pool, _string(source.strings, offset)))
    return output


def _full_table(client_data: Path, name: str) -> tuple[bytes, str]:
    files = ClientFiles(str(client_data), "enUS")
    try:
        return files.find(f"DBFilesClient\\{name}.dbc")
    finally:
        files.close()


def _effective_file(client_data: Path, entry: str) -> tuple[bytes, str]:
    files = ClientFiles(str(client_data), "enUS")
    try:
        return files.find(entry)
    finally:
        files.close()


def _ensure_id_free(data: bytes, table_name: str, ids: set[int]) -> None:
    table = RawWdbc(data)
    existing = {int.from_bytes(row[:4], "little") for row in table.records}
    collisions = sorted(existing & ids)
    if collisions:
        raise ValueError(f"{table_name} ID collision(s): {collisions[:20]}")


def _allocated_sequence(allocation: dict, slug: str, table: str, count: int) -> list[int]:
    bounds = allocation["race_allocations"][slug][table]
    if isinstance(bounds, dict):
        raise ValueError(f"{table} uses named allocation, not a sequence")
    start, end = bounds
    if start + count - 1 > end:
        raise ValueError(f"{table} allocation {start}-{end} cannot hold {count} rows")
    return list(range(start, start + count))


def _merge_model_table(
    table_name: str,
    data: bytes,
    manifest: dict,
    allocation: dict,
) -> bytes:
    source = RawWdbc(data)
    pool = bytearray(source.strings)
    obsolete_ids = set(manifest.get("obsolete_dbc_ids", {}).get(table_name, ()))
    records = [row for row in source.records if int.from_bytes(row[:4], "little") not in obsolete_ids]
    by_id = {int.from_bytes(row[:4], "little"): index for index, row in enumerate(records)}
    named = allocation["race_allocations"][manifest["slug"]][table_name]

    for gender in ("male", "female"):
        model = manifest["models"][gender]
        source_id = model["source_model_id"] if table_name == "CreatureModelData" else model["source_display_id"]
        target_id = named[gender]
        donor = next((row for row in source.records if int.from_bytes(row[:4], "little") == source_id), None)
        if donor is None:
            raise ValueError(f"{table_name} donor row {source_id} is missing")
        existing_index = by_id.get(target_id)
        runtime_model_path = model.get("runtime_model_path", model["model_path"])
        if existing_index is not None:
            existing = records[existing_index]
            if table_name == "CreatureModelData":
                existing_path = _string(source.strings, _value(existing, 2 * 4)).decode("utf-8")
                allowed_paths = {
                    runtime_model_path.casefold(),
                    model["model_path"].casefold(),
                    *(path.casefold() for path in model.get("previous_runtime_model_paths", ())),
                }
                if existing_path.casefold() not in allowed_paths:
                    raise ValueError(f"{table_name} target ID {target_id} is owned by {existing_path}")
            else:
                expected_model_id = allocation["race_allocations"][manifest["slug"]]["CreatureModelData"][gender]
                if _value(existing, 1 * 4) != expected_model_id:
                    raise ValueError(f"{table_name} target ID {target_id} is owned by another model")

        row = _clone_strings(table_name, source, donor, pool)
        row = _replace(row, 0, 4, target_id)
        if table_name == "CreatureModelData":
            row = _set_string(row, 2, pool, runtime_model_path)
        else:
            model_id = allocation["race_allocations"][manifest["slug"]]["CreatureModelData"][gender]
            row = _replace(row, 4, 4, model_id)
        if existing_index is None:
            records.append(row)
            by_id[target_id] = len(records) - 1
        else:
            records[existing_index] = row

    return source.build(records, bytes(pool))


def _merge_chr_races(data: bytes, manifest: dict, allocation: dict) -> bytes:
    source = RawWdbc(data)
    layout = WDBC_LAYOUTS["ChrRaces"]
    pool = bytearray(source.strings)
    records = list(source.records)
    existing = {int.from_bytes(row[:4], "little"): index for index, row in enumerate(records)}
    source_race = manifest["source_race_id"]
    donor = next((row for row in records if int.from_bytes(row[:4], "little") == source_race), None)
    if donor is None:
        raise ValueError(f"ChrRaces source race {source_race} is missing")

    for race_id in manifest["race_ids"]:
        existing_index = existing.get(race_id)
        if existing_index is not None:
            existing_row = records[existing_index]
            existing_file_string = _string(source.strings, _value(existing_row, 11 * 4)).decode("utf-8")
            expected_file_string = manifest["client_file_strings"][str(race_id)]
            if existing_file_string.casefold() != expected_file_string.casefold():
                raise ValueError(f"ChrRaces target race {race_id} is owned by {existing_file_string}")

        row = _clone_strings("ChrRaces", source, donor, pool)
        row = _replace(row, layout.race_offset, layout.race_width, race_id)
        row = _replace(row, 4 * 4, 4, allocation["race_allocations"][manifest["slug"]]["CreatureDisplayInfo"]["male"])
        row = _replace(row, 5 * 4, 4, allocation["race_allocations"][manifest["slug"]]["CreatureDisplayInfo"]["female"])
        row = _set_string(row, 6, pool, "Mh" if manifest["slug"] == "maghar" else manifest["slug"][:2].title())
        row = _set_string(row, 11, pool, manifest["client_file_strings"][str(race_id)])
        for field in (*range(14, 30), *range(31, 47), *range(48, 64)):
            row = _set_string(row, field, pool, manifest["name"])
        if existing_index is None:
            records.append(row)
            existing[race_id] = len(records) - 1
        else:
            records[existing_index] = row

    return source.build(records, bytes(pool))


def _append_u32_record(table: RawWdbc, values: list[int], pool: bytearray, strings: dict[int, str]) -> bytes:
    if len(values) != table.fields:
        raise ValueError(f"record has {len(values)} fields, expected {table.fields}")
    for field, value in list(strings.items()):
        values[field] = _append_string(pool, value)
    return struct.pack(f"<{table.fields}I", *(value & 0xFFFFFFFF for value in values))


def _maghar_char_sections(data: bytes, manifest: dict, allocation: dict) -> bytes:
    """Build RaceID 45 on the native HD Orc2/Wrath compositor layout.

    Orc rows are used only as structural donors for field/flag semantics. Every visible
    Race45 body, base-head, face, hair-color, and underwear texture remains Mag'har art.
    Skin and Face stay independent legacy selectors instead of being encoded together.
    """
    table = RawWdbc(data)
    if table.fields != 10 or table.record_size != 40:
        raise ValueError("unexpected CharSections layout")

    spec = manifest["appearance"]
    target_race = manifest["race_ids"][0]
    donor_race = manifest["source_race_id"]
    skin_sources = spec["skin_source_indices"]
    face_indices = spec["face_indices"]
    hair_colors = spec["hair_color_indices"]
    face_count = len(face_indices)
    combined_count = len(skin_sources) * face_count

    donor_rows: dict[tuple[int, int, int, int], bytes] = {}
    for row in table.records:
        if _value(row, 1 * 4) != donor_race:
            continue
        key = (_value(row, 2 * 4), _value(row, 3 * 4), _value(row, 8 * 4), _value(row, 9 * 4))
        donor_rows[key] = row

    def donor(gender: int, section: int, style: int, color: int) -> bytes:
        key = (gender, section, style, color)
        row = donor_rows.get(key)
        if row is None:
            raise ValueError(
                f"HD Orc CharSections donor is missing gender={gender} section={section} "
                f"style={style} color={color}"
            )
        return row

    count = 0
    for gender in (0, 1):
        hair_styles = spec["male_hair_styles"] if gender == 0 else spec["female_hair_styles"]
        count += len(skin_sources)  # one body + base-head pair per skin
        count += combined_count  # every face style for every skin color
        count += hair_styles * len(hair_colors)
        count += len(skin_sources)  # underwear follows skin only
        if gender == 0:
            count += spec["male_facial_styles"] * len(hair_colors)

    ids = _allocated_sequence(allocation, manifest["slug"], "CharSections", count)
    allocated_ids = set(ids)
    allocation_start, allocation_end = allocation["race_allocations"][manifest["slug"]]["CharSections"]
    pool = bytearray(table.strings)
    records: list[bytes] = []
    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        row_race = _value(record, 1 * 4)
        if allocation_start <= row_id <= allocation_end and row_race == target_race:
            continue
        if row_id in allocated_ids and row_race != target_race:
            raise ValueError(f"CharSections target ID {row_id} is owned by another race")
        records.append(record)
    id_iter = iter(ids)

    def append_from_donor(
        donor_row: bytes,
        color_index: int,
        style_index: int | None = None,
        texture_overrides: dict[int, str] | None = None,
        flags: int = 0x11,
    ) -> None:
        row = _clone_strings("CharSections", table, donor_row, pool)
        row = _replace(row, 0, 4, next(id_iter))
        row = _replace(row, 1 * 4, 4, target_race)
        # Wrath uses section-specific applicability flags. Normal face rows
        # use 0x1, while the generated skin/hair/underwear rows use 0x11.
        row = _replace(row, 7 * 4, 4, flags)
        if style_index is not None:
            row = _replace(row, 8 * 4, 4, style_index)
        row = _replace(row, 9 * 4, 4, color_index)
        for field, texture in (texture_overrides or {}).items():
            row = _set_string(row, field, pool, texture)
        records.append(row)

    for gender, sex in ((0, "male"), (1, "female")):
        stem = "orcmale" if gender == 0 else "orcfemale"
        hair_styles = spec["male_hair_styles"] if gender == 0 else spec["female_hair_styles"]
        # Match the native Orc2/Wrath layout exactly: Skin Color and Face are
        # independent selectors. Section 0 has one body/base-head pair per skin;
        # section 1 has every face style for every skin color. Do not encode the
        # Cartesian product into the character's Skin byte.
        for skin_index, _source_skin in enumerate(skin_sources):
            append_from_donor(
                donor(gender, 0, 0, 0),
                skin_index,
                texture_overrides={
                    4: _derived_body_path(sex, stem, skin_index),
                    5: _derived_base_head_path(sex, stem, skin_index),
                },
            )

        for face_index, _source_face in enumerate(face_indices):
            for skin_index, _source_skin in enumerate(skin_sources):
                append_from_donor(
                    donor(gender, 1, 0, 0),
                    skin_index,
                    style_index=face_index,
                    flags=0x1,
                    texture_overrides={
                        4: _derived_face_fragment_path(sex, stem, face_index, skin_index, "lower"),
                        5: _derived_face_fragment_path(sex, stem, face_index, skin_index, "upper"),
                        6: "",
                    },
                )

        if gender == 0:
            for feature_style in range(spec["male_facial_styles"]):
                for color_index in hair_colors:
                    # This is an alpha beard overlay painted onto FaceLower. A
                    # full DXT hair atlas has no palette and triggers neon-green
                    # error fill in the native compositor; retain the donor mask.
                    append_from_donor(
                        donor(gender, 2, feature_style, color_index),
                        color_index,
                    )

        for hair_style in range(hair_styles):
            for color_index in hair_colors:
                append_from_donor(
                    donor(gender, 3, hair_style, color_index),
                    color_index,
                    texture_overrides={
                        4: f"custom\\maghar\\character\\orc\\orcclanhair00_{color_index:02d}.blp"
                    },
                )

        for skin_index, source_skin in enumerate(skin_sources):
            append_from_donor(
                donor(gender, 4, 0, 0),
                skin_index,
                texture_overrides={
                    4: (
                        f"custom\\maghar\\character\\orc\\{sex}\\"
                        f"{stem}clannakedpelvisskin00_{source_skin:02d}.blp"
                    ),
                    5: (
                        f"custom\\maghar\\character\\orc\\{sex}\\"
                        f"{stem}clannakedtorsoskin00_{source_skin:02d}.blp"
                    ),
                },
            )

    return table.build(records, bytes(pool))


def _clone_race_rows(
    table_name: str,
    data: bytes,
    manifest: dict,
    allocation: dict,
    source_race: int | None = None,
) -> bytes:
    table = RawWdbc(data)
    layout = WDBC_LAYOUTS[table_name]
    source_race = manifest["source_race_id"] if source_race is None else source_race
    source_rows = [
        row for row in table.records
        if _value(row, layout.race_offset, layout.race_width) == source_race
    ]
    if not source_rows:
        raise ValueError(f"{table_name} has no rows for source race {source_race}")
    pool = bytearray(table.strings)
    records = list(table.records)
    keyed = table_name not in {"CharacterFacialHairStyles", "CharBaseInfo"}
    target_race = manifest["race_ids"][0]
    new_ids: list[int] = []
    if keyed:
        new_ids = _allocated_sequence(allocation, manifest["slug"], table_name, len(source_rows))
        allocated_ids = set(new_ids)
        kept_records: list[bytes] = []
        for record in records:
            row_id = int.from_bytes(record[:4], "little")
            if row_id in allocated_ids:
                if _value(record, layout.race_offset, layout.race_width) != target_race:
                    raise ValueError(f"{table_name} target ID {row_id} is owned by another race")
                continue
            kept_records.append(record)
        records = kept_records
    else:
        records = [
            record for record in records
            if _value(record, layout.race_offset, layout.race_width) != target_race
        ]

    for index, donor in enumerate(source_rows):
        row = _clone_strings(table_name, table, donor, pool)
        row = _replace(row, layout.race_offset, layout.race_width, manifest["race_ids"][0])
        if keyed:
            row = _replace(row, 0, 4, new_ids[index])
        records.append(row)
    return table.build(records, bytes(pool))


def _build_char_base_info(data: bytes, manifest: dict) -> bytes:
    table = RawWdbc(data)
    if table.record_size != 2:
        raise ValueError("unexpected CharBaseInfo record size")
    records = list(table.records)
    existing = set(records)
    for race_id in manifest["race_ids"]:
        for class_id in manifest["classes"]:
            row = bytes((race_id, class_id))
            if row not in existing:
                records.append(row)
                existing.add(row)
    return table.build(records)


def _build_char_start_outfit(data: bytes, manifest: dict, allocation: dict) -> bytes:
    table = RawWdbc(data)
    layout = WDBC_LAYOUTS["CharStartOutfit"]
    donor_rows = [
        row for row in table.records
        if _value(row, layout.race_offset, layout.race_width) == manifest["source_race_id"]
    ]
    donor_rows = [row for row in donor_rows if row[5] in manifest["classes"]]
    if not donor_rows:
        return data
    ids = _allocated_sequence(allocation, manifest["slug"], "CharStartOutfit", len(donor_rows))
    allocated_ids = set(ids)
    target_race = manifest["race_ids"][0]
    records: list[bytes] = []
    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id in allocated_ids:
            if _value(record, layout.race_offset, layout.race_width) != target_race:
                raise ValueError(f"CharStartOutfit target ID {row_id} is owned by another race")
            continue
        records.append(record)
    for row_id, donor in zip(ids, donor_rows):
        row = _replace(donor, 0, 4, row_id)
        row = _replace(row, layout.race_offset, layout.race_width, manifest["race_ids"][0])
        records.append(row)
    return table.build(records)


def _clone_namegen(data: bytes, manifest: dict, allocation: dict) -> bytes:
    table = RawWdbc(data)
    layout = WDBC_LAYOUTS["NameGen"]
    donors = [row for row in table.records if _value(row, layout.race_offset, layout.race_width) == manifest["source_race_id"]]
    ids = _allocated_sequence(allocation, manifest["slug"], "NameGen", len(donors))
    allocated_ids = set(ids)
    target_race = manifest["race_ids"][0]
    pool = bytearray(table.strings)
    records: list[bytes] = []
    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id in allocated_ids:
            if _value(record, layout.race_offset, layout.race_width) != target_race:
                raise ValueError(f"NameGen target ID {row_id} is owned by another race")
            continue
        records.append(record)
    for row_id, donor in zip(ids, donors):
        row = _clone_strings("NameGen", table, donor, pool)
        row = _replace(row, 0, 4, row_id)
        row = _replace(row, layout.race_offset, layout.race_width, manifest["race_ids"][0])
        records.append(row)
    return table.build(records, bytes(pool))


def _sql_scalar(text: str, field_index: int) -> int | str:
    text = text.strip().rstrip(",")
    if text.startswith("'") and text.endswith("'"):
        value = text[1:-1]
        value = value.replace("\\'", "'").replace("\\\\", "\\")
        return value
    if field_index in SPELL_FLOAT_FIELDS:
        return struct.unpack("<I", struct.pack("<f", float(text)))[0]
    return int(float(text)) & 0xFFFFFFFF


def _load_maghar_spell_continuation(manifest: dict) -> bytes:
    lines = MAGHAR_SPELL_SQL.read_text(encoding="utf-8").splitlines()
    donor_ids = set(manifest["racial_spell_donor_ids"])
    target_map = dict(zip(manifest["racial_spell_donor_ids"], manifest["racial_spells"]))
    rows: list[list[int]] = []
    strings: dict[tuple[int, int], str] = {}
    collecting = False
    values: list[str] = []

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "(":
            collecting = True
            values = []
            continue
        if not collecting:
            continue
        if stripped in (")", "),", ");"):
            if values:
                first = _sql_scalar(values[0], 0)
                if isinstance(first, int) and first in donor_ids:
                    converted: list[int] = []
                    pending_strings: dict[int, str] = {}
                    for field_index, raw in enumerate(values):
                        value = _sql_scalar(raw, field_index)
                        if isinstance(value, str):
                            pending_strings[field_index] = value
                            converted.append(0)
                        else:
                            converted.append(value)
                    if len(converted) != 234:
                        raise ValueError(f"Mag'har spell {first} has {len(converted)} fields, expected 234")
                    converted[0] = target_map[first]
                    row_index = len(rows)
                    for field, value in pending_strings.items():
                        strings[(row_index, field)] = value
                    rows.append(converted)
            collecting = False
            continue
        if "--" in stripped:
            stripped = stripped.split("--", 1)[0].rstrip()
        if stripped:
            values.append(stripped.rstrip(","))

    if len(rows) != len(donor_ids):
        raise ValueError(f"found {len(rows)} Mag'har racial spell rows, expected {len(donor_ids)}")
    return build_wdbc(rows, 234, 936, strings)


def _drop_wdbc_ids(data: bytes, table_name: str, ids: set[int]) -> bytes:
    table = Wdbc(data)
    rows = [row for row in table.rows if row[0] not in ids]
    strings: dict[tuple[int, int], str] = {}
    for row_index, row in enumerate(rows):
        for field in DBC_STRING_FIELDS.get(table_name, ()):
            if row[field]:
                value = table.text(row[field])
                if value:
                    strings[(row_index, field)] = value
    return build_wdbc(rows, table.fields, table.record_size, strings)


def _merge_spells(data: bytes, manifest: dict) -> tuple[bytes, bytes]:
    continuation = _load_maghar_spell_continuation(manifest)
    target_ids = set(manifest["racial_spells"])
    expected = Wdbc(continuation)
    expected_names = {row[0]: expected.text(row[136]) for row in expected.rows}
    current = Wdbc(data)
    for row in current.rows:
        if row[0] not in target_ids:
            continue
        current_name = current.text(row[136])
        if current_name != expected_names[row[0]]:
            raise ValueError(f"Spell.dbc target ID {row[0]} is owned by {current_name}")

    base = _drop_wdbc_ids(data, "Spell", target_ids)
    return merge_wdbc_continuations(base, continuation, "Spell"), continuation


def _table_rows_for_race(data: bytes, table_name: str, race_id: int) -> list[bytes]:
    table = RawWdbc(data)
    layout = WDBC_LAYOUTS[table_name]
    return [row for row in table.records if _value(row, layout.race_offset, layout.race_width) == race_id]


def _continuation_from_records(full_data: bytes, table_name: str, records: list[bytes]) -> bytes:
    table = RawWdbc(full_data)
    pool = bytearray(b"\0")
    output: list[bytes] = []
    for record in records:
        row = bytearray(record)
        for field in STRING_FIELDS.get(table_name, ()):
            offset = _value(record, field * 4)
            if offset:
                row[field * 4 : field * 4 + 4] = _append_string(pool, _string(table.strings, offset)).to_bytes(4, "little")
        output.append(bytes(row))
    header = struct.pack("<4s4I", b"WDBC", len(output), table.fields, table.record_size, len(pool))
    return header + b"".join(output) + bytes(pool)


def _server_continuations(tables: dict[str, bytes], manifest: dict, allocation: dict, spell_continuation: bytes) -> dict[str, bytes]:
    race_id = manifest["race_ids"][0]
    result: dict[str, bytes] = {}
    for table_name in SERVER_DBC_TABLES:
        if table_name == "Spell":
            result["Spell.dbc1-retroported-races"] = spell_continuation
            continue
        data = tables[table_name]
        if table_name in ("ChrRaces", "CharStartOutfit", "CharSections", "BarberShopStyle"):
            rows = _table_rows_for_race(data, table_name, race_id)
        elif table_name == "CreatureModelData":
            ids = set(allocation["race_allocations"][manifest["slug"]][table_name].values())
            rows = [row for row in RawWdbc(data).records if int.from_bytes(row[:4], "little") in ids]
        elif table_name == "CreatureDisplayInfo":
            ids = set(allocation["race_allocations"][manifest["slug"]][table_name].values())
            rows = [row for row in RawWdbc(data).records if int.from_bytes(row[:4], "little") in ids]
        else:
            rows = []
        if rows:
            result[f"{table_name}.dbc1-retroported-races"] = _continuation_from_records(data, table_name, rows)
    return result


def _patch_character_create_lua(data: bytes) -> bytes:
    text = data.decode("utf-8")
    text, count = re.subn(r"(?m)^MAX_RACES\s*=\s*40\s*;", "MAX_RACES = 64;", text, count=1)
    if count != 1 and "MAX_RACES = 64;" not in text:
        raise ValueError("CharacterCreate.lua MAX_RACES anchor not found")

    old = """    local selectedSex = GetSelectedSex();\n    if ( selectedSex == SEX_MALE ) then"""
    new = """    local selectedSex = GetSelectedSex();\n    local availableRaceIDs = nil;\n    if ( type(GetAvailableRaceIDs) == \"function\" ) then\n        availableRaceIDs = {GetAvailableRaceIDs()};\n    end\n    if ( selectedSex == SEX_MALE ) then"""
    if old in text and "availableRaceIDs = {GetAvailableRaceIDs()}" not in text:
        text = text.replace(old, new, 1)

    old = """        local raceID = index;\n        local _, faction = GetFactionForRace(raceID);"""
    new = """        local raceID = availableRaceIDs and availableRaceIDs[index] or index;\n        local _, faction = GetFactionForRace(index);\n        if ( _G.GetFactionForRaceID ) then\n            faction = _G.GetFactionForRaceID(raceID);\n        end"""
    if old in text:
        text = text.replace(old, new, 1)
    elif "availableRaceIDs and availableRaceIDs[index] or index" not in text:
        raise ValueError("CharacterCreate.lua race ID enumeration anchor not found")

    exact_anchor = "        local raceID = availableRaceIDs and availableRaceIDs[index] or index;"
    exact_block = """        local raceID = availableRaceIDs and availableRaceIDs[index] or index;\n        if ( _G.GetExactRaceIDForFileString ) then\n            local exactRaceID = _G.GetExactRaceIDForFileString(fileString);\n            if ( exactRaceID ) then\n                raceID = exactRaceID;\n            end\n        end"""
    if "local exactRaceID = _G.GetExactRaceIDForFileString(fileString);" not in text:
        if exact_anchor not in text:
            raise ValueError("CharacterCreate.lua exact race FileString anchor not found")
        text = text.replace(exact_anchor, exact_block, 1)

    old = """        button = _G[\"CharacterCreateRaceButton\"..index];\n        button.raceFileString = fileString;"""
    new = """        button = _G[\"CharacterCreateRaceButton\"..index];\n        button.uiSlot = index;\n        button.raceID = raceID;\n        button.raceFileString = fileString;"""
    if old in text:
        text = text.replace(old, new, 1)
    elif "button.raceID = raceID;" not in text:
        raise ValueError("CharacterCreate.lua race button metadata anchor not found")

    text = text.replace("table.insert(CharacterCreate.raceIndicesAlliance, raceID)", "table.insert(CharacterCreate.raceIndicesAlliance, index)")
    text = text.replace("table.insert(CharacterCreate.raceIndicesHorde, raceID)", "table.insert(CharacterCreate.raceIndicesHorde, index)")
    text = text.replace("        local raceID = button:GetID()\n        local faction = _G.GetFactionForRaceID(raceID)", "        local raceID = button.raceID or button:GetID()\n        local faction = _G.GetFactionForRaceID(raceID)")

    old = """    CharacterCreate_UpdateButtonCheckedStates();\n\n    local name, faction = GetFactionForRace(CharacterCreate.selectedRace);"""
    new = """    CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;\n    CharacterCreate_UpdateButtonCheckedStates();\n\n    local name, faction = GetFactionForRace(CharacterCreate.selectedRace);\n    if ( _G.GetFactionForRaceID ) then\n        faction = _G.GetFactionForRaceID(CharacterCreate.selectedRaceID);\n    end"""
    if old in text:
        text = text.replace(old, new, 1)
    elif "CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;" not in text:
        raise ValueError("CharacterCreate.lua selected RaceID anchor not found")
    return text.encode("utf-8")


def _patch_character_create_xml(data: bytes) -> bytes:
    text = data.decode("utf-8")
    if "CharacterCreateRaceButton64" in text:
        return data
    anchor = '                                <CheckButton name="CharacterCreateRaceButton40" inherits="CharacterCreateRaceButtonTemplate" id="40"/>'
    if anchor not in text:
        raise ValueError("CharacterCreate.xml race button 40 anchor not found")
    extra = "\n".join(
        f'                                <CheckButton name="CharacterCreateRaceButton{index}" inherits="CharacterCreateRaceButtonTemplate" id="{index}"/>'
        for index in range(41, 65)
    )
    return text.replace(anchor, anchor + "\n" + extra, 1).encode("utf-8")


def _patch_character_info(data: bytes) -> bytes:
    text = data.decode("utf-8")

    # Remove the first-pass mistake that treated exact RaceID 45 as a UI/enumeration slot.
    text = text.replace('    [45] = { glueString = "MAGHAR", faction = "Horde" },\n', "")
    text = text.replace(
        "local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 45}",
        "local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17, 19}",
    )
    text = re.sub(r'(?m)^\s*\[45\] = \{token = "MAGHAR"[^\n]*\n', "", text)

    if "local EXACT_RACE_DATA = {" not in text:
        anchor = "local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16, 18}"
        addition = """local EXACT_RACE_DATA = {\n    [45] = { glueString = \"MAGHAR\", name = \"Mag'har Orc\", faction = \"Horde\", fileString = \"Maghar\" },\n}\n\n"""
        if anchor not in text:
            raise ValueError("CharacterInfo.lua exact-race metadata anchor not found")
        text = text.replace(anchor, addition + anchor, 1)

    old = """local function GetRaceName(raceID)\n    local raceData = RACE_DATA[raceID]\n    if not raceData then\n        return \"Human\"\n    end\n\n    return _G[raceData.glueString] or raceData.glueString\nend"""
    new = """local function GetRaceName(raceID)\n    local exactRaceData = EXACT_RACE_DATA[raceID]\n    if exactRaceData then\n        return exactRaceData.name\n    end\n\n    local raceData = RACE_DATA[raceID]\n    if not raceData then\n        return \"Human\"\n    end\n\n    return _G[raceData.glueString] or raceData.glueString\nend"""
    if old in text:
        text = text.replace(old, new, 1)
    elif "local exactRaceData = EXACT_RACE_DATA[raceID]" not in text:
        raise ValueError("CharacterInfo.lua GetRaceName anchor not found")

    old = """local function GetFactionForRaceID(raceID)\n    local _, faction = GetFactionForRace(raceID)\n    if faction then\n        return faction\n    end\n    local raceData = RACE_DATA[raceID]\n    return raceData and raceData.faction or \"Alliance\"\nend"""
    new = """local function GetFactionForRaceID(raceID)\n    local exactRaceData = EXACT_RACE_DATA[raceID]\n    if exactRaceData then\n        return exactRaceData.faction\n    end\n\n    local _, faction = GetFactionForRace(raceID)\n    if faction then\n        return faction\n    end\n    local raceData = RACE_DATA[raceID]\n    return raceData and raceData.faction or \"Alliance\"\nend"""
    if old in text:
        text = text.replace(old, new, 1)
    elif "return exactRaceData.faction" not in text:
        raise ValueError("CharacterInfo.lua GetFactionForRaceID anchor not found")

    text = text.replace(
        '    Spell_1 = {name = "Might of the Blackrock", icon = "racial_orc_command", description = "Attack power and spell damage increased."},\n'
        '    Spell_2 = {name = "Hardiness", icon = "inv_helmet_23", description = "Reduced duration of Stun effects."},\n'
        '    Spell_3 = {name = "Ancestral Call", icon = "spell_nature_ancestralguardian", description = "Chance to resist Curse, Disease, and Poison effects."},\n'
        '    Spell_4 = {name = "Open Skies", icon = "ability_mount_kodo_03", description = "Pets\' maximum health increased."},',
        '    Spell_1 = {name = "Ancestral Call", icon = "spell_nature_ancestralguardian", description = "Calls on your uncorrupted ancestors to increase attack power and spell damage."},\n'
        '    Spell_2 = {name = "Savage Blood", icon = "racial_orc_command", description = "Grants a chance to resist Curse, Disease, and Poison effects."},\n'
        '    Spell_3 = {name = "Sympathetic Vigor", icon = "ability_hunter_beastcall", description = "Increases your pet\'s maximum health."},\n'
        '    Spell_4 = {name = "Unwavering Will", icon = "inv_helmet_23", description = "Reduces the duration of Stun effects."},',
    )

    old_maghar = '    [15] = {token = "MAGHAR", name = "Mag\'har Orc", spells = {"Might of the Blackrock", "Ancestral Call", "Open Skies", "Hardiness"}},'
    new_maghar = '    [15] = {token = "MAGHAR", name = "Mag\'har Orc", spells = {"Ancestral Call", "Savage Blood", "Sympathetic Vigor", "Unwavering Will"}},'
    text = text.replace(old_maghar, new_maghar)

    if "local function GetExactRaceIDForFileString(fileString)" not in text:
        anchor = "local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16, 18}"
        helper = """local EXACT_RACE_ID_BY_FILE_STRING = {}\nfor exactRaceID, exactRaceData in pairs(EXACT_RACE_DATA) do\n    if exactRaceData.fileString then\n        EXACT_RACE_ID_BY_FILE_STRING[strupper(exactRaceData.fileString)] = exactRaceID\n    end\nend\n\nlocal function GetExactRaceIDForFileString(fileString)\n    if not fileString then\n        return nil\n    end\n    return EXACT_RACE_ID_BY_FILE_STRING[strupper(fileString)]\nend\n\n"""
        if anchor not in text:
            raise ValueError("CharacterInfo.lua exact FileString helper anchor not found")
        text = text.replace(anchor, helper + anchor, 1)

    if "_G.EXACT_RACE_DATA = EXACT_RACE_DATA" not in text:
        anchor = "_G.RACE_DATA = RACE_DATA"
        if anchor not in text:
            raise ValueError("CharacterInfo.lua export anchor not found")
        text = text.replace(anchor, anchor + "\n_G.EXACT_RACE_DATA = EXACT_RACE_DATA", 1)
    if "_G.GetExactRaceIDForFileString = GetExactRaceIDForFileString" not in text:
        anchor = "_G.EXACT_RACE_DATA = EXACT_RACE_DATA"
        if anchor not in text:
            raise ValueError("CharacterInfo.lua exact FileString export anchor not found")
        text = text.replace(anchor, anchor + "\n_G.GetExactRaceIDForFileString = GetExactRaceIDForFileString", 1)

    return text.encode("utf-8")


def _patch_glue_strings(data: bytes) -> bytes:
    text = data.decode("utf-8")
    marker = 'RACE_INFO_MAGHAR = "The uncorrupted orc clans of Draenor fight with pride, courage, and an unrelenting sense of honor.";'
    if marker in text:
        return data

    block = """

MAGHAR = "Mag'har Orc";
MAGHAR_MALE = "Mag'har Orc";
MAGHAR_FEMALE = "Mag'har Orc";
RACE_INFO_MAGHAR = "The uncorrupted orc clans of Draenor fight with pride, courage, and an unrelenting sense of honor.";
RACE_INFO_MAGHAR_FEMALE = RACE_INFO_MAGHAR;
ABILITY_INFO_MAGHAR1 = "- Ancestral Call increases attack power and spell damage.";
ABILITY_INFO_MAGHAR2 = "- Savage Blood grants a chance to resist Curse, Disease, and Poison effects.";
ABILITY_INFO_MAGHAR3 = "- Sympathetic Vigor increases your pet's maximum health.";
ABILITY_INFO_MAGHAR4 = "- Unwavering Will reduces the duration of Stun effects.";
"""
    return (text.rstrip() + block + "\n").encode("utf-8")


def _patch_glue_parent(data: bytes) -> bytes:
    text = data.decode("utf-8")
    if 'CharModelFogInfo["MAGHAR"]' not in text:
        anchor = 'CharModelFogInfo["ORC"] = { r=0.5, g=0.5, b=0.5, far=270 };'
        text = text.replace(anchor, anchor + '\nCharModelFogInfo["MAGHAR"] = CharModelFogInfo["ORC"];', 1)
    if 'RaceLights["MAGHAR"] = RaceLights["ORC"]' not in text:
        anchor = 'RaceLights["ILLIDARI"] = RaceLights["ORC"];'
        if anchor in text:
            text = text.replace(anchor, anchor + '\nRaceLights["MAGHAR"] = RaceLights["ORC"];', 1)
    return text.encode("utf-8")


def _portrait_entries(client_data: Path, manifest: dict) -> dict[str, bytes]:
    male_template, _ = _effective_file(client_data, r"Interface\CharacterFrame\TemporaryPortrait-Male-Orc.blp")
    if manifest.get("portrait_sources"):
        from race_portrait_pack import circular_mask, compose_race_icon, decode_client_blp, portrait_bytes, ring_layer

        ring_data, _ = _effective_file(client_data, r"Interface\Glues\CharacterCreate\UI-CharacterCreate-GenderMale.blp")
        ring = ring_layer(decode_client_blp(ring_data))
        entries = {}
        for race, token in manifest["client_file_strings"].items():
            sources = manifest["portrait_sources"].get(race, manifest["portrait_sources"])
            for sex, source in sources.items():
                art = portrait_bytes(Path(source), circular_mask())
                portrait = encode_portrait(art, male_template)
                icon = encode_portrait(compose_race_icon(art, ring), male_template)
                stem = f"{CHARACTER_FRAME_ROOT}TemporaryPortrait-{sex.title()}-{token}"
                entries[stem] = entries[stem + ".blp"] = portrait
                entries[f"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-{token}{sex.title()}.blp"] = icon
        return entries
    source_root = Path(manifest["source_patch_root"]) / "custom" / "maghar" / "character" / "orc"
    result: dict[str, bytes] = {}
    for gender, sex in (("Male", "male"), ("Female", "female")):
        source = source_root / sex / ("orcmaleclanfaceupper00_00.blp" if sex == "male" else "orcfemaleclanfaceupper00_00.blp")
        image = Image.open(source).convert("RGBA")
        # The modern upper-face sheet is square and centered enough for a deterministic UI portrait.
        portrait_image = image.resize((64, 64), Image.Resampling.LANCZOS)
        encoded = encode_portrait(portrait_image, male_template)
        validate_portrait(encoded, source)
        result[f"{CHARACTER_FRAME_ROOT}TemporaryPortrait-{gender}-Maghar.blp"] = encoded
    return result


def _asset_entries(manifest: dict) -> dict[str, bytes]:
    source = Path(manifest["source_patch_root"])
    if not source.is_dir():
        raise FileNotFoundError(f"retroported asset root does not exist: {source}")
    entries: dict[str, bytes] = {}
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        key = "\\".join(relative.parts)
        entries[key] = path.read_bytes()
    return entries


def _maghar_runtime_model_entries(manifest: dict) -> dict[str, bytes]:
    """Stage an experimental Retail-geometry runtime only when explicitly selected.

    Retail identifies Mag'har as an Orc model-fallback race. The directly converted
    modern Orc M2 keeps Retail-only geoset groups that build 12340 does not select,
    which makes most of the body disappear in Character Creation. The production
    Race45 profile therefore uses the client's known-good Orc2 HD player geometry
    and applies the retroported Mag'har materials through CharSections.

    Keep the Retail geometry transform available for future client/geoset work, but
    do not package it unless the manifest deliberately points at custom\\maghar\\runtime.
    """
    runtime_models = [
        manifest["models"][sex].get("runtime_model_path", manifest["models"][sex]["model_path"])
        for sex in ("male", "female")
    ]
    if not any(path.casefold().startswith("custom\\maghar\\runtime\\") for path in runtime_models):
        return {}

    source_root = Path(manifest["source_patch_root"])
    runtime_root = source_root.parents[1] / "integration" / "retail-runtime"
    entries: dict[str, bytes] = {}
    for sex, stem in (("male", "orcmale_hd"), ("female", "orcfemale_hd")):
        source_prefix = f"custom\\maghar\\character\\orc\\{sex}"
        target_model = manifest["models"][sex]["runtime_model_path"]
        if not target_model.casefold().startswith("custom\\maghar\\runtime\\"):
            continue
        target_parent = PureWindowsPath(target_model).parent

        for suffix in (".m2", "00.skin"):
            source_key = f"{source_prefix}\\{stem}{suffix}"
            source_path = runtime_root.joinpath(*PureWindowsPath(source_key).parts)
            if not source_path.is_file():
                raise FileNotFoundError(
                    f"RetroPorter runtime model is missing: {source_path}. "
                    "Run `python -m retroporter prepare-player-runtime --race maghar`."
                )
            target_key = str(target_parent / f"{stem}{suffix}")
            entries[target_key] = source_path.read_bytes()

        animation_root = source_root.joinpath(*PureWindowsPath(source_prefix).parts)
        animations = sorted(animation_root.glob(f"{stem}*.anim"))
        if not animations:
            raise FileNotFoundError(f"RetroPorter runtime animations are missing under {animation_root}")
        for animation in animations:
            target_key = str(target_parent / animation.name)
            entries[target_key] = animation.read_bytes()
    return entries


def _crop_blp_rgba(image: BlpImage, x: int, y: int, width: int, height: int) -> BlpImage:
    if x < 0 or y < 0 or x + width > image.width or y + height > image.height:
        raise ValueError(
            f"crop {x},{y} {width}x{height} exceeds {image.width}x{image.height}"
        )
    source = memoryview(image.data)
    output = bytearray(width * height * 4)
    source_stride = image.width * 4
    target_stride = width * 4
    for row in range(height):
        source_start = (y + row) * source_stride + x * 4
        target_start = row * target_stride
        output[target_start:target_start + target_stride] = source[source_start:source_start + target_stride]
    return BlpImage.from_rgba(width, height, output)


def _encode_wotlk_paletted(
    image: BlpImage,
    palette_rgb: list[tuple[int, int, int]] | None = None,
    mapper: PaletteMapper | None = None,
) -> bytes:
    """Encode an opaque CharSections texture using Blizzard's indexed BLP2 contract.

    The 3.3.5a character compositor reliably consumes the same compression=1,
    alpha_size=0, alpha_type=8 layout used by Esteria's working Orc2 body skins.
    A generic DXT1 BLP2 is valid to the renderer overall but renders neon green when
    used as a dynamic CharSections body layer, so do not substitute DXT here.

    Retail body and head textures for one skin tone can share a palette/mapper. That
    keeps their quantized complexion identical and reuses the mapper's colour cache,
    which makes the 180-texture appearance bake substantially faster.
    """
    # Blizzard's stock non-square CharSections fragments stop their mip chain
    # as soon as the shorter axis reaches 1 pixel. The generic encoder keeps
    # shrinking the remaining axis down to 1x1, which gives FaceLower/FaceUpper
    # extra 1-D mip levels that the character compositor was never authored for.
    # Match the stock Orc2 fragment contract exactly while keeping square body/
    # head textures on their normal full chain.
    mip_levels = min(image.width, image.height).bit_length()
    mip_chain = image.mip_chain(levels=mip_levels)
    if palette_rgb is None:
        palette_rgb = build_palette(image.data, 256)
    if mapper is None:
        mapper = PaletteMapper(palette_rgb)
    payloads = [bytes(mapper.map_image(level.data)) for level in mip_chain]
    # alpha_size=0: the high palette byte is padding, not authored alpha.
    # Match the working Orc2 BGRX representation. The earlier female regression
    # did not establish an alpha requirement: its face UV bake was also wrong.
    palette = [
        (b & 0xFF) | ((g & 0xFF) << 8) | ((r & 0xFF) << 16)
        for r, g, b in palette_rgb
    ]
    result = Blp.from_images(
        mip_chain,
        compression=BLP_COMPRESSION_PALETTE,
        alpha_type=8,
        alpha_size=0,
        palette=palette,
        payloads=payloads,
    )
    encoded = result.serialize()
    check = Blp.parse(encoded, "derived Mag'har skin")
    compatible, reason = check.is_wotlk_compatible()
    if (
        not compatible
        or check.width != image.width
        or check.height != image.height
        or check.compression != BLP_COMPRESSION_PALETTE
        or check.alpha_size != 0
        or check.alpha_type != 8
    ):
        raise ValueError(f"derived Mag'har skin is not Orc2 CharSections-compatible: {reason}")
    return encoded


def _derived_body_path(sex: str, stem: str, skin_index: int) -> str:
    return (
        f"custom\\maghar\\derived\\native\\{sex}\\body\\"
        f"{stem}body{skin_index:02d}.blp"
    )


def _derived_base_head_path(sex: str, stem: str, skin_index: int) -> str:
    return (
        f"custom\\maghar\\derived\\native\\{sex}\\head\\"
        f"{stem}headbase{skin_index:02d}.blp"
    )


def _derived_face_fragment_path(
    sex: str,
    stem: str,
    face_index: int,
    skin_index: int,
    fragment: str,
) -> str:
    if fragment not in {"upper", "lower"}:
        raise ValueError(f"unknown Mag'har face fragment {fragment}")
    return (
        f"custom\\maghar\\derived\\native\\{sex}\\face\\"
        f"{stem}face{fragment}{face_index:02d}_{skin_index:02d}.blp"
    )


def _maghar_face_uv_map(manifest: dict, client: Path, sex: str):
    """Project Retail head UVs onto the installed Orc2 model's legacy face sheet."""
    import numpy as np
    from wotlkconv.m2 import parse_m2, parse_skin

    model_path = manifest["models"][sex]["runtime_model_path"]
    with ClientFiles(str(client / "Data"), "enUS") as files:
        destination = parse_m2(files.find(model_path)[0], model_path)
        destination_skin = parse_skin(files.find(model_path[:-3] + "00.skin")[0])
    source_path = _patch_root_path(Path(manifest["source_patch_root"]), manifest["models"][sex]["model_path"])
    source = parse_m2(source_path.read_bytes(), str(source_path))
    source_skin = parse_skin(source_path.with_name(source_path.stem + "00.skin").read_bytes())

    def position(model, index):
        return tuple(round(value, 4) for value in struct.unpack_from("<3f", model.vertices, index * 48))

    def uv(model, index):
        return np.array(struct.unpack_from("<2f", model.vertices, index * 48 + 32))

    def triangles(skin, submesh):
        _, level, _, _, start, count = struct.unpack_from("<6H", submesh)
        start += level << 16
        return (tuple(skin.vertices[j] for j in skin.indices[i:i + 3]) for i in range(start, start + count, 3))

    source_triangles = {}
    source_vertices = {}
    # Retail's normal Orc head is geoset 3202, using the right half of clanskin.
    for submesh in source_skin.submeshes:
        if struct.unpack_from("<H", submesh)[0] != 3202:
            continue
        for triangle in triangles(source_skin, submesh):
            source_triangles[tuple(sorted(position(source, i) for i in triangle))] = triangle
            for index in triangle:
                source_vertices.setdefault(position(source, index), set()).add(index)
    if not source_triangles:
        raise ValueError(f"{sex}: Retail Orc head geoset 3202 is missing")

    coordinates = np.full((192, 256, 2), np.nan)
    matched = unmatched = 0
    maximum_distance = 0.0
    for mesh_index, submesh in enumerate(destination_skin.submeshes):
        batches = [b for b in destination_skin.batches if struct.unpack_from("<H", b, 4)[0] == mesh_index]
        if struct.unpack_from("<H", submesh)[0] != 0 or not any(
            destination.textures[destination.texture_combos[struct.unpack_from("<H", b, 16)[0]]]["type"] == 1
            for b in batches
        ):
            continue
        for triangle in triangles(destination_skin, submesh):
            target_uv = np.array([uv(destination, j) for j in triangle])
            if target_uv[:, 1].min() < .625:
                continue
            original = source_triangles.get(tuple(sorted(position(destination, j) for j in triangle)))
            if original:
                matched += 1
                mapped = [
                    next(k for k in original if position(source, k) == position(destination, j)) for j in triangle
                ]
            else:
                unmatched += 1
                mapped = []
                for index in triangle:
                    point = position(destination, index)
                    candidates = source_vertices.get(point)
                    if not candidates:
                        # ponytail: a few seam vertices differ by rounding; reject actual geometry changes.
                        nearest = min(source_vertices, key=lambda p: np.linalg.norm(np.array(p) - point))
                        distance = float(np.linalg.norm(np.array(nearest) - point))
                        maximum_distance = max(maximum_distance, distance)
                        if distance > .001:
                            raise ValueError(f"{sex}: Orc2 head vertex differs from Retail by {distance}")
                        candidates = source_vertices[nearest]
                    normal = np.array(struct.unpack_from("<3f", destination.vertices, index * 48 + 20))
                    mapped.append(min(candidates, key=lambda k: np.linalg.norm(
                        np.array(struct.unpack_from("<3f", source.vertices, k * 48 + 20)) - normal)))
            source_uv = np.array([[(uv(source, j)[0] - .5) * 2, uv(source, j)[1]] for j in mapped])
            target_uv = target_uv * 512 - np.array([0, 320])
            transform = np.column_stack((target_uv, np.ones(3)))
            if abs(np.linalg.det(transform)) < 1e-8:
                continue
            x0 = max(0, int(np.floor(target_uv[:, 0].min())))
            x1 = min(256, int(np.ceil(target_uv[:, 0].max())))
            y0 = max(0, int(np.floor(target_uv[:, 1].min())))
            y1 = min(192, int(np.ceil(target_uv[:, 1].max())))
            yy, xx = np.mgrid[y0:y1, x0:x1]
            weights = np.stack((xx + .5, yy + .5, np.ones_like(xx)), axis=-1) @ np.linalg.inv(transform)
            inside = (weights >= -1e-6).all(axis=-1)
            coordinates[y0:y1, x0:x1][inside] = (weights @ source_uv)[inside]

    covered = np.isfinite(coordinates).all(axis=-1)
    if matched < .9 * (matched + unmatched) or covered.mean() < .7:
        raise ValueError(f"{sex}: insufficient matching head geometry for a reliable face bake")
    report = {"matched_triangles": matched, "unmatched_triangles": unmatched,
              "maximum_vertex_distance": maximum_distance, "covered_pixels": int(covered.sum())}
    # Extend edge texels into unused UV space to prevent dark seams in lower mips.
    filled = covered.copy()
    while not filled.all():
        previous = filled.copy()
        for axis in (0, 1):
            for shift in (-1, 1):
                neighbors = np.roll(previous, shift, axis=axis)
                edge = [slice(None), slice(None)]
                edge[axis] = 0 if shift == 1 else -1
                neighbors[tuple(edge)] = False
                take = neighbors & ~filled
                coordinates[take] = np.roll(coordinates, shift, axis=axis)[take]
                filled[take] = True
    return coordinates, covered, report


def _project_maghar_face(image: BlpImage, coordinates) -> BlpImage:
    import numpy as np

    pixels = np.frombuffer(image.data, dtype=np.uint8).reshape(image.height, image.width, 4)
    points = np.clip(coordinates * [image.width, image.height] - .5, 0, [image.width - 1, image.height - 1])
    lower = points.astype(int)
    upper = np.minimum(lower + 1, [image.width - 1, image.height - 1])
    weight = points - lower
    x, y = lower[..., 0], lower[..., 1]
    x1, y1 = upper[..., 0], upper[..., 1]
    wx, wy = weight[..., 0, None], weight[..., 1, None]
    result = ((pixels[y, x] * (1 - wx) + pixels[y, x1] * wx) * (1 - wy)
              + (pixels[y1, x] * (1 - wx) + pixels[y1, x1] * wx) * wy)
    return BlpImage(256, 192, bytearray(np.rint(result).astype(np.uint8).tobytes()))


def _maghar_derived_asset_entries(manifest: dict, client: Path) -> dict[str, bytes]:
    """Bake Retail Mag'har art into the native Wrath Orc2 compositor contract.

    Retail's converted `clanskin` is a 1024x512 atlas. The left 512x512 half is
    the body base and the right 512x512 half is the skin-specific head base.
    Retail `clanfaceupper` files are complete 512x512 face materials. For Wrath,
    keep skin and face independent: one body/base-head pair per skin, plus the
    legacy FaceLower/FaceUpper fragments for every face/skin pair. Project through
    the matching Retail/Orc2 head geometry; those models do not share face UVs.
    """
    source_root = Path(manifest["source_patch_root"])
    maghar_root = source_root.parents[1]
    derived_root = maghar_root / "integration" / "derived"
    if derived_root.exists():
        shutil.rmtree(derived_root)
    derived_root.mkdir(parents=True, exist_ok=True)

    entries: dict[str, bytes] = {}
    body_rows: list[dict[str, object]] = []
    head_rows: list[dict[str, object]] = []
    face_fragment_rows: list[dict[str, object]] = []
    uv_reports = {}
    appearance = manifest["appearance"]
    skin_sources = appearance["skin_source_indices"]
    face_sources = appearance["face_indices"]

    for sex, stem in (("male", "orcmale"), ("female", "orcfemale")):
        face_coordinates, _, uv_reports[sex] = _maghar_face_uv_map(manifest, client, sex)
        for skin_index, source_skin in enumerate(skin_sources):
            source = (
                source_root / "custom" / "maghar" / "character" / "orc" / sex
                / f"{stem}clanskin00_{source_skin:02d}.blp"
            )
            parsed = Blp.parse(source.read_bytes(), str(source))
            if parsed.width != 1024 or parsed.height != 512:
                raise ValueError(
                    f"{source} is {parsed.width}x{parsed.height}; expected Retail Mag'har 1024x512 clan skin"
                )
            source_image = parsed.decode_level(0)
            body = _crop_blp_rgba(source_image, 0, 0, 512, 512)
            base_head = _crop_blp_rgba(source_image, 512, 0, 512, 512)

            face_images: list[tuple[int, int, BlpImage]] = []
            palette_source = bytearray(body.data)
            palette_source.extend(base_head.data)
            for face_index, source_face in enumerate(face_sources):
                face_source = (
                    source_root / "custom" / "maghar" / "character" / "orc" / sex
                    / f"{stem}clanfaceupper{source_face:02d}_{source_skin:02d}.blp"
                )
                face = Blp.parse(face_source.read_bytes(), str(face_source))
                if face.width != 512 or face.height != 512:
                    raise ValueError(
                        f"{face_source} is {face.width}x{face.height}; expected Retail Mag'har 512x512 head material"
                    )
                face_image = face.decode_level(0)
                face_images.append((face_index, source_face, face_image))
                palette_source.extend(face_image.data)

            # Keep one exact indexed colour contract for the body and all nine
            # Retail face materials belonging to this skin. Besides making the
            # bake much faster, this prevents independent palette quantization
            # from shifting the face complexion away from its matching body.
            palette_rgb = build_palette(palette_source, 256)
            mapper = PaletteMapper(palette_rgb)

            key = _derived_body_path(sex, stem, skin_index)
            encoded = _encode_wotlk_paletted(body, palette_rgb, mapper)
            entries[key] = encoded
            disk_path = derived_root.joinpath(*PureWindowsPath(key).parts)
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            disk_path.write_bytes(encoded)
            body_rows.append(
                {
                    "sex": sex,
                    "runtime_skin_index": skin_index,
                    "retail_source_skin": source_skin,
                    "path": key,
                    "sha256": hashlib.sha256(encoded).hexdigest(),
                }
            )

            head_key = _derived_base_head_path(sex, stem, skin_index)
            head_encoded = _encode_wotlk_paletted(base_head, palette_rgb, mapper)
            entries[head_key] = head_encoded
            head_disk_path = derived_root.joinpath(*PureWindowsPath(head_key).parts)
            head_disk_path.parent.mkdir(parents=True, exist_ok=True)
            head_disk_path.write_bytes(head_encoded)
            head_rows.append(
                {
                    "sex": sex,
                    "runtime_skin_index": skin_index,
                    "retail_source_skin": source_skin,
                    "path": head_key,
                    "sha256": hashlib.sha256(head_encoded).hexdigest(),
                }
            )

            for face_index, source_face, face_image in face_images:
                face_sheet = _project_maghar_face(face_image, face_coordinates)
                for fragment, crop in (
                    ("upper", (0, 0, 256, 64)),
                    ("lower", (0, 64, 256, 128)),
                ):
                    fragment_image = _crop_blp_rgba(face_sheet, *crop)
                    fragment_key = _derived_face_fragment_path(
                        sex, stem, face_index, skin_index, fragment
                    )
                    fragment_encoded = _encode_wotlk_paletted(
                        fragment_image, palette_rgb, mapper
                    )
                    entries[fragment_key] = fragment_encoded
                    fragment_disk_path = derived_root.joinpath(
                        *PureWindowsPath(fragment_key).parts
                    )
                    fragment_disk_path.parent.mkdir(parents=True, exist_ok=True)
                    fragment_disk_path.write_bytes(fragment_encoded)
                    face_fragment_rows.append(
                        {
                            "sex": sex,
                            "runtime_skin_index": skin_index,
                            "retail_source_skin": source_skin,
                            "runtime_face_index": face_index,
                            "retail_source_face": source_face,
                            "fragment": fragment,
                            "path": fragment_key,
                            "sha256": hashlib.sha256(fragment_encoded).hexdigest(),
                        }
                    )

    report = {
        "schema_version": 5,
        "source": str(source_root),
        "derived_root": str(derived_root),
        "bodies": body_rows,
        "heads": head_rows,
        "face_fragments": face_fragment_rows,
        "face_uv_projection": uv_reports,
    }
    (derived_root / "derived-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return entries


def _embedded_m2_texture_refs_from_bytes(data: bytes) -> set[str]:
    refs = set()
    for match in re.finditer(rb"(?i)(?:custom\\[^\x00\r\n]+?\.blp)", data):
        refs.add(match.group(0).decode("utf-8", errors="strict"))
    return refs


def _embedded_m2_texture_refs(path: Path) -> set[str]:
    return _embedded_m2_texture_refs_from_bytes(path.read_bytes())


def _patch_root_path(root: Path, asset_path: str) -> Path:
    return root.joinpath(*PureWindowsPath(asset_path).parts)


def _validate_asset_dependencies(manifest: dict) -> None:
    root = Path(manifest["source_patch_root"])
    appearance = manifest["appearance"]
    missing: list[Path] = []
    for gender in ("male", "female"):
        model_path = _patch_root_path(root, manifest["models"][gender]["model_path"])
        if not model_path.is_file():
            missing.append(model_path)
            continue
        for texture_ref in sorted(_embedded_m2_texture_refs(model_path)):
            dependency = _patch_root_path(root, texture_ref)
            if not dependency.is_file():
                missing.append(dependency)
    retail_skin_sources = appearance.get("retail_skin_source_indices", appearance["skin_source_indices"])
    retail_face_indices = appearance.get("retail_face_indices", appearance["face_indices"])
    for sex, stem in (("male", "orcmale"), ("female", "orcfemale")):
        for source_color in retail_skin_sources:
            for name in (
                f"{stem}clanskin00_{source_color:02d}.blp",
                f"{stem}clannakedpelvisskin00_{source_color:02d}.blp",
                f"{stem}clannakedtorsoskin00_{source_color:02d}.blp",
            ):
                path = root / "custom" / "maghar" / "character" / "orc" / sex / name
                if not path.is_file():
                    missing.append(path)
            for face in retail_face_indices:
                path = root / "custom" / "maghar" / "character" / "orc" / sex / f"{stem}clanfaceupper{face:02d}_{source_color:02d}.blp"
                if not path.is_file():
                    missing.append(path)
    for color in appearance["hair_color_indices"]:
        path = root / "custom" / "maghar" / "character" / "orc" / f"orcclanhair00_{color:02d}.blp"
        if not path.is_file():
            missing.append(path)
    if missing:
        raise ValueError(f"Mag'har appearance dependency is missing: {missing[0]} ({len(missing)} missing)")


def build_tables(client_data: Path, manifest: dict, allocation: dict) -> tuple[dict[str, bytes], bytes]:
    table_names = (
        "ChrRaces",
        "CreatureModelData",
        "CreatureDisplayInfo",
        "CharSections",
        "CharHairGeosets",
        "CharHairTextures",
        "CharacterFacialHairStyles",
        "BarberShopStyle",
        "CharBaseInfo",
        "CharStartOutfit",
        "NameGen",
        "Spell",
    )
    base = {name: _full_table(client_data, name)[0] for name in table_names}
    output = dict(base)
    output["CreatureModelData"] = _merge_model_table("CreatureModelData", base["CreatureModelData"], manifest, allocation)
    output["CreatureDisplayInfo"] = _merge_model_table("CreatureDisplayInfo", base["CreatureDisplayInfo"], manifest, allocation)
    output["ChrRaces"] = _merge_chr_races(base["ChrRaces"], manifest, allocation)
    output["CharSections"] = _maghar_char_sections(base["CharSections"], manifest, allocation)
    output["CharHairGeosets"] = _clone_race_rows("CharHairGeosets", base["CharHairGeosets"], manifest, allocation)
    output["CharHairTextures"] = _clone_race_rows("CharHairTextures", base["CharHairTextures"], manifest, allocation)
    output["CharacterFacialHairStyles"] = _clone_race_rows(
        "CharacterFacialHairStyles", base["CharacterFacialHairStyles"], manifest, allocation
    )
    output["BarberShopStyle"] = _clone_race_rows("BarberShopStyle", base["BarberShopStyle"], manifest, allocation)
    output["CharBaseInfo"] = _build_char_base_info(base["CharBaseInfo"], manifest)
    output["CharStartOutfit"] = _build_char_start_outfit(base["CharStartOutfit"], manifest, allocation)
    output["NameGen"] = _clone_namegen(base["NameGen"], manifest, allocation)
    output["Spell"], spell_continuation = _merge_spells(base["Spell"], manifest)
    return output, spell_continuation


def plan(slug: str, client: Path) -> dict:
    manifest = load_manifest(slug)
    allocation = load_json(ALLOCATION_PATH)
    if slug != "maghar":
        raise NotImplementedError("Phase 1 currently validates the generic framework with Mag'har first")
    _validate_asset_dependencies(manifest)
    tables, _ = build_tables(client / "Data", manifest, allocation)
    assets = _asset_entries(manifest)
    return {
        "slug": slug,
        "client": str(client),
        "race_ids": manifest["race_ids"],
        "assets": len(assets),
        "tables": {name: len(RawWdbc(data).records) for name, data in tables.items() if name != "Spell"},
        "spell_rows": len(Wdbc(tables["Spell"]).rows),
        "server_dbcs": list(SERVER_DBC_TABLES),
        "source_root": manifest["source_patch_root"],
    }


def _build_root(slug: str) -> Path:
    return Path(r"G:\RetroPorterWork") / slug / "integration" / "latest"


def build(slug: str, client: Path) -> BuildPaths:
    if slug == "skyborne":
        from skyborne_race_pack import build as build_skyborne

        return build_skyborne(client)
    manifest = load_manifest(slug)
    allocation = load_json(ALLOCATION_PATH)
    _validate_asset_dependencies(manifest)
    tables, _ = build_tables(client / "Data", manifest, allocation)
    assets = _asset_entries(manifest)
    derived_assets: dict[str, bytes] = {}
    runtime_model_assets: dict[str, bytes] = {}
    if slug == "maghar":
        runtime_model_assets = _maghar_runtime_model_entries(manifest)
        assets.update(runtime_model_assets)
        derived_assets = _maghar_derived_asset_entries(manifest, client)
        assets.update(derived_assets)

    output = _build_root(slug)
    if output.exists():
        shutil.rmtree(output)
    (output / "Data" / "enUS").mkdir(parents=True, exist_ok=True)
    server_dbc_dir = output / "server" / "dbc"
    server_dbc_dir.mkdir(parents=True, exist_ok=True)
    stage_global = output / GLOBAL_ARCHIVE_REL
    stage_asset = output / ASSET_ARCHIVE_REL
    stage_locale = output / LOCALE_ARCHIVE_REL
    shutil.copy2(client / LOCALE_ARCHIVE_REL, stage_locale)

    storm = Storm(DLL_DEFAULT)
    dbc_entries = {f"{DBC_ROOT}{name}.dbc": data for name, data in tables.items()}

    # The client does not use the locale Z copy of core character DBCs to build
    # the runtime customization hierarchy. During the Mag'har pilot the live
    # CharSections/CreatureModelData in patch-Z remained stale while locale Z
    # contained the corrected rows; the runtime table exactly matched patch-Z.
    # Rebuild the live global archive only when one of the generated DBCs actually
    # changed. Appearance-only rebuilds update Patch-R/locale Z and can safely copy
    # an already-synchronized global Z verbatim, avoiding a multi-minute 2+ GiB
    # streaming rebuild on every texture experiment.
    live_global = client / GLOBAL_ARCHIVE_REL
    global_size_before_compact = live_global.stat().st_size
    global_needs_dbc_update = any(
        _read_archive_entry(storm, live_global, path) != payload
        for path, payload in dbc_entries.items()
    )
    if global_needs_dbc_update:
        rebuild_archive_streaming(storm, live_global, stage_global)
        storm.replace_archive_entries(stage_global, dbc_entries)
    else:
        shutil.copy2(live_global, stage_global)
    global_size_after_compact = stage_global.stat().st_size
    glue_entries: dict[str, bytes] = {}
    for name, patcher in (
        ("CharacterCreate.lua", _patch_character_create_lua),
        ("CharacterCreate.xml", _patch_character_create_xml),
        ("CharacterInfo.lua", _patch_character_info),
        ("GlueStrings.lua", _patch_glue_strings),
        ("GlueParent.lua", _patch_glue_parent),
    ):
        original, _ = _effective_file(client / "Data", f"{GLUE_ROOT}{name}")
        glue_entries[f"{GLUE_ROOT}{name}"] = patcher(original)
    portrait_entries = _portrait_entries(client / "Data", manifest)

    # Dynamic CharSections art must be available from the global archive chain.
    # patch-Z is already at the classic 4 GiB ceiling and also contains stale
    # Mag'har fragments from earlier experiments. Never append another appearance
    # generation to it. Build a dedicated Patch-R (Retroported races) from scratch
    # instead. New native-compositor paths are unique, so the older patch-Z entries
    # cannot shadow them even though Z has higher archive priority than R.
    storm.create_archive(stage_asset, assets)
    storm.replace_archive_entries(stage_locale, {**assets, **dbc_entries, **glue_entries, **portrait_entries})

    for name in SERVER_DBC_TABLES:
        (server_dbc_dir / f"{name}.dbc").write_bytes(tables[name])

    report = {
        "slug": slug,
        "race_ids": manifest["race_ids"],
        "client_source_hashes": {
            str(GLOBAL_ARCHIVE_REL): sha256(client / GLOBAL_ARCHIVE_REL),
            str(LOCALE_ARCHIVE_REL): sha256(client / LOCALE_ARCHIVE_REL),
        },
        "staged_hashes": {
            str(GLOBAL_ARCHIVE_REL): sha256(stage_global),
            str(ASSET_ARCHIVE_REL): sha256(stage_asset),
            str(LOCALE_ARCHIVE_REL): sha256(stage_locale),
        },
        "asset_count": len(assets),
        "runtime_model_asset_count": len(runtime_model_assets),
        "derived_asset_count": len(derived_assets),
        "global_archive_size_before_compact": global_size_before_compact,
        "global_archive_size_after_compact": global_size_after_compact,
        "global_archive_rebuilt": global_needs_dbc_update,
        "dbc_tables": sorted(tables),
        "server_dbcs": list(SERVER_DBC_TABLES),
    }
    report_path = output / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return BuildPaths(output, stage_global, stage_asset, stage_locale, server_dbc_dir, report_path)


def _read_archive_entry(storm: Storm, archive: Path, name: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)


def _row_ids(data: bytes) -> set[int]:
    return {int.from_bytes(row[:4], "little") for row in RawWdbc(data).records}


def validate(slug: str, client: Path, paths: BuildPaths | None = None) -> dict:
    manifest = load_manifest(slug)
    allocation = load_json(ALLOCATION_PATH)
    paths = paths or BuildPaths(
        _build_root(slug),
        _build_root(slug) / GLOBAL_ARCHIVE_REL,
        _build_root(slug) / ASSET_ARCHIVE_REL,
        _build_root(slug) / LOCALE_ARCHIVE_REL,
        _build_root(slug) / "server" / "dbc",
        _build_root(slug) / "build-report.json",
    )
    if slug == "skyborne":
        from skyborne_race_pack import validate as validate_skyborne

        return validate_skyborne(client, paths)
    if (
        not paths.global_archive.is_file()
        or not paths.asset_archive.is_file()
        or not paths.locale_archive.is_file()
    ):
        raise FileNotFoundError("staged archives do not exist; run build first")

    storm = Storm(DLL_DEFAULT)
    race_id = manifest["race_ids"][0]
    validations: dict[str, object] = {}
    for archive in (paths.global_archive, paths.locale_archive):
        races = RawWdbc(_read_archive_entry(storm, archive, f"{DBC_ROOT}ChrRaces.dbc"))
        race_rows = [row for row in races.records if int.from_bytes(row[:4], "little") == race_id]
        if len(race_rows) != 1:
            raise ValueError(f"{archive}: expected exactly one ChrRaces row for {race_id}")
        row = race_rows[0]
        if _string(races.strings, _value(row, 11 * 4)).decode() != manifest["client_file_strings"][str(race_id)]:
            raise ValueError(f"{archive}: wrong ClientFileString for race {race_id}")
        sections = _table_rows_for_race(_read_archive_entry(storm, archive, f"{DBC_ROOT}CharSections.dbc"), "CharSections", race_id)
        if not sections:
            raise ValueError(f"{archive}: no CharSections for race {race_id}")
        glue = _read_archive_entry(storm, archive, f"{GLUE_ROOT}CharacterCreate.lua").decode("utf-8")
        if (
            "MAX_RACES = 64;" not in glue
            or "button.raceID = raceID;" not in glue
            or "CharacterCreate.selectedRaceID" not in glue
            or "local exactRaceID = _G.GetExactRaceIDForFileString(fileString);" not in glue
        ):
            raise ValueError(f"{archive}: CharacterCreate high-ID mapping is missing")
        xml = _read_archive_entry(storm, archive, f"{GLUE_ROOT}CharacterCreate.xml").decode("utf-8")
        if "CharacterCreateRaceButton64" not in xml:
            raise ValueError(f"{archive}: CharacterCreate button capacity is below 64")
        info = _read_archive_entry(storm, archive, f"{GLUE_ROOT}CharacterInfo.lua").decode("utf-8")
        if '[45] = { glueString = "MAGHAR", name = "Mag\'har Orc", faction = "Horde", fileString = "Maghar" }' not in info:
            raise ValueError(f"{archive}: Mag'har exact CharacterInfo row is missing")
        if "_G.GetExactRaceIDForFileString = GetExactRaceIDForFileString" not in info:
            raise ValueError(f"{archive}: exact RaceID FileString resolver is missing")
        if 'local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 45}' in info:
            raise ValueError(f"{archive}: exact RaceID 45 leaked into the UI-slot HORDE_RACES table")
        strings = _read_archive_entry(storm, archive, f"{GLUE_ROOT}GlueStrings.lua").decode("utf-8")
        if 'RACE_INFO_MAGHAR = "The uncorrupted orc clans of Draenor' not in strings:
            raise ValueError(f"{archive}: Mag'har GlueStrings are missing")
        validations[str(archive)] = {"charsections": len(sections)}

    # Core character DBC resolution is global-first in the 3.3.5a runtime. The
    # locale Z can make static inspection look correct while CharacterCreate is
    # still consuming stale rows from patch-Z. Require every generated full DBC
    # to be byte-identical in both Z archives so this cannot regress again.
    build_report = load_json(paths.report)
    for table_name in build_report["dbc_tables"]:
        global_dbc = _read_archive_entry(storm, paths.global_archive, f"{DBC_ROOT}{table_name}.dbc")
        locale_dbc = _read_archive_entry(storm, paths.locale_archive, f"{DBC_ROOT}{table_name}.dbc")
        if global_dbc != locale_dbc:
            raise ValueError(
                f"global/locale DBC mismatch for {table_name}.dbc; the runtime may consume stale global rows"
            )

    model_ids = set(allocation["race_allocations"][slug]["CreatureModelData"].values())
    display_ids = set(allocation["race_allocations"][slug]["CreatureDisplayInfo"].values())
    if any(display_id > 0xFFFF for display_id in display_ids):
        raise ValueError(f"player display IDs must fit AzerothCore uint16 PlayerInfo storage: {sorted(display_ids)}")

    # Read the global copies for runtime-critical model resolution. Validation
    # above guarantees the locale copies are identical.
    model_data = _read_archive_entry(storm, paths.global_archive, f"{DBC_ROOT}CreatureModelData.dbc")
    display_data = _read_archive_entry(storm, paths.global_archive, f"{DBC_ROOT}CreatureDisplayInfo.dbc")
    if not model_ids <= _row_ids(model_data) or not display_ids <= _row_ids(display_data):
        raise ValueError("staged model/display DBC rows are incomplete")
    for obsolete_id in manifest.get("obsolete_dbc_ids", {}).get("CreatureDisplayInfo", ()):
        if obsolete_id in _row_ids(display_data):
            raise ValueError(f"obsolete CreatureDisplayInfo row {obsolete_id} is still present")

    displays = RawWdbc(display_data)
    display_rows = {int.from_bytes(row[:4], "little"): row for row in displays.records}
    models = RawWdbc(model_data)
    model_rows = {int.from_bytes(row[:4], "little"): row for row in models.records}
    for gender in ("male", "female"):
        display_id = allocation["race_allocations"][slug]["CreatureDisplayInfo"][gender]
        model_id = allocation["race_allocations"][slug]["CreatureModelData"][gender]
        if _value(display_rows[display_id], 1 * 4) != model_id:
            raise ValueError(f"{gender} display {display_id} does not resolve to model {model_id}")
        expected_path = manifest["models"][gender].get("runtime_model_path", manifest["models"][gender]["model_path"])
        actual_path = _string(models.strings, _value(model_rows[model_id], 2 * 4)).decode("utf-8")
        if actual_path.casefold() != expected_path.casefold():
            raise ValueError(f"{gender} model {model_id} resolves to {actual_path}, expected {expected_path}")

    baseline_textures: set[str] = set()
    facial_overlays: set[str] = set()
    global_handle = storm.open_archive(paths.global_archive)
    asset_handle = storm.open_archive(paths.asset_archive)
    locale_handle = storm.open_archive(paths.locale_archive)
    try:
        global_map = {name.casefold(): name for name, *_ in storm.list_files(global_handle)}
        asset_map = {name.casefold(): name for name, *_ in storm.list_files(asset_handle)}
        locale_map = {name.casefold(): name for name, *_ in storm.list_files(locale_handle)}

        def staged_read(name: str) -> bytes:
            key = name.casefold()
            if key in locale_map:
                return storm.read(locale_handle, locale_map[key])
            if key in global_map:
                return storm.read(global_handle, global_map[key])
            if key in asset_map:
                return storm.read(asset_handle, asset_map[key])
            raise FileNotFoundError(name)

        def global_chain_read(name: str) -> bytes:
            key = name.casefold()
            if key in global_map:
                return storm.read(global_handle, global_map[key])
            if key in asset_map:
                return storm.read(asset_handle, asset_map[key])
            raise FileNotFoundError(name)

        for gender in ("male", "female"):
            model_spec = manifest["models"][gender]
            model_path = model_spec.get("runtime_model_path", model_spec["model_path"])
            try:
                model_bytes = staged_read(model_path)
            except FileNotFoundError:
                try:
                    model_bytes, _ = _effective_file(client / "Data", model_path)
                except Exception as exc:
                    raise ValueError(f"runtime player model is missing: {model_path}") from exc

            from wotlkconv.m2 import parse_m2

            if model_path.casefold().startswith("custom\\"):
                try:
                    global_model_bytes = global_chain_read(model_path)
                except FileNotFoundError as exc:
                    raise ValueError(f"runtime player model is missing from the global MPQ chain: {model_path}") from exc
                if global_model_bytes != model_bytes:
                    raise ValueError(
                        f"runtime player model differs between the global chain and locale overlay: {model_path}"
                    )

                model_windows_path = PureWindowsPath(model_path)
                skin_path = str(model_windows_path.parent / f"{model_windows_path.stem}00.skin")
                try:
                    global_chain_read(skin_path)
                except FileNotFoundError as exc:
                    raise ValueError(f"runtime player skin is missing from the global MPQ chain: {skin_path}") from exc

                if slug == "maghar":
                    source_animation_root = (
                        Path(manifest["source_patch_root"])
                        / "custom" / "maghar" / "character" / "orc" / gender
                    )
                    animation_files = sorted(source_animation_root.glob(f"{model_windows_path.stem}*.anim"))
                    if not animation_files:
                        raise ValueError(f"runtime player animations are missing for {model_path}")
                    for animation in animation_files:
                        animation_path = str(model_windows_path.parent / animation.name)
                        try:
                            global_chain_read(animation_path)
                        except FileNotFoundError as exc:
                            raise ValueError(
                                f"runtime player animation is missing from the global MPQ chain: {animation_path}"
                            ) from exc

            parsed_model = parse_m2(model_bytes, model_path)
            unsupported_types = sorted({texture["type"] for texture in parsed_model.textures if texture["type"] in {11, 15}})
            if unsupported_types:
                raise ValueError(f"runtime player model {model_path} still uses unsupported modern texture types {unsupported_types}")

            for texture_ref in sorted(_embedded_m2_texture_refs_from_bytes(model_bytes)):
                if model_path.casefold().startswith("custom\\"):
                    try:
                        staged_read(texture_ref)
                    except FileNotFoundError as exc:
                        raise ValueError(f"staged client is missing M2 texture dependency {texture_ref}") from exc
                else:
                    baseline_textures.add(texture_ref)

        sections_data = staged_read(f"{DBC_ROOT}CharSections.dbc")
        sections_table = RawWdbc(sections_data)
        race_sections = [row for row in sections_table.records if _value(row, 1 * 4) == race_id]
        for row in race_sections:
            for field in (4, 5, 6):
                offset = _value(row, field * 4)
                if not offset:
                    continue
                texture = _string(sections_table.strings, offset).decode("utf-8")
                if not texture:
                    continue
                if texture.casefold().startswith("custom\\maghar\\"):
                    try:
                        texture_bytes = staged_read(texture)
                    except FileNotFoundError as exc:
                        raise ValueError(f"staged client is missing CharSections texture {texture}") from exc
                    if _value(row, 3 * 4) == 2 and field == 4:
                        overlay = Blp.parse(texture_bytes, texture)
                        if overlay.compression != BLP_COMPRESSION_PALETTE or overlay.alpha_size != 8:
                            raise ValueError(f"facial-hair overlay needs indexed RGB and authored alpha: {texture}")
                    if texture.casefold().startswith("custom\\maghar\\derived\\"):
                        try:
                            global_texture_bytes = global_chain_read(texture)
                        except FileNotFoundError as exc:
                            raise ValueError(
                                f"derived Mag'har CharSections texture is missing from the global MPQ chain: {texture}"
                            ) from exc
                        if global_texture_bytes != texture_bytes:
                            raise ValueError(
                                f"derived Mag'har texture differs between the global chain and locale overlay: {texture}"
                            )
                        parsed = Blp.parse(global_texture_bytes, texture)
                        if (
                            parsed.compression != BLP_COMPRESSION_PALETTE
                            or parsed.alpha_size != 0
                            or parsed.alpha_type != 8
                            or any(entry >> 24 for entry in parsed.palette)
                        ):
                            raise ValueError(
                                f"derived Mag'har CharSections texture is not Orc2-compatible BGRX BLP2: {texture}"
                            )
                else:
                    baseline_textures.add(texture)
                    if _value(row, 3 * 4) == 2 and field == 4:
                        facial_overlays.add(texture)
    finally:
        storm.dll.SFileCloseArchive(locale_handle)
        storm.dll.SFileCloseArchive(asset_handle)
        storm.dll.SFileCloseArchive(global_handle)

    if baseline_textures:
        client_files = ClientFiles(str(client / "Data"), "enUS")
        try:
            for texture in sorted(baseline_textures):
                try:
                    texture_bytes, _ = client_files.find(texture)
                except Exception as exc:
                    raise ValueError(f"baseline client is missing CharSections texture {texture}") from exc
                if texture in facial_overlays:
                    parsed = Blp.parse(texture_bytes, texture)
                    if parsed.compression != BLP_COMPRESSION_PALETTE or parsed.alpha_size != 8:
                        raise ValueError(f"facial-hair overlay needs indexed RGB and authored alpha: {texture}")
        finally:
            client_files.close()

    for table_name in SERVER_DBC_TABLES:
        server_path = paths.server_dbc_dir / f"{table_name}.dbc"
        if not server_path.is_file():
            raise ValueError(f"full standard server DBC is missing: {server_path}")
        server_bytes = server_path.read_bytes()
        RawWdbc(server_bytes)
        locale_bytes = _read_archive_entry(storm, paths.locale_archive, f"{DBC_ROOT}{table_name}.dbc")
        global_bytes = _read_archive_entry(storm, paths.global_archive, f"{DBC_ROOT}{table_name}.dbc")
        if server_bytes != locale_bytes or server_bytes != global_bytes:
            raise ValueError(f"server/global/locale full DBC mismatch for {table_name}.dbc")

    validations["staged_hashes"] = {
        "global": sha256(paths.global_archive),
        "assets": sha256(paths.asset_archive),
        "locale": sha256(paths.locale_archive),
    }
    return validations


def install(slug: str, client: Path) -> dict:
    # Reuse a fully built stage when it was produced from the exact current live
    # archives. This keeps iterative visual QA from spending several minutes
    # rebuilding the multi-gigabyte global Z a second time between `build` and
    # `install`, while the source-hash gate prevents installing a stale stage.
    root = _build_root(slug)
    staged = BuildPaths(
        root,
        root / GLOBAL_ARCHIVE_REL,
        root / ASSET_ARCHIVE_REL,
        root / LOCALE_ARCHIVE_REL,
        root / "server" / "dbc",
        root / "build-report.json",
    )
    reuse_stage = False
    if staged.report.is_file():
        report = json.loads(staged.report.read_text(encoding="utf-8"))
        source_hashes = report.get("client_source_hashes", {})
        reuse_stage = (
            staged.global_archive.is_file()
            and staged.asset_archive.is_file()
            and staged.locale_archive.is_file()
            and source_hashes.get(str(GLOBAL_ARCHIVE_REL)) == sha256(client / GLOBAL_ARCHIVE_REL)
            and source_hashes.get(str(LOCALE_ARCHIVE_REL)) == sha256(client / LOCALE_ARCHIVE_REL)
        )
    paths = staged if reuse_stage else build(slug, client)
    validation = validate(slug, client, paths)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Keep multi-gigabyte client safety backups beside the client drive rather than
    # consuming the source checkout volume. The dev client can live on a much larger
    # disk than the repository, and failed installs should never exhaust the repo drive.
    backup = client.parent / "3.3.5a - Backups" / f"retroported-races-{slug}-{timestamp}"
    (backup / "Data" / "enUS").mkdir(parents=True, exist_ok=True)

    live_global = client / GLOBAL_ARCHIVE_REL
    live_asset = client / ASSET_ARCHIVE_REL
    live_locale = client / LOCALE_ARCHIVE_REL
    source_hashes: dict[Path, str | None] = {
        live_global: sha256(live_global),
        live_asset: sha256(live_asset) if live_asset.is_file() else None,
        live_locale: sha256(live_locale),
    }
    staged_archives = {
        live_global: paths.global_archive,
        live_asset: paths.asset_archive,
        live_locale: paths.locale_archive,
    }
    changed_archives = {
        live: staged
        for live, staged in staged_archives.items()
        if source_hashes[live] is None or sha256(staged) != source_hashes[live]
    }

    archive_relatives = {
        live_global: GLOBAL_ARCHIVE_REL,
        live_asset: ASSET_ARCHIVE_REL,
        live_locale: LOCALE_ARCHIVE_REL,
    }
    for live, staged in changed_archives.items():
        relative = archive_relatives[live]
        if live.is_file():
            backup_file = backup / relative
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, backup_file)
            if sha256(backup_file) != source_hashes[live]:
                raise RuntimeError(f"client backup hash verification failed for {live}; live client was not changed")

        temp_file = live.with_suffix(live.suffix + ".retroported-next")
        shutil.copy2(staged, temp_file)
        if sha256(temp_file) != sha256(staged):
            temp_file.unlink(missing_ok=True)
            raise RuntimeError(f"staged client copy hash verification failed for {live}; live client was not changed")
        os.replace(temp_file, live)

    SERVER_DBC_ROOT.mkdir(parents=True, exist_ok=True)
    server_backup = backup / "server-dbc"
    server_backup.mkdir(parents=True, exist_ok=True)
    installed_server_dbcs: dict[str, str] = {}
    for source in paths.server_dbc_dir.glob("*.dbc"):
        target = SERVER_DBC_ROOT / source.name
        if target.is_file():
            shutil.copy2(target, server_backup / target.name)
        shutil.copy2(source, target)
        if sha256(target) != sha256(source):
            raise RuntimeError(f"server DBC copy hash verification failed for {source.name}")
        installed_server_dbcs[source.name] = sha256(target)

    stale_backup = backup / "obsolete-dbc-continuations"
    stale_race_continuations = list(SERVER_CONTINUATION_ROOT.glob("*.dbc1-retroported-races"))
    if stale_race_continuations:
        stale_backup.mkdir(parents=True, exist_ok=True)
        for stale in stale_race_continuations:
            shutil.copy2(stale, stale_backup / stale.name)
            stale.unlink()

    install_report = {
        "slug": slug,
        "backup": str(backup),
        "pre_install_hashes": {str(path): digest for path, digest in source_hashes.items()},
        "installed_hashes": {
            str(live_global): sha256(live_global),
            str(live_asset): sha256(live_asset),
            str(live_locale): sha256(live_locale),
        },
        "installed_server_dbcs": installed_server_dbcs,
        "removed_race_continuations": [path.name for path in stale_race_continuations],
        "validation": validation,
    }
    (backup / "install-report.json").write_text(json.dumps(install_report, indent=2) + "\n", encoding="utf-8")
    return install_report


def _validate_runtime_dll(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError(f"runtime extension is not a PE image: {path}")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError(f"runtime extension has no PE signature: {path}")
    machine = struct.unpack_from("<H", data, pe_offset + 4)[0]
    if machine != 0x14C:
        raise ValueError(f"runtime extension is not Win32/x86: machine=0x{machine:04X}")
    for export in (b"WXL_Load\0", b"WXL_Query\0"):
        if export not in data:
            raise ValueError(f"runtime extension is missing export {export[:-1].decode()}")


def install_appearance(slug: str, client: Path) -> dict:
    """Install only the staged retroported appearance payload for fast visual QA.

    This is intentionally narrower than a full race install. It requires the live
    global CharSections/CreatureModelData contract to already match the staged
    build, replaces the compact Patch-R payload transactionally, and updates only
    the derived Mag'har texture entries inside locale Z in place. That avoids
    recopying multi-gigabyte Z archives for a texture-only experiment.
    """
    if slug != "maghar":
        raise NotImplementedError("appearance-only install is currently validated for Mag'har")

    root = _build_root(slug)
    paths = BuildPaths(
        root,
        root / GLOBAL_ARCHIVE_REL,
        root / ASSET_ARCHIVE_REL,
        root / LOCALE_ARCHIVE_REL,
        root / "server" / "dbc",
        root / "build-report.json",
    )
    validation = validate(slug, client, paths)
    storm = Storm(DLL_DEFAULT)
    live_global = client / GLOBAL_ARCHIVE_REL
    live_asset = client / ASSET_ARCHIVE_REL
    live_locale = client / LOCALE_ARCHIVE_REL

    def charsections_signature(archive: Path) -> list[tuple[object, ...]]:
        data = _read_archive_entry(storm, archive, f"{DBC_ROOT}CharSections.dbc")
        table = RawWdbc(data)
        signature: list[tuple[object, ...]] = []
        for row in table.records:
            if _value(row, 1 * 4) != 45:
                continue
            signature.append(
                (
                    _value(row, 2 * 4),
                    _value(row, 3 * 4),
                    _value(row, 7 * 4),
                    _value(row, 8 * 4),
                    _value(row, 9 * 4),
                    *(
                        _string(table.strings, _value(row, field * 4)).decode("utf-8")
                        for field in (4, 5, 6)
                    ),
                )
            )
        return sorted(signature)

    if charsections_signature(live_global) != charsections_signature(paths.global_archive):
        raise RuntimeError(
            "live Race45 CharSections do not match the staged appearance contract; run a full install first"
        )

    stage_handle = storm.open_archive(paths.asset_archive)
    try:
        stage_names = [name for name, *_ in storm.list_files(stage_handle)]
        appearance_names = [
            name for name in stage_names
            if name.casefold().startswith("custom\\maghar\\derived\\native\\")
        ]
        appearance_entries = {name: storm.read(stage_handle, name) for name in appearance_names}
    finally:
        storm.dll.SFileCloseArchive(stage_handle)
    if len(appearance_entries) != 360:
        raise RuntimeError(f"expected 360 staged Mag'har derived textures, found {len(appearance_entries)}")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = client.parent / "3.3.5a - Backups" / f"retroported-races-{slug}-appearance-{timestamp}"
    backup.mkdir(parents=True, exist_ok=True)

    if live_asset.is_file():
        backup_asset = backup / ASSET_ARCHIVE_REL
        backup_asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live_asset, backup_asset)
        if sha256(backup_asset) != sha256(live_asset):
            raise RuntimeError("Patch-R backup hash verification failed; live client was not changed")

    old_locale_entries: dict[str, bytes] = {}
    locale_handle = storm.open_archive(live_locale)
    try:
        for name in appearance_entries:
            try:
                old_locale_entries[name] = storm.read(locale_handle, name)
            except OSError:
                pass
    finally:
        storm.dll.SFileCloseArchive(locale_handle)
    backup_locale_assets = backup / "locale-derived-before.MPQ"
    if old_locale_entries:
        storm.create_archive(backup_locale_assets, old_locale_entries)

    temp_asset = live_asset.with_suffix(live_asset.suffix + ".retroported-next")
    shutil.copy2(paths.asset_archive, temp_asset)
    if sha256(temp_asset) != sha256(paths.asset_archive):
        temp_asset.unlink(missing_ok=True)
        raise RuntimeError("Patch-R staged copy hash verification failed; live client was not changed")
    os.replace(temp_asset, live_asset)

    storm.replace_archive_entries(live_locale, appearance_entries)

    asset_handle = storm.open_archive(live_asset)
    locale_handle = storm.open_archive(live_locale)
    try:
        for name, payload in appearance_entries.items():
            if storm.read(asset_handle, name) != payload:
                raise RuntimeError(f"Patch-R appearance verification failed: {name}")
            if storm.read(locale_handle, name) != payload:
                raise RuntimeError(f"locale appearance verification failed: {name}")
    finally:
        storm.dll.SFileCloseArchive(locale_handle)
        storm.dll.SFileCloseArchive(asset_handle)

    report = {
        "slug": slug,
        "backup": str(backup),
        "appearance_entries": len(appearance_entries),
        "installed_asset_hash": sha256(live_asset),
        "locale_archive_hash": sha256(live_locale),
        "validation": validation,
    }
    (backup / "install-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def install_runtime_extension(client: Path, built_dll: Path = RUNTIME_BUILD_DEFAULT) -> dict:
    _validate_runtime_dll(built_dll)
    live_dll = client / RUNTIME_EXTENSION_DLL
    live_manifest = client / RUNTIME_EXTENSION_MANIFEST
    if not live_dll.is_file() or not live_manifest.is_file():
        raise FileNotFoundError("existing Esteria race runtime extension is incomplete")

    manifest = json.loads(live_manifest.read_text(encoding="utf-8"))
    extension = manifest.get("extension", {})
    if extension.get("id") != "darkfallen-character-select" or extension.get("entry") != live_dll.name:
        raise ValueError("live race runtime manifest does not match the expected extension contract")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "3.3.5a - Backups" / f"retroported-races-runtime-{timestamp}"
    backup_dll = backup / RUNTIME_EXTENSION_DLL
    backup_manifest = backup / RUNTIME_EXTENSION_MANIFEST
    backup_dll.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(live_dll, backup_dll)
    shutil.copy2(live_manifest, backup_manifest)

    live_hash = sha256(live_dll)
    if sha256(backup_dll) != live_hash:
        raise RuntimeError("runtime extension backup hash verification failed; live DLL was not changed")

    temp_dll = live_dll.with_suffix(live_dll.suffix + ".retroported-next")
    shutil.copy2(built_dll, temp_dll)
    if sha256(temp_dll) != sha256(built_dll):
        temp_dll.unlink(missing_ok=True)
        raise RuntimeError("runtime extension staged copy hash verification failed; live DLL was not changed")
    _validate_runtime_dll(temp_dll)
    os.replace(temp_dll, live_dll)

    report = {
        "backup": str(backup),
        "pre_install_hash": live_hash,
        "installed_hash": sha256(live_dll),
        "installed_dll": str(live_dll),
    }
    (backup / "install-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("plan", "build", "validate", "install", "install-appearance", "install-runtime"),
    )
    parser.add_argument("--race", required=True)
    parser.add_argument("--client", type=Path, default=CLIENT_DEFAULT)
    parser.add_argument("--runtime-dll", type=Path, default=RUNTIME_BUILD_DEFAULT)
    args = parser.parse_args()

    if args.command == "plan":
        result = plan(args.race, args.client)
    elif args.command == "build":
        paths = build(args.race, args.client)
        result = {"root": str(paths.root), "report": str(paths.report)}
    elif args.command == "validate":
        result = validate(args.race, args.client)
    elif args.command == "install-appearance":
        result = install_appearance(args.race, args.client)
    elif args.command == "install-runtime":
        result = install_runtime_extension(args.client, args.runtime_dll)
    else:
        result = install(args.race, args.client)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
