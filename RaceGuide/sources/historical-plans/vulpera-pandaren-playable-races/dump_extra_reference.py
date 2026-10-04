"""Dump the Sethrak extra rows and compare SoundEntries coverage with the donor."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HERE_TOOLS = HERE.parents[2] / "tools"
sys.path.insert(0, str(HERE_TOOLS))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
DONOR_DBC = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")


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
        extras = RawWdbc(storm.read(handle, names["dbfilesclient\\creaturedisplayinfoextra.dbc"]))
        sounds = RawWdbc(storm.read(handle, names["dbfilesclient\\soundentries.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)

    for row in extras.records:
        row_id = int.from_bytes(row[:4], "little")
        if row_id not in (45439, 45440):
            continue
        fields = [int.from_bytes(row[i * 4 : i * 4 + 4], "little") for i in range(21)]
        print(f"extra {row_id}: {fields}")

    ours = {int.from_bytes(r[:4], "little"): r for r in sounds.records}
    donor = RawWdbc((DONOR_DBC / "SoundEntries.dbc").read_bytes())
    donor_rows = {int.from_bytes(r[:4], "little"): r for r in donor.records}
    for sound_id in (4012, 6278, 3111, 3113, 49):
        print(
            f"sound {sound_id}: patch_c={'yes' if sound_id in ours else 'no'} "
            f"donor={'yes' if sound_id in donor_rows else 'no'}"
        )
        row = donor_rows.get(sound_id)
        if row is not None and sound_id not in ours:
            files = [cstring(donor.strings, int.from_bytes(row[(9 + i) * 4 : (10 + i) * 4], "little"))
                     for i in range(10)]
            print(f"     donor files: {[f for f in files if f][:4]}")


if __name__ == "__main__":
    main()
