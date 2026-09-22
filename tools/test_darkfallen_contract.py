import json
import hashlib
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "NewModels" / "_Other" / "PlayableDarkfallen" / "Darkfallen"
SHARED_DEFINES = ROOT / "src" / "server" / "shared" / "SharedDefines.h"
REGISTRY = ROOT / "modules" / "mod-custom-server" / "data" / "races" / "race_registry.json"
# The updater only scans modules/<name>/data/sql/<db>/ (recursively), so module
# migrations live in db-world/updates - not in the module's own pending_db_world dir.
SQL = ROOT / "modules" / "mod-custom-server" / "data" / "sql" / "db-world" / "updates" / (
    "u_custom_server_2026_09_21_00_darkfallen.sql"
)
RACIAL_SQL = ROOT / "modules" / "mod-custom-server" / "data" / "sql" / "db-world" / "updates" / (
    "u_custom_server_2026_09_21_01_darkfallen_racials.sql"
)
RACIAL_SCRIPT = ROOT / "modules" / "mod-custom-server" / "src" / "darkfallen_racials.cpp"
MODULE_LOADER = ROOT / "modules" / "mod-custom-server" / "src" / "MP_loader.cpp"
SPELL_DBC = ROOT / "DBCs" / "Spell.dbc"
PACKER = ROOT / "tools" / "darkfallen_race_pack.py"
CHARACTER_SELECT_EXTENSION = ROOT / "wxl-races-patcher" / "DarkfallenCharacterSelect.cpp"
UNIT = ROOT / "src" / "server" / "game" / "Entities" / "Unit" / "Unit.h"


