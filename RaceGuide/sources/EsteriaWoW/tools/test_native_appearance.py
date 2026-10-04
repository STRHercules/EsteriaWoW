"""Checks the independent native patch, byte codec, and expanded model data."""

import collections
import struct
import unittest
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from wotlkconv.m2 import parse_m2, parse_skin

import expanded_appearance_pack as expansion
import native_appearance_patch as native
import retroported_race_pack as p
from wow_xref import Pe


class NativeAppearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = p.CLIENT_DEFAULT
        installed = expansion.STAGE / "last-install.json"
        if installed.exists():
            report = p.load_json(installed)
            cls.baseline = Path(report.get("baseline_backup", report["backup"]))

    def test_patch_keeps_foundation_and_lua_validation_in_text(self):
        original = Pe(self.baseline / "Wow.exe")
        self.assertEqual(p.sha256(self.baseline / "Wow.exe"), native.EXPECTED_SHA256)
        patched = Pe(native.STAGE / "Wow.exe")
        report = p.load_json(native.STAGE / "exe-patch-report.json")
        self.assertEqual(original.read_va(0xDFE000, 29), patched.read_va(0xDFE000, 29))
        self.assertEqual(original.read_va(0x00464C4F, 1), patched.read_va(0x00464C4F, 1))
        self.assertEqual(original.read_va(0x0086B5A0, 85), patched.read_va(0x0086B5A0, 85))
        callback = int(report["lua_callback_va"], 16)
        text = next(section for section in patched.sections if section[0] == ".text")
        self.assertTrue(patched.image_base + text[1] <= callback < patched.image_base + text[1] + text[2])
        disassembler = Cs(CS_ARCH_X86, CS_MODE_32)
        for site in report["sites"]:
            address = int(site["va"], 16)
            instructions = list(disassembler.disasm(patched.read_va(address, 5), address))
            self.assertEqual(instructions[0].mnemonic, "jmp")
            target = int(site["thunk"], 16)
            self.assertEqual(int(instructions[0].op_str, 16), target)
            self.assertTrue(list(disassembler.disasm(patched.read_va(target, 8), target)))

    def test_all_independent_choice_states_fit_and_roundtrip(self):
        report = p.load_json(expansion.ROOT / "preparation.json")
        for sex, row in report["sexes"].items():
            descriptors = expansion.descriptors(row["profile"])
            self.assertEqual([offset for offset, _, _ in descriptors],
                             [0x28, 0x2C, 0x34, 0x24, 0x28, 0x30, 0x30, 0x30, 0x2C, 0x34])
            by_field = collections.defaultdict(list)
            for offset, count, factor in descriptors:
                by_field[offset].append((count, factor))
            for options in by_field.values():
                size = max(count * factor for count, factor in options)
                self.assertLessEqual(size, 256)
                combinations = set()
                for encoded in range(size):
                    values = tuple((encoded // factor) % count for count, factor in options)
                    self.assertEqual(encoded, sum(value * factor for value, (_, factor) in zip(values, options)))
                    combinations.add(values)
                self.assertEqual(len(combinations), size)
                for encoded in range(size):
                    for index, (count, factor) in enumerate(options):
                        old = (encoded // factor) % count
                        for delta in (-1, 1):
                            changed = encoded - old * factor + ((old + delta) % count) * factor
                            for other, (other_count, other_factor) in enumerate(options):
                                if other != index:
                                    self.assertEqual((encoded // other_factor) % other_count,
                                                     (changed // other_factor) % other_count)

    def test_expanded_geometry_has_full_hair_and_no_horns(self):
        report = p.load_json(expansion.ROOT / "preparation.json")
        for sex, row in report["sexes"].items():
            model_path = expansion.ART.joinpath(*p.PureWindowsPath(row["model_path"]).parts)
            model = parse_m2(model_path.read_bytes())
            skin = parse_skin(model_path.with_name(model_path.stem + "00.skin").read_bytes())
            self.assertLessEqual(model.vertex_count, 65535)
            self.assertLessEqual(len(skin.vertices), 65535)
            geosets = {int.from_bytes(submesh[:2], "little") for submesh in skin.submeshes}
            self.assertFalse(any(300 <= geo < 400 for geo in geosets))
            self.assertTrue(set(range(201, 205)) <= geosets)
            for color in range(8):
                self.assertTrue({geo + color * 100 for geo in row["profile"]["feather_geosets"] if geo} <= geosets)
            self.assertTrue(set(row["profile"]["hair_geosets"]) <= geosets)
            self.assertTrue(any(int.from_bytes(submesh[2:4], "little") for submesh in skin.submeshes))
            for submesh in skin.submeshes:
                self.assertLessEqual(int.from_bytes(submesh[12:14], "little"), 75)
                start = int.from_bytes(submesh[8:10], "little") | (int.from_bytes(submesh[2:4], "little") << 16)
                count = int.from_bytes(submesh[10:12], "little")
                self.assertLessEqual(start + count, len(skin.indices))
            self.assertIn(8, {texture["type"] for texture in model.textures})
            for submesh in skin.submeshes:
                first, count, _, _, bones, bone_start = struct.unpack_from("<6H", submesh, 4)
                for slot in range(first, first + count):
                    vertex = skin.vertices[slot]
                    for influence in range(4):
                        at = vertex * 48
                        if model.vertices[at + 12 + influence]:
                            local = skin.bones[slot * 4 + influence]
                            self.assertLess(local, bones)
                            self.assertEqual(model.bone_combos[bone_start + local],
                                             model.vertices[at + 16 + influence])

    def test_expanded_client_server_tables_and_non_skyborne_rows(self):
        stage = expansion.STAGE / "pack"
        report = p.load_json(expansion.STAGE / "expanded-pack-report.json")
        storm = p.Storm(p.DLL_DEFAULT)
        for name in report["dbc_tables"]:
            key = p.DBC_ROOT + name + ".dbc"
            original = p.RawWdbc(p._read_archive_entry(storm, self.baseline / p.GLOBAL_ARCHIVE_REL, key))
            a = p._read_archive_entry(storm, stage / p.GLOBAL_ARCHIVE_REL, key)
            b = p._read_archive_entry(storm, stage / p.LOCALE_ARCHIVE_REL, key)
            self.assertEqual(a, b, name)
            if name in p.SERVER_DBC_TABLES:
                self.assertEqual(a, (stage / "server" / "dbc" / (name + ".dbc")).read_bytes())
            changed = p.RawWdbc(a)

            def owned(row):
                if name == "CreatureModelData":
                    return p._value(row, 0) in (120052, 120053)
                if name in p.WDBC_LAYOUTS:
                    layout = p.WDBC_LAYOUTS[name]
                    return p._value(row, layout.race_offset, layout.race_width) in (52, 53)
                return False

            previous = collections.Counter(row for row in original.records if not owned(row))
            current = collections.Counter(changed.records)
            self.assertTrue(all(current[row] >= count for row, count in previous.items()), name)
            self.assertTrue(changed.strings.startswith(original.strings), name)
        sections = p.RawWdbc(p._read_archive_entry(storm, stage / p.GLOBAL_ARCHIVE_REL,
                                                 p.DBC_ROOT + "CharSections.dbc"))
        for gender, sex in ((0, "male"), (1, "female")):
            profile = p.load_json(expansion.ROOT / "preparation.json")["sexes"][sex]["profile"]
            rows = [row for row in sections.records if p._value(row, 4) == 53 and p._value(row, 8) == gender]
            count = len(profile["eye_textures"]) * 5
            skins = [row for row in rows if p._value(row, 12) == 0]
            self.assertEqual({p._value(row, 36) for row in skins}, set(range(count)))
            faces = [row for row in rows if p._value(row, 12) == 1]
            self.assertEqual(len(faces), count * 10 * len(profile["beard_geosets"]))


if __name__ == "__main__":
    unittest.main()
