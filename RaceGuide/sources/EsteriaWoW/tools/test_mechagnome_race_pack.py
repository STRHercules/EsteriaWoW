"""Native Race47 appearance byte, geometry, and staged integration checks."""

import collections
import struct
import unittest

import mechagnome_race_pack as m


class MechagnomeTests(unittest.TestCase):
    def test_each_control_roundtrips_without_changing_other_controls(self):
        discovery = m.p.load_json(m.ROOT / "reports/discovery.json")
        for model in (73, 74):
            prof = m.profile(discovery, model)
            fields = collections.defaultdict(list)
            for offset, count, factor in m.descriptors(prof):
                fields[offset].append((count, factor))
            for options in fields.values():
                capacity = max(count * factor for count, factor in options)
                self.assertLessEqual(capacity, 256)
                for encoded in range(capacity):
                    values = [(encoded // factor) % count for count, factor in options]
                    self.assertEqual(encoded, sum(value * factor for value, (_, factor) in zip(values, options)))
                    for index, (count, factor) in enumerate(options):
                        changed = encoded - values[index] * factor + ((values[index] + 1) % count) * factor
                        for other, (other_count, other_factor) in enumerate(options):
                            if other != index:
                                self.assertEqual(values[other], (changed // other_factor) % other_count)
            self.assertEqual(m.counts(prof)["Modification"], 20)
            self.assertEqual(m.counts(prof)["Arm Upgrade"], 4)
            self.assertEqual(m.counts(prof)["Leg Upgrade"], 2)

    def test_prepared_model_has_every_mechanical_selector(self):
        report = m.p.load_json(m.ROOT / "integration/preparation.json")
        for row in report["sexes"].values():
            self.assertLessEqual(row["vertices"], 65535)
            self.assertTrue({301, 302, 303, 304, 501, 502, 1001, 1002,
                             702, 703, 704, 705, 1602, 1603, 1604, 1803} <= set(row["geosets"]))
        from wotlkconv.m2 import parse_m2

        for sex in ("male", "female"):
            source = m.source(f"custom\\mechagnome\\character\\mechagnome\\{sex}\\mechagnome{sex}.m2")
            old = m.v.read_player_model(source)
            new = parse_m2(m.ART.joinpath(*m.p.PureWindowsPath(report["sexes"][sex]["model_path"]).parts).read_bytes())
            self.assertEqual(old.sequences, new.sequences[:len(old.sequences)])
            for a, b in zip(old.bones, new.bones):
                for kind in ("translation", "rotation", "scale"):
                    for index in a[kind].external:
                        self.assertEqual(a[kind].timestamp_spans[index], b[kind].timestamp_spans[index])

    def test_movement_combat_and_emotes_have_animation_tracks(self):
        from wotlkconv.m2.types import value_size

        report = m.p.load_json(m.ROOT / "integration/preparation.json")
        for sex in ("male", "female"):
            path = m.ART.joinpath(*m.p.PureWindowsPath(report["sexes"][sex]["model_path"]).parts)
            model = m.v.read_player_model(path)
            # Walking/running/backwards, attacks, weapon ready, jump, sit, dance, cast.
            for animation in (4, 5, 13, 16, 17, 18, 19, 26, 37, 38, 39, 69, 96, 97, 60, 113):
                index = model.sequence_lookups[animation]
                self.assertNotEqual(index, 65535, (sex, animation))
                visited = set()
                while model.sequences[index]["flags"] & 0x40:
                    self.assertNotIn(index, visited, (sex, animation, "alias cycle"))
                    visited.add(index)
                    index = model.sequences[index]["alias_next"]
                seq = model.sequences[index]
                tracks = [b["rotation"] for b in model.bones if b["rotation"].global_sequence < 0]
                if seq["flags"] & 0x20:
                    self.assertGreater(sum(bool(t.values[index]) for t in tracks if index < len(t.values)), 10)
                else:
                    blob = path.with_name(f"{path.stem}{seq['id']:04d}-{seq['variation_index']:02d}.anim").read_bytes()
                    for track in tracks:
                        for spans, stride in ((track.timestamp_spans, 4),
                                              (track.value_spans, value_size(track.kind))):
                            if index < len(spans):
                                count, offset = spans[index]
                                if count:
                                    self.assertLessEqual(offset + count * stride, len(blob), (sex, animation))

    def test_eyeballs_glow_and_beards_keep_their_own_materials(self):
        from wotlkconv.m2 import parse_skin

        report = m.p.load_json(m.ROOT / "integration/preparation.json")
        for sex in ("male", "female"):
            path = m.ART.joinpath(*m.p.PureWindowsPath(report["sexes"][sex]["model_path"]).parts)
            model = m.v.read_player_model(path)
            skin = parse_skin(path.with_name(path.stem + "00.skin").read_bytes())
            eyeballs = 0
            for batch in skin.batches:
                geo = m.v.u16(skin.submeshes[m.v.u16(batch, 4)], 0)
                textures = [model.textures[i] for i in model.texture_combos[
                    m.v.u16(batch, 16):m.v.u16(batch, 16) + m.v.u16(batch, 14)]]
                if 1700 < geo < 1800:
                    self.assertTrue(all(t["type"] == 0 for t in textures))
                if sex == "male" and 100 <= geo < 200:
                    self.assertEqual([t["type"] for t in textures], [6])
                if any(t["type"] == 5 for t in textures):
                    eyeballs += 1
                    self.assertEqual(m.v.u16(batch, 14), 1)
                    self.assertEqual(model.materials[m.v.u16(batch, 10)]["blending_mode"], 0)
                    self.assertEqual(model.texture_coord_combos[m.v.u16(batch, 18)], 0)
            self.assertEqual(eyeballs, 1)

    def test_staged_archives_and_existing_profiles(self):
        self.assertTrue(m.validate()["verified"])
        data = (m.STAGE / "EsteriaAppearanceMaterials.bin").read_bytes()
        magic, version, count = struct.unpack_from("<3I", data)
        self.assertEqual((magic, version), (0x544D4145, 1))
        self.assertEqual(len(data), 12 + count * 188)

    def test_installed_language_skill_steps_match_gnome_starts(self):
        native = {int(row.split("\t")[0]): int(row.split("\t")[1]) for row in m.sql(
            "SELECT skill,`rank` FROM playercreateinfo_skills WHERE skill IN (98,313) "
            "AND (raceMask & 64) != 0;").splitlines()}
        exact = {int(row.split("\t")[0]): int(row.split("\t")[1]) for row in m.sql(
            "SELECT skill,`rank` FROM custom_race_start_skill WHERE race=47;").splitlines()}
        self.assertEqual(exact, native)
        self.assertEqual(set(exact), {98, 313})
        self.assertEqual({int(row) for row in m.sql(
            "SELECT spell FROM custom_race_start_spell WHERE race=47;").splitlines()}, {668, 7340})


if __name__ == "__main__":
    unittest.main()
