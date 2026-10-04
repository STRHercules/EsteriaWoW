from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import (
    APPEARANCE_TABLES,
    RACE_FIELDS,
    STOCK_RACES,
    STRING_FIELDS,
    WORLD_DISPLAY_IDS,
    WORLD_DISPLAY_PAIRS,
    _read_string,
    _rebase_strings,
    _table,
    _u32,
    hd_dependencies,
    load_donor_tables,
    merge_table_set,
    world_chr_races_payload,
    world_display_payload,
)
from cars_mount_pack import DLL_DEFAULT, Storm
from replace_wod_with_ascension_hd import DBC_TABLES, read_tables
from wod_model_migration import archive_names, sha256

DEFAULT_CLIENT = Path(r"G:\3.3.5a - Dev")
DEFAULT_ASCENSION = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted")
SERVER_CONT_DIR = "/azerothcore/env/dist/data/dbc-continuations"
SERVER_DBC_DIR = "/azerothcore/env/dist/data/dbc"
SERVER_FILES = (
    "ChrRaces.dbc1-ascension-hd",
    "CreatureDisplayInfo.dbc1-ascension-hd",
    "CreatureModelData.dbc1-ascension-hd",
)
HIGH_DISPLAY_IDS = frozenset(
    {
        141284, 141285, 141286, 141287, 141669, 141670, 141671, 141672, 141673, 141674,
        141675, 141676, 141677, 141678, 141679, 141680, 141681, 141682, 141683, 141684,
    }
)


def docker(*args: str, capture: bool = True, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
        check=check,
    )


def row_map(data: bytes, table_name: str) -> dict[int, bytes]:
    table = _table(data, table_name)
    result: dict[int, bytes] = {}
    for row in table.records:
        row_id = _u32(row, 0)
        if row_id in result:
            raise ValueError(f"{table_name} contains duplicate row ID {row_id}")
        result[row_id] = row
    return result


def assert_nonstock_preserved(before: dict[str, bytes], after: dict[str, bytes]) -> dict[str, int]:
    preserved: dict[str, int] = {}

    # Race-keyed appearance tables must preserve every custom/non-stock row byte-for-byte.
    for table_name in APPEARANCE_TABLES:
        race_field = RACE_FIELDS[table_name]
        old = _table(before[table_name], table_name)
        new = _table(after[table_name], table_name)
        old_rows = [row for row in old.records if _u32(row, race_field) not in STOCK_RACES]
        new_rows = [row for row in new.records if _u32(row, race_field) not in STOCK_RACES]
        if old_rows != new_rows:
            raise ValueError(f"{table_name}: a non-stock/custom race row changed")
        preserved[table_name] = len(old_rows)

    # ChrRaces custom rows are not touched at all.
    old = _table(before["ChrRaces"], "ChrRaces")
    new = _table(after["ChrRaces"], "ChrRaces")
    old_rows = [row for row in old.records if _u32(row, 0) not in STOCK_RACES]
    new_rows = [row for row in new.records if _u32(row, 0) not in STOCK_RACES]
    if old_rows != new_rows:
        raise ValueError("ChrRaces: a custom race row changed")
    preserved["ChrRaces"] = len(old_rows)

    # Every existing display row except the 20 Ascension HD rows must remain byte-identical.
    old_map = row_map(before["CreatureDisplayInfo"], "CreatureDisplayInfo")
    new_map = row_map(after["CreatureDisplayInfo"], "CreatureDisplayInfo")
    for row_id, row in old_map.items():
        if row_id in HIGH_DISPLAY_IDS:
            continue
        if new_map.get(row_id) != row:
            raise ValueError(f"CreatureDisplayInfo: unrelated existing row {row_id} changed")
    preserved["CreatureDisplayInfo_existing"] = len(old_map) - len(HIGH_DISPLAY_IDS & old_map.keys())

    # Model/extra rows are semantically preserved.  Ascension model rows may get a new
    # string-pool offset while still resolving to the exact same path.
    for table_name in ("CreatureModelData", "CreatureDisplayInfoExtra"):
        old_table = _table(before[table_name], table_name)
        new_table = _table(after[table_name], table_name)
        old_map = {_u32(row, 0): row for row in old_table.records}
        new_map = {_u32(row, 0): row for row in new_table.records}
        for row_id, old_row in old_map.items():
            new_row = new_map.get(row_id)
            if new_row is None:
                raise ValueError(f"{table_name}: existing row {row_id} disappeared")
            if table_name == "CreatureModelData" and row_id >= 112887 and row_id <= 112926:
                old_path = _read_string(old_table.strings, _u32(old_row, 2))
                new_path = _read_string(new_table.strings, _u32(new_row, 2))
                old_numeric = old_row[:8] + old_row[12:]
                new_numeric = new_row[:8] + new_row[12:]
                if old_path != new_path or old_numeric != new_numeric:
                    raise ValueError(f"CreatureModelData: HD model row {row_id} changed semantically")
            elif new_row != old_row:
                raise ValueError(f"{table_name}: unrelated existing row {row_id} changed")
        preserved[f"{table_name}_existing"] = len(old_map)

    return preserved


