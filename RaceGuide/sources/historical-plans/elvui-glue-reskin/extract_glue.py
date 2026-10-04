"""Extract GlueXML files from client MPQs into a staging tree (read-only on source)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW\tools")))

from cars_mount_pack import Storm, DLL_DEFAULT  # noqa: E402

CLIENT_DATA = Path(r"G:\3.3.5a - Dev\Data")
OUT = Path(__file__).resolve().parent / "extracted"

STOCK = CLIENT_DATA / "enUS" / "locale-enUS.MPQ"
DEPLOYED_ROOT = CLIENT_DATA / "patch-Z.MPQ"
DEPLOYED_LOCALE = CLIENT_DATA / "enUS" / "patch-enUS-Z.MPQ"

# Everything under Interface\GlueXML we may need to touch.
GLUE_NAMES = (
    "AccountLogin.lua", "AccountLogin.xml",
    "AddonList.lua", "AddonList.xml",
    "CharacterCreate.lua", "CharacterCreate.xml",
    "CharacterInfo.lua", "CharacterSelect.lua", "CharacterSelect.xml",
    "CreditsFrame.lua", "CreditsFrame.xml",
    "GlueBasicControls.xml",
    "GlueButtons.lua", "GlueButtons.xml",
    "GlueDialog.lua", "GlueDialog.xml",
    "GlueDropDownMenu.lua", "GlueDropDownMenu.xml", "GlueDropDownMenuTemplates.xml",
    "GlueFonts.xml", "GlueFontStyles.xml",
    "GlueLocalization.lua", "GlueLocalization.xml",
    "GlueLocalizationPost.lua", "GlueLocalizationPost.xml",
    "GlueParent.lua", "GlueParent.xml",
    "GlueSplash.xml", "GlueStrings.lua",
    "GlueTemplates.lua", "GlueTemplates.xml", "GlueTooltip.xml",
    "GlueXML.toc",
    "MovieFrame.lua", "MovieFrame.xml",
    "OptionsFrame.lua", "OptionsFrame.xml", "OptionsFrameTemplates.xml",
    "PatchDownload.lua", "PatchDownload.xml",
    "RaceSelect.lua", "RaceSelect.xml",
    "RealmList.lua", "RealmList.xml",
    "RealmWizard.lua", "RealmWizard.xml",
    "SecurityMatrix.lua", "SecurityMatrix.xml",
    "SoundOptionsFrame.lua", "SoundOptionsFrame.xml",
)


def dump(storm: Storm, archive: Path, subdir: str) -> None:
    handle = storm.open_archive(archive)
    target_dir = OUT / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    got = 0
    try:
        for name in GLUE_NAMES:
            key = f"Interface\\GlueXML\\{name}"
            try:
                payload = storm.read(handle, key)
            except OSError:
                continue
            (target_dir / name).write_bytes(payload)
            got += 1
    finally:
        storm.dll.SFileCloseArchive(handle)
    print(f"{subdir}: {got} files from {archive.name}")


def main() -> int:
    storm = Storm(DLL_DEFAULT)
    dump(storm, STOCK, "stock-locale")
    dump(storm, DEPLOYED_ROOT, "deployed-root")
    dump(storm, DEPLOYED_LOCALE, "deployed-locale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
