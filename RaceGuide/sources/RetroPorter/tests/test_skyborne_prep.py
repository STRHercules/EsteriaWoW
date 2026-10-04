import unittest

from retroporter.cli import build_parser
from retroporter.races import RACES


class SkybornePreparationTests(unittest.TestCase):
    def test_skyborne_is_asset_ready(self):
        spec = RACES["skyborne"]
        self.assertTrue(spec.ready_for_assets)
        self.assertEqual(spec.retail_race_ids, (95, 96))
        self.assertEqual(
            spec.core_model_file_ids,
            (7478487, 7478494, 7845092, 7845093, 2763972, 2763973),
        )

    def test_extract_accepts_alternate_source(self):
        args = build_parser().parse_args(
            [
                "extract-db2",
                "--race",
                "skyborne",
                "--source-root",
                r"G:\\ExampleForever",
                "--source-product",
                "wow_classic_beta",
            ]
        )
        self.assertEqual(args.race, "skyborne")
        self.assertEqual(args.source_product, "wow_classic_beta")
        self.assertEqual(args.source_root, r"G:\\ExampleForever")

    def test_plan_assets_accepts_alternate_source(self):
        args = build_parser().parse_args(
            [
                "plan-assets",
                "--race",
                "skyborne",
                "--source-root",
                r"D:\\Blizzard\\World of Warcraft",
                "--source-product",
                "wow_classic_beta",
            ]
        )
        self.assertEqual(args.race, "skyborne")
        self.assertEqual(args.source_product, "wow_classic_beta")
        self.assertEqual(args.source_root, r"D:\\Blizzard\\World of Warcraft")


if __name__ == "__main__":
    unittest.main()
