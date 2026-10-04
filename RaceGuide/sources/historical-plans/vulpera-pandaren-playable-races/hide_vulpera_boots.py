"""Stage a Vulpera build with the arm sleeves and leg boots geosets hidden.

Reads the skins from a pristine pre-hide archive so this is a clean single
change: sleeves 802/803 (confirmed to be the arm cuffs) plus the boot variants
501-505 (candidates for the remaining leg cuffs). The previously hidden leg
geosets 902/903 are restored by reading from the pristine source.

Geoset IDs, levels, vertex buffers and batches are all left intact; only the
submesh vertex/index ranges are zeroed.
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
HIDE = {802, 803, 501, 502, 503, 504, 505}   # overridden by --geosets
SKINS = [
    B.join(["character", "vulpera", side, "vulpera" + side + prof + ".skin"])
    for side in ("male", "female")
    for prof in ("00", "01", "02", "03")
]


def hide(data: bytes, geosets: set) -> tuple:
    out = bytearray(data)
    vals = struct.unpack_from("<10I", data, 4)
    n_sub, ofs_sub = vals[6], vals[7]
    touched = []
    for s in range(n_sub):
        o = ofs_sub + s * 48
        gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", data, o)
        if gid not in geosets:
            continue
        touched.append((gid, v_count, i_count // 3))
        struct.pack_into("<2H", out, o + 4, 0, 0)
        struct.pack_into("<2H", out, o + 8, 0, 0)
    return bytes(out), touched


def read_skins(archive: Path) -> dict:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(archive)
    try:
        names = {n.casefold(): n for n, *_ in storm.list_files(handle)}
        out = {}
        for want in SKINS:
            key = want.casefold()
            if key in names:
                out[names[key]] = storm.read(handle, names[key])
        return out
    finally:
        storm.dll.SFileCloseArchive(handle)
        del storm
        gc.collect()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True,
                        help="pristine archive to read the skins from")
    parser.add_argument("--live", type=Path, default=REPO / "3.3.5a - Dev" / "Data" / "Patch-C.MPQ")
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "geoset-hide2")
    parser.add_argument("--geosets", type=int, nargs="*", default=None,
                        help="geoset ids to empty; default is the sleeve+boot set")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    global HIDE
    if args.geosets:
        HIDE = set(args.geosets)
    print("hiding geosets: %s" % sorted(HIDE))
    pristine = read_skins(args.source)
    print("read %d skin files from %s" % (len(pristine), args.source.parent.name))
    if len(pristine) != len(SKINS):
        raise SystemExit("expected %d skins, got %d" % (len(SKINS), len(pristine)))

    updates = {}
    for name, data in pristine.items():
        updated, touched = hide(data, HIDE)
        updates[name] = updated
        print("   %-26s %s" % (name.rsplit(B, 1)[-1],
              ", ".join("g%d v%d t%d" % t for t in touched) or "nothing matched"))

    staging = args.staging
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    staged = staging / args.live.name
    print("copying pristine source (%.0f MB)" % (args.source.stat().st_size / 1e6))
    shutil.copy2(args.source, staged)
    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(staged, updates)
    del storm
    gc.collect()

    check = Storm(DLL_DEFAULT)
    h2 = check.open_archive(staged)
    try:
        n2 = {n.casefold(): n for n, *_ in check.list_files(h2)}
        for name in updates:
            d = check.read(h2, n2[name.casefold()])
            vals = struct.unpack_from("<10I", d, 4)
            n_sub, ofs_sub = vals[6], vals[7]
            bad = []
            for s in range(n_sub):
                o = ofs_sub + s * 48
                gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", d, o)
                if gid in HIDE and (v_count or i_count):
                    bad.append(gid)
                if gid in (902, 903) and not (v_count and i_count):
                    bad.append(("902/903 still empty", gid))
            if bad:
                raise SystemExit("VERIFY FAIL %s: %s" % (name, sorted(set(map(str, bad)))))
        print("verify: %s empty, 902/903 present" % sorted(HIDE))
    finally:
        check.dll.SFileCloseArchive(h2)
        del check
        gc.collect()

    if args.dry_run:
        print("dry run: staged at %s" % staged)
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = args.backup_root / ("patch-c-before-geoset-hide2-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / args.live.name
    shutil.copy2(args.live, backup)
    os.replace(staged, args.live)
    shutil.rmtree(staging, ignore_errors=True)
    print("installed %s (%.0f MB); rollback %s" % (args.live, args.live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
