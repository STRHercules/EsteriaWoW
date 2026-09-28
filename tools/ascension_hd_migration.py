from __future__ import annotations

import argparse
import os
import shutil
import struct
import sys
import tempfile
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parent
CLIENT_PATCH_DIR = TOOL_DIR.parent / "modules" / "mod-classless-wildcard" / "client-patch"
sys.path.insert(0, str(TOOL_DIR))
sys.path.insert(0, str(CLIENT_PATCH_DIR))

from lib.mpq import (  # noqa: E402
    FLAG_COMPRESS,
    FLAG_ENCRYPTED,
    FLAG_IMPLODE,
    FLAG_PATCH_FILE,
    FLAG_SECTOR_CRC,
    FLAG_SINGLE_UNIT,
    HASH_FILE_KEY,
    MPQArchive,
    _pack_sectors,
    decrypt,
    encrypt,
    mpq_hash,
    write_archive,
)
from playable_race_pack import RawWdbc  # noqa: E402


STOCK_TO_HD = {
    1: 51,
    2: 52,
    3: 53,
    4: 54,
    5: 55,
    6: 56,
    7: 57,
    8: 58,
    10: 60,
    11: 61,
}
HD_TO_STOCK = {hd: stock for stock, hd in STOCK_TO_HD.items()}
STOCK_RACES = frozenset(STOCK_TO_HD)
HD_RACES = frozenset(HD_TO_STOCK)

STOCK_DISPLAY_PAIRS = {
    1: (49, 50),
    2: (51, 52),
    3: (53, 54),
    4: (55, 56),
    5: (57, 58),
    6: (59, 60),
    7: (1563, 1564),
    8: (1478, 1479),
    10: (15476, 15475),
    11: (16125, 16126),
}

# Ascension's Race2 player models live at high donor model IDs.  Esteria's
# native 3.3.5 player/display chain is far safer when those donor rows are
# copied onto the existing stock model IDs instead of changing ChrRaces or
# CreatureDisplayInfo IDs.
NPC_STOCK_TO_HD_MODEL = {
    49: 112887,
    50: 112888,
    51: 112889,
    52: 112890,
    53: 112913,
    54: 112914,
    55: 112915,
    56: 112916,
    57: 112917,
    58: 112918,
    59: 112919,
    60: 112920,
    182: 112921,
    183: 112922,
    185: 112911,
    186: 112912,
    2208: 112923,
    2209: 112924,
    2248: 112925,
    2250: 112926,
}

# The 3.3.5 in-world player display path truncates UNIT_FIELD_DISPLAYID to
# 16 bits.  Ascension's HD player display rows live at 141xxx and work in Glue,
# but must be cloned below 65536 for world rendering.  This range is reserved by
# Esteria for the ten stock HD race male/female pairs and is intentionally below
# the Battlemon continuation range (50001+).
WORLD_DISPLAY_PAIRS = {
    1: (49000, 49001),
    2: (49002, 49003),
    3: (49004, 49005),
    4: (49006, 49007),
    5: (49008, 49009),
    6: (49010, 49011),
    7: (49012, 49013),
    8: (49014, 49015),
    10: (49016, 49017),
    11: (49018, 49019),
}
WORLD_DISPLAY_IDS = frozenset(display_id for pair in WORLD_DISPLAY_PAIRS.values() for display_id in pair)

RACE_FIELDS = {
    "CharSections": 1,
    "CharHairGeosets": 1,
    "CharHairTextures": 1,
    "CharacterFacialHairStyles": 0,
    "BarberShopStyle": 37,
}
APPEARANCE_TABLES = tuple(RACE_FIELDS)
HD_APPEARANCE_TABLES = frozenset({"CharSections", "CharHairGeosets", "CharacterFacialHairStyles"})

STRING_FIELDS = {
    "ChrRaces": (6, 11, 65, 66, 67)
    + tuple(range(14, 30))
    + tuple(range(31, 47))
    + tuple(range(48, 64)),
    "CharSections": (4, 5, 6),
    "BarberShopStyle": tuple(range(2, 18)) + tuple(range(19, 35)),
    "CreatureDisplayInfo": (6, 7, 8, 9),
    "CreatureModelData": (2,),
    "CreatureDisplayInfoExtra": (20,),
}

