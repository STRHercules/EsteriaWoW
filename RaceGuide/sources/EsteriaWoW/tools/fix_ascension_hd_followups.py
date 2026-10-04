from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import (  # noqa: E402
    NPC_STOCK_TO_HD_MODEL,
    _read_string,
    _rebase_strings,
    _set_u32,
    _table,
    _u32,
)
from cars_mount_pack import DLL_DEFAULT, Storm, _m2_texture_records  # noqa: E402
from wod_character_appearance_repair import changed_fields, repair_row  # noqa: E402
from wod_model_migration import archive_names  # noqa: E402

DEFAULT_CLIENT = Path(r"G:\3.3.5a - Dev")
DEFAULT_ASCENSION = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted")

HIGH_ELF_RACE = 13
BLOOD_ELF_RACE = 10
STOCK_RACES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 10, 11})

DBC_TABLES = (
    "CharSections",
    "CharHairGeosets",
    "CharHairTextures",
    "CharacterFacialHairStyles",
    "BarberShopStyle",
    "CreatureDisplayInfo",
    "CreatureDisplayInfoExtra",
)

RACE2_MODELS = (
    ("Human2", "Male", "HumanMale2"),
    ("Human2", "Female", "HumanFemale2"),
    ("Orc2", "Male", "OrcMale2"),
    ("Orc2", "Female", "OrcFemale2"),
    ("Dwarf2", "Male", "DwarfMale2"),
    ("Dwarf2", "Female", "DwarfFemale2"),
    ("NightElf2", "Male", "NightElfMale2"),
    ("NightElf2", "Female", "NightElfFemale2"),
    ("Scourge2", "Male", "ScourgeMale2"),
    ("Scourge2", "Female", "ScourgeFemale2"),
    ("Tauren2", "Male", "TaurenMale2"),
    ("Tauren2", "Female", "TaurenFemale2"),
    ("Gnome2", "Male", "GnomeMale2"),
    ("Gnome2", "Female", "GnomeFemale2"),
    ("Troll2", "Male", "TrollMale2"),
    ("Troll2", "Female", "TrollFemale2"),
    ("BloodElf2", "Male", "BloodElfMale2"),
    ("BloodElf2", "Female", "BloodElfFemale2"),
    ("Draenei2", "Male", "DraeneiMale2"),
    ("Draenei2", "Female", "DraeneiFemale2"),
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


def wow_running() -> bool:
    result = subprocess.run(
        ["cmd.exe", "/c", "tasklist", "/FI", "IMAGENAME eq Wow.exe", "/NH"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return "wow.exe" in result.stdout.casefold()


def mysql_scalar(sql: str) -> int:
    result = subprocess.run(
        [
            "docker",
            "exec",
            "ac-database",
            "mysql",
            "-uroot",
            "-ppassword",
            "-N",
            "-B",
            "-e",
            sql,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return int(result.stdout.strip() or "0")


def docker_copy_to_worldserver(source: Path, destination: str) -> None:
    temporary = "/tmp/esteria-ascension-hd-followup"
    subprocess.run(["docker", "cp", str(source), f"ac-worldserver:{temporary}"], check=True)
    subprocess.run(
        ["docker", "exec", "-u", "0", "ac-worldserver", "mv", "-f", temporary, destination],
        check=True,
    )
    subprocess.run(
        ["docker", "exec", "-u", "0", "ac-worldserver", "chmod", "755", destination],
        check=True,
    )


def docker_remove(path: str) -> None:
    subprocess.run(["docker", "exec", "-u", "0", "ac-worldserver", "rm", "-f", path], check=True)


def read_tables(storm: Storm, archive: Path) -> dict[str, bytes]:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        result: dict[str, bytes] = {}
        for name in DBC_TABLES:
            actual = names.get(f"dbfilesclient\\{name.lower()}.dbc")
            if actual is None:
                raise KeyError(f"{archive} is missing DBFilesClient\\{name}.dbc")
            result[name] = storm.read(handle, actual)
        return result
    finally:
        storm.dll.SFileCloseArchive(handle)


def _string_cache(pool: bytes) -> dict[bytes, int]:
    result: dict[bytes, int] = {}
    cursor = 0
    while cursor < len(pool):
        end = pool.find(b"\0", cursor)
        if end < 0:
            break
        value = pool[cursor:end]
        if value and value not in result:
            result[value] = cursor
        cursor = end + 1
    return result


def _append_string(pool: bytearray, cache: dict[bytes, int], value: bytes) -> int:
    existing = cache.get(value)
    if existing is not None:
        return existing
    offset = len(pool)
    pool.extend(value + b"\0")
    cache[value] = offset
    return offset


def _replace_matching_keyed_rows(
    data: bytes,
    table_name: str,
    race_field: int,
    key_fields: tuple[int, ...],
) -> tuple[bytes, int]:
    table = _table(data, table_name)
    blood = {
        tuple(_u32(row, field) for field in key_fields): row
        for row in table.records
        if _u32(row, race_field) == BLOOD_ELF_RACE
    }
    result: list[bytes] = []
    changed = 0
    for row in table.records:
        if _u32(row, race_field) != HIGH_ELF_RACE:
            result.append(row)
            continue
        key = tuple(_u32(row, field) for field in key_fields)
        donor = blood.get(key)
        if donor is None:
            result.append(row)
            continue
        replacement = donor
        if race_field != 0:
            replacement = _set_u32(replacement, 0, _u32(row, 0))
        replacement = _set_u32(replacement, race_field, HIGH_ELF_RACE)
        result.append(replacement)
        if replacement != row:
            changed += 1
    return table.build(result, table.strings), changed


def inherit_high_elf_charsections(data: bytes, available_assets: set[str]) -> tuple[bytes, dict[str, int]]:
    table = _table(data, "CharSections")
    blood_by_key = {
        (_u32(row, 2), _u32(row, 3), _u32(row, 8), _u32(row, 9)): row
        for row in table.records
        if _u32(row, 1) == BLOOD_ELF_RACE
    }
    pool = bytearray(table.strings)
    cache = _string_cache(table.strings)
    result: list[bytes] = []
    standard_replaced = 0
    extra_paths_upgraded = 0
    old_prefix = b"character\\bloodelf\\"
    new_prefix = b"Character\\BloodElf2\\"

    for row in table.records:
        if _u32(row, 1) != HIGH_ELF_RACE:
            result.append(row)
            continue

        key = (_u32(row, 2), _u32(row, 3), _u32(row, 8), _u32(row, 9))
        donor = blood_by_key.get(key)
        if donor is not None:
            replacement = _set_u32(donor, 0, _u32(row, 0))
            replacement = _set_u32(replacement, 1, HIGH_ELF_RACE)
            result.append(replacement)
            if replacement != row:
                standard_replaced += 1
            continue

        updated = row
        for field in (4, 5, 6):
            value = _read_string(table.strings, _u32(row, field))
            if not value or not value.replace(b"/", b"\\").lower().startswith(old_prefix):
                continue
            normalized = value.replace(b"/", b"\\")
            candidate = new_prefix + normalized[len(old_prefix) :]
            if candidate.decode("latin1").casefold() not in available_assets:
                continue
            offset = _append_string(pool, cache, candidate)
            updated = _set_u32(updated, field, offset)
            extra_paths_upgraded += 1
        result.append(updated)

    return table.build(result, bytes(pool)), {
        "standard_rows_replaced": standard_replaced,
        "high_elf_extra_texture_fields_upgraded": extra_paths_upgraded,
    }


def inherit_high_elf_facial(data: bytes) -> tuple[bytes, int]:
    table = _table(data, "CharacterFacialHairStyles")
    blood = {
        (_u32(row, 1), _u32(row, 2)): row
        for row in table.records
        if _u32(row, 0) == BLOOD_ELF_RACE
    }
    blood_keys = set(blood)
    preserved = [
        row
        for row in table.records
        if not (
            _u32(row, 0) == HIGH_ELF_RACE
            and (_u32(row, 1), _u32(row, 2)) in blood_keys
        )
    ]
    clones = [_set_u32(row, 0, HIGH_ELF_RACE) for _, row in sorted(blood.items())]
    return table.build(preserved + clones, table.strings), len(clones)


def inherit_high_elf(data: dict[str, bytes], available_assets: set[str]) -> tuple[dict[str, bytes], dict[str, object]]:
    output = dict(data)
    output["CharSections"], sections = inherit_high_elf_charsections(data["CharSections"], available_assets)
    output["CharHairGeosets"], hair_geosets = _replace_matching_keyed_rows(
        data["CharHairGeosets"],
        "CharHairGeosets",
        1,
        (2, 3),
    )
    output["CharHairTextures"], hair_textures = _replace_matching_keyed_rows(
        data["CharHairTextures"],
        "CharHairTextures",
        1,
        (2,),
    )
    output["CharacterFacialHairStyles"], facial = inherit_high_elf_facial(
        data["CharacterFacialHairStyles"]
    )
    output["BarberShopStyle"], barber = _replace_matching_keyed_rows(
        data["BarberShopStyle"],
        "BarberShopStyle",
        37,
        (1, 38, 39),
    )
    return output, {
        "CharSections": sections,
        "CharHairGeosets_standard_rows_replaced": hair_geosets,
        "CharHairTextures_rows_replaced": hair_textures,
        "CharacterFacialHairStyles_standard_rows_rebuilt": facial,
        "BarberShopStyle_standard_rows_replaced": barber,
    }


def build_contract(tables: dict[str, bytes]) -> dict[tuple[int, int], dict[str, object]]:
    sections = _table(tables["CharSections"], "CharSections")
    geosets = _table(tables["CharHairGeosets"], "CharHairGeosets")
    facial = _table(tables["CharacterFacialHairStyles"], "CharacterFacialHairStyles")
    contract: dict[tuple[int, int], dict[str, object]] = {}
    for race in STOCK_RACES:
        for gender in (0, 1):
            skin_colors: set[int] = set()
            faces_by_skin: dict[int, set[int]] = {}
            hair_pairs: set[tuple[int, int]] = set()
            facial_pairs: set[tuple[int, int]] = set()
            for row in sections.records:
                if _u32(row, 1) != race or _u32(row, 2) != gender:
                    continue
                section_type = _u32(row, 3)
                variation = _u32(row, 8)
                color = _u32(row, 9)
                if section_type == 0:
                    skin_colors.add(color)
                elif section_type == 1:
                    faces_by_skin.setdefault(color, set()).add(variation)
                elif section_type == 2:
                    facial_pairs.add((variation, color))
                elif section_type == 3:
                    hair_pairs.add((variation, color))
            hair_styles = {
                _u32(row, 3)
                for row in geosets.records
                if _u32(row, 1) == race and _u32(row, 2) == gender
            }
            facial_styles = {
                _u32(row, 2)
                for row in facial.records
                if _u32(row, 0) == race and _u32(row, 1) == gender
            }
            textured = {style for style, _ in hair_pairs}
            if textured:
                hair_styles &= textured
            contract[(race, gender)] = {
                "skin_colors": skin_colors,
                "faces_by_skin": faces_by_skin,
                "hair_pairs": hair_pairs,
                "hair_styles": hair_styles,
                "facial_pairs": facial_pairs,
                "facial_styles": facial_styles,
            }
    return contract


def repair_npc_extras(tables: dict[str, bytes]) -> tuple[dict[str, bytes], dict[str, object], set[int]]:
    display = _table(tables["CreatureDisplayInfo"], "CreatureDisplayInfo")
    extras = _table(tables["CreatureDisplayInfoExtra"], "CreatureDisplayInfoExtra")
    stock_models = set(NPC_STOCK_TO_HD_MODEL)
    used_extra_ids = {
        _u32(row, 3)
        for row in display.records
        if _u32(row, 1) in stock_models and _u32(row, 3)
    }
    contract = build_contract(tables)
    changed_ids: set[int] = set()
    fields = Counter()
    races = Counter()
    result: list[bytes] = []

    for row in extras.records:
        extra_id = _u32(row, 0)
        if extra_id not in used_extra_ids:
            result.append(row)
            continue
        race = _u32(row, 1)
        gender = _u32(row, 2)
        if (race, gender) not in contract:
            result.append(row)
            continue
        before = {
            "race": race,
            "gender": gender,
            "skin": _u32(row, 3),
            "face": _u32(row, 4),
            "hairStyle": _u32(row, 5),
            "hairColor": _u32(row, 6),
            "facialStyle": _u32(row, 7),
        }
        after = repair_row(before, contract)
        changed = changed_fields(before, after)
        if not changed:
            result.append(row)
            continue
        updated = row
        updated = _set_u32(updated, 3, int(after["skin"]))
        updated = _set_u32(updated, 4, int(after["face"]))
        updated = _set_u32(updated, 5, int(after["hairStyle"]))
        updated = _set_u32(updated, 6, int(after["hairColor"]))
        updated = _set_u32(updated, 7, int(after["facialStyle"]))
        result.append(updated)
        changed_ids.add(extra_id)
        fields.update(changed)
        races[race] += 1

    output = dict(tables)
    output["CreatureDisplayInfoExtra"] = extras.build(result, extras.strings)
    return output, {
        "stock_model_display_extra_ids": len(used_extra_ids),
        "npc_extra_rows_remapped": len(changed_ids),
        "field_changes": dict(fields),
        "race_changes": {str(key): value for key, value in sorted(races.items())},
    }, changed_ids


def direct_texture_dependencies(storm: Storm, archive: Path, donor_root: Path) -> dict[str, bytes]:
    donor_character = donor_root / "patch-CHA.mpq" / "Character"
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        refs: dict[str, str] = {}
        for race, gender, stem in RACE2_MODELS:
            key = f"character\\{race.lower()}\\{gender.lower()}\\{stem.lower()}.m2"
            actual = names.get(key)
            if actual is None:
                raise ValueError(f"missing Race2 model in live patch-Z: {key}")
            payload = storm.read(handle, actual)
            for _, texture_type, raw_name in _m2_texture_records(payload):
                if texture_type != 0 or not raw_name:
                    continue
                name = raw_name.decode("ascii", "strict").replace("/", "\\")
                refs.setdefault(name.casefold(), name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    result: dict[str, bytes] = {}
    for name in refs.values():
        source = donor_character.parent / Path(name.replace("\\", "/"))
        if not source.exists():
            raise FileNotFoundError(f"Ascension donor is missing direct M2 texture: {name}")
        result[name] = source.read_bytes()
    return result


def validate_direct_textures(storm: Storm, archive: Path, textures: dict[str, bytes]) -> None:
    handle = storm.open_archive(archive)
    try:
        for name, expected in textures.items():
            actual = storm.read(handle, name)
            if actual != expected:
                raise ValueError(f"direct texture does not match Ascension donor: {name}")
    finally:
        storm.dll.SFileCloseArchive(handle)


def validate_high_elf(tables: dict[str, bytes]) -> dict[str, int]:
    sections = _table(tables["CharSections"], "CharSections")
    blood = {
        (_u32(row, 2), _u32(row, 3), _u32(row, 8), _u32(row, 9)): row
        for row in sections.records
        if _u32(row, 1) == BLOOD_ELF_RACE
    }
    high = {
        (_u32(row, 2), _u32(row, 3), _u32(row, 8), _u32(row, 9)): row
        for row in sections.records
        if _u32(row, 1) == HIGH_ELF_RACE
    }
    missing = set(blood) - set(high)
    if missing:
        raise ValueError(f"High Elf is missing {len(missing)} Blood Elf HD CharSections keys")
    mismatched = 0
    for key, donor in blood.items():
        target = high[key]
        for field in (4, 5, 6, 7, 8, 9):
            if field in (4, 5, 6):
                left = _read_string(sections.strings, _u32(donor, field))
                right = _read_string(sections.strings, _u32(target, field))
                if left != right:
                    mismatched += 1
                    break
            elif _u32(donor, field) != _u32(target, field):
                mismatched += 1
                break
    if mismatched:
        raise ValueError(f"{mismatched} standard High Elf CharSections rows do not mirror Blood Elf HD")
    return {
        "blood_elf_standard_keys": len(blood),
        "high_elf_total_rows": sum(1 for row in sections.records if _u32(row, 1) == HIGH_ELF_RACE),
    }


def validate_npc_extras(tables: dict[str, bytes]) -> None:
    _, report, changed = repair_npc_extras(tables)
    if changed:
        raise ValueError(f"{len(changed)} NPC display-extra rows remain incompatible with the HD appearance contract")
    if report["npc_extra_rows_remapped"]:
        raise ValueError("NPC appearance validation unexpectedly changed rows")


def build_server_extra_continuation(data: bytes, row_ids: set[int]) -> bytes:
    table = _table(data, "CreatureDisplayInfoExtra")
    selected = [row for row in table.records if _u32(row, 0) in row_ids]
    found = {_u32(row, 0) for row in selected}
    if found != row_ids:
        raise ValueError(f"server continuation is missing display-extra IDs: {sorted(row_ids - found)}")
    selected, strings = _rebase_strings(
        "CreatureDisplayInfoExtra",
        selected,
        table.strings,
        b"\0",
    )
    return table.build(selected, strings)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix Ascension HD direct textures, High Elf inheritance, and NPC appearance rows")
    parser.add_argument("--client-root", type=Path, default=DEFAULT_CLIENT)
    parser.add_argument("--ascension-root", type=Path, default=DEFAULT_ASCENSION)
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client = args.client_root.resolve()
    donor_root = args.ascension_root.resolve()
    patch_z = client / "Data" / "patch-Z.MPQ"
    locale_z = client / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    storm = Storm(args.stormlib)

    before = {
        "patch-Z": read_tables(storm, patch_z),
        "patch-enUS-Z": read_tables(storm, locale_z),
    }
    handle = storm.open_archive(patch_z)
    try:
        live_asset_names = {
            name.casefold()
            for name, *_ in storm.list_files(handle)
        }
    finally:
        storm.dll.SFileCloseArchive(handle)

    direct_textures = direct_texture_dependencies(storm, patch_z, donor_root)
    missing_direct = [name for name in direct_textures if name.casefold() not in live_asset_names]

    corrected: dict[str, dict[str, bytes]] = {}
    high_reports: dict[str, object] = {}
    npc_reports: dict[str, object] = {}
    npc_ids: dict[str, set[int]] = {}
    for label, tables in before.items():
        high_fixed, high_report = inherit_high_elf(tables, live_asset_names)
        npc_fixed, npc_report, changed_ids = repair_npc_extras(high_fixed)
        corrected[label] = npc_fixed
        high_reports[label] = high_report
        npc_reports[label] = npc_report
        npc_ids[label] = changed_ids
        validate_high_elf(npc_fixed)
        validate_npc_extras(npc_fixed)

    if npc_ids["patch-Z"] != npc_ids["patch-enUS-Z"]:
        raise ValueError("patch-Z and patch-enUS-Z require different NPC display-extra repairs")

    preview = {
        "apply": args.apply,
        "archive_hashes_before": {
            "patch-Z": sha256(patch_z),
            "patch-enUS-Z": sha256(locale_z),
        },
        "direct_type0_textures": {
            "total_required": len(direct_textures),
            "missing_before": len(missing_direct),
            "examples": sorted(missing_direct)[:12],
        },
        "high_elf": high_reports,
        "npc": npc_reports,
        "npc_extra_ids": sorted(npc_ids["patch-Z"]),
    }
    print(json.dumps(preview, indent=2))
    if not args.apply:
        return 0

    if wow_running():
        raise RuntimeError("Wow.exe is running; close the client before applying the HD follow-up repair")
    online = mysql_scalar("SELECT COUNT(*) FROM acore_characters.characters WHERE online <> 0;")
    if online:
        raise RuntimeError(f"refusing to restart worldserver while {online} player(s) are online")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = client / "Backups" / f"ascension-hd-followups-{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    backup_data = backup / "Data"
    backup_data.mkdir()
    shutil.copy2(patch_z, backup_data / patch_z.name)
    shutil.copy2(locale_z, backup_data / locale_z.name)
    for label, original, copied in (
        ("patch-Z", patch_z, backup_data / patch_z.name),
        ("patch-enUS-Z", locale_z, backup_data / locale_z.name),
    ):
        if sha256(original) != sha256(copied):
            raise RuntimeError(f"backup hash mismatch for {label}")

    server_before = backup / "server-continuations-before"
    server_before.mkdir()
    subprocess.run(
        ["docker", "cp", "ac-worldserver:/azerothcore/env/dist/data/dbc-continuations/.", str(server_before)],
        check=True,
    )

    stage_z = backup / "patch-Z.staged.MPQ"
    stage_locale = backup / "patch-enUS-Z.staged.MPQ"
    shutil.copy2(patch_z, stage_z)
    shutil.copy2(locale_z, stage_locale)

    replacements_z = {
        f"DBFilesClient\\{name}.dbc": payload
        for name, payload in corrected["patch-Z"].items()
        if payload != before["patch-Z"][name]
    }
    replacements_locale = {
        f"DBFilesClient\\{name}.dbc": payload
        for name, payload in corrected["patch-enUS-Z"].items()
        if payload != before["patch-enUS-Z"][name]
    }
    asset_additions = {name: payload for name, payload in direct_textures.items() if name.casefold() not in live_asset_names}
    storm.replace_archive_entries(stage_z, {**asset_additions, **replacements_z})
    storm.replace_archive_entries(stage_locale, replacements_locale)

    staged_z = read_tables(storm, stage_z)
    staged_locale = read_tables(storm, stage_locale)
    validate_high_elf(staged_z)
    validate_high_elf(staged_locale)
    validate_npc_extras(staged_z)
    validate_npc_extras(staged_locale)
    validate_direct_textures(storm, stage_z, direct_textures)

    server_payload = build_server_extra_continuation(
        staged_z["CreatureDisplayInfoExtra"],
        npc_ids["patch-Z"],
    )
    server_stage = backup / "CreatureDisplayInfoExtra.dbc1-ascension-hd-npc"
    server_stage.write_bytes(server_payload)

    installed_client = False
    server_target = "/azerothcore/env/dist/data/dbc-continuations/CreatureDisplayInfoExtra.dbc1-ascension-hd-npc"
    old_server_target = server_before / "CreatureDisplayInfoExtra.dbc1-ascension-hd-npc"
    try:
        os.replace(stage_z, patch_z)
        os.replace(stage_locale, locale_z)
        installed_client = True

        if npc_ids["patch-Z"]:
            docker_copy_to_worldserver(server_stage, server_target)
        else:
            docker_remove(server_target)

        subprocess.run(["docker", "restart", "ac-worldserver"], check=True, stdout=subprocess.PIPE, text=True)
        subprocess.run([sys.executable, "-c", "import time; time.sleep(8)"], check=True)
        log_result = subprocess.run(
            ["docker", "logs", "--since", "30s", "ac-worldserver"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        # Docker emits container logs on stderr on some Windows setups.
        log = log_result.stdout + log_result.stderr
        expected_line = (
            f"CreatureDisplayInfoExtra.dbc1-ascension-hd-npc -> {len(npc_ids['patch-Z'])} row(s) "
            "into CreatureDisplayInfoExtra.dbc"
        )
        if npc_ids["patch-Z"] and expected_line not in log:
            raise RuntimeError(f"worldserver did not confirm NPC display-extra continuation: {expected_line}")
        if "Base data/dbc/ files were not modified" not in log:
            raise RuntimeError("worldserver continuation summary is missing")

        final_z = read_tables(storm, patch_z)
        final_locale = read_tables(storm, locale_z)
        validate_high_elf(final_z)
        validate_high_elf(final_locale)
        validate_npc_extras(final_z)
        validate_npc_extras(final_locale)
        validate_direct_textures(storm, patch_z, direct_textures)

        report = {
            **preview,
            "backup_dir": str(backup),
            "archive_hashes_after": {
                "patch-Z": sha256(patch_z),
                "patch-enUS-Z": sha256(locale_z),
            },
            "server_npc_extra_rows": len(npc_ids["patch-Z"]),
            "worldserver_verified": True,
        }
        (backup / "manifest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0
    except Exception:
        if installed_client:
            shutil.copy2(backup_data / patch_z.name, patch_z)
            shutil.copy2(backup_data / locale_z.name, locale_z)
        if old_server_target.exists():
            docker_copy_to_worldserver(old_server_target, server_target)
        else:
            docker_remove(server_target)
        subprocess.run(["docker", "restart", "ac-worldserver"], check=False, stdout=subprocess.PIPE, text=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
