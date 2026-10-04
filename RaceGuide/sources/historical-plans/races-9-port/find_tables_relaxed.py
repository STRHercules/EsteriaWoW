"""Find attachment tables whose ids are consecutive but do not start at 0."""
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
    "pandaren": "character\\pandaren\\male\\pandarenmale.m2",
    "broken": "character\\esteriabroken\\male\\brokenmale.m2",
    "eredar": "character\\eredar\\male\\eredarmale.m2",
    "vulpera": "character\\vulpera\\male\\vulperamale.m2",
}
STRIDE = 0x28


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


def find_tables(payload: bytes, minimum: int = 12):
    hits = []
    for offset in range(0, len(payload) - STRIDE * minimum, 4):
        first = struct.unpack_from("<I", payload, offset)[0]
        if first > 3:
            continue
        run = 1
        for index in range(1, 40):
            here = offset + index * STRIDE
            if here + STRIDE > len(payload):
                break
            if struct.unpack_from("<I", payload, here)[0] != first + index:
                break
            run += 1
        if run >= minimum:
            hits.append((offset, first, run))
    return hits


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in MODELS.items():
        source, payload = load(storm, key)
        if payload is None:
            print(f"{label}: missing")
            continue
        bone_count, bone_offset = struct.unpack_from("<II", payload, 0x2C)
        head_bone = None
        head_pivot = None
        for index in range(bone_count):
            record = bone_offset + index * 0x58
            if struct.unpack_from("<i", payload, record)[0] == 6:
                head_bone = index
                head_pivot = struct.unpack_from("<3f", payload, record + 0x4C)
        print(f"== {label} [{source}] head bone {head_bone} at "
              f"({head_pivot[0]:+.3f}, {head_pivot[1]:+.3f}, {head_pivot[2]:+.3f})")
        tables = find_tables(payload)
        print(f"   {len(tables)} consecutive-id candidate table(s)")
        for offset, first, run in tables[:3]:
            print(f"   table @{offset:#08x}: ids {first}..{first + run - 1}")
            for identifier in range(max(first, 9), min(first + run, 14)):
                record = offset + (identifier - first) * STRIDE
                bone = struct.unpack_from("<H", payload, record + 4)[0]
                pivot = struct.unpack_from("<3f", payload, record + 8)
                print(f"      id {identifier:>2} bone {bone:>4} pivot=({pivot[0]:+.3f}, "
                      f"{pivot[1]:+.3f}, {pivot[2]:+.3f})")


if __name__ == "__main__":
    main()
