"""Dump ChrRaces fields side by side for working and crashing custom races."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
RACES = (14, 15, 18, 20)
STRING_FIELDS = (6, 11, 65, 66, 67) + tuple(range(14, 30))


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        table = RawWdbc(storm.read(handle, names["dbfilesclient\\chrraces.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    def text(offset: int) -> str:
        if not offset:
            return ""
        end = table.strings.find(b"\x00", offset)
        return table.strings[offset:end].decode("ascii", "replace")

    rows = {int.from_bytes(r[:4], "little"): r for r in table.records}
    for race in RACES:
        row = rows[race]
        values = [int.from_bytes(row[i * 4 : i * 4 + 4], "little") for i in range(69)]
        named = {
            "flags": values[1],
            "faction": values[2],
            "explorationSound": values[3],
            "model_m": values[4],
            "model_f": values[5],
            "prefix": text(values[6]),
            "baseLang": values[7],
            "creatureType": values[8],
            "resSickness": values[9],
            "splashSound": values[10],
            "clientFile": text(values[11]),
            "cinematic": values[12],
            "alliance": values[13],
            "facialHair1": text(values[65]),
            "facialHair2": text(values[66]),
            "hair": text(values[67]),
            "requiredExpansion": values[68],
        }
        print(f"race {race}: {named}")


if __name__ == "__main__":
    main()
