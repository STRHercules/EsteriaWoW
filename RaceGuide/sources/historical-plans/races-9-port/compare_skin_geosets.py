"""List the geoset indices each model's level-0 .skin declares.

Helmets in WotLK are drawn as character geosets in the 1500+/1900+ range, so a model whose skin
profile has no entries up there cannot show a hood or helm - the client falls back to its
missing-geometry placeholder (the blue/white checker cube).
"""

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
ARCHIVES = ("Patch-Y.MPQ", "PATCH-X.MPQ", "Patch-G.MPQ", "Patch-E.MPQ", "Patch-D.MPQ",
            "Patch-C.MPQ", "PATCH-A.MPQ", "lichking.MPQ", "patch.mpq", "expansion.MPQ", "common.MPQ")
SKINS = {
    "broken_male": r"character\esteriabroken\male\brokenmale00.skin",
    "eredar_male": r"character\eredar\male\eredarmale00.skin",
    "dracthyr_male": r"character\dracthyr\male\dracthyrmale00.skin",
    "vulpera_male": r"character\vulpera\male\vulperamale00.skin",
    "human_male": r"character\human\male\humanmale00.skin",
}


def read(storm: Storm, key: str) -> bytes | None:
    for name in ARCHIVES:
        path = CLIENT / name
        if not path.is_file():
            continue
        handle = H()
        if not storm.dll.SFileOpenArchive(str(path), 0, 0x100, ctypes.byref(handle)):
            continue
        try:
            try:
                return storm.read(handle, key)
            except Exception:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
    return None


def geosets(skin: bytes) -> Counter:
    """Every batch names the geoset it draws; the batch array is described at header 0x24
    (records are 0x18 bytes, geosetIndex is the uint16 at +6)."""
    batch_count, batch_offset = struct.unpack_from("<II", skin, 0x24)
    counter: Counter = Counter()
    for index in range(batch_count):
        geoset = struct.unpack_from("<H", skin, batch_offset + index * 0x18 + 6)[0]
        counter[geoset] += 1
    return counter


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    for label, key in SKINS.items():
        data = read(storm, key)
        if data is None:
            print(f"{label}: skin not found")
            continue
        counter = geosets(data)
        helms = sorted(geoset for geoset in counter if geoset >= 1500)
        print(f"{label}: {len(counter)} texture units, geosets {sorted(counter)}")
        print(f"    helmet-range geosets (>=1500): {helms}")


if __name__ == "__main__":
    main()
