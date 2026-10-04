"""Check the SoundID referenced by the custom race model rows."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import RawWdbc  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
MODEL_SOUNDS = {49: 49, 4896: 3111, 4898: 3113, 112885: 6278, 112929: 4012}


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        sounds = RawWdbc(storm.read(handle, names["dbfilesclient\\soundentries.dbc"]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    ids = {int.from_bytes(r[:4], "little") for r in sounds.records}
    print(f"SoundEntries rows: {len(ids)} max={max(ids)}")
    for model_id, sound_id in MODEL_SOUNDS.items():
        print(f"model {model_id}: soundId={sound_id} -> {'ok' if sound_id in ids else 'MISSING'}")


if __name__ == "__main__":
    main()
