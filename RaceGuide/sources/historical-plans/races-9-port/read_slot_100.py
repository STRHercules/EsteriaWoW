"""Read the array the Vulpera header points at from slot 0x100 (29 records)."""
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
    for slot in (0xF8, 0x100, 0x108, 0x110, 0x118, 0x120):
        count, offset = struct.unpack_from("<II", payload, slot)
        print(f"slot {slot:#05x}: count={count} offset={offset:#x}")
    count, offset = struct.unpack_from("<II", payload, 0x100)
    print(f"\nrecords at {offset:#x} (stride 0x28):")
    for index in range(count):
        record = offset + index * 0x28
        identifier, bone = struct.unpack_from("<IH", payload, record)
        pivot = struct.unpack_from("<3f", payload, record + 8)
        print(f"   {index:>2}: id={identifier:>4} bone={bone:>4} unknown="
              f"{struct.unpack_from('<H', payload, record + 6)[0]:>5} pivot=({pivot[0]:+.3f}, "
              f"{pivot[1]:+.3f}, {pivot[2]:+.3f})")


if __name__ == "__main__":
    main()
