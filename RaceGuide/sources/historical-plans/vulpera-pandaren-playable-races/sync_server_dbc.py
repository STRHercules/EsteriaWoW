"""Compare client Patch-C DBC tables against the worldserver runtime copies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import (  # noqa: E402
    MODEL_TABLES,
    RACE_TABLES,
    RawWdbc,
    TARGET_RACES,
)

TABLES = tuple(RACE_TABLES) + tuple(MODEL_TABLES)


def read_client_tables(patch_c: Path) -> dict[str, bytes]:
    storm = Storm(DLL_DEFAULT)
    archive = storm.open_archive(patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(archive)}
        collected: dict[str, bytes] = {}
        for table in TABLES:
            key = rf"dbfilesclient\{table}.dbc".casefold()
            if key not in names:
                continue
            collected[table] = storm.read(archive, names[key])
        return collected
    finally:
        storm.dll.SFileCloseArchive(archive)


def summarize(data: bytes, table: str) -> dict[str, object]:
    wdbc = RawWdbc(data)
    ids = [int.from_bytes(record[:4], "little") for record in wdbc.records]
    return {
        "table": table,
        "bytes": len(data),
        "records": wdbc.count,
        "fields": wdbc.fields,
        "record_size": wdbc.record_size,
        "max_id": max(ids, default=0),
        "target_ids": sorted({value for value in ids if value in TARGET_RACES}),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--server-dbc", type=Path)
    parser.add_argument("--export-root", type=Path)
    args = parser.parse_args()

    client = read_client_tables(args.patch_c)
    if args.export_root is not None:
        args.export_root.mkdir(parents=True, exist_ok=True)
        for table, payload in client.items():
            (args.export_root / f"{table}.dbc").write_bytes(payload)

    report: dict[str, object] = {}
    for table, payload in sorted(client.items()):
        rows = [summarize(payload, table)]
        server_path = None if args.server_dbc is None else args.server_dbc / f"{table}.dbc"
        if server_path is not None and server_path.is_file():
            rows.append(summarize(server_path.read_bytes(), table))
        report[table] = rows
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
