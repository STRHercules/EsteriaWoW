import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_DEFINES = ROOT / "src/server/shared/SharedDefines.h"
RACE_REGISTRY = ROOT / "modules/mod-custom-server/data/races/race_registry.json"
PLAYERBOT_FACTORY = ROOT / "modules/mod-playerbots/src/Bot/Factory/RandomPlayerbotFactory.cpp"
SQL_MIGRATION = (
    ROOT
    / "modules/mod-custom-server/data/sql/db-world/updates/"
    / "u_custom_server_2026_09_10_01_race_scope_corrective.sql"
)


EXPECTED_RACE_MAP = {
    "RACE_SETHRAK": 15,
    "RACE_EREDAR": 16,
    "RACE_NIGHTBORNE": 17,
    "RACE_PANDAREN_ALLIANCE": 18,
    "RACE_VOIDELF": 19,
    "RACE_VULPERA": 20,
    "RACE_LIGHTFORGEDDRAENEI": 21,
    "RACE_ZANDALARITROLL": 22,
    "RACE_DARKIRONDWARF": 23,
    "RACE_BROKEN_ALLIANCE": 24,
    "RACE_FORSAKEN": 25,
    "RACE_PANDAREN_HORDE": 26,
    "RACE_BROKEN_HORDE": 27,
    "RACE_DRACTHYR": 28,
}


def parse_race_enum(source):
    enum_body = re.search(r"enum\s+Races\s*:\s*uint8\s*\{(.*?)\};", source, re.DOTALL)
    if enum_body is None:
        enum_body = re.search(r"enum\s+Races\s*\{(.*?)\};", source, re.DOTALL)
    if enum_body is None:
        raise AssertionError("Races enum not found")

    return {
        name: int(value)
        for name, value in re.findall(r"\b(RACE_[A-Z0-9_]+)\s*=\s*(\d+)", enum_body.group(1))
    }


