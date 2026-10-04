"""Dump rows from any client DBC (read-only): python dump_dbc.py <key> [column] [value]."""

from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402
from inspect_client_races import ORDER, DATA  # noqa: E402


def main() -> None:
    key = sys.argv[1]
    column = int(sys.argv[2]) if len(sys.argv) > 2 else None
    wanted = {int(a) for a in sys.argv[3:]} if len(sys.argv) > 3 else None
    storm = Storm(DLL_DEFAULT)
    payload = None
    source = None
    for name in ORDER:
        path = DATA / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, key)
                source = name
            except Exception:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    if payload is None:
        raise SystemExit(f"{key}: not found in any archive")
    table = Wdbc(payload)
    print(f"{key} <- {source}: fields={table.fields} record={table.record_size} rows={len(table.rows)}")
    for row in table.rows:
        if column is not None and row[column] not in wanted:
            continue
        print(row)


if __name__ == "__main__":
    main()
