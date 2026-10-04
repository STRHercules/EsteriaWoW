"""Locate CharVariations.dbc across every client archive and report its contents."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = (
    "Data/common.MPQ",
    "Data/common-2.MPQ",
    "Data/expansion.MPQ",
    "Data/lichking.MPQ",
    "Data/patch.MPQ",
    "Data/patch-2.MPQ",
    "Data/patch-3.MPQ",
    "Data/PATCH-A.MPQ",
    "Data/PATCH-X.MPQ",
    "Data/Patch-C.MPQ",
    "Data/enUS/locale-enUS.MPQ",
    "Data/enUS/patch-enUS-2.MPQ",
    "Data/enUS/patch-enUS-3.MPQ",
)
TABLES = ("CharVariations", "CreatureDisplayInfoGeosetData")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for table in TABLES:
        key = f"dbfilesclient\\{table}.dbc".casefold()
        print(f"== {table} ==")
        for relative in ARCHIVES:
            path = CLIENT / relative
            if not path.is_file():
                continue
            try:
                handle = storm.open_archive(path)
            except Exception:  # noqa: BLE001
                continue
            try:
                names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
                actual = names.get(key)
                if actual is None:
                    continue
                data = storm.read(handle, actual)
            finally:
                storm.dll.SFileCloseArchive(handle)
            detail = ""
            if len(data) >= 20 and data[:4] == b"WDBC":
                wdbc = RawWdbc(data)
                detail = f" rows={wdbc.count} fields={wdbc.fields}"
            print(f"   {relative}: {len(data)} bytes{detail}")


if __name__ == "__main__":
    main()
