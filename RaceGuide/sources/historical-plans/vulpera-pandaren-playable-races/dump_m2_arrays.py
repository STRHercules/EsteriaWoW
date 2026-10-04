"""Dump every M2 header array (count@offset) for working and crashing models."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = (
    "Data/Patch-C.MPQ",
    "Data/PATCH-A.MPQ",
)
MODELS = {
    "human_male": r"character\human\male\humanmale.m2",
    "sethrak_male": r"character\sethrak\male\sethrakmale.m2",
    "broken_male": r"character\esteriabroken\male\brokenmale.m2",
    "vulpera_male": r"character\vulpera\male\vulperamale.m2",
    "pandaren_male": r"character\pandaren\male\pandarenmale.m2",
}


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    pool: dict[str, tuple[str, str]] = {}
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except OSError:
            continue
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
        print(f"== {label} from {entry[0]} ({len(data)} bytes)")
        for offset in range(0x14, 0x130, 8):
            count, array_offset = struct.unpack_from("<II", data, offset)
            if count and array_offset:
                print(f"   {offset:#05x}: count={count} offset={array_offset}")
        print()


if __name__ == "__main__":
    main()
