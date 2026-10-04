"""Set the client's ChrRaces NOT_PLAYABLE flag on race 15 to match the server."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc, _stage_archive_updates  # noqa: E402

SETHRAK = 15


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        name = names["dbfilesclient\\chrraces.dbc"]
        payload = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    table = RawWdbc(payload)
    records = []
    for record in table.records:
        if int.from_bytes(record[:4], "little") == SETHRAK:
            values = bytearray(record)
            values[4:8] = (int.from_bytes(values[4:8], "little") | 1).to_bytes(4, "little")
            record = bytes(values)
        records.append(record)
    updated = table.build(records)

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, {name: updated})
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
