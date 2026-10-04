"""List donor DBC tables that the client archives do not contain."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
DONOR = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")
ARCHIVES = (
    "Data/common.MPQ",
    "Data/common-2.MPQ",
    "Data/expansion.MPQ",
    "Data/lichking.MPQ",
    "Data/patch.MPQ",
    "Data/patch-2.MPQ",
    "Data/patch-3.MPQ",
    "Data/patch-4.mpq",
    "Data/PATCH-A.MPQ",
    "Data/PATCH-X.MPQ",
    "Data/Patch-C.MPQ",
    "Data/Patch-F.MPQ",
    "Data/Patch-O.mpq",
    "Data/enUS/base-enUS.MPQ",
    "Data/enUS/locale-enUS.MPQ",
    "Data/enUS/expansion-locale-enUS.MPQ",
    "Data/enUS/lichking-locale-enUS.MPQ",
    "Data/enUS/patch-enUS.MPQ",
    "Data/enUS/patch-enUS-2.MPQ",
    "Data/enUS/patch-enUS-3.MPQ",
)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    shipped: set[str] = set()
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            shipped |= {
                Path(name).name.casefold()
                for name, *_ in storm.list_files(handle)
                if name.casefold().startswith("dbfilesclient\\")
            }
        finally:
            storm.dll.SFileCloseArchive(handle)

    donor = {p.name.casefold() for p in DONOR.glob("*.dbc")}
    missing = sorted(donor - shipped)
    print(f"client tables: {len(shipped)}  donor tables: {len(donor)}  donor-only: {len(missing)}")
    for name in missing:
        print(f"   {name}")


if __name__ == "__main__":
    main()
