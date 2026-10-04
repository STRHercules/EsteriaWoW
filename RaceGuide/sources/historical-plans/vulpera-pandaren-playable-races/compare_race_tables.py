"""Per-race row counts for character tables: PATCH-A vs Patch-C vs PATCH-X."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RACE_BYTE_LAYOUTS, RawWdbc  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = {
    "PATCH-A": CLIENT / "Data" / "PATCH-A.MPQ",
    "Patch-C": CLIENT / "Data" / "Patch-C.MPQ",
    "PATCH-X": CLIENT / "Data" / "PATCH-X.MPQ",
}
TABLES = ("CharSections", "CharHairGeosets", "CharHairTextures", "CharacterFacialHairStyles", "NameGen")


def load(storm: Storm, archive: Path, table: str) -> RawWdbc:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        key = f"dbfilesclient\\{table}.dbc".casefold()
        return RawWdbc(storm.read(handle, names[key]))
    finally:
        storm.dll.SFileCloseArchive(handle)


def counts(table: RawWdbc, name: str) -> Counter[int]:
    offset, width = RACE_BYTE_LAYOUTS[name]
    return Counter(
        int.from_bytes(record[offset : offset + width], "little") for record in table.records
    )


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for name in TABLES:
        print(f"== {name} ==")
        per_archive = {}
        for label, path in ARCHIVES.items():
            if not path.is_file():
                continue
            try:
                per_archive[label] = counts(load(storm, path, name), name)
            except Exception as error:  # noqa: BLE001
                print(f"   {label}: unreadable ({error})")
        for race in (14, 15, 18, 20):
            values = {label: table.get(race, 0) for label, table in per_archive.items()}
            print(f"   race {race}: {values}")


if __name__ == "__main__":
    main()