EXPECTED_LAYOUTS = {
    "ChrRaces": (69, 276),
    "CharSections": (10, 40),
    "CharHairGeosets": (6, 24),
    "CharHairTextures": (8, 32),
    "CharacterFacialHairStyles": (8, 32),
    "BarberShopStyle": (40, 160),
    "CreatureDisplayInfo": (16, 64),
    "CreatureDisplayInfoExtra": (21, 84),
    "CreatureModelData": (28, 112),
}

RACE_FOLDERS = (
    "Human",
    "Orc",
    "Dwarf",
    "NightElf",
    "Scourge",
    "Tauren",
    "Gnome",
    "Troll",
    "BloodElf",
    "Draenei",
)


def _table(data: bytes, name: str) -> RawWdbc:
    table = RawWdbc(data)
    expected = EXPECTED_LAYOUTS.get(name)
    if expected and (table.fields, table.record_size) != expected:
        raise ValueError(
            f"{name} layout {table.fields}/{table.record_size} != {expected[0]}/{expected[1]}"
        )
    return table


def _u32(record: bytes, field: int) -> int:
    return int.from_bytes(record[field * 4 : field * 4 + 4], "little")


def _set_u32(record: bytes, field: int, value: int) -> bytes:
    result = bytearray(record)
    result[field * 4 : field * 4 + 4] = value.to_bytes(4, "little")
    return bytes(result)


def _read_string(pool: bytes, offset: int) -> bytes:
    if not offset:
        return b""
    end = pool.find(b"\0", offset)
    if end < 0:
        raise ValueError(f"unterminated WDBC string at {offset}")
    return pool[offset:end]


def _rebase_strings(
    table_name: str,
    records: list[bytes],
    donor_strings: bytes,
    base_strings: bytes = b"\0",
    *,
    normalize_model_paths: bool = False,
) -> tuple[list[bytes], bytes]:
    fields = STRING_FIELDS.get(table_name, ())
    pool = bytearray(base_strings)
    offsets: dict[bytes, int] = {}
    cursor = 0
    while cursor < len(base_strings):
        end = base_strings.find(b"\0", cursor)
        if end < 0:
            break
        value = base_strings[cursor:end]
        if value and value not in offsets:
            offsets[value] = cursor
        cursor = end + 1
    result: list[bytes] = []

    for record in records:
        updated = record
        for field in fields:
            value = _read_string(donor_strings, _u32(record, field))
            if not value:
                # Donor tables sometimes point at a non-zero offset whose byte is
                # NUL.  That offset is meaningful only inside the donor string
                # block; carrying the integer into another DBC can point at an
                # unrelated string.  Canonicalize every empty string to offset 0.
                updated = _set_u32(updated, field, 0)
                continue
            if normalize_model_paths and field == 2 and value.lower().endswith(b".mdx"): 
                value = value[:-4] + b".m2"
            offset = offsets.get(value)
            if offset is None:
                offset = len(pool)
                pool.extend(value + b"\0")
                offsets[value] = offset
            updated = _set_u32(updated, field, offset)
        result.append(updated)

    return result, bytes(pool)


def _next_row_id(records: list[bytes]) -> int:
    return max((_u32(row, 0) for row in records), default=0) + 1


