from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name('generate_pack_v2.5.py')
SPEC = importlib.util.spec_from_file_location('generate_pack_v2_5', MODULE_PATH)
GENERATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATOR)


def write_dbc(path, rows):
    payload = b''.join(GENERATOR.ITEM_DBC_RECORD.pack(*row) for row in sorted(rows))
    header = GENERATOR.ITEM_DBC_HEADER.pack(
        GENERATOR.ITEM_DBC_MAGIC,
        len(rows),
        GENERATOR.ITEM_DBC_FIELD_COUNT,
        GENERATOR.ITEM_DBC_RECORD.size,
        1,
    )
    path.write_bytes(header + payload + b'\0')


def row(entry, display_id):
    return (entry, 4, 3, -1, 5, display_id, 7, 0)


class ItemDbcMergeTests(unittest.TestCase):
    def test_merges_all_sources_before_generated_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_a = root / 'vanilla.dbc'
            source_b = root / 'custom.dbc'
            output = root / 'merged.dbc'
            write_dbc(source_a, [row(1, 100), row(900010, 55243)])
            write_dbc(source_b, [row(900138, 134240)])

            stats = GENERATOR.merge_item_dbcs(
                [source_a, source_b],
                [row(200000, 9415)],
                output,
            )

            merged, _ = GENERATOR._read_item_dbc(output)
            self.assertEqual(set(merged), {1, 900010, 900138, 200000})
            self.assertEqual(stats['source_file_count'], 2)
            self.assertEqual(stats['source_row_count'], 3)
            self.assertEqual(stats['merged_row_count'], 4)

    def test_rejects_conflicting_rows_between_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_a = root / 'source-a.dbc'
            source_b = root / 'source-b.dbc'
            output = root / 'merged.dbc'
            write_dbc(source_a, [row(900138, 134240)])
            write_dbc(source_b, [row(900138, 134241)])

            with self.assertRaisesRegex(ValueError, 'conflicting Item.dbc source rows'):
                GENERATOR.merge_item_dbcs([source_a, source_b], [], output)

    def test_item_dbc_source_option_is_repeatable(self):
        args = GENERATOR.parse_args([
            '--item-dbc-source', 'vanilla.dbc',
            '--item-dbc-source', 'custom.dbc',
        ])

        self.assertEqual(args.item_dbc_sources, [Path('vanilla.dbc'), Path('custom.dbc')])


if __name__ == '__main__':
    unittest.main()