class DarkfallenContractTest(unittest.TestCase):
    def test_unit_race_mask_uses_shared_race_helper(self):
        source = UNIT.read_text(encoding="utf-8")
        self.assertRegex(source, r"getRaceMask\(\) const.*GetRaceMaskForRace\(getRace\(true\)\)")

    def test_supplied_assets_have_both_unique_player_models(self):
        self.assertTrue((ASSET_ROOT / "Male" / "DarkfallenMale.m2").is_file())
        self.assertTrue((ASSET_ROOT / "Female" / "DarkfallenFemale.m2").is_file())
        self.assertGreaterEqual(sum(path.is_file() for path in ASSET_ROOT.rglob("*")), 600)

    def test_enum_uses_two_ids_and_shared_mask_helper(self):
        source = SHARED_DEFINES.read_text(encoding="utf-8")
        self.assertRegex(source, r"RACE_DARKFALLEN_ALLIANCE\s*=\s*43")
        self.assertRegex(source, r"RACE_DARKFALLEN_HORDE\s*=\s*44")
        self.assertIn("GetRaceMaskForRace", source)
        self.assertIn("DARKFALLEN_RACE_MASK = 0x80000000u", source)

    def test_registry_contains_both_faction_entries(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        entries = {entry["id"]: entry for entry in registry["playable"]}
        self.assertEqual(entries[43]["faction"], "alliance")
        self.assertEqual(entries[44]["faction"], "horde")
        self.assertEqual(entries[43]["mask"], entries[44]["mask"])
        self.assertEqual(entries[43]["mask"], 0x80000000)

    def test_pending_sql_contains_complete_darkfallen_contract(self):
        source = SQL.read_text(encoding="utf-8")
        for value in (43, 44, 3658, 3659, 60028, 60029, 20579, 20577, 110040, 110042):
            self.assertIn(str(value), source)
        self.assertIn("0x80000000", source)
        self.assertRegex(source, r"(?i)Language Common")
        self.assertRegex(source, r"(?i)Language Orcish")
        self.assertIn("Darkfallen", source)
        self.assertIn("Vampiric Sustenance", source)
        self.assertIn("Crimson Thirst", source)
        self.assertIn("Children of the Night", source)
        # Endurance (20550) is replaced by Crimson Thirst: the cleanup may still delete the
        # old grant, but it must never be handed to a new Darkfallen character again.
        grants = source[source.index("INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`"):]
        grants = grants[:grants.index(";")]
        self.assertNotIn("20550", grants)
        self.assertIn("110040", grants)

    def test_pending_sql_puts_both_factions_in_the_scourge_start_area(self):
        source = SQL.read_text(encoding="utf-8")
        for race in (43, 44):
            self.assertRegex(
                source,
                rf"SELECT {race}, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`\s*"
                rf"FROM `playercreateinfo`\s*WHERE `race` = 5",
            )
        self.assertRegex(
            source,
            r"(?is)UPDATE `quest_template`\s+SET `AllowableRaces` = `AllowableRaces` \| @DarkfallenMask\s+"
            r"WHERE `AllowableRaces` <> 0 AND \(`AllowableRaces` & 16\) <> 0;",
        )

    def test_pending_sql_keeps_the_undead_racial_skill_line_for_darkfallen(self):
        # Vampiric Sustenance and Shadow Resistance hang off skill 220; if the skill line
        # rejects the race the core deletes both spells on login.
        source = SQL.read_text(encoding="utf-8")
        match = re.search(r"\(72, 220, (-?\d+), 1535, 1170, 0, 0, 0\)", source)
        self.assertIsNotNone(match)
        mask = int(match.group(1)) & 0xFFFFFFFF
        self.assertTrue(mask & 0x80000000, "Darkfallen bit missing from the racial skill line")
        self.assertTrue(mask & 0x10, "Undead bit missing from the racial skill line")

    def test_registry_starts_darkfallen_in_tirisfal(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        entries = {entry["id"]: entry for entry in registry["playable"]}
        self.assertEqual(entries[43]["start_profile"], "tirisfal")
        self.assertEqual(entries[44]["start_profile"], "tirisfal")
        self.assertEqual(registry["start_profiles"]["tirisfal"]["zone"], 85)

    def test_spell_table_carries_the_new_racial_rows(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from cars_mount_pack import Wdbc
        from darkfallen_race_pack import (
            SPELL_AURA_1,
            SPELL_AURA_2,
            SPELL_BASE_POINTS_1,
            SPELL_CHILDREN_GHOST_SPEED,
            SPELL_CHILDREN_OF_THE_NIGHT,
            SPELL_CHILDREN_STEALTH_SPEED,
            SPELL_CRIMSON_THIRST,
            SPELL_CRIMSON_THIRST_HEAL,
            SPELL_DURATION_INDEX,
            SPELL_EFFECT_1,
            SPELL_NAME,
            SPELL_PROC_TYPE_MASK,
            SPELL_RECOVERY_TIME,
            SPELL_TRIGGER_1,
            SPELL_VAMPIRIC_SUSTENANCE,
            SPELL_VAMPIRIC_SUSTENANCE_AURA,
            merge_spell_table,
        )

        table = Wdbc(merge_spell_table(SPELL_DBC.read_bytes()))
        rows = {row[0]: row for row in table.rows}

        thirst = rows[SPELL_CRIMSON_THIRST]
        self.assertEqual(table.text(thirst[SPELL_NAME]), "Crimson Thirst")
        self.assertEqual(thirst[SPELL_RECOVERY_TIME], 120000)  # 2 minute cooldown
        self.assertEqual(thirst[SPELL_DURATION_INDEX], 1)  # SpellDuration id 1 = 10 seconds
        self.assertEqual(thirst[SPELL_AURA_1], 42)  # SPELL_AURA_PROC_TRIGGER_SPELL
        self.assertEqual(thirst[SPELL_TRIGGER_1], SPELL_CRIMSON_THIRST_HEAL)
        self.assertTrue(thirst[SPELL_PROC_TYPE_MASK] & 0x4)  # procs on melee auto attacks
        self.assertTrue(thirst[SPELL_PROC_TYPE_MASK] & 0x100)  # ...and ranged damage spells

        heal = rows[SPELL_CRIMSON_THIRST_HEAL]
        self.assertEqual(heal[SPELL_EFFECT_1], 136)  # SPELL_EFFECT_HEAL_PCT
        self.assertEqual(heal[SPELL_BASE_POINTS_1] + 1, 4)  # 4% of maximum health

        children = rows[SPELL_CHILDREN_OF_THE_NIGHT]
        self.assertEqual(table.text(children[SPELL_NAME]), "Children of the Night")
        self.assertEqual(children[SPELL_AURA_1], 17)  # stealth detection
        self.assertEqual(children[SPELL_AURA_2], 154)  # stealth level

        stealth = rows[SPELL_CHILDREN_STEALTH_SPEED]
        self.assertEqual(stealth[SPELL_AURA_1], 31)  # SPELL_AURA_MOD_INCREASE_SPEED
        self.assertEqual(stealth[SPELL_BASE_POINTS_1] + 1, 10)

        ghost = rows[SPELL_CHILDREN_GHOST_SPEED]
        # Stock ghosts run at +50%; the racial adds 40% on top of that max().
        self.assertEqual(ghost[SPELL_BASE_POINTS_1] + 1, 90)

        self.assertEqual(table.text(rows[SPELL_VAMPIRIC_SUSTENANCE][SPELL_NAME]), "Vampiric Sustenance")
        self.assertEqual(table.text(rows[SPELL_VAMPIRIC_SUSTENANCE_AURA][SPELL_NAME]), "Vampiric Sustenance")

    def test_racial_spell_sql_is_the_packer_output(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import render_spell_sql

        expected = render_spell_sql(SPELL_DBC.read_bytes())
        self.assertEqual(RACIAL_SQL.read_text(encoding="utf-8"), expected)
        self.assertIn("INSERT INTO `spell_proc` (`SpellId`, `Cooldown`) VALUES (110040, 2000);", expected)
        self.assertIn("`EquippedItemClass`", expected)  # -1, not a zeroed default

    def test_racial_script_is_wired_into_the_module_loader(self):
        source = RACIAL_SCRIPT.read_text(encoding="utf-8")
        for token in ("110043", "110044", "SPELL_AURA_MOD_STEALTH", "OnPlayerReleasedGhost", "OnPlayerResurrect"):
            self.assertIn(token, source)
        self.assertIn("AddSC_darkfallen_racials", MODULE_LOADER.read_text(encoding="utf-8"))

    def test_glue_strings_upgrade_the_shipped_racial_list(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import DARKFALLEN_GLUE_STRINGS, PREVIOUS_DARKFALLEN_GLUE_STRINGS, patch_glue_strings

        shipped = ("BASE = 1;\n" + PREVIOUS_DARKFALLEN_GLUE_STRINGS + "\nEXTRA = 2;\n").encode("utf-8")
        upgraded = patch_glue_strings(shipped).decode("utf-8")
        # A replacement, not an append: the surrounding text is untouched and the block
        # appears exactly once, now with the new racial lines.
        self.assertEqual(upgraded, "BASE = 1;\n" + DARKFALLEN_GLUE_STRINGS + "\nEXTRA = 2;\n")
        self.assertIn("ABILITY_INFO_DARKFALLEN4", upgraded)
        self.assertEqual(upgraded.count("RACE_INFO_DARKFALLEN ="), 1)
        self.assertEqual(patch_glue_strings(upgraded.encode("utf-8")), upgraded.encode("utf-8"))

    def test_character_info_lists_the_new_racial_names(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import patch_character_info

        source = (
            'Races_Informations[17] = { Name = "Vulpera", '
            'Description = "Resourceful desert survivors and clever allies." }\n'
            '    VULPERA = Races_Informations[17],\n'
            '    [17] = {token = "VULPERA", name = "Vulpera", spells = {}},\n'
            '    [17] = { glueString = "VULPERA",  faction = "Horde" },\n'
            '_G.RACE_15 = "Mag\'har Orc"\n'
            'local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16}\n'
            'local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17}\n'
            '_G.BROKEN_FEMALE = "Broken"\n'
        ).encode("utf-8")
        patched = patch_character_info(source).decode("utf-8")
        self.assertIn('    [18] = {token = "DARKFALLEN", name = "Darkfallen", '
                      'spells = {"Crimson Thirst", "Shadow Resistance", "Vampiric Sustenance", '
                      '"Children of the Night"}}', patched)
        self.assertNotIn("Cannibalize", patched)

    def test_sql_clones_creation_cast_spells_for_both_donors(self):
        source = SQL.read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r"(?is)DELETE\s+FROM\s+`playercreateinfo_cast_spell`\s+WHERE\s+`raceMask`\s*=\s*@DarkfallenMask\s*;",
        )
        self.assertRegex(
            source,
            r"(?is)INSERT\s+IGNORE\s+INTO\s+`playercreateinfo_cast_spell`\s*\(`raceMask`,\s*`classMask`,\s*`spell`,\s*`note`\).*?"
            r"SELECT\s+@DarkfallenMask,\s*`classMask`,\s*`spell`,\s*`note`\s+FROM\s+`playercreateinfo_cast_spell`\s+"
            r"WHERE\s+\(`raceMask`\s*&\s*4096\)\s*<>\s*0\s*;",
        )
        self.assertRegex(
            source,
            r"(?is)INSERT\s+IGNORE\s+INTO\s+`playercreateinfo_cast_spell`\s*\(`raceMask`,\s*`classMask`,\s*`spell`,\s*`note`\).*?"
            r"SELECT\s+@DarkfallenMask,\s*`classMask`,\s*`spell`,\s*`note`\s+FROM\s+`playercreateinfo_cast_spell`\s+"
            r"WHERE\s+\(`raceMask`\s*&\s*512\)\s*<>\s*0\s*;",
        )

    def test_sql_language_mask_updates_skip_zero_masks(self):
        source = SQL.read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r"(?is)UPDATE\s+`skillraceclassinfo_dbc`.*?WHERE\s+`SkillID`\s+IN\s*\(98,\s*109\)\s+AND\s+`RaceMask`\s+<>\s+0\s*;",
        )
        self.assertRegex(
            source,
            r"(?is)UPDATE\s+`skilllineability_dbc`.*?WHERE\s+`SkillLine`\s+IN\s*\(98,\s*109\)\s+AND\s+`RaceMask`\s+<>\s+0\s*;",
        )

    def test_packer_exposes_approved_identity(self):
        source = PACKER.read_text(encoding="utf-8")
        for token in (
            "DARKFALLEN_MASK = 0x80000000",
            "DARKFALLEN_MODEL_IDS",
            "DARKFALLEN_DISPLAY_IDS",
            "Character\\\\Darkfallen\\\\Male",
            "Character\\\\Darkfallen\\\\Female",
            "patch-Z.MPQ",
            "patch-enUS-Z.MPQ",
        ):
            self.assertIn(token, source)

    def test_packer_prints_machine_readable_contract(self):
        result = subprocess.run(
            [sys.executable, str(PACKER), "--print-contract"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        contract = json.loads(result.stdout)
        self.assertEqual(contract["race_ids"], {"alliance": 43, "horde": 44})
        self.assertEqual(contract["race_mask"], 0x80000000)
        self.assertEqual(contract["model_ids"], {"male": 3658, "female": 3659})
        self.assertEqual(contract["display_ids"], {"male": 60028, "female": 60029})
        self.assertEqual(contract["languages"], {"alliance": "Common", "horde": "Orcish"})

    def test_character_create_patch_does_not_override_native_hair_selection(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import patch_character_create

        patched = patch_character_create(
            b'    ["BLOODELF_MALE"] = "Interface\\\\Glues\\\\CharacterCreate\\\\UI-CharacterCreate-BloodElfMale",\n'
            b'        ["MAGHAR"] = "ORC",\n'
        ).decode()
        self.assertNotIn("DARKFALLEN_HAIR_STYLE_COUNT", patched)
        self.assertNotIn("function CharacterCustomization_Left(id)", patched)
        self.assertNotIn("function CharacterCustomization_Right(id)", patched)

    def test_character_info_keeps_the_void_elf_off_the_horde_darkfallen_slot(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import patch_character_info

        # The ordinal-19 Darkfallen insertion that shipped first aliased the Void Elf's
        # Races_Informations[19], so hovering the Void Elf read "Darkfallen".
        stale = (
            'Races_Informations[17] = { Name = "Vulpera", '
            'Description = "Resourceful desert survivors and clever allies." }\n'
            'Races_Informations[18] = { Name = "Darkfallen", '
            'Description = "Children of the night, bound by shadow and blood." }\n'
            'Races_Informations[19] = Races_Informations[18]\n'
            '    [17] = {token = "VULPERA", name = "Vulpera", spells = {}},\n'
            '    [18] = {token = "DARKFALLEN", name = "Darkfallen", spells = {"Shadow Resistance", "Cannibalize"}},\n'
            '    [19] = {token = "DARKFALLEN", name = "Darkfallen", spells = {"Shadow Resistance", "Cannibalize"}},\n'
            '    VULPERA = Races_Informations[17],\n'
            'local ALLIANCE_RACES = {1, 2, 3, 4, 5, 6, 7, 16}\n'
            'local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17}\n'
            '    [17] = { glueString = "VULPERA",  faction = "Horde" },\n'
            '_G.RACE_15 = "Mag\'har Orc"\n'
            '_G.BROKEN_FEMALE = "Broken"\n'
        ).encode()
        repaired = patch_character_info(stale).decode()
        self.assertNotIn("Races_Informations[19] = Races_Informations[18]", repaired)
        self.assertIn('Races_Informations[19] = { Name = "Void Elf"', repaired)
        self.assertIn('Races_Informations[18] = { Name = "Darkfallen"', repaired)
        self.assertNotIn('    [19] = {token = "DARKFALLEN"', repaired)
        self.assertIn('    [18] = {token = "DARKFALLEN"', repaired)
        self.assertIn('_G.RACE_19 = "Darkfallen"', repaired)
        self.assertIn('    [19] = { glueString = "DARKFALLEN", faction = "Horde" }', repaired)
        self.assertEqual(repaired, patch_character_info(repaired.encode()).decode())

    def test_glue_parent_puts_darkfallen_in_the_character_select_backdrop_list(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import patch_glue_parent

        # SetBackgroundModel() falls back to UI_<Race>.m2 for races missing from its faction
        # lists, which left the Darkfallen character-select scene black.
        source = (
            'CharModelFogInfo = { };\n'
            'CharModelGlowInfo = { };\n'
            'GlueAmbienceTracks = { };\n'
            'CharModelFogInfo["KULTIRAN"] = CharModelFogInfo["HUMAN"];\n'
            'RaceLights = {\n'
            '    ORC = { },\n'
            '}\n'
            'RaceLights["KULTIRAN"] = RaceLights["HUMAN"];\n'
            '    local allianceRaces = {\n'
            '        ["KULTIRAN"] = true,\n'
            '    };\n'
            '    local hordeRaces = {\n'
            '        ["ILLIDARI"] = true,\n'
            '    };\n'
        ).encode()
        patched = patch_glue_parent(source).decode()
        self.assertIn('        ["DARKFALLEN"] = true,\n', patched)
        self.assertIn('        ["DARKFALLENHORDE"] = true,\n', patched)
        self.assertIn('CharModelFogInfo["DARKFALLEN"]', patched)
        self.assertIn('CharModelFogInfo["DARKFALLENHORDE"] = CharModelFogInfo["ORC"];', patched)
        self.assertIn('RaceLights["DARKFALLEN"]', patched)
        self.assertIn('RaceLights["DARKFALLENHORDE"]', patched)
        # Every race lookup has to come after its table definition or the Glue aborts on load.
        self.assertLess(patched.index('RaceLights = {'), patched.index('RaceLights["DARKFALLENHORDE"]'))
        self.assertLess(
            patched.index('CharModelGlowInfo = { };'), patched.index('CharModelGlowInfo["DARKFALLENHORDE"]')
        )
        self.assertEqual(patched, patch_glue_parent(patched.encode()).decode())

    def test_character_select_extension_does_not_overwrite_native_race_names(self):
        self.assertTrue(CHARACTER_SELECT_EXTENSION.is_file())
        source = CHARACTER_SELECT_EXTENSION.read_text(encoding="utf-8")
        self.assertNotIn('names[43] = kDarkfallenName;', source)
        self.assertNotIn('names[44] = kDarkfallenName;', source)
        self.assertNotIn('kRaceNameTablePointerOffset', source)
        self.assertIn('        307,', source)

    def test_character_select_extension_limits_native_darkfallen_hair_counts(self):
        source = CHARACTER_SELECT_EXTENSION.read_text(encoding="utf-8")
        self.assertIn("kCharacterCustomizationTablePointerOffset = 0x0076B864", source)
        self.assertIn("kCycleCharCustomizationOffset = 0x000E0B50", source)
        self.assertIn("kCharacterModelTableReferenceOffset = 0x000E157D", source)
        self.assertIn("kSelectedCharacterIndexOffset = 0x006C436C", source)
        self.assertIn('"Darkfallen_CycleCharCustomization"', source)
        self.assertIn('"Darkfallen_CharacterSelectModelProbe"', source)
        self.assertIn('"Darkfallen_ModelDescriptorProbe"', source)
        self.assertIn('"Darkfallen_CharacterListLoadProbe"', source)
        self.assertIn('kResolveModelDescriptorOffset = 0x002DC810', source)
        self.assertIn('kCharacterListLoadOffset = 0x000E3CD0', source)
        self.assertIn('resourceReady', source)
        self.assertIn('renderer', source)
        self.assertIn("CycleCharCustomizationDetour", source)
        self.assertIn("SetCustomizationCount(customizations, 43, 0, 9);", source)
        self.assertIn("SetCustomizationCount(customizations, 43, 1, 10);", source)
        self.assertIn("SetCustomizationCount(customizations, 44, 0, 9);", source)
        self.assertIn("SetCustomizationCount(customizations, 44, 1, 10);", source)

    def test_char_sections_merge_replaces_existing_darkfallen_rows(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import ASSET_ROOT as PACKER_ASSET_ROOT, _merge_race_table
        from playable_race_pack import RawWdbc

        baseline = (ROOT / "DBCs" / "CharSections.dbc").read_bytes()
        merged = _merge_race_table("CharSections", baseline, PACKER_ASSET_ROOT)
        refreshed_sections = RawWdbc(_merge_race_table("CharSections", merged, PACKER_ASSET_ROOT))
        for race_id in (43, 44):
            self.assertEqual(
                sum(
                    int.from_bytes(row[4:8], "little") == race_id
                    and int.from_bytes(row[12:16], "little") == 0
                    for row in refreshed_sections.records
                ),
                12,
            )

    def test_hair_geosets_only_include_darkfallen_model_styles(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import ASSET_ROOT as PACKER_ASSET_ROOT, _merge_race_table
        from playable_race_pack import RawWdbc

        baseline = (ROOT / "DBCs" / "CharHairGeosets.dbc").read_bytes()
        merged = RawWdbc(_merge_race_table("CharHairGeosets", baseline, PACKER_ASSET_ROOT))
        for race_id in (43, 44):
            styles_by_gender = {
                gender: {
                    int.from_bytes(row[12:16], "little")
                    for row in merged.records
                    if int.from_bytes(row[4:8], "little") == race_id
                    and int.from_bytes(row[8:12], "little") == gender
                }
                for gender in (0, 1)
            }
            self.assertEqual(styles_by_gender[0], set(range(9)))
            self.assertEqual(styles_by_gender[1], set(range(10)))

    def test_barber_hair_styles_only_include_darkfallen_model_styles(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import ASSET_ROOT as PACKER_ASSET_ROOT, _merge_race_table
        from playable_race_pack import RawWdbc

        baseline = (ROOT / "DBCs" / "BarberShopStyle.dbc").read_bytes()
        merged = RawWdbc(_merge_race_table("BarberShopStyle", baseline, PACKER_ASSET_ROOT))
        for race_id in (43, 44):
            styles_by_gender = {
                gender: {
                    int.from_bytes(row[156:160], "little")
                    for row in merged.records
                    if int.from_bytes(row[148:152], "little") == race_id
                    and int.from_bytes(row[152:156], "little") == gender
                    and int.from_bytes(row[4:8], "little") == 0
                }
                for gender in (0, 1)
            }
            self.assertEqual(styles_by_gender[0], set(range(9)))
            self.assertEqual(styles_by_gender[1], set(range(10)))

    @unittest.skipUnless(
        (ROOT / "patch-Z.MPQ").is_file()
        and (ROOT / "patch-enUS-Z.MPQ").is_file()
        and (ROOT / "NewModels" / "_Other" / "PlayableDarkfallen" / "Darkfallen").is_dir(),
        "Darkfallen source archives/assets are required for the pack integration contract",
    )
    def test_packer_stages_real_dbc_and_asset_merge_without_mutating_sources(self):
        sys.path.insert(0, str(ROOT / "tools"))
        from darkfallen_race_pack import build_darkfallen_pack

        with self.subTest("stage"):
            import tempfile

            with tempfile.TemporaryDirectory() as temporary:
                source_hashes = {
                    path: hashlib.sha256(path.read_bytes()).digest()
                    for path in (ROOT / "patch-Z.MPQ", ROOT / "patch-enUS-Z.MPQ")
                }
                report = build_darkfallen_pack(
                    ROOT / "patch-Z.MPQ",
                    ROOT / "patch-enUS-Z.MPQ",
                    Path(temporary) / "staged",
                )

                self.assertEqual(report.race_ids, (43, 44))
                self.assertIn("DBFilesClient\\ChrRaces.dbc", report.root_updates)
                self.assertIn("Character\\Darkfallen\\Male\\DarkfallenMale.m2", report.root_updates)
                self.assertIn(
                    "Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkfallenMale.blp",
                    report.root_updates,
                )
                self.assertIn("Interface\\GlueXML\\GlueStrings.lua", report.locale_updates)
                self.assertTrue((Path(temporary) / "staged" / "patch-Z.MPQ").is_file())
                self.assertTrue((Path(temporary) / "staged" / "patch-enUS-Z.MPQ").is_file())
                self.assertEqual(
                    source_hashes,
                    {path: hashlib.sha256(path.read_bytes()).digest() for path in source_hashes},
                )

                from derive_playable_race_portraits import validate_portrait
                from playable_race_pack import RawWdbc, WDBC_LAYOUTS

                for gender in ("Male", "Female"):
                    portrait = f"Interface\\CharacterFrame\\TemporaryPortrait-{gender}-Darkfallen.blp"
                    self.assertIn(portrait, report.root_updates)
                    self.assertIn(portrait, report.locale_updates)
                    validate_portrait(report.root_updates[portrait], Path(portrait))

                races = RawWdbc(report.root_updates["DBFilesClient\\ChrRaces.dbc"])
                race_rows = {int.from_bytes(row[:4], "little"): row for row in races.records}
                self.assertEqual(set((43, 44)), set(race_rows) & {43, 44})
                self.assertEqual(int.from_bytes(race_rows[43][28:32], "little"), 7)
                self.assertEqual(int.from_bytes(race_rows[44][28:32], "little"), 1)
                self.assertEqual(int.from_bytes(race_rows[43][16:20], "little"), 60028)
                self.assertEqual(int.from_bytes(race_rows[43][20:24], "little"), 60029)
                self.assertEqual(race_rows[43][12:16], race_rows[13][12:16])
                self.assertEqual(race_rows[44][12:16], race_rows[10][12:16])
                self.assertEqual(
                    races.strings[int.from_bytes(race_rows[43][44:48], "little") :].split(b"\0", 1)[0],
                    b"Darkfallen",
                )
                self.assertEqual(
                    races.strings[int.from_bytes(race_rows[44][44:48], "little") :].split(b"\0", 1)[0],
                    b"DarkfallenHorde",
                )

                base_info = RawWdbc(report.root_updates["DBFilesClient\\CharBaseInfo.dbc"])
                base_rows = {
                    row[0]: row
                    for row in base_info.records
                }
                self.assertEqual(base_rows[43][1:], base_rows[10][1:])
                self.assertEqual(base_rows[44][1:], base_rows[10][1:])

                models = RawWdbc(report.root_updates["DBFilesClient\\CreatureModelData.dbc"])
                model_paths = {
                    int.from_bytes(row[:4], "little"): models.strings[
                        int.from_bytes(row[8:12], "little") :
                    ].split(b"\0", 1)[0].decode()
                    for row in models.records
                    if int.from_bytes(row[:4], "little") in (3658, 3659)
                }
                self.assertEqual(model_paths[3658], "Character\\Darkfallen\\Male\\DarkfallenMale.m2")
                self.assertEqual(model_paths[3659], "Character\\Darkfallen\\Female\\DarkfallenFemale.m2")

                displays = RawWdbc(report.root_updates["DBFilesClient\\CreatureDisplayInfo.dbc"])
                display_models = {
                    int.from_bytes(row[:4], "little"): int.from_bytes(row[4:8], "little")
                    for row in displays.records
                    if int.from_bytes(row[:4], "little") in (60028, 60029)
                }
                self.assertEqual(display_models[60028], 3658)
                self.assertEqual(display_models[60029], 3659)

                from darkfallen_race_pack import _merge_model_rows

                refreshed_models = RawWdbc(
                    _merge_model_rows("CreatureModelData", report.root_updates["DBFilesClient\\CreatureModelData.dbc"])
                )
                refreshed_displays = RawWdbc(
                    _merge_model_rows("CreatureDisplayInfo", report.root_updates["DBFilesClient\\CreatureDisplayInfo.dbc"])
                )
                self.assertEqual(
                    {
                        int.from_bytes(row[:4], "little"): int.from_bytes(row[4:8], "little")
                        for row in refreshed_displays.records
                        if int.from_bytes(row[:4], "little") in (60028, 60029)
                    },
                    display_models,
                )
                self.assertEqual(
                    {
                        int.from_bytes(row[:4], "little"): refreshed_models.strings[
                            int.from_bytes(row[8:12], "little") :
                        ]
                        .split(b"\0", 1)[0]
                        .decode()
                        for row in refreshed_models.records
                        if int.from_bytes(row[:4], "little") in (3658, 3659)
                    },
                    model_paths,
                )

                sections = RawWdbc(report.root_updates["DBFilesClient\\CharSections.dbc"])

                def strings(row):
                    return [
                        sections.strings[int.from_bytes(row[offset : offset + 4], "little") :]
                        .split(b"\0", 1)[0]
                        .decode()
                        for offset in (16, 20, 24)
                    ]

                for race_id in (43, 44):
                    race_rows = [row for row in sections.records if int.from_bytes(row[4:8], "little") == race_id]
                    skin_rows = [row for row in race_rows if int.from_bytes(row[12:16], "little") == 0]
                    hair_rows = [row for row in race_rows if int.from_bytes(row[12:16], "little") == 3]
                    self.assertEqual(len(skin_rows), 12)
                    self.assertTrue(hair_rows)
                    for row in race_rows:
                        for texture in filter(None, strings(row)):
                            if texture.startswith("Character\\Darkfallen\\"):
                                asset = ASSET_ROOT / texture.removeprefix("Character\\Darkfallen\\").replace("\\", "/")
                                self.assertTrue(asset.is_file(), texture)
                    self.assertTrue(
                        all(
                            texture.startswith("Character\\BloodElf\\")
                            for row in hair_rows
                            for texture in filter(None, strings(row))
                        )
                    )

                masks = RawWdbc(report.root_updates["DBFilesClient\\SkillRaceClassInfo.dbc"])
                mask_offset = WDBC_LAYOUTS["SkillRaceClassInfo"].race_offset
                source_bits = (1 << (10 - 1)) | (1 << (13 - 1))
                source_masks = [
                    int.from_bytes(row[mask_offset : mask_offset + 4], "little")
                    for row in masks.records
                    if int.from_bytes(row[mask_offset : mask_offset + 4], "little") & source_bits
                ]
                self.assertTrue(any(mask & (1 << (13 - 1)) for mask in source_masks))
                self.assertTrue(all(mask & 0x80000000 for mask in source_masks))

                root_info = report.root_updates["Interface\\GlueXML\\CharacterInfo.lua"].decode()
                root_create = report.root_updates["Interface\\GlueXML\\CharacterCreate.lua"].decode()
                root_parent = report.root_updates["Interface\\GlueXML\\GlueParent.lua"].decode()
                locale_strings = report.locale_updates["Interface\\GlueXML\\GlueStrings.lua"].decode()
                self.assertIn('[18] = { glueString = "DARKFALLEN", faction = "Alliance" }', root_info)
                self.assertIn('[19] = { glueString = "DARKFALLEN", faction = "Horde" }', root_info)
                self.assertIn('"DARKFALLEN_MALE"', root_create)
                self.assertIn('CharModelFogInfo["DARKFALLEN"]', root_parent)
                self.assertIn('        ["DARKFALLEN"] = true,\n', root_parent)
                self.assertIn('        ["DARKFALLEN"] = true,\n', report.locale_updates["Interface\\GlueXML\\GlueParent.lua"].decode())
                self.assertIn('        ["DARKFALLENHORDE"] = true,\n', root_parent)
                self.assertIn('"DARKFALLENHORDE_MALE"', root_create)
                select = report.root_updates["Interface\\GlueXML\\CharacterSelect.lua"].decode()
                self.assertIn('raceModel = strupper(GetSelectBackgroundModel(actualIndex) or "")', select)
                self.assertIn("RACE_INFO_DARKFALLEN", locale_strings)
                validate_portrait(
                    report.root_updates["Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-DarkfallenMale.blp"],
                    Path("DarkfallenMale.blp"),
                )

    def test_direct_race_shifts_are_not_left_in_server_sources(self):
        source_roots = (
            ROOT / "src" / "server" / "game",
            ROOT / "src" / "server" / "shared",
        )
        offenders = []
        for root in source_roots:
            for path in root.rglob("*.h"):
                text = path.read_text(encoding="utf-8", errors="replace")
                if re.search(r"1\s*<<\s*\(\s*race\s*-\s*1\s*\)", text):
                    offenders.append(str(path.relative_to(ROOT)))
            for path in root.rglob("*.cpp"):
                text = path.read_text(encoding="utf-8", errors="replace")
                if re.search(r"1\s*<<\s*\(\s*race\s*-\s*1\s*\)", text):
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
