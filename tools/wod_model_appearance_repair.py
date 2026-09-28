"""Repair Esteria's WoD stock-race appearance contract after the initial model splice.

This is deliberately narrower than the original migration:
- backs up the currently migrated patch-Z/enUS-Z;
- imports donor CharSections-referenced textures that live only in patch-w.mpq;
- replaces stock-race rows in CharHairGeosets, CharacterFacialHairStyles, and
  BarberShopStyle with the donor client's active rows;
- preserves all non-stock/custom race rows;
- rebuilds staged MPQs to discard stale replacement blocks;
- validates donor equality for the stock appearance contract before install.

It does not touch Wow.exe, SQL, server code, or custom-race appearance rows.
"""

from __future__ import annotations

import argparse
import ctypes as c
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL_DIR))

from ascension_hd_migration import (  # noqa: E402
    _next_row_id,
    _read_string,
    _rebase_strings,
    _set_u32,
    _table,
    _u32,
)
from cars_mount_pack import DLL_DEFAULT, H, Storm  # noqa: E402
from wod_model_migration import (  # noqa: E402
    archive_names,
    rebuild_archive_streaming,
    sha256,
    splice_dbcs,
)


STOCK_RACES = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 10, 11})


def try_read(storm: Storm, handle: H, path: str) -> bytes | None:
    try:
        return storm.read(handle, path)
    except OSError:
        return None


def donor_hidden_texture_payloads(
    storm: Storm,
    donor_x_assets: Path,
    donor_w_assets: Path,
    donor_char_sections: bytes,
) -> dict[str, bytes]:
    """Find stock CharSections textures absent from X but addressable by hash in W."""

    sections = _table(donor_char_sections, "CharSections")
    referenced: set[str] = set()
    for row in sections.records:
        if _u32(row, 1) not in STOCK_RACES:
            continue
        for field in (4, 5, 6):
            offset = _u32(row, field)
            if not offset:
                continue
            value = _read_string(sections.strings, offset).decode("utf-8")
            if value:
                referenced.add(value.replace("/", "\\"))

    x_handle = storm.open_archive(donor_x_assets)
    w_handle = storm.open_archive(donor_w_assets)
    try:
        result: dict[str, bytes] = {}
        unresolved: list[str] = []
        for path in sorted(referenced, key=str.casefold):
            if try_read(storm, x_handle, path) is not None:
                continue
            payload = try_read(storm, w_handle, path)
            if payload is not None:
                result[path] = payload
            else:
                unresolved.append(path)
    finally:
        storm.dll.SFileCloseArchive(w_handle)
        storm.dll.SFileCloseArchive(x_handle)

    # The donor can legitimately resolve some older non-HD component textures
    # from lower stock MPQs. The repair only needs the files uniquely supplied
    # by patch-w, so unresolved lower-archive paths are informational.
    print(
        f"CharSections referenced textures: {len(referenced)}; "
        f"hidden W-only: {len(result)}; lower-archive/unresolved: {len(unresolved)}"
    )
    return result


def replace_stock_rows(
    table_name: str,
    base_data: bytes,
    donor_data: bytes,
    race_field: int,
    *,
    keyed_ids: bool,
) -> bytes:
    """Use donor rows for stock races while retaining all custom-race rows."""

    base = _table(base_data, table_name)
    donor = _table(donor_data, table_name)
    if (base.fields, base.record_size) != (donor.fields, donor.record_size):
        raise ValueError(
            f"{table_name} layout mismatch: "
            f"base={base.fields}/{base.record_size} donor={donor.fields}/{donor.record_size}"
        )

    preserved = [row for row in base.records if _u32(row, race_field) not in STOCK_RACES]
    selected = [row for row in donor.records if _u32(row, race_field) in STOCK_RACES]
    selected, strings = _rebase_strings(table_name, selected, donor.strings, base.strings)

    if keyed_ids:
        used_ids = {_u32(row, 0) for row in preserved}
        next_id = _next_row_id(preserved)
        normalized: list[bytes] = []
        for row in selected:
            row_id = _u32(row, 0)
            if row_id in used_ids:
                while next_id in used_ids:
                    next_id += 1
                row = _set_u32(row, 0, next_id)
                row_id = next_id
                next_id += 1
            used_ids.add(row_id)
            normalized.append(row)
        selected = normalized

    return base.build(preserved + selected, strings)


