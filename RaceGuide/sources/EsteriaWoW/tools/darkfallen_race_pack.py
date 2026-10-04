"""Build an additive Darkfallen race pack from the active WotLK MPQs."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

from cars_mount_pack import DLL_DEFAULT, Storm, Wdbc, build_wdbc
from derive_playable_race_portraits import CROP_BOX, decode_source_face, encode_portrait, validate_portrait
from playable_race_pack import RACE_ID_FIELDS, RACE_MASK_FIELDS, RawWdbc, STRING_FIELDS, WDBC_LAYOUTS


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "NewModels" / "_Other" / "PlayableDarkfallen" / "Darkfallen"
DARKFALLEN_MASK = 0x80000000
DARKFALLEN_SOURCE_RACES = {43: 13, 44: 10}
DARKFALLEN_RACE_IDS = (43, 44)
# The Horde race gets its own client-file string: the client derives both the
# character-select backdrop name (Wow.exe GetSelectBackgroundModel -> ChrRaces field 11)
# and the TemporaryPortrait-<Sex>-<FileString>.blp name from it, so a distinct string is
# what lets the two factions have different backdrops and different portrait art.
DARKFALLEN_FILE_STRINGS = {43: "Darkfallen", 44: "DarkfallenHorde"}
DARKFALLEN_MODEL_IDS = {"male": 3658, "female": 3659}
DARKFALLEN_DISPLAY_IDS = {"male": 60028, "female": 60029}
DARKFALLEN_MODEL_SOURCES = {"male": 3638, "female": 3639}
DARKFALLEN_DISPLAY_SOURCES = {"male": 60012, "female": 60013}
DARKFALLEN_HAIR_STYLE_IDS = {0: frozenset(range(9)), 1: frozenset(range(10))}
DARKFALLEN_BLOOD_ELF_APPEARANCE_TABLES = {
    "BarberShopStyle",
    "CharacterFacialHairStyles",
    "CharHairGeosets",
    "CharHairTextures",
    "CharSections",
}
ARCHIVE_NAME = "patch-Z.MPQ"
LOCALE_ARCHIVE_NAME = "patch-enUS-Z.MPQ"
DARKFALLEN_MALE_PATH = "Character\\Darkfallen\\Male"
DARKFALLEN_FEMALE_PATH = "Character\\Darkfallen\\Female"
GLUE_ROOT = "Interface\\GlueXML\\"
PORTRAIT_ROOT = "Interface\\Glues\\CharacterCreate\\"
# The character-select list and the paper-doll portrait load their image from
# Interface\CharacterFrame\TemporaryPortrait-<Sex>-<ClientFileString>.blp, which is why
# every race pack for this client ships that pair next to its creation-screen icons.
CHARACTER_FRAME_ROOT = "Interface\\CharacterFrame\\"
PORTRAIT_SOURCES = {
    "male": "Male\\DarkfallenMaleFaceLower00_00.blp",
    "female": "Female\\DarkfallenFemaleFaceLower00_00.blp",
}
# (fileString, gender) portrait pairs, with the Horde art mirrored: the supplied Horde
# portraits face the opposite way to the Alliance ones.
FRAME_PORTRAIT_KEYS = (
    ("Darkfallen", "male", False),
    ("Darkfallen", "female", False),
    ("DarkfallenHorde", "male", True),
    ("DarkfallenHorde", "female", True),
)
# The supplied face sheets are 256x128 head textures with the face in the upper-left
# square, unlike the Pandaren/Vulpera 512x256 sheets CROP_BOX was tuned for.
PORTRAIT_CROP_BOX = (0, 0, 116, 120)


# --- Darkfallen racial spells ------------------------------------------------
#
# Spell.dbc is rewritten whole, the same way the race tables are: donor rows are
# cloned, the Darkfallen fields/strings replace the ones the stock spell used, and
# every existing row keeps its text because the string pool is rebuilt.

SPELL_CRIMSON_THIRST = 110040
SPELL_CRIMSON_THIRST_HEAL = 110041
SPELL_CHILDREN_OF_THE_NIGHT = 110042
SPELL_CHILDREN_STEALTH_SPEED = 110043
SPELL_CHILDREN_GHOST_SPEED = 110044
SPELL_VAMPIRIC_SUSTENANCE = 20577
SPELL_VAMPIRIC_SUSTENANCE_AURA = 20578

# Spell.dbc field indices (234 fields, 936 byte records).
SPELL_ID = 0
SPELL_ATTRIBUTES = 4
SPELL_ATTRIBUTES_EX = 5
SPELL_ATTRIBUTES_EX2 = 6
SPELL_SHAPESHIFT_MASK = 12
SPELL_CAST_TIME = 28
SPELL_RECOVERY_TIME = 29
SPELL_PROC_TYPE_MASK = 34
SPELL_PROC_CHANCE = 35
SPELL_DURATION_INDEX = 40
SPELL_RANGE_INDEX = 46
SPELL_EFFECT_1, SPELL_EFFECT_2, SPELL_EFFECT_3 = 71, 72, 73
SPELL_DIE_SIDES_1, SPELL_DIE_SIDES_2, SPELL_DIE_SIDES_3 = 74, 75, 76
SPELL_BASE_POINTS_1, SPELL_BASE_POINTS_2, SPELL_BASE_POINTS_3 = 80, 81, 82
SPELL_TARGET_A_1, SPELL_TARGET_A_2, SPELL_TARGET_A_3 = 86, 87, 88
SPELL_AURA_1, SPELL_AURA_2, SPELL_AURA_3 = 95, 96, 97
SPELL_MISC_1, SPELL_MISC_2, SPELL_MISC_3 = 110, 111, 112
SPELL_TRIGGER_1 = 116
SPELL_VISUAL_1 = 131
SPELL_ICON = 133
SPELL_START_RECOVERY_CATEGORY = 205
SPELL_NAME = 136
SPELL_NAME_SUBTEXT = 153
SPELL_DESCRIPTION = 170
SPELL_AURA_DESCRIPTION = 187
# The four 16-locale string blocks (enUS first); this client only fills enUS.
SPELL_STRING_FIELDS = (
    tuple(range(136, 152)) + tuple(range(153, 169)) + tuple(range(170, 186)) + tuple(range(187, 203))
)

SPELL_EFFECT_APPLY_AURA = 6
SPELL_EFFECT_HEAL_PCT = 136
SPELL_AURA_PROC_TRIGGER_SPELL = 42
SPELL_AURA_MOD_STEALTH_DETECT = 17
SPELL_AURA_MOD_STEALTH_LEVEL = 154
SPELL_AURA_MOD_INCREASE_SPEED = 31

SPELL_ATTR_IS_ABILITY = 0x00000010
SPELL_ATTR_PASSIVE = 0x00000040
SPELL_ATTR_DO_NOT_DISPLAY = 0x00000080

# SpellDuration.dbc ids: 1 = 10 seconds, 21 = infinite.
SPELL_DURATION_10_SECONDS = 1
SPELL_DURATION_INFINITE = 21

# "Your damaging attacks and spells": melee/ranged auto attacks, melee/ranged
# damage class spells, negative none/magic damage class spells, and main/off-hand
# special attacks (the core PROC_FLAG_DONE_* bits).
CRIMSON_THIRST_PROC_FLAGS = (
    0x00000004  # melee auto attack
    | 0x00000040  # ranged auto attack
    | 0x00000010  # spell, melee damage class
    | 0x00000100  # spell, ranged damage class
    | 0x00001000  # spell, none damage class (negative)
    | 0x00010000  # spell, magic damage class (negative)
    | 0x00400000  # main-hand special attack
    | 0x00800000  # off-hand special attack
)
CRIMSON_THIRST_INTERNAL_COOLDOWN_MS = 2000
CRIMSON_THIRST_HEAL_PERCENT = 4

ICON_CRIMSON_THIRST = 2961  # Ability_Rogue_HungerforBlood
ICON_CHILDREN_OF_THE_NIGHT = 222  # Spell_Shadow_NightOfTheDead
ICON_STEALTH_SPEED = 250  # Ability_Stealth

# A living ghost already runs at +50% (spell 8326) and run speed auras take the
# highest amount instead of stacking, so +40% over a stock ghost is +90%.
GHOST_SPEED_ATTRIBUTES = 763363584
GHOST_SPEED_BASE_POINTS = 89
STEALTH_SPEED_BASE_POINTS = 9  # +10%
STEALTH_DETECT_BASE_POINTS = 4  # +5
STEALTH_LEVEL_BASE_POINTS = 4  # +5

CRIMSON_THIRST_DONOR = 20600  # Perception: instant on-use racial
HEAL_DONOR = 28306  # Great Heal: single SPELL_EFFECT_HEAL_PCT effect
PASSIVE_DONOR = 20550  # Endurance: instant passive aura
GHOST_DONOR = 20584  # Ghost: the night elf +75% ghost run speed

VAMPIRIC_SUSTENANCE_DESCRIPTION = (
    "When activated, regenerates $20578s1% of total health every $20578t1 sec for $20578d.  "
    "Only works on Humanoid or Undead corpses within $a1 yds.  Any movement, action, or damage "
    "taken while feeding will cancel the effect."
)
VAMPIRIC_SUSTENANCE_AURA_DESCRIPTION = "Regenerate $s1% of total health every $t1 seconds."


@dataclass(frozen=True)
class DarkfallenSpell:
    """One Spell.dbc row cloned from a stock donor and retitled for Darkfallen."""

    spell_id: int
    donor_id: int
    fields: dict[int, int]
    name: str
    subtext: str = ""
    description: str = ""
    aura_description: str = ""


def spell_spec() -> tuple[DarkfallenSpell, ...]:
    return (
        DarkfallenSpell(
            spell_id=SPELL_CRIMSON_THIRST,
            donor_id=CRIMSON_THIRST_DONOR,
            fields={
                SPELL_SHAPESHIFT_MASK: 0,  # Perception is form restricted; this racial is not
                SPELL_ATTRIBUTES_EX2: 0,
                SPELL_VISUAL_1: 0,
                SPELL_RECOVERY_TIME: 120000,
                SPELL_DURATION_INDEX: SPELL_DURATION_10_SECONDS,
                SPELL_PROC_TYPE_MASK: CRIMSON_THIRST_PROC_FLAGS,
                SPELL_PROC_CHANCE: 101,  # always, limited by the proc cooldown
                SPELL_EFFECT_1: SPELL_EFFECT_APPLY_AURA,
                SPELL_BASE_POINTS_1: 0,
                SPELL_TARGET_A_1: 1,
                SPELL_AURA_1: SPELL_AURA_PROC_TRIGGER_SPELL,
                SPELL_TRIGGER_1: SPELL_CRIMSON_THIRST_HEAL,
                SPELL_ICON: ICON_CRIMSON_THIRST,
            },
            name="Crimson Thirst",
            subtext="Racial",
            description=(
                "Awakens your Darkfallen hunger for $d.  Your damaging attacks and spells have a chance "
                "to restore $110041s1% of your maximum health, but no more than once every 2 seconds."
            ),
            aura_description="Your hunger is awake; the damage you deal may restore your health.",
        ),
        DarkfallenSpell(
            spell_id=SPELL_CRIMSON_THIRST_HEAL,
            donor_id=HEAL_DONOR,
            fields={
                SPELL_ATTRIBUTES: SPELL_ATTR_IS_ABILITY,
                SPELL_ATTRIBUTES_EX: 0,
                SPELL_ATTRIBUTES_EX2: 0,
                SPELL_CAST_TIME: 1,
                SPELL_DIE_SIDES_1: 1,
                SPELL_BASE_POINTS_1: CRIMSON_THIRST_HEAL_PERCENT - 1,
                SPELL_TARGET_A_1: 1,
                SPELL_RANGE_INDEX: 1,
                SPELL_START_RECOVERY_CATEGORY: 0,
                SPELL_VISUAL_1: 0,
            },
            name="Crimson Thirst",
        ),
        DarkfallenSpell(
            spell_id=SPELL_CHILDREN_OF_THE_NIGHT,
            donor_id=PASSIVE_DONOR,
            fields={
                SPELL_ATTRIBUTES: SPELL_ATTR_IS_ABILITY | SPELL_ATTR_PASSIVE,
                SPELL_ICON: ICON_CHILDREN_OF_THE_NIGHT,
                SPELL_EFFECT_1: SPELL_EFFECT_APPLY_AURA,
                SPELL_DIE_SIDES_1: 1,
                SPELL_BASE_POINTS_1: STEALTH_DETECT_BASE_POINTS,
                SPELL_TARGET_A_1: 1,
                SPELL_AURA_1: SPELL_AURA_MOD_STEALTH_DETECT,
                SPELL_EFFECT_2: SPELL_EFFECT_APPLY_AURA,
                SPELL_DIE_SIDES_2: 1,
                SPELL_BASE_POINTS_2: STEALTH_LEVEL_BASE_POINTS,
                SPELL_TARGET_A_2: 1,
                SPELL_MISC_2: 0,  # StealthType 0 = normal stealth
                SPELL_AURA_2: SPELL_AURA_MOD_STEALTH_LEVEL,
            },
            name="Children of the Night",
            subtext="Racial Passive",
            description=(
                "Slightly increases your stealth detection and makes you harder to detect while stealthed.  "
                "Increases your movement speed while stealthed by 10% and while dead by 40%."
            ),
        ),
        DarkfallenSpell(
            spell_id=SPELL_CHILDREN_STEALTH_SPEED,
            donor_id=PASSIVE_DONOR,
            fields={
                # Hidden helper aura; modules/mod-custom-server/src/darkfallen_racials.cpp
                # applies it for as long as a stealth aura is present.
                SPELL_ATTRIBUTES: SPELL_ATTR_IS_ABILITY | SPELL_ATTR_DO_NOT_DISPLAY,
                SPELL_DURATION_INDEX: SPELL_DURATION_INFINITE,
                SPELL_ICON: ICON_STEALTH_SPEED,
                SPELL_EFFECT_1: SPELL_EFFECT_APPLY_AURA,
                SPELL_DIE_SIDES_1: 1,
                SPELL_BASE_POINTS_1: STEALTH_SPEED_BASE_POINTS,
                SPELL_TARGET_A_1: 1,
                SPELL_AURA_1: SPELL_AURA_MOD_INCREASE_SPEED,
            },
            name="Children of the Night",
        ),
        DarkfallenSpell(
            spell_id=SPELL_CHILDREN_GHOST_SPEED,
            donor_id=GHOST_DONOR,
            fields={
                SPELL_ATTRIBUTES: GHOST_SPEED_ATTRIBUTES | SPELL_ATTR_DO_NOT_DISPLAY,
                SPELL_BASE_POINTS_1: GHOST_SPEED_BASE_POINTS,
                # The donor also swim faster and turn into a wisp; neither is racial here.
                SPELL_EFFECT_2: 0,
                SPELL_BASE_POINTS_2: 0,
                SPELL_AURA_2: 0,
                SPELL_EFFECT_3: 0,
                SPELL_MISC_3: 0,
                SPELL_AURA_3: 0,
            },
            name="Children of the Night",
        ),
    )


def spell_renames() -> tuple[DarkfallenSpell, ...]:
    """Stock Undead racials retitled for Darkfallen (no mechanical change)."""
    return (
        DarkfallenSpell(
            spell_id=SPELL_VAMPIRIC_SUSTENANCE,
            donor_id=SPELL_VAMPIRIC_SUSTENANCE,
            fields={},
            name="Vampiric Sustenance",
            subtext="Racial",
            description=VAMPIRIC_SUSTENANCE_DESCRIPTION,
        ),
        DarkfallenSpell(
            spell_id=SPELL_VAMPIRIC_SUSTENANCE_AURA,
            donor_id=SPELL_VAMPIRIC_SUSTENANCE_AURA,
            fields={},
            name="Vampiric Sustenance",
            aura_description=VAMPIRIC_SUSTENANCE_AURA_DESCRIPTION,
        ),
    )


@dataclass(frozen=True)
class DarkfallenPackReport:
    race_ids: tuple[int, int]
    root_updates: dict[str, bytes]
    locale_updates: dict[str, bytes]
    collisions: tuple[str, ...]
    staged_root: str


def contract() -> dict[str, object]:
    return {
        "race_ids": {"alliance": 43, "horde": 44},
        "client_file_strings": DARKFALLEN_FILE_STRINGS,
        "race_mask": DARKFALLEN_MASK,
        "model_ids": DARKFALLEN_MODEL_IDS,
        "display_ids": DARKFALLEN_DISPLAY_IDS,
        "languages": {"alliance": "Common", "horde": "Orcish"},
        "archives": {"root": ARCHIVE_NAME, "locale": LOCALE_ARCHIVE_NAME},
        "racial_spells": {
            "crimson_thirst": SPELL_CRIMSON_THIRST,
            "crimson_thirst_heal": SPELL_CRIMSON_THIRST_HEAL,
            "children_of_the_night": SPELL_CHILDREN_OF_THE_NIGHT,
            "children_stealth_speed": SPELL_CHILDREN_STEALTH_SPEED,
            "children_ghost_speed": SPELL_CHILDREN_GHOST_SPEED,
            "vampiric_sustenance": SPELL_VAMPIRIC_SUSTENANCE,
        },
    }


def collect_assets(source: Path) -> dict[str, bytes]:
    required = (source / "Male" / "DarkfallenMale.m2", source / "Female" / "DarkfallenFemale.m2")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing Darkfallen model: " + ", ".join(missing))
    entries: dict[str, bytes] = {}
    for path in source.rglob("*"):
        if not path.is_file() or path.name.casefold() == "darkfallen.md":
            continue
        relative = path.relative_to(source).as_posix().replace("/", "\\")
        entries[f"Character\\Darkfallen\\{relative}"] = path.read_bytes()
    if not entries:
        raise ValueError(f"no Darkfallen assets found under {source}")
    return entries


def _read_archive(storm: Storm, path: Path) -> dict[str, bytes]:
    archive = storm.open_archive(path)
    try:
        return {name: storm.read(archive, name) for name, *_ in storm.list_files(archive)}
    finally:
        storm.dll.SFileCloseArchive(archive)


def _find_entry(entries: dict[str, bytes], name: str) -> tuple[str, bytes]:
    matches = [(key, value) for key, value in entries.items() if key.casefold() == name.casefold()]
    if len(matches) != 1:
        raise ValueError(f"required archive entry is missing or duplicated: {name}")
    return matches[0]


def _value(record: bytes, offset: int, width: int) -> int:
    return int.from_bytes(record[offset : offset + width], "little")


def _replace(record: bytes, offset: int, width: int, value: int) -> bytes:
    if value < 0 or value >= 1 << (width * 8):
        raise ValueError(f"value {value} does not fit in {width} bytes")
    result = bytearray(record)
    result[offset : offset + width] = value.to_bytes(width, "little")
    return bytes(result)


def _string(pool: bytes, offset: int) -> bytes:
    if offset == 0:
        return b""
    end = pool.find(b"\0", offset)
    if end < 0:
        raise ValueError(f"unterminated WDBC string at offset {offset}")
    return pool[offset:end]


def _append_string(pool: bytearray, value: bytes) -> int:
    offset = len(pool)
    pool.extend(value)
    pool.append(0)
    return offset


def _clone_with_strings(
    table_name: str,
    donor: RawWdbc,
    record: bytes,
    pool: bytearray,
    rewrite_blood_elf_paths: bool = False,
) -> bytes:
    result = bytearray(record)
    for field in STRING_FIELDS.get(table_name, ()):
        field_offset = field * 4
        source_offset = _value(record, field_offset, 4)
        if source_offset == 0:
            continue
        value = _string(donor.strings, source_offset)
        if rewrite_blood_elf_paths:
            value = value.replace(b"BloodElf", b"Darkfallen")
        result[field_offset : field_offset + 4] = _append_string(pool, value).to_bytes(4, "little")
    return bytes(result)


def _clone_darkfallen_char_section(donor: RawWdbc, record: bytes, pool: bytearray, source: Path) -> bytes | None:
    result = bytearray(record)
    generation_type = _value(record, 3 * 4, 4)
    for field in STRING_FIELDS["CharSections"]:
        field_offset = field * 4
        source_offset = _value(record, field_offset, 4)
        if source_offset == 0:
            continue
        value = _string(donor.strings, source_offset)
        if generation_type == 3:
            result[field_offset : field_offset + 4] = _append_string(pool, value).to_bytes(4, "little")
            continue
        darkfallen_value = value.replace(b"BloodElf", b"Darkfallen")
        relative = darkfallen_value.removeprefix(b"Character\\Darkfallen\\").decode().replace("\\", "/")
        if (source / relative).is_file():
            result[field_offset : field_offset + 4] = _append_string(pool, darkfallen_value).to_bytes(4, "little")
        elif generation_type == 0 and field != 4:
            result[field_offset : field_offset + 4] = (0).to_bytes(4, "little")
        else:
            return None
    return bytes(result)


def _set_string(record: bytes, field: int, pool: bytearray, value: str) -> bytes:
    result = bytearray(record)
    result[field * 4 : field * 4 + 4] = _append_string(pool, value.encode("utf-8")).to_bytes(4, "little")
    return bytes(result)


def _alloc_id(existing: set[int]) -> int:
    value = max(existing, default=0) + 1
    while value in existing:
        value += 1
    existing.add(value)
    return value


def _merge_race_table(table_name: str, data: bytes, asset_source: Path) -> bytes:
    layout = WDBC_LAYOUTS[table_name]
    donor = RawWdbc(data)
    if (donor.fields, donor.record_size) != (layout.fields, layout.record_size):
        raise ValueError(f"unsupported donor layout for {table_name}: {donor.header}")
    source_rows_by_race: dict[int, list[bytes]] = {}
    for row in donor.records:
        source_rows_by_race.setdefault(_value(row, layout.race_offset, layout.race_width), []).append(row)

    pool = bytearray(donor.strings)
    records = [
        row
        for row in donor.records
        if _value(row, layout.race_offset, layout.race_width) not in DARKFALLEN_RACE_IDS
    ]
    keyed = table_name not in {"CharBaseInfo", "CharacterFacialHairStyles"}
    existing_ids = {int.from_bytes(row[:4], "little") for row in records} if keyed else set()
    target_rows: list[bytes] = []

    for target_race in DARKFALLEN_RACE_IDS:
        source_race = (
            10
            if table_name == "CharBaseInfo"
            else 13
            if table_name in DARKFALLEN_BLOOD_ELF_APPEARANCE_TABLES
            else DARKFALLEN_SOURCE_RACES[target_race]
        )
        source_rows = source_rows_by_race.get(source_race, [])
        if not source_rows:
            raise ValueError(f"donor race {source_race} rows are missing from {table_name}")
        for source_row in source_rows:
            if table_name == "CharHairGeosets" and _value(source_row, 2 * 4, 4) in DARKFALLEN_HAIR_STYLE_IDS:
                if _value(source_row, 3 * 4, 4) not in DARKFALLEN_HAIR_STYLE_IDS[_value(source_row, 2 * 4, 4)]:
                    continue
            if table_name == "BarberShopStyle" and _value(source_row, 1 * 4, 4) == 0:
                gender = _value(source_row, 38 * 4, 4)
                if gender in DARKFALLEN_HAIR_STYLE_IDS and _value(source_row, 39 * 4, 4) not in DARKFALLEN_HAIR_STYLE_IDS[gender]:
                    continue
            row = _replace(source_row, layout.race_offset, layout.race_width, target_race)
            if table_name == "CharSections":
                row = _clone_darkfallen_char_section(donor, row, pool, asset_source)
                if row is None:
                    continue
            else:
                row = _clone_with_strings(table_name, donor, row, pool)
            if table_name == "ChrRaces":
                row = _replace(row, 2 * 4, 4, 1 if target_race == 43 else 1610)
                row = _replace(row, 4 * 4, 4, DARKFALLEN_DISPLAY_IDS["male"])
                row = _replace(row, 5 * 4, 4, DARKFALLEN_DISPLAY_IDS["female"])
                row = _replace(row, 7 * 4, 4, 7 if target_race == 43 else 1)
                row = _replace(row, 13 * 4, 4, 0 if target_race == 43 else 1)
                row = _set_string(row, 6, pool, "Be")
                row = _set_string(row, 11, pool, DARKFALLEN_FILE_STRINGS[target_race])
                for field in (*range(14, 30), *range(31, 47), *range(48, 64)):
                    row = _set_string(row, field, pool, "Darkfallen")
            elif keyed:
                row = _replace(row, 0, 4, _alloc_id(existing_ids))
            target_rows.append(row)

    if table_name == "ChrRaces":
        records = [row for row in records if int.from_bytes(row[:4], "little") not in DARKFALLEN_RACE_IDS]
        existing_ids = {int.from_bytes(row[:4], "little") for row in records}
        for row in target_rows:
            row_id = int.from_bytes(row[:4], "little")
            if row_id in existing_ids:
                raise ValueError(f"{table_name} target row collides with existing ID {row_id}")
            existing_ids.add(row_id)
            records.append(row)
    elif keyed:
        records.extend(target_rows)
    else:
        existing = set(records)
        records.extend(row for row in target_rows if row not in existing)
    return donor.build(records, bytes(pool))


def _merge_mask_table(table_name: str, data: bytes) -> bytes:
    layout = WDBC_LAYOUTS[table_name]
    table = RawWdbc(data)
    if (table.fields, table.record_size) != (layout.fields, layout.record_size):
        raise ValueError(f"unsupported donor layout for {table_name}: {table.header}")
    race_offset = layout.race_offset
    source_mask = sum(1 << (race - 1) for race in DARKFALLEN_SOURCE_RACES.values())
    records = [
        _replace(row, race_offset, layout.race_width, _value(row, race_offset, layout.race_width) | DARKFALLEN_MASK)
        if _value(row, race_offset, layout.race_width) & source_mask
        else row
        for row in table.records
    ]
    return table.build(records)


def _merge_model_rows(table_name: str, data: bytes) -> bytes:
    table = RawWdbc(data)
    pool = bytearray(table.strings)
    records = list(table.records)
    by_id = {int.from_bytes(row[:4], "little"): index for index, row in enumerate(records)}
    sources = DARKFALLEN_MODEL_SOURCES if table_name == "CreatureModelData" else DARKFALLEN_DISPLAY_SOURCES
    target_ids = DARKFALLEN_MODEL_IDS if table_name == "CreatureModelData" else DARKFALLEN_DISPLAY_IDS
    for gender, source_id in sources.items():
        source = next((row for row in table.records if int.from_bytes(row[:4], "little") == source_id), None)
        if source is None:
            raise ValueError(f"{table_name} donor row {source_id} is missing")
        row = _replace(source, 0, 4, target_ids[gender])
        if table_name == "CreatureModelData":
            model_root = DARKFALLEN_MALE_PATH if gender == "male" else DARKFALLEN_FEMALE_PATH
            model_path = f"{model_root}\\Darkfallen{gender.title()}.m2"
            row = _set_string(row, 2, pool, model_path)
        else:
            row = _replace(row, 1 * 4, 4, DARKFALLEN_MODEL_IDS[gender])
        target_id = int.from_bytes(row[:4], "little")
        if target_id in by_id:
            records[by_id[target_id]] = row
            continue
        by_id[target_id] = len(records)
        records.append(row)
    return table.build(records, bytes(pool))


@dataclass(frozen=True)
class PreparedSpell:
    """A Darkfallen spell row placed in a rebuilt Spell.dbc table."""

    spell: DarkfallenSpell
    index: int
    row: tuple[int, ...]


def _prepare_spells(table: Wdbc) -> tuple[list[list[int]], list[PreparedSpell], list[PreparedSpell]]:
    """Clone the Darkfallen spell rows and retitle the stock ones.

    Returns the rewritten record list, the appended spells, and the renamed stock
    spells. ``table`` must be the Spell.dbc being patched (archive or extract), so
    the clones match whatever the client already ships.
    """
    records = [list(row) for row in table.rows]
    index_by_id: dict[int, int] = {}
    for index, row in enumerate(records):
        index_by_id.setdefault(row[0], index)

    def donor_row(spell_id: int) -> list[int]:
        index = index_by_id.get(spell_id)
        if index is None:
            raise ValueError(f"Spell.dbc donor {spell_id} is missing")
        return list(records[index])

    appended: list[PreparedSpell] = []
    for spell in spell_spec():
        if spell.spell_id in index_by_id:
            raise ValueError(f"Spell.dbc already contains id {spell.spell_id}")
        row = donor_row(spell.donor_id)
        row[SPELL_ID] = spell.spell_id
        for field, value in spell.fields.items():
            row[field] = value
        # Blank the donor's text; the new strings (some intentionally empty) come
        # from the caller so a clone never keeps "Endurance"/"Perception" wording.
        for field in (SPELL_NAME, SPELL_NAME_SUBTEXT, SPELL_DESCRIPTION, SPELL_AURA_DESCRIPTION):
            row[field] = 0
        index_by_id[spell.spell_id] = len(records)
        appended.append(PreparedSpell(spell=spell, index=len(records), row=tuple(row)))
        records.append(row)

    renamed: list[PreparedSpell] = []
    for spell in spell_renames():
        index = index_by_id.get(spell.spell_id)
        if index is None:
            raise ValueError(f"Spell.dbc {spell.spell_id} cannot be renamed; it is missing")
        row = list(records[index])
        for field, value in spell.fields.items():
            row[field] = value
        for field in (SPELL_NAME, SPELL_NAME_SUBTEXT, SPELL_DESCRIPTION, SPELL_AURA_DESCRIPTION):
            row[field] = 0
        records[index] = row
        renamed.append(PreparedSpell(spell=spell, index=index, row=tuple(row)))

    return records, appended, renamed


def _spell_string_fields(table: Wdbc, records: list[list[int]]) -> dict[tuple[int, int], str]:
    """Preserve every string already present in the table (fresh pool on rebuild)."""
    strings: dict[tuple[int, int], str] = {}
    for index, row in enumerate(records):
        for field in SPELL_STRING_FIELDS:
            if row[field]:
                value = table.text(row[field])
                if value:
                    strings[(index, field)] = value
    return strings


def _spell_text_overrides(prepared: list[PreparedSpell]) -> dict[tuple[int, int], str]:
    overrides: dict[tuple[int, int], str] = {}
    for item in prepared:
        for field, value in (
            (SPELL_NAME, item.spell.name),
            (SPELL_NAME_SUBTEXT, item.spell.subtext),
            (SPELL_DESCRIPTION, item.spell.description),
            (SPELL_AURA_DESCRIPTION, item.spell.aura_description),
        ):
            if value:
                overrides[(item.index, field)] = value
    return overrides


def merge_spell_table(data: bytes) -> bytes:
    """Add the Crimson Thirst / Children of the Night rows and the rename."""
    table = Wdbc(data)
    records, appended, renamed = _prepare_spells(table)
    strings = _spell_string_fields(table, records)
    strings.update(_spell_text_overrides(appended + renamed))
    return build_wdbc(records, table.fields, table.record_size, strings)


# `spell_dbc` replaces the whole Spell.dbc row for an id, so a row that only lists a
# few columns silently zeroes the rest (EquippedItemClass -1, the 1.0 effect
# multipliers, ...). The column list and its types therefore come from the world
# schema, and only the columns whose value differs from the schema default are
# written; the remaining ones are already 0/empty in the DBC row.
SPELL_DBC_DDL = ROOT / "data" / "sql" / "base" / "db_world" / "spell_dbc.sql"
# (Spell.dbc field, spell_dbc column, DarkfallenSpell attribute). Only the columns the
# world schema declares as text are written: `Description_Lang_*` is an int column in
# `spell_dbc` (the server never reads a spell description), so the client tooltip text
# lives in the patched Spell.dbc only.
SPELL_DBC_TEXT_COLUMNS: tuple[tuple[int, str, str], ...] = (
    (SPELL_NAME, "Name_Lang_enUS", "name"),
    (SPELL_NAME_SUBTEXT, "NameSubtext_Lang_enUS", "subtext"),
    (SPELL_DESCRIPTION, "Description_Lang_enUS", "description"),
    (SPELL_AURA_DESCRIPTION, "AuraDescription_Lang_enUS", "aura_description"),
)


def _spell_dbc_columns() -> tuple[tuple[str, str], ...]:
    """(column, kind) pairs in Spell.dbc field order, read from the world schema."""
    schema = SPELL_DBC_DDL.read_text(encoding="utf-8")
    start = schema.index("CREATE TABLE `spell_dbc` (")
    end = schema.index(") ENGINE=", start)
    columns: list[tuple[str, str]] = []
    for name, type_text in re.findall(r"\n\s*`([^`]+)`\s+([^\n,]+),", schema[start:end]):
        if type_text.startswith("float"):
            kind = "float"
        elif "char" in type_text:
            kind = "string"
        elif "unsigned" in type_text:
            kind = "unsigned"
        else:
            kind = "signed"
        columns.append((name, kind))
    if len(columns) != 234:
        raise ValueError(f"unexpected spell_dbc column count: {len(columns)}")
    return tuple(columns)


def _spell_sql_value(value: int, kind: str) -> object:
    if kind == "float":
        return struct.unpack("<f", struct.pack("<I", value))[0]
    if kind == "signed":
        return struct.unpack("<i", struct.pack("<I", value))[0]
    return value


def _sql_literal(value: object) -> str:
    if isinstance(value, str):
        return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"
    if isinstance(value, float):
        return repr(value)
    return str(value)


def render_spell_sql(data: bytes) -> str:
    """Emit the world-DB half of the racial spells for a pending migration."""
    table = Wdbc(data)
    _, appended, _ = _prepare_spells(table)
    columns = _spell_dbc_columns()
    text_columns = tuple(
        (field, column, attribute)
        for field, column, attribute in SPELL_DBC_TEXT_COLUMNS
        if columns[field][1] == "string"
    )

    statements: list[str] = []
    for item in appended:
        names = ["ID"]
        values = [str(item.spell.spell_id)]
        for field, (column, kind) in enumerate(columns):
            if kind == "string" or column == "ID":
                continue
            value = item.row[field]
            if not value:
                continue
            names.append(column)
            values.append(_sql_literal(_spell_sql_value(value, kind)))
        for field, column, attribute in text_columns:
            text_value = getattr(item.spell, attribute)
            if text_value:
                names.append(column)
                values.append(_sql_literal(text_value))
        statements.append(
            f"INSERT INTO `spell_dbc` ({', '.join(f'`{name}`' for name in names)}) VALUES\n"
            f"({', '.join(values)});"
        )

    ids = ", ".join(str(item.spell.spell_id) for item in appended)
    return (
        "-- GENERATED by `python tools/darkfallen_race_pack.py --spell-sql-out <path>`; do not hand edit.\n"
        "-- The rows mirror the client Spell.dbc entries the packer writes into patch-Z.MPQ.\n"
        "-- `spell_dbc` overrides the whole row, so every non-default field of the cloned\n"
        "-- stock spell is listed here; anything omitted is 0/empty in the DBC row too.\n"
        "\n"
        f"DELETE FROM `spell_dbc` WHERE `ID` IN ({ids});\n"
        + "\n".join(statements)
        + "\n"
        "\n"
        "-- Without a `spell_proc` row a proc aura can never trigger at all. ProcFlags,\n"
        "-- charges and chance stay at their Spell.dbc values; only the internal cooldown is\n"
        "-- added, which is what stops Crimson Thirst healing more than once every 2 seconds.\n"
        f"DELETE FROM `spell_proc` WHERE `SpellId` = {SPELL_CRIMSON_THIRST};\n"
        f"INSERT INTO `spell_proc` (`SpellId`, `Cooldown`) VALUES "
        f"({SPELL_CRIMSON_THIRST}, {CRIMSON_THIRST_INTERNAL_COOLDOWN_MS});\n"
    )


def read_archive_entry(storm: Storm, archive: Path, entry_name: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, entry_name)
    finally:
        storm.dll.SFileCloseArchive(handle)


def build_dbc_updates(entries: dict[str, bytes], source: Path = ASSET_ROOT) -> dict[str, bytes]:
    updates: dict[str, bytes] = {}
    for table_name in RACE_ID_FIELDS:
        key, data = _find_entry(entries, f"DBFilesClient\\{table_name}.dbc")
        updates[key] = _merge_race_table(table_name, data, source)
    for table_name in RACE_MASK_FIELDS:
        key, data = _find_entry(entries, f"DBFilesClient\\{table_name}.dbc")
        updates[key] = _merge_mask_table(table_name, data)
    for table_name in ("CreatureModelData", "CreatureDisplayInfo"):
        key, data = _find_entry(entries, f"DBFilesClient\\{table_name}.dbc")
        updates[key] = _merge_model_rows(table_name, data)
    key, data = _find_entry(entries, "DBFilesClient\\Spell.dbc")
    updates[key] = merge_spell_table(data)
    return updates


def _insert_once(text: str, anchor: str, addition: str, marker: str, label: str) -> str:
    """Append `addition` after the first `anchor`, unless `marker` is already present."""
    if marker in text:
        return text
    if anchor not in text:
        raise ValueError(f"CharacterInfo.lua missing {label} anchor")
    return text.replace(anchor, anchor + addition, 1)


def _extend_once(text: str, old: str, new: str, marker: str, label: str) -> str:
    """Replace `old` with `new` once, unless `marker` shows it is already extended."""
    if marker in text:
        return text
    if old not in text:
        raise ValueError(f"CharacterInfo.lua missing {label} anchor")
    return text.replace(old, new, 1)


DARKFALLEN_INFO = (
    'Races_Informations[18] = { Name = "Darkfallen", '
    'Description = "Children of the night, bound by shadow and blood." }\n'
)
# Ordinal 19 is the Horde Darkfallen creation button, but raceInfoByFileString.VOIDELF
# reads Races_Informations[19]. Giving the Void Elf its own entry keeps that button's
# tooltip (and Pandaren's) from reading "Darkfallen".
VOID_ELF_INFO = (
    'Races_Informations[19] = { Name = "Void Elf", '
    'Description = _G.RACE_INFO_VOIDELF or "Shadow-touched elves who wield the Void '
    'from Telogrus Rift." }\n'
)
STALE_DARKFALLEN_ALIAS = DARKFALLEN_INFO + "Races_Informations[19] = Races_Informations[18]\n"
# raceLocalization entry for the Alliance creator button. The racial list changed with
# the kit, so the shipped entry is upgraded in place instead of being skipped.
DARKFALLEN_RACE_LOCALIZATION = (
    '    [18] = {token = "DARKFALLEN", name = "Darkfallen", '
    'spells = {"Crimson Thirst", "Shadow Resistance", "Vampiric Sustenance", "Children of the Night"}},\n'
)
STALE_DARKFALLEN_RACE_LOCALIZATION = (
    '    [18] = {token = "DARKFALLEN", name = "Darkfallen", '
    'spells = {"Shadow Resistance", "Cannibalize"}},\n'
)
# The ordinal-19 duplicate that shipped before the Void Elf fix, kept verbatim so the
# packer strips it from archives that already carry it.
STALE_DARKFALLEN_ORDINAL_19 = (
    '    [19] = {token = "DARKFALLEN", name = "Darkfallen", '
    'spells = {"Shadow Resistance", "Cannibalize"}},\n'
)


def patch_character_info(data: bytes) -> bytes:
    text = data.decode("utf-8")
    if STALE_DARKFALLEN_ALIAS in text:
        text = text.replace(STALE_DARKFALLEN_ALIAS, DARKFALLEN_INFO + VOID_ELF_INFO, 1)
    else:
        text = _insert_once(
            text,
            'Races_Informations[17] = { Name = "Vulpera", '
            'Description = "Resourceful desert survivors and clever allies." }\n',
            DARKFALLEN_INFO + VOID_ELF_INFO,
            VOID_ELF_INFO,
            "Vulpera ordinal",
        )
    text = text.replace(STALE_DARKFALLEN_ORDINAL_19, "", 1)
    text = _insert_once(
        text,
        '    VULPERA = Races_Informations[17],\n',
        '    DARKFALLEN = Races_Informations[18],\n',
        '    DARKFALLEN = Races_Informations[18],\n',
        "raceInfoByFileString Vulpera",
    )
    text = _insert_once(
        text,
        '    DARKFALLEN = Races_Informations[18],\n',
        '    DARKFALLENHORDE = Races_Informations[18],\n',
        '    DARKFALLENHORDE = Races_Informations[18],\n',
        "raceInfoByFileString Darkfallen",
    )
    text = _insert_once(
        text,
        '    [17] = { glueString = "VULPERA",  faction = "Horde" },\n',
        '    [18] = { glueString = "DARKFALLEN", faction = "Alliance" },\n'
        '    [19] = { glueString = "DARKFALLEN", faction = "Horde" },\n',
        '[18] = { glueString = "DARKFALLEN"',
        "RACE_DATA Vulpera",
    )
    text = _extend_once(
        text,
        "local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16}",
        "local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16, 18}",
        "local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16, 18}",
        "ALLIANCE_RACES",
    )
    text = _extend_once(
        text,
        "local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17}",
        "local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17, 19}",
        "local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17, 19}",
        "HORDE_RACES",
    )
    text = text.replace(STALE_DARKFALLEN_RACE_LOCALIZATION, DARKFALLEN_RACE_LOCALIZATION, 1)
    text = _insert_once(
        text,
        '    [17] = {token = "VULPERA", name = "Vulpera", spells = {}},\n',
        DARKFALLEN_RACE_LOCALIZATION,
        '    [18] = {token = "DARKFALLEN"',
        "raceLocalization Vulpera",
    )
    text = _insert_once(
        text,
        '_G.RACE_15 = "Mag\'har Orc"\n',
        '_G.RACE_18 = "Darkfallen"\n'
        '_G.RACE_19 = "Darkfallen"\n',
        '_G.RACE_18 = "Darkfallen"\n',
        "race name block",
    )
    text = _insert_once(
        text,
        '_G.BROKEN_FEMALE = "Broken"\n',
        '_G.DARKFALLEN = "Darkfallen"\n'
        '_G.DARKFALLEN_MALE = "Darkfallen"\n'
        '_G.DARKFALLEN_FEMALE = "Darkfallen"\n',
        '_G.DARKFALLEN = "Darkfallen"\n',
        "Broken glove string block",
    )
    return text.encode("utf-8")


def patch_character_create(data: bytes) -> bytes:
    text = data.decode("utf-8")
    icon_anchor = (
        '    ["BLOODELF_MALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-BloodElfMale",\n'
    )
    text = _insert_once(
        text,
        icon_anchor,
        '    ["DARKFALLEN_MALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-DarkfallenMale",\n'
        '    ["DARKFALLEN_FEMALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
        'UI-CharacterCreate-DarkfallenFemale",\n',
        '"DARKFALLEN_MALE"',
        "Blood Elf icon anchor",
    )
    text = _insert_once(
        text,
        icon_anchor,
        '    ["DARKFALLENHORDE_MALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
        'UI-CharacterCreate-DarkfallenHordeMale",\n'
        '    ["DARKFALLENHORDE_FEMALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\'
        'UI-CharacterCreate-DarkfallenHordeFemale",\n',
        '"DARKFALLENHORDE_MALE"',
        "Blood Elf icon anchor",
    )
    if '"DARKFALLEN_ALLIANCE"' not in text:
        anchor = '        ["MAGHAR"] = "ORC",\n'
        if anchor not in text:
            raise ValueError("CharacterCreate.lua missing background mapping anchor")
        additions = (
            '        ["DARKFALLEN"] = "HUMAN",\n'
            '        ["DARKFALLEN_ALLIANCE"] = "HUMAN",\n'
            '        ["DARKFALLEN_HORDE"] = "ORC",\n'
        )
        text = text.replace(anchor, anchor + additions, 1)
    text = _insert_once(
        text,
        '        ["DARKFALLEN_HORDE"] = "ORC",\n',
        '        ["DARKFALLENHORDE"] = "ORC",\n',
        '        ["DARKFALLENHORDE"] = "ORC",',
        "RACE_BACKGROUND_KEYS Darkfallen Horde",
    )
    hair_controller = re.compile(
        r"\nlocal DARKFALLEN_HAIR_STYLE_COUNT.*?\nend\n$",
        flags=re.DOTALL,
    )
    text = hair_controller.sub("\n", text)
    return text.encode("utf-8")


def patch_glue_parent(data: bytes) -> bytes:
    text = data.decode("utf-8")
    text = _insert_once(
        text,
        'CharModelFogInfo["KULTIRAN"] = CharModelFogInfo["HUMAN"];\n',
        'CharModelFogInfo["DARKFALLEN"] = CharModelFogInfo["HUMAN"];\n'
        'CharModelGlowInfo["DARKFALLEN"] = CharModelGlowInfo["HUMAN"];\n'
        'GlueAmbienceTracks["DARKFALLEN"] = GlueAmbienceTracks["HUMAN"];\n',
        'CharModelFogInfo["DARKFALLEN"]',
        "CharModelFogInfo KULTIRAN",
    )
    # RaceLights is defined well below the fog/glow/ambience tables, so its entries must be
    # added after their own anchor: a RaceLights line next to the fog entries made the Glue
    # fail to load with "attempt to index global 'RaceLights' (a nil value)".
    definition = text.find("RaceLights = {")
    if definition > 0:
        head, tail = text[:definition], text[definition:]
        for line in (
            'RaceLights["DARKFALLEN"] = RaceLights["HUMAN"];\n',
            'RaceLights["DARKFALLENHORDE"] = RaceLights["ORC"];\n',
        ):
            head = head.replace(line, "", 1)
        text = head + tail
    text = _insert_once(
        text,
        'RaceLights["KULTIRAN"] = RaceLights["HUMAN"];\n',
        'RaceLights["DARKFALLEN"] = RaceLights["HUMAN"];\n',
        'RaceLights["DARKFALLEN"]',
        "RaceLights KULTIRAN",
    )
    text = _insert_once(
        text,
        'RaceLights["DARKFALLEN"] = RaceLights["HUMAN"];\n',
        'RaceLights["DARKFALLENHORDE"] = RaceLights["ORC"];\n',
        'RaceLights["DARKFALLENHORDE"]',
        "RaceLights Darkfallen",
    )
    text = _insert_once(
        text,
        'CharModelFogInfo["DARKFALLEN"] = CharModelFogInfo["HUMAN"];\n',
        'CharModelFogInfo["DARKFALLENHORDE"] = CharModelFogInfo["ORC"];\n',
        'CharModelFogInfo["DARKFALLENHORDE"]',
        "CharModelFogInfo Darkfallen",
    )
    text = _insert_once(
        text,
        'CharModelGlowInfo["DARKFALLEN"] = CharModelGlowInfo["HUMAN"];\n',
        'CharModelGlowInfo["DARKFALLENHORDE"] = CharModelGlowInfo["ORC"];\n',
        'CharModelGlowInfo["DARKFALLENHORDE"]',
        "CharModelGlowInfo Darkfallen",
    )
    text = _insert_once(
        text,
        'GlueAmbienceTracks["DARKFALLEN"] = GlueAmbienceTracks["HUMAN"];\n',
        'GlueAmbienceTracks["DARKFALLENHORDE"] = GlueAmbienceTracks["ORC"];\n',
        'GlueAmbienceTracks["DARKFALLENHORDE"]',
        "GlueAmbienceTracks Darkfallen",
    )
    # SetBackgroundModel() picks the character-select backdrop from its faction lists and
    # otherwise falls back to "Interface\\Glues\\Models\\UI_<Race>\\UI_<Race>.m2", which does
    # not exist for Darkfallen: the whole 3D scene (character included) then renders black.
    text = _insert_once(
        text,
        '        ["KULTIRAN"] = true,\n',
        '        ["DARKFALLEN"] = true,\n',
        '["DARKFALLEN"] = true,',
        "SetBackgroundModel allianceRaces KULTIRAN",
    )
    text = _insert_once(
        text,
        '        ["ILLIDARI"] = true,\n',
        '        ["DARKFALLENHORDE"] = true,\n',
        '["DARKFALLENHORDE"] = true,',
        "SetBackgroundModel hordeRaces ILLIDARI",
    )
    check_glue_parent_order(text)
    return text.encode("utf-8")


def check_glue_parent_order(text: str) -> None:
    """Every race lookup in the Glue must come after the table it reads is defined."""
    for table, definition in (
        ("CharModelFogInfo", "CharModelFogInfo = { };"),
        ("CharModelGlowInfo", "CharModelGlowInfo = { };"),
        ("GlueAmbienceTracks", "GlueAmbienceTracks = { };"),
        ("RaceLights", "RaceLights = {"),
    ):
        start = text.find(definition)
        use = text.find(f'{table}["')
        if start < 0 or use < 0 or use < start:
            raise ValueError(f"GlueParent.lua uses {table}[...] before its definition")


def patch_character_select(data: bytes) -> bytes:
    """Make the character list's faction survive the shared Darkfallen display name."""
    text = data.decode("utf-8")
    return _insert_once(
        text,
        "            local faction = GetCharacterFaction(race);\n",
        '            -- Both Darkfallen races share a display name, so take the side from the\n'
        '            -- client\'s own per-character race string (the select backdrop key).\n'
        '            local raceModel = strupper(GetSelectBackgroundModel(actualIndex) or "");\n'
        '            if ( strfind(raceModel, "HORDE") ) then\n'
        '                faction = "Horde";\n'
        '            elseif ( raceModel == "DARKFALLEN" ) then\n'
        '                faction = "Alliance";\n'
        "            end\n",
        "raceModel = strupper(GetSelectBackgroundModel",
        "CharacterSelect faction line",
    ).encode("utf-8")


