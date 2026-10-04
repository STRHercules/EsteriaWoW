"""Check whether the ported display rows' string offsets are valid in the donor pool."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import Wdbc  # noqa: E402

DONOR = HERE.parent / "vulpera-pandaren-playable-races/eunoia-dbc/CreatureDisplayInfo.dbc"
ROWS = (2, 3, 33070, 32902, 33174, 32, 34, 28, 29, 27298, 14754, 5, 6, 37, 41, 12, 24)


def main() -> None:
    table = Wdbc(DONOR.read_bytes())
    pool = table.strings
    starts = {0}
    for index, byte in enumerate(pool):
        if byte == 0:
            starts.add(index + 1)
    print(f"donor pool size {len(pool)}, head {pool[:60]!r}")
    for offset in (51,):
        end = pool.find(b"\x00", offset)
        print(f"donor offset {offset}: {pool[offset:end]!r} (valid start: {offset in starts})")
    for row_id in ROWS:
        row = next((r for r in table.rows if r[0] == row_id), None)
        if row is None:
            print(f"  donor display {row_id}: missing")
            continue
        print(f"  donor display {row_id}: extra={row[3]} fields6-9={row[6:10]} "
              f"valid={[value in starts for value in row[6:10]]}")


if __name__ == "__main__":
    main()
