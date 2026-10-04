"""Regenerate the corrected ChrRaces + CharacterCreate.lua and stage an updated Patch-C."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import (  # noqa: E402
    RawWdbc,
    _start_outfit_display_ids,
    _stage_archive_updates,
    merge_direct_dbc,
    merge_dbc_rows_by_id,
    patch_character_create,
)

DONOR_CHR_RACES = Path(
    r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient\ChrRaces.dbc"
)
DONOR_ROOT = Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient")


def find_entry(storm: Storm, archive: Path, wanted: str) -> str:
    handle = storm.open_archive(archive)
    try:
        matches = [name for name, *_ in storm.list_files(handle) if name.casefold() == wanted.casefold()]
    finally:
        storm.dll.SFileCloseArchive(handle)
    if len(matches) != 1:
        raise ValueError(f"expected one archive entry for {wanted}, found {matches}")
    return matches[0]


def read_entry(archive: Path, name: str) -> bytes:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)


def client_file_string(data: bytes, race: int) -> str:
    table = RawWdbc(data)
    row = next(r for r in table.records if int.from_bytes(r[:4], "little") == race)
    for field in (6, 11, 65):
        offset = int.from_bytes(row[field * 4 : field * 4 + 4], "little")
        end = table.strings.find(b"\x00", offset)
        value = table.strings[offset:end] if offset else b""
        if not all(32 <= byte < 127 for byte in value):
            raise ValueError(f"race {race} field {field} is not printable: {value!r}")
    offset = int.from_bytes(row[11 * 4 : 12 * 4], "little")
    end = table.strings.find(b"\x00", offset)
    return table.strings[offset:end].decode("ascii")


def disable_race(data: bytes, race: int) -> bytes:
    """Set the ChrRaces NOT_PLAYABLE bit (0x1); race 26 is out of scope."""
    table = RawWdbc(data)
    records = []
    for record in table.records:
        if int.from_bytes(record[:4], "little") == race:
            values = bytearray(record)
            values[4:8] = (int.from_bytes(values[4:8], "little") | 1).to_bytes(4, "little")
            record = bytes(values)
        records.append(record)
    return table.build(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    chr_name = find_entry(Storm(DLL_DEFAULT), args.patch_c, "dbfilesclient\\chrraces.dbc")
    lua_name = find_entry(Storm(DLL_DEFAULT), args.patch_c, "interface\\gluexml\\charactercreate.lua")
    outfit_name = find_entry(Storm(DLL_DEFAULT), args.patch_c, "dbfilesclient\\charstartoutfit.dbc")
    item_name = find_entry(Storm(DLL_DEFAULT), args.patch_c, "dbfilesclient\\itemdisplayinfo.dbc")

    base = RawWdbc(read_entry(args.patch_c, chr_name))
    donor = RawWdbc(DONOR_CHR_RACES.read_bytes())
    merged = merge_direct_dbc("ChrRaces", base, donor)
    merged = disable_race(merged, 26)
    (args.out / "ChrRaces.dbc").write_bytes(merged)
    for race, expected in ((18, "Pandaren"), (20, "Vulpera")):
        actual = client_file_string(merged, race)
        if actual != expected:
            raise ValueError(f"race {race} ClientFileString {actual!r} != {expected!r}")
        print(f"race {race}: ClientFileString={actual!r} ok")

    lua = patch_character_create(read_entry(args.patch_c, lua_name))
    if b'RACE_ICON_TCOORDS["HUMAN_"' not in lua:
        raise ValueError("icon coordinate fallback missing after patch")
    (args.out / "CharacterCreate.lua").write_bytes(lua)
    print(f"CharacterCreate.lua: {len(lua)} bytes with fallback")

    outfits = RawWdbc(read_entry(args.patch_c, outfit_name))
    display_ids = _start_outfit_display_ids(outfits.records)
    items = merge_dbc_rows_by_id(
        "ItemDisplayInfo",
        RawWdbc(read_entry(args.patch_c, item_name)),
        RawWdbc((DONOR_ROOT / "ItemDisplayInfo.dbc").read_bytes()),
        display_ids,
    )
    (args.out / "ItemDisplayInfo.dbc").write_bytes(items)
    print(f"ItemDisplayInfo: {len(display_ids)} start-outfit display ids merged")

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(
        staging,
        args.patch_c,
        {chr_name: merged, lua_name: lua, item_name: items},
    )
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    check = Storm(DLL_DEFAULT)
    handle = check.open_archive(staged)
    try:
        verify_chr = check.read(handle, chr_name)
        verify_lua = check.read(handle, lua_name)
        verify_items = check.read(handle, item_name)
    finally:
        check.dll.SFileCloseArchive(handle)
    if verify_chr != merged or verify_lua != lua or verify_items != items:
        raise ValueError("staged archive entries do not match the intended bytes")
    print(f"verified staged entries: race18={client_file_string(verify_chr, 18)} "
          f"race20={client_file_string(verify_chr, 20)}")


if __name__ == "__main__":
    main()
