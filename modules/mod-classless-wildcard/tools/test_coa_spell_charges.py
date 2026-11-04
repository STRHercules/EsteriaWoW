import struct
import unittest

from coa_spell_charges import charge_rows


def dbc(fields, rows):
    return struct.pack('<4s4I', b'WDBC', len(rows), fields, fields * 4, 1) + b''.join(
        struct.pack('<%dI' % fields, *row) for row in rows) + b'\0'


class ChargeMetadataTests(unittest.TestCase):
    def test_ranks_share_pool_but_independent_abilities_do_not(self):
        links = dbc(2, [(500001, 10), (500002, 10), (500003, 10)])
        rows = charge_rows(links, dbc(3, [(10, 2, 5000)]), {500001, 500002, 500003},
                           '{12, 500001, 500001, 1} {12, 500001, 500002, 10}')
        self.assertEqual([row[3] for row in rows], [500001, 500001, 500003])

    def test_tinker_contract_and_missing_spell_filter(self):
        rows = charge_rows(dbc(2, [(707141, 110), (500003, 110)]),
                           dbc(3, [(110, 3, 5000)]), {707141, 504594}, '')
        self.assertEqual(rows, [(504594, 2, 8000, 504527, 323), (707141, 3, 6000, 707141, 110)])

    def test_conflicting_rank_metadata_is_rejected(self):
        with self.assertRaises(ValueError):
            charge_rows(dbc(2, [(1, 10), (2, 11)]), dbc(3, [(10, 2, 1000), (11, 3, 1000)]),
                        {1, 2}, '{12, 1, 1, 1} {12, 1, 2, 10}')

    def test_invalid_recovery_is_rejected(self):
        with self.assertRaises(ValueError):
            charge_rows(dbc(2, [(1, 10)]), dbc(3, [(10, 2, 0)]), {1}, '')


if __name__ == '__main__':
    unittest.main()
