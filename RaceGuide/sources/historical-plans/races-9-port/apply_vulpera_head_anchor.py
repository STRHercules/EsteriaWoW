"""Bake the corrected head anchor into the Vulpera models and keep a small calibration ring.

The client reads attachment 11 from the array at header slot 0xF0 (43 records at 0x674c36
for the male).  This rewrites that record's pivot to the position computed from the model's
own skull geometry, so every Vulpera helmet (`_Vu` stem) sits on the head instead of ~0.2
above it, then re-stages the seven calibration stems with only the *deltas* around that
value so a refinement can still be picked in one session.

Usage:
    python apply_vulpera_head_anchor.py --dry-run
    python apply_vulpera_head_anchor.py
"""

from __future__ import annotations

import argparse
import ctypes
import datetime
import shutil
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
PATCH_Y = CLIENT / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Backups"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
HEAD = "Item\\ObjectComponents\\Head\\"
BASE_STEM = "Helm_Leather_B_06"
PREFIX = "Vu"
MODELS = {"M": "character\\vulpera\\male\\vulperamale.m2",
          "F": "character\\vulpera\\female\\vulperafemale.m2"}
STRIDE = 48
ATTACHMENT_STRIDE = 0x28
ATTACHMENT_SLOT = 0xF0
ATTACHMENT_ID = 11
BONE_SIZE = 0x58
HEAD_KEY_BONE = 6
# variant -> delta from the freshly computed anchor (dx = backwards, dz = up)
VARIANTS = {
    "A": (0.00, 0.00),
    "B": (0.00, -0.10),
    "C": (0.00, 0.10),
    "D": (0.09, 0.00),
    "E": (-0.09, 0.00),
    "F": (0.09, -0.10),
    "G": (-0.09, -0.10),
}


def open_archives(storm: Storm):
    handles = []
    for name in ORDER:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            handles.append((name, handle))
    return handles


def read(storm: Storm, handles, key: str):
    for name, handle in reversed(handles):
        try:
            return name, storm.read(handle, key)
        except Exception:
            continue
    return None, None


def head_bone_set(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    parents = []
    head = None
    for index in range(count):
        record = offset + index * BONE_SIZE
        if struct.unpack_from("<i", payload, record)[0] == HEAD_KEY_BONE:
            head = index
        parents.append(struct.unpack_from("<h", payload, record + 8)[0])
    members = {head}
    for index in range(count):
        walker = index
        for _step in range(32):
            walker = parents[walker] if 0 <= walker < count else -1
            if walker < 0:
                break
            if walker in members:
                members.add(index)
                break
    return members


def head_pivot_z(payload: bytes) -> float:
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    for index in range(count):
        record = offset + index * BONE_SIZE
        if struct.unpack_from("<i", payload, record)[0] == HEAD_KEY_BONE:
            return struct.unpack_from("<3f", payload, record + 0x4C)[2]
    raise SystemExit("no head key bone")


def skull_box(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    bones = head_bone_set(payload)
    ceiling = head_pivot_z(payload) + 0.30
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for index in range(count):
        record = offset + index * STRIDE
        point = struct.unpack_from("<3f", payload, record)
        weights = payload[record + 12:record + 16]
        indices = payload[record + 16:record + 20]
        if any(abs(value) > 100 for value in point) or point[2] > ceiling:
            continue
        best = max(range(4), key=lambda slot: weights[slot])
        if not weights[best] or indices[best] not in bones:
            continue
        for axis in range(3):
            lo[axis] = min(lo[axis], point[axis])
            hi[axis] = max(hi[axis], point[axis])
    return lo, hi


def attachment_record(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, ATTACHMENT_SLOT)
    for index in range(count):
        record = offset + index * ATTACHMENT_STRIDE
        if struct.unpack_from("<I", payload, record)[0] == ATTACHMENT_ID:
            return record
    raise SystemExit("attachment 11 not in the model's real table")


def shifted_vertices(payload: bytes, dx: float, dz: float) -> bytes:
    patched = bytearray(payload)
    count, offset = struct.unpack_from("<II", patched, 0x3C)
    for index in range(count):
        record = offset + index * STRIDE
        x, y, z = struct.unpack_from("<3f", patched, record)
        struct.pack_into("<3f", patched, record, x + dx, y, z + dz)
    return bytes(patched)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handles = open_archives(storm)
    entries: dict[str, bytes] = {}
    try:
        for sex in ("M", "F"):
            model_source, character = read(storm, handles, MODELS[sex])
            _source, helm = read(storm, handles, f"{HEAD}{BASE_STEM}_{PREFIX}{sex}.m2")
            skin = read(storm, handles, f"{HEAD}{BASE_STEM}_{PREFIX}{sex}00.skin")[1]
            if character is None or helm is None or skin is None:
                raise SystemExit(f"missing model data for sex {sex}")

            low, high = skull_box(character)
            helm_low = struct.unpack_from("<3f", helm, 0xA0)
            helm_high = struct.unpack_from("<3f", helm, 0xAC)
            record = attachment_record(character)
            old = struct.unpack_from("<3f", character, record + 8)
            ideal = (
                ((low[0] + high[0]) - (helm_low[0] + helm_high[0])) / 2,
                old[1],
                ((low[2] + high[2]) - (helm_low[2] + helm_high[2])) / 2,
            )
            print(f"sex {sex} [{model_source}]: skull x[{low[0]:+.3f},{high[0]:+.3f}] "
                  f"z[{low[2]:+.3f},{high[2]:+.3f}]")
            print(f"   attachment 11 pivot ({old[0]:+.3f}, {old[1]:+.3f}, {old[2]:+.3f}) -> "
                  f"({ideal[0]:+.3f}, {ideal[1]:+.3f}, {ideal[2]:+.3f})")
            patched = bytearray(character)
            struct.pack_into("<3f", patched, record + 8, *ideal)
            entries[MODELS[sex]] = bytes(patched)

            for label, (ddx, ddz) in VARIANTS.items():
                # the anchor now carries the ideal, so the variants only need the delta
                entries[f"{HEAD}HelmCal{label}_{PREFIX}{sex}.m2"] = shifted_vertices(
                    helm, ddx, ddz)
                entries[f"{HEAD}HelmCal{label}_{PREFIX}{sex}00.skin"] = skin
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-vulpera-anchor-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, entries)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), {len(entries)} entries, "
          f"backup {backup}")


if __name__ == "__main__":
    main()