def canonical_rows(data: bytes, table_name: str, race_field: int) -> list[tuple[int, ...]]:
    """Canonical numeric stock rows; IDs are excluded where they are merge-local."""

    table = _table(data, table_name)
    rows: list[tuple[int, ...]] = []
    for raw in table.records:
        if _u32(raw, race_field) not in STOCK_RACES:
            continue
        values = tuple(_u32(raw, field) for field in range(table.fields))
        # CharHairGeosets and BarberShopStyle have synthetic row IDs that may
        # be renumbered to avoid colliding with preserved custom-race IDs.
        if table_name in {"CharHairGeosets", "BarberShopStyle"}:
            values = values[1:]
        rows.append(values)
    return sorted(rows)


def canonical_barber_rows(data: bytes) -> list[tuple[object, ...]]:
    """Canonical BarberShopStyle rows including rebased strings but excluding row ID."""

    table = _table(data, "BarberShopStyle")
    string_fields = set(tuple(range(2, 18)) + tuple(range(19, 35)))
    rows: list[tuple[object, ...]] = []
    for raw in table.records:
        if _u32(raw, 37) not in STOCK_RACES:
            continue
        values: list[object] = []
        for field in range(1, table.fields):
            if field in string_fields:
                values.append(_read_string(table.strings, _u32(raw, field)))
            else:
                values.append(_u32(raw, field))
        rows.append(tuple(values))
    return sorted(rows, key=repr)


def splice_payloads(storm: Storm, archive_path: Path, entries: dict[str, bytes]) -> None:
    archive = storm.open_archive(archive_path)
    try:
        storm.ensure_capacity(archive, len(entries))
        for name, payload in entries.items():
            file_handle = H()
            flags = 0x80000000  # MPQ_FILE_REPLACEEXISTING
            if not storm.dll.SFileCreateFile(
                archive,
                name.encode("ascii"),
                0,
                len(payload),
                0,
                flags,
                c.byref(file_handle),
            ):
                raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
            finished = False
            try:
                buffer = c.create_string_buffer(payload or b"\0")
                if not storm.dll.SFileWriteFile(file_handle, buffer, len(payload), 0x00000002):
                    raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
                if not storm.dll.SFileFinishFile(file_handle):
                    raise OSError(f"SFileFinishFile failed: {name} ({c.get_last_error()})")
                finished = True
            finally:
                if not finished:
                    storm.dll.SFileCloseFile(file_handle)
    finally:
        storm.dll.SFileCloseArchive(archive)


def load_tables(storm: Storm, archive: Path, table_names: tuple[str, ...]) -> dict[str, bytes]:
    handle = storm.open_archive(archive)
    try:
        names = archive_names(storm, handle)
        result: dict[str, bytes] = {}
        for table in table_names:
            key = rf"DBFilesClient\{table}.dbc"
            actual = names.get(key.casefold())
            if actual is None:
                raise KeyError(f"{archive} is missing {key}")
            result[table] = storm.read(handle, actual)
        return result
    finally:
        storm.dll.SFileCloseArchive(handle)


def count_stock(data: bytes, table_name: str, race_field: int) -> int:
    table = _table(data, table_name)
    return sum(1 for row in table.records if _u32(row, race_field) in STOCK_RACES)


