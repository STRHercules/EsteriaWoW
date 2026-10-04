"""Dump CharVariations rows from the client locale archive and the donor."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
DONOR = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(CLIENT / "Data" / "enUS" / "locale-enUS.MPQ")
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        client = RawWdbc(storm.read(handle, names["dbfilesclient\\charvariations.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    donor = RawWdbc((DONOR / "CharVariations.dbc").read_bytes())

    for label, table in (("client", client), ("donor", donor)):
        print(f"== {label}: {table.count} rows, {table.fields} fields ==")
        for record in table.records:
            fields = [int.from_bytes(record[i * 4 : i * 4 + 4], "little") for i in range(table.fields)]
            print(f"   {fields}")


if __name__ == "__main__":
    main()
