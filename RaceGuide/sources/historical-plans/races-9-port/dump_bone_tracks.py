"""Decode the head attachment's bone tracks (translation/rotation/scale)."""
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
KEY = "character\\vulpera\\male\\vulperamale.m2"
BONE_SIZE = 0x58
BONES = (56, 195)


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


def track(payload: bytes, offset: int, label: str, components: int) -> None:
    interp, global_seq = struct.unpack_from("<HH", payload, offset)
    stamps_count, stamps_offset = struct.unpack_from("<II", payload, offset + 4)
    values_count, values_offset = struct.unpack_from("<II", payload, offset + 12)
    print(f"      {label}: interp={interp} globalSeq={global_seq} "
          f"stamps=({stamps_count}, {stamps_offset:#x}) values=({values_count}, {values_offset:#x})")
    if not values_count or not values_offset:
        return
    inner_count, inner_offset = struct.unpack_from("<II", payload, values_offset)
    print(f"         inner values: count={inner_count} offset={inner_offset:#x}")
    for index in range(min(inner_count, 4)):
        here = inner_offset + index * 4 * components
        if here + 4 * components > len(payload):
            break
        data = struct.unpack_from(f"<{components}f", payload, here)
        print(f"            key {index}: " + ", ".join(f"{value:+.4f}" for value in data))


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    source, payload = load(storm, KEY)
    print(f"[{source}] {KEY}")
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    print(f"bones: {count} at {offset:#x}")
    for index in BONES:
        record = offset + index * BONE_SIZE
        key_bone, flags = struct.unpack_from("<Ii", payload, record)
        parent = struct.unpack_from("<h", payload, record + 8)[0]
        pivot = struct.unpack_from("<3f", payload, record + 0x4C)
        print(f"== bone {index}: keyBone={key_bone} flags={flags:#010x} parent={parent} "
              f"pivot=({pivot[0]:+.3f}, {pivot[1]:+.3f}, {pivot[2]:+.3f})")
        track(payload, record + 0x10, "translation", 3)
        track(payload, record + 0x24, "rotation", 4)
        track(payload, record + 0x38, "scale", 3)


if __name__ == "__main__":
    main()