# Creation-screen strings. The racial lines change as the Darkfallen kit changes, so
# the previous release of this block is replaced rather than skipped.
DARKFALLEN_GLUE_STRINGS = (
    "\nRACE_18 = \"Darkfallen\";\nRACE_19 = \"Darkfallen\";\n"
    "DARKFALLEN = \"Darkfallen\";\nDARKFALLEN_MALE = \"Darkfallen\";\nDARKFALLEN_FEMALE = \"Darkfallen\";\n"
    "RACE_INFO_DARKFALLEN = \"Children of the night, bound by shadow and blood.\";\n"
    "RACE_INFO_DARKFALLEN_FEMALE = \"Children of the night, bound by shadow and blood.\";\n"
    "ABILITY_INFO_DARKFALLEN1 = \"- Resistant to Shadow damage.\";\n"
    "ABILITY_INFO_DARKFALLEN2 = \"- May consume corpses to regain health.\";\n"
    "ABILITY_INFO_DARKFALLEN3 = \"- May awaken a crimson hunger that mends wounds.\";\n"
    "ABILITY_INFO_DARKFALLEN4 = \"- Sees further in shadow, and runs faster stealthed or dead.\";\n"
)
# Exactly what the first Darkfallen archive pass shipped, so re-running the packer on
# the deployed archive upgrades the block instead of appending a duplicate.
PREVIOUS_DARKFALLEN_GLUE_STRINGS = (
    "\nRACE_18 = \"Darkfallen\";\nRACE_19 = \"Darkfallen\";\n"
    "DARKFALLEN = \"Darkfallen\";\nDARKFALLEN_MALE = \"Darkfallen\";\nDARKFALLEN_FEMALE = \"Darkfallen\";\n"
    "RACE_INFO_DARKFALLEN = \"Children of the night, bound by shadow and blood.\";\n"
    "RACE_INFO_DARKFALLEN_FEMALE = \"Children of the night, bound by shadow and blood.\";\n"
    "ABILITY_INFO_DARKFALLEN1 = \"- Resistant to Shadow damage.\";\n"
    "ABILITY_INFO_DARKFALLEN2 = \"- May consume corpses to regain health.\";\n"
)


