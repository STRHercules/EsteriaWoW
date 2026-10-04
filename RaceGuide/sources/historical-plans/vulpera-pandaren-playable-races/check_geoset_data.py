"""Check donor CreatureDisplayInfoGeosetData rows for the target race displays."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from playable_race_pack import RawWdbc  # noqa: E402

DONOR = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
DISPLAYS = (141254, 141255, 141687, 141688, 60004, 60005, 60006, 60007)


def main() -> None:
    table = RawWdbc((DONOR / "CreatureDisplayInfoGeosetData.dbc").read_bytes())
    print(f"rows={table.count} fields={table.fields}")
    counts: dict[int, int] = {}
    for record in table.records:
        display_id = int.from_bytes(record[:4], "little")
        counts[display_id] = counts.get(display_id, 0) + 1
    print(f"distinct display ids: {len(counts)} max={max(counts)}")
    for display_id in DISPLAYS:
        rows = [
            [int.from_bytes(r[i * 4 : i * 4 + 4], "little") for i in range(table.fields)]
            for r in table.records
            if int.from_bytes(r[:4], "little") == display_id
        ]
        print(f"   display {display_id}: {len(rows)} rows {rows[:4]}")


if __name__ == "__main__":
    main()
