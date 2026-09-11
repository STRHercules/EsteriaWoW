"""Contract tests for the additive Vulpera/Pandaren client pack."""

from __future__ import annotations

import os
import re
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch


TOOLS_ROOT = Path(__file__).resolve().parent
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

GLUE_STAGE_ROOT = Path(
    os.environ.get(
        "ESTERIA_PLAYABLE_RACE_GLUE_STAGE_ROOT",
        r"G:\Ascension\Ascension\resources\ascension-live\Data\Staging\Patch-B-vulpera-pandaren-task5",
    )
)
GLUE_INTERFACE_ROOT = GLUE_STAGE_ROOT / "Interface"
GLUE_XML_ROOT = GLUE_INTERFACE_ROOT / "GlueXML"
GLUE_SHARED_XML_ROOT = GLUE_INTERFACE_ROOT / "SharedXML"
PORTRAIT_CONVERTER = TOOLS_ROOT / "derive_playable_race_portraits.py"
PORTRAIT_SOURCE_ROOT = Path(
    r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq\Character"
)
PORTRAIT_HEADER_TEMPLATE = Path(
    r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\Ogre\Interface\GLUES\CHARACTERCREATE"
) / "UI-CharacterCreate-OgreMale.blp"
PORTRAIT_SOURCES = {
    "PandarenMale": Path("Pandaren/male/pandamalefacelower00_00.blp"),
    "PandarenFemale": Path("Pandaren/female/pandafemalefacelower00_00.blp"),
    "VulperaMale": Path("vulpera/male/vulperamalefacelower00_00.blp"),
    "VulperaFemale": Path("vulpera/female/vulperafemalefacelower00_00.blp"),
}
PORTRAIT_HASHES = {
    "PandarenMale": "1248eb90183a150780d5ebf4f98b2a3a02ced0f5273ca2430ebf59c1f73cbef5",
    "PandarenFemale": "a7559f3221dad2fd7a7406c1eb840af9cea244fb96845a28704fa99ef4c6b3a8",
    "VulperaMale": "7970929b1ad68f505b73f122a677ac9090595a163b123cd91fce0331bd8b698d",
    "VulperaFemale": "5f9e1ab83d668fe85b4a6efe4e38c9ebd6c25ac9646b769821a3e073eda2444c",
}

from playable_race_pack import (  # noqa: E402
    RACE_BYTE_LAYOUTS,
    RACE_ID_FIELDS,
    RawWdbc,
    WDBC_LAYOUTS,
    _build_continuations,
    _merge_manifest_entry,
    build_race_pack,
    collect_race_assets,
    remap_race_masks,
    remap_race_rows,
)
import playable_race_pack as packer  # noqa: E402
from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402


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

    def test_rejects_single_source_skill_race_class_info_bit(self):
        layout = WDBC_LAYOUTS["SkillRaceClassInfo"]
        record = bytearray(layout.record_size)
        record[layout.race_offset : layout.race_offset + layout.race_width] = (
            (1 << 19) | (1 << 4)
        ).to_bytes(layout.race_width, "little")
        raw = RawWdbc(
            struct.pack("<4s4I", b"WDBC", 1, layout.fields, layout.record_size, 0)
            + bytes(record)
        )

        with self.assertRaisesRegex(ValueError, "incomplete source race mask"):
            _build_continuations({"SkillRaceClassInfo": raw})

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


