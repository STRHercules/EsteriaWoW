"""Small offline checks for server-data integrity and installation safeguards."""
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tarfile
import tempfile
import unittest

import prepare_data
import sync_housing_sql
import unpack_manastorm_items

ROOT = Path(__file__).resolve().parents[2]


class InstallTests(unittest.TestCase):
    def test_custom_script_loader_is_optional(self):
        cmake = shutil.which("cmake")
        if not cmake:
            self.skipTest("CMake is required for the script-discovery regression check")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            custom = root / "src/server/scripts/Custom"
            custom.mkdir(parents=True)
            (custom / "README.md").write_text("Local custom scripts\n")
            (root / "src/server/scripts/World").mkdir()
            macro = ROOT / "src/cmake/macros/ConfigureScripts.cmake"
            script = root / "check.cmake"
            script.write_text(f'''cmake_minimum_required(VERSION 3.16)
include("{macro.as_posix()}")
set(CMAKE_SOURCE_DIR "{root.as_posix()}")
GetScriptModuleList(discovered)
if("Custom" IN_LIST discovered OR NOT "World" IN_LIST discovered)
  message(FATAL_ERROR "Empty Custom group must be skipped without hiding normal scripts")
endif()
file(WRITE "{custom.as_posix()}/custom_script_loader.cpp" "void AddCustomScripts() {{}}\\n")
GetScriptModuleList(discovered)
if(NOT "Custom" IN_LIST discovered)
  message(FATAL_ERROR "Existing local custom loaders must remain enabled")
endif()
''', encoding="utf-8")
            subprocess.run([cmake, "-P", str(script)], check=True, capture_output=True)

    def test_manastorm_dataset(self):
        sql = unpack_manastorm_items.verified_sql().decode("utf-8")
        bundle = ROOT / "data/server/manastorm"
        manifest = json.loads((bundle / "manifest.json").read_text())
        ids = (bundle / "item-ids.txt").read_text().splitlines()
        self.assertEqual(len(ids), manifest["items"])
        self.assertEqual(len(set(ids)), manifest["items"])
        self.assertTrue(all(value.isdecimal() for value in ids))
        tables = set(re.findall(r"^INSERT INTO `([^`]+)`", sql, re.M))
        self.assertEqual(tables, {"item_template"})
        self.assertNotRegex(sql, r"(?im)^\s*(?:DROP|TRUNCATE|DELETE)\s+TABLE?\b")
        self.assertIn("ON DUPLICATE KEY UPDATE", sql)
        native = manifest["native_dbc"]
        data = (bundle / native["file"]).read_bytes()
        self.assertEqual(len(data), native["bytes"])
        self.assertEqual(prepare_data.digest(bundle / native["file"]), native["sha256"])
        magic, count, fields, record_size, strings = struct.unpack_from("<4s4I", data)
        self.assertEqual((magic, fields, record_size), (b"WDBC", 9, 36))
        self.assertEqual(len(data), 20 + count * record_size + strings)

    def test_manastorm_checksum_rejects_damage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "manifest.json").write_text(json.dumps({"archive": "items.gz", "sha256": "invalid"}))
            (root / "items.gz").write_bytes(b"damaged")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                unpack_manastorm_items.verified_sql(root)

    def test_published_dbc_bundle(self):
        bundle = ROOT / "data/server"
        manifest = json.loads((bundle / "manifest.json").read_text())
        archive = bundle / manifest["dbc_archive"]
        self.assertEqual(prepare_data.digest(archive), manifest["sha256"])
        with tarfile.open(archive) as dbcs:
            files = {member.name for member in dbcs if member.isfile()}
            self.assertEqual(files, set(manifest["files"]))
            for name, required in (("CreatureDisplayInfo", {17028}), ("VehicleSeat", {4689, 4692, 4693})):
                data = dbcs.extractfile(f"dbc/{name}.dbc").read()
                magic, count, fields, record_size, strings = struct.unpack_from("<4s4I", data)
                self.assertEqual(magic, b"WDBC")
                self.assertEqual(len(data), 20 + count * record_size + strings)
                self.assertEqual(record_size, fields * 4)
                ids = {struct.unpack_from("<I", data, 20 + i * record_size)[0] for i in range(count)}
                self.assertLessEqual(required, ids)

    def test_rejects_archive_traversal(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):
                prepare_data.destination(Path(temporary), "maps/../../outside")

    def test_incarnation_displays_are_shipped(self):
        sql = (ROOT / "data/sql/updates/pending_db_world/rev_20261117010000000_incarnations.sql").read_text()
        looks = set(map(int, re.findall(r"^INSERT INTO `esteria_incarnation` .*? VALUES \(\d+,(\d+),", sql, re.M)))
        self.assertTrue(looks)
        displays = set()
        manifest = json.loads((ROOT / "data/server/manifest.json").read_text())
        with tarfile.open(ROOT / "data/server" / manifest["dbc_archive"]) as archive:
            for member in archive:
                if member.isfile() and member.name.rsplit("/", 1)[-1].startswith("CreatureDisplayInfo.dbc"):
                    data = archive.extractfile(member).read()
                    _, count, _, size, _ = struct.unpack_from("<4s4I", data)
                    displays.update(struct.unpack_from("<I", data, 20 + i * size)[0] for i in range(count))
        self.assertLessEqual(looks, displays)

    def test_rejects_old_navigation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ("maps", "vmaps", "mmaps"):
                (root / directory).mkdir()
                (root / directory / "present").touch()
            tile = root / "mmaps/test.mmtile"
            tile.write_bytes(struct.pack("<III", 0x4D4D4150, 0, 19))
            with self.assertRaisesRegex(ValueError, "MMAP version"):
                prepare_data.verify(root, {"files": {}, "mmap_version": 20})
            tile.write_bytes(struct.pack("<III", 0x4D4D4150, 0, 20))
            prepare_data.verify(root, {"files": {}, "mmap_version": 20})

    def test_housing_migrations_match_sources(self):
        for database in sync_housing_sql.SOURCES:
            path = ROOT / f"data/sql/updates/pending_db_{database}/rev_20261117020000000_housing.sql"
            self.assertEqual(path.read_text(encoding="utf-8"), sync_housing_sql.render(database))


if __name__ == "__main__":
    unittest.main()
