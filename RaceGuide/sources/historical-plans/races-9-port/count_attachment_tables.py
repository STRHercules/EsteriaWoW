"""Count candidate attachment tables in the Vulpera model (are there several?)."""
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
    print(f"{KEY} [{source}] size={len(payload):,}")
    for stride in (0x24, 0x28, 0x2C, 0x30):
        matches = []
        for offset in range(0, len(payload) - stride * 6, 4):
            if struct.unpack_from("<I", payload, offset)[0] != 0:
                continue
            run = 1
            for index in range(1, 40):
                here = offset + index * stride
                if here + stride > len(payload):
                    break
                if struct.unpack_from("<I", payload, here)[0] != index:
                    break
                run += 1
            if run >= 6:
                matches.append((offset, run))
        print(f"  stride {stride:#x}: {len(matches)} candidate table(s) "
              f"{[f'{offset:#x}({run})' for offset, run in matches[:6]]}")


if __name__ == "__main__":
    main()
