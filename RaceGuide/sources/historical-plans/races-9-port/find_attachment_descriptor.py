"""Which header slot points at each model's attachment table?"""
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
    "human": ("character\\human\\male\\humanmale.m2", 0x859E0, 23),
    "gnome": ("character\\gnome\\male\\gnomemale.m2", None, 23),
    "vulpera": ("character\\vulpera\\male\\vulperamale.m2", 0x171E20, 23),
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


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, (key, table, count) in MODELS.items():
        source, payload = load(storm, key)
        print(f"== {label} [{source}] expected table {table and hex(table)} count {count}")
        print("   header slots:")
        for slot in range(0x30, 0x160, 8):
            c, o = struct.unpack_from("<II", payload, slot)
            if c or o:
                print(f"     {slot:#05x}: count={c:<6} offset={o:#010x}")
        print()


if __name__ == "__main__":
    main()
