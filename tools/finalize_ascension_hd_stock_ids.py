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

from ascension_hd_migration import (
    APPEARANCE_TABLES,
    NPC_STOCK_TO_HD_MODEL,
    STOCK_DISPLAY_PAIRS,
    STOCK_RACES,
    WORLD_DISPLAY_IDS,
    _read_string,
    _rebase_strings,
    _set_u32,
    _table,
    _u32,
    hd_dependencies,
    load_donor_tables,
    merge_appearance_table,
    merge_stock_model_rows,
    restore_stock_chr_race_displays,
)
from cars_mount_pack import DLL_DEFAULT, Storm
from wod_model_migration import archive_names

DEFAULT_CLIENT = Path(r"G:\3.3.5a - Dev")
DEFAULT_ASCENSION = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted")

TABLES = (
    "ChrRaces",
    "CharSections",
    "CharHairGeosets",
    "CharHairTextures",
    "CharacterFacialHairStyles",
    "BarberShopStyle",
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


def read_tables(storm: Storm, archive: Path) -> dict[str, bytes]:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        result: dict[str, bytes] = {}
        for table_name in TABLES:
            actual = names.get(f"dbfilesclient\\{table_name.lower()}.dbc")
            if actual is None:
                raise KeyError(f"{archive} is missing DBFilesClient\\{table_name}.dbc")
            result[table_name] = storm.read(handle, actual)
        return result
    finally:
        storm.dll.SFileCloseArchive(handle)


def filter_rows(table_name: str, data: bytes, remove_ids: set[int]) -> bytes:
    table = _table(data, table_name)
    records = [record for record in table.records if _u32(record, 0) not in remove_ids]
    return table.build(records, table.strings)


def build_corrected_tables(base: dict[str, bytes], donor: dict[str, bytes]) -> tuple[dict[str, bytes], dict[str, object]]:
    display_ids, source_model_ids, _ = hd_dependencies(donor["ChrRaces"], donor["CreatureDisplayInfo"])
    cleanup_display_ids = set(display_ids) | set(WORLD_DISPLAY_IDS)

    output = dict(base)
    output["ChrRaces"] = restore_stock_chr_race_displays(base["ChrRaces"])
    for table_name in APPEARANCE_TABLES:
        output[table_name] = merge_appearance_table(table_name, base[table_name], donor[table_name])

    # Remove only the temporary player-display rows introduced by the failed
    # high-ID/16-bit-clone migration.  Stock CreatureDisplayInfo rows stay exact.
    output["CreatureDisplayInfo"] = filter_rows(
        "CreatureDisplayInfo",
        base["CreatureDisplayInfo"],
        cleanup_display_ids,
    )

    # Remove the temporary high source model rows from the client table, then
    # copy their metadata onto the native stock model IDs.
    cleaned_models = filter_rows(
        "CreatureModelData",
        base["CreatureModelData"],
        set(source_model_ids),
    )
    output["CreatureModelData"] = merge_stock_model_rows(
        cleaned_models,
        donor["CreatureModelData"],
    )

    return output, {
        "removed_high_display_ids": sorted(display_ids),
        "removed_world_clone_ids": sorted(WORLD_DISPLAY_IDS),
        "removed_source_model_ids": sorted(source_model_ids),
    }


def stock_model_paths(data: bytes) -> dict[int, str]:
    table = _table(data, "CreatureModelData")
    by_id = {_u32(record, 0): record for record in table.records}
    result: dict[int, str] = {}
    for destination_id in NPC_STOCK_TO_HD_MODEL:
        record = by_id.get(destination_id)
        if record is None:
            raise ValueError(f"CreatureModelData is missing stock model row {destination_id}")
        result[destination_id] = _read_string(table.strings, _u32(record, 2)).decode("latin1")
    return result


def validate_corrected_tables(
    before: dict[str, bytes],
    after: dict[str, bytes],
    donor: dict[str, bytes],
) -> dict[str, object]:
    display_ids, source_model_ids, _ = hd_dependencies(donor["ChrRaces"], donor["CreatureDisplayInfo"])
    cleanup_display_ids = set(display_ids) | set(WORLD_DISPLAY_IDS)

    races = _table(after["ChrRaces"], "ChrRaces")
    race_pairs: dict[int, tuple[int, int]] = {}
    for record in races.records:
        race = _u32(record, 0)
        if race in STOCK_RACES:
            race_pairs[race] = (_u32(record, 4), _u32(record, 5))
    if race_pairs != STOCK_DISPLAY_PAIRS:
        raise ValueError(f"stock ChrRaces display pairs are wrong: {race_pairs}")

    displays = _table(after["CreatureDisplayInfo"], "CreatureDisplayInfo")
    display_row_ids = {_u32(record, 0) for record in displays.records}
    bad_displays = display_row_ids & cleanup_display_ids
    if bad_displays:
        raise ValueError(f"temporary Ascension display IDs remain: {sorted(bad_displays)}")

    models = _table(after["CreatureModelData"], "CreatureModelData")
    model_row_ids = {_u32(record, 0) for record in models.records}
    bad_models = model_row_ids & set(source_model_ids)
    if bad_models:
        raise ValueError(f"temporary Ascension source model IDs remain: {sorted(bad_models)}")

    paths = stock_model_paths(after["CreatureModelData"])
    expected_fragments = {
        49: "Human2\\Male\\HumanMale2.m2",
        50: "Human2\\Female\\HumanFemale2.m2",
        51: "Orc2\\Male\\OrcMale2.m2",
        52: "Orc2\\Female\\OrcFemale2.m2",
        53: "Dwarf2\\Male\\DwarfMale2.m2",
        54: "Dwarf2\\Female\\DwarfFemale2.m2",
        55: "NightElf2\\Male\\NightElfMale2.m2",
        56: "NightElf2\\Female\\NightElfFemale2.m2",
        57: "Scourge2\\Male\\ScourgeMale2.m2",
        58: "Scourge2\\Female\\ScourgeFemale2.m2",
        59: "Tauren2\\Male\\TaurenMale2.m2",
        60: "Tauren2\\Female\\TaurenFemale2.m2",
        182: "Gnome2\\Male\\GnomeMale2.m2",
        183: "Gnome2\\Female\\GnomeFemale2.m2",
        185: "Troll2\\Male\\TrollMale2.m2",
        186: "Troll2\\Female\\TrollFemale2.m2",
        2208: "BloodElf2\\Male\\BloodElfMale2.m2",
        2209: "BloodElf2\\Female\\BloodElfFemale2.m2",
        2248: "Draenei2\\Male\\DraeneiMale2.m2",
        2250: "Draenei2\\Female\\DraeneiFemale2.m2",
    }
    for row_id, fragment in expected_fragments.items():
        normalized = paths[row_id].replace("/", "\\")
        if not normalized.casefold().endswith(fragment.casefold()):
            raise ValueError(f"stock model {row_id} path is wrong: {paths[row_id]}")

    # Preserve every non-stock/custom row exactly.  String pools may grow, but
    # offsets in untouched records stay unchanged because merges append strings.
    preservation: dict[str, int] = {}
    for table_name in APPEARANCE_TABLES:
        before_table = _table(before[table_name], table_name)
        after_table = _table(after[table_name], table_name)
        race_field = {
            "CharSections": 1,
            "CharHairGeosets": 1,
            "CharHairTextures": 1,
            "CharacterFacialHairStyles": 0,
            "BarberShopStyle": 37,
        }[table_name]
        before_rows = [row for row in before_table.records if _u32(row, race_field) not in STOCK_RACES]
        after_rows = [row for row in after_table.records if _u32(row, race_field) not in STOCK_RACES]
        if before_rows != after_rows:
            raise ValueError(f"{table_name}: non-stock/custom rows changed")
        preservation[table_name] = len(before_rows)

    before_races = _table(before["ChrRaces"], "ChrRaces")
    after_races = _table(after["ChrRaces"], "ChrRaces")
    before_nonstock = [row for row in before_races.records if _u32(row, 0) not in STOCK_RACES]
    after_nonstock = [row for row in after_races.records if _u32(row, 0) not in STOCK_RACES]
    if before_nonstock != after_nonstock:
        raise ValueError("ChrRaces: custom race rows changed")
    preservation["ChrRaces"] = len(before_nonstock)

    before_displays = _table(before["CreatureDisplayInfo"], "CreatureDisplayInfo")
    after_displays = _table(after["CreatureDisplayInfo"], "CreatureDisplayInfo")
    before_display_rows = [row for row in before_displays.records if _u32(row, 0) not in cleanup_display_ids]
    if before_display_rows != list(after_displays.records):
        raise ValueError("CreatureDisplayInfo: unrelated rows changed")
    preservation["CreatureDisplayInfo"] = len(before_display_rows)

    before_models = _table(before["CreatureModelData"], "CreatureModelData")
    after_models = _table(after["CreatureModelData"], "CreatureModelData")
    ignored_models = set(source_model_ids) | set(NPC_STOCK_TO_HD_MODEL)
    before_model_rows = {
        _u32(row, 0): row
        for row in before_models.records
        if _u32(row, 0) not in ignored_models
    }
    after_model_rows = {
        _u32(row, 0): row
        for row in after_models.records
        if _u32(row, 0) not in ignored_models
    }
    if before_model_rows != after_model_rows:
        raise ValueError("CreatureModelData: unrelated rows changed")
    preservation["CreatureModelData"] = len(before_model_rows)

    stock_counts: dict[str, int] = {}
    for table_name in APPEARANCE_TABLES:
        table = _table(after[table_name], table_name)
        race_field = {
            "CharSections": 1,
            "CharHairGeosets": 1,
            "CharHairTextures": 1,
            "CharacterFacialHairStyles": 0,
            "BarberShopStyle": 37,
        }[table_name]
        stock_counts[table_name] = sum(1 for row in table.records if _u32(row, race_field) in STOCK_RACES)

    return {
        "stock_display_pairs": {str(race): list(pair) for race, pair in sorted(race_pairs.items())},
        "stock_model_paths": {str(row_id): path for row_id, path in sorted(paths.items())},
        "stock_appearance_counts": stock_counts,
        "preserved_rows": preservation,
    }


def validate_assets(storm: Storm, archive: Path, donor_root: Path) -> dict[str, object]:
    character_root = donor_root / "patch-CHA.mpq" / "Character"
    required = [
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
    ]
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        verified: list[str] = []
        for race, sex, stem in required:
            m2_key = f"character\\{race.lower()}\\{sex.lower()}\\{stem.lower()}.m2"
            skin_key = f"character\\{race.lower()}\\{sex.lower()}\\{stem.lower()}00.skin"
            actual_m2 = names.get(m2_key)
            actual_skin = names.get(skin_key)
            if actual_m2 is None:
                raise ValueError(f"client asset archive is missing {m2_key}")
            if actual_skin is None:
                # Ascension naming is usually Stem00.skin, but tolerate _00.skin.
                skin_key = f"character\\{race.lower()}\\{sex.lower()}\\{stem.lower()}_00.skin"
                actual_skin = names.get(skin_key)
            if actual_skin is None:
                raise ValueError(f"client asset archive is missing first skin for {stem}")

            donor_m2 = character_root / race / sex / f"{stem}.m2"
            if not donor_m2.exists():
                # Extracted donor names can differ only in case; resolve by scan.
                matches = [path for path in (character_root / race / sex).glob("*.m2") if path.stem.casefold() == stem.casefold()]
                if len(matches) != 1:
                    raise ValueError(f"cannot resolve donor M2 for {stem}")
                donor_m2 = matches[0]
            if storm.read(handle, actual_m2) != donor_m2.read_bytes():
                raise ValueError(f"client M2 differs from Ascension donor: {actual_m2}")
            verified.append(actual_m2)
        return {"models_verified": len(verified), "models": verified}
    finally:
        storm.dll.SFileCloseArchive(handle)


def build_server_model_continuation(donor_model_data: bytes) -> bytes:
    donor = _table(donor_model_data, "CreatureModelData")
    by_id = {_u32(record, 0): record for record in donor.records}
    rows: list[bytes] = []
    for destination_id, source_id in NPC_STOCK_TO_HD_MODEL.items():
        source = by_id.get(source_id)
        if source is None:
            raise ValueError(f"donor CreatureModelData missing source {source_id}")
        rows.append(_set_u32(source, 0, destination_id))
    rows, strings = _rebase_strings(
        "CreatureModelData",
        rows,
        donor.strings,
        b"\0",
        normalize_model_paths=True,
    )
    return donor.build(rows, strings)


def mysql_scalar(sql: str) -> int:
    command = [
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
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    text = result.stdout.strip()
    return int(text or "0")


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


def docker_cp_to_worldserver(source: Path, destination: str) -> None:
    temporary = "/tmp/esteria-ascension-hd-continuation"
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize Ascension HD stock races on native 3.3.5 display/model IDs")
    parser.add_argument("--client-root", type=Path, default=DEFAULT_CLIENT)
    parser.add_argument("--ascension-root", type=Path, default=DEFAULT_ASCENSION)
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client = args.client_root.resolve()
    donor_root = args.ascension_root.resolve()
    patch_z = client / "Data" / "patch-Z.MPQ"
    locale_z = client / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    donor = load_donor_tables(donor_root / "DBFilesClient")
    storm = Storm(args.stormlib)

    before = {
        "patch-Z": read_tables(storm, patch_z),
        "patch-enUS-Z": read_tables(storm, locale_z),
    }
    corrected: dict[str, dict[str, bytes]] = {}
    reports: dict[str, object] = {}
    metadata: dict[str, object] = {}
    for label, tables in before.items():
        fixed, meta = build_corrected_tables(tables, donor)
        corrected[label] = fixed
        reports[label] = validate_corrected_tables(tables, fixed, donor)
        metadata[label] = meta

    asset_report = validate_assets(storm, patch_z, donor_root)
    preview = {
        "apply": args.apply,
        "archive_hashes_before": {
            "patch-Z": sha256(patch_z),
            "patch-enUS-Z": sha256(locale_z),
        },
        "correction_metadata": metadata,
        "validation": reports,
        "assets": asset_report,
    }
    print(json.dumps(preview, indent=2))
    if not args.apply:
        return 0

    if wow_running():
        raise RuntimeError("Wow.exe is running; close the client before applying the archive repair")
    online = mysql_scalar("SELECT COUNT(*) FROM acore_characters.characters WHERE online <> 0;")
    if online:
        raise RuntimeError(f"refusing to restart worldserver while {online} player(s) are online")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = client / "Backups" / f"ascension-hd-native-stock-{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    backup_data = backup / "Data"
    backup_data.mkdir()
    shutil.copy2(patch_z, backup_data / patch_z.name)
    shutil.copy2(locale_z, backup_data / locale_z.name)
    hashes = {
        "patch-Z": sha256(patch_z),
        "patch-enUS-Z": sha256(locale_z),
    }
    for label, path in (("patch-Z", backup_data / patch_z.name), ("patch-enUS-Z", backup_data / locale_z.name)):
        if sha256(path) != hashes[label]:
            raise RuntimeError(f"backup hash mismatch for {label}")

    server_before = backup / "server-continuations-before"
    server_before.mkdir()
    subprocess.run(
        [
            "docker",
            "cp",
            "ac-worldserver:/azerothcore/env/dist/data/dbc-continuations/.",
            str(server_before),
        ],
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
    storm.replace_archive_entries(stage_z, replacements_z)
    storm.replace_archive_entries(stage_locale, replacements_locale)

    staged_z = read_tables(storm, stage_z)
    staged_locale = read_tables(storm, stage_locale)
    validate_corrected_tables(before["patch-Z"], staged_z, donor)
    validate_corrected_tables(before["patch-enUS-Z"], staged_locale, donor)
    validate_assets(storm, stage_z, donor_root)

    server_payload = build_server_model_continuation(donor["CreatureModelData"])
    server_stage = backup / "CreatureModelData.dbc1-ascension-hd"
    server_stage.write_bytes(server_payload)
    server_table = _table(server_payload, "CreatureModelData")
    if {_u32(record, 0) for record in server_table.records} != set(NPC_STOCK_TO_HD_MODEL):
        raise ValueError("server model continuation does not contain exactly the 20 stock model IDs")

    # Install client archives only after both staged copies and server payload pass.
    os.replace(stage_z, patch_z)
    os.replace(stage_locale, locale_z)

    server_dir = "/azerothcore/env/dist/data/dbc-continuations"
    docker_remove(f"{server_dir}/ChrRaces.dbc1-ascension-hd")
    docker_remove(f"{server_dir}/CreatureDisplayInfo.dbc1-ascension-hd")
    docker_remove(f"{server_dir}/CreatureDisplayInfoExtra.dbc1-ascension-hd")
    docker_cp_to_worldserver(server_stage, f"{server_dir}/CreatureModelData.dbc1-ascension-hd")

    subprocess.run(["docker", "restart", "ac-worldserver"], check=True, stdout=subprocess.PIPE, text=True)
    subprocess.run(["python", "-c", "import time; time.sleep(8)"], check=True)
    log = subprocess.run(
        ["docker", "logs", "--since", "30s", "ac-worldserver"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout
    required_log = [
        "CreatureModelData.dbc1-ascension-hd -> 20 row(s) into CreatureModelData.dbc",
        "Base data/dbc/ files were not modified",
    ]
    missing_log = [needle for needle in required_log if needle not in log]
    if missing_log:
        raise RuntimeError(f"worldserver continuation verification failed: {missing_log}")
    if "ChrRaces.dbc1-ascension-hd" in log or "CreatureDisplayInfo.dbc1-ascension-hd" in log:
        raise RuntimeError("obsolete Ascension race/display continuation still loaded")

    final_z = read_tables(storm, patch_z)
    final_locale = read_tables(storm, locale_z)
    final_report = {
        "backup_dir": str(backup),
        "archive_hashes_after": {
            "patch-Z": sha256(patch_z),
            "patch-enUS-Z": sha256(locale_z),
        },
        "patch-Z": validate_corrected_tables(before["patch-Z"], final_z, donor),
        "patch-enUS-Z": validate_corrected_tables(before["patch-enUS-Z"], final_locale, donor),
        "server_continuation_rows": len(server_table.records),
        "worldserver_verified": True,
    }
    (backup / "manifest.json").write_text(json.dumps(final_report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final_report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
