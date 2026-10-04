"""Show server-only CharStartOutfit/CharSections rows and client coverage."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from playable_race_pack import RawWdbc  # noqa: E402


def load(side: str, table: str) -> RawWdbc:
    folder = "client-dbc-extract" if side == "client" else "server-dbc-snapshot"
    return RawWdbc((HERE / folder / f"{table}.dbc").read_bytes())


def u32(record: bytes, field: int) -> int:
    return int.from_bytes(record[field * 4 : field * 4 + 4], "little")


def main() -> None:
    client = load("client", "CharStartOutfit")
    server = load("server", "CharStartOutfit")
    client_keys = {(u32(r, 1), u32(r, 2), u32(r, 3)) for r in client.records}
    orphans = [r for r in server.records if u32(r, 0) not in {u32(c, 0) for c in client.records}]
    print(f"CharStartOutfit server-only rows: {len(orphans)}")
    uncovered = [r for r in orphans if (u32(r, 1), u32(r, 2), u32(r, 3)) not in client_keys]
    print(f"  not covered by client race/class/gender: {len(uncovered)}")
    for record in uncovered[:20]:
        print(
            f"    id={u32(record, 0)} race={u32(record, 1)} "
            f"class={u32(record, 2)} gender={u32(record, 3)}"
        )

    client = load("client", "CharSections")
    server = load("server", "CharSections")
    client_keys = Counter((u32(r, 1), u32(r, 2), u32(r, 3)) for r in client.records)
    orphans = [r for r in server.records if u32(r, 0) not in {u32(c, 0) for c in client.records}]
    print(f"CharSections server-only rows: {len(orphans)}")
    uncovered = Counter(
        (u32(r, 1), u32(r, 2), u32(r, 3)) for r in orphans
    )
    gap = {
        key: (count, client_keys[key])
        for key, count in uncovered.items()
        if client_keys[key] < count
    }
    print(f"  logical keys where server has more rows than client: {gap}")
    for record in orphans[:15]:
        print(
            f"    id={u32(record, 0)} race={u32(record, 1)} gender={u32(record, 2)} "
            f"type={u32(record, 3)} variant={u32(record, 9)}"
        )


if __name__ == "__main__":
    main()
