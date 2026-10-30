"""Install the DragonUI spellbook patch that gives cosmetic wings their own tab.

The client's native tab ranges drift (a few wings land in General), so the patched spellbook files
wings by spell id (970200-970999) into a fourth "Cosmetics" category.  Close the game first: the
archive is locked while Wow.exe runs.  Originals are saved under _backups\\dragonui-cosmetic-tab.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
CLIENT = Path(r"G:\3.3.5a - Dev")
ARCHIVE = CLIENT / "Data" / "Patch-ZzzzzDragonUI.MPQ"
SOURCE = REPO / "client-customization" / "DragonUICosmeticTab" / "spellbook"
PREFIX = "Interface\\AddOns\\DragonUI\\modules\\spellbook\\"


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    entries = {PREFIX + path.name: path.read_bytes() for path in sorted(SOURCE.glob("*.lua"))}
    backup = CLIENT / "_backups" / "dragonui-cosmetic-tab"
    backup.mkdir(parents=True, exist_ok=True)
    archive = storm.open_archive(ARCHIVE)
    for name in entries:
        target = backup / name.rsplit("\\", 1)[1]
        if not target.exists():
            target.write_bytes(storm.read(archive, name))
    storm.dll.SFileCloseArchive(archive)
    storm.replace_archive_entries(ARCHIVE, entries)
    archive = storm.open_archive(ARCHIVE)
    for name, payload in entries.items():
        assert storm.read(archive, name) == payload, name
    storm.dll.SFileCloseArchive(archive)
    print("installed", ", ".join(name.rsplit("\\", 1)[1] for name in entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
