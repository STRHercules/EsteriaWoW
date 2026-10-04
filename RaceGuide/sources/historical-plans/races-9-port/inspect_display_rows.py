"""Print CreatureDisplayInfo fields 6-10 and the resolved portrait texture for chosen rows."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inspect_client_races import Client  # noqa: E402

KEY = "DBFilesClient\\CreatureDisplayInfo.dbc"
ROWS = (49, 50, 60002, 60008, 60010, 60012, 60014, 60016, 60018, 60020, 60022, 60024, 141254, 141687)


def main() -> None:
    client = Client()
    table = client.table(KEY)
    assert table
    print(f"fields={table.fields} record={table.record_size} strings={len(table.strings)}")
    wanted = tuple(int(a) for a in sys.argv[1:]) or ROWS
    for row_id in wanted:
        row = next((r for r in table.rows if r[0] == row_id), None)
        if row is None:
            print(f"{row_id}: missing")
            continue
        name = table.text(row[9]) if row[9] < len(table.strings) else "<out of pool>"
        print(f"  display {row_id}: model={row[1]} textureVariation={row[6:9]} portrait={row[9]} ({name!r}) "
              f"bloodLevel={row[10]} blood={row[11]} npcSound={row[12]} particle={row[13]} "
              f"geoset={row[14]} effectPackage={row[15]}")


if __name__ == "__main__":
    main()
