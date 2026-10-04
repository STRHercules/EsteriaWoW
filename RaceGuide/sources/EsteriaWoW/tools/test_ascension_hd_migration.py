from __future__ import annotations

import struct
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tools.ascension_hd_migration import (
        MPQArchive,
        NPC_STOCK_TO_HD_MODEL,
        STOCK_DISPLAY_PAIRS,
        WORLD_DISPLAY_PAIRS,
        add_world_display_clones,
        merge_appearance_table,
        merge_chr_races,
        merge_rows_by_id,
        merge_stock_model_rows,
        merge_table_set,
        patch_mpq_entry,
        restore_stock_chr_race_displays,
        world_chr_races_payload,
        world_display_payload,
        write_archive,
    )
    from lib.mpq import FLAG_PATCH_FILE, HASH_FILE_KEY, decrypt, encrypt, mpq_hash
except ModuleNotFoundError:
    from ascension_hd_migration import (
        MPQArchive,
        NPC_STOCK_TO_HD_MODEL,
        STOCK_DISPLAY_PAIRS,
        WORLD_DISPLAY_PAIRS,
        add_world_display_clones,
        merge_appearance_table,
        merge_chr_races,
        merge_rows_by_id,
        merge_stock_model_rows,
        merge_table_set,
        patch_mpq_entry,
        restore_stock_chr_race_displays,
        world_chr_races_payload,
        world_display_payload,
        write_archive,
    )
    from lib.mpq import FLAG_PATCH_FILE, HASH_FILE_KEY, decrypt, encrypt, mpq_hash


def make_dbc(rows: list[list[int]], fields: int, strings: bytes = b"\0") -> bytes:
    records = b"".join(struct.pack("<%dI" % fields, *row) for row in rows)
    return struct.pack("<4s4I", b"WDBC", len(rows), fields, fields * 4, len(strings)) + records + strings


