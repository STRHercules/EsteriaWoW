from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLIENT = Path(r"G:\3.3.5a - Dev")
EXPECTED_LIMIT = 100

sys.path.insert(0, str(ROOT / "modules" / "mod-classless-wildcard" / "client-patch"))
from lib.mpq import MPQArchive


def assert_configured(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert re.search(r"CharactersPerAccount\s*=\s*100", text), path
    assert re.search(r"CharactersPerRealm\s*=\s*100", text), path


def read_glue(archive_path: Path, name: str) -> str:
    archive = MPQArchive(str(archive_path))
    return archive.read_file(name).decode("utf-8-sig")


def main() -> None:
    world_config = (ROOT / "src/server/game/World/WorldConfig.cpp").read_text(encoding="utf-8")
    assert '"CharactersPerRealm", 100' in world_config
    assert "value > 0 && value <= 100" in world_config
    assert '"CharactersPerAccount", 100' in world_config

    for path in (
        ROOT / "src/server/apps/worldserver/worldserver.conf.dist",
        ROOT / "env/dist/etc/worldserver.conf.dist",
        ROOT / "env/dist/etc/worldserver.conf",
    ):
        assert_configured(path)

    for path in (
        ROOT / "src/server/scripts/Commands/cs_character.cpp",
        ROOT / "src/server/game/Tools/PlayerDump.cpp",
    ):
        text = path.read_text(encoding="utf-8")
        assert "charcount >= 10" not in text
        assert "getIntConfig(CONFIG_CHARACTERS_PER_ACCOUNT)" in text

    hire_action = (ROOT / "modules/mod-playerbots/src/Ai/Base/Actions/HireAction.cpp").read_text(encoding="utf-8")
    assert "charCount >= 10" not in hire_action
    assert "uint32 charCount = 10" not in hire_action
    assert "getIntConfig(CONFIG_CHARACTERS_PER_ACCOUNT)" in hire_action

    realm_schema = (ROOT / "data/sql/base/db_auth/realmcharacters.sql").read_text(encoding="utf-8")
    assert "`numchars` tinyint unsigned" in realm_schema

    wow = (CLIENT / "Wow.exe").read_bytes()
    assert wow[0x6404C:0x64050] == bytes.fromhex("80 7D FF 64")

    for archive_path in (
        CLIENT / "Data/patch-Z.MPQ",
        CLIENT / "Data/enUS/patch-enUS-Z.MPQ",
    ):
        lua = read_glue(archive_path, r"Interface\GlueXML\CharacterSelect.lua")
        xml = read_glue(archive_path, r"Interface\GlueXML\CharacterSelect.xml")
        assert "MAX_CHARACTERS_PER_REALM = 100" in lua
        assert "CharacterSelect_ScrollBy" in lua
        assert "button:SetID(actualIndex)" in lua
        assert "CharacterSelectCharacterScrollFrame" in xml
        assert "GlueScrollFrameTemplate" in xml
        assert "OnMouseWheel" in xml
        scroll_frame = re.search(
            r'<ScrollFrame name="CharacterSelectCharacterScrollFrame".*?</ScrollFrame>',
            xml,
            re.DOTALL,
        )
        assert scroll_frame and scroll_frame.group(0).count('<AbsDimension x="1" y="560"/>') == 2, archive_path

    print("character-limit contract: PASS")


if __name__ == "__main__":
    main()
