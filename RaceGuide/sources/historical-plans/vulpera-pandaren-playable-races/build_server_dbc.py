"""Build server runtime DBCs: client Patch-C rows win, server-only rows kept."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from playable_race_pack import RawWdbc, _rebase_string_records  # noqa: E402

TABLES = (
    "ChrRaces",
    "CharStartOutfit",
    "CharSections",
    "BarberShopStyle",
    "SkillLineAbility",
    "SkillRaceClassInfo",
    "CharBaseInfo",
    "ItemDisplayInfo",
)


def merge(table: str, client: RawWdbc, server: RawWdbc) -> tuple[bytes, int]:
    client_ids = {record[:4] for record in client.records}
    extras = [record for record in server.records if record[:4] not in client_ids]
    if not extras:
        return client.build(client.records), 0
    rebased, extra_strings = _rebase_string_records(
        table, extras, server.strings, len(client.strings)
    )
    payload = client.build([*client.records, *rebased], client.strings + extra_strings)
    return payload, len(rebased)


def force_not_playable(data: bytes, races: set[int]) -> bytes:
    """Set the ChrRaces NOT_PLAYABLE bit (0x1) on the given race rows."""
    table = RawWdbc(data)
    records = []
    for record in table.records:
        if int.from_bytes(record[:4], "little") in races:
            values = bytearray(record)
            values[4:8] = (int.from_bytes(values[4:8], "little") | 1).to_bytes(4, "little")
            record = bytes(values)
        records.append(record)
    return table.build(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", type=Path, required=True)
    parser.add_argument("--server", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--disable-races", type=int, nargs="*", default=[])
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    for table in TABLES:
        client = RawWdbc((args.client / f"{table}.dbc").read_bytes())
        server_path = args.server / f"{table}.dbc"
        if not server_path.is_file():
            (args.out / f"{table}.dbc").write_bytes(client.build(client.records))
            print(f"{table}: server copy missing, wrote client table ({client.count} rows)")
            continue
        server = RawWdbc(server_path.read_bytes())
        payload, kept = merge(table, client, server)
        if table == "ChrRaces" and args.disable_races:
            payload = force_not_playable(payload, set(args.disable_races))
        (args.out / f"{table}.dbc").write_bytes(payload)
        print(
            f"{table}: client={client.count} server={server.count} "
            f"kept_server_only={kept} out={RawWdbc(payload).count}"
        )


if __name__ == "__main__":
    main()
