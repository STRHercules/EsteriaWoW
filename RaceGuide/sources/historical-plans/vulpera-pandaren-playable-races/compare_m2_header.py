"""Compare M2 header array counts/offsets between working and crashing models."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = (
    "Data/common.MPQ",
    "Data/patch.MPQ",
    "Data/lichking.MPQ",
    "Data/PATCH-A.MPQ",
    "Data/Patch-C.MPQ",
)
MODELS = {
    "human_male": r"character\human\male\humanmale.m2",
    "goblin_male": r"character\goblin\male\goblinmale.m2",
    "tauren_male": r"character\tauren\male\taurenmale.m2",
    "sethrak_male": r"character\sethrak\male\sethrakmale.m2",
    "broken_male": r"character\esteriabroken\male\brokenmale.m2",
    "vulpera_male": r"character\vulpera\male\vulperamale.m2",
    "pandaren_male": r"character\pandaren\male\pandarenmale.m2",
}
LABELS = (
    (0x14, "globalLoops"),
    (0x1C, "sequences"),
    (0x24, "sequenceLookup"),
    (0x2C, "bones"),
    (0x34, "keyBoneLookup"),
    (0x3C, "vertices"),
    (0x48, "colors"),
    (0x50, "textures"),
    (0x58, "textureWeights"),
    (0x60, "textureTransforms"),
    (0x70, "materials"),
    (0x90, "transparencyLookup"),
    (0x98, "particles"),
    (0xA0, "particles2"),
    (0xA8, "ribbons"),
    (0xB0, "ribbonEmitters"),
)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    pool: dict[str, tuple[str, str]] = {}
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        handle = storm.open_archive(path)
        try:
            for name, *_ in storm.list_files(handle):
                pool.setdefault(name.casefold(), (relative, name))
        finally:
            storm.dll.SFileCloseArchive(handle)

    for label, wanted in MODELS.items():
        entry = pool.get(wanted)
        if entry is None:
            print(f"{label}: missing")
            continue
        handle = storm.open_archive(CLIENT / entry[0])
        try:
            data = storm.read(handle, entry[1])
        finally:
            storm.dll.SFileCloseArchive(handle)
        size = len(data)
        parts = []
        for offset, name in LABELS:
            if offset + 8 > size:
                continue
            count, array_offset = struct.unpack_from("<II", data, offset)
            if count:
                parts.append(f"{name}={count}@{array_offset}")
        print(f"{label} ({size} bytes): " + ", ".join(parts))


if __name__ == "__main__":
    main()
