from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import _read_string, _set_u32, _table, _u32
from cars_mount_pack import DLL_DEFAULT, Storm, _m2_texture_records, rewrite_m2_texture_paths
from wod_model_migration import archive_names

DEFAULT_CLIENT = Path(r"G:\3.3.5a - Dev")
DEFAULT_F_DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)")
DEFAULT_ASCENSION = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted")
DEFAULT_DARKFALLEN = Path(r"G:\New Folder (2)\DarkfallenAttempts\Upscaled")

HIGH_ELF_RACE = 13
BLOOD_ELF_RACE = 10
DARKFALLEN_RACES = frozenset({43, 44})

NPC_MODEL_PATHS = {
    6000: r"Character\NightElf\Female\NightElfFemaleNPC.m2",
    6001: r"Character\Human\Male\HumanMaleNPC.m2",
    6002: r"Character\Gnome\Female\GnomeFemaleNPC.m2",
    6003: r"Character\Gnome\Male\GnomeMaleNPC.m2",
    6004: r"Character\NightElf\Male\NightElfMaleNPC.m2",
    6005: r"Character\Human\Female\HumanFemaleNPC.m2",
    6006: r"Character\Dwarf\Male\DwarfMaleNPC.m2",
    6007: r"Character\Dwarf\Female\DwarfFemaleNPC.m2",
    6008: r"Character\Orc\Male\OrcMaleNPC.m2",
    6009: r"Character\Orc\Female\OrcFemaleNPC.m2",
    6010: r"Character\Troll\Male\TrollMaleNPC.m2",
    6011: r"Character\Troll\Female\TrollFemaleNPC.m2",
    6012: r"Character\Tauren\Male\TaurenMaleNPC.m2",
    6013: r"Character\Tauren\Female\TaurenFemaleNPC.m2",
    6014: r"Character\BloodElf\Male\BloodElfMaleNPC.m2",
    6015: r"Character\BloodElf\Female\BloodElfFemaleNPC.m2",
    6016: r"Character\Scourge\Male\ScourgeMaleNPC.m2",
    6017: r"Character\Scourge\Female\ScourgeFemaleNPC.m2",
    6018: r"Character\Draenei\Male\DraeneiMaleNPC.m2",
    6019: r"Character\Draenei\Female\DraeneiFemaleNPC.m2",
}

PLAYER_DISPLAY_IDS = frozenset(
    {
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        1478,
        1479,
        1563,
        1564,
        15475,
        15476,
        16125,
        16126,
    }
)

