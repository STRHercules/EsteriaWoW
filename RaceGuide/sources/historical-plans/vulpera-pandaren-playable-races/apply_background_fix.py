"""Patch the CharacterCreate.lua background fallback into Patch-C."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates, patch_character_create  # noqa: E402


def find_entry(archive: Path, wanted: str) -> str:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        matches = [
            name for name, *_ in storm.list_files(handle) if name.casefold() == wanted.casefold()
        ]
    finally:
        storm.dll.SFileCloseArchive(handle)
    if len(matches) != 1:
        raise ValueError(f"expected one entry for {wanted}, found {matches}")
    return matches[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    name = find_entry(args.patch_c, "interface\\gluexml\\charactercreate.lua")
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        original = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    updated = patch_character_create(original)
    if b"UI_Alliance.m2" not in updated:
        raise ValueError("background fallback missing after patch")
    print(f"CharacterCreate.lua: {len(original)} -> {len(updated)} bytes")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, {name: updated})
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    handle = storm.open_archive(staged)
    try:
        names = {entry.casefold(): entry for entry, *_ in storm.list_files(handle)}
        verify = storm.read(handle, names[name.casefold()])
    finally:
        storm.dll.SFileCloseArchive(handle)
    if verify != updated:
        raise SystemExit("staged entry mismatch")
    print("verified staged CharacterCreate.lua")


if __name__ == "__main__":
    main()
