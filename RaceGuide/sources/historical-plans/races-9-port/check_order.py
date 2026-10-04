"""Verify DBC row ids are strictly ascending (the client binary-searches these tables)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inspect_client_races import Client  # noqa: E402

KEYS = (
    "DBFilesClient\\ChrRaces.dbc",
    "DBFilesClient\\CreatureDisplayInfo.dbc",
    "DBFilesClient\\CreatureDisplayInfoExtra.dbc",
    "DBFilesClient\\CreatureModelData.dbc",
    "DBFilesClient\\CharSections.dbc",
    "DBFilesClient\\CharHairGeosets.dbc",
    "DBFilesClient\\CharacterFacialHairStyles.dbc",
    "DBFilesClient\\CharBaseInfo.dbc",
    "DBFilesClient\\CharStartOutfit.dbc",
)


def main() -> None:
    client = Client()
    for key in KEYS:
        table = client.table(key)
        if table is None:
            print(f"{key}: missing")
            continue
        problems = [
            (index, table.rows[index - 1][0], table.rows[index][0])
            for index in range(1, len(table.rows))
            if table.rows[index][0] <= table.rows[index - 1][0]
        ]
        source = client.source.get(key, "?")
        status = "ordered" if not problems else f"{len(problems)} out-of-order"
        print(f"{key:<48} rows={len(table.rows):<6} {status} <- {source}")
        for index, previous, current in problems[:10]:
            print(f"    row {index}: {previous} then {current}")


if __name__ == "__main__":
    main()
