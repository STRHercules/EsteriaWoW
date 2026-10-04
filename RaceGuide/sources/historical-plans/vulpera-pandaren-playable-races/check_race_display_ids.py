"""Check which candidate player display ids exist in the client and what they model."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
CANDIDATES = (
    49, 50, 6894, 6895, 90006, 90007, 90010, 90011,
    3000006, 3000007, 3000010, 3000011,
    141687, 141688, 141254, 141255,
    # ids truncated to 16 bits, in case the client masks the player display field
    141687 % 65536, 141688 % 65536, 141254 % 65536, 141255 % 65536,
    # free custom ids in the range Sethrak already uses
    60002, 60003, 60004, 60005, 60006, 60007, 60008,
)


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        displays = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturedisplayinfo.dbc"]))
        models = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturemodeldata.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    display_rows = {int.from_bytes(r[:4], "little"): r for r in displays.records}
    model_rows = {int.from_bytes(r[:4], "little"): r for r in models.records}
    for display_id in CANDIDATES:
        row = display_rows.get(display_id)
        if row is None:
            print(f"{display_id}: not in client CreatureDisplayInfo")
            continue
        model_id = int.from_bytes(row[4:8], "little")
        model = model_rows.get(model_id)
        path = (
            cstring(models.strings, int.from_bytes(model[8:12], "little")) if model else "<no model>"
        )
        print(f"{display_id}: model={model_id} path={path}")


if __name__ == "__main__":
    main()
