from __future__ import annotations

import json
from pathlib import Path
import struct
import unittest

from retroporter.config import DEFAULT
from retroporter.player_runtime import prepare_maghar_runtime
from wotlkconv.m2.model import parse_m2
from wotlkconv.m2.skin import parse_skin


SOURCE = DEFAULT.work_root / "maghar" / "output" / "patch-root" / "custom" / "maghar" / "character" / "orc"


@unittest.skipUnless((SOURCE / "male" / "orcmale_hd.m2").is_file(), "converted Mag'har assets are not available")
class MagharPlayerRuntimeTests(unittest.TestCase):
    def test_retail_player_atlas_is_split_without_replacing_geometry(self) -> None:
        report_path = prepare_maghar_runtime(DEFAULT)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        runtime = report_path.parent / "custom" / "maghar" / "character" / "orc"

        for sex, stem in (("male", "orcmale_hd"), ("female", "orcfemale_hd")):
            source_model = parse_m2((SOURCE / sex / f"{stem}.m2").read_bytes(), f"source-{sex}")
            model = parse_m2((runtime / sex / f"{stem}.m2").read_bytes(), f"runtime-{sex}")
            skin = parse_skin((runtime / sex / f"{stem}00.skin").read_bytes(), f"runtime-{sex}-skin")

            self.assertEqual(model.vertex_count, source_model.vertex_count)
            self.assertEqual(len(model.vertices), len(source_model.vertices))
            self.assertEqual(report["sexes"][sex]["body_vertices"] + report["sexes"][sex]["head_vertices"],
                             report["sexes"][sex]["body_vertices"] + report["sexes"][sex]["head_vertices"])
            self.assertEqual(len([t for t in model.textures if t.get("type") == 15]), 0)
            self.assertEqual(len([t for t in model.textures if t.get("type") == 8]), 1)

            head_slot = report["sexes"][sex]["head_texture_slot"]
            head_batches = 0
            for raw in skin.batches:
                values = struct.unpack("<12H", raw)
                count = values[7]
                combo = values[8]
                slots = model.texture_combos[combo:combo + count]
                if head_slot in slots:
                    head_batches += 1
            self.assertEqual(head_batches, report["sexes"][sex]["head_batches"])
            self.assertGreater(head_batches, 0)

            for key in ("body_u_range", "head_u_range"):
                low, high = report["sexes"][sex][key]
                self.assertGreaterEqual(low, -0.001)
                self.assertLessEqual(high, 1.001)

            self.assertNotIn("Orc2", (runtime / sex / f"{stem}.m2").as_posix())


if __name__ == "__main__":
    unittest.main()
