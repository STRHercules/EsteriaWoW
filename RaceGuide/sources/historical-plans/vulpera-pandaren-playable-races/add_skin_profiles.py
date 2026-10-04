"""Give the custom race models four skin profiles like every working player model."""

from __future__ import annotations

import argparse
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates  # noqa: E402

MODELS = (
    "character\\vulpera\\male\\vulperamale",
    "character\\vulpera\\female\\vulperafemale",
    "character\\pandaren\\male\\pandarenmale",
    "character\\pandaren\\female\\pandarenfemale",
)
PROFILE_COUNT = 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        updates: dict[str, bytes] = {}
        for stem in MODELS:
            model_key = f"{stem}.m2"
            skin_key = f"{stem}00.skin"
            model_name = names.get(model_key)
            skin_name = names.get(skin_key)
            if model_name is None or skin_name is None:
                raise ValueError(f"missing model or skin for {stem}")
            data = bytearray(storm.read(handle, model_name))
            current = struct.unpack_from("<I", data, 0x44)[0]
            struct.pack_into("<I", data, 0x44, PROFILE_COUNT)
            updates[model_name] = bytes(data)
            skin_bytes = storm.read(handle, skin_name)
            added = []
            for index in range(1, PROFILE_COUNT):
                candidate = f"{stem}{index:02d}.skin"
                existing = names.get(candidate.casefold())
                if existing is None:
                    updates[candidate] = skin_bytes
                    added.append(candidate)
            print(
                f"{stem}: nSkinProfiles {current} -> {PROFILE_COUNT}, "
                f"added {[a.rsplit(chr(92), 1)[-1] for a in added]}"
            )
    finally:
        storm.dll.SFileCloseArchive(handle)

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes), {len(updates)} entries")

    handle = storm.open_archive(staged)
    try:
        staged_names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        for stem in MODELS:
            data = storm.read(handle, staged_names[f"{stem}.m2"])
            profiles = struct.unpack_from("<I", data, 0x44)[0]
            skins = sum(
                1
                for key in staged_names
                if key.startswith(stem.casefold()) and key.endswith(".skin")
            )
            print(f"   {stem}: nSkinProfiles={profiles} skin files={skins}")
    finally:
        storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
