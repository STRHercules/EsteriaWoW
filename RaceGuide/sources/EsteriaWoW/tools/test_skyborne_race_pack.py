"""Focused acceptance checks for Skyborne's staged client/server data."""

import collections
import unittest

import retroported_race_pack as pack
import skyborne_race_pack as skyborne


class SkyborneRaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = pack._build_root("skyborne")
        cls.storm = pack.Storm(pack.DLL_DEFAULT)
        cls.report = pack.load_json(cls.stage / "build-report.json")

    def read(self, root, table):
        return pack._read_archive_entry(self.storm, root / pack.GLOBAL_ARCHIVE_REL,
                                        pack.DBC_ROOT + table + ".dbc")

    def test_existing_data_and_maghar_payload_are_preserved(self):
        for name in self.report["dbc_tables"]:
            original = pack.RawWdbc(self.read(pack.CLIENT_DEFAULT, name))
            staged = pack.RawWdbc(self.read(self.stage, name))
            def owned(row):
                if name in pack.WDBC_LAYOUTS:
                    layout = pack.WDBC_LAYOUTS[name]
                    if pack._value(row, layout.race_offset, layout.race_width) in skyborne.RACES:
                        return True
                ids = pack.load_json(pack.ALLOCATION_PATH)["race_allocations"]["skyborne"].get(name)
                return isinstance(ids, dict) and pack._value(row, 0) in ids.values()

            previous = collections.Counter(row for row in original.records if not owned(row))
            current = collections.Counter(staged.records)
            self.assertTrue(all(current[row] >= count for row, count in previous.items()), name)
            self.assertTrue(staged.strings.startswith(original.strings), name)
        live = self.storm.open_archive(pack.CLIENT_DEFAULT / pack.ASSET_ARCHIVE_REL)
        staged = self.storm.open_archive(self.stage / pack.ASSET_ARCHIVE_REL)
        try:
            for name, *_ in self.storm.list_files(live):
                if name.casefold().startswith("custom\\maghar\\"):
                    self.assertEqual(self.storm.read(live, name), self.storm.read(staged, name), name)
        finally:
            self.storm.dll.SFileCloseArchive(live)
            self.storm.dll.SFileCloseArchive(staged)

    def test_factions_models_and_appearance_axes(self):
        manifest = pack.load_manifest("skyborne")
        allocations = pack.load_json(pack.ALLOCATION_PATH)["race_allocations"]["skyborne"]
        races = pack.RawWdbc(self.read(self.stage, "ChrRaces"))
        rows = {pack._value(row, 0): row for row in races.records}
        models = pack.RawWdbc(self.read(self.stage, "CreatureModelData"))
        model_rows = {pack._value(row, 0): row for row in models.records}
        appearances = pack.RawWdbc(self.read(self.stage, "CharSections"))
        for race in skyborne.RACES:
            donor = rows[manifest["source_races"][str(race)]]
            self.assertEqual(rows[race][8:16], donor[8:16])
            self.assertEqual(pack._string(races.strings, pack._value(rows[race], 44)).decode(),
                             manifest["client_file_strings"][str(race)])
            for sex, field in (("male", 4), ("female", 5)):
                self.assertEqual(pack._value(rows[race], field * 4), allocations["CreatureDisplayInfo"][sex])
                model = model_rows[allocations["CreatureModelData"][sex]]
                self.assertEqual(pack._string(models.strings, pack._value(model, 8)).decode(),
                                 manifest["models"][sex]["runtime_model_path"])
            for gender in (0, 1):
                selected = [row for row in appearances.records
                            if pack._value(row, 4) == race and pack._value(row, 8) == gender]
                skins = [row for row in selected if pack._value(row, 12) == 0]
                faces = [row for row in selected if pack._value(row, 12) == 1]
                self.assertEqual({pack._value(row, 36) for row in skins}, set(range(5)))
                self.assertEqual({(pack._value(row, 32), pack._value(row, 36)) for row in faces},
                                 {(face, skin) for face in range(4) for skin in range(5)})

    def test_shared_validation_and_glue_identity(self):
        result = pack.validate("skyborne", pack.CLIENT_DEFAULT)
        self.assertEqual(result["charsections_per_race"], 188)
        for relative in (pack.GLOBAL_ARCHIVE_REL, pack.LOCALE_ARCHIVE_REL):
            info = pack._read_archive_entry(self.storm, self.stage / relative,
                                            pack.GLUE_ROOT + "CharacterInfo.lua").decode()
            self.assertIn('[52] = { glueString = "SKYBORNE"', info)
            self.assertIn('[53] = { glueString = "SKYBORNEHORDE"', info)
            self.assertIn("if raceData.name == raceName then", info)
            strings = pack._read_archive_entry(self.storm, self.stage / relative,
                                               pack.GLUE_ROOT + "GlueStrings.lua").decode()
            self.assertIn('FACIAL_HAIR_SKYBORNE_FEATURES = "Features";', strings)
            create = pack._read_archive_entry(self.storm, self.stage / relative,
                                              pack.GLUE_ROOT + "CharacterCreate.lua").decode()
            self.assertIn('CharacterCustomizationButtonFrame3Text:SetText("Hair Style");', create)


if __name__ == "__main__":
    unittest.main()
