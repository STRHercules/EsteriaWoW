"""Compare the five attachment tables inside the Vulpera model, and find the header's."""
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
STRIDE = 0x28
TABLES = (0x171e20, 0x2e4230, 0x451b40, 0x5befb0, 0x5bf790)


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
    source, payload = load(storm, KEY)
    print(f"[{source}] size={len(payload):,}")
    for offset in TABLES:
        record = offset + 11 * STRIDE
        identifier, bone = struct.unpack_from("<IH", payload, record)
        pivot = struct.unpack_from("<3f", payload, record + 8)
        print(f"  table {offset:#08x}: id {identifier} bone {bone} "
              f"pivot=({pivot[0]:+.3f}, {pivot[1]:+.3f}, {pivot[2]:+.3f})")
    print("\nheader slots referencing those tables:")
    for slot in range(0x40, 0x200, 8):
        count, offset = struct.unpack_from("<II", payload, slot)
        if offset in TABLES:
            print(f"  slot {slot:#05x}: count={count} offset={offset:#08x}")
    print("\nall descriptor slots with count 20..30:")
    for slot in range(0x40, 0x200, 8):
        count, offset = struct.unpack_from("<II", payload, slot)
        if 20 <= count <= 30 and offset < len(payload):
            print(f"  slot {slot:#05x}: count={count} offset={offset:#08x}")


if __name__ == "__main__":
    main()
