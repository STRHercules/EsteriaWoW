from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "src/server/shared/SharedDefines.h"
OBJECT_MGR = ROOT / "src/server/game/Globals/ObjectMgr.cpp"
WORLD_DB_H = ROOT / "src/server/database/Database/Implementation/WorldDatabase.h"
WORLD_DB_CPP = ROOT / "src/server/database/Database/Implementation/WorldDatabase.cpp"
PLAYERBOT_FACTORY = ROOT / "modules/mod-playerbots/src/Bot/Factory/RandomPlayerbotFactory.cpp"
PLAYERBOT_AI = ROOT / "modules/mod-playerbots/src/Bot/PlayerbotAI.cpp"
PLAYERBOT_REVIVE = ROOT / "modules/mod-playerbots/src/Ai/Base/Actions/ReviveFromCorpseAction.cpp"
REGISTRY = ROOT / "modules/mod-custom-server/data/races/race_registry.json"
ALLOCATION = ROOT / "data/retroported-races/allocation.json"
MAGHAR = ROOT / "data/retroported-races/maghar.json"
PHASE0_SQL = ROOT / "data/sql/updates/pending_db_world/rev_20260929001000000.sql"
MAGHAR_SQL = ROOT / "data/sql/updates/pending_db_world/rev_20260929002000000.sql"
COMPOSE = ROOT / "docker-compose.override.yml"
RACE_RUNTIME = ROOT / "wxl-races-patcher/DarkfallenCharacterSelect.cpp"


