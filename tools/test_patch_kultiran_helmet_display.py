import struct
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from patch_kultiran_helmet_display import patch_display_models  # noqa: E402


class HelmetDisplayPatchTest(unittest.TestCase):
    def test_repoints_only_requested_display_model_names(self):
        strings = b"\0HelmCalE.mdx\0HelmCalB.mdx\0Unchanged\0"
        rows = []
        for display_id, model_offset in ((64427, 1), (64429, 14), (70000, 27)):
            row = bytearray(100)
            struct.pack_into("<I", row, 0, display_id)
            struct.pack_into("<I", row, 4, model_offset)
            row[8:12] = b"keep"
            rows.append(bytes(row))
        data = struct.pack("<4s4I", b"WDBC", 3, 25, 100, len(strings)) + b"".join(rows) + strings

        patched, report = patch_display_models(
            data,
            {
                64427: "helm_leather_raidrogue_h_01.mdx",
                64429: "helm_leather_raidrogue_h_01.mdx",
            },
        )

        _magic, count, fields, record_size, string_size = struct.unpack_from("<4s4I", patched)
        self.assertEqual((count, fields, record_size), (3, 25, 100))
        self.assertGreaterEqual(string_size, len(strings))
        self.assertEqual(report[64427]["before"], "HelmCalE.mdx")
        self.assertEqual(report[64427]["after"], "helm_leather_raidrogue_h_01.mdx")
        self.assertEqual(report[64429]["before"], "HelmCalB.mdx")
        self.assertEqual(report[64429]["after"], "helm_leather_raidrogue_h_01.mdx")

        for index, display_id in enumerate((64427, 64429, 70000)):
            row = patched[20 + index * 100 : 20 + (index + 1) * 100]
            self.assertEqual(struct.unpack_from("<I", row, 0)[0], display_id)
            self.assertEqual(row[8:12], b"keep")

        self.assertEqual(patch_display_models(patched, {
            64427: "helm_leather_raidrogue_h_01.mdx",
            64429: "helm_leather_raidrogue_h_01.mdx",
        })[0], patched)


if __name__ == "__main__":
    unittest.main()
