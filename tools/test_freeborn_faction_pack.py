"""Contract test for the Freeborn player-hostility FactionTemplate rows.

Run:  python tools/test_freeborn_faction_pack.py
"""

from __future__ import annotations

import hashlib
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import freeborn_faction_pack as MOD  # noqa: E402

FACTION_DBC = MOD.REPO_ROOT / "modules" / "mod-Faction-Free" / "dbc" / "Faction.dbc"


def masks(row):
    return row[3], row[4], row[5]


def rep_capable(faction_id: int) -> bool:
    data = FACTION_DBC.read_bytes()
    _, count, fields, record_size, _ = struct.unpack_from("<4sIIII", data, 0)
    for index in range(count):
        row = struct.unpack_from(f"<{fields}I", data, 20 + index * record_size)
        if row[0] == faction_id:
            return struct.unpack("<i", struct.pack("<I", row[1]))[0] >= 0
    return False


def hostile_to(a, b) -> bool:
    """FactionTemplateEntry::IsHostileTo: enemy list first, then masks."""
    if b[1]:
        for value in a[6:10]:
            if value == b[1]:
                return True
        for value in a[10:14]:
            if value == b[1]:
                return False
    return bool(a[5] & b[3])


def friendly_to(a, b) -> bool:
    if a[1] == b[1]:
        return True
    if b[1]:
        for value in a[6:10]:
            if value == b[1]:
                return False
        for value in a[10:14]:
            if value == b[1]:
                return True
    return bool((a[4] & b[3]) or (a[3] & b[4]))


def reaction(a, b) -> str:
    if hostile_to(a, b):
        return "hostile"
    if friendly_to(a, b):
        return "friendly"
    if a[2] & 0x2000:
        return "hostile"
    return "neutral"


class FreebornFactionPackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_bytes = MOD.base_table_bytes(None)
        cls.full_bytes, cls.continuation_bytes = MOD.build_rows(cls.base_bytes)
        cls.base = MOD.parse_wdbc(cls.base_bytes).by_id
        cls.after = MOD.parse_wdbc(cls.full_bytes).by_id
        cls.freeborn = cls.after[MOD.FREEBORN_TEMPLATE_ID]

    def test_base_is_the_deployed_table(self):
        self.assertEqual(hashlib.sha256(self.base_bytes).hexdigest(), MOD.BASE_SHA256)

    def test_only_intended_rows_change(self):
        report = MOD.verify(self.base_bytes, self.full_bytes)
        self.assertEqual(report["added"], [MOD.FREEBORN_TEMPLATE_ID])
        self.assertEqual(sorted(report["modified"]), sorted(MOD.PLAYER_TEMPLATE_IDS))

    def test_untouched_rows_are_byte_identical(self):
        for template_id, row in self.base.items():
            if template_id in MOD.PLAYER_TEMPLATE_IDS:
                continue
            self.assertEqual(self.after[template_id], row, f"row {template_id} changed")

    def test_player_rows_only_gain_the_two_intended_bits(self):
        for template_id in MOD.PLAYER_TEMPLATE_IDS:
            before, after = self.base[template_id], self.after[template_id]
            self.assertEqual(after[3], before[3] | MOD.FREEBORN_GROUP_MASK)
            self.assertEqual(after[5], before[5] | MOD.PLAYER_MONSTER_HOSTILITY_BIT)
            self.assertEqual(after[:3] + (after[4],) + after[6:],
                             before[:3] + (before[4],) + before[6:])

    def test_freeborn_row_values(self):
        self.assertEqual(self.freeborn[1], MOD.FREEBORN_FACTION_ID)
        self.assertEqual(self.freeborn[2], MOD.FREEBORN_FLAGS)
        self.assertEqual(masks(self.freeborn),
                         (MOD.FREEBORN_OUR_MASK, MOD.FREEBORN_FRIENDLY_MASK, MOD.FREEBORN_HOSTILE_MASK))

    def test_freeborn_faction_has_no_reputation_and_is_unreferenced(self):
        """The reputation path must stay out of the way, and no other row may share the faction."""
        self.assertFalse(rep_capable(MOD.FREEBORN_FACTION_ID))
        for template_id, row in self.after.items():
            if template_id == MOD.FREEBORN_TEMPLATE_ID:
                continue
            self.assertNotEqual(row[1], MOD.FREEBORN_FACTION_ID,
                                f"row {template_id} shares the Freeborn faction")

    def test_freeborn_is_hostile_to_every_player_template_both_ways(self):
        for template_id in MOD.PLAYER_TEMPLATE_IDS:
            player = self.after[template_id]
            self.assertEqual(reaction(self.freeborn, player), "hostile")
            self.assertEqual(reaction(player, self.freeborn), "hostile")

    def test_freeborn_is_hostile_to_itself_and_to_monsters(self):
        self.assertEqual(reaction(self.freeborn, self.freeborn), "hostile")
        monster = self.after[14]  # "Monster": ourMask 8, hostileMask 1
        self.assertEqual(reaction(self.freeborn, monster), "hostile")
        self.assertEqual(reaction(monster, self.freeborn), "hostile")

    def test_freeborn_and_npcs_stay_friendly(self):
        for template_id in (11, 12, 57, 80):  # Stormwind guard/civilian, Ironforge, Darnassus
            npc = self.after[template_id]
            self.assertNotEqual(reaction(self.freeborn, npc), "hostile",
                                f"Freeborn -> template {template_id} became hostile")

    def test_players_are_not_hostile_to_each_other(self):
        """Regression guard: the new group bit must not enable friendly-fire."""
        for a_id in MOD.PLAYER_TEMPLATE_IDS:
            for b_id in MOD.PLAYER_TEMPLATE_IDS:
                if a_id == b_id:
                    continue
                self.assertNotEqual(reaction(self.after[a_id], self.after[b_id]), "hostile")
                self.assertNotEqual(reaction(self.after[b_id], self.after[a_id]), "hostile")

    def test_no_npc_gained_the_freeborn_group_bit(self):
        for template_id, row in self.after.items():
            if template_id == MOD.FREEBORN_TEMPLATE_ID or template_id in MOD.PLAYER_TEMPLATE_IDS:
                continue
            self.assertFalse(row[3] & MOD.FREEBORN_GROUP_MASK, f"row {template_id} gained the bit")

    def test_continuation_holds_only_the_changed_rows_and_reproduces_the_table(self):
        continuation = MOD.parse_wdbc(self.continuation_bytes)
        self.assertEqual(sorted(row[0] for row in continuation.records),
                         sorted(list(MOD.PLAYER_TEMPLATE_IDS) + [MOD.FREEBORN_TEMPLATE_ID]))
        merged = dict(self.base)
        for row in continuation.records:
            merged[row[0]] = row
        expected = MOD.parse_wdbc(self.full_bytes).by_id
        self.assertEqual(merged, expected)

    def test_continuation_bytes_match_the_table_it_was_built_from(self):
        self.assertEqual(hashlib.sha256(MOD.build_rows(self.base_bytes)[0]).hexdigest(),
                         hashlib.sha256(self.full_bytes).hexdigest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
