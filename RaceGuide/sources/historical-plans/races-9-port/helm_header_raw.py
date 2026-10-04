"""Raw header dump of two helm models."""
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
FILES = [
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_HuM.m2",
    "Item\\ObjectComponents\\Head\\Helm_Leather_B_06_VuM.m2",
]


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
    for key in FILES:
        source, payload = load(storm, key)
        print(f"== {key.split(chr(92))[-1]} [{source}] size={len(payload):,}")
        for offset in range(0, 0x110, 16):
            chunk = payload[offset:offset + 16]
            words = struct.unpack("<4I", chunk)
            floats = "/".join(f"{struct.unpack('<f', struct.pack('<I', w))[0]:.2f}" for w in words)
            print(f"  {offset:#05x}  " + " ".join(f"{w:#010x}" for w in words) + f"   {floats}")
        print("   name:", payload[8:72].split(b"\0")[0])
        print()


if __name__ == "__main__":
    main()
