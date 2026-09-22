"""Read-only check: the live GlueParent.lua defines each race table before using it."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm
from darkfallen_race_pack import check_glue_parent_order


ENTRY = "Interface\\GlueXML\\GlueParent.lua"


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    for archive in (Path(value) for value in sys.argv[1:]):
        handle = storm.open_archive(archive)
        try:
            text = storm.read(handle, ENTRY).decode("utf-8")
        finally:
            storm.dll.SFileCloseArchive(handle)
        check_glue_parent_order(text)
        lines = [
            (index, line.strip())
            for index, line in enumerate(text.splitlines(), 1)
            if "DARKFALLEN" in line
        ]
        print(f"{archive.name}: order OK")
        for index, line in lines:
            print(f"   {index:4d}: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
