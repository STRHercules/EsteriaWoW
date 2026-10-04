"""Print every field for a couple of display rows to spot anomalies."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
IDS = (49, 60000, 60006, 60004)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        table = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturedisplayinfo.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    rows = {int.from_bytes(r[:4], "little"): r for r in table.records}
    for display_id in IDS:
        row = rows[display_id]
        fields = [int.from_bytes(row[i * 4 : i * 4 + 4], "little") for i in range(16)]
        print(f"{display_id}: {fields}")


if __name__ == "__main__":
    main()
