"""Add Eunoia's Kul Tiran head components and fix the client race prefix."""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import os
import re
import shutil
import struct
from collections import Counter
from datetime import datetime
from pathlib import Path

from cars_mount_pack import Storm


READ_ONLY = 0x00000100
REPLACE_EXISTING = 0x80000000
WRITE_FLAGS = 0x00000002
BOOKKEEPING_ENTRIES = {"(listfile)", "(attributes)"}
HEAD_ROOT = "item\\objectcomponents\\head\\"
HEAD_RE = re.compile(r".*_kt(?P<gender>[mf])(?P<variant>\d{0,4}(?:-00)?)\.(?P<ext>m2|skin|anim|phys)$", re.IGNORECASE)
CHR_RACES_PATH = r"DBFilesClient\ChrRaces.dbc"
CHR_RACES_FIELDS = 69
CHR_RACES_RECORD_SIZE = 276
CLIENT_PREFIX_FIELD = 6
CLIENT_FILESTRING_FIELD = 11
KUL_TIRAN_RACE_ID = 29

DEFAULT_TARGET = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-Y.MPQ")
DEFAULT_DONOR = Path(r"G:\Eunoia\Client\data\Patch-6.mpq")
DEFAULT_STORMLIB = Path(
    r"R:\Users\Zach\Downloads\battlemon\Client\wdbx-2.4.1.a-extended-dbc\x64\StormLib.dll"
)


def normalize(name: str) -> str:
    return name.replace("/", "\\").casefold()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_archive(storm: Storm, path: Path, flags: int):
    handle = c.c_void_p()
    if not storm.dll.SFileOpenArchive(str(path), flags, 0, c.byref(handle)):
        raise OSError(f"SFileOpenArchive failed: {path} ({c.get_last_error()})")
    return handle


def close_archive(storm: Storm, handle) -> None:
    if handle:
        storm.dll.SFileCloseArchive(handle)


def archive_files(storm: Storm, path: Path) -> list[tuple[str, int, int, int]]:
    handle = open_archive(storm, path, READ_ONLY)
    try:
        return storm.list_files(handle)
    finally:
        close_archive(storm, handle)


def find_entry(files: list[tuple[str, int, int, int]], wanted: str) -> str:
    wanted_key = normalize(wanted)
    matches = [name for name, *_ in files if normalize(name) == wanted_key]
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one {wanted} entry, found {len(matches)}")
    return matches[0]


def head_entries(files: list[tuple[str, int, int, int]]) -> list[str]:
    selected = []
    for name, *_ in files:
        normalized = normalize(name)
        if not normalized.startswith(HEAD_ROOT):
            continue
        if HEAD_RE.fullmatch(normalized.rsplit("\\", 1)[-1]):
            selected.append(name)
    if len({normalize(name) for name in selected}) != len(selected):
        raise ValueError("duplicate case-insensitive Kul Tiran head entry")
    return sorted(selected, key=normalize)


def validate_head_set(names: list[str]) -> dict[str, int]:
    counts = Counter()
    for name in names:
        match = HEAD_RE.fullmatch(normalize(name).rsplit("\\", 1)[-1])
        if match is None:
            raise ValueError(f"unexpected Kul Tiran head path: {name}")
        counts[f"{match.group('gender').lower()}_{match.group('ext').lower()}"] += 1

    expected = {
        "m_m2": 887,
        "f_m2": 887,
        "m_skin": 888,
        "f_skin": 888,
        "m_anim": 11,
        "f_anim": 11,
        "m_phys": 11,
        "f_phys": 11,
    }
    if counts != expected:
        raise ValueError(f"unexpected Kul Tiran head counts: {dict(counts)}")

    by_ext = Counter()
    by_gender = Counter()
    for key, count in counts.items():
        gender, extension = key.split("_", 1)
        by_ext[extension] += count
        by_gender[gender] += count

    stems = {extension: set() for extension in ("m2", "skin", "anim", "phys")}
    for name in names:
        normalized = normalize(name)
        extension = normalized.rsplit(".", 1)[1]
        stem = normalized.rsplit(".", 1)[0]
        if extension == "skin":
            if not re.search(r"\d{2}$", stem):
                raise ValueError(f"skin does not end in a two-digit variant: {name}")
            stem = stem[:-2]
        stems[extension].add(stem)

    if stems["m2"] != stems["skin"]:
        raise ValueError("Kul Tiran M2 and skin stems do not pair exactly")
    if not stems["phys"] <= stems["m2"]:
        raise ValueError("Kul Tiran physics stem has no M2")
    for name in names:
        normalized = normalize(name)
        if not normalized.endswith(".anim"):
            continue
        stem = normalized.rsplit(".", 1)[0]
        base = re.sub(r"(_kt[fm])\d{4}-00$", r"\1", stem)
        if base not in stems["m2"]:
            raise ValueError(f"Kul Tiran animation stem has no M2: {name}")

    return {
        "total": len(names),
        "m2": by_ext["m2"],
        "skin": by_ext["skin"],
        "anim": by_ext["anim"],
        "phys": by_ext["phys"],
        "male": by_gender["m"],
        "female": by_gender["f"],
    }


