"""Compare target CreatureDisplayInfo texture fields between donor and Patch-C."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

DONOR_DBC = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
IDS = (141254, 141255, 141687, 141688, 60004, 60006)


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def main() -> None:
    donor = RawWdbc((DONOR_DBC / "CreatureDisplayInfo.dbc").read_bytes())
    donor_rows = {int.from_bytes(r[:4], "little"): r for r in donor.records}
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        packed = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturedisplayinfo.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    packed_rows = {int.from_bytes(r[:4], "little"): r for r in packed.records}

    for display_id in IDS:
        for label, table, rows in (
            ("donor", donor, donor_rows),
            ("Patch-C", packed, packed_rows),
        ):
            row = rows.get(display_id)
            if row is None:
                print(f"{display_id} {label}: absent")
                continue
            values = [
                (int.from_bytes(row[f * 4 : f * 4 + 4], "little"),
                 cstring(table.strings, int.from_bytes(row[f * 4 : f * 4 + 4], "little")))
                for f in (6, 7, 8)
            ]
            print(f"{display_id} {label}: {values}")


if __name__ == "__main__":
    main()
