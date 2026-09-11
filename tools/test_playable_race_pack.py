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
    RawWdbc,
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


class RawWdbcContractTest(unittest.TestCase):
    @staticmethod
    def _wdbc(records: list[bytes], fields: int, record_size: int, strings: bytes = b"\0") -> bytes:
        header = struct.pack("<4s4I", b"WDBC", len(records), fields, record_size, len(strings))
        return header + b"".join(records) + strings

    def test_packed_char_start_outfit_changes_only_race_byte_and_remains_valid(self):
        record = bytearray(296)
        record[4] = 19
        record[5] = 0xA5
        record[8:12] = struct.pack("<I", 0x12345678)
        source = self._wdbc([bytes(record)], 77, 296, b"")

        donor = RawWdbc(source)
        changed = donor.remap_race_records("CharStartOutfit", 19, 20)
        output = donor.build(changed)
        parsed = RawWdbc(output)

        self.assertEqual(parsed.header, (b"WDBC", 1, 77, 296, 0))
        self.assertEqual(len(output), 20 + 296)
        self.assertEqual(parsed.records[0][4], 20)
        self.assertEqual(parsed.records[0][5:], record[5:])
        self.assertEqual(parsed.records[0][:4], record[:4])

    def test_byte_race_and_standard_race_fields_round_trip_without_malformed_output(self):
        packed = self._wdbc([bytes((19, 6)), bytes((7, 8))], 2, 2, b"")
        namegen_record = bytearray(16)
        namegen_record[8:12] = struct.pack("<I", 20)
        namegen = self._wdbc([bytes(namegen_record)], 4, 16)

        packed_donor = RawWdbc(packed)
        namegen_donor = RawWdbc(namegen)
        packed_output = packed_donor.build(packed_donor.remap_race_records("CharBaseInfo", 19, 20))
        namegen_output = namegen_donor.build(namegen_donor.remap_race_records("NameGen", 20, 18))

        self.assertEqual(RawWdbc(packed_output).records, (bytes((20, 6)), bytes((7, 8))))
        self.assertEqual(RawWdbc(namegen_output).records[0][8:12], struct.pack("<I", 18))
        self.assertEqual(len(packed_output), 24)
        self.assertEqual(len(namegen_output), 37)


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
