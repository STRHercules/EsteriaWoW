"""Resolve which MPQ wins for each GlueXML path, using WoW 3.3.5a archive load order."""

from __future__ import annotations

import ctypes as c
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))

from cars_mount_pack import Storm, FindData, DLL_DEFAULT  # noqa: E402

DATA = Path(r"G:\3.3.5a - Dev\Data")
LOCALE = "enUS"

# WoW 3.3.5a load order: later archives override earlier ones.
BASE = ["common.MPQ", "common-2.MPQ", "common-3.MPQ", "expansion.MPQ", "lichking.MPQ"]
LOCALE_BASE = [
    f"{LOCALE}\\locale-{LOCALE}.MPQ",
    f"{LOCALE}\\expansion-locale-{LOCALE}.MPQ",
    f"{LOCALE}\\lichking-locale-{LOCALE}.MPQ",
    f"{LOCALE}\\speech-{LOCALE}.MPQ",
    f"{LOCALE}\\expansion-speech-{LOCALE}.MPQ",
    f"{LOCALE}\\lichking-speech-{LOCALE}.MPQ",
]


def load_order() -> list[str]:
    order = list(BASE) + list(LOCALE_BASE)
    order.append("patch.MPQ")
    order.append(f"{LOCALE}\\patch-{LOCALE}.MPQ")
    for index in "23456789":
        order.append(f"patch-{index}.MPQ")
        order.append(f"{LOCALE}\\patch-{LOCALE}-{index}.MPQ")
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        order.append(f"patch-{letter}.MPQ")
        order.append(f"{LOCALE}\\patch-{LOCALE}-{letter}.MPQ")
    return order


def list_safe(storm: Storm, archive) -> set[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        return set()
    out: set[str] = set()
    try:
        while True:
            out.add(data.cFileName.split(b"\0", 1)[0].decode("latin-1").casefold().replace("/", "\\"))
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


TARGETS = [
    r"Interface\GlueXML\AccountLogin.lua",
    r"Interface\GlueXML\AccountLogin.xml",
    r"Interface\GlueXML\GlueButtons.xml",
    r"Interface\GlueXML\GlueFontStyles.xml",
    r"Interface\GlueXML\GlueFonts.xml",
    r"Interface\GlueXML\GlueTemplates.xml",
    r"Interface\GlueXML\GlueDialog.xml",
    r"Interface\GlueXML\GlueTooltip.xml",
    r"Interface\GlueXML\GlueDropDownMenu.xml",
    r"Interface\GlueXML\RealmList.xml",
    r"Interface\GlueXML\RealmList.lua",
    r"Interface\GlueXML\GlueXML.toc",
    r"Interface\GlueXML\CharacterSelect.xml",
    r"Interface\GlueXML\CharacterCreate.xml",
    r"Interface\GlueXML\GlueParent.lua",
    r"Interface\Glues\Common\Glue-Panel-Button-Up.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Up-Blue.blp",
    r"Interface\Buttons\UI-CheckBox-Check.blp",
]


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    order = load_order()

    # Map: candidate archive path -> entry set (only for archives that exist)
    available: list[tuple[str, set[str]]] = []
    for rel in order:
        path = DATA / rel
        if not path.exists():
            continue
        try:
            handle = storm.open_archive(path)
        except OSError:
            continue
        try:
            names = list_safe(storm, handle)
        finally:
            storm.dll.SFileCloseArchive(handle)
        available.append((rel, names))

    print(f"scanned {len(available)} archives in load order\n")
    for target in TARGETS:
        key = target.casefold()
        holders = [rel for rel, names in available if key in names]
        winner = holders[-1] if holders else None
        flag = "CUSTOM" if winner and winner.casefold() not in {
            f"{LOCALE}\\locale-{LOCALE}.mpq".casefold(),
        } else "stock"
        print(f"{target}")
        print(f"    holder(s): {', '.join(holders) if holders else '(none)'}")
        print(f"    WINNER   : {winner}  [{flag}]\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
