"""Dump the header of character .skin files (old WotLK layout)."""
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
SKINS = [
    "character\\human\\male\\humanmale00.skin",
    "character\\vulpera\\male\\vulperamale00.skin",
    "character\\esteriabroken\\male\\brokenmale00.skin",
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
    for key in SKINS:
        source, payload = load(storm, key)
        if payload is None:
            print(f"{key}: missing")
            continue
        header = struct.unpack_from("<12I", payload, 0)
        print(f"== {key} [{source}] size={len(payload):,}")
        print("   header: " + " ".join(f"{value:#x}" for value in header))
        batch_count, batch_offset = struct.unpack_from("<II", payload, 0x24)
        print(f"   batches: count={batch_count} offset={batch_offset:#x}")
        for index in range(min(batch_count, 24)):
            record = batch_offset + index * 0x18
            values = struct.unpack_from("<6I", payload, record)
            unit, geoset, mesh, submesh = struct.unpack_from("<HHHH", payload, record)
            print(f"     batch {index:>3}: bytes={values} (unit={unit} geoset={geoset} "
                  f"mesh={mesh} submesh={submesh})")


if __name__ == "__main__":
    main()