class ProductionPackContractTest(unittest.TestCase):
    def _write_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        dbc_root = root / "dbc"
        dbc_root.mkdir()
        model_root = root / "models"
        RaceAssetContractTest()._write_required_assets(model_root)
        patch_root = root / "patch-b"
        patch_root.mkdir()
        (patch_root / "Interface.txt").write_bytes(b"unchanged")
        (patch_root / "WXL-DBC.MANIFEST").write_bytes(b"# existing\n")

        for table_name, layout in WDBC_LAYOUTS.items():
            records = []
            if table_name in RACE_ID_FIELDS:
                for race in (19, 20):
                    record = bytearray(layout.record_size)
                    record[layout.race_offset : layout.race_offset + layout.race_width] = race.to_bytes(
                        layout.race_width, "little"
                    )
                    records.append(bytes(record))
            else:
                record = bytearray(layout.record_size)
                mask = (1 << 19) | (1 << 20) | (1 << 4)
                record[layout.race_offset : layout.race_offset + layout.race_width] = mask.to_bytes(
                    layout.race_width, "little"
                )
                records.append(bytes(record))
            header = struct.pack("<4s4I", b"WDBC", len(records), layout.fields, layout.record_size, 0)
            (dbc_root / f"{table_name}.dbc").write_bytes(header + b"".join(records))
        return dbc_root, model_root, patch_root

    def test_logical_field_map_remains_separate_from_verified_byte_layouts(self):
        self.assertEqual(RACE_ID_FIELDS["CharSections"], 0)
        self.assertEqual(RACE_ID_FIELDS["CharacterFacialHairStyles"], 0)
        self.assertEqual(RACE_ID_FIELDS["NameGen"], 2)
        self.assertEqual(RACE_ID_FIELDS["CreatureDisplayInfoExtra"], 1)
        self.assertEqual(RACE_BYTE_LAYOUTS["CharSections"], (4, 4))
        self.assertEqual(RACE_BYTE_LAYOUTS["CharacterFacialHairStyles"], (4, 4))
        self.assertEqual(RACE_BYTE_LAYOUTS["CharBaseInfo"], (0, 1))
        self.assertEqual(RACE_BYTE_LAYOUTS["CharStartOutfit"], (4, 1))

    def test_production_continuation_rejects_duplicate_chr_race_ids(self):
        layout = WDBC_LAYOUTS["ChrRaces"]
        record = bytearray(layout.record_size)
        record[:4] = (19).to_bytes(4, "little")
        raw = RawWdbc(
            struct.pack("<4s4I", b"WDBC", 2, layout.fields, layout.record_size, 0)
            + bytes(record)
            + bytes(record)
        )

        with self.assertRaisesRegex(ValueError, "duplicate row ID"):
            _build_continuations({"ChrRaces": raw})

    def test_rejects_patch_source_output_ancestor_overlap(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            patch_root = root / "patch-b"
            patch_root.mkdir()

            with self.assertRaisesRegex(ValueError, "overlap"):
                build_race_pack(root / "missing-dbc", root / "missing-models", patch_root, patch_root / "stage")
            with self.assertRaisesRegex(ValueError, "overlap"):
                build_race_pack(root / "missing-dbc", root / "missing-models", patch_root, root)

    def test_rejects_donor_source_output_overlap_for_dbc_and_models(self):
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as sibling_temporary:
            root = Path(temporary)
            sibling = Path(sibling_temporary)
            patch_root = sibling / "patch-b"
            patch_root.mkdir()
            for donor_name in ("dbc", "models"):
                donor_root = root / donor_name
                donor_root.mkdir()
                other_dbc = sibling / f"{donor_name}-other-dbc"
                other_model = sibling / f"{donor_name}-other-model"
                other_dbc.mkdir()
                other_model.mkdir()

                with self.assertRaisesRegex(ValueError, "overlap"):
                    build_race_pack(
                        donor_root if donor_name == "dbc" else other_dbc,
                        donor_root if donor_name == "models" else other_model,
                        patch_root,
                        donor_root / "stage",
                    )
                with self.assertRaisesRegex(ValueError, "overlap"):
                    build_race_pack(
                        donor_root if donor_name == "dbc" else other_dbc,
                        donor_root if donor_name == "models" else other_model,
                        patch_root,
                        root,
                    )

    def test_manifest_case_variant_merges_through_collision_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            dbc_root, model_root, patch_root = self._write_fixture(Path(temporary))
            output_root = Path(temporary) / "staged"

            report = build_race_pack(dbc_root, model_root, patch_root, output_root)

            manifests = [
                path
                for path in output_root.rglob("*")
                if path.is_file() and path.name.casefold() == "wxl-dbc.manifest"
            ]
            self.assertEqual(len(manifests), 1)
            manifest = manifests[0].read_text(encoding="utf-8")
            self.assertIn("# existing", manifest)
            self.assertIn("DBFilesClient/ChrRaces.dbc1-vulpera-pandaren", manifest)
            self.assertIn("DBFilesClient/SkillRaceClassInfo.dbc1-vulpera-pandaren", manifest)
            self.assertEqual(len(report.continuations), 12)

            mask = RawWdbc(report.continuations["DBFilesClient/SkillRaceClassInfo.dbc1-vulpera-pandaren"])
            value = RawWdbc._value(mask.records[0], RACE_BYTE_LAYOUTS["SkillRaceClassInfo"][0], 4)
            self.assertEqual(value & (1 << 19), 0)
            self.assertTrue(value & (1 << 20))
            self.assertTrue(value & (1 << 18))
            self.assertTrue(value & (1 << 4))

    def test_rejects_conflicting_manifest_case_variants(self):
        entries = {"wxl-dbc.manifest": b"one", "WXL-DBC.MANIFEST": b"two"}

        with self.assertRaisesRegex(ValueError, "archive path collision"):
            _merge_manifest_entry(entries, b"# additions\n")

    def test_rejects_stale_output_directory_through_production_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            dbc_root, model_root, patch_root = self._write_fixture(Path(temporary))
            output_root = Path(temporary) / "staged"
            output_root.mkdir()
            (output_root / "stale.bin").write_bytes(b"stale")

            with self.assertRaisesRegex(ValueError, "fresh"):
                build_race_pack(dbc_root, model_root, patch_root, output_root)

    @unittest.skipUnless(DLL_DEFAULT.is_file(), "StormLib is required for archive staging")
    def test_archive_staging_publishes_completed_directory_and_cleans_temporary_sibling(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dbc_root, model_root, _ = self._write_fixture(root)
            patch_root = root / "patch-b.MPQ"
            Storm(DLL_DEFAULT).create_archive(
                patch_root,
                {"Interface.txt": b"unchanged", "WXL-DBC.MANIFEST": b"# existing\n"},
            )
            output_root = root / "staged"
            real_replace = packer.os.replace
            observations = []

            def guarded_replace(source, destination):
                observations.append((Path(source), Path(destination), output_root.exists()))
                self.assertFalse(output_root.exists())
                self.assertEqual(Path(destination), output_root)
                real_replace(source, destination)

            with patch.object(packer.os, "replace", side_effect=guarded_replace):
                report = build_race_pack(dbc_root, model_root, patch_root, output_root)

            self.assertEqual(report.staged_root, str(output_root / "patch-b-vulpera-pandaren.MPQ"))
            self.assertEqual(len(observations), 1)
            self.assertTrue(output_root.is_dir())
            self.assertTrue(Path(report.staged_root).is_file())
            self.assertEqual(list(root.glob(f".{output_root.name}.tmp-*")), [])


class GlueContractTest(unittest.TestCase):
    def _read(self, root: Path, name: str) -> str:
        path = root / name
        self.assertTrue(path.is_file(), f"missing staged Glue file: {path}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _xml_elements(root, tag):
        return (element for element in root.iter() if element.tag.rsplit("}", 1)[-1] == tag)

    def _run_portrait_converter(self, output_dir: Path, source_paths: dict[str, Path], header: Path):
        command = [
            sys.executable,
            str(PORTRAIT_CONVERTER),
            "--output-dir",
            str(output_dir),
            "--header-template",
            str(header),
        ]
        command.extend(
            argument
            for key, source in source_paths.items()
            for argument in (f"--{key.lower()}", str(source))
        )
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def test_converter_reproduces_explicit_portrait_identity(self):
        source_paths = {key: PORTRAIT_SOURCE_ROOT / relative for key, relative in PORTRAIT_SOURCES.items()}
        for source in source_paths.values():
            self.assertTrue(source.is_file(), source)
        with tempfile.TemporaryDirectory() as temporary:
            result = self._run_portrait_converter(Path(temporary), source_paths, PORTRAIT_HEADER_TEMPLATE)
            self.assertEqual(result.returncode, 0, result.stderr)
            for key, expected_hash in PORTRAIT_HASHES.items():
                output = Path(temporary) / f"UI-CharacterCreate-{key}.blp"
                self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(), expected_hash, output)

    def test_converter_rejects_malformed_source_and_header(self):
        source_paths = {key: PORTRAIT_SOURCE_ROOT / relative for key, relative in PORTRAIT_SOURCES.items()}
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            malformed_source = temporary_root / PORTRAIT_SOURCES["PandarenMale"]
            malformed_source.parent.mkdir(parents=True)
            malformed_source.write_bytes(b"not a blp")
            bad_sources = dict(source_paths)
            bad_sources["PandarenMale"] = malformed_source
            result = self._run_portrait_converter(temporary_root / "bad-source", bad_sources, PORTRAIT_HEADER_TEMPLATE)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expected BLP2 magic", result.stderr)

            malformed_header = temporary_root / "bad-header.blp"
            malformed_header.write_bytes(b"BLP2")
            result = self._run_portrait_converter(temporary_root / "bad-header", source_paths, malformed_header)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("portrait header template is truncated", result.stderr)

    def test_converter_rejects_trailing_bytes_after_final_mip(self):
        from derive_playable_race_portraits import validate_portrait

        asset = GLUE_INTERFACE_ROOT / "Glues" / "CharacterCreate" / "UI-CharacterCreate-PandarenMale.blp"
        with self.assertRaisesRegex(ValueError, "does not end at file length"):
            validate_portrait(asset.read_bytes() + b"trailing", asset)

    def test_character_create_uses_thirteen_race_buttons_and_bounded_loops(self):
        source = self._read(GLUE_XML_ROOT, "CharacterCreate.lua")

        self.assertRegex(source, r"(?m)^MAX_RACES\s*=\s*13\s*;")
        for function_name in ("HighlightValidRaces", "StopHighlightingRaces"):
            function = re.search(
                rf"function\s+CharCreateClassButtonMixin:{function_name}\(\)(.*?)(?=\nend)",
                source,
                re.DOTALL,
            )
            self.assertIsNotNone(function, function_name)
            self.assertRegex(function.group(1), r"for\s+i\s*=\s*1\s*,\s*MAX_RACES\b")

    def test_character_create_has_ordinal_buttons_for_target_races(self):
        root = ET.parse(GLUE_XML_ROOT / "CharacterCreate.xml").getroot()
        buttons = {
            button.attrib["name"]: button
            for button in self._xml_elements(root, "CheckButton")
            if button.attrib.get("name", "").startswith("CharCreateRaceButton")
        }

        for ordinal in (12, 13):
            self.assertIn(f"CharCreateRaceButton{ordinal}", buttons)
            self.assertEqual(buttons[f"CharCreateRaceButton{ordinal}"].attrib.get("id"), str(ordinal))
            self.assertEqual(
                buttons[f"CharCreateRaceButton{ordinal}"].attrib.get("inherits"),
                "CharCreateRaceButtonTemplate",
            )
        for button in buttons.values():
            self.assertNotIn(button.attrib.get("id"), {"18", "20"})

        anchor_12 = next(self._xml_elements(buttons["CharCreateRaceButton12"], "Anchor"))
        anchor_13 = next(self._xml_elements(buttons["CharCreateRaceButton13"], "Anchor"))
        self.assertEqual(anchor_12.attrib.get("relativeTo"), "CharCreateRaceButton11")
        self.assertEqual(anchor_13.attrib.get("relativeTo"), "CharCreateRaceButton12")
        self.assertEqual(anchor_12.attrib.get("relativePoint"), "BOTTOMLEFT")
        self.assertEqual(anchor_13.attrib.get("relativePoint"), "BOTTOMLEFT")
        self.assertEqual(anchor_12.attrib.get("y"), "-30")
        self.assertEqual(anchor_13.attrib.get("y"), "-30")

    def test_glue_declares_only_alliance_pandaren_and_vulpera_text(self):
        localization = self._read(GLUE_XML_ROOT, "GlueLocalization.lua")

        for key in (
            "RACE_INFO_PANDAREN",
            "RACE_INFO_PANDAREN_FEMALE",
            "RACE_INFO_VULPERA",
            "RACE_INFO_VULPERA_FEMALE",
        ):
            self.assertRegex(localization, rf"(?m)^{key}\s*=")

        self.assertNotRegex(localization, r"(?i)PANDAREN[_ ]?HORDE")
        self.assertNotRegex(localization, r"(?m)^ABILITY_INFO_(?:PANDAREN|VULPERA)")

    def test_glue_has_target_icon_coordinates_and_explicit_gender_assets(self):
        character_create = self._read(GLUE_XML_ROOT, "CharacterCreate.lua")
        shared_constants = self._read(GLUE_SHARED_XML_ROOT, "SharedConstants.lua")
        combined = character_create + "\n" + shared_constants

        for key in (
            "PANDAREN_MALE",
            "PANDAREN_FEMALE",
            "VULPERA_MALE",
            "VULPERA_FEMALE",
        ):
            self.assertRegex(combined, rf"\[\"{key}\"\]\s*=\s*\{{[^}}]+\}}")

        expected_texture_paths = {
            "PANDAREN_MALE": r"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-PandarenMale",
            "PANDAREN_FEMALE": r"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-PandarenFemale",
            "VULPERA_MALE": r"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VulperaMale",
            "VULPERA_FEMALE": r"Interface\\Glues\\CharacterCreate\\UI-CharacterCreate-VulperaFemale",
        }
        for key, expected_path in expected_texture_paths.items():
            match = re.findall(rf'\["{key}"\]\s*=\s*"([^"]+)"', shared_constants)
            self.assertEqual(match, [expected_path], key)
            coords = re.findall(rf'\["{key}"\]\s*=\s*\{{([^}}]+)\}}', shared_constants)
            self.assertEqual(coords, [" 0, 1, 0, 1 "], key)

        expected_assets = {
            f"{race}{gender}": GLUE_INTERFACE_ROOT
            / "Glues"
            / "CharacterCreate"
            / f"UI-CharacterCreate-{race}{gender}.blp"
            for race in ("Pandaren", "Vulpera")
            for gender in ("Male", "Female")
        }
        for key, asset in expected_assets.items():
            self.assertTrue(asset.is_file(), f"missing_requirements: explicit target icon asset: {asset}")
            data = asset.read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), PORTRAIT_HASHES[key], asset)
            self.assertEqual(data[:4], b"BLP2", asset)
            self.assertEqual(data[8:12], bytes((3, 8, 8, 1)), asset)
            self.assertEqual(struct.unpack("<II", data[12:20]), (64, 64), asset)
            offsets = struct.unpack("<16I", data[20:84])
            sizes = struct.unpack("<16I", data[84:148])
            expected_sizes = (16384, 4096, 1024, 256, 64, 16, 4)
            expected_offsets = (1172, 17556, 21652, 22676, 22932, 22996, 23012)
            self.assertEqual(tuple(offsets[:7]), expected_offsets, asset)
            self.assertEqual(tuple(sizes[:7]), expected_sizes, asset)
            self.assertFalse(any(sizes[7:]), asset)
            end = 1172
            for offset, size in zip(offsets[:7], sizes[:7]):
                self.assertEqual(offset, end, asset)
                self.assertGreater(size, 0, asset)
                self.assertLessEqual(offset + size, len(data), asset)
                end = offset + size
            self.assertEqual(end, len(data), asset)
            base = data[offsets[0] : offsets[0] + sizes[0]]
            self.assertTrue(any(base[3::4]), f"empty BLP2 alpha: {asset}")

    def test_glue_has_alliance_and_horde_lighting_aliases_without_horde_pandaren_path(self):
        parent = self._read(GLUE_XML_ROOT, "GlueParent.lua")

        for table_name in ("CharModelFogInfo", "CharModelGlowInfo", "GlueAmbienceTracks", "RaceLights"):
            self.assertIn(table_name, parent)
            for race in ("PANDAREN", "VULPERA"):
                self.assertRegex(
                    parent,
                    rf'(?m){table_name}\["{race}"\]\s*=\s*{table_name}\["ALLIANCE"\];',
                )
        self.assertNotRegex(parent, r"(?i)PANDAREN[_ ]?HORDE")


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