def merge_appearance_table(table_name: str, base_data: bytes, donor_data: bytes) -> bytes:
    """Replace Esteria stock-race appearance rows with Ascension rows."""

    if table_name not in RACE_FIELDS:
        raise ValueError(f"unsupported appearance table: {table_name}")
    base = _table(base_data, table_name)
    donor = _table(donor_data, table_name)
    race_field = RACE_FIELDS[table_name]
    donor_races = HD_RACES if table_name in HD_APPEARANCE_TABLES else STOCK_RACES
    selected: list[bytes] = []
    for record in donor.records:
        source_race = _u32(record, race_field)
        if source_race not in donor_races:
            continue
        if source_race in HD_TO_STOCK:
            record = _set_u32(record, race_field, HD_TO_STOCK[source_race])
        selected.append(record)

    base_records = [
        record
        for record in base.records
        if _u32(record, race_field) not in STOCK_RACES
    ]
    selected, strings = _rebase_strings(
        table_name,
        selected,
        donor.strings,
        base.strings,
    )

    if table_name != "CharacterFacialHairStyles":
        used_ids = {_u32(record, 0) for record in base_records}
        next_id = _next_row_id(base_records)
        normalized: list[bytes] = []
        for record in selected:
            row_id = _u32(record, 0)
            if row_id in used_ids:
                while next_id in used_ids:
                    next_id += 1
                record = _set_u32(record, 0, next_id)
                next_id += 1
            used_ids.add(_u32(record, 0))
            normalized.append(record)
        selected = normalized

    return base.build(base_records + selected, strings)


def merge_chr_races(base_data: bytes, donor_data: bytes) -> bytes:
    """Keep Esteria race rows and replace only their stock display pairs."""

    base = _table(base_data, "ChrRaces")
    donor = _table(donor_data, "ChrRaces")
    donor_by_id = {_u32(record, 0): record for record in donor.records}
    result: list[bytes] = []
    for record in base.records:
        race = _u32(record, 0)
        hd_race = STOCK_TO_HD.get(race)
        if hd_race is not None:
            hd_record = donor_by_id.get(hd_race)
            if hd_record is None:
                raise ValueError(f"Ascension ChrRaces is missing HD row {hd_race}")
            record = _set_u32(record, 4, _u32(hd_record, 4))
            record = _set_u32(record, 5, _u32(hd_record, 5))
        result.append(record)
    return base.build(result, base.strings)


def merge_rows_by_id(
    table_name: str,
    base_data: bytes,
    donor_data: bytes,
    row_ids: set[int],
) -> bytes:
    """Replace or append selected donor WDBC rows, rebasing strings."""

    base = _table(base_data, table_name)
    donor = _table(donor_data, table_name)
    selected = [record for record in donor.records if _u32(record, 0) in row_ids]
    if not selected:
        raise ValueError(f"No selected rows found in donor {table_name}")
    selected, strings = _rebase_strings(
        table_name,
        selected,
        donor.strings,
        base.strings,
        normalize_model_paths=table_name == "CreatureModelData",
    )
    records = list(base.records)
    indexes = {_u32(record, 0): index for index, record in enumerate(records)}
    for record in selected:
        row_id = _u32(record, 0)
        index = indexes.get(row_id)
        if index is None:
            indexes[row_id] = len(records)
            records.append(record)
        else:
            records[index] = record
    return base.build(records, strings)


def merge_stock_model_rows(base_data: bytes, donor_data: bytes) -> bytes:
    """Copy Ascension Race2 model metadata onto Esteria's stock model IDs.

    Only the 20 approved stock destination rows are replaced.  Every unrelated
    model row remains byte-identical.  Donor model paths are rebased into the
    base string block and normalized from .mdx to .m2.
    """

    base = _table(base_data, "CreatureModelData")
    donor = _table(donor_data, "CreatureModelData")
    donor_by_id = {_u32(record, 0): record for record in donor.records}

    replacements: list[bytes] = []
    for destination_id, source_id in NPC_STOCK_TO_HD_MODEL.items():
        source = donor_by_id.get(source_id)
        if source is None:
            raise ValueError(f"Ascension CreatureModelData is missing HD source row {source_id}")
        replacements.append(_set_u32(source, 0, destination_id))

    replacements, strings = _rebase_strings(
        "CreatureModelData",
        replacements,
        donor.strings,
        base.strings,
        normalize_model_paths=True,
    )

    records = list(base.records)
    indexes = {_u32(record, 0): index for index, record in enumerate(records)}
    for replacement in replacements:
        destination_id = _u32(replacement, 0)
        index = indexes.get(destination_id)
        if index is None:
            indexes[destination_id] = len(records)
            records.append(replacement)
        else:
            records[index] = replacement
    return base.build(records, strings)


