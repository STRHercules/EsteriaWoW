"""Point the Vulpera model rows back at the non-HD model in Patch-C and PATCH-X.

The donor's Vulpera_HD mesh is a retail-era export. In the 3.3.5a client it
loses the mouth and ear pieces and renders the tail and back of the head black,
while the non-HD build keeps every customization part. Use --to hd to switch
back to the HD paths.
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
DATA = REPO / "3.3.5a - Dev" / "Data"
TARGET_ARCHIVES = ("Patch-C.MPQ", "PATCH-X.MPQ")
DBC_ENTRY = B.join(["DBFilesClient", "CreatureModelData.dbc"])

MODEL_PATHS = {
    "legacy": {
        112885: B.join(["character", "vulpera", "male", "vulperamale.m2"]),
        112886: B.join(["character", "vulpera", "female", "vulperafemale.m2"]),
    },
    "hd": {
        112885: B.join(["Character", "Vulpera_HD", "Male", "VulperaMale.m2"]),
        112886: B.join(["Character", "Vulpera_HD", "Female", "VulperaFemale.m2"]),
    },
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


def read_paths(archive: Path) -> dict:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        raw = storm.read(handle, DBC_ENTRY)
    finally:
        storm.dll.SFileCloseArchive(handle)
        del storm
        gc.collect()
    magic, count, fields, rec_size, str_size = struct.unpack_from("<4sIIII", raw, 0)
    base = 20 + count * rec_size
    out = {}
    for i in range(count):
        rec = 20 + i * rec_size
        rid = struct.unpack_from("<I", raw, rec)[0]
        if rid in (112885, 112886):
            off = struct.unpack_from("<I", raw, rec + 8)[0]
            e = raw.find(b"\x00", base + off)
            out[rid] = raw[base + off:e].decode("ascii", "replace")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--to", choices=sorted(MODEL_PATHS), default="legacy")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--archives", nargs="*", default=list(TARGET_ARCHIVES))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    want = MODEL_PATHS[args.to]
    print("target model rows (%s):" % args.to)
    for k, v in sorted(want.items()):
        print("   %d -> %s" % (k, v))

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for name in args.archives:
        live = args.data_dir / name
        if not live.exists():
            print("skip %s" % name); continue
        staging = REPO / "var" / "vulpera-modelswap" / name
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)
        staged = staging / name
        shutil.copy2(live, staged)

        storm = Storm(DLL_DEFAULT)
        handle = storm.open_archive(staged)
        try:
            table = storm.read(handle, DBC_ENTRY)
        finally:
            storm.dll.SFileCloseArchive(handle)
        updated = repath_dbc(table, want)
        storm.replace_archive_entries(staged, {DBC_ENTRY: updated})
        del storm
        gc.collect()

        now = read_paths(staged)
        if now != want:
            raise SystemExit("VERIFY FAIL %s: %s" % (name, now))
        print("%s: verified %s" % (name, now[112885]))
        if args.dry_run:
            print("   dry run, staged at %s" % staged)
            continue
        backup_dir = REPO / "3.3.5a - Dev" / "Backups" / ("%s-before-model-%s-%s" % (name.lower().replace(".mpq",""), args.to, stamp))
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / live.name
        shutil.copy2(live, backup)
        os.replace(staged, live)
        shutil.rmtree(staging, ignore_errors=True)
        print("   installed; rollback %s" % backup)

if __name__ == "__main__":
    main()
