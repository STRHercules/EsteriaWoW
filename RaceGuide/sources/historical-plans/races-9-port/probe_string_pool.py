"""Show CreatureDisplayInfo's string pool head and what offset 51 lands on."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inspect_client_races import Client  # noqa: E402
from cars_mount_pack import Wdbc  # noqa: E402

KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"


def main() -> None:
    client = Client()
    table = client.table(KEY)
    assert isinstance(table, Wdbc)
    pool = table.strings
    print(f"pool size {len(pool)}")
    print(f"head: {pool[:120]!r}")
    offset = 51
    print(f"at {offset}: {pool[offset:pool.find(b'\\x00', offset)]!r}")
    # valid string starts
    starts = {0}
    for index, byte in enumerate(pool):
        if byte == 0:
            starts.add(index + 1)
    print(f"is {offset} a string start: {offset in starts}")
    for row_id in (60008, 60002, 49):
        row = next((r for r in table.rows if r[0] == row_id), None)
        if row:
            print(f"row {row_id} fields 6-9 = {row[6:10]}, starts? "
                  f"{[value in starts for value in row[6:10]]}")


if __name__ == "__main__":
    main()
