import struct
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from patch_kultiran_head_attachment import patch_real_attachment  # noqa: E402


class HeadAttachmentPatchTest(unittest.TestCase):
    def test_patches_header_referenced_attachment_without_touching_decoy_table(self):
        payload = bytearray(0x500)
        struct.pack_into("<II", payload, 0xF0, 2, 0x300)
        struct.pack_into("<I", payload, 0x300, 0)
        struct.pack_into("<IHH3f", payload, 0x328, 11, 175, 0, 0.1, 0.0, 2.6)
        struct.pack_into("<IHH3f", payload, 0x400, 11, 175, 0, -0.06, 0.0, 2.39)

        patched, old = patch_real_attachment(bytes(payload), (-0.04, 0.0, 2.41))

        for actual, expected in zip(old, (0.1, 0.0, 2.6)):
            self.assertAlmostEqual(actual, expected, places=6)
        for actual, expected in zip(
            struct.unpack_from("<3f", patched, 0x328 + 8),
            (-0.04, 0.0, 2.41),
        ):
            self.assertAlmostEqual(actual, expected, places=6)
        for actual, expected in zip(
            struct.unpack_from("<3f", patched, 0x400 + 8),
            (-0.06, 0.0, 2.39),
        ):
            self.assertAlmostEqual(actual, expected, places=6)


if __name__ == "__main__":
    unittest.main()
