"""Build an additive WDBC/model pack for Vulpera and Alliance Pandaren."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from dataclasses import dataclass
from pathlib import Path

from cars_mount_pack import (
    DBC_STRING_FIELDS,
    DLL_DEFAULT,
    Storm,
    WOTLK_MODEL_VERSION,
    Wdbc,
    build_wdbc,
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


def _load_donor_wdbcs(dbc_root: Path) -> dict[str, Wdbc]:
    directory = _dbc_directory(dbc_root)
    loaded: dict[str, Wdbc] = {}
    errors: list[str] = []
    for table_name in RACE_TABLES:
        path = directory / f"{table_name}.dbc"
        if not path.is_file():
            errors.append(f"missing donor DBC: {path}")
            continue
        try:
            table = Wdbc(path.read_bytes())
        except (OSError, ValueError, struct.error) as exc:
            errors.append(f"donor WDBC header mismatch for {table_name}: {exc}")
            continue
        configured_field = RACE_ID_FIELDS.get(table_name, RACE_MASK_FIELDS.get(table_name))
        if configured_field is None or configured_field >= table.fields:
            errors.append(f"donor field position mismatch for {table_name}: field {configured_field}")
            continue
        if table_name in RACE_ID_FIELDS:
            source_ids = set(SOURCE_RACES.values())
            configured_hits = sum(row[configured_field] in source_ids for row in table.rows)
            alternate_fields = [
                index
                for index in range(table.fields)
                if any(row[index] in source_ids for row in table.rows)
            ]
            if not configured_hits and alternate_fields:
                errors.append(
                    f"donor field position mismatch for {table_name}: "
                    f"configured {configured_field}, observed {alternate_fields}"
                )
        loaded[table_name] = table
    if errors:
        raise ValueError("; ".join(errors))
    return loaded


def _string_map(table_name: str, table: Wdbc, rows: list[list[int]]) -> dict[tuple[int, int], str]:
    strings: dict[tuple[int, int], str] = {}
    for row_index, row in enumerate(rows):
        for field in DBC_STRING_FIELDS.get(table_name, ()):
            if field >= len(row) or not row[field]:
                continue
            value = table.text(row[field])
            if value:
                strings[(row_index, field)] = value
    return strings


def _build_continuations(tables: dict[str, Wdbc]) -> dict[str, bytes]:
    continuations: dict[str, bytes] = {}
    for table_name, table in tables.items():
        rows: list[list[int]] = []
        if table_name in RACE_ID_FIELDS:
            field = RACE_ID_FIELDS[table_name]
            for source_race, target_race in ((19, 20), (20, 18)):
                source_rows = [row for row in table.rows if row[field] == source_race]
                rows.extend(remap_race_rows(table_name, source_rows, source_race, target_race))
        else:
            field = RACE_MASK_FIELDS[table_name]
            source_mask = (1 << 19) | (1 << 20)
            target_mask = (1 << 20) | (1 << 18)
            rows = [
                [
                    remap_race_masks(value, source_mask, target_mask) if index == field else value
                    for index, value in enumerate(row)
                ]
                for row in table.rows
                if row[field] & source_mask
            ]
        if not rows:
            continue
        strings = _string_map(table_name, table, rows)
        output_name = f"DBFilesClient/{table_name}{CONTINUATION_SUFFIX}"
        continuations[output_name] = build_wdbc(rows, table.fields, table.record_size, strings)
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
        return {name: storm.read(archive, name) for name, *_ in storm.list_files(archive)}
    finally:
        storm.dll.SFileCloseArchive(archive)


def _stage_directory(output_root: Path, entries: dict[str, bytes]) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for name, payload in sorted(entries.items(), key=lambda item: item[0].casefold()):
        destination = output_root / safe_relative(name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.read_bytes() != payload:
            raise ValueError(f"staged path collision with different bytes: {name}")
        if not destination.exists():
            destination.write_bytes(payload)


def _stage_archive(output_root: Path, source_path: Path, entries: dict[str, bytes]) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    staged_path = output_root / f"{source_path.stem}-vulpera-pandaren.MPQ"
    if staged_path.exists():
        raise FileExistsError(f"refusing to overwrite staged archive: {staged_path}")
    if not DLL_DEFAULT.is_file():
        raise FileNotFoundError(f"StormLib not found for staged archive: {DLL_DEFAULT}")
    archive_entries = dict(entries)
    archive_entries["(listfile)"] = ("\n".join(sorted(entries)) + "\n").encode("utf-8")
    Storm(DLL_DEFAULT).create_archive(staged_path, archive_entries)
    return staged_path


def build_race_pack(dbc_root: Path, model_root: Path, patch_b_root: Path, output_root: Path) -> PackReport:
    """Validate donors, build continuations, and stage a Patch-B copy."""

    dbc_root = Path(dbc_root)
    model_root = Path(model_root)
    patch_b_root = Path(patch_b_root)
    output_root = Path(output_root)
    if patch_b_root.is_dir() and output_root.resolve() == patch_b_root.resolve():
        raise ValueError("output_root must not be the Patch-B source directory")
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
            and any(existing.casefold() == name.casefold() and prior == payload for existing, prior in source_entries.items())
        )
    )
    merged = merge_archive_entries(source_entries, additions)
    existing_manifest = source_entries.get("wxl-dbc.manifest", b"")
    manifest = ("# Esteria additive Vulpera/Pandaren pack\n" + "\n".join(manifest_entries) + "\n").encode("utf-8")
    merged["wxl-dbc.manifest"] = merge_wxl_manifest(existing_manifest, manifest)
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
