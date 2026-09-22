"""Build an additive WDBC/model pack for Vulpera and Alliance Pandaren."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import tempfile
from dataclasses import dataclass
from pathlib import Path

from cars_mount_pack import (
    DLL_DEFAULT,
    Storm,
    WOTLK_MODEL_VERSION,
    Wdbc,
    merge_archive_entries,
    safe_relative,
)


SOURCE_RACES = {"vulpera": 19, "pandaren": 20}
TARGET_RACES = {"vulpera": 20, "pandaren": 18}
RACE_ID_FIELDS = {
    "ChrRaces": 0,
    "CharBaseInfo": 0,
    "CharStartOutfit": 1,
    "CharSections": 0,
    "CharHairGeosets": 1,
    "CharHairTextures": 1,
    "BarberShopStyle": 37,
    "CharacterFacialHairStyles": 0,
    "NameGen": 2,
    "CreatureDisplayInfoExtra": 1,
}
RACE_MASK_FIELDS = {
    "SkillLineAbility": 3,
    "SkillRaceClassInfo": 2,
}
RACE_TABLES = tuple(RACE_ID_FIELDS) + tuple(RACE_MASK_FIELDS)
MODEL_TABLES = ("CreatureDisplayInfo", "CreatureModelData", "ItemDisplayInfo")
RACE_ASSET_ROOTS = ("vulpera", "Pandaren")
RACE_BYTE_LAYOUTS = {
    "ChrRaces": (0, 4),
    "CharBaseInfo": (0, 1),
    "CharStartOutfit": (4, 1),
    "CharSections": (4, 4),
    "CharHairGeosets": (4, 4),
    "CharHairTextures": (4, 4),
    "BarberShopStyle": (37 * 4, 4),
    "CharacterFacialHairStyles": (0, 4),
    "NameGen": (8, 4),
    "CreatureDisplayInfoExtra": (4, 4),
    "SkillLineAbility": (3 * 4, 4),
    "SkillRaceClassInfo": (2 * 4, 4),
}


@dataclass(frozen=True)
class WdbcLayout:
    fields: int
    record_size: int
    race_offset: int
    race_width: int


WDBC_LAYOUTS = {
    "ChrRaces": WdbcLayout(69, 276, *RACE_BYTE_LAYOUTS["ChrRaces"]),
    "CharBaseInfo": WdbcLayout(2, 2, *RACE_BYTE_LAYOUTS["CharBaseInfo"]),
    "CharStartOutfit": WdbcLayout(77, 296, *RACE_BYTE_LAYOUTS["CharStartOutfit"]),
    "CharSections": WdbcLayout(10, 40, *RACE_BYTE_LAYOUTS["CharSections"]),
    "CharHairGeosets": WdbcLayout(6, 24, *RACE_BYTE_LAYOUTS["CharHairGeosets"]),
    "CharHairTextures": WdbcLayout(8, 32, *RACE_BYTE_LAYOUTS["CharHairTextures"]),
    "BarberShopStyle": WdbcLayout(40, 160, *RACE_BYTE_LAYOUTS["BarberShopStyle"]),
    "CharacterFacialHairStyles": WdbcLayout(8, 32, *RACE_BYTE_LAYOUTS["CharacterFacialHairStyles"]),
    "NameGen": WdbcLayout(4, 16, *RACE_BYTE_LAYOUTS["NameGen"]),
    "CreatureDisplayInfoExtra": WdbcLayout(21, 84, *RACE_BYTE_LAYOUTS["CreatureDisplayInfoExtra"]),
    "SkillLineAbility": WdbcLayout(14, 56, *RACE_BYTE_LAYOUTS["SkillLineAbility"]),
    "SkillRaceClassInfo": WdbcLayout(8, 32, *RACE_BYTE_LAYOUTS["SkillRaceClassInfo"]),
    "CreatureDisplayInfo": WdbcLayout(16, 64, 0, 4),
    "CreatureModelData": WdbcLayout(28, 112, 0, 4),
    "ItemDisplayInfo": WdbcLayout(25, 100, 0, 4),
}

STRING_FIELDS = {
    # ChrRaces also carries ClientPrefix (6), ClientFileString (11) and the facial/hair
    # customization strings (65-67). The glue character-create screen reads ClientFileString
    # verbatim, so donor rows must rebase those offsets as well.
    "ChrRaces": (6, 11, 65, 66, 67)
    + tuple(range(14, 30))
    + tuple(range(31, 47))
    + tuple(range(48, 64)),
    "CharSections": (4, 5, 6),
    "BarberShopStyle": tuple(range(2, 18)) + tuple(range(19, 35)),
    "NameGen": (1,),
    "CreatureModelData": (2,),
    "CreatureDisplayInfo": (6, 7, 8),
    # ModelName_1/2 (1, 2), ModelTexture_1/2 (3, 4), InventoryIcon_1/2 (5, 6) and
    # Texture_1..8 (15-22) are all string offsets; unrebased rows point at the wrong pool.
    "ItemDisplayInfo": (1, 2, 3, 4, 5, 6) + tuple(range(15, 23)),
}


class RawWdbc:
    """WDBC reader/writer that preserves packed record bytes verbatim."""

    def __init__(self, data: bytes):
        if len(data) < 20:
            raise ValueError("truncated WDBC header")
        self.header = struct.unpack_from("<4s4I", data)
        magic, self.count, self.fields, self.record_size, self.string_size = self.header
        if magic != b"WDBC":
            raise ValueError("unsupported WDBC magic")
        records_end = 20 + self.count * self.record_size
        expected = records_end + self.string_size
        if len(data) != expected:
            raise ValueError(f"invalid WDBC size: {len(data)} != {expected}")
        self.records = tuple(
            data[20 + index * self.record_size : 20 + (index + 1) * self.record_size]
            for index in range(self.count)
        )
        self.strings = data[records_end:]

    @staticmethod
    def _value(record: bytes, offset: int, width: int) -> int:
        return int.from_bytes(record[offset : offset + width], "little")

    @staticmethod
    def _replace(record: bytes, offset: int, width: int, value: int) -> bytes:
        if value < 0 or value >= 1 << (width * 8):
            raise ValueError(f"value {value} does not fit in {width} bytes")
        result = bytearray(record)
        result[offset : offset + width] = value.to_bytes(width, "little")
        return bytes(result)

    def remap_race_records(
        self,
        table_name: str,
        source_race: int,
        target_race: int,
        records: tuple[bytes, ...] | list[bytes] | None = None,
    ) -> list[bytes]:
        layout = WDBC_LAYOUTS[table_name]
        selected = self.records if records is None else tuple(records)
        result = []
        for record in selected:
            if len(record) != self.record_size:
                raise ValueError(f"{table_name} record has invalid length")
            if self._value(record, layout.race_offset, layout.race_width) == source_race:
                record = self._replace(record, layout.race_offset, layout.race_width, target_race)
            result.append(record)
        return result

    def build(
        self,
        records: tuple[bytes, ...] | list[bytes],
        strings: bytes | None = None,
    ) -> bytes:
        records = tuple(records)
        if any(len(record) != self.record_size for record in records):
            raise ValueError("record length does not match donor WDBC")
        string_pool = self.strings if strings is None else strings
        header = struct.pack(
            "<4s4I",
            self.header[0],
            len(records),
            self.fields,
            self.record_size,
            len(string_pool),
        )
        return header + b"".join(records) + string_pool


@dataclass(frozen=True)
class AssetReport:
    asset_paths: tuple[str, ...]
    sha256: dict[str, str]
    file_counts: dict[str, int]
    entries: dict[str, bytes]


@dataclass(frozen=True)
class PackReport:
    merged_dbc: dict[str, bytes]
    asset_paths: tuple[str, ...]
    collisions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    sha256: dict[str, str]
    file_counts: dict[str, int]
    staged_root: str


def _race_field(table_name: str) -> int:
    try:
        return RACE_ID_FIELDS[table_name]
    except KeyError as exc:
        raise ValueError(f"unknown race-ID table: {table_name}") from exc


def _check_unique_chr_races(rows: list[list[int]]) -> None:
    row_ids = [row[0] for row in rows]
    if len(row_ids) != len(set(row_ids)):
        raise ValueError("duplicate row ID in ChrRaces")


def remap_race_rows(
    table_name: str,
    rows: list[list[int]],
    source_race: int,
    target_race: int,
) -> list[list[int]]:
    """Return rows with only the configured race field changed."""

    field = _race_field(table_name)
    if any(field >= len(row) for row in rows):
        raise ValueError(f"{table_name} race field {field} is outside a row")
    result = [row.copy() for row in rows]
    for row in result:
        if row[field] == source_race:
            row[field] = target_race
    if table_name == "ChrRaces":
        _check_unique_chr_races(result)
    return result


def remap_race_masks(value: int, source_mask: int, target_mask: int) -> int:
    """Replace source race bits while retaining every unrelated bit."""

    return ((value & 0xFFFFFFFF) & ~source_mask) | target_mask


SOURCE_TO_TARGET = {19: 20, 20: 18}
TARGET_RACES = frozenset(SOURCE_TO_TARGET.values())
SOURCE_RACE_MASK = sum(1 << race for race in SOURCE_TO_TARGET)


def _field_value(record: bytes, field: int) -> int:
    return int.from_bytes(record[field * 4 : field * 4 + 4], "little")


def _replace_field(record: bytes, field: int, value: int) -> bytes:
    result = bytearray(record)
    result[field * 4 : field * 4 + 4] = value.to_bytes(4, "little")
    return bytes(result)


def _transform_race_record(table_name: str, record: bytes) -> bytes | None:
    layout = WDBC_LAYOUTS[table_name]
    source_race = RawWdbc._value(record, layout.race_offset, layout.race_width)
    target_race = SOURCE_TO_TARGET.get(source_race)
    if target_race is None:
        return None
    transformed = RawWdbc._replace(record, layout.race_offset, layout.race_width, target_race)
    if table_name == "ChrRaces":
        values = bytearray(transformed)
        values[4:8] = (int.from_bytes(values[4:8], "little") & ~1).to_bytes(4, "little")
        values[8:12] = (1 if target_race == 18 else 2).to_bytes(4, "little")
        values[28:32] = (7 if target_race == 18 else 1).to_bytes(4, "little")
        values[52:56] = (0 if target_race == 18 else 1).to_bytes(4, "little")
        transformed = bytes(values)
    return transformed


def _rebase_string_records(
    table_name: str,
    records: list[bytes],
    donor_strings: bytes,
    base_string_size: int,
) -> tuple[list[bytes], bytes]:
    fields = STRING_FIELDS.get(table_name, ())
    if not fields:
        return records, donor_strings
    rebased: list[bytes] = []
    for record in records:
        value = bytearray(record)
        for field in fields:
            offset = field * 4
            string_offset = int.from_bytes(value[offset : offset + 4], "little")
            if not string_offset:
                continue
            if string_offset >= len(donor_strings):
                raise ValueError(f"{table_name} string offset outside donor pool: {string_offset}")
            value[offset : offset + 4] = (base_string_size + string_offset).to_bytes(4, "little")
        rebased.append(bytes(value))
    return rebased, donor_strings


def merge_direct_dbc(table_name: str, base: RawWdbc, donor: RawWdbc) -> bytes:
    """Merge target race rows into a complete WDBC table, preserving base rows."""

    expected = WDBC_LAYOUTS[table_name]
    if (base.fields, base.record_size) != (expected.fields, expected.record_size):
        raise ValueError(f"base WDBC layout mismatch for {table_name}")
    if (donor.fields, donor.record_size) != (expected.fields, expected.record_size):
        raise ValueError(f"donor WDBC layout mismatch for {table_name}")

    if table_name in RACE_ID_FIELDS:
        selected = [
            transformed
            for record in donor.records
            if (transformed := _transform_race_record(table_name, record)) is not None
        ]
        if table_name == "CharBaseInfo":
            class_ids = {
                record[1]
                for record in (*base.records, *selected)
            }
            selected = [record for record in selected if record[0] not in TARGET_RACES]
            selected.extend(
                bytes((race, class_id))
                for race in sorted(TARGET_RACES)
                for class_id in sorted(class_ids)
            )
        if not selected:
            return base.build(base.records, base.strings)
        selected, donor_strings = _rebase_string_records(
            table_name, selected, donor.strings, len(base.strings)
        )
        records = [
            record
            for record in base.records
            if RawWdbc._value(
                record,
                expected.race_offset,
                expected.race_width,
            ) not in TARGET_RACES
        ]
        keyed_rows = table_name not in {"CharBaseInfo", "CharacterFacialHairStyles"}
        existing_ids = {record[:4] for record in records} if keyed_rows else set()
        next_id = max((int.from_bytes(row[:4], "little") for row in records), default=0) + 1
        for record in selected:
            if keyed_rows and record[:4] in existing_ids:
                if table_name == "ChrRaces":
                    raise ValueError(f"{table_name} target row collides with unrelated base row")
                while next_id.to_bytes(4, "little") in existing_ids:
                    next_id += 1
                record = _replace_field(record, 0, next_id)
                next_id += 1
            if keyed_rows:
                existing_ids.add(record[:4])
            records.append(record)
        return base.build(records, base.strings + donor_strings)

    if table_name in RACE_MASK_FIELDS:
        records = list(base.records)
        existing_ids = {record[:4]: index for index, record in enumerate(records)}
        for donor_record in donor.records:
            donor_mask = RawWdbc._value(
                donor_record,
                WDBC_LAYOUTS[table_name].race_offset,
                WDBC_LAYOUTS[table_name].race_width,
            )
            source_bits = donor_mask & SOURCE_RACE_MASK
            if not source_bits:
                continue
            mapped_bits = 0
            if source_bits & (1 << 19):
                mapped_bits |= 1 << 20
            if source_bits & (1 << 20):
                mapped_bits |= 1 << 18
            row_id = donor_record[:4]
            index = existing_ids.get(row_id)
            if index is None:
                records.append(RawWdbc._replace(
                    donor_record,
                    WDBC_LAYOUTS[table_name].race_offset,
                    WDBC_LAYOUTS[table_name].race_width,
                    (donor_mask & ~SOURCE_RACE_MASK) | mapped_bits,
                ))
                existing_ids[row_id] = len(records) - 1
                continue
            current = records[index]
            current_mask = RawWdbc._value(
                current,
                WDBC_LAYOUTS[table_name].race_offset,
                WDBC_LAYOUTS[table_name].race_width,
            )
            records[index] = RawWdbc._replace(
                current,
                WDBC_LAYOUTS[table_name].race_offset,
                WDBC_LAYOUTS[table_name].race_width,
                ((current_mask | donor_mask) & ~SOURCE_RACE_MASK) | mapped_bits,
            )
        return base.build(records, base.strings)

    raise ValueError(f"unsupported direct race DBC table: {table_name}")


def _normalise_model_strings(table_name: str, records: list[bytes], strings: bytes) -> bytes:
    if table_name != "CreatureModelData":
        return strings
    result = bytearray(strings)
    for record in records:
        string_offset = _field_value(record, 2)
        if not string_offset:
            continue
        end = result.find(bytes([0]), string_offset)
        if end < 0:
            raise ValueError("CreatureModelData model path is unterminated")
        value = bytes(result[string_offset:end])
        if value.lower().endswith(b".mdx"):
            replacement = value[:-4] + b".m2\0\0"
            result[string_offset : end + 1] = replacement
    return bytes(result)


def merge_dbc_rows_by_id(
    table_name: str,
    base: RawWdbc,
    donor: RawWdbc,
    row_ids: set[int],
) -> bytes:
    """Merge selected donor rows by primary ID into an actual WDBC table."""

    expected = WDBC_LAYOUTS[table_name]
    if (base.fields, base.record_size) != (expected.fields, expected.record_size):
        raise ValueError(f"base WDBC layout mismatch for {table_name}")
    selected = [record for record in donor.records if int.from_bytes(record[:4], "little") in row_ids]
    if not selected:
        return base.build(base.records, base.strings)
    donor_strings = _normalise_model_strings(table_name, selected, donor.strings)
    selected, donor_strings = _rebase_string_records(
        table_name, selected, donor_strings, len(base.strings)
    )
    records = list(base.records)
    indexes = {record[:4]: index for index, record in enumerate(records)}
    for record in selected:
        row_id = record[:4]
        index = indexes.get(row_id)
        if index is None:
            indexes[row_id] = len(records)
            records.append(record)
        else:
            records[index] = record
    return base.build(records, base.strings + donor_strings)


def patch_character_info(data: bytes) -> bytes:
    """Add ordinal 16/17 race metadata to the existing Glue race table."""

    text = data.decode("utf-8")
    if "glueString = \"PANDAREN\"" in text and "glueString = \"VULPERA\"" in text:
        return data

    info_anchor = "Races_Informations[14] = brokenInfo\n"
    if info_anchor in text:
        insert_at = text.index(info_anchor) + len(info_anchor)
    else:
        fallback = re.search(r"^local (?:brokenInfo|goblinInfo) = .*\n", text, re.MULTILINE)
        if fallback is None:
            return data
        insert_at = fallback.start()
    info_text = (
        'Races_Informations[16] = { Name = "Pandaren", Description = "Disciplined and resilient people of the mists." }\n'
        'Races_Informations[17] = { Name = "Vulpera", Description = "Resourceful desert survivors and clever allies." }\n'
    )
    text = text[:insert_at] + info_text + text[insert_at:]

    file_string_anchor = "    MAGHAR = Races_Informations[15],\n"
    if file_string_anchor in text:
        text = text.replace(
            file_string_anchor,
            file_string_anchor
            + "    PANDAREN = Races_Informations[16],\n"
            + "    VULPERA = Races_Informations[17],\n",
            1,
        )

    race_data_match = re.search(r'^    \[15\] = \{ glueString = .*\n', text, re.MULTILINE)
    if race_data_match is None:
        raise ValueError("CharacterInfo.lua missing RACE_DATA anchor")
    race_data_text = (
        '    [16] = { glueString = "PANDAREN", faction = "Alliance" },\n'
        '    [17] = { glueString = "VULPERA",  faction = "Horde" },\n'
    )
    insert_at = race_data_match.end()
    text = text[:insert_at] + race_data_text + text[insert_at:]

    alliance_anchor = "local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7}"
    horde_anchor = "local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15}"
    if alliance_anchor not in text or horde_anchor not in text:
        raise ValueError("CharacterInfo.lua missing faction race lists")
    text = text.replace(alliance_anchor, "local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16}", 1)
    text = text.replace(horde_anchor, "local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17}", 1)

    localization_match = re.search(r'^    \[15\] = \{token = .*\n', text, re.MULTILINE)
    if localization_match is None:
        raise ValueError("CharacterInfo.lua missing race localization anchor")
    localization_text = (
        '    [16] = {token = "PANDAREN", name = "Pandaren", spells = {}},\n'
        '    [17] = {token = "VULPERA", name = "Vulpera", spells = {}},\n'
    )
    insert_at = localization_match.end()
    text = text[:insert_at] + localization_text + text[insert_at:]
    return text.encode("utf-8")


def patch_glue_parent(data: bytes) -> bytes:
    """Repair separators, register custom races, and guard the glue ambience call."""

    text = data.decode("utf-8")
    text = text.replace(
        '["HIGHELF"] = true\n        ["PANDAREN"]',
        '["HIGHELF"] = true,\n        ["PANDAREN"]',
    )
    text = text.replace(
        '["SETHRAK"] = true\n        ["VULPERA"]',
        '["SETHRAK"] = true,\n        ["VULPERA"]',
    )
    if 'GlueAmbienceTracks["BROKEN"]' not in text:
        anchor = 'GlueAmbienceTracks["SETHRAK"] = GlueAmbienceTracks["ORC"];\n'
        if anchor not in text:
            anchor = 'GlueAmbienceTracks["SETHRAK"] = "GlueScreenOrcTroll";\n'
        if anchor in text:
            text = text.replace(
                anchor,
                anchor + 'GlueAmbienceTracks["BROKEN"] = GlueAmbienceTracks["ORC"];\n',
                1,
            )
    # SetBackgroundModel(model, race) builds "UI_<race>\\UI_<race>.m2" unless the race is
    # listed in these tables. Broken was missing, so the create screen tried to load a
    # non-existent UI_BROKEN model (black scene plus missing-model placeholders).
    # A table entry needs a trailing comma before the next entry; adding one without the
    # comma produced "']' expected" at load time.
    text = text.replace(
        '        ["VULPERA"] = true\n        ["BROKEN"] = true,',
        '        ["VULPERA"] = true,\n        ["BROKEN"] = true,',
    )
    text = text.replace('        ["VULPERA"] = true\n', '        ["VULPERA"] = true,\n')
    horde_anchor = '        ["VULPERA"] = true,\n'
    if horde_anchor in text and '["BROKEN"] = true' not in text:
        text = text.replace(horde_anchor, horde_anchor + '        ["BROKEN"] = true,\n', 1)
    # An unknown race would pass a nil track to PlayGlueAmbience, raising a Lua error that
    # leaves the glue screen unusable until relog.
    ambience_original = "    PlayGlueAmbience(GlueAmbienceTracks[nameupper], 4.0);\n"
    ambience_replacement = (
        "    local ambienceTrack = GlueAmbienceTracks[nameupper];\n"
        "    if ( ambienceTrack ) then\n"
        "        PlayGlueAmbience(ambienceTrack, 4.0);\n"
        "    end\n"
    )
    text = text.replace(ambience_original, ambience_replacement)
    return text.encode("utf-8")


def patch_character_create(data: bytes) -> bytes:
    """Keep Broken portrait coordinates distinct and make race icon lookups nil-safe."""

    text = data.decode("utf-8")
    text = re.sub(
        r'(\["BROKEN_MALE"\]\s*=\s*)\{[^}]+\}',
        r'\1{0.750, 0.875, 0.5, 0.625}',
        text,
        count=1,
    )
    text = re.sub(
        r'(\["BROKEN_FEMALE"\]\s*=\s*)\{[^}]+\}',
        r'\1{0.750, 0.875, 0.625, 0.75}',
        text,
        count=1,
    )
    # Any race the glue screen reports without an atlas entry used to raise
    # "attempt to index local 'coords' (a nil value)" and abort the whole enumeration,
    # which hid every later race button. Fall back to the human portrait instead.
    fallback = ' or RACE_ICON_TCOORDS["HUMAN_"..(gender or "MALE")]'
    for original in (
        "local coords = RACE_ICON_TCOORDS[raceKey];",
        "coords = RACE_ICON_TCOORDS[raceKey];",
    ):
        text = text.replace(original, original[: -len(";")] + fallback + ";")
    # SetBackgroundModel expects a race key (e.g. "HUMAN"), not a model path: it builds
    # "UI_<race>\\UI_<race>.m2" from it and looks the key up in GlueAmbienceTracks. Custom
    # races get no usable key from the client, which left the create scene black.
    if "RACE_BACKGROUND_KEYS" not in text and "GetCreateBackgroundModel" in text:
        background_pattern = re.compile(
            r"    local backgroundFilename = GetCreateBackgroundModel\(\);\n"
            r"(?:    .*\n)*?"
            r"    SetBackgroundModel\(CharacterCreate, backgroundFilename\);\n"
        )
        background_replacement = (
            "    local backgroundFilename = GetCreateBackgroundModel();\n"
            "    local selectedRaceButton = "
            "_G[\"CharacterCreateRaceButton\"..(CharacterCreate.selectedRace or 0)];\n"
            "    local selectedRaceKey = selectedRaceButton and selectedRaceButton.raceFileString;\n"
            "    local RACE_BACKGROUND_KEYS = {\n"
            "        [\"BROKEN\"] = \"ORC\",\n"
            "        [\"BROKEN_ALLIANCE\"] = \"HUMAN\",\n"
            "        [\"BROKEN_HORDE\"] = \"ORC\",\n"
            "        [\"PANDAREN\"] = \"HUMAN\",\n"
            "        [\"PANDAREN_ALLIANCE\"] = \"HUMAN\",\n"
            "        [\"PANDAREN_HORDE\"] = \"ORC\",\n"
            "        [\"VULPERA\"] = \"ORC\",\n"
            "        [\"SETHRAK\"] = \"ORC\",\n"
            "        [\"HIGHELF\"] = \"HUMAN\",\n"
            "        [\"MAGHAR\"] = \"ORC\",\n"
            "    };\n"
            "    local mappedBackground = selectedRaceKey and "
            "RACE_BACKGROUND_KEYS[strupper(selectedRaceKey)];\n"
            "    if ( mappedBackground ) then\n"
            "        backgroundFilename = mappedBackground;\n"
            "    end\n"
            "    if ( not backgroundFilename or backgroundFilename == \"\" ) then\n"
            "        if ( faction == \"Alliance\" ) then\n"
            "            backgroundFilename = \"HUMAN\";\n"
            "        else\n"
            "            backgroundFilename = \"ORC\";\n"
            "        end\n"
            "    end\n"
            "    SetBackgroundModel(CharacterCreate, backgroundFilename);\n"
        )
        text, replaced = background_pattern.subn(background_replacement, text, count=1)
        if not replaced:
            raise ValueError("CharacterCreate.lua background call not found")
    return text.encode("utf-8")


def _model_root(model_root: Path) -> Path:
    character = model_root / "Character"
    if character.is_dir():
        return character
    if model_root.name.casefold() == "character" and model_root.is_dir():
        return model_root
    raise FileNotFoundError(f"Character asset root not found under {model_root}")


def _find_casefold_child(root: Path, name: str) -> Path:
    matches = [child for child in root.iterdir() if child.name.casefold() == name.casefold()]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {name} directory under {root}")
    return matches[0]


def _asset_name(character_root: Path, path: Path) -> str:
    relative = path.relative_to(character_root).as_posix().replace("/", "\\")
    return str(safe_relative(f"Character\\{relative}")) .replace("/", "\\")


def collect_race_assets(model_root: Path) -> AssetReport:
    """Validate and collect both genders of each required race asset tree."""

    character_root = _model_root(model_root)
    entries: dict[str, bytes] = {}
    digests: dict[str, str] = {}
    file_counts: dict[str, int] = {}
    for race in RACE_ASSET_ROOTS:
        race_root = _find_casefold_child(character_root, race)
        files = sorted((path for path in race_root.rglob("*") if path.is_file()), key=lambda path: str(path).casefold())
        if not files:
            raise ValueError(f"missing assets under Character\\{race}")
        for path in files:
            if path.suffix.casefold() == ".mdx":
                raise ValueError(f"unsupported .mdx asset: {path}")
        for gender in ("male", "female"):
            gender_root = _find_casefold_child(race_root, gender)
            gender_files = [path for path in files if gender_root in path.parents]
            suffixes = {path.suffix.casefold() for path in gender_files}
            missing = [suffix for suffix in (".m2", ".skin", ".anim") if suffix not in suffixes]
            if missing:
                raise ValueError(f"missing {race} {gender} asset sets: {', '.join(missing)}")
            for path in gender_files:
                if path.suffix.casefold() == ".m2":
                    payload = path.read_bytes()
                    if len(payload) < 8 or payload[:4] not in (b"MD20", b"MD21"):
                        raise ValueError(f"invalid M2 header: {path}")
                    version = struct.unpack_from("<I", payload, 4)[0]
                    if version != WOTLK_MODEL_VERSION:
                        raise ValueError(f"non-WotLK M2 model: {path} ({version})")
        file_counts[race.casefold()] = len(files)
        for path in files:
            name = _asset_name(character_root, path)
            payload = path.read_bytes()
            prior = entries.get(name)
            if prior is not None and prior != payload:
                raise ValueError(f"asset path collision with different bytes: {name}")
            entries[name] = payload
            digests[name] = hashlib.sha256(payload).hexdigest()
    return AssetReport(tuple(sorted(entries)), digests, file_counts, entries)


def _dbc_directory(dbc_root: Path) -> Path:
    nested = dbc_root / "DBFilesClient"
    return nested if nested.is_dir() else dbc_root


def _load_donor_wdbcs(dbc_root: Path) -> dict[str, RawWdbc]:
    directory = _dbc_directory(dbc_root)
    loaded: dict[str, RawWdbc] = {}
    errors: list[str] = []
    for table_name in RACE_TABLES + MODEL_TABLES:
        path = directory / f"{table_name}.dbc"
        if not path.is_file():
            errors.append(f"missing donor DBC: {path}")
            continue
        try:
            data = path.read_bytes()
            table = RawWdbc(data)
        except (OSError, ValueError, struct.error) as exc:
            errors.append(f"donor WDBC header mismatch for {table_name}: {exc}")
            continue
        expected = WDBC_LAYOUTS[table_name]
        if (table.fields, table.record_size) != (expected.fields, expected.record_size):
            errors.append(
                f"donor WDBC header mismatch for {table_name}: "
                f"got fields={table.fields} record_size={table.record_size}, "
                f"expected fields={expected.fields} record_size={expected.record_size}"
            )
            continue
        if expected.race_offset + expected.race_width > table.record_size:
            errors.append(f"donor race byte range is outside {table_name} records")
            continue
        if expected.record_size == expected.fields * 4:
            try:
                Wdbc(data)
            except ValueError as exc:
                errors.append(f"donor WDBC field framing mismatch for {table_name}: {exc}")
                continue
        loaded[table_name] = table
    if errors:
        raise ValueError("; ".join(errors))
    return loaded


def _read_directory_entries(root: Path) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    for path in sorted((path for path in root.rglob("*") if path.is_file()), key=lambda item: str(item).casefold()):
        relative = path.relative_to(root).as_posix().replace("/", "\\")
        name = str(safe_relative(relative)).replace("/", "\\")
        entries = merge_archive_entries(entries, {name: path.read_bytes()})
    return entries


def _read_patch_b_entries(patch_b_root: Path) -> dict[str, bytes]:
    if patch_b_root.is_dir():
        return _read_directory_entries(patch_b_root)
    if not patch_b_root.is_file():
        raise FileNotFoundError(patch_b_root)
    if not DLL_DEFAULT.is_file():
        raise FileNotFoundError(f"StormLib not found for Patch-B archive: {DLL_DEFAULT}")
    storm = Storm(DLL_DEFAULT)
    archive = storm.open_archive(patch_b_root)
    try:
        entries: dict[str, bytes] = {}
        for name, *_ in storm.list_files(archive):
            normalized = name.casefold()
            if (
                normalized.startswith("dbfilesclient\\") and normalized.endswith(".dbc")
            ) or normalized == "interface\\gluexml\\characterinfo.lua":
                entries = merge_archive_entries(entries, {name: storm.read(archive, name)})
        return entries
    finally:
        storm.dll.SFileCloseArchive(archive)


def _stage_directory(output_root: Path, entries: dict[str, bytes]) -> None:
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.tmp-", dir=output_root.parent))
    try:
        for name, payload in sorted(entries.items(), key=lambda item: item[0].casefold()):
            destination = temporary_root / safe_relative(name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
        os.replace(temporary_root, output_root)
    except BaseException:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise


def _stage_archive_updates(output_root: Path, source_path: Path, updates: dict[str, bytes]) -> Path:
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    archive_name = f"{source_path.stem}-vulpera-pandaren.MPQ"
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.tmp-", dir=output_root.parent))
    temporary_archive = temporary_root / archive_name
    try:
        shutil.copy2(source_path, temporary_archive)
        Storm(DLL_DEFAULT).replace_archive_entries(temporary_archive, updates)
        os.replace(temporary_root, output_root)
    except BaseException:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise
    return output_root / archive_name


def _find_archive_entry(entries: dict[str, bytes], relative_name: str) -> tuple[str, bytes] | None:
    matches = [
        (name, payload)
        for name, payload in entries.items()
        if name.casefold() == relative_name.casefold()
    ]
    if len(matches) > 1:
        raise ValueError(f"duplicate archive path variants: {relative_name}")
    return matches[0] if matches else None


def _start_outfit_display_ids(records: tuple[bytes, ...] | list[bytes]) -> set[int]:
    ids: set[int] = set()
    for record in records:
        race = RawWdbc._value(record, 4, 1)
        if race not in TARGET_RACES:
            continue
        ids.update(
            int.from_bytes(record[offset : offset + 4], "little")
            for offset in range(104, 200, 4)
        )
    ids.discard(0)
    return ids


def _merge_actual_dbc_entries(
    source_entries: dict[str, bytes],
    donor_tables: dict[str, RawWdbc],
) -> dict[str, bytes]:
    updates: dict[str, bytes] = {}
    for table_name in RACE_TABLES:
        entry = _find_archive_entry(source_entries, f"DBFilesClient\\{table_name}.dbc")
        if entry is None:
            continue
        archive_name, payload = entry
        updates[archive_name] = merge_direct_dbc(
            table_name,
            RawWdbc(payload),
            donor_tables[table_name],
        )

    chr_entry = _find_archive_entry(source_entries, "DBFilesClient\\ChrRaces.dbc")
    display_entry = _find_archive_entry(source_entries, "DBFilesClient\\CreatureDisplayInfo.dbc")
    model_entry = _find_archive_entry(source_entries, "DBFilesClient\\CreatureModelData.dbc")
    if display_entry is not None and model_entry is not None:
        if chr_entry is not None:
            chr_payload = updates.get(chr_entry[0], chr_entry[1])
            chr_records = RawWdbc(chr_payload).records
        else:
            chr_records = tuple(
                transformed
                for record in donor_tables["ChrRaces"].records
                if (transformed := _transform_race_record("ChrRaces", record)) is not None
            )
        display_ids = {
            int.from_bytes(record[offset : offset + 4], "little")
            for record in chr_records
            if int.from_bytes(record[:4], "little") in TARGET_RACES
            for offset in (16, 20)
        }
        donor_display = donor_tables["CreatureDisplayInfo"]
        display_rows = {
            int.from_bytes(record[:4], "little"): record
            for record in donor_display.records
            if int.from_bytes(record[:4], "little") in display_ids
        }
        updates[display_entry[0]] = merge_dbc_rows_by_id(
            "CreatureDisplayInfo",
            RawWdbc(display_entry[1]),
            donor_display,
            display_ids,
        )
        model_ids = {
            int.from_bytes(record[4:8], "little")
            for record in display_rows.values()
        }
        updates[model_entry[0]] = merge_dbc_rows_by_id(
            "CreatureModelData",
            RawWdbc(model_entry[1]),
            donor_tables["CreatureModelData"],
            model_ids,
        )

    outfit_entry = _find_archive_entry(source_entries, "DBFilesClient\\CharStartOutfit.dbc")
    item_entry = _find_archive_entry(source_entries, "DBFilesClient\\ItemDisplayInfo.dbc")
    if item_entry is not None:
        if outfit_entry is not None:
            outfit_payload = updates.get(outfit_entry[0], outfit_entry[1])
            outfit_records = RawWdbc(outfit_payload).records
        else:
            outfit_records = tuple(
                transformed
                for record in donor_tables["CharStartOutfit"].records
                if (transformed := _transform_race_record("CharStartOutfit", record)) is not None
            )
        item_ids = _start_outfit_display_ids(outfit_records)
        updates[item_entry[0]] = merge_dbc_rows_by_id(
            "ItemDisplayInfo",
            RawWdbc(item_entry[1]),
            donor_tables["ItemDisplayInfo"],
            item_ids,
        )
    return updates


def build_race_pack(
    dbc_root: Path,
    model_root: Path,
    patch_root: Path,
    output_root: Path,
    include_assets: bool = True,
) -> PackReport:
    """Validate donors, stitch actual DBCs, and stage a complete client archive."""

    dbc_root = Path(dbc_root)
    model_root = Path(model_root)
    patch_root = Path(patch_root)
    output_root = Path(output_root)
    destination_path = output_root.resolve()
    for source_name, source_root in (
        ("DBC donor", dbc_root),
        ("model donor", model_root),
        ("Patch source", patch_root),
    ):
        source_path = source_root.resolve()
        if (
            source_path == destination_path
            or source_path in destination_path.parents
            or destination_path in source_path.parents
        ):
            raise ValueError(f"{source_name} and output paths must not overlap")
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    tables = _load_donor_wdbcs(dbc_root)
    assets = collect_race_assets(model_root) if include_assets else AssetReport((), {}, {}, {})
    source_entries = _read_patch_b_entries(patch_root)
    merged_dbc = _merge_actual_dbc_entries(source_entries, tables)
    ui_updates = {
        name: (
            patch_character_info(payload)
            if name.casefold() == "interface\\gluexml\\characterinfo.lua"
            else patch_glue_parent(payload)
            if name.casefold() == "interface\\gluexml\\glueparent.lua"
            else patch_character_create(payload)
        )
        for name, payload in source_entries.items()
        if name.casefold() in {
            "interface\\gluexml\\characterinfo.lua",
            "interface\\gluexml\\glueparent.lua",
            "interface\\gluexml\\charactercreate.lua",
        }
    }
    if patch_root.is_dir():
        merged = dict(source_entries)
        merged.update(merged_dbc)
        merged.update(ui_updates)
        collisions = tuple(sorted(
            name
            for name, payload in assets.entries.items()
            if (prior := _find_archive_entry(source_entries, name)) is not None and prior[1] == payload
        ))
        merged = merge_archive_entries(merged, assets.entries)
        _stage_directory(output_root, merged)
        staged_name = str(output_root)
    else:
        storm = Storm(DLL_DEFAULT)
        archive = storm.open_archive(patch_root)
        try:
            existing_names = {
                name.casefold(): name
                for name, *_ in storm.list_files(archive)
            }
            updates = dict(merged_dbc)
            updates.update(ui_updates)
            collisions_list: list[str] = []
            for name, payload in assets.entries.items():
                existing = existing_names.get(name.casefold())
                if existing is None:
                    updates[name] = payload
                    continue
                if storm.read(archive, existing) != payload:
                    raise ValueError(f"archive path collision with different bytes: {name} vs {existing}")
                collisions_list.append(name)
            collisions = tuple(sorted(collisions_list))
        finally:
            storm.dll.SFileCloseArchive(archive)
        staged_name = str(_stage_archive_updates(output_root, patch_root, updates))
    return PackReport(
        merged_dbc=merged_dbc,
        asset_paths=assets.asset_paths,
        collisions=collisions,
        missing_requirements=(),
        sha256=assets.sha256,
        file_counts=assets.file_counts,
        staged_root=staged_name,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dbc-root",
        type=Path,
        default=Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient"),
    )
    parser.add_argument(
        "--model-root",
        type=Path,
        default=Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq"),
    )
    parser.add_argument(
        "--patch-root",
        "--patch-b-root",
        dest="patch_root",
        type=Path,
        default=Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\PATCH-A.MPQ"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(
            r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Staging\PATCH-A-vulpera-pandaren"
        ),
    )
    parser.add_argument("--no-assets", action="store_true")
    args = parser.parse_args()
    report = build_race_pack(
        args.dbc_root,
        args.model_root,
        args.patch_root,
        args.output_root,
        include_assets=not args.no_assets,
    )
    print(
        json.dumps(
            {
                "staged_root": report.staged_root,
                "merged_dbc": list(report.merged_dbc),
                "assets": len(report.asset_paths),
                "file_counts": report.file_counts,
                "collisions": list(report.collisions),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
