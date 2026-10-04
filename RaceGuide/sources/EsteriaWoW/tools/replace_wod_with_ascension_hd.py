"""Replace Esteria's failed F: WoD stock-race splice with Ascension's HD races.

The migration is intentionally surgical and reversible:

* backs up the live Z/enUS-Z archives, Wow.exe, and temporary donor patch-T;
* removes the F: donor's stock character payload from patch-Z, restoring any
  entries that already existed in the pre-WoD backup;
* imports only Ascension's isolated Race2 asset families (Human2..Draenei2);
* replaces only stock-race appearance rows with Ascension's HD race contract;
* restores the stock display/model/extra rows changed by the F: migration;
* appends Ascension's dedicated HD display/model/extra rows;
* changes only the stock ChrRaces male/female display IDs;
* preserves custom races and unrelated DBC rows;
* reverts the one F-donor-only Wow.exe byte patch if it is still present;
* removes patch-T only when it is byte-identical to the staged donor W archive;
* produces server DBC continuation files matching the new player display IDs.

No server binary, SQL, custom-race asset, or unrelated DBC row is modified.
"""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import os
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import (  # noqa: E402
    APPEARANCE_TABLES,
    STOCK_RACES,
    WORLD_DISPLAY_IDS,
    _rebase_strings,
    _table,
    _u32,
    hd_dependencies,
    load_donor_tables,
    merge_table_set,
    world_chr_races_payload,
    world_display_payload,
)
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402
from wod_model_appearance_repair import donor_hidden_texture_payloads  # noqa: E402
from wod_model_migration import (  # noqa: E402
    archive_names,
    derive_stock_dependencies,
    donor_asset_names,
    rebuild_archive_streaming,
    sha256,
)


DEFAULT_CLIENT = Path(r"G:\3.3.5a - Dev")
DEFAULT_ASCENSION = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted")
DEFAULT_WOD_DONOR = Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)")
DEFAULT_PRE_WOD_BACKUP = DEFAULT_CLIENT / "Backups" / "wod-models-20260927-224721"

RACE2_FOLDERS = (
    "Human2",
    "Orc2",
    "Dwarf2",
    "NightElf2",
    "Scourge2",
    "Tauren2",
    "Gnome2",
    "Troll2",
    "BloodElf2",
    "Draenei2",
)

DBC_TABLES = (
    "ChrRaces",
    "CharSections",
    "CharHairGeosets",
    "CharHairTextures",
    "CharacterFacialHairStyles",
    "BarberShopStyle",
    "CreatureDisplayInfo",
    "CreatureModelData",
    "CreatureDisplayInfoExtra",
)

WOW_BRANCH_OFFSET = 0x2B1F48
WOW_DONOR_PATCH_BYTE = 0xEB
WOW_ESTERIA_ORIGINAL_BYTE = 0x74
DONOR_W_SHA256 = "5e014fbcefbf2257e52ef8abe2d32fa3cc643a31214b334d561b7c1823433052"


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_archive_entry(storm: Storm, archive: Path, entry: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, entry)
    finally:
        storm.dll.SFileCloseArchive(handle)


def read_tables(storm: Storm, archive: Path, names: tuple[str, ...] = DBC_TABLES) -> dict[str, bytes]:
    handle = storm.open_archive(archive)
    try:
        available = archive_names(storm, handle)
        result: dict[str, bytes] = {}
        for name in names:
            key = rf"DBFilesClient\{name}.dbc"
            actual = available.get(key.casefold())
            if actual is None:
                raise KeyError(f"{archive} is missing {key}")
            result[name] = storm.read(handle, actual)
        return result
    finally:
        storm.dll.SFileCloseArchive(handle)


def collect_race2_assets(root: Path) -> dict[str, Path]:
    character_root = root / "patch-CHA.mpq" / "Character"
    if not character_root.is_dir():
        raise FileNotFoundError(f"Ascension extracted Character root is missing: {character_root}")
    assets: dict[str, Path] = {}
    for folder in RACE2_FOLDERS:
        race_root = character_root / folder
        if not race_root.is_dir():
            raise FileNotFoundError(f"Ascension HD race folder is missing: {race_root}")
        for path in sorted(race_root.rglob("*"), key=lambda item: item.as_posix().casefold()):
            if not path.is_file():
                continue
            entry = "Character\\" + path.relative_to(character_root).as_posix().replace("/", "\\")
            assets[entry] = path
    if not assets:
        raise RuntimeError("No Ascension Race2 assets were collected")
    return assets


