"""Runnable checks for the staged Skyborne runtime, without changing the client."""

import struct
import unittest

from wotlkconv.m2 import parse_m2, parse_skin

import skyborne_visual_pack as visuals
import retroported_race_pack as pack


class SkyborneVisualTests(unittest.TestCase):
    def test_models_have_closed_materials_and_legacy_geosets(self):
        report = pack.load_json(visuals.ROOT / "integration" / "visual-preparation.json")
        for sex, details in report["sexes"].items():
            path = visuals.OUTPUT.joinpath(*pack.PureWindowsPath(details["model_path"]).parts)
            model = parse_m2(path.read_bytes(), str(path))
            skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
            self.assertLessEqual(model.vertex_count, 65535)
            self.assertEqual(len(list(path.parent.glob("*.anim"))), 53)
            self.assertFalse({11, 15} & {t["type"] for t in model.textures})
            geosets = {visuals.u16(row, 0) for row in skin.submeshes}
            self.assertTrue({0, 201, 202, 901, 1601} <= geosets)
            self.assertFalse(any(300 <= geoset < 400 for geoset in geosets))
            self.assertLess(max(geosets), 2000)
            self.assertLessEqual(len(skin.indices), 65535)
            self.assertTrue(all(visuals.u16(row, 2) == 0 for row in skin.submeshes))
            self.assertTrue(all(struct.unpack_from("<I", row)[0] < 2000 for row in skin.submeshes))
            for texture in model.textures:
                if texture["filename"]:
                    self.assertTrue(visuals.path_for(texture["filename"]).is_file(), texture["filename"])
            for batch in skin.batches:
                self.assertLess(visuals.u16(batch, 4), len(skin.submeshes))
                combo = visuals.u16(batch, 16)
                count = visuals.u16(batch, 14)
                self.assertLessEqual(combo + count, len(model.texture_combos))
                self.assertTrue(all(i < len(model.textures) for i in model.texture_combos[combo:combo + count]))

    def test_skin_ranges_and_merged_bone_palettes(self):
        report = pack.load_json(visuals.ROOT / "integration" / "visual-preparation.json")
        for details in report["sexes"].values():
            path = visuals.OUTPUT.joinpath(*pack.PureWindowsPath(details["model_path"]).parts)
            model = parse_m2(path.read_bytes())
            skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
            for row in skin.submeshes:
                start, count = struct.unpack_from("<2H", row, 4)
                triangle_start = visuals.u16(row, 8) + (visuals.u16(row, 2) << 16)
                triangle_count = visuals.u16(row, 10)
                self.assertLessEqual(start + count, len(skin.vertices))
                self.assertLessEqual(triangle_start + triangle_count, len(skin.indices))
                self.assertTrue(all(start <= i < start + count
                                    for i in skin.indices[triangle_start:triangle_start + triangle_count]))
                bone_count, bone_start = struct.unpack_from("<2H", row, 12)
                self.assertLessEqual(bone_start + bone_count, len(model.bone_combos))
                for lookup in range(start, start + count):
                    vertex = skin.vertices[lookup]
                    self.assertLess(vertex, model.vertex_count)
                    for influence in range(4):
                        if not model.vertices[vertex * 48 + 12 + influence]:
                            continue
                        palette_index = skin.bones[lookup * 4 + influence]
                        self.assertLess(palette_index, bone_count)
                        resolved = model.bone_combos[bone_start + palette_index]
                        self.assertEqual(resolved, model.vertices[vertex * 48 + 16 + influence])

    def test_curated_skin_face_pairs_are_indexed_and_independent(self):
        report = pack.load_json(visuals.ROOT / "integration" / "visual-preparation.json")
        for sex, details in report["sexes"].items():
            self.assertEqual(len(details["profile"]["skins"]), 5)
            self.assertEqual(len(details["profile"]["face_choices"]), 4)
            self.assertEqual(len(details["appearance"]), 50 if sex == "male" else 55)
            manifest = pack.load_manifest("skyborne")
            self.assertEqual([skin["choice_id"] for skin in details["profile"]["skins"]],
                             manifest["appearance"]["skin_choices"][sex])
            for entry in details["appearance"]:
                path = visuals.OUTPUT.joinpath(*pack.PureWindowsPath(entry["path"]).parts)
                blp = pack.Blp.parse(path.read_bytes(), str(path))
                self.assertEqual(blp.compression, 1)
                self.assertEqual(blp.alpha_size, 0)
                self.assertTrue(all(value >> 24 == 0 for value in blp.palette))
                self.assertIn((blp.width, blp.height), ((512, 512), (256, 128), (256, 64)))


if __name__ == "__main__":
    unittest.main()