def restore_stock_chr_race_displays(base_data: bytes) -> bytes:
    """Force only the ten stock race display pairs back to native 3.3.5 IDs."""

    table = _table(base_data, "ChrRaces")
    records: list[bytes] = []
    seen: set[int] = set()
    for record in table.records:
        race = _u32(record, 0)
        pair = STOCK_DISPLAY_PAIRS.get(race)
        if pair is not None:
            record = _set_u32(record, 4, pair[0])
            record = _set_u32(record, 5, pair[1])
            seen.add(race)
        records.append(record)
    missing = sorted(STOCK_RACES - seen)
    if missing:
        raise ValueError(f"ChrRaces is missing stock race rows: {missing}")
    return table.build(records, table.strings)


def hd_dependencies(chr_races_data: bytes, display_data: bytes) -> tuple[set[int], set[int], set[int]]:
    races = _table(chr_races_data, "ChrRaces")
    displays = _table(display_data, "CreatureDisplayInfo")
    display_ids = {
        _u32(record, field)
        for record in races.records
        if _u32(record, 0) in HD_RACES
        for field in (4, 5)
    }
    display_records = [record for record in displays.records if _u32(record, 0) in display_ids]
    model_ids = {_u32(record, 1) for record in display_records}
    extra_ids = {_u32(record, 3) for record in display_records if _u32(record, 3)}
    return display_ids, model_ids, extra_ids


def add_world_display_clones(display_data: bytes, chr_races_data: bytes) -> bytes:
    """Add 16-bit-safe clones of the Ascension HD player display rows.

    The high 141xxx IDs remain authoritative for Glue/character creation.  The
    low 49000-49019 rows are only for the in-world player display path, which
    truncates UNIT_FIELD_DISPLAYID to 16 bits in this 3.3.5 client.
    """

    displays = _table(display_data, "CreatureDisplayInfo")
    races = _table(chr_races_data, "ChrRaces")
    by_display_id = {_u32(record, 0): record for record in displays.records}
    records = list(displays.records)

    for race, low_pair in WORLD_DISPLAY_PAIRS.items():
        race_rows = [record for record in races.records if _u32(record, 0) == race]
        if len(race_rows) != 1:
            raise ValueError(f"ChrRaces must contain exactly one row for race {race}")
        source_pair = (_u32(race_rows[0], 4), _u32(race_rows[0], 5))
        for source_id, low_id in zip(source_pair, low_pair):
            source = by_display_id.get(source_id)
            if source is None:
                raise ValueError(f"CreatureDisplayInfo is missing HD source display {source_id}")
            clone = _set_u32(source, 0, low_id)
            existing = by_display_id.get(low_id)
            if existing is not None:
                if existing != clone:
                    raise ValueError(
                        f"16-bit world display ID {low_id} is already occupied by unrelated data"
                    )
                continue
            by_display_id[low_id] = clone
            records.append(clone)

    return displays.build(records, displays.strings)


def world_chr_races_payload(chr_races_data: bytes) -> bytes:
    """Build the server continuation rows using 16-bit-safe world display IDs."""

    races = _table(chr_races_data, "ChrRaces")
    selected: list[bytes] = []
    for record in races.records:
        race = _u32(record, 0)
        pair = WORLD_DISPLAY_PAIRS.get(race)
        if pair is None:
            continue
        record = _set_u32(record, 4, pair[0])
        record = _set_u32(record, 5, pair[1])
        selected.append(record)
    selected, strings = _rebase_strings("ChrRaces", selected, races.strings, b"\0")
    return races.build(selected, strings)


def world_display_payload(display_data: bytes) -> bytes:
    """Build the server continuation containing only 16-bit HD display clones."""

    displays = _table(display_data, "CreatureDisplayInfo")
    selected = [record for record in displays.records if _u32(record, 0) in WORLD_DISPLAY_IDS]
    found = {_u32(record, 0) for record in selected}
    if found != WORLD_DISPLAY_IDS:
        raise ValueError(f"Missing 16-bit world display clones: {sorted(WORLD_DISPLAY_IDS - found)}")
    selected, strings = _rebase_strings("CreatureDisplayInfo", selected, displays.strings, b"\0")
    return displays.build(selected, strings)


