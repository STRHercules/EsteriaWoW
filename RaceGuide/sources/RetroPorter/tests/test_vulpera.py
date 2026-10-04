import unittest

from retroporter.cli import build_parser
from retroporter.races import RACES


class VulperaSourceTests(unittest.TestCase):
    def test_verified_source_and_cli(self):
        spec = RACES["vulpera"]
        self.assertEqual(spec.retail_race_ids, (35,))
        self.assertEqual(spec.core_model_file_ids, (1890761, 1890759))
        self.assertEqual(spec.asset_roots, ("character\\vulpera\\",))
        self.assertEqual(build_parser().parse_args(["discover", "--race", "vulpera"]).race, "vulpera")


if __name__ == "__main__":
    unittest.main()
