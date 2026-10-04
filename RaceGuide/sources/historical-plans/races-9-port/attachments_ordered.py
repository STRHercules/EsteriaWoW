"""Find the M2 attachment table by its ordered ids and print each pivot."""
from __future__ import annotations

import ctypes
import struct
import sys
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402

CLIENT = REPO / "3.3.5a - Dev/Data"
OUR_ORDER = ["common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ", "patch.MPQ",
             "patch-2.MPQ", "patch-3.MPQ", "patch-4.mpq", "PATCH-A.MPQ", "Patch-B.MPQ",
             "Patch-C.MPQ", "Patch-D.MPQ", "Patch-E.MPQ", "Patch-F.MPQ", "Patch-G.MPQ",
             "Patch-O.mpq", "PATCH-X.MPQ", "Patch-Y.MPQ"]
MODELS = [
    ("human", "character\\human\\male\\humanmale.m2"),
    ("broken", "character\\esteriabroken\\male\\brokenmale.m2"),
    ("eredar", "character\\eredar\\male\\eredarmale.m2"),
    ("pandaren", "character\\pandaren\\male\\pandarenmale.m2"),
    ("vulpera", "character\\vulpera\\male\\vulperamale.m2"),
]
STRIDE = 0x28


def load(storm: Storm, key: str):
    for name in reversed(OUR_ORDER):
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


def find_table(payload: bytes, minimum: int = 10):
    size = len(payload)
    for offset in range(0, size - STRIDE * minimum, 4):
        if struct.unpack_from("<I", payload, offset)[0] != 0:
            continue
        for index in range(1, minimum):
            if struct.unpack_from("<I", payload, offset + index * STRIDE)[0] != index:
                break
        else:
            return offset
    return None


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in MODELS:
        source, payload = load(storm, key)
        if payload is None:
            print(f"{label}: missing")
            continue
        offset = find_table(payload)
        if offset is None:
            print(f"{label} [{source}]: no ordered attachment table")
            continue
        print(f"== {label} [{source}] table at {offset:#x}")
        for index in range(14):
            record = offset + index * STRIDE
            identifier, bone = struct.unpack_from("<IH", payload, record)
            pivot = struct.unpack_from("<3f", payload, record + 8)
            print(f"    id {identifier:>2} bone {bone:>4} "
                  f"pivot=({pivot[0]:+.3f}, {pivot[1]:+.3f}, {pivot[2]:+.3f})")


if __name__ == "__main__":
    main()