def patch_glue_strings(data: bytes) -> bytes:
    text = data.decode("utf-8")
    if DARKFALLEN_GLUE_STRINGS in text:
        return data
    if PREVIOUS_DARKFALLEN_GLUE_STRINGS in text:
        return text.replace(PREVIOUS_DARKFALLEN_GLUE_STRINGS, DARKFALLEN_GLUE_STRINGS, 1).encode("utf-8")
    return (text + DARKFALLEN_GLUE_STRINGS).encode("utf-8")


def _portrait_image(source_path: Path) -> Image.Image:
    try:
        image = decode_source_face(source_path)
        crop_box = PORTRAIT_CROP_BOX
    except ValueError as error:
        data = source_path.read_bytes()
        if data[:4] != b"BLP2":
            raise
        alpha_depth, alpha_encoding, _, blp_type, width, height = struct.unpack("<4BII", data[8:20])
        if (alpha_depth, alpha_encoding, blp_type) != (1, 0, 1):
            raise error
        offsets = struct.unpack("<16I", data[20:84])
        sizes = struct.unpack("<16I", data[84:148])
        if (width, height) != (256, 128) or sizes[0] != width * height:
            raise error
        indices = data[offsets[0] : offsets[0] + sizes[0]]
        image = Image.frombytes("P", (width, height), indices)
        image.putpalette(data[148:1172], rawmode="BGRA")
        image = image.convert("RGBA")
        image.putalpha(255)
        crop_box = PORTRAIT_CROP_BOX
    return image.crop(crop_box).resize((64, 64), Image.Resampling.LANCZOS)


