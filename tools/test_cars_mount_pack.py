import importlib.util
import struct
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("cars_mount_pack.py")
SPEC = importlib.util.spec_from_file_location("cars_mount_pack", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CarsMountPackTest(unittest.TestCase):
    @staticmethod
    def _m2_with_texture(version=264, texture=b"body.blp"):
        data = bytearray(0x70 + 16 + len(texture) + 1)
        data[:4] = b"MD20"
        struct.pack_into("<I", data, 4, version)
        struct.pack_into("<II", data, 0x50, 1, 0x70)
        struct.pack_into("<IIII", data, 0x70, 0, 0, len(texture) + 1, 0x80)
        data[0x80 : 0x80 + len(texture)] = texture
        data[0x80 + len(texture)] = 0
        return bytes(data)

    @staticmethod
    def _m2_with_blank_texture(version=264):
        return CarsMountPackTest._m2_with_blank_textures(version, (11,))

    @staticmethod
    def _m2_with_blank_textures(version=264, texture_types=(11, 12)):
        name_offset = 0x70 + len(texture_types) * 16
        data = bytearray(name_offset + 1)
        data[:4] = b"MD20"
        struct.pack_into("<I", data, 4, version)
        struct.pack_into("<II", data, 0x50, len(texture_types), 0x70)
        for index, texture_type in enumerate(texture_types):
            struct.pack_into("<IIII", data, 0x70 + index * 16, texture_type, 0, 1, name_offset)
        return bytes(data)

    @staticmethod
    def _mount_baseline(path):
        path.mkdir()
        spell = [0] * 234
        spell[0] = 23214
        spell[131] = 3339
        flying_spell = [0] * 234
        flying_spell[0] = 61309
        flying_spell[4], flying_spell[8], flying_spell[11] = 269844752, 67108864, 0
        flying_spell[31], flying_spell[32] = 31, 128
        flying_spell[71:74] = [6, 6, 6]
        flying_spell[74:77] = [0, 1, 1]
        flying_spell[80:83] = [0, 99, 279]
        flying_spell[95:98] = [78, 32, 207]
        flying_spell[116], flying_spell[131] = 3908, 12844
        item = [18776, 15, 5, 0xFFFFFFFF, 4, 25132, 0, 0]
        vehicle = [0] * 40
        vehicle[0], vehicle[7] = 318, 2804
        seat = [0] * 58
        seat[0], seat[1], seat[2] = 1541, 0x0200840F, 0
        seat[13], seat[14], seat[15], seat[16], seat[17], seat[18], seat[19] = 37, 38, 0xFFFFFFFF, 0, 0, 0, 0
        seat[26], seat[27], seat[28], seat[32], seat[41], seat[44], seat[45] = 37, 38, 39, 0xFFFFFFFF, 1, 0, 0
        (path / "Spell.dbc").write_bytes(MODULE.build_wdbc([spell, flying_spell], 234, 936))
        (path / "Item.dbc").write_bytes(MODULE.build_wdbc([item], 8, 32))
        (path / "ItemDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[68742] + [0] * 24], 25, 100))
        (path / "CreatureDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[94234] + [0] * 15], 16, 64))
        (path / "CreatureModelData.dbc").write_bytes(MODULE.build_wdbc([[4899] + [0] * 27], 28, 112))
        (path / "Vehicle.dbc").write_bytes(MODULE.build_wdbc([vehicle], 40, 160))
        (path / "VehicleSeat.dbc").write_bytes(MODULE.build_wdbc([seat], 58, 232))

    def test_car_texture_namespace_matches_model_namespace(self):
        for car in MODULE.CARS:
            self.assertEqual(
                MODULE.car_texture_namespace(car),
                f"Creature\\Cars\\{car.slug}\\",
            )

    def test_rewrite_m2_paths_keeps_size_and_offsets(self):
        source = b"MD20" + b"CREATURE\\GOBLINHOTROD\\GOBLINHOTROD_01.BLP\0" + b"tail"
        result = MODULE.rewrite_m2_paths(
            source,
            {
                b"CREATURE\\GOBLINHOTROD\\GOBLINHOTROD_01.BLP":
                b"C\\BENTLEY_01.BLP",
            },
        )
        self.assertEqual(len(result), len(source))
        self.assertTrue(result.startswith(b"MD20C\\BENTLEY_01.BLP\0"))
        self.assertTrue(result.endswith(b"tail"))


    def test_build_continuation_round_trips_rows_and_strings(self):
        data = MODULE.build_wdbc([[7, 12, 0]], 3, 12, {2: "Car"})
        self.assertEqual(data[:4], b"WDBC")
        self.assertEqual(struct.unpack_from("<4I", data, 4), (1, 3, 12, 5))
        self.assertEqual(data[20:32], struct.pack("<3I", 7, 12, 1))
        self.assertEqual(data[32:], b"\0Car\0")

    def test_discover_mounts_filters_non_wotlk_models_and_reports_rejections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            (root / "Creature").mkdir(parents=True)
            (root / "Creature" / "good.m2").write_bytes(b"MD20" + struct.pack("<I", 264))
            (root / "Creature" / "bad.m2").write_bytes(b"MD20" + struct.pack("<I", 272))

            mounts = MODULE.discover_mounts((root,))
            rejected = MODULE.rejected_models((root,))

            self.assertEqual([mount.model_version for mount in mounts], [264])
            self.assertEqual([item.model.name for item in rejected], ["bad.m2"])
            self.assertEqual(rejected[0].version, 272)

    def test_mount_ids_are_deterministic_and_unique(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            (root / "Creature").mkdir(parents=True)
            for name in ("zeta.m2", "alpha.m2"):
                (root / "Creature" / name).write_bytes(b"MD20" + struct.pack("<I", 264))

            first = MODULE.discover_mounts((root,))
            second = MODULE.discover_mounts((root,))
            first_ids = MODULE.mount_ids(first)
            second_ids = MODULE.mount_ids(second)

            self.assertEqual([mount.slug for mount in first], [mount.slug for mount in second])
            self.assertEqual(first_ids, second_ids)
            self.assertEqual(first_ids["creature"], (3460608, 3460609))
            for ids in first_ids.values():
                self.assertEqual(len(ids), len(set(ids)))

    def test_client_model_path_fits_creature_modeldata_name_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / ("very_long_mount_source_name_" * 3)
            model_dir = root / "Creature" / ("very_long_model_family_name_" * 2)
            model_dir.mkdir(parents=True)
            (model_dir / ("very_long_mount_model_name_" * 2 + ".m2")).write_bytes(b"MD20" + struct.pack("<I", 264))

            mount = MODULE.discover_mounts((root,))[0]

            self.assertLessEqual(len(mount.client_model_path), 100)

    def test_baseline_mount_display_ids_stay_inside_native_dbc_ranges(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(b"MD20" + struct.pack("<I", 264))
            baseline = Path(tmp) / "baseline"
            baseline.mkdir()
            (baseline / "ItemDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[68742] + [0] * 24], 25, 100))
            (baseline / "CreatureDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[94234] + [0] * 15], 16, 64))
            (baseline / "CreatureModelData.dbc").write_bytes(MODULE.build_wdbc([[4899] + [0] * 27], 28, 112))

            mounts = MODULE.discover_mounts((root,))
            ids = MODULE.mount_ids(mounts, baseline)

            self.assertLess(ids["item_display"][0], 68742)
            self.assertLess(ids["display"][0], 94234)
            self.assertLess(ids["model"][0], 4899)

    def test_merge_archive_entries_preserves_identical_and_rejects_conflicting_paths(self):
        existing = {r"Existing\Path.blp": b"same", "Keep.m2": b"old"}
        merged = MODULE.merge_archive_entries(existing, {"existing/path.BLP": b"same", "New.m2": b"new"})
        self.assertEqual(merged[r"Existing\Path.blp"], b"same")
        self.assertEqual(merged["New.m2"], b"new")

        with self.assertRaises(ValueError):
            MODULE.merge_archive_entries(existing, {"KEEP.M2": b"different"})

    def test_remove_existing_mount_entries_preserves_cars_and_unrelated_files(self):
        entries = {
            r"Creature\EsteriaMounts\old\old.m2": b"old",
            "DBFilesClient/CreatureModelData.dbc1-mounts": b"old dbc",
            r"Interface\Icons\INV_Mount_old.blp": b"old icon",
            r"Creature\Cars\Bentley\Bentley.m2": b"car",
            "Other/file.blp": b"other",
        }
        result = MODULE.remove_existing_mount_entries(entries)
        self.assertNotIn(r"Creature\EsteriaMounts\old\old.m2", result)
        self.assertNotIn("DBFilesClient/CreatureModelData.dbc1-mounts", result)
        self.assertNotIn(r"Interface\Icons\INV_Mount_old.blp", result)
        self.assertIn(r"Creature\Cars\Bentley\Bentley.m2", result)
        self.assertIn("Other/file.blp", result)

    def test_requested_texture_variants_are_appended_as_independent_mounts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Game_Boy_Mount_1.0" / "WotLK" / "Creature" / "GameBoyMount"
            root.mkdir(parents=True)
            (root / "GameBoyMount.m2").write_bytes(self._m2_with_blank_textures())
            (root / "GameBoyMount00.skin").write_bytes(b"skin")
            for name in (
                "GameBoyMount_Case_01.blp",
                "GameBoyMount_Screen_DonkeyKong.blp",
                "GameBoyMount_Screen_ZeldaDX.blp",
                "GameBoyMount_Screen_WarioLand.blp",
                "GameBoyMount_Screen_SuperMarioLand.blp",
                "GameBoyMount_Screen_PKMNYellow.blp",
                "GameBoyMount_Screen_PKMNSilver.blp",
                "GameBoyMount_Screen_PKMNRed.blp",
                "GameBoyMount_Screen_PKMNGreen.blp",
                "GameBoyMount_Screen_PKMNGold.blp",
                "GameBoyMount_Screen_PKMNBlue.blp",
                "GameBoyMount_Screen_Metroid2.blp",
                "GameBoyMount_Screen_MegaMan2.blp",
                "GameBoyMount_Screen_Kirby2.blp",
            ):
                (root / name).write_bytes(name.encode())

            base = MODULE.discover_mounts((Path(tmp) / "Game_Boy_Mount_1.0",))
            mounts = MODULE.expand_mount_variants(base)

            self.assertEqual(len(base), 1)
            self.assertEqual(len(mounts), 13)
            self.assertEqual([mount.slug for mount in mounts[:1]], [base[0].slug])
            self.assertEqual(len({mount.slug for mount in mounts}), 13)
            self.assertEqual(
                {mount.display_name for mount in mounts[1:]},
                {
                    "Game Boy Mount - Zelda DX",
                    "Game Boy Mount - Wario Land",
                    "Game Boy Mount - Super Mario Land",
                    "Game Boy Mount - Pokemon Yellow",
                    "Game Boy Mount - Pokemon Silver",
                    "Game Boy Mount - Pokemon Red",
                    "Game Boy Mount - Pokemon Green",
                    "Game Boy Mount - Pokemon Gold",
                    "Game Boy Mount - Pokemon Blue",
                    "Game Boy Mount - Metroid 2",
                    "Game Boy Mount - Mega Man 2",
                    "Game Boy Mount - Kirby 2",
                },
            )
            variant_entries = MODULE.collect_mount_entries(mounts[1])
            self.assertIn("ZeldaDX.blp", "".join(variant_entries))

    def test_flat_mounts_use_carpet_pose_without_vehicle_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            roots = []
            for package, model_stem in (("Game_Boy_Mount_1.0", "GameBoyMount"), ("PKMN_Card_Mount_1.0", "PokemonCardMount")):
                root = Path(tmp) / package / "WotLK" / "Creature" / model_stem
                root.mkdir(parents=True)
                (root / f"{model_stem}.m2").write_bytes(self._m2_with_blank_textures())
                roots.append(Path(tmp) / package)
            baseline = Path(tmp) / "baseline"
            self._mount_baseline(baseline)

            mounts = MODULE.discover_mounts(tuple(roots))
            records = MODULE.build_mount_records(mounts, baseline)
            entries = MODULE.build_mount_dbc_entries(records, baseline)

            expected_fields = {
                4: 269844752,
                8: 67108864,
                11: 0,
                31: 31,
                32: 128,
                73: 6,
                76: 1,
                82: 279,
                97: 207,
                116: 3908,
                131: 12844,
            }
            for record in records:
                for field, expected in expected_fields.items():
                    self.assertEqual(record.spell_row[field], expected)
            self.assertTrue(all(record.mount.vehicle_id is None for record in records))
            self.assertNotIn("DBFilesClient/Vehicle.dbc1-mounts", entries)
            self.assertNotIn("DBFilesClient/VehicleSeat.dbc1-mounts", entries)
            sql = MODULE.render_mount_sql(records)
            spell_columns = next(line for line in sql.splitlines() if line.startswith("INSERT INTO `spell_dbc`"))
            for column in (
                "AttributesEx4", "AuraInterruptFlags", "Effect_3", "EffectDieSides_3", "EffectBasePoints_3",
                "EffectAura_3", "EffectTriggerSpell_1",
            ):
                self.assertIn(f"`{column}`", spell_columns)
            column_names = [value.strip().strip("`") for value in spell_columns.split("(", 1)[1].split(")", 1)[0].split(",")]
            spell_row = next(line for line in sql.splitlines() if line.startswith(f"({records[0].spell_id},"))
            values = spell_row.rstrip(",;").split(",")
            for column, expected in {
                "AttributesEx4": "67108864",
                "AuraInterruptFlags": "128",
                "Effect_3": "6",
                "EffectDieSides_3": "1",
                "EffectBasePoints_3": "279",
                "EffectAura_3": "207",
                "EffectTriggerSpell_1": "3908",
            }.items():
                self.assertEqual(values[column_names.index(column)].strip(), expected)
            self.assertNotIn("vehicle_dbc", sql)
            self.assertNotIn("vehicleseat_dbc", sql)

    def test_native_mount_ids_preserve_existing_prefix_when_variants_append(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Game_Boy_Mount_1.0" / "WotLK" / "Creature" / "GameBoyMount"
            root.mkdir(parents=True)
            (root / "GameBoyMount.m2").write_bytes(self._m2_with_blank_textures())
            baseline = Path(tmp) / "baseline"
            self._mount_baseline(baseline)

            base = MODULE.discover_mounts((Path(tmp) / "Game_Boy_Mount_1.0",))
            expanded = MODULE.expand_mount_variants(base)
            base_ids = MODULE.mount_ids(base, baseline)
            expanded_ids = MODULE.mount_ids(expanded, baseline)

            for kind in ("item_display", "display", "model"):
                self.assertEqual(expanded_ids[kind][:len(base)], base_ids[kind])

    def test_merge_wxl_continuations_combines_rows_into_working_car_suffix(self):
        base = MODULE.build_wdbc([[3, 4]], 2, 8)
        extra = MODULE.build_wdbc([[1, 2]], 2, 8)

        merged = MODULE.merge_wdbc_continuations(base, extra, "Item")
        table = MODULE.Wdbc(merged)

        self.assertEqual(table.count, 2)
        self.assertEqual([row[0] for row in table.rows], [1, 3])

    def test_rewrite_m2_texture_paths_updates_texture_records_without_touching_model_header(self):
        source = self._m2_with_texture(texture=b"body.blp")
        result = MODULE.rewrite_m2_texture_paths(source, {b"body.blp": r"Creature\EsteriaMounts\body.blp"})

        self.assertEqual(result[:8], source[:8])
        length, offset = struct.unpack_from("<II", result, 0x78)
        self.assertEqual(result[offset : offset + length], b"Creature\\EsteriaMounts\\body.blp\0")

    def test_collect_mount_entries_namespaces_model_and_referenced_texture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture())
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (model_dir / "body.blp").write_bytes(b"BLP")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount)

            self.assertIn(mount.client_model_path, entries)
            self.assertIn(f"Creature\\EsteriaMounts\\{mount.slug}\\Example00.skin", entries)
            texture_paths = [name for name in entries if name.lower().endswith("body.blp")]
            self.assertEqual(len(texture_paths), 1)
            self.assertIn(b"Creature\\EsteriaMounts\\", entries[mount.client_model_path])

    def test_collect_mount_entries_remaps_source_root_texture_with_creature_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture(texture=b"Creature\\Example\\body.blp"))
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (root / "body.blp").write_bytes(b"BLP")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount)
            refs = [name for _, name in MODULE._m2_texture_entries(entries[mount.client_model_path])]

            self.assertEqual(len(refs), 1)
            self.assertIn(b"Creature\\EsteriaMounts\\", refs[0])
            self.assertEqual(entries[refs[0].decode("ascii")], b"BLP")

    def test_collect_mount_entries_uses_explicit_model_texture_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "mk8standard"
            model_dir = root / "Creature"
            model_dir.mkdir(parents=True)
            (model_dir / "mk8standard.m2").write_bytes(
                self._m2_with_texture(texture=b"Creature\\mk8\\emblem\\dummy.blp")
            )
            (model_dir / "mk8standard00.skin").write_bytes(b"SKIN")
            alias_dir = root / "Creature" / "mk8" / "emblem"
            alias_dir.mkdir(parents=True)
            (alias_dir / "emblem_dummy.blp").write_bytes(b"ALIAS_TEXTURE")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount)
            refs = [name for _, name in MODULE._m2_texture_entries(entries[mount.client_model_path])]

            self.assertEqual(len(refs), 1)
            self.assertEqual(entries[refs[0].decode("ascii")], b"ALIAS_TEXTURE")

    def test_collect_mount_entries_does_not_use_icon_as_model_texture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture(texture=b"body.blp"))
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            icon_dir = model_dir / "Interface" / "Icons"
            icon_dir.mkdir(parents=True)
            (icon_dir / "body.blp").write_bytes(b"ICON_TEXTURE")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount, default_icon=b"DEFAULT_ICON")
            refs = [name for _, name in MODULE._m2_texture_entries(entries[mount.client_model_path])]

            self.assertEqual(refs, [b"body.blp"])
            self.assertNotIn(
                f"Creature\\EsteriaMounts\\{mount.slug}\\textures\\01_body.blp",
                entries,
            )

    def test_collect_mount_entries_ignores_inv_files_outside_icon_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture())
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (model_dir / "inv_example.blp").write_bytes(b"MODEL_DIRECTORY_ICON")
            (root / "inv_example.blp").write_bytes(b"ROOT_ICON")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount, default_icon=b"DEFAULT_ICON")

            self.assertEqual(
                entries[f"Interface\\Icons\\INV_Mount_{mount.slug}.blp"],
                b"DEFAULT_ICON",
            )

    def test_collect_mount_entries_aliases_noncanonical_zero_skin_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example - Copia.m2").write_bytes(self._m2_with_texture())
            (model_dir / "Example00 - Copia.skin").write_bytes(b"SKIN")
            (model_dir / "body.blp").write_bytes(b"BLP")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount)
            expected_skin = str(Path(mount.client_model_path).parent / "Example - Copia00.skin").replace("/", "\\")

            self.assertIn(expected_skin, entries)
            self.assertEqual(entries[expected_skin], b"SKIN")

    def test_collect_mount_entries_packages_a_named_mount_icon(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture())
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (model_dir / "body.blp").write_bytes(b"MODEL_TEXTURE")
            icon_dir = root / "Interface" / "Icons"
            icon_dir.mkdir(parents=True)
            (icon_dir / "inv_example.blp").write_bytes(b"MOUNT_ICON")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount)

            self.assertEqual(
                entries[f"Interface\\Icons\\INV_Mount_{mount.slug}.blp"],
                b"MOUNT_ICON",
            )

    def test_collect_mount_entries_uses_explicit_default_icon_instead_of_model_texture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture())
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (model_dir / "body.blp").write_bytes(b"MODEL_TEXTURE")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount, default_icon=b"DEFAULT_ICON")

            self.assertEqual(
                entries[f"Interface\\Icons\\INV_Mount_{mount.slug}.blp"],
                b"DEFAULT_ICON",
            )

    def test_collect_mount_entries_keeps_blank_skin_slot_and_packages_sibling_texture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "WhimsyshireCloudMount"
            model_dir = root / "Creature"
            model_dir.mkdir(parents=True)
            model_path = model_dir / "WhimsyshireCloudMount.m2"
            model_path.write_bytes(self._m2_with_blank_texture())
            (model_dir / "WhimsyshireCloudMount00.skin").write_bytes(b"SKIN")
            (model_dir / "WhimsyshireCloudMount_Happy.blp").write_bytes(b"BODY_TEXTURE")

            mount = MODULE.discover_mounts((root,))[0]
            entries = MODULE.collect_mount_entries(mount)
            model = entries[mount.client_model_path]
            refs = [(texture_type, name) for _, texture_type, name in MODULE._m2_texture_records(model)]

            self.assertEqual(refs, [(11, b"")])
            output_texture = str(
                Path(mount.client_model_path).parent / "WhimsyshireCloudMount_Happy.blp"
            ).replace("/", "\\")
            self.assertEqual(entries[output_texture], b"BODY_TEXTURE")

    def test_scaled_drake_preserves_each_source_body_layer(self):
        roots = MODULE.MOUNT_SOURCE_DEFAULTS
        if not all(root.is_dir() for root in roots):
            self.skipTest("mount source assets are not available")

        mount = next(item for item in MODULE.discover_mounts(roots) if item.model.stem.casefold() == "scaleddrakemount")
        entries = MODULE.collect_mount_entries(mount)
        model = entries[mount.client_model_path]
        body_refs = [
            name.decode("ascii")
            for _, texture_type, name in MODULE._m2_texture_records(model)
            if texture_type == 0 and b"drakeskinscaled" in name.lower()
        ]

        self.assertEqual(
            [Path(name).name.casefold() for name in body_refs],
            [
                "01_drakeskinscaled_03.blp",
                "02_drakeskinscaled_04.blp",
                "03_drakeskinscaled_02.blp",
                "04_drakeskinscaled_01.blp",
            ],
        )

    def test_problem_mounts_use_model_specific_variation_assets(self):
        roots = MODULE.MOUNT_SOURCE_DEFAULTS
        if not all(root.is_dir() for root in roots):
            self.skipTest("mount source assets are not available")

        mounts = {mount.model.stem.casefold(): mount for mount in MODULE.discover_mounts(roots)}
        expected = {
            "faeriedragoncreature": {11: "faeriedragonmount01_noalpha.blp", 12: "faeriedragonmountsaddle.blp"},
            "mushanbeastmount": {11: "MushanBeastMount1Brown.blp", 12: "MushanBeastMount2Brown.blp"},
            "horsehighelfmount - copia": {11: "horse2mountHighElf.blp", 12: "Horse2_Saddle.blp"},
            "horsehighelfmount": {11: "horse2mountHighElf.blp", 12: "Horse2_Saddle.blp"},
            "horsehighelfmountelite": {
                11: "Horse2MountElite_Body_silver.blp", 12: "Horse2MountElite_Armor_silver.blp",
            },
            "horsehighelfpaladin": {11: "paladinmount_GoldRed.blp", 12: "Horse2_Saddle_HighElf.blp"},
            "horsehighelfpaladinelite": {
                11: "Horse2MountElite_Body_Paladin.blp", 12: "Horse2MountElite_Armor_Paladin.blp",
            },
        }

        for model_stem, expected_files in expected.items():
            self.assertEqual(
                {texture_type: path.name for texture_type, path in MODULE._mount_texture_variation_paths(mounts[model_stem]).items()},
                expected_files,
            )

    def test_blank_creature_skin_slots_use_display_variations_and_sibling_textures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Example"
            model_dir = root / "Creature"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_blank_textures())
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (model_dir / "body.blp").write_bytes(b"BODY")
            (model_dir / "saddle.blp").write_bytes(b"SADDLE")

            baseline = Path(tmp) / "baseline"
            baseline.mkdir()
            (baseline / "Spell.dbc").write_bytes(MODULE.build_wdbc([[23214] + [0] * 233], 234, 936))
            (baseline / "Item.dbc").write_bytes(MODULE.build_wdbc([[18776] + [0] * 7], 8, 32))
            (baseline / "ItemDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[68742] + [0] * 24], 25, 100))
            (baseline / "CreatureDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[94234] + [0] * 15], 16, 64))
            (baseline / "CreatureModelData.dbc").write_bytes(MODULE.build_wdbc([[4899] + [0] * 27], 28, 112))

            mount = MODULE.discover_mounts((root,))[0]
            record = MODULE.build_mount_records((mount,), baseline)[0]
            display = MODULE.Wdbc(
                MODULE.build_mount_dbc_entries((record,))["DBFilesClient/CreatureDisplayInfo.dbc1-mounts"]
            )
            display_row = display.row(record.display_id)

            self.assertEqual(display.text(display_row[6]), "body")
            self.assertEqual(display.text(display_row[7]), "saddle")

            entries = MODULE.collect_mount_entries(mount)
            model = entries[mount.client_model_path]
            self.assertEqual(
                [(texture_type, name) for _, texture_type, name in MODULE._m2_texture_records(model)],
                [(11, b""), (12, b"")],
            )
            output_dir = Path(mount.client_model_path).parent
            self.assertEqual(entries[str(output_dir / "body.blp").replace("/", "\\")], b"BODY")
            self.assertEqual(entries[str(output_dir / "saddle.blp").replace("/", "\\")], b"SADDLE")

    def test_build_mount_dbc_entries_assigns_named_unique_mount_icons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture())
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (model_dir / "body.blp").write_bytes(b"MODEL_TEXTURE")
            icon_dir = root / "Interface" / "Icons"
            icon_dir.mkdir(parents=True)
            (icon_dir / "inv_example.blp").write_bytes(b"MOUNT_ICON")

            baseline = Path(tmp) / "baseline"
            baseline.mkdir()
            spell = [0] * 234
            spell[0] = 23214
            item = [18776, 15, 5, 0xFFFFFFFF, 4, 25132, 0, 0]
            (baseline / "Spell.dbc").write_bytes(MODULE.build_wdbc([spell], 234, 936))
            (baseline / "Item.dbc").write_bytes(MODULE.build_wdbc([item], 8, 32))
            (baseline / "ItemDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[68742] + [0] * 24], 25, 100))
            (baseline / "CreatureDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[94234] + [0] * 15], 16, 64))
            (baseline / "CreatureModelData.dbc").write_bytes(MODULE.build_wdbc([[4899] + [0] * 27], 28, 112))

            mount = MODULE.discover_mounts((root,))[0]
            record = MODULE.build_mount_records((mount,), baseline)[0]
            entries = MODULE.build_mount_dbc_entries((record,))
            spell_table = MODULE.Wdbc(entries["DBFilesClient/Spell.dbc1-mounts"])
            icon_table = MODULE.Wdbc(entries["DBFilesClient/SpellIcon.dbc1-mounts"])
            item_display_table = MODULE.Wdbc(entries["DBFilesClient/ItemDisplayInfo.dbc1-mounts"])
            spell_row = spell_table.row(record.spell_id)
            icon_row = icon_table.row(spell_row[133])
            item_display_row = item_display_table.row(record.item_display_id)

            self.assertNotEqual(spell_row[133], 1716)
            self.assertEqual(icon_table.text(icon_row[1]), f"Interface\\Icons\\INV_Mount_{mount.slug}")
            self.assertEqual(item_display_table.text(item_display_row[5]), f"INV_Mount_{mount.slug}")
            self.assertEqual(spell_table.text(spell_row[136]), mount.display_name)

    def test_build_mount_records_and_sql_use_unique_wotlk_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pack"
            model_dir = root / "Creature" / "Example"
            model_dir.mkdir(parents=True)
            (model_dir / "Example.m2").write_bytes(self._m2_with_texture())
            (model_dir / "Example00.skin").write_bytes(b"SKIN")
            (model_dir / "body.blp").write_bytes(b"BLP")

            baseline = Path(tmp) / "baseline"
            baseline.mkdir()
            spell = [0] * 234
            spell[0] = 23214
            item = [18776, 15, 5, 0xFFFFFFFF, 4, 25132, 0, 0]
            (baseline / "Spell.dbc").write_bytes(MODULE.build_wdbc([spell], 234, 936))
            (baseline / "Item.dbc").write_bytes(MODULE.build_wdbc([item], 8, 32))
            (baseline / "ItemDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[68742] + [0] * 24], 25, 100))
            (baseline / "CreatureDisplayInfo.dbc").write_bytes(MODULE.build_wdbc([[94234] + [0] * 15], 16, 64))
            (baseline / "CreatureModelData.dbc").write_bytes(MODULE.build_wdbc([[4899] + [0] * 27], 28, 112))

            mounts = MODULE.discover_mounts((root,))
            records = MODULE.build_mount_records(mounts, baseline)
            dbc_entries = MODULE.build_mount_dbc_entries(records)
            sql = MODULE.render_mount_sql(records)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].spell_id, 201000)
            self.assertEqual(records[0].item_id, 901000)
            self.assertEqual(records[0].creature_id, 3460608)
            self.assertEqual(records[0].spell_row[110], records[0].creature_id)
            self.assertNotEqual(records[0].spell_row[110], records[0].display_id)
            self.assertEqual(MODULE.Wdbc(dbc_entries["DBFilesClient/Spell.dbc1-mounts"]).count, 1)
            skill_table = MODULE.Wdbc(dbc_entries["DBFilesClient/SkillLineAbility.dbc1-mounts"])
            self.assertEqual(
                skill_table.row(records[0].spell_id),
                [records[0].spell_id, 777, records[0].spell_id, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            )
            self.assertEqual(
                skill_table.row(201111),
                [201111, 777, 201111, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            )
            spell_columns = next(line for line in sql.splitlines() if line.startswith("INSERT INTO `spell_dbc`"))
            spell_sql = next(line for line in sql.splitlines() if line.startswith("(201000,"))
            column_names = [value.strip().strip("`") for value in spell_columns.split("(", 1)[1].split(")", 1)[0].split(",")]
            values = spell_sql.rstrip(",;").split(",")
            self.assertEqual(int(values[column_names.index("EffectMiscValue_1")].strip()), records[0].creature_id)
            item_display_sql = next(line for line in sql.splitlines() if line.startswith("(68741,"))
            self.assertIn("'INV_Mount_", item_display_sql)
            self.assertIn("INSERT INTO `creature_template_model`", sql)
            self.assertIn(f"(3460608, 0, {records[0].display_id}, 1, 1, 51831)", sql)
            self.assertIn("REPLACE INTO `creature_template`", sql)
            model_info_sql = sql.split("REPLACE INTO `creature_model_info`", 1)[1]
            self.assertIn(f"({records[0].display_id},", model_info_sql)
            self.assertNotIn("DELETE FROM `creature_template`", sql)
            self.assertIn("REPLACE INTO `item_template` (`entry`", sql)
            self.assertIn("(901000,", sql)
            self.assertIn("INSERT INTO `skilllineability_dbc`", sql)
            self.assertIn(f"({records[0].spell_id}, 777, {records[0].spell_id}, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0)", sql)
            self.assertIn("Example", sql)
            item_row = next(line for line in sql.splitlines() if line.startswith("(901000, 15, 5, -1, 'Reins"))
            self.assertEqual(len(item_row.rstrip(",;").split(",")), 59)
            self.assertIn("12340, 483, 0, -1, 0, -1, 330, 3000, 201000, 6", item_row)

    def test_merge_wxl_manifest_preserves_existing_paths_and_appends_new_paths_once(self):
        result = MODULE.merge_wxl_manifest(
            b"# existing\nDBFilesClient/Spell.dbc1-cars\n",
            b"# generated\nDBFilesClient/Spell.dbc1-cars\nDBFilesClient/Spell.dbc1-mounts\n",
        )
        self.assertEqual(
            result.decode(),
            "# existing\nDBFilesClient/Spell.dbc1-cars\nDBFilesClient/Spell.dbc1-mounts\n",
        )
