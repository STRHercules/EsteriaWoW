"""Compare hair/customization table coverage between stock and custom races."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
TABLES = ("CharHairGeosets", "CharHairTextures", "CharacterFacialHairStyles")
RACES = (1, 4, 18, 20)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        loaded = {
            table: RawWdbc(storm.read(handle, names[f"dbfilesclient\\{table}.dbc".casefold()]))
            for table in TABLES
        }
    finally:
        storm.dll.SFileCloseArchive(handle)

    for table, wdbc in loaded.items():
        print(f"== {table}: {wdbc.count} rows, {wdbc.fields} fields ==")
        per_race: dict[int, dict[int, list[tuple[int, ...]]]] = defaultdict(lambda: defaultdict(list))
        for record in wdbc.records:
            fields = [int.from_bytes(record[i * 4 : i * 4 + 4], "little") for i in range(wdbc.fields)]
            race = fields[1] if table != "CharHairGeosets" else fields[1]
            gender = fields[2]
            per_race[race][gender].append(tuple(fields))
        for race in RACES:
            for gender in (0, 1):
                rows = per_race.get(race, {}).get(gender, [])
                sample = sorted({row[3] for row in rows})[:10]
                print(
                    f"   race {race} gender {gender}: {len(rows)} rows, "
                    f"field3 values={sample}"
                )


if __name__ == "__main__":
    main()
