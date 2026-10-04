"""Dump the head attachment pivot of each character model.

Attachment records in the v264 M2 are 0x28 bytes:
  +0x00 u32 id, +0x04 u16 bone, +0x06 u16 unk, +0x08 vec3 pivot,
  +0x14 u16 interpolation, u16 globalSequence, +0x18 timestamps, +0x20 values
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
    ("human", "character\\human\\male\\humanmale.m2"),
    ("broken", "character\\esteriabroken\\male\\brokenmale.m2"),
    ("eredar", "character\\eredar\\male\\eredarmale.m2"),
    ("pandaren", "character\\pandaren\\male\\pandarenmale.m2"),
    ("vulpera", "character\\vulpera\\male\\vulperamale.m2"),
]
STRIDE = 0x28
HEAD_IDS = (9, 10, 11, 12)


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


def find_table(payload: bytes):
    size = len(payload)
    best = None
    for offset in range(0x40, min(size - STRIDE * 16, 8_000_000)):
        run = 0
        for index in range(16):
            record = offset + index * STRIDE
            if record + STRIDE > size:
                break
            identifier, bone = struct.unpack_from("<IH", payload, record)
            if identifier > 40 or bone > 2000:
                break
            run += 1
        if run >= 16 and struct.unpack_from("<I", payload, offset)[0] == 0:
            if best is None or run > best[1]:
                best = (offset, run)
    return best


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    ours = open_all(storm, CLIENT, OUR_ORDER)
    donor = open_all(storm, DONOR, DONOR_ORDER)
    try:
        for label, key in MODELS:
            for tag, handles in (("ours", ours), ("donor", donor)):
                source, payload = read(storm, handles, key)
                if payload is None:
                    print(f"{label} [{tag}]: missing")
                    continue
                found = find_table(payload)
                if found is None:
                    print(f"{label} [{tag} <- {source}]: no attachment table found")
                    continue
                offset, run = found
                print(f"{label} [{tag} <- {source}] attachments at {offset:#x} ({run}+ records)")
                for index in range(20):
                    record = offset + index * STRIDE
                    identifier, bone = struct.unpack_from("<IH", payload, record)
                    pivot = struct.unpack_from("<3f", payload, record + 8)
                    print(f"    id {identifier:>2} bone {bone:>4} "
                          f"pivot=({pivot[0]:+.3f}, {pivot[1]:+.3f}, {pivot[2]:+.3f})")
    finally:
        for _name, handle in ours + donor:
            storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
