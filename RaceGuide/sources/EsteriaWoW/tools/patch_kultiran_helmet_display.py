"""Restore the original display-model stem for the Kul Tiran Geistlord helms."""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import struct
import shutil
from pathlib import Path

from cars_mount_pack import DLL_DEFAULT, Storm


REPO = Path(__file__).resolve().parents[1]
PATCH_Y = REPO / "3.3.5a - Dev" / "Data" / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Dev" / "Backups"
DBC_ENTRY = r"DBFilesClient\ItemDisplayInfo.dbc"
MODEL_FIELD = 1
DISPLAY_IDS = {
    64427: "helm_leather_raidrogue_h_01.mdx",
    64429: "helm_leather_raidrogue_h_01.mdx",
}
KUL_TIRAN_HEADS = (
    r"Item\ObjectComponents\Head\helm_leather_raidrogue_h_01_KtM.m2",
    r"Item\ObjectComponents\Head\helm_leather_raidrogue_h_01_KtM00.skin",
    r"Item\ObjectComponents\Head\helm_leather_raidrogue_h_01_KtF.m2",
    r"Item\ObjectComponents\Head\helm_leather_raidrogue_h_01_KtF00.skin",
)
READ_ONLY = 0x00000100


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_read(storm: Storm, path: Path):
    handle = c.c_void_p()
    if not storm.dll.SFileOpenArchive(str(path), 0, READ_ONLY, c.byref(handle)):
        raise OSError(f"SFileOpenArchive failed: {path} ({c.get_last_error()})")
    return handle


def read_string(pool: bytes, offset: int) -> str:
    if offset == 0:
        return ""
    if offset >= len(pool):
        raise ValueError(f"DBC string offset outside pool: {offset}")
    end = pool.find(b"\0", offset)
    if end < 0:
        raise ValueError(f"unterminated DBC string at {offset}")
    return pool[offset:end].decode("utf-8")


def find_string(pool: bytes, value: bytes) -> int | None:
    cursor = 0
    while cursor < len(pool):
        end = pool.find(b"\0", cursor)
        if end < 0:
            raise ValueError("unterminated DBC string pool")
        if pool[cursor:end] == value:
            return cursor
        cursor = end + 1
    return None


def patch_display_models(
    data: bytes,
    replacements: dict[int, str],
) -> tuple[bytes, dict[int, dict[str, str | bool]]]:
    if len(data) < 20:
        raise ValueError("truncated WDBC header")
    magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", data)
    if magic != b"WDBC" or record_size != fields * 4 or MODEL_FIELD >= fields:
        raise ValueError("unsupported ItemDisplayInfo.dbc layout")
    records_end = 20 + count * record_size
    if len(data) != records_end + string_size:
        raise ValueError("invalid ItemDisplayInfo.dbc size")

    rows = [
        bytearray(data[20 + index * record_size : 20 + (index + 1) * record_size])
        for index in range(count)
    ]
    pool = bytearray(data[records_end:])
    report: dict[int, dict[str, str | bool]] = {}
    for display_id, wanted in replacements.items():
        matches = [
            row
            for row in rows
            if struct.unpack_from("<I", row, 0)[0] == display_id
        ]
        if len(matches) != 1:
            raise ValueError(f"expected one display row {display_id}, found {len(matches)}")
        row = matches[0]
        before = read_string(pool, struct.unpack_from("<I", row, MODEL_FIELD * 4)[0])
        if before == wanted:
            report[display_id] = {"before": before, "after": wanted, "changed": False}
            continue
        wanted_bytes = wanted.encode("utf-8")
        offset = find_string(bytes(pool), wanted_bytes)
        if offset is None:
            offset = len(pool)
            pool.extend(wanted_bytes + b"\0")
        struct.pack_into("<I", row, MODEL_FIELD * 4, offset)
        report[display_id] = {"before": before, "after": wanted, "changed": True}

    if not any(bool(item["changed"]) for item in report.values()):
        return data, report
    output = (
        struct.pack("<4s4I", magic, count, fields, record_size, len(pool))
        + b"".join(bytes(row) for row in rows)
        + bytes(pool)
    )
    return output, report


def backup_target(target: Path) -> tuple[Path, str]:
    before = sha256(target)
    backup = BACKUP_ROOT / f"Patch-Y-before-kultiran-display-{before[:12]}.MPQ"
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        if sha256(backup) != before:
            raise ValueError(f"existing backup hash mismatch: {backup}")
    else:
        shutil.copy2(target, backup)
    if sha256(backup) != before:
        raise ValueError("backup hash does not match Patch-Y")
    return backup, before


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--target", type=Path, default=PATCH_Y)
    args = parser.parse_args()
    if not args.target.is_file():
        raise FileNotFoundError(args.target)

    storm = Storm(DLL_DEFAULT)
    handle = open_read(storm, args.target)
    try:
        dbc = storm.read(handle, DBC_ENTRY)
        for name in KUL_TIRAN_HEADS:
            storm.read(handle, name)
    finally:
        storm.dll.SFileCloseArchive(handle)

    patched, report = patch_display_models(dbc, DISPLAY_IDS)
    if args.dry_run:
        print(json.dumps({"status": "dry-run", "dbc": report}, indent=2))
        return
    if patched == dbc:
        print(json.dumps({"status": "already-complete", "dbc": report}, indent=2))
        return

    backup, before = backup_target(args.target)
    storm.replace_archive_entries(args.target, {DBC_ENTRY: patched})

    verify_handle = open_read(storm, args.target)
    try:
        actual = storm.read(verify_handle, DBC_ENTRY)
    finally:
        storm.dll.SFileCloseArchive(verify_handle)
    if actual != patched:
        raise ValueError("post-write ItemDisplayInfo.dbc verification failed")

    print(
        json.dumps(
            {
                "status": "patched",
                "target": str(args.target),
                "backup": str(backup),
                "before_sha256": before,
                "after_sha256": sha256(args.target),
                "dbc": report,
                "verified_kultiran_assets": list(KUL_TIRAN_HEADS),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