class AscensionHdMigrationTests(unittest.TestCase):
    def test_hd_appearance_rows_replace_stock_rows_and_preserve_custom_rows(self) -> None:
        base = make_dbc(
            [
                [100, 1, 0, 0, 0, 0],
                [200, 99, 0, 0, 0, 0],
            ],
            6,
        )
        donor = make_dbc(
            [
                [300, 51, 1, 7, 123, 1],
            ],
            6,
        )

        merged = merge_appearance_table("CharHairGeosets", base, donor)
        _, count, fields, record_size, string_size = struct.unpack_from("<4s4I", merged, 0)
        rows = [
            list(struct.unpack_from("<%dI" % fields, merged, 20 + index * record_size))
            for index in range(count)
        ]

        self.assertEqual(string_size, 1)
        self.assertEqual(rows, [[200, 99, 0, 0, 0, 0], [300, 1, 1, 7, 123, 1]])

    def test_hd_chr_race_display_ids_replace_stock_model_pair_only(self) -> None:
        base = make_dbc(
            [
                [1, 12, 1, 0, 49, 50] + [0] * 63,
                [99, 1, 1, 0, 900, 901] + [0] * 63,
            ],
            69,
        )
        donor = make_dbc(
            [
                [51, 5, 1, 0, 141284, 141285] + [0] * 63,
            ],
            69,
        )

        merged = merge_chr_races(base, donor)
        _, count, fields, record_size, _ = struct.unpack_from("<4s4I", merged, 0)
        rows = [
            list(struct.unpack_from("<%dI" % fields, merged, 20 + index * record_size))
            for index in range(count)
        ]

        self.assertEqual(rows[0][0:6], [1, 12, 1, 0, 141284, 141285])
        self.assertEqual(rows[1][0:6], [99, 1, 1, 0, 900, 901])
        self.assertNotIn(51, [row[0] for row in rows])

    def test_model_rows_are_replaced_and_mdx_paths_are_normalized(self) -> None:
        base_strings = b"\0Character\\Human\\Male\\HumanMale.m2\0"
        donor_strings = b"\0Character\\Human2\\Male\\HumanMale2.mdx\0"
        base = make_dbc([[1000, 0, 0, 0] + [0] * 24], 28, base_strings)
        donor = make_dbc([[112887, 0, 1, 0] + [0] * 24], 28, donor_strings)

        merged = merge_rows_by_id("CreatureModelData", base, donor, {112887})
        _, count, fields, record_size, string_size = struct.unpack_from("<4s4I", merged, 0)
        rows = [
            merged[20 + index * record_size : 20 + (index + 1) * record_size]
            for index in range(count)
        ]
        strings = merged[20 + count * record_size : 20 + count * record_size + string_size]

        self.assertEqual(len(rows), 2)
        self.assertEqual(struct.unpack_from("<I", rows[1], 0)[0], 112887)
        path_offset = struct.unpack_from("<I", rows[1], 8)[0]
        self.assertEqual(strings[path_offset:].split(b"\0", 1)[0], b"Character\\Human2\\Male\\HumanMale2.m2")

    def test_creature_display_strings_rebase_empty_sentinel_to_zero(self) -> None:
        base = make_dbc([[900, 9, 0, 0, 0, 0, 1, 1, 1, 1] + [0] * 6], 16, b"\0nLow\0")
        donor_strings = b"\0\0HDTexture.blp\0"
        donor = make_dbc(
            [[141284, 112887, 0, 0, 0, 0, 1, 1, 2, 1] + [0] * 6],
            16,
            donor_strings,
        )

        merged = merge_rows_by_id("CreatureDisplayInfo", base, donor, {141284})
        _, count, fields, record_size, string_size = struct.unpack_from("<4s4I", merged, 0)
        rows = [
            list(struct.unpack_from("<%dI" % fields, merged, 20 + index * record_size))
            for index in range(count)
        ]
        strings = merged[20 + count * record_size : 20 + count * record_size + string_size]
        hd = next(row for row in rows if row[0] == 141284)

        self.assertEqual(hd[6], 0)
        self.assertEqual(hd[7], 0)
        self.assertEqual(hd[9], 0)
        self.assertNotEqual(hd[8], 2)
        self.assertEqual(strings[hd[8] :].split(b"\0", 1)[0], b"HDTexture.blp")

    def test_world_display_clones_keep_high_glue_ids_and_use_low_server_ids(self) -> None:
        stock_races = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
        high_pairs = {
            race: (141284 + index * 2, 141285 + index * 2)
            for index, race in enumerate(stock_races)
        }
        race_rows = [
            [race, 0, 0, 0, *high_pairs[race]] + [0] * 63
            for race in stock_races
        ]
        display_rows = []
        expected_models: dict[int, int] = {}
        for index, race in enumerate(stock_races):
            for gender, high_id in enumerate(high_pairs[race]):
                model_id = 112887 + index * 2 + gender
                display_rows.append([high_id, model_id, 0, 0] + [0] * 12)
                expected_models[WORLD_DISPLAY_PAIRS[race][gender]] = model_id

        chr_races = make_dbc(race_rows, 69)
        displays = make_dbc(display_rows, 16)
        with_clones = add_world_display_clones(displays, chr_races)
        _, count, fields, record_size, _ = struct.unpack_from("<4s4I", with_clones, 0)
        rows = [
            list(struct.unpack_from("<%dI" % fields, with_clones, 20 + index * record_size))
            for index in range(count)
        ]
        by_id = {row[0]: row for row in rows}

        for race in stock_races:
            for high_id in high_pairs[race]:
                self.assertIn(high_id, by_id)
            for low_id in WORLD_DISPLAY_PAIRS[race]:
                self.assertLess(low_id, 65536)
                self.assertEqual(by_id[low_id][1], expected_models[low_id])

        server_races = world_chr_races_payload(chr_races)
        _, count, fields, record_size, _ = struct.unpack_from("<4s4I", server_races, 0)
        server_rows = [
            list(struct.unpack_from("<%dI" % fields, server_races, 20 + index * record_size))
            for index in range(count)
        ]
        for row in server_rows:
            self.assertEqual((row[4], row[5]), WORLD_DISPLAY_PAIRS[row[0]])

        server_displays = world_display_payload(with_clones)
        _, count, fields, record_size, _ = struct.unpack_from("<4s4I", server_displays, 0)
        ids = {
            struct.unpack_from("<I", server_displays, 20 + index * record_size)[0]
            for index in range(count)
        }
        self.assertEqual(ids, {value for pair in WORLD_DISPLAY_PAIRS.values() for value in pair})

    def test_stock_model_rows_copy_ascension_metadata_without_changing_ids(self) -> None:
        base_strings = b"\0Character\\Human\\Male\\HumanMale.mdx\0Custom\\Keep.m2\0"
        donor_strings = b"\0Character\\Human2\\Male\\HumanMale2.mdx\0"
        base_rows = [
            [49, 700, 1, 0] + [11] * 24,
            [900000, 800, 42, 0] + [22] * 24,
        ]
        donor_rows = [
            [112887, 2052, 1, 1] + [33] * 24,
        ]
        base = make_dbc(base_rows, 28, base_strings)
        donor = make_dbc(donor_rows, 28, donor_strings)

        original_mapping = dict(NPC_STOCK_TO_HD_MODEL)
        try:
            NPC_STOCK_TO_HD_MODEL.clear()
            NPC_STOCK_TO_HD_MODEL[49] = 112887
            merged = merge_stock_model_rows(base, donor)
        finally:
            NPC_STOCK_TO_HD_MODEL.clear()
            NPC_STOCK_TO_HD_MODEL.update(original_mapping)

        _, count, fields, record_size, string_size = struct.unpack_from("<4s4I", merged, 0)
        rows = [
            merged[20 + index * record_size : 20 + (index + 1) * record_size]
            for index in range(count)
        ]
        strings = merged[20 + count * record_size : 20 + count * record_size + string_size]
        by_id = {struct.unpack_from("<I", row, 0)[0]: row for row in rows}

        self.assertEqual(set(by_id), {49, 900000})
        self.assertEqual(struct.unpack_from("<I", by_id[49], 4)[0], 2052)
        path_offset = struct.unpack_from("<I", by_id[49], 8)[0]
        self.assertEqual(
            strings[path_offset:].split(b"\0", 1)[0],
            b"Character\\Human2\\Male\\HumanMale2.m2",
        )
        self.assertEqual(by_id[900000], rows[1])

    def test_restore_stock_chr_race_displays_changes_only_display_pair(self) -> None:
        rows = []
        for race, pair in STOCK_DISPLAY_PAIRS.items():
            rows.append([race, 777, 888, 999, 141000 + race, 142000 + race] + [race] * 63)
        rows.append([99, 1, 2, 3, 900, 901] + [99] * 63)
        base = make_dbc(rows, 69)

        restored = restore_stock_chr_race_displays(base)
        _, count, fields, record_size, _ = struct.unpack_from("<4s4I", restored, 0)
        parsed = [
            list(struct.unpack_from("<%dI" % fields, restored, 20 + index * record_size))
            for index in range(count)
        ]
        by_id = {row[0]: row for row in parsed}
        for race, pair in STOCK_DISPLAY_PAIRS.items():
            self.assertEqual(tuple(by_id[race][4:6]), pair)
            self.assertEqual(by_id[race][1:4], [777, 888, 999])
        self.assertEqual(by_id[99][4:6], [900, 901])

    def test_table_set_preserves_player_rows_and_stock_npc_rows(self) -> None:
        donor_strings = b"\0Character\\Orc2\\Male\\OrcMale2.mdx\0"
        stock_ids = [
            49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
            182, 183, 185, 186, 2208, 2209, 2248, 2250,
        ]
        source_ids = [
            112887, 112888, 112889, 112890, 112913, 112914, 112915, 112916,
            112917, 112918, 112919, 112920, 112921, 112922, 112911, 112912,
            112923, 112924, 112925, 112926,
        ]
        donor_model_rows = [
            [source_id, source_id, 1, 0] + [0] * 24
            for source_id in source_ids
        ]
        stock_races = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
        hd_races = [51, 52, 53, 54, 55, 56, 57, 58, 60, 61]
        donor_races = []
        donor_displays = []
        base_races = []
        for index, (stock_race, hd_race) in enumerate(zip(stock_races, hd_races)):
            base_races.append([stock_race, 0, 0, 0, 10 + index * 2, 11 + index * 2] + [0] * 63)
            male_display = 100 + index * 2
            female_display = male_display + 1
            donor_races.append([hd_race, 0, 0, 0, male_display, female_display] + [0] * 63)
            male_model = source_ids[index * 2]
            female_model = source_ids[index * 2 + 1]
            donor_displays.extend(
                [
                    [male_display, male_model, 0, 0] + [0] * 12,
                    [female_display, female_model, 0, 0] + [0] * 12,
                ]
            )

        appearance_layouts = {
            "CharSections": 10,
            "CharHairGeosets": 6,
            "CharHairTextures": 8,
            "CharacterFacialHairStyles": 8,
            "BarberShopStyle": 40,
        }
        base_model_rows = [
            [stock_id, 70000 + index, 1, 0] + [index + 1] * 24
            for index, stock_id in enumerate(stock_ids)
        ]
        base_model_rows.append([900000, 77, 0, 0] + [0] * 24)
        base = {
            "ChrRaces": make_dbc(base_races, 69),
            "CreatureDisplayInfo": make_dbc([], 16),
            "CreatureModelData": make_dbc(
                base_model_rows,
                28,
                b"\0Character\\Human\\Male\\HumanMale.m2\0",
            ),
            **{name: make_dbc([], fields) for name, fields in appearance_layouts.items()},
        }
        donor = {
            "ChrRaces": make_dbc(donor_races, 69),
            "CreatureDisplayInfo": make_dbc(donor_displays, 16),
            "CreatureModelData": make_dbc(donor_model_rows, 28, donor_strings),
            **{name: make_dbc([], fields) for name, fields in appearance_layouts.items()},
        }

        merged = merge_table_set(base, donor)
        payload = merged["CreatureModelData"]
        _, count, fields, record_size, string_size = struct.unpack_from("<4s4I", payload, 0)
        rows = [
            payload[20 + index * record_size : 20 + (index + 1) * record_size]
            for index in range(count)
        ]
        strings = payload[20 + count * record_size : 20 + count * record_size + string_size]
        by_id = {struct.unpack_from("<I", row, 0)[0]: row for row in rows}

        self.assertEqual(set(by_id), set(source_ids) | set(stock_ids) | {900000})
        for index, stock_id in enumerate(stock_ids):
            self.assertEqual(struct.unpack_from("<I", by_id[stock_id], 4)[0], 70000 + index)
        for source_id in source_ids:
            path_offset = struct.unpack_from("<I", by_id[source_id], 8)[0]
            path = strings[path_offset:].split(b"\0", 1)[0]
            self.assertTrue(path.startswith(b"Character\\"))
            self.assertTrue(path.endswith(b".m2"))
        self.assertEqual(struct.unpack_from("<I", by_id[900000], 4)[0], 77)

    def test_mpq_entry_patch_preserves_unreadable_unrelated_entries(self) -> None:
        target = "DBFilesClient\\CreatureModelData.dbc"
        opaque = "Other\\opaque.bin"
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / "patch-Z.MPQ"
            write_archive(
                archive_path,
                {
                    target: b"old model data",
                    opaque: b"opaque payload",
                },
            )

            with MPQArchive(str(archive_path)) as archive:
                opaque_index = archive._find_block_index(opaque)
                old_opaque_block = archive._block(opaque_index)
                block_pos = archive.block_pos
                block_count = archive.block_count
                listfile = archive.read_file("(listfile)")

            with archive_path.open("r+b") as handle:
                handle.seek(block_pos)
                block_table = bytearray(
                    decrypt(handle.read(block_count * 16), mpq_hash("(block table)", HASH_FILE_KEY))
                )
                flags = struct.unpack_from("<I", block_table, opaque_index * 16 + 12)[0]
                struct.pack_into(
                    "<I",
                    block_table,
                    opaque_index * 16 + 12,
                    flags | FLAG_PATCH_FILE,
                )
                handle.seek(block_pos)
                handle.write(encrypt(bytes(block_table), mpq_hash("(block table)", HASH_FILE_KEY)))

            with MPQArchive(str(archive_path)) as archive:
                with self.assertRaises(NotImplementedError):
                    archive.read_file(opaque)

            patch_mpq_entry(archive_path, target, b"new model data")

            with MPQArchive(str(archive_path)) as archive:
                self.assertEqual(archive.read_file(target), b"new model data")
                with self.assertRaises(NotImplementedError):
                    archive.read_file(opaque)
                self.assertEqual(archive.read_file("(listfile)"), listfile)
                self.assertEqual(archive._block(opaque_index), old_opaque_block[:-1] + (old_opaque_block[3] | FLAG_PATCH_FILE,))


if __name__ == "__main__":
    unittest.main()