def merge_table_set(base: dict[str, bytes], donor: dict[str, bytes]) -> dict[str, bytes]:
    """Build the client/server WDBC set from an existing base and Ascension data."""

    required = {"ChrRaces", "CreatureDisplayInfo", "CreatureModelData", *APPEARANCE_TABLES}
    missing = sorted(name for name in required if name not in base or name not in donor)
    if missing:
        raise ValueError(f"Missing required DBC table(s): {', '.join(missing)}")

    output = dict(base)
    output["ChrRaces"] = merge_chr_races(base["ChrRaces"], donor["ChrRaces"])
    for name in APPEARANCE_TABLES:
        output[name] = merge_appearance_table(name, base[name], donor[name])

    display_ids, model_ids, extra_ids = hd_dependencies(
        donor["ChrRaces"], donor["CreatureDisplayInfo"]
    )
    output["CreatureDisplayInfo"] = merge_rows_by_id(
        "CreatureDisplayInfo", base["CreatureDisplayInfo"], donor["CreatureDisplayInfo"], display_ids
    )
    output["CreatureDisplayInfo"] = add_world_display_clones(
        output["CreatureDisplayInfo"], output["ChrRaces"]
    )
    output["CreatureModelData"] = merge_rows_by_id(
        "CreatureModelData", base["CreatureModelData"], donor["CreatureModelData"], model_ids
    )
    if extra_ids and "CreatureDisplayInfoExtra" in base and "CreatureDisplayInfoExtra" in donor:
        output["CreatureDisplayInfoExtra"] = merge_rows_by_id(
            "CreatureDisplayInfoExtra",
            base["CreatureDisplayInfoExtra"],
            donor["CreatureDisplayInfoExtra"],
            extra_ids,
        )
    return output


def load_table_dir(root: Path) -> dict[str, bytes]:
    return {
        path.stem: path.read_bytes()
        for path in root.glob("*.dbc")
        if path.is_file()
    }


def load_tables_from_archive(archive: MPQArchive) -> dict[str, bytes]:
    names = archive.read_file("(listfile)").decode("utf-8", "replace")
    names = names.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
    tables: dict[str, bytes] = {}
    for line in names.splitlines():
        line = line.strip().replace("/", "\\")
        if not line.lower().startswith("dbfilesclient\\") or not line.lower().endswith(".dbc"):
            continue
        table_name = Path(line.replace("\\", "/")).stem
        tables[table_name] = archive.read_file(line)
    return tables


def load_archive_entries(archive: MPQArchive) -> dict[str, bytes]:
    raw = archive.read_file("(listfile)").decode("utf-8", "replace")
    raw = raw.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
    entries: dict[str, bytes] = {}
    for line in raw.splitlines():
        name = line.strip().replace("/", "\\")
        if not name or name == "(listfile)":
            continue
        if name.casefold() in {key.casefold() for key in entries}:
            continue
        try:
            entries[name] = archive.read_file(name)
        except (KeyError, NotImplementedError):
            continue
    return entries


def load_donor_tables(root: Path) -> dict[str, bytes]:
    return load_table_dir(root)


def collect_character_assets(root: Path) -> dict[str, bytes]:
    character_root = root / "Character"
    wanted = {name.casefold() for name in RACE_FOLDERS}
    wanted.update((name + "2").casefold() for name in RACE_FOLDERS)
    assets: dict[str, bytes] = {}
    for directory in sorted(character_root.iterdir(), key=lambda path: path.name.casefold()):
        if not directory.is_dir() or directory.name.casefold() not in wanted:
            continue
        for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix().casefold()):
            if not path.is_file():
                continue
            entry = "Character\\" + path.relative_to(character_root).as_posix().replace("/", "\\")
            assets[entry] = path.read_bytes()
    if not assets:
        raise ValueError(f"No stock character assets found under {character_root}")
    return assets


