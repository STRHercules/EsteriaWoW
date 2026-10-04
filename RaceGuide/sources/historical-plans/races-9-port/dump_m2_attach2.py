"""Locate and dump M2 attachment records (v264) for character models.

M2 header (version 264): magic, version, name[64], then a run of {count, offset}
descriptors.  Attachment records are {u32 id, u16 bone, u16 unk, M2Track position,
u8 animateAttached}; the position track's value array holds the pivot.
"""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
DONOR = Path(r"G:\Eunoia\Client\data")
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
DONOR_ORDER = ["common.mpq", "common-2.mpq", "expansion.mpq", "lichking.mpq", "patch.mpq",
               "patch-2.mpq", "patch-3.mpq", "Patch-4.mpq", "Patch-5.mpq", "Patch-6.mpq",
               "Patch-7.mpq", "Patch-8.mpq", "Patch-9.mpq", "patch-I.mpq", "patch-m.mpq",
               "patch-x.mpq", "patch-y.mpq", "patch-z.mpq"]
MODELS = [
    ("vulpera_male", "character\\vulpera\\male\\vulperamale.m2"),
    ("human_male", "character\\human\\male\\humanmale.m2"),
    ("broken_male", "character\\esteriabroken\\male\\brokenmale.m2"),
    ("eredar_male", "character\\eredar\\male\\eredarmale.m2"),
    ("pandaren_male", "character\\pandaren\\male\\pandarenmale.m2"),
]


def open_all(storm: Storm, root: Path, order):
    handles = []
    for name in order:
        path = root / name
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


def find_attachments(payload: bytes):
    size = len(payload)
    version = struct.unpack_from("<I", payload, 4)[0]
    start = 0x4C if version >= 256 else 0x44
    candidates = []
    for slot in range(start, 0x1A0, 8):
        count, offset = struct.unpack_from("<II", payload, slot)
        if not (1 <= count <= 64) or offset <= 0 or offset + count * 0x20 > size:
            continue
        ids = []
        bones = []
        ok = True
        for index in range(count):
            record = offset + index * 0x20
            identifier, bone = struct.unpack_from("<IH", payload, record)
            if identifier > 32 or bone > 4096:
                ok = False
                break
            ids.append(identifier)
            bones.append(bone)
        if ok and len(set(ids)) == len(ids) and max(ids) >= 6:
            candidates.append((slot, count, offset, ids, bones))
    return candidates


def track_value(payload: bytes, record: int):
    """First vec3 of the attachment's position track."""
    offset = record + 0x08
    interp, global_seq = struct.unpack_from("<HH", payload, offset)
    stamps = struct.unpack_from("<II", payload, offset + 4)
    values = struct.unpack_from("<II", payload, offset + 12)
    if not (1 <= values[0] <= 8) or values[1] + values[0] * 12 > len(payload):
        return None
    point = struct.unpack_from("<3f", payload, values[1])
    return interp, global_seq, stamps, values, point


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = open_all(storm, CLIENT, OUR_ORDER)
    donor = open_all(storm, DONOR, DONOR_ORDER)
    try:
        for label, key in MODELS:
            source, payload = read(storm, ours, key)
            if payload is None:
                print(f"{label}: model not found ({key})")
                continue
            candidates = find_attachments(payload)
            print(f"== {label} [{source}] version={struct.unpack_from('<I', payload, 4)[0]} "
                  f"size={len(payload):,}: {len(candidates)} attachment table candidate(s)")
            for slot, count, offset, ids, bones in candidates:
                print(f"   slot {slot:#x}: {count} attachments at {offset:#x}, ids={ids}")
                for index, identifier in enumerate(ids):
                    record = offset + index * 0x20
                    info = track_value(payload, record)
                    if info is None:
                        print(f"      id {identifier:>2} bone {bones[index]:>3}: track unreadable")
                        continue
                    interp, global_seq, stamps, values, point = info
                    print(f"      id {identifier:>2} bone {bones[index]:>3}: "
                          f"pivot=({point[0]:+.3f}, {point[1]:+.3f}, {point[2]:+.3f}) "
                          f"keys={values[0]}")
    finally:
        for _name, handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
