"""Compare external animation file headers between working and custom race models."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev")
ARCHIVES = (
    "Data/PATCH-A.MPQ",
    "Data/Patch-C.MPQ",
    "Data/common.MPQ",
    "Data/patch.MPQ",
    "Data/expansion.MPQ",
    "Data/lichking.MPQ",
)
NEEDLES = (
    "Character\\Human\\Male\\HumanMale0060-00.anim",
    "Character\\Sethrak\\Male\\SethrakMale0060-00.anim",
    "Character\\EsteriaBroken\\Male\\BrokenMale0060-00.anim",
    "character\\vulpera\\male\\vulperamale0060-00.anim",
    "character\\pandaren\\male\\pandarenmale0060-00.anim",
)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    pool: dict[str, tuple[str, str]] = {}
    for relative in ARCHIVES:
        path = CLIENT / relative
        if not path.is_file():
            continue
        try:
            handle = storm.open_archive(path)
        except Exception:  # noqa: BLE001
            continue
        try:
            for name, *_ in storm.list_files(handle):
                pool.setdefault(name.casefold(), (relative, name))
        finally:
            storm.dll.SFileCloseArchive(handle)

    for wanted in NEEDLES:
        entry = pool.get(wanted.casefold())
        if entry is None:
            print(f"{wanted}: not found")
            continue
        handle = storm.open_archive(CLIENT / entry[0])
        try:
            blob = storm.read(handle, entry[1])
        finally:
            storm.dll.SFileCloseArchive(handle)
        print(
            f"{wanted.rsplit(chr(92), 2)[-2] + '/' + wanted.rsplit(chr(92), 1)[-1]}: "
            f"len={len(blob)} head={blob[:20].hex()} ascii={blob[:8]!r}"
        )


if __name__ == "__main__":
    main()