DBC_TABLES = (
    "CharSections",
    "CharHairGeosets",
    "CreatureDisplayInfo",
    "CreatureModelData",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def wow_processes(client_root: Path) -> list[dict[str, str | int]]:
    script = (
        "Get-Process | Where-Object { $_.Path -like '"
        + str(client_root).replace("'", "''")
        + "*' } | Select-Object Id,ProcessName,Path | ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    text = result.stdout.strip()
    if not text:
        return []
    value = json.loads(text)
    return value if isinstance(value, list) else [value]


def read_tables(storm: Storm, archive: Path) -> dict[str, bytes]:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        result: dict[str, bytes] = {}
        for name in DBC_TABLES:
            key = f"dbfilesclient\\{name.lower()}.dbc"
            actual = names.get(key)
            if actual is None:
                raise KeyError(f"{archive} missing DBFilesClient\\{name}.dbc")
            result[name] = storm.read(handle, actual)
        return result
    finally:
        storm.dll.SFileCloseArchive(handle)


def read_donor_table(storm: Storm, archive: Path, name: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        return storm.read(handle, names[f"dbfilesclient\\{name.lower()}.dbc"])
    finally:
        storm.dll.SFileCloseArchive(handle)


def string_cache(pool: bytes) -> dict[bytes, int]:
    result: dict[bytes, int] = {b"": 0}
    cursor = 0
    while cursor < len(pool):
        end = pool.find(b"\0", cursor)
        if end < 0:
            break
        value = pool[cursor:end]
        result.setdefault(value, cursor)
        cursor = end + 1
    return result


def append_string(pool: bytearray, cache: dict[bytes, int], value: bytes) -> int:
    existing = cache.get(value)
    if existing is not None:
        return existing
    offset = len(pool)
    pool.extend(value + b"\0")
    cache[value] = offset
    return offset


def patch_high_elf_appearance(data: dict[str, bytes]) -> tuple[dict[str, bytes], dict[str, int]]:
    output = dict(data)

    # High Elves share the exact Blood Elf HD model/display IDs. Their appearance
    # tables therefore need to be a race-13 view of the Blood Elf rows, not the
    # old Turtle/StoreHeads/StoreSkins customization set. Mixing those rows with
    # BloodElf2 textures produces the patchwork body/face seen in character select.
    #
    # CharHairGeosets: expose only the Blood Elf-supported hair geosets. Reuse
    # High Elf row IDs where possible so existing references remain stable.
    hair = _table(data["CharHairGeosets"], "CharHairGeosets")
    blood = {
        (_u32(row, 2), _u32(row, 3)): row
        for row in hair.records
        if _u32(row, 1) == BLOOD_ELF_RACE
    }
    high_existing = {
        (_u32(row, 2), _u32(row, 3)): row
        for row in hair.records
        if _u32(row, 1) == HIGH_ELF_RACE
    }
    untouched = [row for row in hair.records if _u32(row, 1) != HIGH_ELF_RACE]
    cloned_hair: list[bytes] = []
    next_id = max(_u32(row, 0) for row in hair.records) + 1
    for key, donor in sorted(blood.items()):
        existing = high_existing.get(key)
        row_id = _u32(existing, 0) if existing is not None else next_id
        if existing is None:
            next_id += 1
        clone = _set_u32(donor, 0, row_id)
        clone = _set_u32(clone, 1, HIGH_ELF_RACE)
        cloned_hair.append(clone)
    output["CharHairGeosets"] = hair.build(untouched + cloned_hair, hair.strings)

    # CharSections: clone the entire Blood Elf appearance surface, not only hair.
    # Race 13 was carrying hundreds of extra StoreHeads/StoreSkins/legacy BloodElf
    # rows. Those extra skin/face/underwear choices are incompatible with the HD
    # BloodElf2 model and are the direct cause of mismatched body regions.
    sections = _table(data["CharSections"], "CharSections")
    blood_rows = [row for row in sections.records if _u32(row, 1) == BLOOD_ELF_RACE]
    high_rows = [row for row in sections.records if _u32(row, 1) == HIGH_ELF_RACE]
    high_by_key = {
        (_u32(row, 2), _u32(row, 3), _u32(row, 8), _u32(row, 9)): row
        for row in high_rows
    }
    untouched = [row for row in sections.records if _u32(row, 1) != HIGH_ELF_RACE]
    next_id = max(_u32(row, 0) for row in sections.records) + 1
    cloned_sections: list[bytes] = []
    reused_ids = 0
    created_ids = 0
    for donor in blood_rows:
        key = (_u32(donor, 2), _u32(donor, 3), _u32(donor, 8), _u32(donor, 9))
        existing = high_by_key.get(key)
        if existing is not None:
            row_id = _u32(existing, 0)
            reused_ids += 1
        else:
            row_id = next_id
            next_id += 1
            created_ids += 1
        clone = _set_u32(donor, 0, row_id)
        clone = _set_u32(clone, 1, HIGH_ELF_RACE)
        cloned_sections.append(clone)
    output["CharSections"] = sections.build(untouched + cloned_sections, sections.strings)

    return output, {
        "hair_geoset_rows": len(cloned_hair),
        "charsection_rows_before": len(high_rows),
        "charsection_rows_after": len(cloned_sections),
        "charsection_ids_reused": reused_ids,
        "charsection_ids_created": created_ids,
        "legacy_charsection_rows_removed": len(high_rows) - reused_ids,
    }


def donor_npc_payloads(storm: Storm, donor_root: Path) -> tuple[dict[str, bytes], set[str], dict[int, bytes], bytes]:
    patch_x = donor_root / "Data" / "patch-x.mpq"
    locale_x = donor_root / "Data" / "enUS" / "patch-enUS-x.mpq"
    handle = storm.open_archive(patch_x)
    try:
        names = archive_names(storm, handle)
        entries: dict[str, bytes] = {}
        m2_payloads: dict[str, bytes] = {}
        for key, actual in names.items():
            if "character" not in key or "npc" not in key:
                continue
            if not key.endswith((".m2", ".skin", ".anim")):
                continue
            payload = storm.read(handle, actual)
            entries[actual] = payload
            if key.endswith(".m2"):
                m2_payloads[actual] = payload
        direct_refs: set[str] = set()
        for payload in m2_payloads.values():
            if payload[:4] != b"MD20" or struct.unpack_from("<I", payload, 4)[0] != 264:
                raise ValueError("donor NPC M2 is not native WotLK MD20/264")
            for _, texture_type, name in _m2_texture_records(payload):
                if texture_type == 0 and name:
                    direct_refs.add(name.decode("latin1").replace("/", "\\"))
    finally:
        storm.dll.SFileCloseArchive(handle)

    if len(m2_payloads) != 20:
        raise ValueError(f"expected 20 donor NPC M2 files, found {len(m2_payloads)}")

    donor_model = read_donor_table(storm, locale_x, "CreatureModelData")
    donor_display = read_donor_table(storm, locale_x, "CreatureDisplayInfo")
    model_table = _table(donor_model, "CreatureModelData")
    model_rows = {_u32(row, 0): row for row in model_table.records if _u32(row, 0) in NPC_MODEL_PATHS}
    if set(model_rows) != set(NPC_MODEL_PATHS):
        raise ValueError("donor NPC CreatureModelData rows 6000-6019 are incomplete")
    return entries, direct_refs, model_rows, donor_display


def merge_npc_dbcs(
    data: dict[str, bytes],
    donor_model_rows: dict[int, bytes],
    donor_display_data: bytes,
) -> tuple[dict[str, bytes], dict[str, int]]:
    output = dict(data)

    # Add/update dedicated model IDs 6000-6019 without touching stock player
    # model IDs. The repair is intentionally idempotent because it may be run
    # again against a client that already has the first repair installed.
    models = _table(data["CreatureModelData"], "CreatureModelData")
    existing_by_id = {_u32(row, 0): row for row in models.records}
    for model_id, path in NPC_MODEL_PATHS.items():
        existing = existing_by_id.get(model_id)
        if existing is None:
            continue
        existing_path = _read_string(models.strings, _u32(existing, 2)).decode("latin1")
        if existing_path.casefold() != path.casefold():
            raise ValueError(
                f"NPC model ID {model_id} is already used by a different path: {existing_path}"
            )

    pool = bytearray(models.strings)
    cache = string_cache(models.strings)
    desired_models: dict[int, bytes] = {}
    added_model_ids: set[int] = set()
    replaced_model_ids: set[int] = set()
    for model_id, path in sorted(NPC_MODEL_PATHS.items()):
        donor = donor_model_rows[model_id]
        clone = donor
        path_offset = append_string(pool, cache, path.encode("ascii"))
        clone = _set_u32(clone, 2, path_offset)
        desired_models[model_id] = clone
        if model_id in existing_by_id:
            replaced_model_ids.add(model_id)
        else:
            added_model_ids.add(model_id)

    model_rows = [desired_models.get(_u32(row, 0), row) for row in models.records]
    model_rows.extend(desired_models[model_id] for model_id in sorted(added_model_ids))
    output["CreatureModelData"] = models.build(model_rows, bytes(pool))

    # The donor redirects NPC display rows to the dedicated model family. Only
    # copy the ModelID field so Esteria-specific scale/extra/item metadata stays.
    donor_displays = _table(donor_display_data, "CreatureDisplayInfo")
    desired = {
        _u32(row, 0): _u32(row, 1)
        for row in donor_displays.records
        if _u32(row, 1) in NPC_MODEL_PATHS
    }
    if PLAYER_DISPLAY_IDS & set(desired):
        raise ValueError("donor NPC mapping unexpectedly contains a player display ID")

    displays = _table(data["CreatureDisplayInfo"], "CreatureDisplayInfo")
    changed = 0
    missing = 0
    result: list[bytes] = []
    for row in displays.records:
        display_id = _u32(row, 0)
        model_id = desired.get(display_id)
        if model_id is None:
            result.append(row)
            continue
        replacement = _set_u32(row, 1, model_id)
        result.append(replacement)
        changed += int(replacement != row)
    present_ids = {_u32(row, 0) for row in displays.records}
    missing = len(set(desired) - present_ids)
    output["CreatureDisplayInfo"] = displays.build(result, displays.strings)

    return output, {
        "npc_model_rows_added": len(added_model_ids),
        "npc_model_rows_refreshed": len(replaced_model_ids),
        "npc_display_rows_targeted": len(desired),
        "npc_display_rows_changed": changed,
        "npc_display_rows_missing_from_esteria": missing,
    }


def patch_darkfallen_hd_skin_sections(data: dict[str, bytes]) -> tuple[dict[str, bytes], dict[str, int]]:
    """Give Darkfallen the second HD body-skin layer expected by BloodElf2.

    The legacy Darkfallen CharSections only populated the primary skin texture.
    The WoD/HD Blood Elf model uses a second ``*_Extra.blp`` layer for parts of
    the body mesh. Leaving that field empty makes those UV islands fall back to
    an untextured/light appearance, most visibly on the ears and neck.
    """

    output = dict(data)
    sections = _table(data["CharSections"], "CharSections")
    pool = bytearray(sections.strings)
    cache = string_cache(sections.strings)
    changed = 0
    rows: list[bytes] = []

    for row in sections.records:
        if _u32(row, 1) not in DARKFALLEN_RACES or _u32(row, 3) != 0:
            rows.append(row)
            continue

        primary = _read_string(sections.strings, _u32(row, 4)).decode("latin1")
        if not primary:
            rows.append(row)
            continue
        if not primary.casefold().endswith(".blp"):
            raise ValueError(f"unexpected Darkfallen skin texture path: {primary}")

        extra = primary[:-4] + "_Extra.blp"
        replacement = _set_u32(row, 5, append_string(pool, cache, extra.encode("latin1")))
        rows.append(replacement)
        changed += int(replacement != row)

    output["CharSections"] = sections.build(rows, bytes(pool))
    return output, {"hd_skin_extra_rows": changed}


def darkfallen_texture_map(
    charsections: bytes,
    darkfallen_root: Path,
) -> tuple[dict[str, bytes], list[str]]:
    table = _table(charsections, "CharSections")
    refs: set[str] = set()
    for row in table.records:
        if _u32(row, 1) not in DARKFALLEN_RACES:
            continue
        for field in (4, 5, 6):
            value = _read_string(table.strings, _u32(row, field)).decode("latin1")
            if value and value.replace("/", "\\").casefold().startswith("character\\darkfallen\\"):
                refs.add(value.replace("/", "\\"))

    files: dict[tuple[str, str], Path] = {}
    for sex in ("male", "female"):
        root = darkfallen_root / sex
        for path in root.glob("*.blp"):
            files[(sex, path.name.casefold())] = path

    result: dict[str, bytes] = {}
    unresolved: list[str] = []
    for target in sorted(refs, key=str.casefold):
        parts = target.split("\\")
        sex = parts[2].casefold() if len(parts) >= 4 else ""
        basename = parts[-1]
        candidates = [
            basename,
            basename.replace("DarkfallenMale", "BloodElfMale").replace("DarkfallenFemale", "BloodElfFemale"),
        ]
        source = next(
            (files[(sex, candidate.casefold())] for candidate in candidates if (sex, candidate.casefold()) in files),
            None,
        )
        if source is None:
            unresolved.append(target)
            continue
        result[target] = source.read_bytes()
    return result, unresolved


def darkfallen_alias_assets(darkfallen_root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    glow_sources = darkfallen_root / "_LegacyDarkfallenGlowSources"
    glow_targets = {
        "Male_DarkfallenEyeGlow.blp": r"Character\Darkfallen\Male\DarkfallenEyeGlow.blp",
        "Female_DarkfallenEyeGlow.blp": r"Character\Darkfallen\Female\DarkfallenEyeGlow.blp",
        "Female_DarkfallenDKGlow.blp": r"Character\Darkfallen\Female\DarkfallenDKGlow.blp",
    }
    for source_name, destination in glow_targets.items():
        source = glow_sources / source_name
        if not source.is_file():
            raise FileNotFoundError(f"missing Darkfallen legacy glow source: {source}")
        result[destination] = source.read_bytes()

    for sex in ("male", "female"):
        cap = sex.capitalize()
        prefix = f"Darkfallen{cap}".casefold()
        for source in (darkfallen_root / sex).iterdir():
            if not source.is_file() or source.suffix.casefold() not in {".m2", ".skin", ".anim"}:
                continue
            if not source.name.casefold().startswith(prefix):
                continue
            destination = f"Character\\Darkfallen\\{cap}\\{source.name}"
            payload = source.read_bytes()
            if source.suffix.casefold() == ".m2":
                if sex == "male":
                    payload = rewrite_m2_texture_paths(
                        payload,
                        {
                            b"character\\bloodelf\\eyes00_00_3492879.blp": r"Character\Darkfallen\Male\DarkfallenEyeGlow.blp",
                            b"character\\bloodelf\\male\\bloodelfmale_hd_eyereflect.blp": r"Character\Darkfallen\Male\DarkfallenEyeGlow.blp",
                        },
                    )
                else:
                    payload = rewrite_m2_texture_paths(
                        payload,
                        {
                            b"character/bloodelf/eyes00_00_3492879.blp": r"Character\Darkfallen\Female\DarkfallenEyeGlow.blp",
                            b"character\\bloodelf\\female\\bloodelffemale_hd_eyereflect.blp": r"Character\Darkfallen\Female\DarkfallenDKGlow.blp",
                        },
                    )
            result[destination] = payload
    if len(result) != 468:
        raise ValueError(f"expected 468 Darkfallen HD alias/glow assets, found {len(result)}")
    return result


def merge_darkfallen_models(data: dict[str, bytes]) -> tuple[dict[str, bytes], dict[str, str]]:
    output = dict(data)
    table = _table(data["CreatureModelData"], "CreatureModelData")
    by_id = {_u32(row, 0): row for row in table.records}
    mapping = {
        3658: (2208, r"Character\Darkfallen\Male\DarkfallenMale.m2"),
        3659: (2209, r"Character\Darkfallen\Female\DarkfallenFemale.m2"),
    }
    pool = bytearray(table.strings)
    cache = string_cache(table.strings)
    replacements: dict[int, bytes] = {}
    for destination, (source, path) in mapping.items():
        donor = by_id.get(source)
        if donor is None or destination not in by_id:
            raise ValueError(f"Darkfallen model metadata source/destination missing: {destination} <- {source}")
        clone = _set_u32(donor, 0, destination)
        clone = _set_u32(clone, 2, append_string(pool, cache, path.encode("ascii")))
        replacements[destination] = clone
    rows = [replacements.get(_u32(row, 0), row) for row in table.records]
    output["CreatureModelData"] = table.build(rows, bytes(pool))
    return output, {str(key): value[1] for key, value in mapping.items()}


def archive_has(storm: Storm, archive: Path, path: str) -> bool:
    handle = storm.open_archive(archive)
    try:
        try:
            storm.read(handle, path)
            return True
        except OSError:
            return False
    finally:
        storm.dll.SFileCloseArchive(handle)


def donor_direct_dependency(storm: Storm, donor_root: Path, path: str) -> bytes | None:
    for archive in (
        donor_root / "Data" / "patch-x.mpq",
        donor_root / "Data" / "common.MPQ",
    ):
        handle = storm.open_archive(archive)
        try:
            try:
                return storm.read(handle, path)
            except OSError:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None


def ascension_direct_dependency(ascension_root: Path, path: str) -> bytes | None:
    root = ascension_root / "patch-CHA.mpq"
    wanted = path.replace("/", "\\").casefold()
    for source in root.rglob("*"):
        if not source.is_file():
            continue
        rel = str(source.relative_to(root)).replace("/", "\\").casefold()
        if rel == wanted:
            return source.read_bytes()
    return None


def validate_staged(
    storm: Storm,
    patch_z: Path,
    locale_z: Path,
    darkfallen_assets: dict[str, bytes],
    npc_entries: dict[str, bytes],
    expected_npc_displays: int,
) -> dict[str, object]:
    tables_z = read_tables(storm, patch_z)
    tables_l = read_tables(storm, locale_z)
    report: dict[str, object] = {}

    for label, tables in (("patch-Z", tables_z), ("patch-enUS-Z", tables_l)):
        models = _table(tables["CreatureModelData"], "CreatureModelData")
        model_ids = {_u32(row, 0): row for row in models.records}
        for model_id, path in NPC_MODEL_PATHS.items():
            row = model_ids.get(model_id)
            if row is None:
                raise ValueError(f"{label}: missing NPC model row {model_id}")
            actual = _read_string(models.strings, _u32(row, 2)).decode("latin1")
            if actual.casefold() != path.casefold():
                raise ValueError(f"{label}: model {model_id} path mismatch: {actual}")
        for model_id, path in ((3658, r"Character\Darkfallen\Male\DarkfallenMale.m2"), (3659, r"Character\Darkfallen\Female\DarkfallenFemale.m2")):
            row = model_ids[model_id]
            actual = _read_string(models.strings, _u32(row, 2)).decode("latin1")
            if actual.casefold() != path.casefold():
                raise ValueError(f"{label}: Darkfallen model {model_id} path mismatch")

        displays = _table(tables["CreatureDisplayInfo"], "CreatureDisplayInfo")
        npc_count = sum(1 for row in displays.records if _u32(row, 1) in NPC_MODEL_PATHS)
        if npc_count != expected_npc_displays:
            raise ValueError(f"{label}: expected {expected_npc_displays} NPC display rows, found {npc_count}")
        if any(_u32(row, 0) in PLAYER_DISPLAY_IDS and _u32(row, 1) in NPC_MODEL_PATHS for row in displays.records):
            raise ValueError(f"{label}: player display was redirected to an NPC model")

        hair = _table(tables["CharHairGeosets"], "CharHairGeosets")
        high_keys = {
            (_u32(row, 2), _u32(row, 3), _u32(row, 4), _u32(row, 5))
            for row in hair.records
            if _u32(row, 1) == HIGH_ELF_RACE
        }
        blood_keys = {
            (_u32(row, 2), _u32(row, 3), _u32(row, 4), _u32(row, 5))
            for row in hair.records
            if _u32(row, 1) == BLOOD_ELF_RACE
        }
        if high_keys != blood_keys:
            raise ValueError(f"{label}: High Elf hair geosets do not exactly match Blood Elf")

        sections = _table(tables["CharSections"], "CharSections")
        blood_sections: dict[tuple[int, int, int, int], tuple[bytes, bytes, bytes, int]] = {}
        high_sections: dict[tuple[int, int, int, int], tuple[bytes, bytes, bytes, int]] = {}
        for row in sections.records:
            race = _u32(row, 1)
            if race not in {BLOOD_ELF_RACE, HIGH_ELF_RACE}:
                continue
            key = (_u32(row, 2), _u32(row, 3), _u32(row, 8), _u32(row, 9))
            value = (
                _read_string(sections.strings, _u32(row, 4)),
                _read_string(sections.strings, _u32(row, 5)),
                _read_string(sections.strings, _u32(row, 6)),
                _u32(row, 7),
            )
            (blood_sections if race == BLOOD_ELF_RACE else high_sections)[key] = value
        if high_sections != blood_sections:
            missing = sorted(set(blood_sections) - set(high_sections))
            extra = sorted(set(high_sections) - set(blood_sections))
            mismatched = sorted(
                key
                for key in set(high_sections) & set(blood_sections)
                if high_sections[key] != blood_sections[key]
            )
            raise ValueError(
                f"{label}: High Elf CharSections do not exactly mirror Blood Elf "
                f"(missing={len(missing)} extra={len(extra)} mismatched={len(mismatched)})"
            )

        dark_skin_rows = [
            row
            for row in sections.records
            if _u32(row, 1) in DARKFALLEN_RACES and _u32(row, 3) == 0
        ]
        dark_missing_extra = []
        for row in dark_skin_rows:
            extra_path = _read_string(sections.strings, _u32(row, 5)).decode("latin1")
            if not extra_path.casefold().endswith("_extra.blp"):
                dark_missing_extra.append((_u32(row, 0), extra_path))
        if dark_missing_extra:
            raise ValueError(f"{label}: Darkfallen HD skin rows missing *_Extra layer: {dark_missing_extra[:8]}")

        report[label] = {
            "npc_display_rows": npc_count,
            "high_elf_hair_geosets": len(high_keys),
            "high_elf_charsections": len(high_sections),
            "darkfallen_hd_skin_rows": len(dark_skin_rows),
        }

    handle = storm.open_archive(patch_z)
    try:
        names = archive_names(storm, handle)
        for path, payload in darkfallen_assets.items():
            actual = names.get(path.casefold(), path)
            if storm.read(handle, actual) != payload:
                raise ValueError(f"Darkfallen asset validation failed: {path}")
        for path, payload in npc_entries.items():
            actual = names.get(path.casefold(), path)
            if storm.read(handle, actual) != payload:
                raise ValueError(f"NPC asset validation failed: {path}")
    finally:
        storm.dll.SFileCloseArchive(handle)

    report["assets"] = {
        "darkfallen_verified": len(darkfallen_assets),
        "npc_verified": len(npc_entries),
    }
    return report


def stage(args: argparse.Namespace) -> Path:
    client = args.client_root.resolve()
    donor = args.f_donor.resolve()
    ascension = args.ascension_root.resolve()
    darkfallen = args.darkfallen_root.resolve()
    storm = Storm(args.stormlib)

    patch_z = client / "Data" / "patch-Z.MPQ"
    locale_z = client / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    staging = client / "Data" / "Staging" / f"hd-npc-highelf-darkfallen-{stamp}"
    staging.mkdir(parents=True, exist_ok=False)
    staged_z = staging / "patch-Z.MPQ"
    staged_l = staging / "patch-enUS-Z.MPQ"

    # Windows WoW holds MPQs open read-only; normal file copying remains safe.
    shutil.copy2(patch_z, staged_z)
    shutil.copy2(locale_z, staged_l)
    source_hashes = {"patch-Z": sha256(patch_z), "patch-enUS-Z": sha256(locale_z)}
    if sha256(staged_z) != source_hashes["patch-Z"] or sha256(staged_l) != source_hashes["patch-enUS-Z"]:
        raise RuntimeError("staging copy hash mismatch")

    base_z = read_tables(storm, staged_z)
    base_l = read_tables(storm, staged_l)

    npc_entries, npc_refs, donor_model_rows, donor_display = donor_npc_payloads(storm, donor)
    dark_alias = darkfallen_alias_assets(darkfallen)

    fixed: dict[str, dict[str, bytes]] = {}
    reports: dict[str, object] = {}
    for label, base in (("patch-Z", base_z), ("patch-enUS-Z", base_l)):
        current, high_report = patch_high_elf_appearance(base)
        current, dark_skin_report = patch_darkfallen_hd_skin_sections(current)
        current, npc_report = merge_npc_dbcs(current, donor_model_rows, donor_display)
        current, dark_report = merge_darkfallen_models(current)
        fixed[label] = current
        reports[label] = {
            "high_elf": high_report,
            "darkfallen_skin": dark_skin_report,
            "npc": npc_report,
            "darkfallen_models": dark_report,
        }

    dark_textures, dark_unresolved = darkfallen_texture_map(fixed["patch-Z"]["CharSections"], darkfallen)

    direct_assets: dict[str, bytes] = {}
    unresolved_direct: list[str] = []
    # Resolve named NPC dependencies only if they are absent from the staged client.
    for path in sorted(npc_refs, key=str.casefold):
        if archive_has(storm, staged_z, path):
            continue
        payload = donor_direct_dependency(storm, donor, path)
        if payload is None:
            unresolved_direct.append(path)
        else:
            direct_assets[path] = payload

    # Darkfallen HD aliases use Ascension Blood Elf type-0 textures.
    for payload in (dark_alias[r"Character\Darkfallen\Male\DarkfallenMale.m2"], dark_alias[r"Character\Darkfallen\Female\DarkfallenFemale.m2"]):
        for _, texture_type, name in _m2_texture_records(payload):
            if texture_type != 0 or not name:
                continue
            path = name.decode("latin1").replace("/", "\\")
            if archive_has(storm, staged_z, path) or path in direct_assets:
                continue
            source = ascension_direct_dependency(ascension, path)
            if source is None:
                unresolved_direct.append(path)
            else:
                direct_assets[path] = source

    replacements_z = {
        f"DBFilesClient\\{name}.dbc": payload
        for name, payload in fixed["patch-Z"].items()
        if payload != base_z[name]
    }
    replacements_l = {
        f"DBFilesClient\\{name}.dbc": payload
        for name, payload in fixed["patch-enUS-Z"].items()
        if payload != base_l[name]
    }
    all_assets = dict(npc_entries)
    all_assets.update(direct_assets)
    all_assets.update(dark_alias)
    all_assets.update(dark_textures)
    replacements_z.update(all_assets)

    storm.replace_archive_entries(staged_z, replacements_z)
    storm.replace_archive_entries(staged_l, replacements_l)

    expected_npc_displays = reports["patch-Z"]["npc"]["npc_display_rows_targeted"]
    validation = validate_staged(storm, staged_z, staged_l, {**dark_alias, **dark_textures}, npc_entries, expected_npc_displays)

    manifest = {
        "created": stamp,
        "source_hashes": source_hashes,
        "staged_hashes": {"patch-Z": sha256(staged_z), "patch-enUS-Z": sha256(staged_l)},
        "source_processes": wow_processes(client),
        "reports": reports,
        "assets": {
            "npc_family_files": len(npc_entries),
            "npc_direct_dependencies_added": len(direct_assets),
            "npc_direct_dependencies_unresolved": sorted(set(unresolved_direct), key=str.casefold),
            "darkfallen_alias_files": len(dark_alias),
            "darkfallen_texture_overrides": len(dark_textures),
            "darkfallen_unresolved_texture_refs": dark_unresolved,
        },
        "validation": validation,
    }
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"staging": str(staging), **manifest}, indent=2))
    return staging


def apply_staged(args: argparse.Namespace, staging: Path) -> None:
    client = args.client_root.resolve()
    processes = wow_processes(client)
    if processes:
        raise RuntimeError(f"WoW/client process is still running: {processes}")

    manifest_path = staging / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    patch_z = client / "Data" / "patch-Z.MPQ"
    locale_z = client / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    staged_z = staging / "patch-Z.MPQ"
    staged_l = staging / "patch-enUS-Z.MPQ"
    if not staged_z.exists() or not staged_l.exists():
        raise FileNotFoundError("staged MPQs are missing")

    live_hashes = {"patch-Z": sha256(patch_z), "patch-enUS-Z": sha256(locale_z)}
    if live_hashes != manifest["source_hashes"]:
        raise RuntimeError(f"live archives changed since staging: {live_hashes} != {manifest['source_hashes']}")
    if sha256(staged_z) != manifest["staged_hashes"]["patch-Z"] or sha256(staged_l) != manifest["staged_hashes"]["patch-enUS-Z"]:
        raise RuntimeError("staged archive hash mismatch")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = client / "Backups" / f"hd-npc-highelf-darkfallen-{stamp}"
    (backup / "Data" / "enUS").mkdir(parents=True, exist_ok=False)
    shutil.copy2(patch_z, backup / "Data" / "patch-Z.MPQ")
    shutil.copy2(locale_z, backup / "Data" / "enUS" / "patch-enUS-Z.MPQ")
    shutil.copy2(manifest_path, backup / "staging-manifest.json")
    if sha256(backup / "Data" / "patch-Z.MPQ") != live_hashes["patch-Z"]:
        raise RuntimeError("patch-Z backup hash mismatch")
    if sha256(backup / "Data" / "enUS" / "patch-enUS-Z.MPQ") != live_hashes["patch-enUS-Z"]:
        raise RuntimeError("locale backup hash mismatch")

    # Keep staged files for audit by copying validated bytes into temporary live siblings.
    tmp_z = client / "Data" / "patch-Z.MPQ.hd-next"
    tmp_l = client / "Data" / "enUS" / "patch-enUS-Z.MPQ.hd-next"
    shutil.copy2(staged_z, tmp_z)
    shutil.copy2(staged_l, tmp_l)
    if sha256(tmp_z) != manifest["staged_hashes"]["patch-Z"] or sha256(tmp_l) != manifest["staged_hashes"]["patch-enUS-Z"]:
        raise RuntimeError("final temporary archive copy hash mismatch")
    os.replace(tmp_z, patch_z)
    os.replace(tmp_l, locale_z)

    final = {
        "backup": str(backup),
        "live_hashes_after": {"patch-Z": sha256(patch_z), "patch-enUS-Z": sha256(locale_z)},
        "staging": str(staging),
    }
    if final["live_hashes_after"] != manifest["staged_hashes"]:
        raise RuntimeError("live archives do not match staged hashes after install")
    (backup / "install-result.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair HD NPCs, High Elf hair, and stage HD Darkfallen assets")
    parser.add_argument("--client-root", type=Path, default=DEFAULT_CLIENT)
    parser.add_argument("--f-donor", type=Path, default=DEFAULT_F_DONOR)
    parser.add_argument("--ascension-root", type=Path, default=DEFAULT_ASCENSION)
    parser.add_argument("--darkfallen-root", type=Path, default=DEFAULT_DARKFALLEN)
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--stage-only", action="store_true")
    parser.add_argument("--apply-staged", type=Path)
    args = parser.parse_args()

    if args.apply_staged:
        apply_staged(args, args.apply_staged.resolve())
        return 0
    stage(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
