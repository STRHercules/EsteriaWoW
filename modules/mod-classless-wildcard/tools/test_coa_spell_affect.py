import struct
import unittest

from coa_spell_affect import client_targets, dbc_rows, imported_targets


def table(rows, fields):
    records = b"".join(struct.pack("<%dI" % fields, *row) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, fields * 4, 1) + records + b"\0"


class SpellAffectExportTest(unittest.TestCase):
    def test_client_rank_roots_expand_without_changing_exact_targets(self):
        self.assertEqual(client_targets([(1, -100), (2, 6940), (3, -200)],
                                         {100: [(100, 1), (101, 10)]}),
                         [(1, 100), (1, 101), (2, 6940), (3, 200)])

    def test_only_imported_coa_modifiers_and_signed_rank_targets(self):
        spells = []
        for spell, family in ((500001, 31), (500002, 31), (100, 10)):
            row = [0] * 234
            row[0], row[208] = spell, family
            spells.append(row)
        affect = table([(1, 500001, 700001), (2, 500001, 0x100000000 - 700002),
                        (3, 500002, 700003), (4, 100, 700004), (5, 500001, 700001)], 3)
        self.assertEqual(imported_targets(affect, table(spells, 234), {500001, 100}),
                         [(500001, -700002), (500001, 700001)])

    def test_reject_truncated_table_and_wrong_field_count(self):
        with self.assertRaises(ValueError):
            dbc_rows(table([(1, 2, 3)], 3)[:-2], 3)
        with self.assertRaises(ValueError):
            dbc_rows(table([(1, 2, 3)], 3), 2)


if __name__ == "__main__":
    unittest.main()
