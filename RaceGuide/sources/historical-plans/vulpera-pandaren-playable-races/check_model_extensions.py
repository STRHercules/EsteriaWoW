"""Compare CharacterModelData paths for custom races between PATCH-A and Patch-C."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
INTERESTING = {4896, 4897, 4898, 4899, 112885, 112886, 112929, 112930}


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def load(storm: Storm, archive: Path, table: str) -> RawWdbc:
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        return RawWdbc(storm.read(handle, names[f"dbfilesclient\\{table}.dbc".casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    archives = {
        "PATCH-A": CLIENT / "Data" / "PATCH-A.MPQ",
        "Patch-C": CLIENT / "Data" / "Patch-C.MPQ",
        "PATCH-X": CLIENT / "Data" / "PATCH-X.MPQ",
    }
    tables = {label: load(storm, path, "CreatureModelData") for label, path in archives.items()}
    for label, table in tables.items():
        rows = {int.from_bytes(r[:4], "little"): r for r in table.records}
        print(f"== {label} ==")
        for model_id in sorted(INTERESTING):
            row = rows.get(model_id)
            if row is None:
                continue
            print(f"   {model_id}: {cstring(table.strings, int.from_bytes(row[8:12], 'little'))}")

    entries: dict[str, set[str]] = {}
    for label, path in archives.items():
        handle = storm.open_archive(path)
        try:
            entries[label] = {n.casefold() for n, *_ in storm.list_files(handle)}
        finally:
            storm.dll.SFileCloseArchive(handle)
    for needle in ("esteriabroken\\male\\brokenmale", "sethrak\\male\\sethrakmale"):
        print(f"-- files matching {needle} --")
        for label, names in entries.items():
            hits = sorted(n for n in names if needle in n)
            print(f"   {label}: {len(hits)} {hits[:4]}")


if __name__ == "__main__":
    main()