def _portrait_entries(source: Path, header: bytes) -> dict[str, bytes]:
    """Creation-screen race icons (Interface\\Glues\\CharacterCreate)."""
    entries: dict[str, bytes] = {}
    for file_string, gender, mirrored in FRAME_PORTRAIT_KEYS:
        image = _portrait_image(source / PORTRAIT_SOURCES[gender])
        if mirrored:
            image = ImageOps.mirror(image)
        encoded = encode_portrait(image, header)
        output_name = f"UI-CharacterCreate-{file_string}{gender.title()}.blp"
        validate_portrait(encoded, Path(output_name))
        entries[PORTRAIT_ROOT + output_name] = encoded
    return entries


def _character_frame_portrait_entries(source: Path, header: bytes) -> dict[str, bytes]:
    """Character-select/paper-doll portraits (Interface\\CharacterFrame).

    The client asks for TemporaryPortrait-<Sex>-<ClientFileString>.blp; without these two
    files a Darkfallen character draws the missing-texture placeholder in the select list
    even though the model itself renders in the creator and in game.
    """
    entries: dict[str, bytes] = {}
    for file_string, gender, mirrored in FRAME_PORTRAIT_KEYS:
        image = _portrait_image(source / PORTRAIT_SOURCES[gender])
        if mirrored:
            image = ImageOps.mirror(image)
        encoded = encode_portrait(image, header)
        stem = CHARACTER_FRAME_ROOT + f"TemporaryPortrait-{gender.title()}-{file_string}"
        for name in (stem, stem + ".blp"):
            validate_portrait(encoded, Path(name))
            entries[name] = encoded
    return entries


