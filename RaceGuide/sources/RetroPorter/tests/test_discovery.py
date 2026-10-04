import unittest

from retroporter.discovery import collect_file_data_ids, rows_by_id


class FakeTable:
    def __init__(self, rows):
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)


class DiscoveryHelpersTests(unittest.TestCase):
    def test_collect_file_data_ids_recurses_and_ignores_other_integers(self):
        data = {
            "SkeletonFileDataID": 100,
            "OtherID": 999,
            "nested": {
                "TextureFileDataID": [200, 0, 201],
                "values": [{"ModelFileDataID": 300}],
            },
        }
        self.assertEqual(collect_file_data_ids(data), {100, 200, 201, 300})

    def test_rows_by_id_uses_explicit_id_when_present(self):
        table = FakeTable(
            [
                (10, {"ID": 100, "Name": "wanted"}),
                (20, {"ID": 200, "Name": "other"}),
                (300, {"Name": "row-id-fallback"}),
            ]
        )
        rows = rows_by_id(table, {100, 300})
        self.assertEqual([row["Name"] for row in rows], ["wanted", "row-id-fallback"])


if __name__ == "__main__":
    unittest.main()