class PlayableRaceContractTest(unittest.TestCase):
    def test_custom_race_enum_assignments_match_contract(self):
        actual = parse_race_enum(SHARED_DEFINES.read_text(encoding="utf-8"))
        self.assertEqual(
            {name: actual.get(name) for name in EXPECTED_RACE_MAP},
            EXPECTED_RACE_MAP,
        )

    def test_registry_contains_required_playable_race_entries(self):
        registry = json.loads(RACE_REGISTRY.read_text(encoding="utf-8"))
        entries = {entry["id"]: entry for entry in registry["playable"]}

        self.assertEqual(entries[18]["faction"], "alliance")
        self.assertEqual(entries[20]["faction"], "horde")
        self.assertEqual(entries[26]["faction"], "horde")
        self.assertEqual(registry["classes"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 11])

    def test_playerbots_has_no_legacy_numeric_race_cutoff(self):
        source = PLAYERBOT_FACTORY.read_text(encoding="utf-8")
        self.assertNotRegex(source, r"race\s*>\s*RACE_BROKEN_PLAYER")

    def test_playerbots_race_allowlist_matches_contract(self):
        source = PLAYERBOT_FACTORY.read_text(encoding="utf-8")
        helper = re.search(
            r"bool\s+IsSupportedRandomBotRace\s*\(uint8\s+race\)\s*\{(.*?)\n\}\n\}",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(helper)

        enum_values = parse_race_enum(SHARED_DEFINES.read_text(encoding="utf-8"))
        supported_names = re.findall(r"case\s+(RACE_[A-Z0-9_]+)\s*:", helper.group(1))
        supported_ids = {enum_values[name] for name in supported_names}
        expected_supported_ids = set(range(1, 15)) | {18, 20}
        self.assertEqual(supported_ids, expected_supported_ids)

        deferred_ids = set(range(15, 29)) - expected_supported_ids
        self.assertEqual(supported_ids & deferred_ids, set())


class SqlMigrationContractTest(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SQL_MIGRATION.is_file())

    def test_corrective_migration_exists(self):
        self.assertTrue(SQL_MIGRATION.is_file())

    def test_corrective_migration_reports_character_counts_for_all_checked_ids(self):
        source = SQL_MIGRATION.read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r"(?s)SELECT\s+race\s*,\s*COUNT\(\*\).*?FROM\s+acore_characters\.characters"
            r".*?WHERE\s+race\s+IN\s*\(\s*15\s*,\s*18\s*,\s*20\s*,\s*26\s*\)"
            r".*?GROUP\s+BY\s+race.*?ORDER\s+BY\s+race",
        )

    def test_corrective_migration_reports_race_rows_for_all_checked_ids(self):
        source = SQL_MIGRATION.read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r"(?s)SELECT\s+ID\s*,\s*Flags\s*,\s*FactionID\s*,\s*Alliance\s*,\s*BaseLanguage\s*,"
            r"\s*MaleDisplayId\s*,\s*FemaleDisplayId.*?FROM\s+chrraces_dbc"
            r".*?WHERE\s+ID\s+IN\s*\(\s*15\s*,\s*18\s*,\s*20\s*,\s*26\s*\)"
            r".*?ORDER\s+BY\s+ID",
        )

    def test_corrective_migration_reports_target_faction_alliance_language_mismatches(self):
        source = SQL_MIGRATION.read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r"(?s)SELECT\s+expected\.ID.*?expected\.FactionID.*?actual\.FactionID.*?"
            r"expected\.Alliance.*?actual\.Alliance.*?expected\.BaseLanguage.*?"
            r"actual\.BaseLanguage.*?FROM\s+\(.*?SELECT\s+18\s+AS\s+ID\s*,\s*1\s+AS\s+FactionID\s*,\s*"
            r"0\s+AS\s+Alliance\s*,\s*7\s+AS\s+BaseLanguage.*?UNION\s+ALL.*?"
            r"SELECT\s+20\s+AS\s+ID\s*,\s*2\s+AS\s+FactionID\s*,\s*1\s+AS\s+Alliance\s*,\s*"
            r"1\s+AS\s+BaseLanguage.*?LEFT\s+JOIN\s+chrraces_dbc.*?"
            r"actual\.FactionID\s*<>\s*expected\.FactionID.*?"
            r"actual\.Alliance\s*<>\s*expected\.Alliance.*?"
            r"actual\.BaseLanguage\s*<>\s*expected\.BaseLanguage",
        )

    def test_corrective_migration_uses_idempotent_playability_flag_updates(self):
        source = SQL_MIGRATION.read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r"(?s)UPDATE\s+chrraces_dbc.*?SET\s+Flags\s*=\s*Flags\s*-\s*\(Flags\s*&\s*1\)"
            r".*?WHERE\s+ID\s+IN\s*\(\s*18\s*,\s*20\s*\)\s+AND\s*\(Flags\s*&\s*1\)\s*=\s*1",
        )
        self.assertRegex(
            source,
            r"(?s)UPDATE\s+chrraces_dbc.*?SET\s+Flags\s*=\s*Flags\s*\|\s*1"
            r".*?WHERE\s+ID\s*=\s*26\s+AND\s*\(Flags\s*&\s*1\)\s*=\s*0",
        )

    def test_corrective_migration_does_not_mutate_character_data(self):
        source = SQL_MIGRATION.read_text(encoding="utf-8")
        self.assertNotRegex(source, r"\b(?:INSERT|UPDATE|DELETE|REPLACE)\b[^;]*\bcharacters\b")

    def test_corrective_migration_reports_missing_starting_data_without_mutation(self):
        source = SQL_MIGRATION.read_text(encoding="utf-8")
        for table in (
            "playercreateinfo",
            "playercreateinfo_item",
            "playercreateinfo_action",
            "player_race_stats",
            "charstartoutfit_dbc",
        ):
            self.assertRegex(source, rf"(?s)SELECT.*?(?:FROM|JOIN)\s+{table}")
        self.assertIn("RaceID", source)
        self.assertIn("ClassID", source)
        self.assertIn("SexID", source)
        self.assertIn("player_race_stats", source)
        self.assertRegex(source, r"(?s)SELECT.*?(?:FROM|JOIN)\s+playercreateinfo_spell_custom.*?racemask")
        self.assertRegex(source, r"(?s)SELECT.*?(?:FROM|JOIN)\s+skillraceclassinfo_dbc.*?RaceMask")
        self.assertGreaterEqual(len(re.findall(r"missing", source, re.IGNORECASE)), 3)


if __name__ == "__main__":
    unittest.main()
