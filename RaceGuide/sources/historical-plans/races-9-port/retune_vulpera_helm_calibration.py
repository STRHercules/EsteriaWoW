"""Retune the Vulpera helm calibration around the computed ideal anchor.

The Vulpera model's real attachment array lives at header slot 0xF0 (43 records at
0x674c36).  Entry 11 (the head slot) is `bone 195, pivot (-0.001, 0.000, 1.270)`, which
puts the donor Vulpera helm about 0.19 above the skull.  The ideal offset is computed here
from the model itself: skull bounding box (vertices weighted to the head bone and its
descendants) minus the helmet's bounding box, then seven variants spread around it.

Usage:
    python retune_vulpera_helm_calibration.py --dry-run
    python retune_vulpera_helm_calibration.py
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

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
PATCH_Y = CLIENT / "Patch-Y.MPQ"
BACKUP_ROOT = REPO / "3.3.5a - Backups"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
HEAD = "Item\\ObjectComponents\\Head\\"
ITEM_DISPLAY_INFO = "DBFilesClient\\ItemDisplayInfo.dbc"
BASE_STEM = "Helm_Leather_B_06"
# every calibration item gets the same helmet geoset-vis pair, so only the fit differs
VIS_ID = 285
DISPLAY_IDS = (64503, 64429, 65195, 65160, 64427, 61210, 62159)
PREFIX = "Vu"
VULPERA = {"M": "character\\vulpera\\male\\vulperamale.m2",
           "F": "character\\vulpera\\female\\vulperafemale.m2"}
STRIDE = 48
ATTACHMENT_STRIDE = 0x28
BONE_SIZE = 0x58
HEAD_KEY_BONE = 6
# variant -> delta from the computed ideal (dx = backwards, dz = up)
VARIANTS = {
    "A": (0.00, 0.00),
    "B": (0.00, -0.10),
    "C": (0.00, 0.10),
    "D": (0.09, 0.00),
    "E": (-0.09, 0.00),
    "F": (0.09, -0.10),
    "G": (-0.09, -0.10),
}


def open_archives(storm: Storm, names):
    handles = []
    for name in names:
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


def head_bone_set(payload: bytes) -> set[int]:
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
        for _step in range(24):
            walker = parents[walker] if 0 <= walker < count else -1
            if walker < 0:
                break
            if walker in members:
                members.add(index)
                break
    return members


def head_bone_pivot(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    for index in range(count):
        record = offset + index * BONE_SIZE
        if struct.unpack_from("<i", payload, record)[0] == HEAD_KEY_BONE:
            return struct.unpack_from("<3f", payload, record + 0x4C)
    return (0.0, 0.0, 0.0)


def real_anchor(payload: bytes, attachment_id: int = 11):
    count, offset = struct.unpack_from("<II", payload, 0xF0)
    for index in range(count):
        record = offset + index * ATTACHMENT_STRIDE
        if struct.unpack_from("<I", payload, record)[0] == attachment_id:
            return struct.unpack_from("<3f", payload, record + 8)
    raise SystemExit("attachment 11 not found in the model's real table")


def skull_box(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x3C)
    bones = head_bone_set(payload)
    ceiling = head_bone_pivot(payload)[2] + 0.30  # keep the skull, drop the ear tips
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for index in range(count):
        record = offset + index * STRIDE
        point = struct.unpack_from("<3f", payload, record)
        weights = payload[record + 12:record + 16]
        indices = payload[record + 16:record + 20]
        if any(abs(value) > 100 for value in point):
            continue
        best = max(range(4), key=lambda slot: weights[slot])
        if not weights[best] or indices[best] not in bones:
            continue
        if point[2] > ceiling:
            continue
        for axis in range(3):
            lo[axis] = min(lo[axis], point[axis])
            hi[axis] = max(hi[axis], point[axis])
    return lo, hi


def shifted(payload: bytes, dx: float, dz: float) -> bytes:
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
    handles = open_archives(storm, ORDER)
    entries: dict[str, bytes] = {}
    try:
        _source, display_payload = read(storm, handles, ITEM_DISPLAY_INFO)
        display = Wdbc(display_payload)
        for row in display.rows:
            if row[0] in DISPLAY_IDS:
                row[13] = VIS_ID
                row[14] = VIS_ID
        entries[ITEM_DISPLAY_INFO] = (
            struct.pack("<4s4I", b"WDBC", len(display.rows), display.fields,
                        display.record_size, len(display.strings))
            + b"".join(struct.pack(f"<{display.fields}I",
                                   *(value & 0xFFFFFFFF for value in row))
                       for row in display.rows)
            + display.strings)
        print(f"{ITEM_DISPLAY_INFO}: {len(DISPLAY_IDS)} rows normalised to vis {VIS_ID}")
        for sex in ("M", "F"):
            base_key = f"{HEAD}{BASE_STEM}_{PREFIX}{sex}.m2"
            skin_key = f"{HEAD}{BASE_STEM}_{PREFIX}{sex}00.skin"
            _source, model = read(storm, handles, base_key)
            _source, skin = read(storm, handles, skin_key)
            if model is None or skin is None:
                raise SystemExit(f"{base_key}: not found")

            _source, character = read(storm, handles, VULPERA[sex])
            if character is None:
                raise SystemExit(f"{VULPERA[sex]}: not found")
            low, high = skull_box(character)
            print(f"sex {sex}: skull x[{low[0]:+.3f},{high[0]:+.3f}] z[{low[2]:+.3f},{high[2]:+.3f}]")
            helm_low, helm_high = helm_box(model)
            anchor = real_anchor(character)
            print(f"   real attachment 11: ({anchor[0]:+.3f}, {anchor[1]:+.3f}, {anchor[2]:+.3f})")
            ideal_x = ((low[0] + high[0]) - (helm_low[0] + helm_high[0])) / 2 - anchor[0]
            ideal_z = ((low[2] + high[2]) - (helm_low[2] + helm_high[2])) / 2 - anchor[2]
            print(f"   helm x[{helm_low[0]:+.3f},{helm_high[0]:+.3f}] "
                  f"z[{helm_low[2]:+.3f},{helm_high[2]:+.3f}] -> ideal shift "
                  f"(dx {ideal_x:+.3f}, dz {ideal_z:+.3f})")
            for label, (ddx, ddz) in VARIANTS.items():
                key = f"{HEAD}HelmCal{label}_{PREFIX}{sex}.m2"
                entries[key] = shifted(model, ideal_x + ddx, ideal_z + ddz)
                entries[f"{HEAD}HelmCal{label}_{PREFIX}{sex}00.skin"] = skin
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-vulpera-calibration2-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, entries)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), {len(entries)} entries, "
          f"backup {backup}")


def helm_box(payload: bytes):
    return (struct.unpack_from("<3f", payload, 0xA0),
            struct.unpack_from("<3f", payload, 0xAC))


if __name__ == "__main__":
    main()
