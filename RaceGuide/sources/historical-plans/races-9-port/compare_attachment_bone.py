"""Compare the bone that hosts the head attachment in the human against the Vulpera's."""
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
BONE_SIZE = 0x58
CASES = {
    "human": ("character\\human\\male\\humanmale.m2", 115),
    "gnome": ("character\\gnome\\male\\gnomemale.m2", None),
    "vulpera": ("character\\vulpera\\male\\vulperamale.m2", 195),
}


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


def describe(payload: bytes, index: int) -> str:
    count, offset = struct.unpack_from("<II", payload, 0x2C)
    if index >= count:
        return "out of range"
    record = offset + index * BONE_SIZE
    key_bone, flags = struct.unpack_from("<Ii", payload, record)
    parent = struct.unpack_from("<h", payload, record + 8)[0]
    pivot = struct.unpack_from("<3f", payload, record + 0x4C)
    translation = struct.unpack_from("<HHII", payload, record + 0x10)
    rotation = struct.unpack_from("<HHII", payload, record + 0x24)
    return (f"bone {index}: keyBone={key_bone} flags={flags:#010x} parent={parent} "
            f"pivot=({pivot[0]:+.3f}, {pivot[1]:+.3f}, {pivot[2]:+.3f}) "
            f"transKeys={translation[2]} rotKeys={rotation[2]}")


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, (key, index) in CASES.items():
        source, payload = load(storm, key)
        count, offset = struct.unpack_from("<II", payload, 0x2C)
        print(f"== {label} [{source}] bones={count}")
        if index is not None:
            print("  ", describe(payload, index))
        # find keybone 6 and list its children
        head = None
        for candidate in range(count):
            record = offset + candidate * BONE_SIZE
            if struct.unpack_from("<i", payload, record)[0] == 6:
                head = candidate
        print("  ", describe(payload, head) if head is not None else "no head keybone")
        children = []
        for candidate in range(count):
            record = offset + candidate * BONE_SIZE
            if struct.unpack_from("<h", payload, record + 8)[0] == head:
                children.append(candidate)
        print(f"   children of head bone: {children}")
        for child in children:
            print("     ", describe(payload, child))


if __name__ == "__main__":
    main()
