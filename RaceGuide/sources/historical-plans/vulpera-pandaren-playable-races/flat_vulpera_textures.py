"""Flat-colour diagnostic for the Vulpera body.

Rewrites the 256-entry palette of every Vulpera body texture so the whole
surface renders in one tone. Pixel indices, mip data, alpha bytes and file size
are all untouched - only the RGB of each palette entry changes.

Purpose: tell paint apart from geometry. A painted colour feature disappears
into a flat surface; a modelled one still shows its silhouette.
"""

from __future__ import annotations

import argparse
import datetime
import gc
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm

B = chr(92)
LIVE = REPO / "3.3.5a - Dev" / "Data" / "Patch-C.MPQ"
PAL_OFFSET = 148
PAL_BYTES = 1024
GREY = 128


def flatten(data: bytes) -> bytes:
    if data[:4] != b"BLP2":
        raise ValueError("not a BLP2")
    if data[8] != 1:
        raise ValueError("not paletted (comp=%d)" % data[8])
    out = bytearray(data)
    for i in range(256):
        o = PAL_OFFSET + i * 4
        alpha = out[o + 3]          # keep the original alpha
        out[o + 0] = GREY           # B
        out[o + 1] = GREY           # G
        out[o + 2] = GREY           # R
        out[o + 3] = alpha
    return bytes(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", type=Path, default=LIVE)
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "flat-test")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

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
        prefix = ("character" + B + "vulpera" + B).casefold()
        targets = []
        for n, *_ in storm.list_files(handle):
            if not n.casefold().startswith(prefix):
                continue
            leaf = n.rsplit(B, 1)[-1].lower()
            if not leaf.endswith(".blp"):
                continue
            if "skin" in leaf or "extra" in leaf:
                targets.append(n)
        print("body textures to flatten: %d" % len(targets))
        updates = {}
        for n in targets:
            updates[n] = flatten(storm.read(handle, n))
    finally:
        storm.dll.SFileCloseArchive(handle)
    if not updates:
        raise SystemExit("no textures matched")

    storm = Storm(DLL_DEFAULT)
    storm.replace_archive_entries(staged, updates)
    del storm
    gc.collect()

    check = Storm(DLL_DEFAULT)
    h2 = check.open_archive(staged)
    try:
        n2 = {n.casefold(): n for n, *_ in check.list_files(h2)}
        sample = sorted(updates)[0]
        d = check.read(h2, n2[sample.casefold()])
        pal = set(d[PAL_OFFSET + i*4: PAL_OFFSET + i*4 + 3] for i in range(256))
        if pal != {bytes([GREY, GREY, GREY])}:
            raise SystemExit("VERIFY FAIL: palette not flat (%d distinct)" % len(pal))
        sizes_ok = all(len(check.read(h2, n2[n.casefold()])) == len(updates[n]) for n in list(updates)[:20])
        if not sizes_ok:
            raise SystemExit("VERIFY FAIL: file size changed")
        print("verify: palettes flat, sizes unchanged (%d textures)" % len(updates))
    finally:
        check.dll.SFileCloseArchive(h2)
        del check
        gc.collect()

    if args.dry_run:
        print("dry run: staged at %s" % staged)
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = args.backup_root / ("patch-c-before-flat-test-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / args.live.name
    shutil.copy2(args.live, backup)
    os.replace(staged, args.live)
    shutil.rmtree(staging, ignore_errors=True)
    print("installed %s (%.0f MB); rollback %s" % (args.live, args.live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
