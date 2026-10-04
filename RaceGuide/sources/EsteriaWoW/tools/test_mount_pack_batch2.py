from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import mount_pack_batch2 as batch2


class MountBatch2InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        batch2.configure_cars()
        cls.base = batch2.discover_base_mounts()
        cls.mounts = batch2.expand_variants(cls.base)
        batch2.validate_source_assets(cls.mounts)
        cls.records = batch2.apply_record_overrides(
            batch2.cars.build_mount_records(cls.mounts, batch2.BASELINE)
        )

    def test_inventory_is_exactly_42_base_and_71_records(self):
        self.assertEqual(len(self.base), 42)
        self.assertEqual(len(self.mounts), 71)
        self.assertEqual(len(self.records), 71)

    def test_excluded_models_are_not_present(self):
        stems = {mount.model.stem.casefold() for mount in self.base}
        self.assertTrue(batch2.EXCLUDED_MODEL_STEMS.isdisjoint(stems))

    def test_all_models_are_wotlk_v264_and_have_canonical_skin(self):
        for mount in self.mounts:
            self.assertEqual(mount.model_version, batch2.WOTLK_MODEL_VERSION, mount.model)
            expected = mount.model.parent / f"{mount.model.stem}00.skin"
            self.assertTrue(expected.is_file(), expected)

    def test_variant_texture_files_exist(self):
        for mount in self.mounts:
            if not mount.texture_overrides:
                continue
            available = {
                path.name.casefold()
                for path in mount.source_root.rglob("*")
                if path.is_file() and path.suffix.casefold() == ".blp"
            }
            for _, filename in mount.texture_overrides:
                self.assertIn(filename.casefold(), available, f"{mount.display_name}: {filename}")

    def test_ids_use_the_reserved_batch2_ranges(self):
        fields = {
            "spell_id": 201200,
            "spell_icon_id": 514800,
            "item_id": 901200,
            "item_display_id": 68800,
            "creature_id": 3460800,
            "display_id": 94500,
            "model_id": 5100,
        }
        for field, first in fields.items():
            values = [getattr(record, field) for record in self.records]
            self.assertEqual(values, list(range(first, first + 71)), field)

    def test_effect_misc_value_points_to_creature_entry(self):
        for record in self.records:
            self.assertEqual(record.spell_row[110], record.creature_id, record.mount.display_name)

    def test_flying_assignment_matches_approved_model_set(self):
        actual = {
            mount.model.stem.casefold()
            for mount in self.mounts
            if mount.model.stem.casefold() in batch2.FLYING_MODEL_STEMS
        }
        self.assertEqual(actual, batch2.FLYING_MODEL_STEMS)
        self.assertEqual(sum(m.model.stem.casefold() in batch2.FLYING_MODEL_STEMS for m in self.base), 29)

    def test_flying_mounts_use_conventional_seated_gryphon_template(self):
        self.assertEqual(batch2.FLYING_MOUNT_SPELL_TEMPLATE_ID, 32235)
        baseline = batch2.cars.Wdbc((batch2.BASELINE / "Spell.dbc").read_bytes()).row(32235)
        flying = next(
            record for record in self.records
            if record.mount.model.stem.casefold() == "gryphonmount_30thanniv"
        )
        self.assertEqual(flying.spell_row[95:98], tuple(baseline[95:98]))
        self.assertEqual(flying.spell_row[11], baseline[11])

    def test_celestial_cat_filedata_texture_is_rewritten_to_supplied_blp(self):
        celestial = next(mount for mount in self.base if mount.model.stem.casefold() == "celestialcatmount")
        entries = batch2.cars.collect_mount_entries(celestial, default_icon=b"")
        model = entries[celestial.client_model_path]
        type11 = [
            name.decode("ascii", errors="ignore").casefold()
            for _, texture_type, name in batch2.cars._m2_texture_records(model)
            if texture_type == 11
        ]
        self.assertEqual(len(type11), 1)
        self.assertNotEqual(type11[0], "unknown/5846547.blp")
        self.assertTrue(type11[0].endswith("celestialcatmount.blp"), type11[0])

    def test_infernal_texture_slots_match_retail_order(self):
        expected = {
            "Infernal": ("infernalmount_metal_red", "infernalmount_rock_red", "infernalmount_fx_purple"),
            "Infernal - Blue": ("infernalmount_metal_blue", "infernalmount_rock_blue", "infernalmount_fx_blue"),
            "Infernal - Green": ("infernalmount_metal_green", "infernalmount_rock_green", "infernalmount_fx_green"),
            "Infernal - Ice": ("infernalmount_metal_ice", "infernalmount_rock_ice", "infernalmount_fx_ice"),
            "Infernal - Lava": ("infernalmount_metal_lava", "infernalmount_rock_lava", "infernalmount_fx_lava"),
            "Infernal - Red": ("infernalmount_metal_red", "infernalmount_rock_red", "infernalmount_fx_purple"),
        }
        actual = {
            record.mount.display_name: record.texture_variations
            for record in self.records
            if record.mount.model.stem.casefold() == "infernalmount"
        }
        self.assertEqual(actual, expected)

    def test_kukulkan_is_downscaled(self):
        kukulkan = next(
            record for record in self.records if record.mount.model.stem.casefold() == "kukulkan"
        )
        self.assertAlmostEqual(batch2.cars._f32_from_u32(kukulkan.creature_display_row[4]), 0.3, places=6)

    def test_sql_is_additem_only_and_does_not_create_distribution_rows(self):
        sql = batch2.cars.render_mount_sql(self.records)
        self.assertIn("`item_template`", sql)
        self.assertIn("201200", sql)
        self.assertIn("901200", sql)
        self.assertIn("3460800", sql)
        self.assertNotIn("npc_vendor", sql.casefold())
        self.assertNotIn("creature_loot_template", sql.casefold())
        self.assertNotIn("quest_template", sql.casefold())
        # The live SQL overlay schema uses underscored CharacterPoints column names.
        normalized = sql.replace("`CharacterPoints1`", "`CharacterPoints_1`").replace(
            "`CharacterPoints2`", "`CharacterPoints_2`"
        )
        self.assertIn("`CharacterPoints_1`", normalized)
        self.assertIn("`CharacterPoints_2`", normalized)
        # Batch #2 must never delete the live batch-1 ID ranges as part of its own overlay.
        self.assertNotIn("135000", sql)
        self.assertNotIn("94300", sql)
        self.assertNotIn("5000", sql)


