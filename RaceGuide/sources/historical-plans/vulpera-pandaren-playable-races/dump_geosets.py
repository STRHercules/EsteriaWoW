"""Show GeosetGroup values for the preview display rows."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
IDS = (9906, 9913, 9915, 10005, 10006, 10008)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        table = RawWdbc(storm.read(handle, names["dbfilesclient\\itemdisplayinfo.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    def text(offset: int) -> str:
        if not offset:
            return ""
        end = table.strings.find(b"\x00", offset)
        return table.strings[offset:end].decode("ascii", "replace")

    for record in table.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id not in IDS:
            continue
        models = [text(int.from_bytes(record[f * 4 : f * 4 + 4], "little")) for f in (1, 2)]
        geosets = [int.from_bytes(record[f * 4 : f * 4 + 4], "little") for f in (7, 8, 9)]
        flags = int.from_bytes(record[10 * 4 : 11 * 4], "little")
        textures = [text(int.from_bytes(record[f * 4 : f * 4 + 4], "little")) for f in range(15, 23)]
        print(f"{row_id}: models={models}")
        print(f"    geosets={geosets} flags={flags}")
        print(f"    textures={[t for t in textures if t]}")


if __name__ == "__main__":
    main()
