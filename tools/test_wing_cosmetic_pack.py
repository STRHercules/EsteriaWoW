"""Offline checks for the cosmetic-wings pilot builder (no MPQ or client required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cars_mount_pack import Wdbc  # noqa: E402
from cars_mount_pack import build_wdbc  # noqa: E402
from wing_cosmetic_pack import (  # noqa: E402
    client_skill_race_class_row,
    DBC_LAYOUT,
    EFFECT_NAME_ID,
    KIT_ATTACH_ID,
    KIT_ID,
    SKILL_LINE,
    SKILL_LINE_CATEGORY,
    SKILL_LINE_ICON,
    SKILL_LINE_NAME,
    SPELL_COLUMNS,
    SPELL_ID,
    VISUAL_ID,
    build_continuations,
    skill_line_ability_row,
    skill_line_row,
    spell_row_for_pilot,
    spell_sql_row,
    sql_text,
)


def template_row() -> list:
    row = [0] * 234
    row[0] = 6606
    row[4] = 0x08800180  # DO_NOT_DISPLAY | DO_NOT_LOG | ALLOW_CAST_WHILE_DEAD | ALLOW_WHILE_SITTING
    row[5] = 0x10000020
    row[28] = 1
    row[32] = 0x4000A
    row[35] = 101
    row[39] = 1
    row[40] = 21
    row[46] = 1
    row[68] = 0xFFFFFFFF
    row[71] = 6
    row[74] = 1
    row[86] = 1
    row[95] = 4
    row[131] = 308
    row[133] = 153
    row[136] = 1
    row[216] = row[217] = row[218] = 0x3F800000
    row[225] = 1
    return row


class WingPilotTest(unittest.TestCase):
    def test_pilot_row_is_visible_castable_and_does_not_sit(self):
        row = spell_row_for_pilot(template_row())
        self.assertEqual(row[0], SPELL_ID)
        self.assertEqual((row[131], row[132]), (VISUAL_ID, 0))
        self.assertEqual(row[4], 0x08800000)
        self.assertFalse(row[4] & 0x80, "DO_NOT_DISPLAY must be cleared or the client hides the spell")
        self.assertFalse(row[5] & 0x10000000, "NO_AURA_ICON must be cleared or the buff is invisible")
        self.assertEqual(row[32], 0, "NOT_SEATED would make the core sit the caster")
        self.assertEqual((row[40], row[95], row[71]), (21, 4, 6))
        self.assertEqual(row[136], 0)

    def test_sql_row_carries_the_cleaned_fields(self):
        row = spell_row_for_pilot(template_row())
        values = dict(zip(SPELL_COLUMNS, spell_sql_row(row)))
        self.assertEqual(values["Attributes"], 0x08800000)
        self.assertEqual(values["AuraInterruptFlags"], 0)
        self.assertEqual(values["SpellVisualID_1"], VISUAL_ID)
        self.assertEqual((values["EffectAura_1"], values["DurationIndex"]), (4, 21))
        self.assertEqual(values["Name_Lang_enUS"], "Cosmetic Wings (Pilot)")
        text = sql_text(row)
        self.assertIn(f"DELETE FROM `spell_dbc` WHERE `ID` IN ({SPELL_ID});", text)
        self.assertIn("skillline_dbc", text)
        self.assertIn("playercreateinfo_skills", text)

    def test_merge_preserves_the_base_row_order(self):
        # SkillRaceClassInfo copies are ordered by SkillID (row ids are not sorted); sorting by id
        # there is what made every spellbook tab disappear into General.
        from wing_cosmetic_pack import merge_table

        rows = [
            [100, 10, 0xFFFFFFFF, 0x5FF, 2, 0, 0, 0],
            [101, 20, 0xFFFFFFFF, 0x5FF, 2, 0, 0, 0],
            [50, 30, 0xFFFFFFFF, 0x5FF, 2, 0, 0, 0],
        ]
        base = build_wdbc(rows, 8, 32)
        extra = build_wdbc([[990900, 25, 0xFFFFFFFF, 0x5FF, 2, 0, 0, 0]], 8, 32)
        merged = Wdbc(merge_table(base, extra, "SkillRaceClassInfo"))
        self.assertEqual([row[1] for row in merged.rows], [10, 20, 25, 30])
        self.assertEqual([row[0] for row in merged.rows], [100, 101, 990900, 50])

    def test_skill_line_row_names_the_cosmetics_tab(self):
        row = skill_line_row([0] * 56)
        self.assertEqual((row[0], row[1], row[37]), (SKILL_LINE, SKILL_LINE_CATEGORY, SKILL_LINE_ICON))
        entries = build_continuations(
            {
                "SpellVisualEffectName": [EFFECT_NAME_ID] + [0] * 6,
                "SpellVisualKit": [KIT_ID] + [0] * 37,
                "SpellVisualKitModelAttach": [KIT_ATTACH_ID, KIT_ID, EFFECT_NAME_ID, 16, 0, 0, 0, 0, 0, 0],
                "SpellVisual": [VISUAL_ID, 0, 0, 0, KIT_ID] + [0] * 27,
                "Spell": spell_row_for_pilot(template_row()),
                "SkillLineAbility": skill_line_ability_row(),
                "SkillRaceClassInfo": client_skill_race_class_row(),
                "SkillLine": row,
            }
        )
        lines = Wdbc(entries["DBFilesClient/SkillLine.dbc1-wings"])
        self.assertEqual(lines.text(lines.row(SKILL_LINE)[3]), SKILL_LINE_NAME)
        effect = Wdbc(entries["DBFilesClient/SpellVisualEffectName.dbc1-wings"])
        self.assertEqual(effect.text(effect.row(EFFECT_NAME_ID)[2]), r"sirus\Wings1.mdx")
        attach = Wdbc(entries["DBFilesClient/SpellVisualKitModelAttach.dbc1-wings"]).row(KIT_ATTACH_ID)
        self.assertEqual((attach[1], attach[2], attach[3]), (KIT_ID, EFFECT_NAME_ID, 16))
        src = Wdbc(entries["DBFilesClient/SkillRaceClassInfo.dbc1-wings"]).row(990900)
        self.assertEqual((src[1], src[3]), (SKILL_LINE, 0x5FF))
        sla = Wdbc(entries["DBFilesClient/SkillLineAbility.dbc1-wings"]).row(SPELL_ID)
        self.assertEqual(sla[1], SKILL_LINE)
        self.assertEqual(sla[4], 0x5FF, "ClassMask must carry every class bit or the client draws no tab")
        spell = Wdbc(entries["DBFilesClient/Spell.dbc1-wings"]).row(SPELL_ID)
        self.assertEqual((spell[131], spell[95], spell[71]), (VISUAL_ID, 4, 6))


if __name__ == "__main__":
    unittest.main()