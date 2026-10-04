"""Restore the Vulpera/Pandaren M2 files to the donor bytes.

The earlier crash hunt cleared the M2 texture-combiner flag (0x8) and forced
four skin profiles on these four models. The crash turned out to be 16-bit
display-id truncation, so those edits were unnecessary and invert the models
away from the donor's known-good rendering (eye/glow layers, LOD skins).
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates  # noqa: E402

MODELS = (
    r"character\vulpera\male\vulperamale.m2",
    r"character\vulpera\female\vulperafemale.m2",
    r"character\pandaren\male\pandarenmale.m2",
    r"character\pandaren\female\pandarenfemale.m2",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--donor", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)

    updates = {}
    for model in MODELS:
        donor_path = args.donor / model
        if not donor_path.is_file():
            raise SystemExit(f"donor model missing: {donor_path}")
        archive_name = names[model.casefold()]
        updates[archive_name] = donor_path.read_bytes()
        print(f"   {model}: {len(updates[archive_name])} bytes -> {archive_name}")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    check = Storm(DLL_DEFAULT)
    handle = check.open_archive(staged)
    try:
        names = {name.casefold(): name for name, *_ in check.list_files(handle)}
        for model in MODELS:
            data = check.read(handle, names[model.casefold()])
            expected = (args.donor / model).read_bytes()
            same = hashlib.sha256(data).hexdigest() == hashlib.sha256(expected).hexdigest()
            print(f"   verified {model}: donor-identical={same}")
            if not same:
                raise SystemExit("restore mismatch")
    finally:
        check.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
