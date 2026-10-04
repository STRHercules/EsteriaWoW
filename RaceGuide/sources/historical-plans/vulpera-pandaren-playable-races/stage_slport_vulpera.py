"""Swap in the Shadowlands-to-WOTLK Vulpera port files.

Stages Character\\Vulpera\\{Male,Female}\\* from the port into Patch-C and
PATCH-X at character\\vulpera\\{male,female}\\* (the port already uses the
legacy naming), and points CreatureModelData rows 112885/112886 at the port
models. Files the port does not provide (legacy 01/02/03 skins, extra-*.blp)
are left untouched.
"""

from __future__ import annotations

import argparse
import datetime
import gc
import os
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm

B = chr(92)
PORT = Path(r"G:\\Downloads\\Shadowland-to-WOTLK-port-main\\Character\\Vulpera")
DATA = REPO / "3.3.5a - Dev" / "Data"
TARGET_ARCHIVES = ("Patch-C.MPQ", "PATCH-X.MPQ")
DBC_ENTRY = B.join(["DBFilesClient", "CreatureModelData.dbc"])
MODEL_PATHS = {
    112885: B.join(["character", "vulpera", "male", "vulperamale.m2"]),
    112886: B.join(["character", "vulpera", "female", "vulperafemale.m2"]),
}


def repath_dbc(data: bytes, replacements: dict) -> bytes:
    magic, count, fields, rec_size, str_size = struct.unpack_from("<4sIIII", data, 0)
    if magic != b"WDBC":
        raise ValueError("not a WDBC file")
    records_end = 20 + count * rec_size
    rows = {}
    for i in range(count):
        rec = 20 + i * rec_size
        rows[struct.unpack_from("<I", data, rec)[0]] = rec
    missing = sorted(set(replacements) - set(rows))
    if missing:
        raise ValueError("model rows absent: %s" % missing)
    added = bytearray()
    offsets = {}
    for path in replacements.values():
        if path in offsets:
            continue
        offsets[path] = str_size + len(added)
        added.extend(path.encode("ascii"))
        added.append(0)
    out = bytearray(data)
    for row_id, path in replacements.items():
        struct.pack_into("<I", out, rows[row_id] + 8, offsets[path])
    header = struct.pack("<4sIIII", magic, count, fields, rec_size, str_size + len(added))
    return bytes(header + bytes(out[20:records_end]) + bytes(data[records_end:]) + bytes(added))


def port_entries() -> dict:
    entries = {}
    for gender in ("Male", "Female"):
        root = PORT / gender
        if not root.is_dir():
            raise SystemExit("port folder missing: %s" % root)
        for path in sorted(root.iterdir()):
            if not path.is_file():
                continue
            entries[B.join(["character", "vulpera", gender.lower(), path.name])] = path.read_bytes()
    return entries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--archives", nargs="*", default=list(TARGET_ARCHIVES))
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "slport-stage")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = port_entries()
    total = sum(len(v) for v in entries.values())
    print("port files to stage: %d (%.1f MB)" % (len(entries), total / 1e6))

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for name in args.archives:
        live = args.data_dir / name
        if not live.exists():
            print("skip %s" % name); continue
        staging = args.staging / name
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        staged = staging / name
        print("=== %s: copying (%.0f MB)" % (name, live.stat().st_size / 1e6))
        shutil.copy2(live, staged)

        storm = Storm(DLL_DEFAULT)
        handle = storm.open_archive(staged)
        try:
            table = storm.read(handle, DBC_ENTRY)
        finally:
            storm.dll.SFileCloseArchive(handle)
        payload = dict(entries)
        payload[DBC_ENTRY] = repath_dbc(table, MODEL_PATHS)
        storm.replace_archive_entries(staged, payload)
        del storm
        gc.collect()

        check = Storm(DLL_DEFAULT)
        handle = check.open_archive(staged)
        try:
            names = {n.casefold(): n for n, *_ in check.list_files(handle)}
            for key in MODEL_PATHS.values():
                if key.casefold() not in names:
                    raise SystemExit("VERIFY FAIL: %s missing" % key)
            raw = check.read(handle, DBC_ENTRY)
        finally:
            check.dll.SFileCloseArchive(handle)
            del check
            gc.collect()
        magic, count, fields, rec_size, str_size = struct.unpack_from("<4sIIII", raw, 0)
        base = 20 + count * rec_size
        for i in range(count):
            rec = 20 + i * rec_size
            rid = struct.unpack_from("<I", raw, rec)[0]
            if rid in MODEL_PATHS:
                off = struct.unpack_from("<I", raw, rec + 8)[0]
                e = raw.find(bytes([0]), base + off)
                got = raw[base + off:e].decode("ascii", "replace")
                if got != MODEL_PATHS[rid]:
                    raise SystemExit("VERIFY FAIL row %d: %s" % (rid, got))
        print("    verify: port models present, rows 112885/112886 repointed")

        if args.dry_run:
            print("    dry run: staged at %s" % staged)
            continue
        backup_dir = args.backup_root / ("%s-before-slport-%s" % (name.lower().replace(".mpq", ""), stamp))
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / live.name
        shutil.copy2(live, backup)
        os.replace(staged, live)
        shutil.rmtree(staging, ignore_errors=True)
        print("    installed %s (%.0f MB); rollback %s" % (live, live.stat().st_size / 1e6, backup))

if __name__ == "__main__":
    main()
