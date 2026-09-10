import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_DEFINES = ROOT / "src/server/shared/SharedDefines.h"
RACE_REGISTRY = ROOT / "modules/mod-custom-server/data/races/race_registry.json"
PLAYERBOT_FACTORY = ROOT / "modules/mod-playerbots/src/Bot/Factory/RandomPlayerbotFactory.cpp"


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


if __name__ == "__main__":
    unittest.main()