def merge_archive(path: Path, donor_root: Path) -> dict[str, int]:
    with MPQArchive(str(path)) as archive:
        base_entries = load_archive_entries(archive)
        base_tables = load_tables_from_archive(archive)
    donor_tables = load_donor_tables(donor_root / "DBFilesClient")
    merged_tables = merge_table_set(base_tables, donor_tables)
    assets = collect_character_assets(donor_root / "patch-CHA.mpq")

    by_casefold = {name.casefold(): name for name in base_entries}
    for name, payload in assets.items():
        old = by_casefold.get(name.casefold())
        if old is not None:
            del base_entries[old]
        base_entries[name] = payload
        by_casefold[name.casefold()] = name
    for name, payload in merged_tables.items():
        entry = f"DBFilesClient\\{name}.dbc"
        old = by_casefold.get(entry.casefold())
        if old is not None:
            del base_entries[old]
        base_entries[entry] = payload
        by_casefold[entry.casefold()] = entry

    with tempfile.NamedTemporaryFile(prefix=path.stem + "-", suffix=".MPQ", dir=path.parent, delete=False) as temp:
        temp_path = Path(temp.name)
    try:
        write_archive(temp_path, base_entries)
        with MPQArchive(str(temp_path)) as check:
            for name in ("DBFilesClient\\ChrRaces.dbc", "DBFilesClient\\CharSections.dbc"):
                if not check.has_file(name):
                    raise ValueError(f"Merged archive is missing {name}")
            if not check.has_file("Character\\Human2\\Male\\humanmale2.m2"):
                raise ValueError("Merged archive is missing the Human2 HD model")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return {"entries": len(base_entries), "assets": len(assets), "tables": len(merged_tables)}


def _patch_mpq_entry_copy(path: Path, entry: str, payload: bytes) -> dict[str, int]:
    with MPQArchive(str(path)) as archive:
        index = archive._find_block_index(entry)
        if index is None or not archive.has_file(entry):
            raise ValueError(f"Archive is missing {entry}")
        old_block = archive._block(index)
        unsupported = (
            FLAG_ENCRYPTED
            | FLAG_IMPLODE
            | FLAG_PATCH_FILE
            | FLAG_SECTOR_CRC
            | FLAG_SINGLE_UNIT
        )
        if not (old_block[3] & FLAG_COMPRESS) or old_block[3] & unsupported:
            raise ValueError(f"Unsupported MPQ flags for replaceable entry {entry}: 0x{old_block[3]:08x}")
        block_count = archive.block_count
        block_pos = archive.block_pos
        archive_offset = archive.archive_offset
        sector_size = archive.sector_size
        header_size = archive.header_size
        format_version = archive.format_version
        hi_block_pos = archive.hi_block_pos
        with open(path, "rb") as handle:
            handle.seek(block_pos)
            encrypted_block_table = handle.read(block_count * 16)
            handle.seek(archive_offset)
            header = bytearray(handle.read(32))

    if header_size != 32 or format_version != 0 or hi_block_pos:
        raise ValueError("Only v0 MPQs without a hi-block table are supported for in-place patching")

    block_table = bytearray(decrypt(encrypted_block_table, mpq_hash("(block table)", HASH_FILE_KEY)))
    packed = _pack_sectors(payload, sector_size)
    file_size = os.path.getsize(path)
    data_pos = file_size - archive_offset
    new_block_pos = data_pos + len(packed)
    new_archive_size = new_block_pos + block_count * 16
    if max(data_pos, new_block_pos, new_archive_size) > 0xFFFFFFFF:
        raise ValueError("In-place MPQ patch would exceed the v0 4 GiB offset limit")
    struct.pack_into("<4I", block_table, index * 16, data_pos, len(packed), len(payload), old_block[3])
    encrypted_block_table = encrypt(bytes(block_table), mpq_hash("(block table)", HASH_FILE_KEY))
    struct.pack_into("<I", header, 8, new_archive_size)
    struct.pack_into("<I", header, 20, new_block_pos)

    with open(path, "r+b") as handle:
        handle.seek(file_size)
        handle.write(packed)
        handle.write(encrypted_block_table)
        handle.seek(archive_offset)
        handle.write(header)
    return {"entries": block_count, "payload_bytes": len(payload), "packed_bytes": len(packed)}