def restore_rows_by_id(
    table_name: str,
    current_data: bytes,
    backup_data: bytes,
    row_ids: set[int],
) -> bytes:
    """Restore selected row IDs from the pre-WoD table while preserving everything else."""

    current = _table(current_data, table_name)
    backup = _table(backup_data, table_name)
    if (current.fields, current.record_size) != (backup.fields, backup.record_size):
        raise ValueError(
            f"{table_name} layout mismatch current={current.fields}/{current.record_size} "
            f"backup={backup.fields}/{backup.record_size}"
        )

    donor_rows = [row for row in backup.records if _u32(row, 0) in row_ids]
    found = {_u32(row, 0) for row in donor_rows}
    missing = sorted(row_ids - found)
    if missing:
        raise ValueError(f"Pre-WoD {table_name} is missing rows required for restore: {missing[:12]}")

    donor_rows, strings = _rebase_strings(table_name, donor_rows, backup.strings, current.strings)
    records = list(current.records)
    index_by_id = {_u32(row, 0): index for index, row in enumerate(records)}
    for row in donor_rows:
        row_id = _u32(row, 0)
        index = index_by_id.get(row_id)
        if index is None:
            index_by_id[row_id] = len(records)
            records.append(row)
        else:
            records[index] = row
    return current.build(records, strings)


def build_ascension_dbcs(
    current: dict[str, bytes],
    pre_wod: dict[str, bytes],
    ascension: dict[str, bytes],
    f_display_ids: set[int],
    f_model_ids: set[int],
    f_extra_ids: set[int],
) -> dict[str, bytes]:
    """Undo the F: stock display rows, then apply Ascension's HD player contract."""

    base = dict(current)
    base["CreatureDisplayInfo"] = restore_rows_by_id(
        "CreatureDisplayInfo",
        current["CreatureDisplayInfo"],
        pre_wod["CreatureDisplayInfo"],
        f_display_ids,
    )
    base["CreatureModelData"] = restore_rows_by_id(
        "CreatureModelData",
        current["CreatureModelData"],
        pre_wod["CreatureModelData"],
        f_model_ids,
    )
    base["CreatureDisplayInfoExtra"] = restore_rows_by_id(
        "CreatureDisplayInfoExtra",
        current["CreatureDisplayInfoExtra"],
        pre_wod["CreatureDisplayInfoExtra"],
        f_extra_ids,
    )
    return merge_table_set(base, ascension)


