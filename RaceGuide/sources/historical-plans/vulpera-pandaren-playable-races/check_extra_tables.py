"""Inspect CharVariations / CreatureDisplayInfoGeosetData in donor and client."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

DONOR = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = ("Data/Patch-C.MPQ", "Data/PATCH-A.MPQ", "Data/common.MPQ", "Data/patch.MPQ")
TABLES = ("CharVariations", "CreatureDisplayInfoGeosetData")
RACES = (18, 19, 20)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    pool: dict[str, tuple[str, str]] = {}
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            for name, *_ in storm.list_files(handle):
                pool.setdefault(name.casefold(), (relative, name))
        finally:
            storm.dll.SFileCloseArchive(handle)

    for table in TABLES:
        key = f"dbfilesclient\\{table}.dbc".casefold()
        donor_path = next(
            (p for p in DONOR.glob("*.dbc") if p.name.casefold() == f"{table}.dbc".casefold()),
            None,
        )
        print(f"== {table} ==")
        if donor_path is not None:
            data = donor_path.read_bytes()
            print(f"   donor: {len(data)} bytes")
            if len(data) >= 20 and data[:4] == b"WDBC":
                wdbc = RawWdbc(data)
                print(f"   donor rows={wdbc.count} fields={wdbc.fields}")
                if table == "CharVariations":
                    races = sorted({int.from_bytes(r[:4], "little") for r in wdbc.records})
                    print(f"   donor race ids: {races[:20]}")
                    for race in RACES:
                        rows = [r for r in wdbc.records if int.from_bytes(r[:4], "little") == race]
                        print(f"      race {race}: {len(rows)} rows")
        entry = pool.get(key)
        if entry is None:
            print("   client: table not present in checked archives")
            continue
        handle = storm.open_archive(CLIENT / entry[0])
        try:
            data = storm.read(handle, entry[1])
        finally:
            storm.dll.SFileCloseArchive(handle)
        print(f"   client: {entry[0]} {len(data)} bytes")
        if len(data) >= 20 and data[:4] == b"WDBC":
            wdbc = RawWdbc(data)
            print(f"   client rows={wdbc.count} fields={wdbc.fields}")
            if table == "CharVariations":
                races = sorted({int.from_bytes(r[:4], "little") for r in wdbc.records})
                print(f"   client race ids: {races[:20]}")


if __name__ == "__main__":
    main()