def _collision_check(existing: dict[str, bytes], updates: dict[str, bytes]) -> tuple[str, ...]:
    by_name = {name.casefold(): (name, payload) for name, payload in existing.items()}
    collisions = []
    for name, payload in updates.items():
        prior = by_name.get(name.casefold())
        if prior is not None and prior[1] == payload:
            collisions.append(prior[0])
        elif prior is not None and name.casefold().startswith("character\\darkfallen\\"):
            raise ValueError(f"archive path collision with different bytes: {name} vs {prior[0]}")
    return tuple(sorted(collisions, key=str.casefold))


def _stage_archive(storm: Storm, source: Path, destination: Path, updates: dict[str, bytes]) -> None:
    shutil.copy2(source, destination)
    storm.replace_archive_entries(destination, updates)


def build_darkfallen_pack(
    root_archive: Path,
    locale_archive: Path,
    output_root: Path,
    source: Path = ASSET_ROOT,
    stormlib: Path = DLL_DEFAULT,
) -> DarkfallenPackReport:
    root_archive = Path(root_archive).resolve()
    locale_archive = Path(locale_archive).resolve()
    output_root = Path(output_root).resolve()
    source = Path(source).resolve()
    if root_archive == locale_archive:
        raise ValueError("root and locale archives must be different")
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    if output_root in root_archive.parents or output_root in locale_archive.parents:
        raise ValueError("output_root must not contain a source archive")
    if not root_archive.is_file() or not locale_archive.is_file():
        raise FileNotFoundError("both source archives are required")

    storm = Storm(stormlib)
    root_entries = _read_archive(storm, root_archive)
    locale_entries = _read_archive(storm, locale_archive)
    _, portrait_header = _find_entry(root_entries, PORTRAIT_ROOT + "UI-CharacterCreate-BloodElfMale.blp")
    assets = collect_assets(source)
    assets.update(_portrait_entries(source, portrait_header))
    assets.update(_character_frame_portrait_entries(source, portrait_header))

    root_dbc_updates = build_dbc_updates(root_entries, source)
    locale_dbc_updates = build_dbc_updates(locale_entries, source)
    shared_ui = {
        key: transform(_find_entry(root_entries, key)[1])
        for key, transform in {
            GLUE_ROOT + "CharacterInfo.lua": patch_character_info,
            GLUE_ROOT + "CharacterCreate.lua": patch_character_create,
            GLUE_ROOT + "CharacterSelect.lua": patch_character_select,
            GLUE_ROOT + "GlueParent.lua": patch_glue_parent,
        }.items()
    }
    root_updates = dict(root_dbc_updates)
    root_updates.update(shared_ui)
    root_updates.update(assets)
    locale_updates = dict(locale_dbc_updates)
    locale_updates.update(
        {
            key: transform(_find_entry(locale_entries, key)[1])
            for key, transform in {
                GLUE_ROOT + "CharacterInfo.lua": patch_character_info,
                GLUE_ROOT + "CharacterCreate.lua": patch_character_create,
                GLUE_ROOT + "CharacterSelect.lua": patch_character_select,
                GLUE_ROOT + "GlueParent.lua": patch_glue_parent,
                GLUE_ROOT + "GlueStrings.lua": patch_glue_strings,
            }.items()
        }
    )
    locale_updates.update(assets)
    collisions = _collision_check(root_entries, assets) + _collision_check(locale_entries, assets)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.tmp-", dir=output_root.parent))
    try:
        _stage_archive(storm, root_archive, temporary_root / ARCHIVE_NAME, root_updates)
        _stage_archive(storm, locale_archive, temporary_root / LOCALE_ARCHIVE_NAME, locale_updates)
        os.replace(temporary_root, output_root)
    except BaseException:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise
    return DarkfallenPackReport(
        race_ids=DARKFALLEN_RACE_IDS,
        root_updates=root_updates,
        locale_updates=locale_updates,
        collisions=tuple(sorted(set(collisions), key=str.casefold)),
        staged_root=str(output_root),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-contract", action="store_true")
    parser.add_argument("--root-archive", type=Path, default=ROOT / ARCHIVE_NAME)
    parser.add_argument("--locale-archive", type=Path, default=ROOT / LOCALE_ARCHIVE_NAME)
    parser.add_argument("--source", type=Path, default=ASSET_ROOT)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument(
        "--spell-sql-out",
        type=Path,
        help="read Spell.dbc from --root-archive and write the pending_db_world SQL for the racial spells",
    )
    args = parser.parse_args()
    if args.print_contract:
        print(json.dumps(contract(), sort_keys=True))
        return
    if args.spell_sql_out is not None:
        spell_table = read_archive_entry(Storm(args.stormlib), args.root_archive, "DBFilesClient\\Spell.dbc")
        args.spell_sql_out.parent.mkdir(parents=True, exist_ok=True)
        args.spell_sql_out.write_text(render_spell_sql(spell_table), encoding="utf-8", newline="\n")
        print(f"wrote {args.spell_sql_out}")
        if args.output_root is None:
            return
    if args.output_root is None:
        parser.error("--output-root is required")
    report = build_darkfallen_pack(args.root_archive, args.locale_archive, args.output_root, args.source, args.stormlib)
    print(
        json.dumps(
            {
                "staged_root": report.staged_root,
                "root_updates": len(report.root_updates),
                "locale_updates": len(report.locale_updates),
                "collisions": list(report.collisions),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
