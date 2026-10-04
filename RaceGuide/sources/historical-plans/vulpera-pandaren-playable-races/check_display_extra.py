"""Check CreatureDisplayInfoExtra coverage for the custom player display ids."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
IDS = (60000, 60001, 60002, 60003, 141254, 141687)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        table = RawWdbc(
            storm.read(handle, names["dbfilesclient\\creaturedisplayinfoextra.dbc"])
        )
    finally:
        storm.dll.SFileCloseArchive(handle)
    present = {int.from_bytes(record[:4], "little") for record in table.records}
    for value in IDS:
        print(f"{value}: extra_row={'yes' if value in present else 'no'}")
    print(f"total extra rows: {len(present)} max={max(present)}")


if __name__ == "__main__":
    main()
