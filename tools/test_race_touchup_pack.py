"""Regression checks for the observed talking-animation crash and selection metadata."""

import struct
import unittest
from pathlib import Path

from lupa import LuaRuntime
from wotlkconv.m2 import parse_m2

import expanded_appearance_pack as expansion
import race_touchup_pack as touchup
import retroported_race_pack as p
import skyborne_visual_pack as visuals


class RaceTouchupTests(unittest.TestCase):
    def test_external_animation_spans_are_not_rebased_into_the_model(self):
        for sex, file_id in (("male", 7478487), ("female", 7478494)):
            source = visuals.path_for(f"custom\\skyborne\\models\\creature\\unk_exp00_{file_id}\\{file_id}.m2")
            original = visuals.read_player_model(source)
            changed = parse_m2((expansion.ART / "custom/skyborne/expanded" / sex / f"{file_id}.m2").read_bytes())
            self.assertEqual(original.sequences, changed.sequences)
            for old_bone, new_bone in zip(original.bones, changed.bones):
                for kind in ("translation", "rotation", "scale"):
                    old, new = old_bone[kind], new_bone[kind]
                    if old.global_sequence >= 0:
                        continue
                    for index in old.external:
                        self.assertEqual(old.timestamp_spans[index], new.timestamp_spans[index], (sex, kind, index))
                        if index < len(old.value_spans):
                            self.assertEqual(old.value_spans[index], new.value_spans[index], (sex, kind, index))
            if sex == "female":
                self.assertEqual(changed.bones[1]["rotation"].timestamp_spans[144], (58, 1024))
                companion = source.with_name(source.stem + "0060-01.anim").read_bytes()
                if companion[:4] in (b"AFM2", b"AFSA", b"ASFM", b"ASFA"):
                    self.fail("Talking animation needs unwrapping before native playback")
                timestamps = struct.unpack_from("<58I", companion, 1024)
                self.assertEqual(list(timestamps), sorted(timestamps))
                self.assertLessEqual(timestamps[-1], changed.sequences[144]["duration"])

    def test_actual_race_ids_resolve_even_with_a_stock_or_death_knight_model(self):
        lua = LuaRuntime()
        for name in ("ECS_Constants.lua", "ECS_Schema.lua", "ECS_Data.lua", "ECS_Tooltip.lua"):
            original = (touchup.STAGE / name).read_text()
            lua.execute(touchup.patch(name, original))
        for race, sex, label, side, art in ((45, 0, "Mag'har Orc", 2, "MagharMale"),
                                           (52, 1, "Skyborn", 1, "SkyborneFemale"),
                                           (53, 1, "Skyborn", 2, "SkyborneHordeFemale")):
            fields = lua.table_from({1: "Alyssa Masterson", 2: race, 3: 2, 4: 1, 5: "Sunstrider Isle", 6: sex + 2})
            record = lua.globals().ECS.Data.FromFields(1, fields, lua.table_from({"model": "DEATHKNIGHT"}))
            self.assertEqual(record.raceName, label)
            self.assertEqual(record.factionID, side)
            self.assertTrue(record.raceKnown)
            self.assertTrue(record.portrait.endswith(art))
        x, y, *_ = lua.globals().ECS.Tooltip.ComputeAnchor(300, 200, 180, 80, 1024, 768)
        self.assertEqual(y, 210)
        x, y, *_ = lua.globals().ECS.Tooltip.ComputeAnchor(1000, 760, 180, 80, 1024, 768)
        self.assertTrue(0 <= x <= 844 and 0 <= y <= 688)

    def test_staged_ui_and_portraits_agree_between_archives(self):
        storm = p.Storm(p.DLL_DEFAULT)
        for name in (*touchup.ECS, "CharacterInfo.lua"):
            key = p.GLUE_ROOT + name
            a = p._read_archive_entry(storm, touchup.STAGE / "pack" / p.GLOBAL_ARCHIVE_REL, key)
            b = p._read_archive_entry(storm, touchup.STAGE / "pack" / p.LOCALE_ARCHIVE_REL, key)
            self.assertEqual(a, b, name)
        for _, sex, token, _ in touchup.icons.SOURCES:
            key = f"Interface\\Glues\\CharacterSelect\\ECS-Portrait-{token}{sex}.blp"
            a = p._read_archive_entry(storm, touchup.STAGE / "pack" / p.GLOBAL_ARCHIVE_REL, key)
            b = p._read_archive_entry(storm, touchup.STAGE / "pack" / p.LOCALE_ARCHIVE_REL, key)
            self.assertEqual(a, b, key)
            touchup.icons.portraits.validate_portrait(a, Path(key))


if __name__ == "__main__":
    unittest.main()
