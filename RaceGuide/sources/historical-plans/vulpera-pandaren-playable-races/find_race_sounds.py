"""Look for Pandaren/Vulpera named sound entries in the client."""

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
        sounds = RawWdbc(storm.read(handle, names["dbfilesclient\\soundentries.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    def cstring(offset: int) -> str:
        if not offset:
            return ""
        end = sounds.strings.find(b"\x00", offset)
        return sounds.strings[offset:end].decode("ascii", "replace")

    for record in sounds.records:
        row_id = int.from_bytes(record[:4], "little")
        name = cstring(int.from_bytes(record[4:8], "little"))
        if any(key in name.casefold() for key in ("pandaren", "vulpera", "sethrak", "broken")):
            print(f"{row_id}: {name!r}")


if __name__ == "__main__":
    main()