def validate(
    storm: Storm,
    patch_z: Path,
    enus_z: Path,
    hidden_textures: dict[str, bytes],
    donor_geosets: bytes,
    donor_facial: bytes,
    donor_barber: bytes,
) -> dict[str, object]:
    assets = storm.open_archive(patch_z)
    try:
        hidden_hashes: dict[str, str] = {}
        for name, expected in hidden_textures.items():
            actual = storm.read(assets, name)
            if actual != expected:
                raise ValueError(f"hidden texture differs from donor: {name}")
            hidden_hashes[name] = hashlib.sha256(actual).hexdigest()
    finally:
        storm.dll.SFileCloseArchive(assets)

    tables = load_tables(
        storm,
        enus_z,
        ("CharHairGeosets", "CharacterFacialHairStyles", "BarberShopStyle", "CharHairTextures"),
    )

    if canonical_rows(tables["CharHairGeosets"], "CharHairGeosets", 1) != canonical_rows(
        donor_geosets, "CharHairGeosets", 1
    ):
        raise ValueError("live stock CharHairGeosets contract does not match donor")
    if canonical_rows(
        tables["CharacterFacialHairStyles"], "CharacterFacialHairStyles", 0
    ) != canonical_rows(donor_facial, "CharacterFacialHairStyles", 0):
        raise ValueError("live stock CharacterFacialHairStyles contract does not match donor")
    if canonical_barber_rows(tables["BarberShopStyle"]) != canonical_barber_rows(donor_barber):
        raise ValueError("live stock BarberShopStyle contract does not match donor")

    return {
        "hidden_w_textures_verified": len(hidden_textures),
        "hidden_w_texture_sha256": hidden_hashes,
        "stock_rows": {
            "CharHairGeosets": count_stock(tables["CharHairGeosets"], "CharHairGeosets", 1),
            "CharacterFacialHairStyles": count_stock(
                tables["CharacterFacialHairStyles"], "CharacterFacialHairStyles", 0
            ),
            "BarberShopStyle": count_stock(tables["BarberShopStyle"], "BarberShopStyle", 37),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair WoD stock-race appearance DBCs and hidden textures")
    parser.add_argument("--client-root", type=Path, default=Path(r"G:\3.3.5a - Dev"))
    parser.add_argument(
        "--donor-root",
        type=Path,
        default=Path(r"F:\Wrath of the Lich King 3.3.5a (wod models)"),
    )
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client_root = args.client_root.resolve()
    donor_root = args.donor_root.resolve()
    patch_z = client_root / "Data" / "patch-Z.MPQ"
    enus_z = client_root / "Data" / "enUS" / "patch-enUS-Z.MPQ"
    donor_x_assets = donor_root / "Data" / "patch-x.mpq"
    donor_w_assets = donor_root / "Data" / "patch-w.mpq"
    donor_x_locale = donor_root / "Data" / "enUS" / "patch-enUS-x.mpq"
    donor_base_locale = donor_root / "Data" / "enUS" / "patch-enUS.MPQ"
    donor_3_locale = donor_root / "Data" / "enUS" / "patch-enUS-3.MPQ"

    required = (
        patch_z,
        enus_z,
        donor_x_assets,
        donor_w_assets,
        donor_x_locale,
        donor_base_locale,
        donor_3_locale,
        args.stormlib,
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    storm = Storm(args.stormlib)
    current = load_tables(
        storm,
        enus_z,
        ("CharHairGeosets", "CharacterFacialHairStyles", "BarberShopStyle"),
    )
    donor_x = load_tables(storm, donor_x_locale, ("CharSections",))
    donor_base = load_tables(
        storm,
        donor_base_locale,
        ("CharHairGeosets", "CharacterFacialHairStyles"),
    )
    donor_3 = load_tables(storm, donor_3_locale, ("BarberShopStyle",))

    hidden_textures = donor_hidden_texture_payloads(
        storm,
        donor_x_assets,
        donor_w_assets,
        donor_x["CharSections"],
    )
    merged_dbcs = {
        "CharHairGeosets": replace_stock_rows(
            "CharHairGeosets",
            current["CharHairGeosets"],
            donor_base["CharHairGeosets"],
            1,
            keyed_ids=True,
        ),
        "CharacterFacialHairStyles": replace_stock_rows(
            "CharacterFacialHairStyles",
            current["CharacterFacialHairStyles"],
            donor_base["CharacterFacialHairStyles"],
            0,
            keyed_ids=False,
        ),
        "BarberShopStyle": replace_stock_rows(
            "BarberShopStyle",
            current["BarberShopStyle"],
            donor_3["BarberShopStyle"],
            37,
            keyed_ids=True,
        ),
    }

    summary = {
        "apply": args.apply,
        "hidden_w_textures": len(hidden_textures),
        "stock_rows_before": {
            "CharHairGeosets": count_stock(current["CharHairGeosets"], "CharHairGeosets", 1),
            "CharacterFacialHairStyles": count_stock(
                current["CharacterFacialHairStyles"], "CharacterFacialHairStyles", 0
            ),
            "BarberShopStyle": count_stock(current["BarberShopStyle"], "BarberShopStyle", 37),
        },
        "stock_rows_after": {
            "CharHairGeosets": count_stock(merged_dbcs["CharHairGeosets"], "CharHairGeosets", 1),
            "CharacterFacialHairStyles": count_stock(
                merged_dbcs["CharacterFacialHairStyles"], "CharacterFacialHairStyles", 0
            ),
            "BarberShopStyle": count_stock(merged_dbcs["BarberShopStyle"], "BarberShopStyle", 37),
        },
    }
    print(json.dumps(summary, indent=2))
    if not args.apply:
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = client_root / "Backups" / f"wod-appearance-repair-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup_patch_z = backup_dir / patch_z.name
    backup_enus_z = backup_dir / enus_z.name
    staged_patch_z = backup_dir / "STAGED-patch-Z.MPQ"
    staged_enus_z = backup_dir / "STAGED-patch-enUS-Z.MPQ"

    print(f"Backing up current migrated archives to {backup_dir}")
    shutil.copy2(patch_z, backup_patch_z)
    shutil.copy2(enus_z, backup_enus_z)
    before = {
        "patch-Z.MPQ": {"size": patch_z.stat().st_size, "sha256": sha256(patch_z)},
        "patch-enUS-Z.MPQ": {"size": enus_z.stat().st_size, "sha256": sha256(enus_z)},
    }

    print("Creating staged copies")
    shutil.copy2(patch_z, staged_patch_z)
    shutil.copy2(enus_z, staged_enus_z)

    print(f"Importing {len(hidden_textures)} hidden patch-w textures")
    splice_payloads(storm, staged_patch_z, hidden_textures)
    print("Replacing stock-race appearance DBC rows")
    splice_dbcs(storm, staged_enus_z, merged_dbcs)

    print("Rebuilding staged MPQs")
    rebuilt_patch_z = backup_dir / "REBUILT-patch-Z.MPQ"
    rebuilt_enus_z = backup_dir / "REBUILT-patch-enUS-Z.MPQ"
    rebuild_archive_streaming(storm, staged_patch_z, rebuilt_patch_z)
    rebuild_archive_streaming(storm, staged_enus_z, rebuilt_enus_z)
    staged_patch_z.unlink()
    staged_enus_z.unlink()
    rebuilt_patch_z.replace(staged_patch_z)
    rebuilt_enus_z.replace(staged_enus_z)

    print("Validating staged repair")
    validation = validate(
        storm,
        staged_patch_z,
        staged_enus_z,
        hidden_textures,
        donor_base["CharHairGeosets"],
        donor_base["CharacterFacialHairStyles"],
        donor_3["BarberShopStyle"],
    )

    print("Installing validated repair")
    os.replace(staged_patch_z, patch_z)
    os.replace(staged_enus_z, enus_z)
    after = {
        "patch-Z.MPQ": {"size": patch_z.stat().st_size, "sha256": sha256(patch_z)},
        "patch-enUS-Z.MPQ": {"size": enus_z.stat().st_size, "sha256": sha256(enus_z)},
    }
    report = {
        "backup_dir": str(backup_dir),
        "before": before,
        "after": after,
        "summary": summary,
        "validation": validation,
    }
    report_path = backup_dir / "repair.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
