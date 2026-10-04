"""Dump ChrRaces rows from any DBC or MPQ for comparison."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402


def dump(label: str, data: bytes, races: set[int] | None) -> None:
    table = RawWdbc(data)
    print(f"== {label} ==")
    for record in table.records:
        race = int.from_bytes(record[:4], "little")
        if races and race not in races:
            continue
        print(
            f"  race {race:>2} flags=0x{int.from_bytes(record[4:8], 'little'):08x} "
            f"faction={int.from_bytes(record[8:12], 'little'):>5} "
            f"lang={int.from_bytes(record[28:32], 'little')} "
            f"display={int.from_bytes(record[16:20], 'little')}/"
            f"{int.from_bytes(record[20:24], 'little')}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--races", type=int, nargs="*")
    args = parser.parse_args()
    wanted = set(args.races) if args.races else None
    for path in args.paths:
        if path.suffix.casefold() == ".mpq":
            storm = Storm(DLL_DEFAULT)
            handle = storm.open_archive(path)
            try:
                names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
                payload = storm.read(handle, names["dbfilesclient\\chrraces.dbc"])
            finally:
                storm.dll.SFileCloseArchive(handle)
            dump(path.name, payload, wanted)
        else:
            dump(path.name, path.read_bytes(), wanted)


if __name__ == "__main__":
    main()