def dbc_string(pool: bytes, offset: int) -> str:
    if offset == 0:
        return ""
    if offset >= len(pool):
        raise ValueError(f"DBC string offset outside pool: {offset}")
    end = pool.find(b"\0", offset)
    if end < 0:
        raise ValueError(f"unterminated DBC string at {offset}")
    return pool[offset:end].decode("utf-8")


def find_string(pool: bytes, wanted: bytes) -> int | None:
    cursor = 0
    while cursor < len(pool):
        end = pool.find(b"\0", cursor)
        if end < 0:
            raise ValueError("unterminated DBC string pool")
        if pool[cursor:end] == wanted:
            return cursor
        cursor = end + 1
    return None


def describe_chr_races(data: bytes) -> dict[str, str]:
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data)
    if magic != b"WDBC" or fields != CHR_RACES_FIELDS or record_size != CHR_RACES_RECORD_SIZE:
        raise ValueError("unexpected ChrRaces.dbc layout")
    records_end = 20 + count * record_size
    if len(data) != records_end + string_size:
        raise ValueError("invalid ChrRaces.dbc size")
    pool = data[records_end:]
    rows = [data[20 + index * record_size : 20 + (index + 1) * record_size] for index in range(count)]
    matches = [row for row in rows if struct.unpack_from("<I", row, 0)[0] == KUL_TIRAN_RACE_ID]
    if len(matches) != 1:
        raise ValueError(f"expected one ChrRaces row 29, found {len(matches)}")
    row = matches[0]
    prefix_offset = struct.unpack_from("<I", row, CLIENT_PREFIX_FIELD * 4)[0]
    filestring_offset = struct.unpack_from("<I", row, CLIENT_FILESTRING_FIELD * 4)[0]
    return {
        "client_prefix": dbc_string(pool, prefix_offset),
        "client_filestring": dbc_string(pool, filestring_offset),
    }


def patch_chr_races(data: bytes) -> tuple[bytes, dict[str, str | bool]]:
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data)
    if magic != b"WDBC" or fields != CHR_RACES_FIELDS or record_size != CHR_RACES_RECORD_SIZE:
        raise ValueError("unexpected ChrRaces.dbc layout")
    records_end = 20 + count * record_size
    if len(data) != records_end + string_size:
        raise ValueError("invalid ChrRaces.dbc size")

    records = [
        bytearray(data[20 + index * record_size : 20 + (index + 1) * record_size])
        for index in range(count)
    ]
    pool = bytearray(data[records_end:])
    row_indexes = [
        index
        for index, row in enumerate(records)
        if struct.unpack_from("<I", row, 0)[0] == KUL_TIRAN_RACE_ID
    ]
    if len(row_indexes) != 1:
        raise ValueError(f"expected one ChrRaces row 29, found {len(row_indexes)}")

    row = records[row_indexes[0]]
    prefix_offset = struct.unpack_from("<I", row, CLIENT_PREFIX_FIELD * 4)[0]
    filestring_offset = struct.unpack_from("<I", row, CLIENT_FILESTRING_FIELD * 4)[0]
    before = {
        "client_prefix": dbc_string(pool, prefix_offset),
        "client_filestring": dbc_string(pool, filestring_offset),
    }
    if before["client_filestring"] != "KulTiran":
        raise ValueError(f"row 29 has unexpected ClientFileString: {before['client_filestring']!r}")
    if before["client_prefix"] not in {"Ni", "Kt"}:
        raise ValueError(f"row 29 has unexpected ClientPrefix: {before['client_prefix']!r}")
    if before["client_prefix"] == "Kt":
        return data, {**before, "changed": False}

    kt_offset = find_string(pool, b"Kt")
    if kt_offset is None:
        kt_offset = len(pool)
        pool.extend(b"Kt\0")
    struct.pack_into("<I", row, CLIENT_PREFIX_FIELD * 4, kt_offset)
    output = (
        struct.pack("<4s4I", magic, count, fields, record_size, len(pool))
        + b"".join(bytes(record) for record in records)
        + bytes(pool)
    )
    after = describe_chr_races(output)
    if after != {"client_prefix": "Kt", "client_filestring": "KulTiran"}:
        raise ValueError(f"patched row 29 did not validate: {after}")
    return output, {**before, **after, "changed": True}


