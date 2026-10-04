"""Dump M2 bone records (modern layout) and follow the head attachment's bone chain."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
         "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
         "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
         "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
MODELS = {
    "vulpera": ("character\\vulpera\\male\\vulperamale.m2", 195),
    "pandaren": ("character\\pandaren\\male\\pandarenmale.m2", 157),
    "human": ("character\\human\\male\\humanmale.m2", 115),
}
BONE_SIZE = 0x58


def load(storm: Storm, key: str):
    for name in reversed(ORDER):
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return name, storm.read(handle, key)
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None, None


def bones(payload: bytes):
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    result = []
    for index in range(count):
        record = offset + index * BONE_SIZE
        key_bone, flags = struct.unpack_from("<Ii", payload, record)
        parent, submesh = struct.unpack_from("<hH", payload, record + 8)
        pivot = struct.unpack_from("<3f", payload, record + 0x4C)
        result.append((index, key_bone, flags, parent, submesh, pivot))
    return result


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, (key, head_bone) in MODELS.items():
        source, payload = load(storm, key)
        if payload is None:
            print(f"{label}: missing")
            continue
        table = bones(payload)
        print(f"== {label} [{source}] {len(table)} bones; head attachment bound to {head_bone}")
        chain = []
        current = head_bone
        seen = set()
        while 0 <= current < len(table) and current not in seen:
            seen.add(current)
            entry = table[current]
            chain.append(entry)
            current = entry[3]
        for entry in reversed(chain):
            print(f"   bone {entry[0]:>3} parent {entry[3]:>4} flags {entry[2]:#010x} "
                  f"pivot=({entry[5][0]:+.3f}, {entry[5][1]:+.3f}, {entry[5][2]:+.3f}) "
                  f"keybone {entry[1]}")
        print("   bones with pivot z between 0.8 and 1.3:")
        for entry in table:
            if 0.8 <= entry[5][2] <= 1.3:
                print(f"      bone {entry[0]:>3} parent {entry[3]:>4} flags {entry[2]:#010x} "
                      f"pivot=({entry[5][0]:+.3f}, {entry[5][1]:+.3f}, {entry[5][2]:+.3f})")
        print()


if __name__ == "__main__":
    main()
