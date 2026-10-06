"""Contract tests for the focused Ogre (60) / Furbolg (61) race pack.

These exercise the staged contract without touching the live client: the DBC merges are
recomputed in memory from the live archives, the model repairs run on staged copies, and
the Glue/SQL/config artefacts are checked against the handoff's stated contract.
"""

from __future__ import annotations

import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ogre_furbolg_race_pack as pack  # noqa: E402


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.allocation = pack.load_allocation()

    def test_race_ids_reserved(self):
        self.assertEqual(self.allocation["race_ids"]["ogre"], [60])
        self.assertEqual(self.allocation["race_ids"]["furbolg"], [61])

    def test_allocation_ranges_cover_new_rows(self):
        ranges = self.allocation["dbc_ranges"]
        self.assertGreaterEqual(ranges["CreatureDisplayInfo"][1], 60056)
        self.assertGreaterEqual(ranges["CharSections"][1], 1100999)
        self.assertGreaterEqual(ranges["CharStartOutfit"][1], 22039)
        self.assertGreaterEqual(ranges["NameGen"][1], 65999)

    def test_registry_entries(self):
        registry = json.loads(
            (ROOT / "modules/mod-custom-server/data/races/race_registry.json").read_text(encoding="utf-8"))
        by_id = {entry["id"]: entry for entry in registry["playable"]}
        self.assertEqual(by_id[60]["faction"], "horde")
        self.assertEqual(by_id[60]["legacy_mask_race"], 2)
        self.assertEqual(by_id[60]["start_profile"], "durotar")
        self.assertEqual(by_id[61]["faction"], "alliance")
        self.assertEqual(by_id[61]["legacy_mask_race"], 4)
        self.assertEqual(by_id[61]["start_profile"], "teldrassil")
        for race in (60, 61):
            self.assertEqual(by_id[race]["supported_genders"], [0, 1])

    def test_enum_names_are_exact(self):
        self.assertEqual(pack.spec("ogre")["enum"], "RACE_OGRE_HORDE")
        self.assertEqual(pack.spec("furbolg")["enum"], "RACE_FURBOLG_ALLIANCE")


class ManifestTests(unittest.TestCase):
    def test_manifests_match_constants(self):
        for entry in pack.RACE_SPECS:
            manifest = json.loads((pack.CONFIG_ROOT / f"{entry['slug']}.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["race_id"], entry["race_id"])
            self.assertEqual(manifest["client_file_string"], entry["client_file_string"])
            self.assertEqual(manifest["glue_token"], "OGREHORDE" if entry["slug"] == "ogre" else "FURBOLG")
            self.assertEqual(manifest["legacy_mask_race"], entry["legacy_mask_race"])
            self.assertEqual(sorted(manifest["dependencies"]), sorted(pack.PINNED_DEPENDENCIES))

    def test_furbolg_shares_one_body(self):
        models = pack.MODELS["furbolg"]
        self.assertEqual(models["male"]["path"], models["female"]["path"])
        self.assertNotEqual(models["male"]["display_id"], models["female"]["display_id"])


class ModelRepairTests(unittest.TestCase):
    def test_furbolg_sequence_flags(self):
        payload = (pack.READY / "Furbolg/Character/Furbolg/furbolgrace.m2").read_bytes()
        repaired, report = pack.repair_furbolg_sequences(payload)
        self.assertEqual({k: v["after"] for k, v in report.items()}, pack.FURBOLG_EMBEDDED_SEQUENCES)
        # Only the four flag words change.
        self.assertEqual(len(repaired), len(payload))
        changed = [i for i in range(len(payload)) if repaired[i] != payload[i]]
        allowed = {v["offset"] + o for v in report.values() for o in range(4)}
        self.assertTrue(set(changed) <= allowed)
        self.assertEqual(pack.repair_furbolg_sequences(repaired)[0], repaired)

    def test_ogre_female_skin_palette(self):
        path = pack.READY / "Ogre/Character/Ogre/Female/ogrefemale00.skin"
        repaired, detail = pack.repair_ogre_female_skin(path.read_bytes())
        self.assertEqual(detail["declared"], 256)
        self.assertEqual(detail["largest"], 66)
        self.assertEqual(struct.unpack_from("<I", repaired, 0x2C)[0], 66)
        # Idempotent: a repaired header is accepted unchanged.
        again, detail2 = pack.repair_ogre_female_skin(repaired)
        self.assertEqual(again, repaired)
        self.assertFalse(detail2["changed"])


class GluePatchTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {}
        for name in pack.GLUE_PATCHERS:
            self.baseline[name] = (ROOT / ".agents/plans/ogre-furbolg-deepseek/baseline-glue" / name).read_bytes()

    def test_patches_are_idempotent_and_present(self):
        patched = pack.build_glue(self.baseline)
        for name in ("CharacterInfo.lua", "CharacterCreate.lua", "GlueStrings.lua", "GlueParent.lua",
                     "CharacterSelect.lua", "ECS_Schema.lua"):
            text = patched[name].decode("utf-8")
            self.assertIn("OGREHORDE", text)
            self.assertIn("FURBOLG", text)
        self.assertIn("[60] = { glueString=\"OGREHORDE\"", patched["CharacterInfo.lua"].decode())
        self.assertIn("[61] = { glueString=\"FURBOLG\"", patched["CharacterInfo.lua"].decode())
        self.assertIn("OGREHORDE_MALE", patched["CharacterCreate.lua"].decode())
        self.assertIn("[60] = {name=\"Ogre\", faction=2, artKey=\"OgreHorde\"}",
                      patched["ECS_Schema.lua"].decode())
        self.assertIn("(race >= 54 and race <= 61)", patched["ECS_Integrate.lua"].decode())
        # Re-running the patchers is a no-op.
        twice = pack.build_glue(patched)
        self.assertEqual(twice, patched)

    def test_freeborn_and_native_blocks_survive(self):
        patched = pack.build_glue(self.baseline)
        create = patched["CharacterCreate.lua"].decode()
        self.assertIn("freeborn-third-team", create)


class SqlTests(unittest.TestCase):
    def test_revision_exists(self):
        files = sorted((ROOT / "data/sql/updates/pending_db_world").glob("rev_2026100408*.sql"))
        self.assertTrue(files, "the pending-db-world revision is missing")
        text = files[-1].read_text(encoding="utf-8")
        for race in (60, 61):
            self.assertIn(f"`ID` = {race}", text)
        self.assertIn("player_totem_model", text)
        self.assertIn("`RaceID` = 11", text)  # Furbolg totems come from Draenei
        self.assertIn("669, 'Language Orcish'", text)
        self.assertIn("668, 'Language Common'", text)
        self.assertFalse(text.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()