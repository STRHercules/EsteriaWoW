"""Copy the missing starter_barbarian item textures into Patch-C."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates  # noqa: E402

NEEDLE = "starter_barbarian"


def read_matches(archive: Path, needle: str) -> dict[str, bytes]:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        matches = {
            name: storm.read(handle, name)
            for name, *_ in storm.list_files(handle)
            if needle in name.casefold()
        }
    finally:
        storm.dll.SFileCloseArchive(handle)
    return matches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    payloads = read_matches(args.source, NEEDLE)
    if not payloads:
        raise ValueError(f"no {NEEDLE} assets found in {args.source}")
    print(f"source entries: {len(payloads)}")
    for name in sorted(payloads):
        print(f"    {name} ({len(payloads[name])} bytes)")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, payloads)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(staged)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
    finally:
        storm.dll.SFileCloseArchive(handle)
    missing = [name for name in payloads if name.casefold() not in names]
    print(f"missing after staging: {missing}")
    if missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
