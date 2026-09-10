# -*- coding: utf-8 -*-
"""Move Battlemon shiny display rows inside a WDBCZ continuation file."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

OLD_SHINY_BASE = 60000
NEW_SHINY_BASE = 70000
NORMAL_BASE = 50000
FORM_COUNT = 1581
HEADER_SIZE = 20


def read_u32(data: bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def relocate(path: Path) -> None:
    data = bytearray(path.read_bytes())
    if data[:4] != b"WDBC" or data[4:5] != b"Z":
        raise SystemExit(f"not a WDBCZ continuation: {path}")

    row_count = read_u32(data, 4)
    field_count = read_u32(data, 8)
    record_size = read_u32(data, 12)
    string_size = read_u32(data, 16)
    expected_size = HEADER_SIZE + row_count * record_size + string_size
    if (row_count, field_count, record_size) != (FORM_COUNT * 2, 16, 64) or len(data) != expected_size:
        raise SystemExit(f"unexpected WDBCZ shape: {path}")

    old_ids = set(range(NORMAL_BASE + 1, NORMAL_BASE + FORM_COUNT + 1))
    old_ids.update(range(OLD_SHINY_BASE + 1, OLD_SHINY_BASE + FORM_COUNT + 1))
    ids = [read_u32(data, HEADER_SIZE + row * record_size) for row in range(row_count)]
    if set(ids) != old_ids or len(ids) != len(set(ids)):
        raise SystemExit(f"unexpected Battlemon display IDs: {path}")

    for row in range(row_count):
        offset = HEADER_SIZE + row * record_size
        display_id = read_u32(data, offset)
        if OLD_SHINY_BASE < display_id <= OLD_SHINY_BASE + FORM_COUNT:
            struct.pack_into("<I", data, offset, display_id + (NEW_SHINY_BASE - OLD_SHINY_BASE))

    new_ids = [read_u32(data, HEADER_SIZE + row * record_size) for row in range(row_count)]
    expected_ids = set(range(NORMAL_BASE + 1, NORMAL_BASE + FORM_COUNT + 1))
    expected_ids.update(range(NEW_SHINY_BASE + 1, NEW_SHINY_BASE + FORM_COUNT + 1))
    if set(new_ids) != expected_ids or {60002, 60003} & set(new_ids):
        raise SystemExit(f"rewritten IDs failed validation: {path}")

    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
    print(f"{path}: {row_count} rows, shiny {OLD_SHINY_BASE + 1}-{OLD_SHINY_BASE + FORM_COUNT} -> "
          f"{NEW_SHINY_BASE + 1}-{NEW_SHINY_BASE + FORM_COUNT}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", type=Path, nargs="+")
    args = parser.parse_args()
    for path in args.paths:
        if not path.is_file():
            raise SystemExit(f"file not found: {path}")
        relocate(path)


if __name__ == "__main__":
    main()
