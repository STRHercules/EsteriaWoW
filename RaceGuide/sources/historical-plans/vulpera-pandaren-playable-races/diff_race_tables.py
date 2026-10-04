"""Row-level diff of race tables between client Patch-C and the server runtime."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

CLIENT_EXTRACT = Path(__file__).resolve().parent / "client-dbc-extract"
SERVER_SNAPSHOT = Path(__file__).resolve().parent / "server-dbc-snapshot"

TABLES = (
    "ChrRaces",
    "CharStartOutfit",
    "CharSections",
    "BarberShopStyle",
    "SkillLineAbility",
    "SkillRaceClassInfo",
    "CharBaseInfo",
)


def rows_by_id(path: Path) -> dict[int, bytes]:
    wdbc = RawWdbc(path.read_bytes())
    return {int.from_bytes(row[:4], "little"): row for row in wdbc.records}


def main() -> None:
    for table in TABLES:
        client = rows_by_id(CLIENT_EXTRACT / f"{table}.dbc")
        server = rows_by_id(SERVER_SNAPSHOT / f"{table}.dbc")
        only_client = sorted(set(client) - set(server))
        only_server = sorted(set(server) - set(client))
        differing = sorted(
            key
            for key in set(client) & set(server)
            if client[key] != server[key]
        )
        print(
            f"{table}: client={len(client)} server={len(server)} "
            f"client_only={only_client[:12]}{'...' if len(only_client) > 12 else ''} "
            f"server_only={only_server[:12]}{'...' if len(only_server) > 12 else ''} "
            f"differing={len(differing)} {differing[:12]}"
        )
        if table == "ChrRaces":
            for race in (15, 18, 20, 26):
                for label, table_rows in (("client", client), ("server", server)):
                    row = table_rows.get(race)
                    if row is None:
                        print(f"  race {race} {label}: absent")
                        continue
                    flags = int.from_bytes(row[4:8], "little")
                    faction = int.from_bytes(row[8:12], "little")
                    print(
                        f"  race {race} {label}: flags=0x{flags:08x} "
                        f"playable={bool(flags & 1)} faction={faction} "
                        f"male_display={int.from_bytes(row[16:20], 'little')} "
                        f"female_display={int.from_bytes(row[20:24], 'little')}"
                    )


if __name__ == "__main__":
    main()
