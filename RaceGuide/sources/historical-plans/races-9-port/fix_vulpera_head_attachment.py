"""Move the Vulpera's head attachment to the top of the skull.

Every race whose helmets render correctly has `ChrRaces.ClientPrefix` pointing at a
stock model set, and its `Item\\ObjectComponents\\Head` attachment (M2 attachment id 11)
sits *inside* the skull - the human's is 0.18 above its head bone.  The ported Vulpera
model (Patch-5 via Patch-C) instead anchors attachment 11 exactly on its head bone, i.e.
at the neck, so any helm lands low/forward and covers the face.

The model already carries a head-top dummy bone (bone 197, pivot -0.119/0.000/1.294) that
marks where the skull ends.  This rewrites the attachment's pivot to that point, in every
attachment table the model contains (the file has several identical copies), and stages the
patched model into `Patch-Y` so `Patch-C` stays untouched.

Usage:
    python fix_vulpera_head_attachment.py --dry-run
    python fix_vulpera_head_attachment.py
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
MODELS = (
    "character\\vulpera\\male\\vulperamale.m2",
    "character\\vulpera\\female\\vulperafemale.m2",
)
HEAD_ATTACHMENT_ID = 11
STRIDE = 0x28
BONE_SIZE = 0x58
HEAD_KEY_BONE = 6  # M2 key bone id for the head


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


def attachment_tables(payload: bytes, minimum: int = 12):
    hits = []
    for offset in range(0, len(payload) - STRIDE * minimum, 4):
        if struct.unpack_from("<I", payload, offset)[0] != 0:
            continue
        run = 1
        for index in range(1, 40):
            here = offset + index * STRIDE
            if here + STRIDE > len(payload):
                break
            if struct.unpack_from("<I", payload, here)[0] != index:
                break
            run += 1
        if run > HEAD_ATTACHMENT_ID:
            hits.append(offset)
    return hits


def bone_record(payload: bytes, index: int):
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    if index >= count:
        return None
    return offset + index * BONE_SIZE


def head_top(payload: bytes):
    """Pivot of the highest bone hanging off the head bone (the top of the skull)."""
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    head_index = None
    for index in range(count):
        record = offset + index * BONE_SIZE
        if struct.unpack_from("<i", payload, record)[0] == HEAD_KEY_BONE:
            head_index = index
    if head_index is None:
        raise SystemExit("model has no head key bone")
    head_pivot = struct.unpack_from("<3f", payload, offset + head_index * BONE_SIZE + 0x4C)
    best = None
    for index in range(count):
        record = offset + index * BONE_SIZE
        parent = struct.unpack_from("<h", payload, record + 8)[0]
        if parent != head_index:
            continue
        pivot = struct.unpack_from("<3f", payload, record + 0x4C)
        if not (head_pivot[2] - 0.05 <= pivot[2] <= head_pivot[2] + 0.35):
            continue
        if best is None or pivot[2] > best[1][2]:
            best = (index, pivot)
    if best is None:
        return head_pivot
    return best[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    handles = open_archives(storm, ORDER)
    entries: dict[str, bytes] = {}
    try:
        for key in MODELS:
            source, payload = read(storm, handles, key)
            if payload is None:
                raise SystemExit(f"{key}: not found")
            patched = bytearray(payload)
            top = head_top(patched)
            tables = attachment_tables(patched)
            print(f"{key} [{source}] {len(patched):,} bytes, {len(tables)} attachment table(s), "
                  f"head-top bone pivot=({top[0]:+.3f}, {top[1]:+.3f}, {top[2]:+.3f})")
            for first in tables:
                for start in range(first, len(patched) - STRIDE, STRIDE):
                    if struct.unpack_from("<I", patched, start)[0] != HEAD_ATTACHMENT_ID:
                        continue
                    old = struct.unpack_from("<3f", patched, start + 8)
                    if not (0.5 < old[2] < 1.5):
                        continue
                    struct.pack_into("<3f", patched, start + 8, *top)
                    print(f"   table @{first:#08x}: attachment 11 pivot "
                          f"({old[0]:+.3f}, {old[1]:+.3f}, {old[2]:+.3f}) -> "
                          f"({top[0]:+.3f}, {top[1]:+.3f}, {top[2]:+.3f})")
                    break
            entries[key] = bytes(patched)
    finally:
        for _name, handle in handles:
            storm.dll.SFileCloseArchive(handle)

    if args.dry_run:
        print("dry run - Patch-Y untouched")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = BACKUP_ROOT / f"patch-y-before-vulpera-head-attachment-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PATCH_Y, backup / "Patch-Y.MPQ")
    storm.replace_archive_entries(PATCH_Y, entries)
    print(f"Patch-Y updated ({PATCH_Y.stat().st_size:,} bytes), backup {backup}")

    handle = H()
    if storm.dll.SFileOpenArchive(str(PATCH_Y), 0, 0x100, ctypes.byref(handle)):
        try:
            for key in MODELS:
                payload = storm.read(handle, key)
                tables = attachment_tables(payload)
                record = tables[0] + HEAD_ATTACHMENT_ID * STRIDE
                pivot = struct.unpack_from("<3f", payload, record + 8)
                print(f"   verify {key.split(chr(92))[-1]}: attachment 11 pivot "
                      f"({pivot[0]:+.3f}, {pivot[1]:+.3f}, {pivot[2]:+.3f})")
        finally:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
