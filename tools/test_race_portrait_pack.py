"""Focused checks for the race portrait converter."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from derive_playable_race_portraits import _read_blp2_header, validate_portrait
from race_portrait_pack import (
    ICON_ART_DIAMETER,
    PORTRAIT_SIZE,
    circular_mask,
    compose_race_icon,
    portrait_bytes,
    race_key,
    ring_layer,
)


SOURCE = Path(r"R:\Users\Zach\Pictures\Portraits")


class RacePortraitPackTest(unittest.TestCase):
    def test_race_key_maps_the_picture_names_onto_client_file_strings(self):
        self.assertEqual(race_key("undead"), "scourge")
        self.assertEqual(race_key("panda"), "pandaren")
        self.assertEqual(race_key("kultiranhuman"), "kultiran")
        self.assertEqual(race_key("DarkIronDwarf"), "darkirondwarf")
        self.assertEqual(race_key("worgen"), "worgen")

    def test_mask_is_circular_with_opaque_centre_and_clear_corners(self):
        mask = circular_mask()
        self.assertEqual(mask.size, (PORTRAIT_SIZE, PORTRAIT_SIZE))
        self.assertEqual(mask.getpixel((PORTRAIT_SIZE // 2, PORTRAIT_SIZE // 2)), 255)
        self.assertLess(mask.getpixel((0, 0)), 8)
        self.assertLess(mask.getpixel((PORTRAIT_SIZE - 1, PORTRAIT_SIZE - 1)), 8)

    def test_ring_layer_keeps_only_the_outer_ring(self):
        icon = Image.new("RGBA", (PORTRAIT_SIZE, PORTRAIT_SIZE), (120, 120, 130, 255))
        ring = ring_layer(icon)
        self.assertEqual(ring.getchannel("A").getpixel((32, 32)), 0)
        self.assertGreater(ring.getchannel("A").getpixel((32, 1)), 200)
        composed = compose_race_icon(Image.new("RGBA", (PORTRAIT_SIZE, PORTRAIT_SIZE), (10, 20, 30, 255)), ring)
        self.assertEqual(composed.getpixel((32, 32))[:3], (10, 20, 30))
        self.assertGreater(composed.getchannel("A").getpixel((32, 1)), 200)
        self.assertLess(ICON_ART_DIAMETER, PORTRAIT_SIZE)

    @unittest.skipUnless((SOURCE / "Alliance").is_dir(), "supplied portrait sources are required")
    def test_converted_portrait_keeps_the_client_icon_header(self):
        source = SOURCE / "Alliance" / "Charactercreate-races_darkfallen-male_alliance.png"
        image = portrait_bytes(source, circular_mask())
        self.assertEqual(image.size, (PORTRAIT_SIZE, PORTRAIT_SIZE))
        self.assertEqual(image.getchannel("A").getpixel((0, 0)), 0)
        self.assertGreater(image.getchannel("A").getpixel((32, 32)), 200)

        from cars_mount_pack import DLL_DEFAULT, Storm
        from race_portrait_pack import ICON_TEMPLATE_ENTRY
        from pathlib import Path as _Path

        storm = Storm(DLL_DEFAULT)
        handle = storm.open_archive(_Path(r"G:\3.3.5a - Dev\Data\patch-Z.MPQ"))
        try:
            template = storm.read(handle, ICON_TEMPLATE_ENTRY)
        finally:
            storm.dll.SFileCloseArchive(handle)
        from derive_playable_race_portraits import encode_portrait

        encoded = encode_portrait(image, template)
        validate_portrait(encoded, _Path("portrait.blp"))
        fields, _ = _read_blp2_header(encoded, _Path("portrait.blp"))
        self.assertEqual(fields, (3, 8, 8, 1, PORTRAIT_SIZE, PORTRAIT_SIZE))


if __name__ == "__main__":
    unittest.main()
