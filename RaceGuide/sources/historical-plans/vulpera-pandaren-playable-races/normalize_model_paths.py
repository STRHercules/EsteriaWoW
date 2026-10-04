"""Rewrite CreatureModelData .mdx paths to .m2 when the .m2 file is present."""

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

    name = find_entry(args.patch_c, "dbfilesclient\\CreatureModelData.dbc")
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        entries = {entry.casefold(): entry for entry, *_ in storm.list_files(handle)}
        payload = storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)
    table = RawWdbc(payload)

    strings = bytearray(table.strings)
    rewritten = 0
    records = []
    for record in table.records:
        offset = int.from_bytes(record[8:12], "little")
        if not offset:
            records.append(record)
            continue
        end = strings.find(b"\x00", offset)
        path = bytes(strings[offset:end])
        if path.lower().endswith(b".mdx"):
            candidate = path[:-4] + b".m2"
            if candidate.decode("ascii", "replace").casefold() in entries:
                # Keep the pool length identical: ".mdx\0" -> ".m2\0\0".
                strings[offset : end + 1] = candidate + b"\x00\x00"
                rewritten += 1
        records.append(record)
    if rewritten:
        payload = table.build(records, bytes(strings))
    print(f"CreatureModelData: rewrote {rewritten} .mdx paths to .m2")

    updates = {name: payload}
    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    handle = storm.open_archive(staged)
    try:
        names = {entry.casefold(): entry for entry, *_ in storm.list_files(handle)}
        verify = RawWdbc(storm.read(handle, names[name.casefold()]))
    finally:
        storm.dll.SFileCloseArchive(handle)
    for record in verify.records:
        row_id = int.from_bytes(record[:4], "little")
        if row_id in (4896, 4897, 4898, 4899):
            offset = int.from_bytes(record[8:12], "little")
            end = verify.strings.find(b"\x00", offset)
            print(f"   model {row_id}: {verify.strings[offset:end].decode('ascii', 'replace')}")


if __name__ == "__main__":
    main()
