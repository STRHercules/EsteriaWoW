"""Hide specific geosets in the Vulpera skin profiles (test build).

Empties the vertex and index ranges of every submesh belonging to the given
geoset IDs, so the client draws nothing for them. Geoset ID and level are left
intact, and batches are untouched, so nothing else shifts.

Default targets are the armour geosets:
    802, 803  -> group 08, Wristbands / Sleeves
    902, 903  -> group 09, Legs (kneepads / legcuffs)

This is a diagnostic build: with these hidden the Vulpera shows no sleeves or
legcuffs even when armour is equipped.
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
DEFAULT_GEOSETS = (802, 803, 902, 903)
DEFAULT_TARGETS = (
    B.join(["character", "vulpera", "male", "vulperamale00.skin"]),
    B.join(["character", "vulpera", "male", "vulperamale01.skin"]),
    B.join(["character", "vulpera", "male", "vulperamale02.skin"]),
    B.join(["character", "vulpera", "male", "vulperamale03.skin"]),
    B.join(["character", "vulpera", "female", "vulperafemale00.skin"]),
    B.join(["character", "vulpera", "female", "vulperafemale01.skin"]),
    B.join(["character", "vulpera", "female", "vulperafemale02.skin"]),
    B.join(["character", "vulpera", "female", "vulperafemale03.skin"]),
)


def hide(data: bytes, geosets: set) -> tuple:
    out = bytearray(data)
    n_idx, ofs_idx, n_tri, ofs_tri, n_props, ofs_props, n_sub, ofs_sub, n_batch, ofs_batch = struct.unpack_from("<10I", data, 4)
    touched = []
    for s in range(n_sub):
        o = ofs_sub + s * 48
        gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", data, o)
        if gid not in geosets:
            continue
        touched.append((s, gid, v_count, i_count // 3))
        struct.pack_into("<2H", out, o + 4, 0, 0)
        struct.pack_into("<2H", out, o + 8, 0, 0)
    return bytes(out), touched


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", type=Path, default=REPO / "3.3.5a - Dev" / "Data" / "Patch-C.MPQ")
    parser.add_argument("--geosets", type=int, nargs="*", default=list(DEFAULT_GEOSETS))
    parser.add_argument("--targets", nargs="*", default=list(DEFAULT_TARGETS))
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "geoset-hide")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    wanted = set(args.geosets)
    print("geosets to hide: %s" % sorted(wanted))

    staging = args.staging
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    staged = staging / args.live.name
    print("copying live archive (%.0f MB)" % (args.live.stat().st_size / 1e6))
    shutil.copy2(args.live, staged)

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(staged)
    try:
        names = {n.casefold(): n for n, *_ in storm.list_files(handle)}
        updates = {}
        total = 0
        for want in args.targets:
            key = want.casefold()
            if key not in names:
                print("   skip (absent): %s" % want)
                continue
            data = storm.read(handle, names[key])
            updated, touched = hide(data, wanted)
            updates[names[key]] = updated
            total += len(touched)
            leaf = names[key].rsplit(B, 1)[-1]
            detail = ", ".join("sub%d/g%d v%d t%d" % t for t in touched) or "nothing matched"
            print("   %-26s %s" % (leaf, detail))
    finally:
        storm.dll.SFileCloseArchive(handle)
    if not updates:
        raise SystemExit("no target skins found in the archive")
    if total == 0:
        raise SystemExit("no matching submeshes found - wrong geoset ids?")
    print("submeshes emptied: %d across %d skin files" % (total, len(updates)))

    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(staged, updates)
    del storm
    gc.collect()

    # verify
    check = Storm(DLL_DEFAULT)
    h2 = check.open_archive(staged)
    try:
        n2 = {n.casefold(): n for n, *_ in check.list_files(h2)}
        for name in updates:
            d = check.read(h2, n2[name.casefold()])
            n_idx, ofs_idx, n_tri, ofs_tri, n_props, ofs_props, n_sub, ofs_sub, n_batch, ofs_batch = struct.unpack_from("<10I", d, 4)
            left = []
            for s in range(n_sub):
                o = ofs_sub + s * 48
                gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", d, o)
                if gid in wanted and (v_count or i_count):
                    left.append(gid)
            if left:
                raise SystemExit("VERIFY FAIL: %s still has %s" % (name, sorted(set(left))))
        print("verify: all target submeshes are empty in the staged archive")
    finally:
        check.dll.SFileCloseArchive(h2)
        del check
        gc.collect()

    if args.dry_run:
        print("dry run: staged at %s" % staged)
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = args.backup_root / ("patch-c-before-geoset-hide-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / args.live.name
    shutil.copy2(args.live, backup)
    os.replace(staged, args.live)
    shutil.rmtree(staging, ignore_errors=True)
    print("installed %s (%.0f MB); rollback %s" % (args.live, args.live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
