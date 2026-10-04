"""Show CharSections texture assignments for races 18/20 male, low variations."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        table = RawWdbc(storm.read(handle, names["dbfilesclient\\charsections.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    def text(offset: int) -> str:
        if not offset:
            return ""
        end = table.strings.find(b"\x00", offset)
        return table.strings[offset:end].decode("ascii", "replace")

    for race in (18, 20):
        print(f"== race {race} male ==")
        for record in table.records:
            if int.from_bytes(record[4:8], "little") != race:
                continue
            if int.from_bytes(record[8:12], "little") != 0:
                continue
            section = int.from_bytes(record[12:16], "little")
            variation = int.from_bytes(record[36:40], "little")
            if section not in (0, 1, 4) or variation > 1:
                continue
            textures = [
                text(int.from_bytes(record[f * 4 : f * 4 + 4], "little")) for f in (4, 5, 6)
            ]
            print(f"    section={section} variation={variation} textures={[t for t in textures if t]}")


if __name__ == "__main__":
    main()
