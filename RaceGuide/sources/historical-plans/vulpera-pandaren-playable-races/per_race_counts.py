"""Per-race row counts for race tables, client Patch-C vs server runtime."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from playable_race_pack import RACE_BYTE_LAYOUTS, RawWdbc, WDBC_LAYOUTS  # noqa: E402

TABLES = (
    "CharStartOutfit",
    "CharSections",
    "BarberShopStyle",
    "CharacterFacialHairStyles",
    "SkillRaceClassInfo",
)


def counts(path: Path, table: str) -> Counter[int]:
    wdbc = RawWdbc(path.read_bytes())
    layout = WDBC_LAYOUTS.get(table)
    offset, width = RACE_BYTE_LAYOUTS[table] if layout else (0, 4)
    return Counter(
        int.from_bytes(record[offset : offset + width], "little")
        for record in wdbc.records
    )


def main() -> None:
    for table in TABLES:
        client = counts(HERE / "client-dbc-extract" / f"{table}.dbc", table)
        server = counts(HERE / "server-dbc-snapshot" / f"{table}.dbc", table)
        races = sorted(set(client) | set(server))
        gaps = {
            race: (server[race], client[race])
            for race in races
            if server[race] > client[race]
        }
        print(f"{table}: client_total={sum(client.values())} server_total={sum(server.values())}")
        print(f"  races where server has more rows (server, client): {gaps}")
        print(
            "  target race rows client: "
            f"18={client[18]} 20={client[20]} | server: 18={server[18]} 20={server[20]}"
        )


if __name__ == "__main__":
    main()
