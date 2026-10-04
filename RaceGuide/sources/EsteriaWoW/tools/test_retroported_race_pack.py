from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import retroported_race_pack as pack  # noqa: E402


CLIENT = Path(r"G:\3.3.5a - Dev")
STAGE = Path(r"G:\RetroPorterWork\maghar\integration\latest")


@unittest.skipUnless(CLIENT.is_dir(), "Esteria developer client is not available")
class RetroportedRacePackTests(unittest.TestCase):
    def test_plan_uses_live_client_and_retroported_assets(self) -> None:
        result = pack.plan("maghar", CLIENT)
        self.assertEqual(result["race_ids"], [45])
        self.assertEqual(result["assets"], 439)
        self.assertEqual(result["tables"]["ChrRaces"], 33)
        self.assertEqual(result["tables"]["CharSections"], 410820)
        self.assertEqual(len(result["server_dbcs"]), 7)
        self.assertNotIn("server_continuations", result)

    @unittest.skipUnless((STAGE / "build-report.json").is_file(), "run retroported_race_pack.py build first")
    def test_staged_maghar_pack_validates(self) -> None:
        result = pack.validate("maghar", CLIENT)
        global_key = str(STAGE / pack.GLOBAL_ARCHIVE_REL)
        locale_key = str(STAGE / pack.LOCALE_ARCHIVE_REL)
        self.assertEqual(result[global_key]["charsections"], 522)
        self.assertEqual(result[locale_key]["charsections"], 522)
        self.assertTrue((STAGE / pack.ASSET_ARCHIVE_REL).is_file())

    def test_maghar_manifest_uses_wrath_compatible_runtime_appearance(self) -> None:
        manifest = json.loads((ROOT / "data/retroported-races/maghar.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["appearance"]["skin_source_indices"], [0, 1, 2, 3, 4, 5, 6, 8, 9])
        self.assertEqual(manifest["appearance"]["face_indices"], list(range(9)))
        self.assertEqual(manifest["appearance"]["retail_skin_source_indices"], [0, 1, 2, 3, 4, 5, 6, 8, 9])
        self.assertEqual(manifest["appearance"]["hair_color_indices"], list(range(9)))
        self.assertEqual(manifest["appearance"]["male_hair_styles"], 12)
        self.assertEqual(manifest["appearance"]["female_hair_styles"], 13)
        self.assertEqual(manifest["models"]["male"]["runtime_model_path"], r"Character\Orc2\Male\OrcMale2.m2")
        self.assertEqual(manifest["models"]["female"]["runtime_model_path"], r"Character\Orc2\Female\OrcFemale2.m2")
        self.assertEqual(
            manifest["models"]["male"]["previous_runtime_model_paths"],
            [r"custom\maghar\character\orc\male\orcmale_hd.m2", r"custom\maghar\runtime\male\orcmale_hd.m2"],
        )
        self.assertEqual(
            manifest["models"]["female"]["previous_runtime_model_paths"],
            [r"custom\maghar\character\orc\female\orcfemale_hd.m2", r"custom\maghar\runtime\female\orcfemale_hd.m2"],
        )
        self.assertEqual(manifest["models"]["male"]["source_model_id"], 51)
        self.assertEqual(manifest["models"]["female"]["source_model_id"], 52)

    @unittest.skipUnless((STAGE / "build-report.json").is_file(), "run retroported_race_pack.py build first")
    def test_maghar_charsections_use_universal_class_flags(self) -> None:
        storm = pack.Storm(pack.DLL_DEFAULT)
        data = pack._read_archive_entry(
            storm,
            STAGE / pack.LOCALE_ARCHIVE_REL,
            f"{pack.DBC_ROOT}CharSections.dbc",
        )
        table = pack.RawWdbc(data)
        rows = [row for row in table.records if pack._value(row, 1 * 4) == 45]
        self.assertEqual(len(rows), 522)
        face_rows = [row for row in rows if pack._value(row, 3 * 4) == 1]
        non_face_rows = [row for row in rows if pack._value(row, 3 * 4) != 1]
        self.assertEqual({pack._value(row, 7 * 4) for row in face_rows}, {0x1})
        self.assertEqual({pack._value(row, 7 * 4) for row in non_face_rows}, {0x11})
        appearance_rows = [row for row in rows if pack._value(row, 3 * 4) in (0, 1)]
        for row in appearance_rows:
            gender = pack._value(row, 2 * 4)
            section = pack._value(row, 3 * 4)
            for field in (4, 5, 6):
                texture = pack._string(table.strings, pack._value(row, field * 4)).decode("utf-8")
                self.assertNotIn("Orc2", texture)

        skin_rows = [row for row in rows if pack._value(row, 3 * 4) == 0]
        self.assertEqual(len(skin_rows), 18)
        for row in skin_rows:
            gender = pack._value(row, 2 * 4)
            skin_index = pack._value(row, 9 * 4)
            self.assertIn(skin_index, range(9))
            self.assertEqual(pack._value(row, 8 * 4), 0)
            stem = "orcmale" if gender == 0 else "orcfemale"
            sex = "male" if gender == 0 else "female"
            body = pack._string(table.strings, pack._value(row, 4 * 4)).decode("utf-8")
            head = pack._string(table.strings, pack._value(row, 5 * 4)).decode("utf-8")
            self.assertEqual(body, pack._derived_body_path(sex, stem, skin_index))
            self.assertEqual(head, pack._derived_base_head_path(sex, stem, skin_index))

        face_rows = [row for row in rows if pack._value(row, 3 * 4) == 1]
        self.assertEqual(len(face_rows), 162)
        for row in face_rows:
            gender = pack._value(row, 2 * 4)
            face_index = pack._value(row, 8 * 4)
            skin_index = pack._value(row, 9 * 4)
            self.assertIn(face_index, range(9))
            self.assertIn(skin_index, range(9))
            stem = "orcmale" if gender == 0 else "orcfemale"
            sex = "male" if gender == 0 else "female"
            lower = pack._string(table.strings, pack._value(row, 4 * 4)).decode("utf-8")
            upper = pack._string(table.strings, pack._value(row, 5 * 4)).decode("utf-8")
            self.assertEqual(lower, pack._derived_face_fragment_path(sex, stem, face_index, skin_index, "lower"))
            self.assertEqual(upper, pack._derived_face_fragment_path(sex, stem, face_index, skin_index, "upper"))

        # Facial-hair overlays are composited onto FaceLower and need indexed RGB
        # plus authored alpha. Direct model hair may use DXT; this overlay cannot.
        facial_rows = [row for row in rows if pack._value(row, 3 * 4) == 2]
        self.assertEqual(len(facial_rows), 99)
        with pack.ClientFiles(str(CLIENT / "Data"), "enUS") as files:
            for row in facial_rows:
                texture = pack._string(table.strings, pack._value(row, 4 * 4)).decode("utf-8")
                if not texture:
                    continue
                overlay = pack.Blp.parse(files.find(texture)[0], texture)
                self.assertEqual(overlay.compression, pack.BLP_COMPRESSION_PALETTE, texture)
                self.assertEqual(overlay.alpha_size, 8, texture)
                self.assertEqual((overlay.width, overlay.height), (256, 128), texture)

    @unittest.skipUnless((STAGE / "build-report.json").is_file(), "run retroported_race_pack.py build first")
    def test_maghar_retail_appearance_is_baked_to_wrath_layers(self) -> None:
        derived = STAGE.parent / "derived"
        report = json.loads((derived / "derived-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], 5)
        self.assertEqual(len(report["bodies"]), 18)
        self.assertEqual(len(report["heads"]), 18)
        self.assertEqual(len(report["face_fragments"]), 324)
        files = sorted(derived.rglob("*.blp"))
        self.assertEqual(len(files), 360)
        for path in files:
            blp = pack.Blp.parse(path.read_bytes(), str(path))
            compatible, reason = blp.is_wotlk_compatible()
            self.assertTrue(compatible, reason)
            self.assertEqual(blp.compression, pack.BLP_COMPRESSION_PALETTE)
            self.assertEqual(blp.alpha_size, 0)
            self.assertEqual(blp.alpha_type, 8)
            self.assertEqual({entry >> 24 for entry in blp.palette}, {0})
            if "\\face\\" in str(path).replace("/", "\\"):
                self.assertIn((blp.width, blp.height), {(256, 64), (256, 128)})
                expected_mips = 7 if blp.height == 64 else 8
                self.assertEqual(blp.mip_count, expected_mips)
            else:
                self.assertEqual((blp.width, blp.height), (512, 512))
                self.assertEqual(blp.mip_count, 10)

        for sex, stem in (("male", "orcmale"), ("female", "orcfemale")):
            for skin_index in range(9):
                body_path = derived.joinpath(*pack.PureWindowsPath(
                    pack._derived_body_path(sex, stem, skin_index)
                ).parts)
                body = pack.Blp.parse(body_path.read_bytes(), str(body_path))
                head_path = derived.joinpath(*pack.PureWindowsPath(
                    pack._derived_base_head_path(sex, stem, skin_index)
                ).parts)
                head = pack.Blp.parse(head_path.read_bytes(), str(head_path))
                self.assertEqual(head.palette, body.palette)

    def test_face_projection_reproduces_known_good_orc2_face_layout(self) -> None:
        """Use Blizzard-compatible art as a control for the geometry-derived UV bake."""
        import numpy as np

        manifest = pack.load_manifest("maghar")
        with pack.ClientFiles(str(CLIENT / "Data"), "enUS") as files:
            for sex, stem in (("male", "OrcMale"), ("female", "OrcFemale")):
                coordinates, covered, report = pack._maghar_face_uv_map(manifest, CLIENT, sex)
                prefix = f"Character\\Orc2\\{sex.capitalize()}\\{stem}"
                extra = pack.Blp.parse(files.find(prefix + "Skin00_00_Extra.blp")[0]).decode_level(0)
                projected = pack._project_maghar_face(extra, coordinates)
                upper = pack.Blp.parse(files.find(prefix + "FaceUpper00_00.blp")[0]).decode_level(0)
                lower = pack.Blp.parse(files.find(prefix + "FaceLower00_00.blp")[0]).decode_level(0)
                control = np.frombuffer(bytes(upper.data) + bytes(lower.data), dtype=np.uint8).reshape(192, 256, 4)
                result = np.frombuffer(projected.data, dtype=np.uint8).reshape(192, 256, 4)
                error = np.abs(result[covered, :3].astype(float) - control[covered, :3]).mean(axis=1)
                # Stock fragments have palette loss and some separately authored details.
                # A strip crop places the nose/mouth elsewhere and fails this control.
                self.assertLess(float(error.mean()), 15, sex)
                self.assertLess(float(np.median(error)), 7, sex)
                self.assertLess(report["maximum_vertex_distance"], .001)

    @unittest.skipUnless((STAGE / "build-report.json").is_file(), "run retroported_race_pack.py build first")
    def test_maghar_uses_wrath_orc2_geometry_and_custom_compositor_art(self) -> None:
        manifest = json.loads((ROOT / "data/retroported-races/maghar.json").read_text(encoding="utf-8"))
        storm = pack.Storm(pack.DLL_DEFAULT)
        asset_handle = storm.open_archive(STAGE / pack.ASSET_ARCHIVE_REL)
        global_handle = storm.open_archive(STAGE / pack.GLOBAL_ARCHIVE_REL)
        try:
            asset_names = {name.casefold() for name, *_ in storm.list_files(asset_handle)}
            global_names = {name.casefold() for name, *_ in storm.list_files(global_handle)}
            for sex, stem in (("male", "orcmale"), ("female", "orcfemale")):
                runtime_model = manifest["models"][sex]["runtime_model_path"].casefold()
                self.assertTrue(runtime_model.startswith("character\\orc2\\"))
                self.assertIn(runtime_model, global_names)
                self.assertNotIn(runtime_model, asset_names)
                derived = pack._derived_face_fragment_path(sex, stem, 0, 0, "lower").casefold()
                self.assertIn(derived, asset_names)
                self.assertNotIn(derived, global_names)
            self.assertFalse(any(name.startswith("custom\\maghar\\runtime\\") for name in asset_names))
        finally:
            storm.dll.SFileCloseArchive(global_handle)
            storm.dll.SFileCloseArchive(asset_handle)

    def test_maghar_player_displays_fit_uint16_and_source_assets_are_closed(self) -> None:
        allocation = json.loads((ROOT / "data/retroported-races/allocation.json").read_text(encoding="utf-8"))
        displays = allocation["race_allocations"]["maghar"]["CreatureDisplayInfo"]
        self.assertEqual(displays, {"male": 60030, "female": 60031})
        self.assertTrue(all(0 < value <= 0xFFFF for value in displays.values()))
        manifest = json.loads((ROOT / "data/retroported-races/maghar.json").read_text(encoding="utf-8"))
        pack._validate_asset_dependencies(manifest)
        root = Path(manifest["source_patch_root"])
        refs = set()
        for gender in ("male", "female"):
            refs.update(pack._embedded_m2_texture_refs(pack._patch_root_path(root, manifest["models"][gender]["model_path"])))
        self.assertEqual(len(refs), 9)
        for ref in refs:
            self.assertTrue(pack._patch_root_path(root, ref).is_file(), ref)

    def test_character_create_patches_are_additive(self) -> None:
        data, _ = pack._effective_file(CLIENT / "Data", r"Interface\GlueXML\CharacterCreate.xml")
        patched = pack._patch_character_create_xml(data).decode("utf-8")
        for index in range(1, 41):
            self.assertIn(f'CharacterCreateRaceButton{index}"', patched)
        self.assertIn('CharacterCreateRaceButton64"', patched)
        self.assertIn('inherits="CharacterCreateRaceButtonTemplate"', patched)

        lua, _ = pack._effective_file(CLIENT / "Data", r"Interface\GlueXML\CharacterCreate.lua")
        patched_lua = pack._patch_character_create_lua(lua).decode("utf-8")
        self.assertIn("MAX_RACES = 64;", patched_lua)
        self.assertIn("availableRaceIDs = {GetAvailableRaceIDs()};", patched_lua)
        self.assertIn("button.uiSlot = index;", patched_lua)
        self.assertIn("button.raceID = raceID;", patched_lua)
        self.assertIn("local exactRaceID = _G.GetExactRaceIDForFileString(fileString);", patched_lua)
        self.assertIn("raceID = exactRaceID;", patched_lua)
        self.assertIn("CharacterCreate.selectedRaceID", patched_lua)
        self.assertIn("function CharacterRace_OnClick(self, id)", patched_lua)
        self.assertIn("SetSelectedRace(id);", patched_lua)
        self.assertIn("CharacterCreate.selectedRace = id;", patched_lua)
        self.assertIn(
            "CharacterCreate.selectedRaceID = selectedButton and (selectedButton.raceID or id) or id;",
            patched_lua,
        )
        self.assertNotIn("SetSelectedRace(self.raceID", patched_lua)

    def test_character_info_keeps_ui_slots_separate_from_exact_race_ids(self) -> None:
        data, _ = pack._effective_file(CLIENT / "Data", r"Interface\GlueXML\CharacterInfo.lua")
        patched = pack._patch_character_info(data).decode("utf-8")
        self.assertIn('local EXACT_RACE_DATA = {', patched)
        self.assertIn('[45] = { glueString = "MAGHAR", name = "Mag\'har Orc", faction = "Horde", fileString = "Maghar" }', patched)
        self.assertNotIn('local HORDE_RACES = {8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 45}', patched)
        self.assertIn('_G.EXACT_RACE_DATA = EXACT_RACE_DATA', patched)
        self.assertIn("EXACT_RACE_ID_BY_FILE_STRING[strupper(exactRaceData.fileString)] = exactRaceID", patched)
        self.assertIn("_G.GetExactRaceIDForFileString = GetExactRaceIDForFileString", patched)

    def test_maghar_glue_strings_are_present(self) -> None:
        data, _ = pack._effective_file(CLIENT / "Data", r"Interface\GlueXML\GlueStrings.lua")
        patched = pack._patch_glue_strings(data).decode("utf-8")
        self.assertIn('MAGHAR = "Mag\'har Orc";', patched)
        self.assertIn('RACE_INFO_MAGHAR = "The uncorrupted orc clans of Draenor', patched)
        self.assertIn('ABILITY_INFO_MAGHAR3 = "- Sympathetic Vigor increases your pet\'s maximum health.";', patched)


if __name__ == "__main__":
    unittest.main()