def patch_mpq_entry(path: Path, entry: str, payload: bytes) -> dict[str, int]:
    """Replace one readable v0 MPQ entry without reserializing other files."""

    with tempfile.NamedTemporaryFile(prefix=path.stem + "-", suffix=path.suffix, dir=path.parent, delete=False) as temp:
        temp_path = Path(temp.name)
    try:
        shutil.copyfile(path, temp_path)
        stats = _patch_mpq_entry_copy(temp_path, entry, payload)
        with MPQArchive(str(temp_path)) as check:
            if check.read_file(entry) != payload:
                raise ValueError(f"Patched archive failed readback for {entry}")
        os.replace(temp_path, path)
        return stats
    finally:
        if temp_path.exists():
            temp_path.unlink()


def write_server_outputs(base_root: Path, donor_root: Path, output_root: Path) -> dict[str, int]:
    base = load_table_dir(base_root)
    donor = load_donor_tables(donor_root / "DBFilesClient")
    merged = merge_table_set(base, donor)
    output_root.mkdir(parents=True, exist_ok=True)
    for name, payload in merged.items():
        (output_root / f"{name}.dbc").write_bytes(payload)
    display_ids, model_ids, extra_ids = hd_dependencies(donor["ChrRaces"], donor["CreatureDisplayInfo"])
    continuation_root = output_root / "dbc-continuations"
    continuation_root.mkdir(parents=True, exist_ok=True)

    # The client keeps the full Ascension 141xxx display IDs for Glue, but the
    # in-world player display path is 16-bit.  Server continuations therefore
    # use only the 49000-49019 clones while retaining Ascension's model IDs.
    (continuation_root / "CreatureDisplayInfo.dbc1-ascension-hd").write_bytes(
        world_display_payload(merged["CreatureDisplayInfo"])
    )

    source = _table(donor["CreatureModelData"], "CreatureModelData")
    selected = [record for record in source.records if _u32(record, 0) in model_ids]
    selected, strings = _rebase_strings(
        "CreatureModelData",
        selected,
        source.strings,
        b"\0",
        normalize_model_paths=True,
    )
    (continuation_root / "CreatureModelData.dbc1-ascension-hd").write_bytes(
        source.build(selected, strings)
    )
    if extra_ids and "CreatureDisplayInfoExtra" in donor:
        source = _table(donor["CreatureDisplayInfoExtra"], "CreatureDisplayInfoExtra")
        selected = [record for record in source.records if _u32(record, 0) in extra_ids]
        selected, strings = _rebase_strings("CreatureDisplayInfoExtra", selected, source.strings, b"\0")
        (continuation_root / "CreatureDisplayInfoExtra.dbc1-ascension-hd").write_bytes(
            source.build(selected, strings)
        )
    (continuation_root / "ChrRaces.dbc1-ascension-hd").write_bytes(
        world_chr_races_payload(merged["ChrRaces"])
    )
    return {"tables": len(merged), "display_rows": len(display_ids), "model_rows": len(model_ids)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Make Ascension stock races the default Esteria HD models")
    parser.add_argument("--ascension-root", type=Path, required=True)
    parser.add_argument("--client-archive", type=Path, action="append")
    parser.add_argument("--server-base", type=Path)
    parser.add_argument("--server-output", type=Path)
    args = parser.parse_args()

    if not args.client_archive and not args.server_base and not args.server_output:
        parser.error("at least one migration output must be selected")
    if bool(args.server_base) != bool(args.server_output):
        parser.error("--server-base and --server-output must be provided together")
    if args.client_archive and not args.server_base:
        parser.error("full migration requires --server-base and --server-output")

    for archive in args.client_archive or ():
        print(archive, merge_archive(archive, args.ascension_root))
    if args.server_base:
        print("server", write_server_outputs(args.server_base, args.ascension_root, args.server_output))


if __name__ == "__main__":
    main()
