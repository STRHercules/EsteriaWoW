from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLIENT = Path(r"G:\3.3.5a - Dev")

sys.path.insert(0, str(ROOT / "modules" / "mod-classless-wildcard" / "client-patch"))
from lib.mpq import MPQArchive


def read_glue(archive_path: Path, name: str) -> str:
    with MPQArchive(str(archive_path)) as archive:
        return archive.read_file(name).decode("utf-8-sig")


def function_block(source: str, signature: str) -> str:
    start = source.index(signature)
    end = source.index("\nfunction ", start + len(signature))
    return source[start:end]


def assert_keyboard_navigation(lua: str) -> None:
    handler = function_block(lua, "function CharacterSelect_OnKeyDown(self,key)")
    assert 'elseif ( key == "DOWN" or key == "RIGHT" )' in handler
    assert "arg1" not in handler


def assert_virtual_scroll(lua: str, xml: str) -> None:
    update = function_block(lua, "function UpdateCharacterList()")
    handler = function_block(lua, "function CharacterSelect_OnVerticalScroll(self, offset)")
    assert "CharacterSelectCharacterScrollChild:SetHeight(viewportHeight + maxOffset * CHARACTER_SELECT_ROW_HEIGHT)" in update
    assert "CharacterSelectCharacterScrollFrame:UpdateScrollChildRect()" in update
    assert "GlueScrollFrame_OnVerticalScroll(self, offset)" in handler
    assert "CharacterSelect_SetScrollOffset(offset / CHARACTER_SELECT_ROW_HEIGHT)" in handler

    scroll_frame = re.search(
        r'<ScrollFrame name="CharacterSelectCharacterScrollFrame".*?</ScrollFrame>',
        xml,
        re.DOTALL,
    )
    assert scroll_frame, "character-select scroll frame is missing"
    scroll_child = re.search(
        r'<Frame name="CharacterSelectCharacterScrollChild".*?</Frame>',
        scroll_frame.group(0),
        re.DOTALL,
    )
    assert scroll_child, "character-select scroll child is missing"
    assert '<AbsDimension x="1" y="560"/>' in scroll_frame.group(0)


def main() -> None:
    for archive_path in (
        CLIENT / "Data/patch-Z.MPQ",
        CLIENT / "Data/enUS/patch-enUS-Z.MPQ",
    ):
        lua = read_glue(archive_path, r"Interface\GlueXML\CharacterSelect.lua")
        xml = read_glue(archive_path, r"Interface\GlueXML\CharacterSelect.xml")
        assert_keyboard_navigation(lua)
        assert_virtual_scroll(lua, xml)

    print("character-select contract: PASS")


if __name__ == "__main__":
    main()