class RetroportedRaceContractTests(unittest.TestCase):
    def test_reserved_race_ids_and_compatibility_aliases(self) -> None:
        source = SHARED.read_text(encoding="utf-8")
        expected = {
            "RACE_MAGHAR_ORC": 45,
            "RACE_HIGHMOUNTAIN_TAUREN": 46,
            "RACE_MECHAGNOME": 47,
            "RACE_EARTHEN_ALLIANCE": 48,
            "RACE_EARTHEN_HORDE": 49,
            "RACE_HARANIR_ALLIANCE": 50,
            "RACE_HARANIR_HORDE": 51,
            "RACE_SKYBORNE_ALLIANCE": 52,
            "RACE_SKYBORNE_HORDE": 53,
        }
        for name, race_id in expected.items():
            self.assertRegex(source, rf"\b{name}\s*=\s*{race_id}\b")
        self.assertIn("GetLegacyMaskRaceForRace", source)
        self.assertIn("GetVisualBaseRaceForRace", source)
        self.assertIn("GetPairedRaceForRace", source)
        self.assertIn("case RACE_MAGHAR_ORC:          return RACE_ORC;", source)
        self.assertIn("case RACE_EARTHEN_ALLIANCE:  return RACE_EARTHEN_HORDE;", source)
        self.assertIn("case RACE_SKYBORNE_HORDE:    return RACE_SKYBORNE_ALLIANCE;", source)

    def test_registry_keeps_npc_and_darkfallen_contracts(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        npc_ids = {row["id"] for row in registry["npc_only"]}
        self.assertEqual(npc_ids, set(range(32, 43)))
        playable = {row["id"]: row for row in registry["playable"]}
        self.assertEqual(playable[43]["species_key"], "darkfallen")
        self.assertEqual(playable[44]["species_key"], "darkfallen")
        self.assertEqual(playable[45]["species_key"], "maghar_orc")
        self.assertEqual(playable[45]["legacy_mask_race"], 2)
        self.assertEqual(playable[45]["visual_base_race"], 2)

    def test_allocation_reserves_only_new_playable_ids(self) -> None:
        allocation = json.loads(ALLOCATION.read_text(encoding="utf-8"))
        race_ids = [value for values in allocation["race_ids"].values() for value in values]
        self.assertEqual(sorted(race_ids), list(range(45, 54)))
        self.assertEqual(len(race_ids), len(set(race_ids)))
        self.assertFalse(set(race_ids) & set(range(32, 45)))
        display_range = allocation["dbc_ranges"]["CreatureDisplayInfo"]
        self.assertEqual(display_range, [60030, 60047])
        self.assertLessEqual(display_range[1], 0xFFFF)
        maghar_displays = allocation["race_allocations"]["maghar"]["CreatureDisplayInfo"]
        self.assertEqual(maghar_displays, {"male": 60030, "female": 60031})

    def test_exact_race_startup_tables_are_loaded_with_prepared_statements(self) -> None:
        object_mgr = OBJECT_MGR.read_text(encoding="utf-8")
        world_db_h = WORLD_DB_H.read_text(encoding="utf-8")
        world_db_cpp = WORLD_DB_CPP.read_text(encoding="utf-8")
        sql = PHASE0_SQL.read_text(encoding="utf-8")
        statements = {
            "custom_race_start_skill": "WORLD_SEL_CUSTOM_RACE_START_SKILL",
            "custom_race_start_skill_exclude": "WORLD_SEL_CUSTOM_RACE_START_SKILL_EXCLUDE",
            "custom_race_start_spell": "WORLD_SEL_CUSTOM_RACE_START_SPELL",
            "custom_race_start_spell_exclude": "WORLD_SEL_CUSTOM_RACE_START_SPELL_EXCLUDE",
        }
        for table, statement in statements.items():
            self.assertIn(f"`{table}`", sql)
            self.assertIn(statement, world_db_h)
            self.assertIn(f"PrepareStatement({statement}", world_db_cpp)
            self.assertIn(statement, object_mgr)
        self.assertIn("IsExtendedPlayableRace(race)", object_mgr)
        self.assertIn("exactSpellExclusions", object_mgr)
        self.assertIn("exactSkillExclusions", object_mgr)

    def test_playerbots_use_extended_race_mask_helper_and_support_maghar(self) -> None:
        factory = PLAYERBOT_FACTORY.read_text(encoding="utf-8")
        ai = PLAYERBOT_AI.read_text(encoding="utf-8")
        revive = PLAYERBOT_REVIVE.read_text(encoding="utf-8")
        self.assertIn("case RACE_MAGHAR_ORC:", factory)
        self.assertIn("GetRaceMaskForRace(race)", factory)
        self.assertIn("GetRaceMaskForRace(race)", ai)
        self.assertIn("GetRaceMaskForRace(race)", revive)
        combined = factory + ai + revive
        self.assertNotRegex(combined, r"uint32\(1\)\s*<<\s*\(race\s*-\s*1\)")

    def test_maghar_uses_new_spells_and_excludes_orc_racials(self) -> None:
        manifest = json.loads(MAGHAR.read_text(encoding="utf-8"))
        self.assertEqual(manifest["race_ids"], [45])
        self.assertEqual(manifest["racial_spells"], [110100, 110101, 110102, 110103])
        self.assertEqual(manifest["racial_spell_donor_ids"], [110001, 110002, 110003, 110004])
        sql = MAGHAR_SQL.read_text(encoding="utf-8")
        for spell_id in manifest["racial_spells"]:
            self.assertIn(str(spell_id), sql)
        for spell_id in manifest["legacy_racial_spell_exclusions"]:
            self.assertRegex(sql, rf"\b{spell_id}\b")
        self.assertNotIn("(@MAGHAR, 0, 110001", sql)

    def test_maghar_runtime_does_not_overwrite_native_charsections_index(self) -> None:
        source = RACE_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("kHairCustomizationCategory = 3", source)
        self.assertIn("ApplyRuntimeCustomizationCounts();", source)
        self.assertIn("Do not mutate Mag'har's native customization table here", source)
        self.assertNotIn("kMagharNativeRaceSlot", source)
        self.assertNotIn("kMagharExactRaceId", source)
        self.assertNotIn("SetCustomizationCategoryCount", source)
        self.assertNotIn("magharRaceSlots", source)
        self.assertNotIn("Maghar_CustomizationRouter", source)
        self.assertNotIn("combinedValue", source)
        self.assertNotIn("kCurrentSkinColorOffset", source)
        self.assertIn('LogCharacterCreateCustomizationState("stock-cycle")', source)

    def test_server_mounts_full_standard_retroported_race_dbcs(self) -> None:
        compose = COMPOSE.read_text(encoding="utf-8")
        for table in (
            "ChrRaces",
            "CharStartOutfit",
            "CharSections",
            "BarberShopStyle",
            "CreatureDisplayInfo",
            "CreatureModelData",
            "Spell",
        ):
            self.assertIn(
                f"./modules/mod-custom-server/data/dbc/retroported-races/{table}.dbc:/azerothcore/env/dist/data/dbc/{table}.dbc:ro",
                compose,
            )
        self.assertNotIn(
            "./modules/mod-custom-server/data/dbc-continuations:/azerothcore/env/dist/data/dbc-continuations:ro",
            compose,
        )
        self.assertIn(
            "./modules/mod-custom-server/data/dbc-continuations/FactionTemplate.dbc1-freeborn:/azerothcore/env/dist/data/dbc-continuations/FactionTemplate.dbc1-freeborn:ro",
            compose,
        )


if __name__ == "__main__":
    unittest.main()
