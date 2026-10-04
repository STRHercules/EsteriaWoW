"""Which bone index carries the Head key bone, and how do the head attachments sit?"""
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
    "human": "character\\human\\male\\humanmale.m2",
    "gnome": "character\\gnome\\male\\gnomemale.m2",
    "vulpera": "character\\vulpera\\male\\vulperamale.m2",
    "pandaren": "character\\pandaren\\male\\pandarenmale.m2",
    "eredar": "character\\eredar\\male\\eredarmale.m2",
    "broken": "character\\esteriabroken\\male\\brokenmale.m2",
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


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in MODELS.items():
        source, payload = load(storm, key)
        if payload is None:
            print(f"{label}: missing")
            continue
        count, offset = struct.unpack_from("<II", payload, 0x2C)
        head_bone = None
        for index in range(count):
            record = offset + index * BONE_SIZE
            key_bone = struct.unpack_from("<i", payload, record)[0]
            if key_bone == 6:
                pivot = struct.unpack_from("<3f", payload, record + 0x4C)
                head_bone = (index, pivot)
        print(f"== {label} [{source}] bones={count} head keybone -> {head_bone}")


if __name__ == "__main__":
    main()