def validate_display_contract(merged: dict[str, bytes], donor: dict[str, bytes]) -> dict[str, object]:
    client_races = _table(merged["ChrRaces"], "ChrRaces")
    client_displays = _table(merged["CreatureDisplayInfo"], "CreatureDisplayInfo")
    donor_displays = _table(donor["CreatureDisplayInfo"], "CreatureDisplayInfo")

    client_by_display = {_u32(row, 0): row for row in client_displays.records}
    donor_by_display = {_u32(row, 0): row for row in donor_displays.records}
    race_pairs: dict[str, dict[str, list[int]]] = {}

    for race, low_pair in WORLD_DISPLAY_PAIRS.items():
        race_row = next(row for row in client_races.records if _u32(row, 0) == race)
        high_pair = (_u32(race_row, 4), _u32(race_row, 5))
        race_pairs[str(race)] = {"glue": list(high_pair), "world": list(low_pair)}
        for high_id, low_id in zip(high_pair, low_pair):
            high = client_by_display[high_id]
            low = client_by_display[low_id]
            donor_row = donor_by_display[high_id]
            if _u32(high, 1) != _u32(low, 1):
                raise ValueError(f"Display clone {low_id} does not point to the same model as {high_id}")
            if low_id >= 65536:
                raise ValueError(f"World display {low_id} is not 16-bit safe")
            # Verify all four string-valued display fields semantically match Ascension.
            for field in STRING_FIELDS["CreatureDisplayInfo"]:
                client_value = _read_string(client_displays.strings, _u32(high, field))
                donor_value = _read_string(donor_displays.strings, _u32(donor_row, field))
                if client_value != donor_value:
                    raise ValueError(
                        f"CreatureDisplayInfo {high_id} field {field} string mismatch: "
                        f"client={client_value!r} donor={donor_value!r}"
                    )
                low_value = _read_string(client_displays.strings, _u32(low, field))
                if low_value != donor_value:
                    raise ValueError(f"World display {low_id} field {field} string mismatch")

    return {"pairs": race_pairs, "world_display_ids": sorted(WORLD_DISPLAY_IDS)}


def build_model_continuation(merged_model_data: bytes, donor: dict[str, bytes]) -> bytes:
    _, model_ids, _ = hd_dependencies(donor["ChrRaces"], donor["CreatureDisplayInfo"])
    source = _table(merged_model_data, "CreatureModelData")
    selected = [row for row in source.records if _u32(row, 0) in model_ids]
    if {_u32(row, 0) for row in selected} != model_ids:
        raise ValueError("Merged CreatureModelData is missing an Ascension HD model row")
    selected, strings = _rebase_strings(
        "CreatureModelData",
        selected,
        source.strings,
        b"\0",
        normalize_model_paths=False,
    )
    return source.build(selected, strings)


def copy_server_file(remote: str, local: Path, *, required: bool = True) -> bool:
    local.parent.mkdir(parents=True, exist_ok=True)
    result = docker("cp", f"ac-worldserver:{remote}", str(local), check=False)
    if result.returncode != 0:
        if required:
            raise RuntimeError(f"docker cp failed for {remote}: {result.stderr.strip()}")
        return False
    return True


def install_server_file(local: Path, remote: str) -> None:
    result = docker("cp", str(local), f"ac-worldserver:{remote}", check=False)
    if result.returncode != 0:
        raise RuntimeError(f"docker cp install failed for {local.name}: {result.stderr.strip()}")