def create_archive_from_live(
    storm: Storm,
    source_path: Path,
    target_path: Path,
    *,
    remove_entries: set[str],
    restore_from_backup: dict[str, bytes],
    add_files: dict[str, Path],
) -> dict[str, int]:
    """Stream a fresh classic MPQ while removing F: assets and adding Ascension Race2 assets."""

    if target_path.exists():
        target_path.unlink()

    source = storm.open_archive(source_path)
    target = H()
    try:
        source_entries = [
            name
            for name, *_ in storm.list_files(source)
            if name.casefold() not in {"(listfile)", "(attributes)"}
        ]
        remove_cf = {name.casefold() for name in remove_entries}
        add_cf = {name.casefold() for name in add_files}
        restore_cf = {name.casefold(): (name, payload) for name, payload in restore_from_backup.items()}

        keep_entries = [name for name in source_entries if name.casefold() not in remove_cf | add_cf]
        output_count = len(keep_entries) + len(restore_from_backup) + len(add_files)
        create_flags = 0x00100000 | 0x00200000  # listfile + attributes, classic MPQ
        if not storm.dll.SFileCreateArchive(
            str(target_path),
            create_flags,
            output_count + 128,
            c.byref(target),
        ):
            raise OSError(f"SFileCreateArchive failed: {target_path} ({c.get_last_error()})")

        def write_entry(name: str, payload: bytes) -> None:
            file_handle = H()
            if not storm.dll.SFileCreateFile(
                target,
                name.encode("ascii"),
                0,
                len(payload),
                0,
                0,
                c.byref(file_handle),
            ):
                raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
            finished = False
            try:
                buffer = c.create_string_buffer(payload or b"\0")
                if not storm.dll.SFileWriteFile(file_handle, buffer, len(payload), 0x00000002):
                    raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
                if not storm.dll.SFileFinishFile(file_handle):
                    raise OSError(f"SFileFinishFile failed: {name} ({c.get_last_error()})")
                finished = True
            finally:
                if not finished:
                    storm.dll.SFileCloseFile(file_handle)

        for index, name in enumerate(keep_entries, 1):
            write_entry(name, storm.read(source, name))
            if index % 2000 == 0:
                print(f"  kept {index}/{len(keep_entries)} existing entries")

        for index, (_, (name, payload)) in enumerate(sorted(restore_cf.items()), 1):
            write_entry(name, payload)
            if index % 250 == 0:
                print(f"  restored {index}/{len(restore_cf)} pre-WoD entries")

        for index, (name, path) in enumerate(sorted(add_files.items(), key=lambda item: item[0].casefold()), 1):
            write_entry(name, path.read_bytes())
            if index % 1000 == 0:
                print(f"  imported {index}/{len(add_files)} Ascension assets")
    finally:
        if target:
            storm.dll.SFileCloseArchive(target)
        storm.dll.SFileCloseArchive(source)

    return {
        "kept": len(keep_entries),
        "restored": len(restore_from_backup),
        "ascension_assets": len(add_files),
        "entries": output_count,
    }


def stage_locale_archive(
    storm: Storm,
    source: Path,
    output: Path,
    dbcs: dict[str, bytes],
) -> None:
    raw = output.with_suffix(output.suffix + ".raw")
    compact = output.with_suffix(output.suffix + ".compact")
    for path in (raw, compact, output):
        if path.exists():
            path.unlink()
    shutil.copy2(source, raw)
    storm.replace_archive_entries(raw, {rf"DBFilesClient\{name}.dbc": payload for name, payload in dbcs.items()})
    rebuild_archive_streaming(storm, raw, compact)
    os.replace(compact, output)
    raw.unlink(missing_ok=True)


def validate_patch_z(
    storm: Storm,
    staged: Path,
    ascension_assets: dict[str, Path],
    removed_f_entries: set[str],
    restored: dict[str, bytes],
) -> dict[str, object]:
    handle = storm.open_archive(staged)
    try:
        names = archive_names(storm, handle)
        missing = []
        different = []
        for index, (entry, source) in enumerate(ascension_assets.items(), 1):
            actual_name = names.get(entry.casefold())
            if actual_name is None:
                missing.append(entry)
            else:
                payload = storm.read(handle, actual_name)
                expected = source.read_bytes()
                if payload != expected:
                    different.append(entry)
            if index % 2000 == 0:
                print(f"  validated {index}/{len(ascension_assets)} Ascension assets")
        if missing or different:
            raise ValueError(
                f"Ascension asset validation failed: missing={len(missing)} different={len(different)} "
                f"first={(missing or different)[:3]}"
            )

        for entry, expected in restored.items():
            actual_name = names.get(entry.casefold())
            if actual_name is None or storm.read(handle, actual_name) != expected:
                raise ValueError(f"Pre-WoD asset restore validation failed: {entry}")

        restored_cf = {name.casefold() for name in restored}
        stale = [
            entry
            for entry in removed_f_entries
            if entry.casefold() not in restored_cf and entry.casefold() in names
        ]
        if stale:
            raise ValueError(f"F: donor-only assets remain after rebuild: {stale[:5]}")
    finally:
        storm.dll.SFileCloseArchive(handle)

    size = staged.stat().st_size
    if size >= 0x100000000:
        raise ValueError(f"staged patch-Z exceeds the classic MPQ 4 GiB ceiling: {size}")
    return {
        "size": size,
        "ascension_assets_verified": len(ascension_assets),
        "pre_wod_assets_restored": len(restored),
        "f_donor_only_remaining": 0,
    }


