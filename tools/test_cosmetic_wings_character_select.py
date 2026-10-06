"""Small resolver checks; the native harness exercises the actual packet parser and ownership."""

import copy
import struct
import unittest

from cosmetic_wings_character_select import catalog_records


class WingCatalogTests(unittest.TestCase):
    def test_state_attachment_resolution_and_rejection(self):
        spell = [0] * 234
        spell[0], spell[131] = 970340, 30240
        visual = [0] * 32
        visual[0], visual[4] = 30240, 21040
        tables = {
            "Spell": {970340: spell},
            "SkillLineAbility": {1: [1, 779, 970340], 2: [2, 777, 123]},
            "SpellVisual": {30240: visual},
            "SpellVisualKitModelAttach": {1: [1, 21040, 8300, 16, 0, 0, 0, 0, 0, 0]},
            "SpellVisualEffectName": {8300: ([8300, 0, 1, 0, 0x3F800000, 0, 0], b"\0wings.mdx\0")},
        }
        record, = catalog_records(tables)
        self.assertEqual((record["spell"], record["model"], record["scale"]), (970340, "wings.mdx", 1))
        for value in (float("nan"), float("inf"), 0.0, -1.0, 101.0):
            changed = copy.deepcopy(tables)
            changed["SpellVisualEffectName"][8300][0][4] = struct.unpack("<I", struct.pack("<f", value))[0]
            with self.assertRaises(ValueError):
                catalog_records(changed)
        changed = copy.deepcopy(tables)
        changed["SpellVisualKitModelAttach"][1][4] = 1
        with self.assertRaises(ValueError):
            catalog_records(changed)
        changed = copy.deepcopy(tables)
        changed["SpellVisualKitModelAttach"][1][3] = 57
        with self.assertRaises(ValueError):
            catalog_records(changed)
        changed = copy.deepcopy(tables)
        changed["SpellVisualKitModelAttach"][2] = changed["SpellVisualKitModelAttach"][1].copy()
        with self.assertRaises(ValueError):
            catalog_records(changed)


if __name__ == "__main__":
    unittest.main()