def write_entry(storm: Storm, archive, name: str, payload: bytes, replace: bool) -> None:
    handle = c.c_void_p()
    flags = REPLACE_EXISTING if replace else 0
    if not storm.dll.SFileCreateFile(
        archive,
        name.encode("ascii"),
        0,
        len(payload),
        0,
        flags,
        c.byref(handle),
    ):
        raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
    try:
        buffer = c.create_string_buffer(payload or b"\0")
        if not storm.dll.SFileWriteFile(handle, buffer, len(payload), WRITE_FLAGS):
            raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
    finally:
        storm.dll.SFileCloseFile(handle)


def read_and_patch_inputs(storm: Storm, target: Path, donor: Path):
    target_files = archive_files(storm, target)
    donor_files = archive_files(storm, donor)
    target_map = {normalize(name): name for name, *_ in target_files}
    donor_heads = head_entries(donor_files)
    source_counts = validate_head_set(donor_heads)
    target_dbc_name = find_entry(target_files, CHR_RACES_PATH)

    target_handle = open_archive(storm, target, READ_ONLY)
    donor_handle = open_archive(storm, donor, READ_ONLY)
    try:
        dbc_before = storm.read(target_handle, target_dbc_name)
        patched_dbc, dbc_report = patch_chr_races(dbc_before)
        collisions = []
        for donor_name in donor_heads:
            existing_name = target_map.get(normalize(donor_name))
            if existing_name is None:
                continue
            if storm.read(donor_handle, donor_name) != storm.read(target_handle, existing_name):
                raise ValueError(f"existing target entry differs from donor: {donor_name}")
            collisions.append(donor_name)
    finally:
        close_archive(storm, donor_handle)
        close_archive(storm, target_handle)

    return (
        target_files,
        donor_files,
        donor_heads,
        source_counts,
        target_dbc_name,
        dbc_before,
        patched_dbc,
        dbc_report,
        collisions,
    )


