"""Contract tests for the additive Vulpera/Pandaren client pack."""

from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parent
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from playable_race_pack import (  # noqa: E402
    collect_race_assets,
    remap_race_masks,
    remap_race_rows,
)


class RaceRowContractTest(unittest.TestCase):
    def test_remaps_target_rows_without_changing_other_fields(self):
        rows = [[19, 5, 141254, 141255], [99, 7, 1234, 5678]]

        actual = remap_race_rows("ChrRaces", rows, source_race=19, target_race=20)

        self.assertEqual(actual, [[20, 5, 141254, 141255], [99, 7, 1234, 5678]])
        self.assertEqual(rows, [[19, 5, 141254, 141255], [99, 7, 1234, 5678]])

    def test_remaps_only_the_declared_race_field(self):
        rows = [[901, 19, 4, 200, 201], [902, 7, 4, 300, 301]]

        actual = remap_race_rows("CharStartOutfit", rows, source_race=19, target_race=20)

        self.assertEqual(actual, [[901, 20, 4, 200, 201], [902, 7, 4, 300, 301]])

    def test_replaces_target_mask_and_preserves_unrelated_bits(self):
        source_mask = 1 << 19
        target_mask = 1 << 20
        unrelated = (1 << 4) | (1 << 31)

        actual = remap_race_masks(source_mask | unrelated, source_mask, target_mask)

        self.assertEqual(actual, target_mask | unrelated)

    def test_rejects_duplicate_primary_id_after_row_remap(self):
        rows = [[19, 5, 141254], [20, 5, 141687]]

        with self.assertRaisesRegex(ValueError, "duplicate row ID"):
            remap_race_rows("ChrRaces", rows, source_race=19, target_race=20)


class RaceAssetContractTest(unittest.TestCase):
    def _write_required_assets(self, root: Path) -> None:
        character_root = root / "Character"
        for race in ("vulpera", "Pandaren"):
            for gender in ("male", "female"):
                gender_root = character_root / race / gender
                gender_root.mkdir(parents=True)
                (gender_root / f"{race}-{gender}.m2").write_bytes(b"MD20" + struct.pack("<I", 264))
                (gender_root / f"{race}-{gender}.skin").write_bytes(b"skin")
                (gender_root / f"{race}-{gender}.anim").write_bytes(b"anim")

    def test_accepts_m2_model_and_records_asset_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_required_assets(root)

            report = collect_race_assets(root)

            self.assertIn("Character\\vulpera\\male\\vulpera-male.m2", report.asset_paths)
            self.assertEqual(report.file_counts["vulpera"], 6)
            self.assertEqual(len(report.sha256), 12)

    def test_rejects_mdx_model_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_required_assets(root)
            (root / "Character" / "vulpera" / "male" / "legacy.mdx").write_bytes(b"MDX")

            with self.assertRaisesRegex(ValueError, "unsupported .mdx asset"):
                collect_race_assets(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
