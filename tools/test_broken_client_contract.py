import struct
import sys
from pathlib import Path


CLIENT_PATCH_ROOT = Path("modules/mod-classless-wildcard/client-patch")
sys.path.insert(0, str(CLIENT_PATCH_ROOT))
from lib.clientfs import ClientFiles  # noqa: E402
from lib.dbc import read_string  # noqa: E402


CLIENT_DATA = Path("3.3.5a - Dev/Data")
CUSTOM_RACE_LANGUAGE_MASK = 0x787FA000
LANGUAGE_SKILL_LINES = (98, 109, 111, 113, 115, 137, 138, 139, 140, 141, 313, 315, 673, 759)


def _table(files, name):
    data, source = files.find(f"DBFilesClient\\{name}.dbc")
    magic, count, fields, record_size, string_size = struct.unpack_from(
        "<4s4I", data
    )
    assert magic == b"WDBC"
    assert len(data) == 20 + count * record_size + string_size
    records = [
        data[20 + index * record_size : 20 + (index + 1) * record_size]
        for index in range(count)
    ]
    strings = data[20 + count * record_size :]
    return records, strings, source


def _field(record, index):
    return struct.unpack_from("<I", record, index * 4)[0]


def test_broken_race14_uses_the_server_model_pair():
    files = ClientFiles(str(CLIENT_DATA), "enUS")
    try:
        races, race_strings, race_source = _table(files, "ChrRaces")
        race = next(record for record in races if _field(record, 0) == 14)
        assert (_field(race, 4), _field(race, 5)) == (60002, 60003), race_source
        assert read_string(race_strings, _field(race, 6)) == "Bk"
        assert read_string(race_strings, _field(race, 11)) == "Broken"

        custom_races = {
            _field(record, 0): (_field(record, 4), _field(record, 5))
            for record in races
            if _field(record, 0) in (16, 17, 18, 19, 20, 21, 22, 23, 28, 29, 30, 31)
        }
        assert custom_races == {
            16: (60008, 60009),
            17: (60010, 60011),
            18: (60004, 60005),
            19: (60012, 60013),
            20: (60006, 60007),
            21: (60014, 60015),
            22: (60016, 60017),
            23: (60018, 60019),
            28: (60020, 60021),
            29: (60022, 60023),
            30: (60024, 60025),
            31: (60026, 60027),
        }, race_source
        for race in (30, 31):
            row = next(record for record in races if _field(record, 0) == race)
            assert all(
                read_string(race_strings, _field(row, field)) == "Illidari"
                for field in (14, 31, 48)
            ), race_source

        base_info, _, base_source = _table(files, "CharBaseInfo")
        base_pairs = {(record[0], record[1]) for record in base_info}
        assert all(
            (race, 2) in base_pairs
            for race in (14, 16, 17, 18, 19, 20, 21, 22, 23, 28, 29, 30, 31)
        ), base_source

        race31 = next(
            (record for record in races if _field(record, 0) == 31),
            None,
        )
        assert race31 is not None, race_source
        assert (_field(race31, 4), _field(race31, 5)) == (60026, 60027), race_source

        language_skills, _, language_source = _table(files, "SkillRaceClassInfo")
        assert all(
            _field(record, 2) & CUSTOM_RACE_LANGUAGE_MASK == CUSTOM_RACE_LANGUAGE_MASK
            for record in language_skills
            if _field(record, 1) in LANGUAGE_SKILL_LINES and _field(record, 2)
        ), language_source
        assert {
            _field(record, 1)
            for record in language_skills
            if _field(record, 1) in LANGUAGE_SKILL_LINES
        } >= set(LANGUAGE_SKILL_LINES), language_source

        language_abilities, _, ability_source = _table(files, "SkillLineAbility")
        assert all(
            _field(record, 3) & CUSTOM_RACE_LANGUAGE_MASK == CUSTOM_RACE_LANGUAGE_MASK
            for record in language_abilities
            if _field(record, 1) in LANGUAGE_SKILL_LINES and _field(record, 3)
        ), ability_source
        assert {
            _field(record, 1)
            for record in language_abilities
            if _field(record, 1) in LANGUAGE_SKILL_LINES
        } >= set(LANGUAGE_SKILL_LINES), ability_source

        sections, section_strings, section_source = _table(files, "CharSections")
        section_text = [
            read_string(section_strings, _field(record, field))
            for record in sections
            if _field(record, 1) in (18, 20)
            for field in (4, 5, 6)
        ]
        assert any("pandaren" in text.lower() for text in section_text), section_source
        assert any("vulpera" in text.lower() for text in section_text), section_source

        geosets, _, geoset_source = _table(files, "CharHairGeosets")
        assert sum(_field(record, 1) == 18 for record in geosets) >= 37, geoset_source
        assert sum(_field(record, 1) == 20 for record in geosets) >= 28, geoset_source

        hair_textures, _, hair_source = _table(files, "CharHairTextures")
        assert sum(_field(record, 1) == 20 for record in hair_textures) >= 4, hair_source

        displays, _, display_source = _table(files, "CreatureDisplayInfo")
        display_models = {
            _field(record, 0): _field(record, 1)
            for record in displays
            if _field(record, 0) in (60002, 60003, 60026, 60027)
        }
        assert display_models == {
            60002: 4898,
            60003: 4899,
            60026: 3656,
            60027: 3657,
        }, display_source

        models, model_strings, model_source = _table(files, "CreatureModelData")
        model_paths = {
            _field(record, 0): read_string(model_strings, _field(record, 2))
            for record in models
            if _field(record, 0) in (3656, 3657, 4898, 4899)
        }
        assert model_paths == {
            3656: r"Character\BloodElf_Dh\Male\BloodElfMale_DH.m2",
            3657: r"Character\BloodElf_Dh\Female\BloodElfFemale_DH.m2",
            4898: r"Character\EsteriaBroken\Male\BrokenMale.m2",
            4899: r"Character\EsteriaBroken\Female\BrokenFemale.m2",
        }, model_source

        for asset in (
            r"Character\BloodElf_Dh\Male\BloodElfMale_DH.m2",
            r"Character\BloodElf_Dh\Female\BloodElfFemale_DH.m2",
            r"Character\EsteriaBroken\Male\BrokenMale.m2",
            r"Character\EsteriaBroken\Female\BrokenFemale.m2",
        ):
            files.find(asset)
    finally:
        files.close()


def test_custom_glue_uses_one_race_ui_bundle():
    files = ClientFiles(str(CLIENT_DATA), "enUS")
    try:
        creator_lua, _ = files.find("Interface\\GlueXML\\CharacterCreate.lua")
        creator_xml, _ = files.find("Interface\\GlueXML\\CharacterCreate.xml")
        select_lua, _ = files.find("Interface\\GlueXML\\CharacterSelect.lua")
        select_xml, _ = files.find("Interface\\GlueXML\\CharacterSelect.xml")
        glue_parent, _ = files.find("Interface\\GlueXML\\GlueParent.lua")
        toc, _ = files.find("Interface\\GlueXML\\GlueXML.toc")

        assert b"MAX_RACES = 40" in creator_lua
        assert b"CharacterCreateRaceButton40" in creator_xml
        assert b"GetCharacterFaction" in select_lua
        assert b"OptionsButton2" in select_xml
        assert b'CharModelFogInfo["ILLIDARI"]' in glue_parent
        assert b"CharacterInfo.lua" in toc
    finally:
        files.close()


if __name__ == "__main__":
    test_broken_race14_uses_the_server_model_pair()
    test_custom_glue_uses_one_race_ui_bundle()
    print("Broken client contract: PASS")
