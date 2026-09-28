"""Safely splice the F: WoD stock-race model pack into Esteria's active Z patches.

The migration is intentionally narrow:
- backs up Data/patch-Z.MPQ and Data/enUS/patch-enUS-Z.MPQ first;
- copies all Character/ and Textures/ assets from the donor patch-x.mpq;
- replaces only stock-race CharSections rows;
- replaces only CreatureDisplayInfo rows that use the donor stock-race player/NPC models;
- replaces the corresponding CreatureModelData and CreatureDisplayInfoExtra rows;
- preserves all unrelated/custom Esteria DBC rows;
- stages and validates both MPQs before atomically replacing the live files.

This script does not touch Wow.exe, server code, SQL, or Patch-Zz.mpq.
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
    _next_row_id,
    _rebase_strings,
    _table,
    _u32,
    _set_u32,
    merge_rows_by_id,
)
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402


STOCK_RACES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 10, 11})
PLAYER_MODEL_PATHS = (
    r"Character\Human\Male\HumanMale.m2",
    r"Character\Human\Female\HumanFemale.m2",
    r"Character\Orc\Male\OrcMale.m2",
    r"Character\Orc\Female\OrcFemale.m2",
    r"Character\Dwarf\Male\DwarfMale.m2",
    r"Character\Dwarf\Female\DwarfFemale.m2",
    r"Character\Nightelf\Male\NightElfMale.m2",
    r"Character\Nightelf\Female\NightElfFemale.m2",
    r"Character\Scourge\Male\SCOURGEMale.m2",
    r"Character\Scourge\Female\SCOURGEFemale.m2",
    r"Character\Tauren\Male\TaurenMale.m2",
    r"Character\Tauren\Female\TaurenFemale.m2",
    r"Character\Gnome\Male\GnomeMale.m2",
    r"Character\Gnome\Female\GnomeFemale.m2",
    r"Character\Troll\Male\TrollMale.m2",
    r"Character\Troll\Female\TrollFemale.m2",
    r"Character\Bloodelf\MALE\BloodElfMale.m2",
    r"Character\Bloodelf\Female\BloodElfFemale.M2",
    r"Character\Draenei\Male\DraeneiMale.m2",
    r"Character\Draenei\Female\DraeneiFemale.m2",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def archive_names(storm: Storm, handle: H) -> dict[str, str]:
    return {name.casefold(): name for name, *_ in storm.list_files(handle)}


def read_entry(storm: Storm, handle: H, names: dict[str, str], key: str) -> bytes:
    actual = names.get(key.casefold())
    if actual is None:
        raise KeyError(f"archive entry is missing: {key}")
    return storm.read(handle, actual)


def merge_char_sections(base_data: bytes, donor_data: bytes) -> bytes:
    """Replace stock-race CharSections while preserving every non-stock Esteria row."""

    base = _table(base_data, "CharSections")
    donor = _table(donor_data, "CharSections")
    preserved = [row for row in base.records if _u32(row, 1) not in STOCK_RACES]
    selected = [row for row in donor.records if _u32(row, 1) in STOCK_RACES]
    selected, strings = _rebase_strings("CharSections", selected, donor.strings, base.strings)

    used_ids = {_u32(row, 0) for row in preserved}
    next_id = _next_row_id(preserved)
    normalized: list[bytes] = []
    for row in selected:
        row_id = _u32(row, 0)
        if row_id in used_ids:
            while next_id in used_ids:
                next_id += 1
            row = _set_u32(row, 0, next_id)
            row_id = next_id
            next_id += 1
        used_ids.add(row_id)
        normalized.append(row)

    return base.build(preserved + normalized, strings)


def derive_stock_dependencies(chr_races_data: bytes, donor_display_data: bytes) -> tuple[set[int], set[int], set[int]]:
    """Return donor display/model/extra IDs belonging to the ten playable stock races."""

    races = _table(chr_races_data, "ChrRaces")
    donor_displays = _table(donor_display_data, "CreatureDisplayInfo")

    player_display_ids = {
        _u32(row, field)
        for row in races.records
        if _u32(row, 0) in STOCK_RACES
        for field in (4, 5)
    }
    by_id = {_u32(row, 0): row for row in donor_displays.records}
    missing = sorted(player_display_ids - set(by_id))
    if missing:
        raise ValueError(f"donor is missing stock player CreatureDisplayInfo rows: {missing}")

    model_ids = {_u32(by_id[display_id], 1) for display_id in player_display_ids}
    display_rows = [row for row in donor_displays.records if _u32(row, 1) in model_ids]
    display_ids = {_u32(row, 0) for row in display_rows}
    extra_ids = {_u32(row, 3) for row in display_rows if _u32(row, 3)}
    return display_ids, model_ids, extra_ids


def build_merged_dbcs(
    base: dict[str, bytes], donor_x: dict[str, bytes], donor_w: dict[str, bytes]
) -> tuple[dict[str, bytes], dict[str, object]]:
    required_base = {
        "ChrRaces",
        "CharSections",
        "CreatureDisplayInfo",
        "CreatureModelData",
        "CreatureDisplayInfoExtra",
    }
    missing_base = sorted(required_base - set(base))
    if missing_base:
        raise ValueError(f"Esteria enUS-Z is missing required DBC(s): {', '.join(missing_base)}")

    for name in ("CharSections", "CreatureDisplayInfo", "CreatureModelData"):
        if name not in donor_x:
            raise ValueError(f"donor patch-enUS-x is missing {name}.dbc")
    if "CreatureDisplayInfoExtra" not in donor_w:
        raise ValueError("donor patch-enUS-w is missing CreatureDisplayInfoExtra.dbc")

    display_ids, model_ids, extra_ids = derive_stock_dependencies(
        base["ChrRaces"], donor_x["CreatureDisplayInfo"]
    )

    output = {
        "CharSections": merge_char_sections(base["CharSections"], donor_x["CharSections"]),
        "CreatureDisplayInfo": merge_rows_by_id(
            "CreatureDisplayInfo",
            base["CreatureDisplayInfo"],
            donor_x["CreatureDisplayInfo"],
            display_ids,
        ),
        "CreatureModelData": merge_rows_by_id(
            "CreatureModelData",
            base["CreatureModelData"],
            donor_x["CreatureModelData"],
            model_ids,
        ),
        "CreatureDisplayInfoExtra": merge_rows_by_id(
            "CreatureDisplayInfoExtra",
            base["CreatureDisplayInfoExtra"],
            donor_w["CreatureDisplayInfoExtra"],
            extra_ids,
        ),
    }

    donor_sections = _table(donor_x["CharSections"], "CharSections")
    stock_section_counts = {
        race: sum(1 for row in donor_sections.records if _u32(row, 1) == race)
        for race in sorted(STOCK_RACES)
    }
    metadata: dict[str, object] = {
        "stock_races": sorted(STOCK_RACES),
        "char_sections_by_race": stock_section_counts,
        "char_sections_total": sum(stock_section_counts.values()),
        "display_rows": len(display_ids),
        "model_rows": len(model_ids),
        "extra_rows": len(extra_ids),
        "display_ids": sorted(display_ids),
        "model_ids": sorted(model_ids),
        "extra_ids": sorted(extra_ids),
    }
    return output, metadata


def load_dbc_entries(storm: Storm, archive: Path, table_names: tuple[str, ...]) -> dict[str, bytes]:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        result: dict[str, bytes] = {}
        for table in table_names:
            key = rf"DBFilesClient\{table}.dbc"
            actual = names.get(key.casefold())
            if actual is not None:
                result[table] = storm.read(handle, actual)
        return result
    finally:
        storm.dll.SFileCloseArchive(handle)


def donor_asset_names(storm: Storm, archive: Path) -> list[str]:
    handle = storm.open_archive(archive)
    try:
        selected = []
        for name, *_ in storm.list_files(handle):
            folded = name.casefold()
            if folded.startswith("character\\") or folded.startswith("textures\\"):
                selected.append(name)
        return sorted(selected, key=str.casefold)
    finally:
        storm.dll.SFileCloseArchive(handle)


def splice_assets(storm: Storm, donor_archive: Path, target_archive: Path, names: list[str]) -> None:
    """Stream donor assets into target so we never hold the whole model pack in memory."""

    donor = storm.open_archive(donor_archive)
    target = storm.open_archive(target_archive)
    try:
        storm.ensure_capacity(target, len(names))
        for index, name in enumerate(names, 1):
            payload = storm.read(donor, name)
            file_handle = H()
            flags = 0x80000000  # MPQ_FILE_REPLACEEXISTING
            if not storm.dll.SFileCreateFile(
                target,
                name.encode("ascii"),
                0,
                len(payload),
                0,
                flags,
                c.byref(file_handle),
            ):
                raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
            try:
                buffer = c.create_string_buffer(payload or b"\0")
                if not storm.dll.SFileWriteFile(file_handle, buffer, len(payload), 0x00000002):
                    raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
            finally:
                storm.dll.SFileCloseFile(file_handle)
            if index % 1000 == 0:
                print(f"  assets: {index}/{len(names)}")
    finally:
        storm.dll.SFileCloseArchive(target)
        storm.dll.SFileCloseArchive(donor)


def splice_dbcs(storm: Storm, target_archive: Path, dbcs: dict[str, bytes]) -> None:
    entries = {rf"DBFilesClient\{name}.dbc": payload for name, payload in dbcs.items()}
    storm.replace_archive_entries(target_archive, entries)


def rebuild_archive_streaming(storm: Storm, source_path: Path, target_path: Path) -> None:
    """Rebuild an MPQ one entry at a time to discard stale replaced blocks without high memory use."""

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
        # Create a classic MPQ v1 with regenerated listfile/attributes. Keeping the
        # rebuilt archive below 4 GiB preserves 3.3.5a compatibility.
        create_flags = 0x00100000 | 0x00200000
        if not storm.dll.SFileCreateArchive(
            str(target_path),
            create_flags,
            len(source_entries) + 64,
            c.byref(target),
        ):
            raise OSError(f"SFileCreateArchive failed: {target_path} ({c.get_last_error()})")

        for index, name in enumerate(source_entries, 1):
            payload = storm.read(source, name)
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
                raise OSError(f"SFileCreateFile failed while rebuilding: {name} ({c.get_last_error()})")
            finished = False
            try:
                buffer = c.create_string_buffer(payload or b"\0")
                if not storm.dll.SFileWriteFile(file_handle, buffer, len(payload), 0x00000002):
                    raise OSError(f"SFileWriteFile failed while rebuilding: {name} ({c.get_last_error()})")
                if not storm.dll.SFileFinishFile(file_handle):
                    raise OSError(f"SFileFinishFile failed while rebuilding: {name} ({c.get_last_error()})")
                finished = True
            finally:
                if not finished:
                    storm.dll.SFileCloseFile(file_handle)
            if index % 1000 == 0:
                print(f"  rebuild: {index}/{len(source_entries)}")
    finally:
        if target:
            storm.dll.SFileCloseArchive(target)
        storm.dll.SFileCloseArchive(source)

    rebuilt = storm.open_archive(target_path)
    original = storm.open_archive(source_path)
    try:
        rebuilt_names = {
            name.casefold()
            for name, *_ in storm.list_files(rebuilt)
            if name.casefold() not in {"(listfile)", "(attributes)"}
        }
        original_names = {
            name.casefold()
            for name, *_ in storm.list_files(original)
            if name.casefold() not in {"(listfile)", "(attributes)"}
        }
        if rebuilt_names != original_names:
            missing = sorted(original_names - rebuilt_names)
            extra = sorted(rebuilt_names - original_names)
            raise ValueError(
                f"rebuilt archive file table mismatch: missing={missing[:3]} extra={extra[:3]}"
            )
    finally:
        storm.dll.SFileCloseArchive(original)
        storm.dll.SFileCloseArchive(rebuilt)


def validate_stage(
    storm: Storm,
    donor_assets_archive: Path,
    target_assets_archive: Path,
    target_locale_archive: Path,
    expected_assets: list[str],
    donor_x: dict[str, bytes],
    metadata: dict[str, object],
) -> dict[str, object]:
    target_handle = storm.open_archive(target_assets_archive)
    donor_handle = storm.open_archive(donor_assets_archive)
    try:
        target_names = archive_names(storm, target_handle)
        donor_names = archive_names(storm, donor_handle)
        missing_assets = [name for name in expected_assets if name.casefold() not in target_names]
        if missing_assets:
            raise ValueError(f"staged patch-Z is missing {len(missing_assets)} donor assets; first={missing_assets[0]}")

        critical_hashes: dict[str, str] = {}
        for key in PLAYER_MODEL_PATHS:
            donor_actual = donor_names.get(key.casefold())
            target_actual = target_names.get(key.casefold())
            if donor_actual is None or target_actual is None:
                raise ValueError(f"critical player model is missing: {key}")
            donor_payload = storm.read(donor_handle, donor_actual)
            target_payload = storm.read(target_handle, target_actual)
            if donor_payload != target_payload:
                raise ValueError(f"critical player model does not match donor: {key}")
            if len(target_payload) < 8 or target_payload[:4] != b"MD20" or struct.unpack_from("<I", target_payload, 4)[0] != 0x108:
                raise ValueError(f"critical player model is not WotLK M2 v0x108: {key}")
            critical_hashes[key] = hashlib.sha256(target_payload).hexdigest()
    finally:
        storm.dll.SFileCloseArchive(donor_handle)
        storm.dll.SFileCloseArchive(target_handle)

    staged = load_dbc_entries(
        storm,
        target_locale_archive,
        ("ChrRaces", "CharSections", "CreatureDisplayInfo", "CreatureModelData", "CreatureDisplayInfoExtra"),
    )
    sections = _table(staged["CharSections"], "CharSections")
    donor_sections = _table(donor_x["CharSections"], "CharSections")
    for race in STOCK_RACES:
        have = sum(1 for row in sections.records if _u32(row, 1) == race)
        want = sum(1 for row in donor_sections.records if _u32(row, 1) == race)
        if have != want:
            raise ValueError(f"CharSections race {race}: staged={have}, donor={want}")

    for table in ("CreatureDisplayInfo", "CreatureModelData", "CreatureDisplayInfoExtra"):
        _table(staged[table], table)

    return {
        "asset_entries_verified": len(expected_assets),
        "critical_player_models_verified": len(critical_hashes),
        "critical_model_sha256": critical_hashes,
        "dbc_metadata": metadata,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Splice WoD stock race models into Esteria Z/enUS-Z")
    parser.add_argument(
        "--client-root",
        type=Path,
        default=Path(r"G:\3.3.5a - Dev"),
    )
    parser.add_argument(
        "--donor-root",
        type=Path,
        default=Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)"),
    )
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--apply", action="store_true", help="perform backup + staged migration; default is read-only dry-run")
    parser.add_argument("--compact-current", action="store_true", help="stage, compact, validate, and reinstall the already-migrated live Z archives")
    args = parser.parse_args()
    if args.apply and args.compact_current:
        parser.error("--apply and --compact-current are mutually exclusive")

    client_root = args.client_root.resolve()
    donor_root = args.donor_root.resolve()
    patch_z = client_root / "Data" / "patch-Z.MPQ"
    enus_z = client_root / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    donor_x_assets = donor_root / "Data" / "patch-x.mpq"
    donor_x_locale = donor_root / "Data" / "enUS" / "patch-enUS-x.mpq"
    donor_w_locale = donor_root / "Data" / "enUS" / "patch-enUS-w.mpq"

    for path in (patch_z, enus_z, donor_x_assets, donor_x_locale, donor_w_locale, args.stormlib):
        if not path.is_file():
            raise FileNotFoundError(path)

    storm = Storm(args.stormlib)
    base = load_dbc_entries(
        storm,
        enus_z,
        ("ChrRaces", "CharSections", "CreatureDisplayInfo", "CreatureModelData", "CreatureDisplayInfoExtra"),
    )
    donor_x = load_dbc_entries(
        storm,
        donor_x_locale,
        ("CharSections", "CreatureDisplayInfo", "CreatureModelData"),
    )
    donor_w = load_dbc_entries(storm, donor_w_locale, ("CreatureDisplayInfoExtra",))
    merged_dbcs, metadata = build_merged_dbcs(base, donor_x, donor_w)
    assets = donor_asset_names(storm, donor_x_assets)

    summary = {
        "client_root": str(client_root),
        "donor_root": str(donor_root),
        "asset_entries": len(assets),
        "dbc_metadata": metadata,
        "apply": args.apply,
        "compact_current": args.compact_current,
    }
    print(json.dumps(summary, indent=2))

    if args.compact_current:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        compact_dir = client_root / "Backups" / f"wod-models-compact-{stamp}"
        compact_dir.mkdir(parents=True, exist_ok=False)
        backup_patch_z = compact_dir / patch_z.name
        backup_enus_z = compact_dir / enus_z.name
        stage_patch_z = compact_dir / "STAGED-patch-Z.MPQ"
        stage_enus_z = compact_dir / "STAGED-patch-enUS-Z.MPQ"
        print(f"Backing up pre-compact migrated archives to {compact_dir}")
        shutil.copy2(patch_z, backup_patch_z)
        shutil.copy2(enus_z, backup_enus_z)
        shutil.copy2(patch_z, stage_patch_z)
        shutil.copy2(enus_z, stage_enus_z)
        before_compact = {
            "patch-Z.MPQ": {"size": patch_z.stat().st_size, "sha256": sha256(patch_z)},
            "patch-enUS-Z.MPQ": {"size": enus_z.stat().st_size, "sha256": sha256(enus_z)},
        }
        print("Rebuilding staged migrated archives to remove stale MPQ blocks")
        rebuilt_patch_z = compact_dir / "REBUILT-patch-Z.MPQ"
        rebuilt_enus_z = compact_dir / "REBUILT-patch-enUS-Z.MPQ"
        rebuild_archive_streaming(storm, stage_patch_z, rebuilt_patch_z)
        rebuild_archive_streaming(storm, stage_enus_z, rebuilt_enus_z)
        stage_patch_z.unlink()
        stage_enus_z.unlink()
        rebuilt_patch_z.replace(stage_patch_z)
        rebuilt_enus_z.replace(stage_enus_z)
        print("Validating rebuilt staged archives")
        validation = validate_stage(
            storm,
            donor_x_assets,
            stage_patch_z,
            stage_enus_z,
            assets,
            donor_x,
            metadata,
        )
        os.replace(stage_patch_z, patch_z)
        os.replace(stage_enus_z, enus_z)
        after_compact = {
            "patch-Z.MPQ": {"size": patch_z.stat().st_size, "sha256": sha256(patch_z)},
            "patch-enUS-Z.MPQ": {"size": enus_z.stat().st_size, "sha256": sha256(enus_z)},
        }
        report = {
            "backup_dir": str(compact_dir),
            "before_compact": before_compact,
            "after_compact": after_compact,
            "validation": validation,
        }
        (compact_dir / "compaction.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0

    if not args.apply:
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = client_root / "Backups" / f"wod-models-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup_patch_z = backup_dir / patch_z.name
    backup_enus_z = backup_dir / enus_z.name
    stage_patch_z = backup_dir / "STAGED-patch-Z.MPQ"
    stage_enus_z = backup_dir / "STAGED-patch-enUS-Z.MPQ"

    print(f"Backing up live archives to {backup_dir}")
    shutil.copy2(patch_z, backup_patch_z)
    shutil.copy2(enus_z, backup_enus_z)
    before = {
        "patch-Z.MPQ": {"size": patch_z.stat().st_size, "sha256": sha256(patch_z)},
        "patch-enUS-Z.MPQ": {"size": enus_z.stat().st_size, "sha256": sha256(enus_z)},
    }
    (backup_dir / "before.json").write_text(json.dumps(before, indent=2) + "\n", encoding="utf-8")

    print("Creating staged working copies")
    shutil.copy2(patch_z, stage_patch_z)
    shutil.copy2(enus_z, stage_enus_z)

    print(f"Splicing {len(assets)} WoD character/texture assets")
    splice_assets(storm, donor_x_assets, stage_patch_z, assets)
    print("Splicing stock-race DBC rows")
    splice_dbcs(storm, stage_enus_z, merged_dbcs)

    print("Rebuilding staged archives to remove stale MPQ blocks")
    rebuilt_patch_z = backup_dir / "REBUILT-patch-Z.MPQ"
    rebuilt_enus_z = backup_dir / "REBUILT-patch-enUS-Z.MPQ"
    rebuild_archive_streaming(storm, stage_patch_z, rebuilt_patch_z)
    rebuild_archive_streaming(storm, stage_enus_z, rebuilt_enus_z)
    stage_patch_z.unlink()
    stage_enus_z.unlink()
    rebuilt_patch_z.replace(stage_patch_z)
    rebuilt_enus_z.replace(stage_enus_z)

    print("Validating staged archives")
    validation = validate_stage(
        storm,
        donor_x_assets,
        stage_patch_z,
        stage_enus_z,
        assets,
        donor_x,
        metadata,
    )
    (backup_dir / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    print("Installing validated staged archives")
    os.replace(stage_patch_z, patch_z)
    os.replace(stage_enus_z, enus_z)

    after = {
        "patch-Z.MPQ": {"size": patch_z.stat().st_size, "sha256": sha256(patch_z)},
        "patch-enUS-Z.MPQ": {"size": enus_z.stat().st_size, "sha256": sha256(enus_z)},
    }
    (backup_dir / "after.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"backup_dir": str(backup_dir), "before": before, "after": after, "validation": validation}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
