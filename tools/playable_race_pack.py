"""Build an additive WDBC/model pack for Vulpera and Alliance Pandaren."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import tempfile
from dataclasses import dataclass
from pathlib import Path

from cars_mount_pack import (
    DLL_DEFAULT,
    Storm,
    WOTLK_MODEL_VERSION,
    Wdbc,
    merge_archive_entries,
    merge_wxl_manifest,
    safe_relative,
)


SOURCE_RACES = {"vulpera": 19, "pandaren": 20}
TARGET_RACES = {"vulpera": 20, "pandaren": 18}
RACE_ID_FIELDS = {
    "ChrRaces": 0,
    "CharBaseInfo": 0,
    "CharStartOutfit": 1,
    "CharSections": 0,
    "CharHairGeosets": 1,
    "CharHairTextures": 1,
    "BarberShopStyle": 37,
    "CharacterFacialHairStyles": 0,
    "NameGen": 2,
    "CreatureDisplayInfoExtra": 1,
}
RACE_MASK_FIELDS = {
    "SkillLineAbility": 3,
    "SkillRaceClassInfo": 2,
}
RACE_TABLES = tuple(RACE_ID_FIELDS) + tuple(RACE_MASK_FIELDS)
RACE_ASSET_ROOTS = ("vulpera", "Pandaren")
CONTINUATION_SUFFIX = ".dbc1-vulpera-pandaren"

RACE_BYTE_LAYOUTS = {
    "ChrRaces": (0, 4),
    "CharBaseInfo": (0, 1),
    "CharStartOutfit": (4, 1),
    "CharSections": (4, 4),
    "CharHairGeosets": (4, 4),
    "CharHairTextures": (4, 4),
    "BarberShopStyle": (37 * 4, 4),
    "CharacterFacialHairStyles": (4, 4),
    "NameGen": (8, 4),
    "CreatureDisplayInfoExtra": (4, 4),
    "SkillLineAbility": (3 * 4, 4),
    "SkillRaceClassInfo": (2 * 4, 4),
}


@dataclass(frozen=True)
class WdbcLayout:
    fields: int
    record_size: int
    race_offset: int
    race_width: int


WDBC_LAYOUTS = {
    "ChrRaces": WdbcLayout(69, 276, *RACE_BYTE_LAYOUTS["ChrRaces"]),
    "CharBaseInfo": WdbcLayout(2, 2, *RACE_BYTE_LAYOUTS["CharBaseInfo"]),
    "CharStartOutfit": WdbcLayout(77, 296, *RACE_BYTE_LAYOUTS["CharStartOutfit"]),
    "CharSections": WdbcLayout(10, 40, *RACE_BYTE_LAYOUTS["CharSections"]),
    "CharHairGeosets": WdbcLayout(6, 24, *RACE_BYTE_LAYOUTS["CharHairGeosets"]),
    "CharHairTextures": WdbcLayout(8, 32, *RACE_BYTE_LAYOUTS["CharHairTextures"]),
    "BarberShopStyle": WdbcLayout(40, 160, *RACE_BYTE_LAYOUTS["BarberShopStyle"]),
    "CharacterFacialHairStyles": WdbcLayout(8, 32, *RACE_BYTE_LAYOUTS["CharacterFacialHairStyles"]),
    "NameGen": WdbcLayout(4, 16, *RACE_BYTE_LAYOUTS["NameGen"]),
    "CreatureDisplayInfoExtra": WdbcLayout(21, 84, *RACE_BYTE_LAYOUTS["CreatureDisplayInfoExtra"]),
    "SkillLineAbility": WdbcLayout(14, 56, *RACE_BYTE_LAYOUTS["SkillLineAbility"]),
    "SkillRaceClassInfo": WdbcLayout(8, 32, *RACE_BYTE_LAYOUTS["SkillRaceClassInfo"]),
}


class RawWdbc:
    """WDBC reader/writer that preserves packed record bytes verbatim."""

    def __init__(self, data: bytes):
        if len(data) < 20:
            raise ValueError("truncated WDBC header")
        self.header = struct.unpack_from("<4s4I", data)
        magic, self.count, self.fields, self.record_size, self.string_size = self.header
        if magic != b"WDBC":
            raise ValueError("unsupported WDBC magic")
        records_end = 20 + self.count * self.record_size
        expected = records_end + self.string_size
        if len(data) != expected:
            raise ValueError(f"invalid WDBC size: {len(data)} != {expected}")
        self.records = tuple(
            data[20 + index * self.record_size : 20 + (index + 1) * self.record_size]
            for index in range(self.count)
        )
        self.strings = data[records_end:]

    @staticmethod
    def _value(record: bytes, offset: int, width: int) -> int:
        return int.from_bytes(record[offset : offset + width], "little")

    @staticmethod
    def _replace(record: bytes, offset: int, width: int, value: int) -> bytes:
        if value < 0 or value >= 1 << (width * 8):
            raise ValueError(f"value {value} does not fit in {width} bytes")
        result = bytearray(record)
        result[offset : offset + width] = value.to_bytes(width, "little")
        return bytes(result)

    def remap_race_records(
        self,
        table_name: str,
        source_race: int,
        target_race: int,
        records: tuple[bytes, ...] | list[bytes] | None = None,
    ) -> list[bytes]:
        layout = WDBC_LAYOUTS[table_name]
        selected = self.records if records is None else tuple(records)
        result = []
        for record in selected:
            if len(record) != self.record_size:
                raise ValueError(f"{table_name} record has invalid length")
            if self._value(record, layout.race_offset, layout.race_width) == source_race:
                record = self._replace(record, layout.race_offset, layout.race_width, target_race)
            result.append(record)
        return result

    def build(self, records: tuple[bytes, ...] | list[bytes]) -> bytes:
        records = tuple(records)
        if any(len(record) != self.record_size for record in records):
            raise ValueError("continuation record length does not match donor WDBC")
        header = struct.pack(
            "<4s4I",
            self.header[0],
            len(records),
            self.fields,
            self.record_size,
            self.string_size,
        )
        return header + b"".join(records) + self.strings


@dataclass(frozen=True)
class AssetReport:
    asset_paths: tuple[str, ...]
    sha256: dict[str, str]
    file_counts: dict[str, int]
    entries: dict[str, bytes]


@dataclass(frozen=True)
class PackReport:
    continuations: dict[str, bytes]
    asset_paths: tuple[str, ...]
    manifest_entries: tuple[str, ...]
    collisions: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    sha256: dict[str, str]
    file_counts: dict[str, int]
    staged_root: str


def _race_field(table_name: str) -> int:
    try:
        return RACE_ID_FIELDS[table_name]
    except KeyError as exc:
        raise ValueError(f"unknown race-ID table: {table_name}") from exc


def _check_unique_chr_races(rows: list[list[int]]) -> None:
    row_ids = [row[0] for row in rows]
    if len(row_ids) != len(set(row_ids)):
        raise ValueError("duplicate row ID in ChrRaces")


def remap_race_rows(
    table_name: str,
    rows: list[list[int]],
    source_race: int,
    target_race: int,
) -> list[list[int]]:
    """Return rows with only the configured race field changed."""

    field = _race_field(table_name)
    if any(field >= len(row) for row in rows):
        raise ValueError(f"{table_name} race field {field} is outside a row")
    result = [row.copy() for row in rows]
    for row in result:
        if row[field] == source_race:
            row[field] = target_race
    if table_name == "ChrRaces":
        _check_unique_chr_races(result)
    return result


def remap_race_masks(value: int, source_mask: int, target_mask: int) -> int:
    """Replace source race bits while retaining every unrelated bit."""

    return ((value & 0xFFFFFFFF) & ~source_mask) | target_mask


def _model_root(model_root: Path) -> Path:
    character = model_root / "Character"
    if character.is_dir():
        return character
    if model_root.name.casefold() == "character" and model_root.is_dir():
        return model_root
    raise FileNotFoundError(f"Character asset root not found under {model_root}")


def _find_casefold_child(root: Path, name: str) -> Path:
    matches = [child for child in root.iterdir() if child.name.casefold() == name.casefold()]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {name} directory under {root}")
    return matches[0]


def _asset_name(character_root: Path, path: Path) -> str:
    relative = path.relative_to(character_root).as_posix().replace("/", "\\")
    return str(safe_relative(f"Character\\{relative}")) .replace("/", "\\")


def collect_race_assets(model_root: Path) -> AssetReport:
    """Validate and collect both genders of each required race asset tree."""

    character_root = _model_root(model_root)
    entries: dict[str, bytes] = {}
    digests: dict[str, str] = {}
    file_counts: dict[str, int] = {}
    for race in RACE_ASSET_ROOTS:
        race_root = _find_casefold_child(character_root, race)
        files = sorted((path for path in race_root.rglob("*") if path.is_file()), key=lambda path: str(path).casefold())
        if not files:
            raise ValueError(f"missing assets under Character\\{race}")
        for path in files:
            if path.suffix.casefold() == ".mdx":
                raise ValueError(f"unsupported .mdx asset: {path}")
        for gender in ("male", "female"):
            gender_root = _find_casefold_child(race_root, gender)
            gender_files = [path for path in files if gender_root in path.parents]
            suffixes = {path.suffix.casefold() for path in gender_files}
            missing = [suffix for suffix in (".m2", ".skin", ".anim") if suffix not in suffixes]
            if missing:
                raise ValueError(f"missing {race} {gender} asset sets: {', '.join(missing)}")
            for path in gender_files:
                if path.suffix.casefold() == ".m2":
                    payload = path.read_bytes()
                    if len(payload) < 8 or payload[:4] not in (b"MD20", b"MD21"):
                        raise ValueError(f"invalid M2 header: {path}")
                    version = struct.unpack_from("<I", payload, 4)[0]
                    if version != WOTLK_MODEL_VERSION:
                        raise ValueError(f"non-WotLK M2 model: {path} ({version})")
        file_counts[race.casefold()] = len(files)
        for path in files:
            name = _asset_name(character_root, path)
            payload = path.read_bytes()
            prior = entries.get(name)
            if prior is not None and prior != payload:
                raise ValueError(f"asset path collision with different bytes: {name}")
            entries[name] = payload
            digests[name] = hashlib.sha256(payload).hexdigest()
    return AssetReport(tuple(sorted(entries)), digests, file_counts, entries)


def _dbc_directory(dbc_root: Path) -> Path:
    nested = dbc_root / "DBFilesClient"
    return nested if nested.is_dir() else dbc_root


def _load_donor_wdbcs(dbc_root: Path) -> dict[str, RawWdbc]:
    directory = _dbc_directory(dbc_root)
    loaded: dict[str, RawWdbc] = {}
    errors: list[str] = []
    for table_name in RACE_TABLES:
        path = directory / f"{table_name}.dbc"
        if not path.is_file():
            errors.append(f"missing donor DBC: {path}")
            continue
        try:
            data = path.read_bytes()
            table = RawWdbc(data)
        except (OSError, ValueError, struct.error) as exc:
            errors.append(f"donor WDBC header mismatch for {table_name}: {exc}")
            continue
        expected = WDBC_LAYOUTS[table_name]
        if (table.fields, table.record_size) != (expected.fields, expected.record_size):
            errors.append(
                f"donor WDBC header mismatch for {table_name}: "
                f"got fields={table.fields} record_size={table.record_size}, "
                f"expected fields={expected.fields} record_size={expected.record_size}"
            )
            continue
        if expected.race_offset + expected.race_width > table.record_size:
            errors.append(f"donor race byte range is outside {table_name} records")
            continue
        if expected.record_size == expected.fields * 4:
            try:
                Wdbc(data)
            except ValueError as exc:
                errors.append(f"donor WDBC field framing mismatch for {table_name}: {exc}")
                continue
        loaded[table_name] = table
    if errors:
        raise ValueError("; ".join(errors))
    return loaded


def _build_continuations(tables: dict[str, RawWdbc]) -> dict[str, bytes]:
    continuations: dict[str, bytes] = {}
    for table_name, table in tables.items():
        records: list[bytes] = []
        layout = WDBC_LAYOUTS[table_name]
        if table_name == "ChrRaces":
            row_ids = [RawWdbc._value(record, 0, 4) for record in table.records]
            if len(row_ids) != len(set(row_ids)):
                raise ValueError("duplicate row ID in production ChrRaces continuation")
        if table_name in RACE_ID_FIELDS:
            for source_race, target_race in ((19, 20), (20, 18)):
                source_records = tuple(
                    record
                    for record in table.records
                    if RawWdbc._value(record, layout.race_offset, layout.race_width) == source_race
                )
                records.extend(table.remap_race_records(table_name, source_race, target_race, source_records))
        else:
            field = layout.race_offset
            width = layout.race_width
            source_mask = (1 << 19) | (1 << 20)
            target_mask = (1 << 20) | (1 << 18)
            for record in table.records:
                value = RawWdbc._value(record, field, width)
                source_bits = value & source_mask
                if table_name == "SkillRaceClassInfo" and source_bits not in (0, source_mask):
                    raise ValueError(
                        "SkillRaceClassInfo donor row has incomplete source race mask; "
                        "expected both source race bits"
                    )
                if source_bits:
                    records.append(
                        RawWdbc._replace(record, field, width, remap_race_masks(value, source_mask, target_mask))
                    )
        if not records:
            continue
        output_name = f"DBFilesClient/{table_name}{CONTINUATION_SUFFIX}"
        continuations[output_name] = table.build(records)
    return dict(sorted(continuations.items()))


def _read_directory_entries(root: Path) -> dict[str, bytes]:
    entries: dict[str, bytes] = {}
    for path in sorted((path for path in root.rglob("*") if path.is_file()), key=lambda item: str(item).casefold()):
        relative = path.relative_to(root).as_posix().replace("/", "\\")
        name = str(safe_relative(relative)).replace("/", "\\")
        entries = merge_archive_entries(entries, {name: path.read_bytes()})
    return entries


def _read_patch_b_entries(patch_b_root: Path) -> dict[str, bytes]:
    if patch_b_root.is_dir():
        return _read_directory_entries(patch_b_root)
    if not patch_b_root.is_file():
        raise FileNotFoundError(patch_b_root)
    if not DLL_DEFAULT.is_file():
        raise FileNotFoundError(f"StormLib not found for Patch-B archive: {DLL_DEFAULT}")
    storm = Storm(DLL_DEFAULT)
    archive = storm.open_archive(patch_b_root)
    try:
        entries: dict[str, bytes] = {}
        for name, *_ in storm.list_files(archive):
            entries = merge_archive_entries(entries, {name: storm.read(archive, name)})
        return entries
    finally:
        storm.dll.SFileCloseArchive(archive)


def _stage_directory(output_root: Path, entries: dict[str, bytes]) -> None:
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.tmp-", dir=output_root.parent))
    try:
        for name, payload in sorted(entries.items(), key=lambda item: item[0].casefold()):
            destination = temporary_root / safe_relative(name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
        os.replace(temporary_root, output_root)
    except BaseException:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise


def _stage_archive(output_root: Path, source_path: Path, entries: dict[str, bytes]) -> Path:
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    archive_name = f"{source_path.stem}-vulpera-pandaren.MPQ"
    if not DLL_DEFAULT.is_file():
        raise FileNotFoundError(f"StormLib not found for staged archive: {DLL_DEFAULT}")
    archive_entries = {
        name: payload
        for name, payload in entries.items()
        if name.casefold() not in {"(listfile)", "(attributes)"}
    }
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.tmp-", dir=output_root.parent))
    temporary_archive = temporary_root / archive_name
    try:
        Storm(DLL_DEFAULT).create_archive(temporary_archive, archive_entries)
        os.replace(temporary_root, output_root)
    except BaseException:
        shutil.rmtree(temporary_root, ignore_errors=True)
        raise
    return output_root / archive_name


def _merge_manifest_entry(entries: dict[str, bytes], additions: bytes) -> dict[str, bytes]:
    normalized: dict[str, bytes] = {}
    for name, payload in entries.items():
        normalized = merge_archive_entries(normalized, {name: payload})
    manifest_names = [name for name in normalized if name.casefold() == "wxl-dbc.manifest"]
    manifest_name = manifest_names[0] if manifest_names else "wxl-dbc.manifest"
    existing = normalized.get(manifest_name, b"")
    merged_manifest = merge_wxl_manifest(existing, additions)
    without_manifest = {
        name: payload for name, payload in normalized.items() if name.casefold() != "wxl-dbc.manifest"
    }
    return merge_archive_entries(without_manifest, {manifest_name: merged_manifest})


def build_race_pack(dbc_root: Path, model_root: Path, patch_b_root: Path, output_root: Path) -> PackReport:
    """Validate donors, build continuations, and stage a Patch-B copy."""

    dbc_root = Path(dbc_root)
    model_root = Path(model_root)
    patch_b_root = Path(patch_b_root)
    output_root = Path(output_root)
    destination_path = output_root.resolve()
    for source_name, source_root in (
        ("DBC donor", dbc_root),
        ("model donor", model_root),
        ("Patch-B source", patch_b_root),
    ):
        source_path = source_root.resolve()
        if (
            source_path == destination_path
            or source_path in destination_path.parents
            or destination_path in source_path.parents
        ):
            raise ValueError(f"{source_name} and output paths must not overlap")
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    tables = _load_donor_wdbcs(dbc_root)
    assets = collect_race_assets(model_root)
    continuations = _build_continuations(tables)
    manifest_entries = tuple(sorted(continuations))
    additions = dict(assets.entries)
    additions.update(continuations)
    source_entries = _read_patch_b_entries(patch_b_root)
    collisions = tuple(
        sorted(
            name
            for name, payload in additions.items()
            if name.casefold() in {existing.casefold() for existing in source_entries}
            and any(
                existing.casefold() == name.casefold() and prior == payload
                for existing, prior in source_entries.items()
            )
        )
    )
    merged = merge_archive_entries(source_entries, additions)
    manifest = ("# Esteria additive Vulpera/Pandaren pack\n" + "\n".join(manifest_entries) + "\n").encode("utf-8")
    merged = _merge_manifest_entry(merged, manifest)
    if patch_b_root.is_dir():
        _stage_directory(output_root, merged)
        staged_name = str(output_root)
    else:
        staged_name = str(_stage_archive(output_root, patch_b_root, merged))
    return PackReport(
        continuations=continuations,
        asset_paths=assets.asset_paths,
        manifest_entries=manifest_entries,
        collisions=collisions,
        missing_requirements=(),
        sha256=assets.sha256,
        file_counts=assets.file_counts,
        staged_root=staged_name,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dbc-root",
        type=Path,
        default=Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\DBFilesClient"),
    )
    parser.add_argument(
        "--model-root",
        type=Path,
        default=Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-CHA.mpq"),
    )
    parser.add_argument(
        "--patch-b-root",
        type=Path,
        default=Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Extracted\patch-b.mpq"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(r"G:\Ascension\Ascension\resources\ascension-live\Data\Staging\Patch-B-vulpera-pandaren"),
    )
    args = parser.parse_args()
    report = build_race_pack(args.dbc_root, args.model_root, args.patch_b_root, args.output_root)
    print(
        json.dumps(
            {
                "staged_root": report.staged_root,
                "continuations": list(report.continuations),
                "assets": len(report.asset_paths),
                "file_counts": report.file_counts,
                "manifest_entries": list(report.manifest_entries),
                "collisions": list(report.collisions),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
