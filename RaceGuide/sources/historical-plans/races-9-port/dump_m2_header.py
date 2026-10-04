"""Print the M2 header array descriptors so the layout can be read off directly."""
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
KEY = "character\\human\\male\\humanmale.m2"


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    payload = None
    for name in ORDER:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                payload = storm.read(handle, KEY)
                print("source:", name)
            except Exception:
                pass
        finally:
            storm.dll.SFileCloseArchive(handle)
        if payload:
            break
    size = len(payload)
    print(f"size={size:,} version={struct.unpack_from('<I', payload, 4)[0]}")
    print("slot  count      offset    count*8   offset+span")
    for slot in range(0x40, 0x180, 8):
        count, offset = struct.unpack_from("<II", payload, slot)
        if count > 200000 or offset > size:
            continue
        print(f"{slot:#06x} {count:>9} {offset:#010x} {count * 8:>9} {offset + count * 8:#010x}")


if __name__ == "__main__":
    main()