class NativeDbcTests(unittest.TestCase):
    def test_native_merge_replaces_same_id_on_rerun(self):
        base = batch2.cars.build_wdbc([[1, 11], [2, 22]], 2, 8)
        extra = batch2.cars.build_wdbc([[2, 222], [3, 33]], 2, 8)
        once = batch2.merge_wdbc_replace_rows(base, extra, "Synthetic")
        twice = batch2.merge_wdbc_replace_rows(once, extra, "Synthetic")
        table = batch2.cars.Wdbc(twice)
        self.assertEqual([row[0] for row in table.rows], [1, 2, 3])
        self.assertEqual(table.row(2)[1], 222)
        self.assertEqual(once, twice)

    def test_locale_z_outranks_root_z_and_patch_w(self):
        with tempfile.TemporaryDirectory() as temporary:
            data = Path(temporary)
            locale = data / "enUS"
            locale.mkdir()
            for path in (
                data / "Patch-W.MPQ",
                data / "patch-Z.MPQ",
                locale / "patch-enUS-Z.MPQ",
            ):
                path.write_bytes(b"")
            chain = batch2.client_archive_chain(data, "enUS")
            names = [str(path.relative_to(data)).replace("/", "\\").casefold() for path in chain]
            self.assertLess(names.index("enus\\patch-enus-z.mpq"), names.index("patch-z.mpq"))
            self.assertLess(names.index("patch-z.mpq"), names.index("patch-w.mpq"))


if __name__ == "__main__":
    unittest.main()
