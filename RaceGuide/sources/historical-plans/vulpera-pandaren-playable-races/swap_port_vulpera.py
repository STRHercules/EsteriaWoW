"""Swap in the Shadowland-to-WOTLK port's Vulpera model, correctly paired.

The port ships one valid skin per gender (profile 00) plus three `_lod0N.skin`
files whose vertex indices overflow the model. Our own 01/02/03 slots hold
data sized for the outgoing 17,276-vertex mesh, which overflows the port's
15,383-vertex mesh and produced the screen-filling triangles on the last try.

So: write the port M2, write the port's 00 skin into all four profile slots,
carry the animations and textures, and skip the orphan lod skins entirely.
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
GENDERS = {"Male": "male", "Female": "female"}
PROFILES = ("00", "01", "02", "03")


def max_vertex_index(skin: bytes) -> int:
    n_idx, ofs_idx = struct.unpack_from("<II", skin, 4)
    return max(struct.unpack_from("<H", skin, ofs_idx + k * 2)[0] for k in range(n_idx))


def model_vertex_count(m2: bytes) -> int:
    return struct.unpack_from("<II", m2, 0x3C)[0]


def build_entries() -> dict:
    entries = {}
    report = []
    for folder, stem in GENDERS.items():
        root = PORT / folder
        if not root.is_dir():
            raise SystemExit("port folder missing: %s" % root)

        model_key = B.join(["character", "vulpera", stem, "vulpera" + stem + ".m2"])
        skin_name = "vulpera" + stem + "00.skin"
        skin_key = B.join(["character", "vulpera", stem, skin_name])

        model_bytes = (root / ("vulpera" + stem + ".m2")).read_bytes()
        skin_bytes = (root / skin_name).read_bytes()

        entries[model_key] = model_bytes
        verts = model_vertex_count(model_bytes)
        overflow = max_vertex_index(skin_bytes) >= verts
        report.append((stem, "model", len(model_bytes), verts, max_vertex_index(skin_bytes), overflow))

        # one valid skin, written into every profile slot the client may ask for
        for prof in PROFILES:
            key = B.join(["character", "vulpera", stem, "vulpera" + stem + prof + ".skin"])
            entries[key] = skin_bytes

        written = 1 + len(PROFILES)
        skipped = []
        for f in sorted(root.iterdir()):
            if not f.is_file():
                continue
            low = f.name.lower()
            if low.endswith(".lod01.skin") or low.endswith(".lod02.skin") or low.endswith(".lod03.skin") or low.endswith("_lod01.skin") or low.endswith("_lod02.skin") or low.endswith("_lod03.skin"):
                skipped.append(f.name)
                continue
            if f.name.lower() == ("vulpera" + stem + ".m2").lower():
                continue
            if f.name.lower() == skin_name.lower():
                continue
            key = B.join(["character", "vulpera", stem, f.name])
            entries[key] = f.read_bytes()
            written += 1
        report.append((stem, "entries written", written, 0, 0, False))
        report.append((stem, "skipped lod skins", len(skipped), 0, 0, False))
        for s in skipped:
            report.append((stem, "   " + s, 0, 0, 0, False))
    return entries, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DATA)
    parser.add_argument("--archive", default="Patch-C.MPQ")
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "portswap2")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries, report = build_entries()
    print("sanity report (gender, what, size/verts, model verts, skin max idx, overflow):")
    for row in report:
        stem, what, a, verts, mx, bad = row
        if what == "model":
            print("   %-7s %-18s bytes=%d verts=%d skinMaxIdx=%d  %s"
                  % (stem, what, a, verts, mx, "OVERFLOW" if bad else "ok"))
        else:
            print("   %-7s %-18s %d" % (stem, what, a))
    total = sum(len(v) for v in entries.values())
    print("\ntotal entries to write: %d (%.1f MB)" % (len(entries), total / 1e6))
    if any(r[5] for r in report):
        raise SystemExit("refusing to install: a skin overflows its model")

    live = args.data_dir / args.archive
    staging = args.staging / args.archive
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    staged = staging / args.archive
    print("copying %s (%.0f MB)" % (args.archive, live.stat().st_size / 1e6))
    shutil.copy2(live, staged)

    storm = Storm(DLL_DEFAULT)
    print("writing %d entries..." % len(entries))
    storm.replace_archive_entries(staged, entries)
    del storm
    gc.collect()

    # re-verify from the staged archive
    check = Storm(DLL_DEFAULT)
    handle = check.open_archive(staged)
    try:
        names = {n.casefold(): n for n, *_ in check.list_files(handle)}
        for folder, stem in GENDERS.items():
            mk = B.join(["character", "vulpera", stem, "vulpera" + stem + ".m2"]).casefold()
            m2 = check.read(handle, names[mk])
            verts = model_vertex_count(m2)
            print("   staged %s model: %d bytes, %d verts" % (stem, len(m2), verts))
            for prof in PROFILES:
                sk = B.join(["character", "vulpera", stem, "vulpera" + stem + prof + ".skin"]).casefold()
                if sk not in names:
                    raise SystemExit("VERIFY FAIL: missing skin profile %s" % prof)
                blob = check.read(handle, names[sk])
                mx = max_vertex_index(blob)
                status = "ok" if mx < verts else "OVERFLOW"
                print("      profile %s: maxIdx=%d vs %d  %s" % (prof, mx, verts, status))
                if mx >= verts:
                    raise SystemExit("VERIFY FAIL: profile %s overflows" % prof)
    finally:
        check.dll.SFileCloseArchive(handle)
        del check
        gc.collect()

    if args.dry_run:
        print("dry run: staged at %s" % staged)
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = args.backup_root / ("patch-c-before-portswap2-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / live.name
    print("backup -> %s" % backup)
    shutil.copy2(live, backup)
    os.replace(staged, live)
    shutil.rmtree(staging, ignore_errors=True)
    print("installed %s (%.0f MB); rollback %s" % (live, live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
