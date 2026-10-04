"""Hide the body submeshes that sit entirely at ankle height.

Reads pristine skins from a pre-change archive, restores normal textures, keeps
the arm fix (geosets 802/803) and additionally empties any geoset-0 submesh
whose whole vertical extent is below Z_LIMIT. For the male Vulpera that selects
exactly one submesh (82 triangles); the female has none that qualify.
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
Z_LIMIT = 0.30
ALWAYS_HIDE = {802, 803}
SKINS = [
    B.join(["character", "vulpera", side, "vulpera" + side + prof + ".skin"])
    for side in ("male", "female")
    for prof in ("00", "01", "02", "03")
]


def process(m2: bytes, skin: bytes):
    nv, ov = struct.unpack_from("<II", m2, 0x3C)
    vals = struct.unpack_from("<10I", skin, 4)
    n_idx, ofs_idx, n_tri, ofs_tri = vals[0], vals[1], vals[2], vals[3]
    n_sub, ofs_sub = vals[6], vals[7]
    g2l = struct.unpack_from(f"<{n_idx}H", skin, ofs_idx)
    tri = struct.unpack_from(f"<{n_tri}H", skin, ofs_tri)
    out = bytearray(skin)
    touched = []
    for s in range(n_sub):
        o = ofs_sub + s * 48
        gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", skin, o)
        hide = gid in ALWAYS_HIDE
        if not hide and gid == 0:
            zs = []
            for k in range(i_count):
                vi = g2l[tri[i_start + k]]
                zs.append(struct.unpack_from("<f", m2, ov + vi * 48 + 8)[0])
            if zs and max(zs) < Z_LIMIT:
                hide = True
        if not hide:
            continue
        touched.append((s, gid, v_count, i_count // 3))
        struct.pack_into("<2H", out, o + 4, 0, 0)
        struct.pack_into("<2H", out, o + 8, 0, 0)
    return bytes(out), touched


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--live", type=Path, default=REPO / "3.3.5a - Dev" / "Data" / "Patch-C.MPQ")
    parser.add_argument("--backup-root", type=Path, default=REPO / "3.3.5a - Dev" / "Backups")
    parser.add_argument("--staging", type=Path, default=REPO / "var" / "ankle-test")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.source)
    try:
        names = {n.casefold(): n for n, *_ in storm.list_files(handle)}
        updates = {}
        for want in SKINS:
            key = want.casefold()
            if key not in names:
                print("   skip (absent): %s" % want)
                continue
            side = want.split(B)[2]
            m2key = B.join(["character", "vulpera", side, "vulpera" + side + ".m2"]).casefold()
            m2 = storm.read(handle, names[m2key])
            data = storm.read(handle, names[key])
            updated, touched = process(m2, data)
            updates[names[key]] = updated
            print("   %-26s %s" % (names[key].rsplit(B, 1)[-1],
                  ", ".join("sub%d/g%d v%d t%d" % t for t in touched) or "nothing matched"))
    finally:
        storm.dll.SFileCloseArchive(handle)
        del storm
        gc.collect()
    if not updates:
        raise SystemExit("no skins read")

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
            empty = []
            for s in range(n_sub):
                o = ofs_sub + s * 48
                gid, level, v_start, v_count, i_start, i_count = struct.unpack_from("<6H", d, o)
                if gid in ALWAYS_HIDE and v_count == 0 and i_count == 0:
                    empty.append(gid)
            if len(empty) < 2:
                raise SystemExit("VERIFY FAIL: 802/803 not both empty in %s" % name)
        # confirm the texture palette is NOT flat anymore
        blp = check.read(h2, n2[B.join(["character", "vulpera", "male", "vulperamaleskin00_00.blp"]).casefold()])
        pal = set(blp[148 + i*4: 148 + i*4 + 3] for i in range(256))
        print("verify: arm geosets hidden, palette has %d distinct colours (normal textures restored)" % len(pal))
    finally:
        check.dll.SFileCloseArchive(h2)
        del check
        gc.collect()

    if args.dry_run:
        print("dry run: staged at %s" % staged)
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bk = args.backup_root / ("patch-c-before-ankle-test-" + stamp)
    bk.mkdir(parents=True, exist_ok=True)
    backup = bk / args.live.name
    shutil.copy2(args.live, backup)
    os.replace(staged, args.live)
    shutil.rmtree(staging, ignore_errors=True)
    print("installed %s (%.0f MB); rollback %s" % (args.live, args.live.stat().st_size / 1e6, backup))


if __name__ == "__main__":
    main()
