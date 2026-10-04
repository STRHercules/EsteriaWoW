"""All geoset/skinSection pairs in the Vulpera skins vs a stock race's."""
from __future__ import annotations

import ctypes
import struct
import sys
from collections import Counter
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
    "character\\vulpera\\male\\vulperamale00.skin",
    "character\\vulpera\\male\\vulperamale01.skin",
    "character\\human\\male\\humanmale00.skin",
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
        if payload is None:
            print(f"{key}: missing")
            continue
        header = struct.unpack_from("<12I", payload, 0)
        batch_count, batch_offset = struct.unpack_from("<II", payload, 0x24)
        geosets = Counter()
        sections = []
        for index in range(batch_count):
            record = batch_offset + index * 0x18
            skin_section, geoset = struct.unpack_from("<HH", payload, record + 4)
            geosets[geoset] += 1
            sections.append(skin_section)
        print(f"== {key.split(chr(92))[-1]} [{source}] batches={batch_count}")
        print(f"   header={[hex(value) for value in header]}")
        print(f"   geoset values: {dict(geosets)}")
        print(f"   skinSection range: {min(sections)}..{max(sections)}")


if __name__ == "__main__":
    main()
