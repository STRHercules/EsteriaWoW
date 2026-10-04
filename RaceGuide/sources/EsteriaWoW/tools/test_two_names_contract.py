"""Contract checks for Esteria's first + last name character creation integration."""

from pathlib import Path
import tempfile
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MAIN_XML = ROOT / "modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Interface/GlueXML/CharacterCreate.xml"
OPTIONAL_XML = ROOT / "modules/mod-worgoblin-high-elf/data/Optional/patch-J.MPQ/Interface/GlueXML/CharacterCreate.xml"
CREATE_LUA = ROOT / "modules/mod-worgoblin-high-elf/data/patch-A.MPQ/Interface/GlueXML/CharacterCreate.lua"
MODULE_CPP = ROOT / "modules/mod-two-names/src/mod_two_names.cpp"
OBJECT_MGR = ROOT / "src/server/game/Globals/ObjectMgr.cpp"
RUNTIME_CPP = ROOT / "wxl-races-patcher/DarkfallenCharacterSelect.cpp"
SQL_UPDATE = ROOT / "data/sql/updates/pending_db_characters/rev_1790759893197493100.sql"


def check_xml(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    ET.fromstring(text)
    assert 'name="CharacterCreateNameEdit" letters="12"' in text
    assert 'name="CharacterCreateLastNameEdit" letters="12"' in text
    assert 'text="First Name"' in text
    assert 'text="Last Name"' in text
    assert '<Anchor point="BOTTOM" x="-110" y="55"/>' in text
    assert '<Anchor point="BOTTOM" x="110" y="55"/>' in text
    assert "CharacterCreate_RandomizeName();" in text


def main() -> None:
    check_xml(MAIN_XML)
    check_xml(OPTIONAL_XML)

    lua = CREATE_LUA.read_text(encoding="utf-8")
    assert "function CharacterCreate_GetFullName()" in lua
    assert 'return firstName.." "..lastName;' in lua
    assert "CreateCharacter(CharacterCreate_GetFullName());" in lua
    assert '"CharacterCreateLastNameEdit",' in lua

    module = MODULE_CPP.read_text(encoding="utf-8")
    assert "CanNormalizePlayerName(std::string& name, bool& result) override" in module
    assert "OnCheckPlayerName(std::string_view name, bool create, uint8& result) override" in module
    assert 'GetOption<uint32>("TwoNames.MaxPartLength", 12)' in module

    object_mgr = OBJECT_MGR.read_text(encoding="utf-8")
    assert "sScriptMgr->CanNormalizePlayerName(name, result)" in object_mgr
    assert "sScriptMgr->OnCheckPlayerName(name, create, result)" in object_mgr

    runtime = RUNTIME_CPP.read_text(encoding="utf-8")
    assert "kValidateNameOffset = 0x002B0390" in runtime
    assert "kValidateNameTwoNamesBytes" in runtime
    assert "ApplyTwoNamesClientPatch()" in runtime

    sql = SQL_UPDATE.read_text(encoding="utf-8")
    assert sql.count("VARCHAR(30)") == 5

    import two_names_client_pack as pack

    with tempfile.TemporaryDirectory() as directory:
        client = Path(directory) / "client"
        for relative in (pack.ROOT_ARCHIVE, pack.LOCALE_ARCHIVE):
            archive = client / relative
            archive.parent.mkdir(parents=True, exist_ok=True)
            archive.write_bytes(b"original archive")
        with patch.object(pack, "Storm"), patch.object(pack, "_read_updates", return_value={"test": b"changed"}), \
                patch.object(pack, "_write_patched_archive"):
            result = pack.install(client)
        backup = Path(result["backup"])
        assert not backup.is_relative_to(client), "backup MPQs must never enter the client's archive mount tree"
        for relative in (pack.ROOT_ARCHIVE, pack.LOCALE_ARCHIVE):
            assert (backup / relative.name).read_bytes() == b"original archive"

    print("two-names contract: PASS")


if __name__ == "__main__":
    main()