def validate_dbcs(storm: Storm, archive: Path, ascension: dict[str, bytes]) -> dict[str, object]:
    live = read_tables(storm, archive)
    # Re-running the merge against an already-merged set must leave the stock
    # appearance/display contract stable.  Canonical checks below make the
    # critical race/display paths explicit as well.
    race_table = _table(live["ChrRaces"], "ChrRaces")
    asc_races = _table(ascension["ChrRaces"], "ChrRaces")
    asc_by_id = {_u32(row, 0): row for row in asc_races.records}
    stock_to_hd = {1: 51, 2: 52, 3: 53, 4: 54, 5: 55, 6: 56, 7: 57, 8: 58, 10: 60, 11: 61}
    race_pairs: dict[int, tuple[int, int]] = {}
    for row in race_table.records:
        race = _u32(row, 0)
        if race not in stock_to_hd:
            continue
        donor = asc_by_id[stock_to_hd[race]]
        expected = (_u32(donor, 4), _u32(donor, 5))
        actual = (_u32(row, 4), _u32(row, 5))
        if actual != expected:
            raise ValueError(f"ChrRaces display pair mismatch for race {race}: {actual} != {expected}")
        race_pairs[race] = actual

    model_table = _table(live["CreatureModelData"], "CreatureModelData")
    model_paths: dict[int, str] = {}
    for row in model_table.records:
        row_id = _u32(row, 0)
        if 112887 <= row_id <= 112926:
            offset = _u32(row, 2)
            if offset:
                end = model_table.strings.find(b"\0", offset)
                model_paths[row_id] = model_table.strings[offset:end].decode("utf-8")
    required_prefixes = tuple(f"Character\\{race2}\\" for race2 in RACE2_FOLDERS)
    hd_ids = hd_dependencies(ascension["ChrRaces"], ascension["CreatureDisplayInfo"])[1]
    missing_models = sorted(hd_ids - set(model_paths))
    if missing_models:
        raise ValueError(f"Merged CreatureModelData is missing Ascension HD models: {missing_models}")
    bad_paths = {row_id: path for row_id, path in model_paths.items() if row_id in hd_ids and not path.startswith(required_prefixes)}
    if bad_paths:
        raise ValueError(f"Ascension model paths did not normalize to Race2 paths: {bad_paths}")

    stock_counts: dict[str, int] = {}
    race_fields = {
        "CharSections": 1,
        "CharHairGeosets": 1,
        "CharHairTextures": 1,
        "CharacterFacialHairStyles": 0,
        "BarberShopStyle": 37,
    }
    for name, race_field in race_fields.items():
        table = _table(live[name], name)
        stock_counts[name] = sum(1 for row in table.records if _u32(row, race_field) in STOCK_RACES)

    return {
        "stock_race_display_pairs": {str(key): list(value) for key, value in sorted(race_pairs.items())},
        "ascension_hd_model_rows": len(hd_ids),
        "stock_appearance_rows": stock_counts,
    }


def build_server_continuations(
    merged: dict[str, bytes],
    ascension: dict[str, bytes],
    output: Path,
) -> dict[str, int]:
    output.mkdir(parents=True, exist_ok=True)
    display_ids, model_ids, extra_ids = hd_dependencies(
        ascension["ChrRaces"], ascension["CreatureDisplayInfo"]
    )
    stats: dict[str, int] = {}

    def write_selected(table_name: str, ids: set[int], filename: str) -> None:
        source = _table(ascension[table_name], table_name)
        selected = [row for row in source.records if _u32(row, 0) in ids]
        selected, strings = _rebase_strings(
            table_name,
            selected,
            source.strings,
            b"\0",
            normalize_model_paths=table_name == "CreatureModelData",
        )
        payload = source.build(selected, strings)
        (output / filename).write_bytes(payload)
        stats[filename] = len(selected)

    display_payload = world_display_payload(merged["CreatureDisplayInfo"])
    display_table = _table(display_payload, "CreatureDisplayInfo")
    (output / "CreatureDisplayInfo.dbc1-ascension-hd").write_bytes(display_payload)
    stats["CreatureDisplayInfo.dbc1-ascension-hd"] = len(display_table.records)

    write_selected("CreatureModelData", model_ids, "CreatureModelData.dbc1-ascension-hd")
    if extra_ids:
        write_selected(
            "CreatureDisplayInfoExtra",
            extra_ids,
            "CreatureDisplayInfoExtra.dbc1-ascension-hd",
        )

    payload = world_chr_races_payload(merged["ChrRaces"])
    race_table = _table(payload, "ChrRaces")
    name = "ChrRaces.dbc1-ascension-hd"
    (output / name).write_bytes(payload)
    stats[name] = len(race_table.records)
    return stats


