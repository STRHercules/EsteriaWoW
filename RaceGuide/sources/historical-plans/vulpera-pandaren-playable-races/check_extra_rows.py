"""Inspect the CreatureDisplayInfoExtra rows referenced by custom race displays."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
DISPLAYS = (60000, 60001, 60002, 60003, 60004, 60005, 60006, 60007)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        displays = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturedisplayinfo.dbc"]))
        extras = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturedisplayinfoextra.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    display_rows = {int.from_bytes(r[:4], "little"): r for r in displays.records}
    extra_rows = {int.from_bytes(r[:4], "little"): r for r in extras.records}
    print(f"extra rows: {len(extra_rows)} max={max(extra_rows)}")
    for display_id in DISPLAYS:
        row = display_rows.get(display_id)
        if row is None:
            print(f"{display_id}: display row absent")
            continue
        extra_id = int.from_bytes(row[12:16], "little")
        extra = extra_rows.get(extra_id)
        if extra is None:
            print(f"{display_id}: extraId={extra_id} -> {'absent' if extra_id else 'none'}")
            continue
        fields = [int.from_bytes(extra[i * 4 : i * 4 + 4], "little") for i in range(21)]
        print(
            f"{display_id}: extraId={extra_id} race={fields[1]} gender={fields[2]} "
            f"skin={fields[3]} face={fields[4]} hair={fields[5]} hairColor={fields[6]} "
            f"facialHair={fields[7]} flags={fields[8]} bald={fields[9]}"
        )


if __name__ == "__main__":
    main()
