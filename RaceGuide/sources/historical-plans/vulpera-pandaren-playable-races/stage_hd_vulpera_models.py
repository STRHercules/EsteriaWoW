"""Stage the donor Vulpera_HD model set into Patch-C and repoint the model rows.

The donor server ships its working Vulpera as Character\\Vulpera_HD\\... and
points its CreatureModelData there. Our pack referenced the non-HD
character\\vulpera\\... build instead, which carries extra arm geometry that
shows up as wrist cuffs. This adds the HD files to Patch-C and repoints
model rows 112885/112886 to them.
"""

from __future__ import annotations

import argparse
import datetime
import os
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm

B = chr(92)
DONOR_ROOT = Path(r"G:\\Esteria\\RaceWork\\Latest\\patch-p\\Character\\Vulpera_HD")
DATA = REPO / "3.3.5a - Dev" / "Data"
TARGET_ARCHIVES = ("Patch-C.MPQ", "PATCH-X.MPQ")
DBC_ENTRY = B.join(["DBFilesClient", "CreatureModelData.dbc"])

MALE_MODEL_ID = 112885
FEMALE_MODEL_ID = 112886
HD_PATHS = {
    MALE_MODEL_ID: B.join(["Character", "Vulpera_HD", "Male", "VulperaMale.m2"]),
    FEMALE_MODEL_ID: B.join(["Character", "Vulpera_HD", "Female", "VulperaFemale.m2"]),
}


def cstring(pool: bytes, offset: int) -> str:
    if not offset:
        return ""
    end = pool.find(b"\x00", offset)
    return pool[offset:end].decode("ascii", "replace")


def repath_dbc(data: bytes, replacements: dict) -> bytes:
    """Point the given model rows at new paths.

    The existing string block is preserved byte-for-byte and the new paths are
    appended, so every other row keeps its original offset.
    """
    magic, count, fields, rec_size, str_size = struct.unpack_from("<4sIIII", data, 0)
    if magic != b"WDBC":
        raise ValueError("not a WDBC file")
    records_end = 20 + count * rec_size
    if len(data) != records_end + str_size:
        raise ValueError("unexpected WDBC size")

    rows = {}
    for i in range(count):
        rec = 20 + i * rec_size
        rows[struct.unpack_from("<I", data, rec)[0]] = rec
    missing = sorted(set(replacements) - set(rows))
    if missing:
        raise ValueError("model rows absent from table: %s" % missing)

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


def donor_entries() -> dict:
    entries = {}
    for gender in ("Male", "Female"):
        root = DONOR_ROOT / gender
        if not root.is_dir():
            raise SystemExit("donor folder missing: %s" % root)
        for path in sorted(root.iterdir()):
            if path.is_file():
                entries[B.join(["Character", "Vulpera_HD", gender, path.name])] = path.read_bytes()
    return entries


def verify(archive: Path, expect_paths: dict) -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        for path in expect_paths.values():
            if path.casefold() not in names:
                raise SystemExit("VERIFY FAIL: %s missing from staged archive" % path)
        table = storm.read(handle, DBC_ENTRY)
        _, count, fields, rec_size, _ = struct.unpack_from("<4sIIII", table, 0)
        base = 20 + count * rec_size
        strings = table[base:]
        found = {}
        for i in range(count):
            rec = 20 + i * rec_size
            row_id = struct.unpack_from("<I", table, rec)[0]
            if row_id in expect_paths:
                off = struct.unpack_from("<I", table, rec + 8)[0]
                found[row_id] = cstring(strings, off)
        for row_id, path in expect_paths.items():
            if found.get(row_id) != path:
                raise SystemExit("VERIFY FAIL: row %s -> %r, expected %r" % (row_id, found.get(row_id), path))
    finally:
        storm.dll.SFileCloseArchive(handle)
    print("verify: HD model files present and both model rows repointed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--archives", nargs="*", default=list(TARGET_ARCHIVES))
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "vulpera-hd-stage")
    parser.add_argument("--skip-models", action="store_true",
                        help="only repoint DBC rows; do not add model files")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not DONOR_ROOT.is_dir():
        raise SystemExit("donor root missing: %s" % DONOR_ROOT)
    entries = {} if args.skip_models else donor_entries()
    if entries:
        total = sum(len(v) for v in entries.values())
        print("donor files to stage: %d (%.0f MB)" % (len(entries), total / 1e6))

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    storm = Storm(DLL_DEFAULT)

    for name in args.archives:
        live = args.data_dir / name
        if not live.exists():
            print("skip %s: not found" % name)
            continue
        staging = args.staging / name
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        staged = staging / name
        print("=== %s: copying to staging (%.0f MB)" % (name, live.stat().st_size / 1e6))
        shutil.copy2(live, staged)

        handle = storm.open_archive(staged)
        try:
            try:
                table = storm.read(handle, DBC_ENTRY)
            except OSError:
                print("    no %s in this archive, skipping" % DBC_ENTRY)
                shutil.rmtree(staging, ignore_errors=True)
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)

        updated = repath_dbc(table, HD_PATHS)
        payload = dict(entries) if entries else {}
        payload[DBC_ENTRY] = updated
        print("    DBC %d -> %d bytes; writing %d entries" % (len(table), len(updated), len(payload)))
        storm.replace_archive_entries(staged, payload)
        verify(staged, HD_PATHS)

        if args.dry_run:
            print("    dry run: staged at %s" % staged)
            continue

        backup_dir = args.backup_root / ("%s-before-vulpera-hd-%s" % (name.lower().replace(".mpq", ""), stamp))
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / live.name
        print("    backup -> %s" % backup)
        shutil.copy2(live, backup)
        os.replace(staged, live)
        shutil.rmtree(staging, ignore_errors=True)
        print("    installed %s (%.0f MB); rollback at %s" % (live, live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
