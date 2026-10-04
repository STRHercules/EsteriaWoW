"""BLP dimensions for Vulpera vs Pandaren skin/extra textures."""

from __future__ import annotations

import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

LIVE = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\3.3.5a - Dev\Data\Patch-C.MPQ")
WANTED = (
    r"character\vulpera\male\vulperamaleskin00_00.blp",
    r"character\vulpera\male\vulperamaleextra_00_00.blp",
    r"character\vulpera\male\vulperamalefaceupper00_00.blp",
    r"character\pandaren\male\pandamaleskin00_00.blp",
    r"character\pandaren\male\pandamaleskinextra00_00.blp",
)


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    handle = storm.open_archive(LIVE)
    try:
        names = {name.casefold(): name for name, *_ in storm.list_files(handle)}
        for wanted in WANTED:
            actual = names.get(wanted)
            if actual is None:
                print(f"{wanted}: not in Patch-C")
                continue
            data = storm.read(handle, actual)
            magic = data[:4]
            width, height = struct.unpack_from("<II", data, 12)
            size = len(data)
            print(f"{wanted}: magic={magic!r} {width}x{height} bytes={size}")
    finally:
        storm.dll.SFileCloseArchive(handle)


if __name__ == "__main__":
    main()
