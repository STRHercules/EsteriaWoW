"""Point the server-side ChrRaces.dbc at the 16-bit player display ids too."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from playable_race_pack import RawWdbc  # noqa: E402

SOURCE = HERE / "server-dbc-final2" / "ChrRaces.dbc"
DISPLAYS = {18: (60004, 60005), 20: (60006, 60007)}
CONTAINER = "ac-worldserver"
TARGET = "/azerothcore/env/dist/data/dbc/ChrRaces.dbc"


def main() -> None:
    table = RawWdbc(SOURCE.read_bytes())
    records = []
    for record in table.records:
        race = int.from_bytes(record[:4], "little")
        if race in DISPLAYS:
            male, female = DISPLAYS[race]
            values = bytearray(record)
            values[16:20] = male.to_bytes(4, "little")
            values[20:24] = female.to_bytes(4, "little")
            record = bytes(values)
        records.append(record)
    payload = table.build(records)
    out = HERE / "server-chrraces-16bit.dbc"
    out.write_bytes(payload)
    print(f"wrote {out} ({len(payload)} bytes)")

    verify = RawWdbc(payload)
    for record in verify.records:
        race = int.from_bytes(record[:4], "little")
        if race in DISPLAYS:
            print(
                f"   race {race}: display="
                f"{int.from_bytes(record[16:20], 'little')}/"
                f"{int.from_bytes(record[20:24], 'little')}"
            )

    subprocess.run(
        ["docker", "cp", str(out), f"{CONTAINER}:{TARGET}"],
        check=True,
        capture_output=True,
    )
    print("deployed to container")


if __name__ == "__main__":
    main()