def validate_server_continuations(storm: Storm, root: Path) -> None:
    expected = {
        "CreatureDisplayInfo.dbc1-ascension-hd": "CreatureDisplayInfo",
        "CreatureModelData.dbc1-ascension-hd": "CreatureModelData",
        "ChrRaces.dbc1-ascension-hd": "ChrRaces",
    }
    optional = root / "CreatureDisplayInfoExtra.dbc1-ascension-hd"
    if optional.exists():
        expected[optional.name] = "CreatureDisplayInfoExtra"
    for filename, table_name in expected.items():
        payload = (root / filename).read_bytes()
        table = _table(payload, table_name)
        if table_name == "CreatureDisplayInfo":
            ids = {_u32(row, 0) for row in table.records}
            if ids != WORLD_DISPLAY_IDS:
                raise ValueError(f"server world-display continuation IDs are wrong: {sorted(ids)}")
        elif table_name == "ChrRaces":
            for row in table.records:
                if _u32(row, 4) >= 65536 or _u32(row, 5) >= 65536:
                    raise ValueError("server ChrRaces continuation contains a >16-bit player display ID")


def patch_wow_exe(exe: Path) -> tuple[bool, int, int]:
    data = bytearray(exe.read_bytes())
    if len(data) <= WOW_BRANCH_OFFSET:
        raise ValueError("Wow.exe is unexpectedly short")
    before = data[WOW_BRANCH_OFFSET]
    if before == WOW_DONOR_PATCH_BYTE:
        data[WOW_BRANCH_OFFSET] = WOW_ESTERIA_ORIGINAL_BYTE
        exe.write_bytes(data)
        return True, before, data[WOW_BRANCH_OFFSET]
    if before == WOW_ESTERIA_ORIGINAL_BYTE:
        return False, before, before
    raise ValueError(
        f"Wow.exe offset {WOW_BRANCH_OFFSET:#x} is {before:#x}, expected "
        f"{WOW_DONOR_PATCH_BYTE:#x} or {WOW_ESTERIA_ORIGINAL_BYTE:#x}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace F: WoD stock races with Ascension HD races")
    parser.add_argument("--client-root", type=Path, default=DEFAULT_CLIENT)
    parser.add_argument("--ascension-root", type=Path, default=DEFAULT_ASCENSION)
    parser.add_argument("--wod-donor-root", type=Path, default=DEFAULT_WOD_DONOR)
    parser.add_argument("--pre-wod-backup", type=Path, default=DEFAULT_PRE_WOD_BACKUP)
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client = args.client_root.resolve()
    ascension_root = args.ascension_root.resolve()
    wod = args.wod_donor_root.resolve()
    pre_wod_backup = args.pre_wod_backup.resolve()
    storm = Storm(args.stormlib)

    patch_z = client / "Data" / "patch-Z.MPQ"
    enus_z = client / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    wow_exe = client / "Wow.exe"
    patch_t = client / "Data" / "patch-T.MPQ"
    donor_x_assets = wod / "Data" / "patch-x.mpq"
    donor_w_assets = wod / "Data" / "patch-w.mpq"
    donor_x_locale = wod / "Data" / "enUS" / "patch-enUS-x.MPQ"
    pre_wod_z = pre_wod_backup / "patch-Z.MPQ"
    pre_wod_enus = pre_wod_backup / "patch-enUS-Z.MPQ"

    required = (
        patch_z,
        enus_z,
        wow_exe,
        donor_x_assets,
        donor_w_assets,
        donor_x_locale,
        pre_wod_z,
        pre_wod_enus,
        ascension_root / "DBFilesClient" / "ChrRaces.dbc",
        ascension_root / "patch-CHA.mpq" / "Character" / "Human2" / "Male" / "humanmale2.m2",
    )
    missing = [path for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required source(s):\n" + "\n".join(str(path) for path in missing))

    print("Reading current/pre-WoD/Ascension DBC contracts...")
    current_tables = read_tables(storm, enus_z)
    pre_wod_tables = read_tables(storm, pre_wod_enus)
    ascension_tables = load_donor_tables(ascension_root / "DBFilesClient")
    missing_donor = sorted(set(DBC_TABLES) - set(ascension_tables))
    if missing_donor:
        raise ValueError(f"Ascension extracted DBC set is missing: {missing_donor}")

    f_x_display = read_archive_entry(
        storm, donor_x_locale, r"DBFilesClient\CreatureDisplayInfo.dbc"
    )
    f_display_ids, f_model_ids, f_extra_ids = derive_stock_dependencies(
        pre_wod_tables["ChrRaces"], f_x_display
    )
    merged_dbcs = build_ascension_dbcs(
        current_tables,
        pre_wod_tables,
        ascension_tables,
        f_display_ids,
        f_model_ids,
        f_extra_ids,
    )

    print("Collecting Ascension Race2 assets...")
    ascension_assets = collect_race2_assets(ascension_root)
    ascension_bytes = sum(path.stat().st_size for path in ascension_assets.values())
    print(f"  {len(ascension_assets)} assets, {ascension_bytes / 1024 / 1024:.1f} MiB source bytes")

    print("Identifying the F: donor payload to remove...")
    f_asset_names = set(donor_asset_names(storm, donor_x_assets))
    f_char_sections = read_archive_entry(storm, donor_x_locale, r"DBFilesClient\CharSections.dbc")
    hidden_w = donor_hidden_texture_payloads(
        storm, donor_x_assets, donor_w_assets, f_char_sections
    )
    removed_f_entries = f_asset_names | set(hidden_w)
    print(f"  F: visible X assets: {len(f_asset_names)}")
    print(f"  F: hidden W dependencies: {len(hidden_w)}")

    backup_handle = storm.open_archive(pre_wod_z)
    try:
        backup_names = archive_names(storm, backup_handle)
        restores: dict[str, bytes] = {}
        for entry in sorted(removed_f_entries, key=str.casefold):
            actual = backup_names.get(entry.casefold())
            if actual is not None:
                restores[actual] = storm.read(backup_handle, actual)
    finally:
        storm.dll.SFileCloseArchive(backup_handle)
    print(f"  pre-WoD entries to restore instead of remove: {len(restores)}")

    display_ids, model_ids, extra_ids = hd_dependencies(
        ascension_tables["ChrRaces"], ascension_tables["CreatureDisplayInfo"]
    )
    print(
        f"Ascension DBC dependencies: displays={len(display_ids)} models={len(model_ids)} extras={len(extra_ids)}"
    )

    dry_validation = {
        "ascension_asset_count": len(ascension_assets),
        "ascension_asset_bytes": ascension_bytes,
        "f_entries_removed_or_restored": len(removed_f_entries),
        "pre_wod_asset_restores": len(restores),
        "f_display_rows_restored": len(f_display_ids),
        "f_model_rows_restored": len(f_model_ids),
        "f_extra_rows_restored": len(f_extra_ids),
        "ascension_display_rows": len(display_ids),
        "ascension_model_rows": len(model_ids),
        "ascension_extra_rows": len(extra_ids),
    }

    if not args.apply:
        print("\nDRY RUN ONLY. No files changed.")
        print(json.dumps(dry_validation, indent=2, sort_keys=True))
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = client / "Backups" / f"ascension-hd-replacement-{stamp}"
    staging = client / "Data" / "Staging" / f"ascension-hd-replacement-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    staging.mkdir(parents=True, exist_ok=False)

    print(f"Backing up live state to {backup_dir} ...")
    shutil.copy2(patch_z, backup_dir / "patch-Z.MPQ")
    shutil.copy2(enus_z, backup_dir / "patch-enUS-Z.MPQ")
    shutil.copy2(wow_exe, backup_dir / "Wow.exe")
    if patch_t.exists():
        shutil.copy2(patch_t, backup_dir / "patch-T.MPQ")

    staged_z = staging / "patch-Z.MPQ"
    staged_enus = staging / "patch-enUS-Z.MPQ"
    print("Building fresh patch-Z without the F: stock-race payload...")
    stage_stats = create_archive_from_live(
        storm,
        patch_z,
        staged_z,
        remove_entries=removed_f_entries,
        restore_from_backup=restores,
        add_files=ascension_assets,
    )
    print("Building compact enUS-Z with Ascension stock-race DBCs...")
    stage_locale_archive(storm, enus_z, staged_enus, merged_dbcs)

    print("Validating staged asset archive...")
    z_validation = validate_patch_z(
        storm, staged_z, ascension_assets, removed_f_entries, restores
    )
    print("Validating staged DBC contract...")
    dbc_validation = validate_dbcs(storm, staged_enus, ascension_tables)

    server_dir = backup_dir / "server-continuations"
    server_stats = build_server_continuations(merged_dbcs, ascension_tables, server_dir)
    validate_server_continuations(storm, server_dir)

    manifest = {
        "created": stamp,
        "client_root": str(client),
        "pre_wod_source": str(pre_wod_backup),
        "ascension_source": str(ascension_root),
        "before": {
            "patch_Z_sha256": sha256(patch_z),
            "patch_enUS_Z_sha256": sha256(enus_z),
            "Wow_exe_sha256": sha256(wow_exe),
            "patch_T_sha256": sha256(patch_t) if patch_t.exists() else None,
        },
        "dry_run": dry_validation,
        "stage": stage_stats,
        "asset_validation": z_validation,
        "dbc_validation": dbc_validation,
        "server_continuations": server_stats,
    }
    (backup_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("Installing validated archives atomically...")
    os.replace(staged_z, patch_z)
    os.replace(staged_enus, enus_z)

    exe_changed, exe_before, exe_after = patch_wow_exe(wow_exe)
    if patch_t.exists():
        patch_t_hash = sha256(patch_t)
        if patch_t_hash != DONOR_W_SHA256:
            raise ValueError(
                f"Refusing to remove patch-T: hash {patch_t_hash} does not match the staged donor W archive"
            )
        patch_t.unlink()

    print("Final live validation...")
    final_z = validate_patch_z(storm, patch_z, ascension_assets, removed_f_entries, restores)
    final_dbc = validate_dbcs(storm, enus_z, ascension_tables)
    manifest["after"] = {
        "patch_Z_sha256": sha256(patch_z),
        "patch_enUS_Z_sha256": sha256(enus_z),
        "Wow_exe_sha256": sha256(wow_exe),
        "Wow_exe_branch_reverted": exe_changed,
        "Wow_exe_branch_byte_before": exe_before,
        "Wow_exe_branch_byte_after": exe_after,
        "patch_T_present": patch_t.exists(),
        "patch_Z_size": patch_z.stat().st_size,
        "patch_enUS_Z_size": enus_z.stat().st_size,
        "asset_validation": final_z,
        "dbc_validation": final_dbc,
    }
    (backup_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    try:
        staging.rmdir()
    except OSError:
        pass

    print("\nAscension HD replacement complete.")
    print(f"Backup: {backup_dir}")
    print(f"Server continuations: {server_dir}")
    print(f"patch-Z: {patch_z.stat().st_size / 1024 / 1024:.1f} MiB")
    print(f"enUS-Z: {enus_z.stat().st_size / 1024 / 1024:.1f} MiB")
    print(f"patch-T removed: {not patch_t.exists()}")
    print(f"Wow.exe donor branch reverted: {exe_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