def assert_server_range_free(backup_dir: Path) -> None:
    server_base = backup_dir / "server-base-CreatureDisplayInfo.dbc"
    copy_server_file(f"{SERVER_DBC_DIR}/CreatureDisplayInfo.dbc", server_base)
    base = _table(server_base.read_bytes(), "CreatureDisplayInfo")
    collisions = sorted({_u32(row, 0) for row in base.records} & WORLD_DISPLAY_IDS)
    if collisions:
        raise ValueError(f"49000-range collides with server base DBC: {collisions}")

    before_dir = backup_dir / "server-continuations-before"
    before_dir.mkdir(parents=True, exist_ok=True)
    for filename in SERVER_FILES:
        copy_server_file(f"{SERVER_CONT_DIR}/{filename}", before_dir / filename, required=False)
    # Battlemon is the only other CreatureDisplayInfo continuation currently loaded.
    battlemon = before_dir / "CreatureDisplayInfo.dbc1-battlemon"
    copy_server_file(f"{SERVER_CONT_DIR}/CreatureDisplayInfo.dbc1-battlemon", battlemon, required=False)
    if battlemon.exists():
        table = _table(battlemon.read_bytes(), "CreatureDisplayInfo")
        collisions = sorted({_u32(row, 0) for row in table.records} & WORLD_DISPLAY_IDS)
        if collisions:
            raise ValueError(f"49000-range collides with Battlemon continuation: {collisions}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair the live Ascension HD stock-race world display mapping")
    parser.add_argument("--client-root", type=Path, default=DEFAULT_CLIENT)
    parser.add_argument("--ascension-root", type=Path, default=DEFAULT_ASCENSION)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client_root = args.client_root.resolve()
    ascension_root = args.ascension_root.resolve()
    enus_z = client_root / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    storm = Storm(DLL_DEFAULT)

    current = read_tables(storm, enus_z)
    donor = load_donor_tables(ascension_root / "DBFilesClient")
    merged = merge_table_set(current, donor)

    preserved = assert_nonstock_preserved(current, merged)
    display_contract = validate_display_contract(merged, donor)

    changed = [name for name in DBC_TABLES if current[name] != merged[name]]
    server_payloads = {
        "ChrRaces.dbc1-ascension-hd": world_chr_races_payload(merged["ChrRaces"]),
        "CreatureDisplayInfo.dbc1-ascension-hd": world_display_payload(merged["CreatureDisplayInfo"]),
        "CreatureModelData.dbc1-ascension-hd": build_model_continuation(merged["CreatureModelData"], donor),
    }

    summary = {
        "apply": args.apply,
        "changed_client_tables": changed,
        "preserved_nonstock_or_existing_rows": preserved,
        "display_contract": display_contract,
        "client_archive_before_sha256": sha256(enus_z),
        "client_archive_before_size": enus_z.stat().st_size,
    }
    print(json.dumps(summary, indent=2))
    if not args.apply:
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = client_root / "Backups" / f"ascension-hd-world-fix-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    client_backup = backup_dir / "patch-enUS-Z.MPQ"
    shutil.copy2(enus_z, client_backup)

    stage_dir = backup_dir / "server-continuations-new"
    stage_dir.mkdir()
    for filename, payload in server_payloads.items():
        (stage_dir / filename).write_bytes(payload)
        table_name = filename.split(".dbc1", 1)[0]
        _table(payload, table_name)

    assert_server_range_free(backup_dir)

    # Stage is fully validated.  Mutate only the DBC entries that actually changed.
    entries = {f"DBFilesClient\\{name}.dbc": merged[name] for name in changed}
    try:
        storm.replace_archive_entries(enus_z, entries)
        readback = read_tables(storm, enus_z)
        for name in changed:
            if readback[name] != merged[name]:
                raise ValueError(f"client DBC readback failed for {name}")
        validate_display_contract(readback, donor)

        for filename in SERVER_FILES:
            install_server_file(stage_dir / filename, f"{SERVER_CONT_DIR}/{filename}")

        docker("restart", "ac-worldserver", capture=True)
        time.sleep(8)
        logs = docker("logs", "--since", "20s", "ac-worldserver", capture=True, check=False)
        combined = (logs.stdout or "") + (logs.stderr or "")
        required_log_fragments = (
            "ChrRaces.dbc1-ascension-hd -> 10 row(s) into ChrRaces.dbc",
            "CreatureDisplayInfo.dbc1-ascension-hd -> 20 row(s) into CreatureDisplayInfo.dbc",
            "CreatureModelData.dbc1-ascension-hd -> 20 row(s) into CreatureModelData.dbc",
        )
        missing_logs = [fragment for fragment in required_log_fragments if fragment not in combined]
        if missing_logs:
            raise RuntimeError(f"worldserver restart did not confirm Ascension continuations: {missing_logs}")

    except Exception:
        shutil.copy2(client_backup, enus_z)
        before_dir = backup_dir / "server-continuations-before"
        for filename in SERVER_FILES:
            old = before_dir / filename
            if old.exists():
                install_server_file(old, f"{SERVER_CONT_DIR}/{filename}")
        docker("restart", "ac-worldserver", capture=True, check=False)
        raise

    final = read_tables(storm, enus_z)
    final_contract = validate_display_contract(final, donor)
    report = {
        **summary,
        "backup_dir": str(backup_dir),
        "client_archive_after_sha256": sha256(enus_z),
        "client_archive_after_size": enus_z.stat().st_size,
        "final_display_contract": final_contract,
        "worldserver_restart_verified": True,
    }
    (backup_dir / "repair-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
