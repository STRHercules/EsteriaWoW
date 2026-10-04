"""Apply the Broken background registration and ambience guard to Patch-C."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import (  # noqa: E402
    _stage_archive_updates,
    patch_character_create,
    patch_glue_parent,
)

TARGETS = (
    ("interface\\gluexml\\charactercreate.lua", patch_character_create),
    ("interface\\gluexml\\glueparent.lua", patch_glue_parent),
)


def assert_table_commas(text: str, label: str) -> None:
    """Catch a table entry inserted without the comma before the next entry."""
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        stripped = line.strip()
        if re.fullmatch(r'\["[A-Z_]+"\] = [^,{}\[\]\s]+\s*', stripped) and lines[
            index + 1
        ].strip().startswith("["):
            raise ValueError(f"{label}:{index + 1}: missing trailing comma after {stripped!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        updates = {}
        for wanted, patcher in TARGETS:
            actual = names[wanted]
            original = storm.read(handle, actual)
            updated = patcher(original)
            updates[actual] = updated
            print(f"{actual}: {len(original)} -> {len(updated)} bytes")
    finally:
        storm.dll.SFileCloseArchive(handle)

    glue = updates[names["interface\\gluexml\\glueparent.lua"]].decode("utf-8")
    assert_table_commas(glue, "GlueParent.lua")
    for needle in ('["BROKEN"] = true,', "if ( ambienceTrack ) then"):
        if needle not in glue:
            raise ValueError(f"glue patch missing {needle!r}")
    create = updates[names["interface\\gluexml\\charactercreate.lua"]].decode("utf-8")
    if ".m2" in create.split("SetBackgroundModel")[1][:200]:
        raise ValueError("character create still passes a model path to SetBackgroundModel")
    print("verified: BROKEN registered, ambience guarded, race key passed")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    handle = storm.open_archive(staged)
    try:
        staged_names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        for wanted, _patcher in TARGETS:
            payload = storm.read(handle, staged_names[wanted])
            if payload != updates[staged_names[wanted]]:
                raise SystemExit(f"staged entry mismatch: {wanted}")
    finally:
        storm.dll.SFileCloseArchive(handle)
    print("verified staged glue files")


if __name__ == "__main__":
    main()
