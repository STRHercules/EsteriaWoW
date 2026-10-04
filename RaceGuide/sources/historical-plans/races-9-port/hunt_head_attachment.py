"""Hunt for the head attachment record in models whose table is not id-ordered."""
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
    "broken": "character\\esteriabroken\\male\\brokenmale.m2",
    "eredar": "character\\eredar\\male\\eredarmale.m2",
    "pandaren": "character\\pandaren\\male\\pandarenmale.m2",
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
        bone_count, bone_offset = struct.unpack_from("<II", payload, 0x2C)
        head_bone = None
        head_pivot = None
        for index in range(bone_count):
            record = bone_offset + index * BONE_SIZE
            if struct.unpack_from("<i", payload, record)[0] == 6:
                head_bone = index
                head_pivot = struct.unpack_from("<3f", payload, record + 0x4C)
        print(f"== {label} [{source}] bones={bone_count} headBone={head_bone} "
              f"headPivot=({head_pivot[0]:+.3f}, {head_pivot[1]:+.3f}, {head_pivot[2]:+.3f})")
        hits = []
        for offset in range(0, len(payload) - 0x28, 4):
            if struct.unpack_from("<I", payload, offset)[0] != 11:
                continue
            bone = struct.unpack_from("<H", payload, offset + 4)[0]
            point = struct.unpack_from("<3f", payload, offset + 8)
            if bone >= bone_count or any(abs(value) > 5 for value in point):
                continue
            hits.append((offset, bone, point))
        print(f"   candidate id-11 records: {len(hits)}")
        for offset, bone, point in hits[:12]:
            print(f"      @{offset:#08x} bone {bone:>3} pivot=({point[0]:+.3f}, "
                  f"{point[1]:+.3f}, {point[2]:+.3f})")


if __name__ == "__main__":
    main()
