"""Print the SetBackgroundModel call sites in the live Glue Lua files."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm


ENTRIES = (
    "Interface\\GlueXML\\GlueParent.lua",
    "Interface\\GlueXML\\CharacterSelect.lua",
    "Interface\\GlueXML\\CharacterCreate.lua",
)


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    for archive in (Path(value) for value in sys.argv[1:]):
        handle = storm.open_archive(archive)
        try:
            for entry in ENTRIES:
                try:
                    text = storm.read(handle, entry).decode("utf-8")
                except OSError:
                    continue
                lines = text.splitlines()
                for index, line in enumerate(lines):
                    if "SetBackgroundModel(" in line and "function" not in line:
                        print(f"{archive.name} {Path(entry).name}:{index + 1}")
                        for offset in range(max(0, index - 3), min(len(lines), index + 3)):
                            print(f"   {offset + 1:4d}: {lines[offset].strip()}")
        finally:
            storm.dll.SFileCloseArchive(handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
