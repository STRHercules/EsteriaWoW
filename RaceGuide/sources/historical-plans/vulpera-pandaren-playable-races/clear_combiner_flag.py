"""Clear the M2 texture-combiner flag on the custom race models."""

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
    "character\\vulpera\\male\\vulperamale.m2",
    "character\\vulpera\\female\\vulperafemale.m2",
    "character\\pandaren\\male\\pandarenmale.m2",
    "character\\pandaren\\female\\pandarenfemale.m2",
)
COMBINER_FLAG = 0x8


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
        for wanted in MODELS:
            actual = names[wanted.casefold()]
            data = bytearray(storm.read(handle, actual))
            flags = struct.unpack_from("<I", data, 0x10)[0]
            new_flags = flags & ~COMBINER_FLAG
            struct.pack_into("<I", data, 0x10, new_flags)
            updates[actual] = bytes(data)
            print(f"{wanted.rsplit(chr(92), 1)[-1]}: globalFlags {flags:#x} -> {new_flags:#x}")
    finally:
        storm.dll.SFileCloseArchive(handle)

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    handle = storm.open_archive(staged)
    try:
        staged_names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        for wanted in MODELS:
            data = storm.read(handle, staged_names[wanted.casefold()])
            flags = struct.unpack_from("<I", data, 0x10)[0]
            profiles = struct.unpack_from("<I", data, 0x44)[0]
            print(f"   verify {wanted.rsplit(chr(92), 1)[-1]}: flags={flags:#x} profiles={profiles}")
    finally:
        storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
