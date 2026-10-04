"""Extract the live (patch-A) glue button art + definitions for analysis."""

from __future__ import annotations

import ctypes as c
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))

from cars_mount_pack import Storm, FindData, DLL_DEFAULT  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "live"

ARCHIVES = {
    "A": Path(r"G:\3.3.5a - Dev\Data\patch-A.MPQ"),
    "enUS2": Path(r"G:\3.3.5a - Dev\Data\enUS\patch-enUS-2.MPQ"),
}

TARGETS = [
    r"Interface\GlueXML\GlueButtons.xml",
    r"Interface\GlueXML\GlueButtons.lua",
    r"Interface\GlueXML\GlueTemplates.xml",
    r"Interface\GlueXML\AccountLogin.xml",
    r"Interface\GlueXML\AccountLogin.lua",
    r"Interface\GlueXML\RealmList.xml",
    r"Interface\GlueXML\GlueFontStyles.xml",
    r"Interface\GlueXML\GlueFonts.xml",
    r"Interface\GlueXML\GlueDialog.xml",
    r"Interface\GlueXML\GlueTooltip.xml",
    r"Interface\Glues\Common\Glue-Panel-Button-Up.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Down.blp",
    r"Interface\Glues\Common\Glue-Panel-Button-Glow.blp",
    r"Interface\Glues\Common\glue-panel-button-up-blue.blp",
    r"Interface\Glues\Common\glue-panel-button-down-blue.blp",
    r"Interface\Glues\Common\glue-panel-button-highlight.blp",
    r"Interface\Glues\Common\glue-panel-button-highlight-blue.blp",
    r"Interface\Glues\Common\Glues-BigButton-Up.blp",
    r"Interface\Glues\Common\Glues-BigButton-Down.blp",
    r"Interface\Glues\Common\Glues-BigButton-Rays.blp",
    r"Interface\Glues\Common\Arrow.blp",
    r"Interface\Glues\Common\generic.blp",
    r"Interface\Glues\CharacterCreate\glue-panel-button-up-v2.blp",
    r"Interface\Glues\CharacterCreate\glue-panel-button-down-v2.blp",
    r"Interface\Glues\CharacterCreate\glue-panel-button-disable-v2.blp",
    r"Interface\Glues\CharacterCreate\RedButtonUp.blp",
    r"Interface\Glues\CharacterCreate\RedButtonDown.blp",
    r"Interface\Glues\CharacterCreate\RedButtonDisable.blp",
    r"Interface\Glues\CharacterCreate\RedButtonHighlight.blp",
]


def list_safe(storm: Storm, archive) -> set[str]:
    data = FindData()
    finder = storm.dll.SFileFindFirstFile(archive, b"*", c.byref(data), None)
    if not finder:
        return set()
    out: set[str] = set()
    try:
        while True:
            out.add(data.cFileName.split(b"\0", 1)[0].decode("latin-1"))
            if not storm.dll.SFileFindNextFile(finder, c.byref(data)):
                break
    finally:
        storm.dll.SFileFindClose(finder)
    return out


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    OUT.mkdir(parents=True, exist_ok=True)
    for tag, archive_path in ARCHIVES.items():
        handle = storm.open_archive(archive_path)
        try:
            names = list_safe(storm, handle)
            lookup = {n.casefold(): n for n in names}
            for target in TARGETS:
                actual = lookup.get(target.casefold())
                if actual is None:
                    continue
                payload = storm.read(handle, actual)
                target_dir = OUT / tag / Path(actual.replace("\\", "/")).parent
                target_dir.mkdir(parents=True, exist_ok=True)
                path = OUT / tag / Path(actual.replace("\\", "/"))
                path.write_bytes(payload)
                print(f"[{tag}] {actual} ({len(payload)} bytes)")
        finally:
            storm.dll.SFileCloseArchive(handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
