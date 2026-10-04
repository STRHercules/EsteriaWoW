"""Replace the dangling SoundID on the Pandaren model rows with an existing entry."""

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

MODELS = (112929, 112930)
FALLBACK_SOUND = 49


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        model_name = names["dbfilesclient\\creaturemodeldata.dbc"]
        sound_name = names["dbfilesclient\\soundentries.dbc"]
        models = RawWdbc(storm.read(handle, model_name))
        sounds = RawWdbc(storm.read(handle, sound_name))
    finally:
        storm.dll.SFileCloseArchive(handle)

    sound_ids = {int.from_bytes(r[:4], "little") for r in sounds.records}
    records = []
    fixed = 0
    for record in models.records:
        model_id = int.from_bytes(record[:4], "little")
        if model_id in MODELS:
            value = int.from_bytes(record[13 * 4 : 14 * 4], "little")
            if value and value not in sound_ids:
                values = bytearray(record)
                values[13 * 4 : 14 * 4] = FALLBACK_SOUND.to_bytes(4, "little")
                record = bytes(values)
                fixed += 1
                print(f"model {model_id}: soundId {value} -> {FALLBACK_SOUND}")
        records.append(record)
    updated = models.build(records)
    print(f"fixed {fixed} model rows")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, {model_name: updated})
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
