"""Verify CharSections texture paths for races 18/20 exist in Patch-C."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

HERE = Path(__file__).resolve().parent
CLIENT = REPO / "3.3.5a - Dev"
TARGET_RACES = {18, 20}


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def main() -> None:
    sections = RawWdbc((HERE / "client-dbc-extract" / "CharSections.dbc").read_bytes())
    paths: dict[str, set[int]] = {}
    for record in sections.records:
        race = int.from_bytes(record[4:8], "little")
        if race not in TARGET_RACES:
            continue
        for field in (4, 5, 6):
            offset = int.from_bytes(record[field * 4 : field * 4 + 4], "little")
            value = cstring(sections.strings, offset)
            if not value:
                continue
            paths.setdefault(value.casefold().replace("/", "\\"), set()).add(race)

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(CLIENT / "Data" / "Patch-C.MPQ")
    try:
        names = {name.casefold() for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)

    missing = {path: races for path, races in paths.items() if path not in names}
    print(f"distinct textures: {len(paths)}  missing: {len(missing)}")
    for path, races in sorted(missing.items())[:20]:
        print(f"    MISSING {path} (races {sorted(races)})")


if __name__ == "__main__":
    main()
