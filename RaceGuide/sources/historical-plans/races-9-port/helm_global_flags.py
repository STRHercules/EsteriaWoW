"""M2 global flags of the helm models we have staged."""
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
CODES = ["Hu", "Gn", "Bk", "Vu", "Pa", "Er", "Nb"]
STEM = "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_"


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
    for code in CODES:
        key = f"{STEM}{code}M.m2"
        source, payload = load(storm, key)
        if payload is None:
            print(f"{code}: missing")
            continue
        version = struct.unpack_from("<I", payload, 4)[0]
        name_count, name_offset = struct.unpack_from("<II", payload, 8)
        flags = struct.unpack_from("<I", payload, 0x10)[0]
        print(f"{code}: [{source}] version={version} nameCount={name_count} "
              f"flags={flags:#010x} size={len(payload):,}")


if __name__ == "__main__":
    main()
