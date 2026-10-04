"""Hide the Vulpera wrist-cuff geoset (1801) by emptying its submeshes.

The Vulpera skin profiles carry a 66-vertex ring at forearm height that the
working races do not have. Zeroing that submesh's vertex/index range removes it
from the draw list without touching buffers, batches or any other geoset.
"""

from __future__ import annotations

import argparse
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402
from playable_race_pack import _stage_archive_updates  # noqa: E402

GEOSET = 1801
KEEP = 1802


def hide(data: bytes) -> tuple[bytes, list[tuple[int, int, int]]]:
    out = bytearray(data)
    nIdx, ofsIdx, numTri, ofsTri, numBones, ofsBones, nsub, ofsSub, nbatch, ofsBatch = struct.unpack_from("<10I", data, 4)
    touched = []
    for s in range(nsub):
        o = ofsSub + s * 48
        gid, level, vstart, vcount, istart, icount = struct.unpack_from("<6H", data, o)
        if gid != GEOSET:
            continue
        touched.append((s, vcount, icount // 3))
        struct.pack_into("<2H", out, o + 4, 0, 0)   # vertexStart, vertexCount
        struct.pack_into("<2H", out, o + 8, 0, 0)   # indexStart, indexCount
    return bytes(out), touched


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(args.patch_c)
    try:
        entries = [name for name, *_ in storm.list_files(handle)]
        targets = sorted(
            name for name in entries
            if name.casefold().startswith("character\\vulpera\\") and name.casefold().endswith(".skin")
        )
        updates = {}
        for name in targets:
            data = storm.read(handle, name)
            updated, touched = hide(data)
            guard_ok = True
            nIdx, ofsIdx, numTri, ofsTri, numBones, ofsBones, nsub, ofsSub, nbatch, ofsBatch = struct.unpack_from("<10I", updated, 4)
            for s in range(nsub):
                o = ofsSub + s * 48
                gid, level, vstart, vcount, istart, icount = struct.unpack_from("<6H", updated, o)
                if gid == KEEP and (vcount == 0 or icount == 0):
                    guard_ok = False
            updates[name] = updated
            print(f"   {name.rsplit(chr(92),1)[-1]:<24} emptied {touched} hands intact={guard_ok}")
        if not updates:
            raise SystemExit("no vulpera skin profiles found")
    finally:
        storm.dll.SFileCloseArchive(handle)

    staging = args.out / "staged"
    if staging.exists():
        shutil.rmtree(staging)
    staged = _stage_archive_updates(staging, args.patch_c, updates)
    print(f"staged archive: {staged} ({staged.stat().st_size} bytes)")

    check = Storm(DLL_DEFAULT)
    handle = check.open_archive(staged)
    try:
        names = {name.casefold(): name for name, *_ in check.list_files(handle)}
        for name in updates:
            data = check.read(handle, names[name.casefold()])
            nIdx, ofsIdx, numTri, ofsTri, numBones, ofsBones, nsub, ofsSub, nbatch, ofsBatch = struct.unpack_from("<10I", data, 4)
            cuff = hand = None
            for s in range(nsub):
                o = ofsSub + s * 48
                gid, level, vstart, vcount, istart, icount = struct.unpack_from("<6H", data, o)
                if gid == GEOSET:
                    cuff = (vcount, icount // 3)
                if gid == KEEP:
                    hand = (vcount, icount // 3)
            print(f"   verify {name.rsplit(chr(92),1)[-1]}: cuff={cuff} hand={hand}")
    finally:
        check.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