def verify_archive(
    storm: Storm,
    path: Path,
    original_files: list[tuple[str, int, int, int]],
    donor_heads: list[str],
    donor: Path,
    target_dbc_name: str,
    expected_dbc: bytes,
) -> dict[str, int]:
    actual_files = archive_files(storm, path)
    original_map = {
        normalize(name): (name, size, compressed, flags)
        for name, size, compressed, flags in original_files
    }
    actual_map = {
        normalize(name): (name, size, compressed, flags)
        for name, size, compressed, flags in actual_files
    }
    if set(original_map) - set(actual_map):
        raise ValueError("modified archive is missing an original entry")
    for key, original in original_map.items():
        if key in {normalize(name) for name in BOOKKEEPING_ENTRIES} or key == normalize(
            target_dbc_name
        ):
            continue
        actual = actual_map[key]
        if original[1:] != actual[1:]:
            raise ValueError(f"unrelated archive metadata changed: {original[0]}")

    target_handle = open_archive(storm, path, READ_ONLY)
    donor_handle = open_archive(storm, donor, READ_ONLY)
    try:
        if storm.read(target_handle, target_dbc_name) != expected_dbc:
            raise ValueError("modified ChrRaces.dbc does not match the verified patch")
        target_names = {normalize(name): name for name, *_ in actual_files}
        for index, donor_name in enumerate(donor_heads, 1):
            target_name = target_names.get(normalize(donor_name))
            if target_name is None:
                raise ValueError(f"modified archive is missing head entry: {donor_name}")
            if storm.read(target_handle, target_name) != storm.read(donor_handle, donor_name):
                raise ValueError(f"packaged head entry differs from donor: {donor_name}")
            if index % 500 == 0:
                print(f"verified {index}/{len(donor_heads)} Kul Tiran head entries")
    finally:
        close_archive(storm, donor_handle)
        close_archive(storm, target_handle)

    row = describe_chr_races(expected_dbc)
    if row != {"client_prefix": "Kt", "client_filestring": "KulTiran"}:
        raise ValueError(f"final ChrRaces row 29 is wrong: {row}")
    return {
        "entry_count": len(actual_files),
        "original_entry_count": len(original_files),
        "verified_head_entries": len(donor_heads),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--donor", type=Path, default=DEFAULT_DONOR)
    parser.add_argument("--stormlib", type=Path, default=DEFAULT_STORMLIB)
    parser.add_argument("--backup-dir", type=Path)
    args = parser.parse_args()

    for path in (args.target, args.donor, args.stormlib):
        if not path.is_file():
            raise FileNotFoundError(path)
    if args.target == args.donor:
        raise ValueError("target and donor must be different archives")

    storm = Storm(args.stormlib)
    (
        target_files,
        _donor_files,
        donor_heads,
        source_counts,
        target_dbc_name,
        dbc_before,
        patched_dbc,
        dbc_report,
        collisions,
    ) = read_and_patch_inputs(storm, args.target, args.donor)
    target_before = describe_chr_races(dbc_before)
    complete = not dbc_report["changed"] and len(collisions) == len(donor_heads)

    if complete:
        verification = verify_archive(
            storm, args.target, target_files, donor_heads, args.donor, target_dbc_name, patched_dbc
        )
        result = {
            "status": "already-complete",
            "target": str(args.target),
            "donor": str(args.donor),
            "before_sha256": sha256(args.target),
            "after_sha256": sha256(args.target),
            "backup": None,
            "backup_sha256": None,
            "dbc": {"path": target_dbc_name, "before": target_before, "after": describe_chr_races(patched_dbc)},
            "head_assets": source_counts,
            "collisions": len(collisions),
            "verification": verification,
        }
        print(json.dumps(result, indent=2))
        return

    before_sha = sha256(args.target)
    backup_dir = args.backup_dir or args.target.parent.parent / "Backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"Patch-Y-before-kultiran-{before_sha[:12]}.MPQ"
    if backup.exists() and sha256(backup) != before_sha:
        raise ValueError(f"existing backup does not match the original target: {backup}")
    if not backup.exists():
        shutil.copy2(args.target, backup)
    if sha256(backup) != before_sha:
        raise ValueError("backup hash does not match the original target")

    temp = args.target.with_name(f"{args.target.name}.kul-tiran.tmp")
    if temp.exists():
        raise FileExistsError(f"refusing to overwrite existing temporary archive: {temp}")
    try:
        shutil.copy2(args.target, temp)
        if sha256(temp) != before_sha:
            raise ValueError("temporary archive copy does not match the original target")

        new_entries = len(donor_heads) - len(collisions)
        target_handle = open_archive(storm, temp, 0)
        donor_handle = open_archive(storm, args.donor, READ_ONLY)
        try:
            storm.ensure_capacity(target_handle, new_entries)
            write_entry(storm, target_handle, target_dbc_name, patched_dbc, replace=True)
            for index, donor_name in enumerate(donor_heads, 1):
                if donor_name in collisions:
                    continue
                write_entry(storm, target_handle, donor_name, storm.read(donor_handle, donor_name), replace=False)
                if index % 500 == 0:
                    print(f"packaged {index}/{len(donor_heads)} Kul Tiran head entries")
        finally:
            close_archive(storm, donor_handle)
            close_archive(storm, target_handle)

        verification = verify_archive(
            storm, temp, target_files, donor_heads, args.donor, target_dbc_name, patched_dbc
        )
        os.replace(temp, args.target)
        final_verification = verify_archive(
            storm, args.target, target_files, donor_heads, args.donor, target_dbc_name, patched_dbc
        )
    finally:
        if temp.exists():
            temp.unlink()

    result = {
        "status": "patched",
        "target": str(args.target),
        "donor": str(args.donor),
        "before_sha256": before_sha,
        "after_sha256": sha256(args.target),
        "backup": str(backup),
        "backup_sha256": sha256(backup),
        "dbc": {"path": target_dbc_name, "before": target_before, "after": describe_chr_races(patched_dbc)},
        "head_assets": source_counts,
        "copied_head_entries": new_entries,
        "collisions": len(collisions),
        "verification_before_swap": verification,
        "verification_after_swap": final_verification,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
