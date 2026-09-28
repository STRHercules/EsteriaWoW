from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ascension_hd_migration import _read_string, _table, _u32
from cars_mount_pack import DLL_DEFAULT, Storm, Wdbc
from wod_model_migration import archive_names

CLIENT = Path(r"G:\3.3.5a - Dev")
DATA = CLIENT / "Data"
OG = DATA / "OG"

OG_ORDER = (
    "PATCH-A.MPQ",
    "Patch-B.MPQ",
    "Patch-C.MPQ",
    "Patch-D.MPQ",
    "Patch-E.MPQ",
    "Patch-G.MPQ",
)

# These are the Project Reforged archives added in the user's 2026-09-28 import.
REFORGED = {
    "patch-a.mpq",
    "patch-b.mpq",
    "patch-c.mpq",
    "patch-d.mpq",
    "patch-e.mpq",
    "patch-g.mpq",
    "patch-i.mpq",
    "patch-m.mpq",
    "patch-n.mpq",
    "patch-p.mpq",
    "patch-s.mpq",
    "patch-u.mpq",
}

# Existing Esteria/client patches that predate the Reforged import and should
# remain authoritative if they already contain the same path.
ESTERIA_PATCHES = {
    "patch-f.mpq",
    "patch-o.mpq",
    "patch-v.mpq",
    "patch-w.mpq",
    "patch-x.mpq",
    "patch-y.mpq",
    "patch-z.mpq",
}

TARGETS = {
    "N": DATA / "patch-N.mpq",
    "P": DATA / "patch-P.mpq",
    "S": DATA / "patch-S.mpq",
    "U": DATA / "patch-U.mpq",
}

AREA_PATH = r"DBFilesClient\AreaTable.dbc"
META_FILES = {"(listfile)", "(attributes)"}
FLY_FLAG_MASK = 0x00000400 | 0x00004000
FLY_MAPS = {0, 1, 530}
MPQ_SAFE_LIMIT = 3_900_000_000
BATCH_LIMIT = 96 * 1024 * 1024


@dataclass(frozen=True)
class AssetRef:
    source_archive: Path
    source_name: str
    size: int
    original_patch: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def wow_running() -> bool:
    import subprocess

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", "Get-Process Wow -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Id"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return bool(result.stdout.strip())


def normalize(path: str) -> str:
    return path.replace("/", "\\").casefold()


def is_dbc(path: str) -> bool:
    return normalize(path).startswith("dbfilesclient\\")


def is_interface(path: str) -> bool:
    return normalize(path).startswith("interface\\")


def list_archive(storm: Storm, path: Path) -> list[tuple[str, int]]:
    handle = storm.open_archive(path)
    try:
        return [(name, size) for name, size, *_ in storm.list_files(handle)]
    finally:
        storm.dll.SFileCloseArchive(handle)


def read_archive(storm: Storm, path: Path, entry: str) -> bytes:
    handle = storm.open_archive(path)
    try:
        return storm.read(handle, entry)
    finally:
        storm.dll.SFileCloseArchive(handle)


def current_patch_paths(storm: Storm, names: set[str]) -> set[str]:
    result: set[str] = set()
    for archive in DATA.glob("*.mpq"):
        if archive.name.casefold() not in names:
            continue
        try:
            for name, _ in list_archive(storm, archive):
                result.add(normalize(name))
        except (OSError, UnicodeDecodeError):
            # The known target/source patch set uses ASCII paths. Ignore an
            # unrelated archive if its listfile cannot be enumerated.
            continue
    return result


def custom_race_roots(storm: Storm) -> set[str]:
    patch_z = DATA / "patch-Z.MPQ"
    handle = storm.open_archive(patch_z)
    try:
        names = archive_names(storm, handle)
        races = _table(storm.read(handle, names[r"dbfilesclient\chrraces.dbc"]), "ChrRaces")
        displays = _table(
            storm.read(handle, names[r"dbfilesclient\creaturedisplayinfo.dbc"]),
            "CreatureDisplayInfo",
        )
        models = _table(
            storm.read(handle, names[r"dbfilesclient\creaturemodeldata.dbc"]),
            "CreatureModelData",
        )
    finally:
        storm.dll.SFileCloseArchive(handle)

    display_by_id = {_u32(row, 0): row for row in displays.records}
    model_by_id = {_u32(row, 0): row for row in models.records}
    roots: set[str] = set()
    for row in races.records:
        if _u32(row, 0) <= 11:
            continue
        for display_id in (_u32(row, 4), _u32(row, 5)):
            display = display_by_id.get(display_id)
            if not display:
                continue
            model = model_by_id.get(_u32(display, 1))
            if not model:
                continue
            path = _read_string(models.strings, _u32(model, 2)).decode("latin1", "replace")
            parts = path.replace("/", "\\").split("\\")
            if len(parts) >= 2 and parts[0].casefold() == "character":
                roots.add(normalize("\\".join(parts[:2]) + "\\"))
    return roots


def effective_og_assets(storm: Storm) -> dict[str, AssetRef]:
    result: dict[str, AssetRef] = {}
    for archive_name in OG_ORDER:
        archive = OG / archive_name
        if not archive.exists():
            continue
        for name, size in list_archive(storm, archive):
            key = normalize(name)
            if name.casefold() in META_FILES or is_dbc(name):
                continue
            # Later OG patch letters replace earlier ones, matching the old
            # client's effective patch ordering.
            result[key] = AssetRef(archive, name, size, archive_name)
    return result


def route_for(asset: AssetRef, key: str, roots: set[str]) -> str:
    if is_interface(asset.source_name):
        return "U"
    if asset.original_patch.casefold() in {"patch-a.mpq", "patch-b.mpq", "patch-c.mpq"}:
        return "U"
    if asset.original_patch.casefold() in {"patch-d.mpq", "patch-g.mpq"}:
        return "N"
    if asset.original_patch.casefold() == "patch-e.mpq":
        return "P"
    # Defensive fallback. Interface and every known OG archive are handled above.
    return "U"


def select_assets(storm: Storm) -> tuple[dict[str, list[AssetRef]], dict[str, object]]:
    effective = effective_og_assets(storm)
    reforged_paths = current_patch_paths(storm, REFORGED)
    ester_paths = current_patch_paths(storm, ESTERIA_PATCHES)
    roots = custom_race_roots(storm)

    selected: dict[str, list[AssetRef]] = defaultdict(list)
    stats = {
        "effective_og_non_dbc": len(effective),
        "selected": 0,
        "selected_interface": 0,
        "selected_custom_race": 0,
        "selected_missing": 0,
        "skipped_newer_esteria": 0,
        "skipped_reforged_collision": 0,
        "custom_race_roots": sorted(roots),
    }

    for key, asset in sorted(effective.items()):
        # Never replace a path already shipped by a later Esteria patch. Those
        # files are newer than the OG snapshot and should remain authoritative.
        if key in ester_paths:
            stats["skipped_newer_esteria"] += 1
            continue

        under_custom_root = any(key.startswith(root) for root in roots)
        force = is_interface(asset.source_name) or under_custom_root
        if not force and key in reforged_paths:
            stats["skipped_reforged_collision"] += 1
            continue

        selected[route_for(asset, key, roots)].append(asset)
        stats["selected"] += 1
        if is_interface(asset.source_name):
            stats["selected_interface"] += 1
        elif under_custom_root:
            stats["selected_custom_race"] += 1
        else:
            stats["selected_missing"] += 1

    return selected, stats


def patch_area_table(data: bytes) -> tuple[bytes, dict[str, int]]:
    table = Wdbc(data)
    if table.fields != 36:
        raise ValueError(f"unexpected AreaTable field count: {table.fields}")
    rows = [row.copy() for row in table.rows]
    changed = 0
    eligible = 0
    for row in rows:
        if row[1] in FLY_MAPS and row[4] > 0:
            eligible += 1
            new_flags = row[4] | FLY_FLAG_MASK
            if new_flags != row[4]:
                row[4] = new_flags
                changed += 1
    body = b"".join(struct.pack(f"<{table.fields}I", *row) for row in rows)
    output = struct.pack(
        "<4s4I",
        b"WDBC",
        len(rows),
        table.fields,
        table.record_size,
        len(table.strings),
    ) + body + table.strings
    return output, {"eligible_rows": eligible, "changed_rows": changed}


def add_assets_batched(
    storm: Storm,
    target: Path,
    assets: list[AssetRef],
) -> tuple[dict[str, int], list[str]]:
    by_source: dict[Path, list[AssetRef]] = defaultdict(list)
    for asset in assets:
        by_source[asset.source_archive].append(asset)

    files_written = 0
    bytes_uncompressed = 0
    skipped_unreadable: list[str] = []
    for source, source_assets in by_source.items():
        source_handle = storm.open_archive(source)
        try:
            batch: dict[str, bytes] = {}
            batch_bytes = 0
            for asset in source_assets:
                try:
                    payload = storm.read(source_handle, asset.source_name)
                except OSError:
                    skipped_unreadable.append(asset.source_name)
                    continue
                if batch and batch_bytes + len(payload) > BATCH_LIMIT:
                    storm.replace_archive_entries(target, batch)
                    files_written += len(batch)
                    bytes_uncompressed += batch_bytes
                    batch = {}
                    batch_bytes = 0
                batch[asset.source_name] = payload
                batch_bytes += len(payload)
            if batch:
                storm.replace_archive_entries(target, batch)
                files_written += len(batch)
                bytes_uncompressed += batch_bytes
        finally:
            storm.dll.SFileCloseArchive(source_handle)
    return {
        "files_written": files_written,
        "uncompressed_bytes": bytes_uncompressed,
        "skipped_unreadable": len(skipped_unreadable),
    }, skipped_unreadable


def validate_selected(storm: Storm, staged: dict[str, Path], selected: dict[str, list[AssetRef]]) -> dict[str, int]:
    checked = 0
    for target_name, assets in selected.items():
        target = staged[target_name]
        target_handle = storm.open_archive(target)
        source_handles: dict[Path, object] = {}
        try:
            for asset in assets:
                source_handle = source_handles.get(asset.source_archive)
                if source_handle is None:
                    source_handle = storm.open_archive(asset.source_archive)
                    source_handles[asset.source_archive] = source_handle
                expected = storm.read(source_handle, asset.source_name)
                actual = storm.read(target_handle, asset.source_name)
                if actual != expected:
                    raise ValueError(f"asset validation failed: {asset.source_name} in {target_name}")
                checked += 1
        finally:
            for handle in source_handles.values():
                storm.dll.SFileCloseArchive(handle)
            storm.dll.SFileCloseArchive(target_handle)
    return {"asset_files_byte_verified": checked}


def validate_area(storm: Storm, staged_s: Path) -> dict[str, int]:
    payload = read_archive(storm, staged_s, AREA_PATH)
    table = Wdbc(payload)
    eligible = 0
    bad = 0
    for row in table.rows:
        if row[1] in FLY_MAPS and row[4] > 0:
            eligible += 1
            if (row[4] & FLY_FLAG_MASK) != FLY_FLAG_MASK:
                bad += 1
    if bad:
        raise ValueError(f"AreaTable validation failed: {bad} eligible rows still lack flight flags")
    return {"eligible_rows": eligible, "rows_missing_fly_flags": bad}


def stage(args: argparse.Namespace) -> Path:
    storm = Storm(args.stormlib)
    selected, selection_stats = select_assets(storm)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    staging = DATA / "Staging" / f"reforged-og-restore-{stamp}"
    staging.mkdir(parents=True, exist_ok=False)

    staged: dict[str, Path] = {}
    source_hashes: dict[str, str] = {}
    for key, live in TARGETS.items():
        if not live.exists():
            raise FileNotFoundError(live)
        dest = staging / live.name
        shutil.copy2(live, dest)
        staged[key] = dest
        source_hashes[key] = sha256(live)
        if sha256(dest) != source_hashes[key]:
            raise RuntimeError(f"staging copy hash mismatch for {live.name}")

    write_report: dict[str, object] = {}
    skipped_unreadable: dict[str, list[str]] = {}
    for key in ("N", "P", "U"):
        report, skipped = add_assets_batched(storm, staged[key], selected.get(key, []))
        write_report[key] = report
        skipped_unreadable[key] = skipped
        if skipped:
            skipped_keys = {normalize(name) for name in skipped}
            selected[key] = [asset for asset in selected.get(key, []) if normalize(asset.source_name) not in skipped_keys]
        if staged[key].stat().st_size >= MPQ_SAFE_LIMIT:
            raise RuntimeError(f"{staged[key].name} exceeds MPQ safety limit: {staged[key].stat().st_size}")

    area_payload = read_archive(storm, staged["S"], AREA_PATH)
    patched_area, area_report = patch_area_table(area_payload)
    storm.replace_archive_entries(staged["S"], {AREA_PATH: patched_area})

    validation = {}
    validation.update(validate_selected(storm, staged, selected))
    validation["area"] = validate_area(storm, staged["S"])

    manifest = {
        "created": stamp,
        "staging": str(staging),
        "source_hashes": source_hashes,
        "staged_hashes": {key: sha256(path) for key, path in staged.items()},
        "staged_sizes": {key: path.stat().st_size for key, path in staged.items()},
        "selection": selection_stats,
        "routed_counts": {key: len(selected.get(key, [])) for key in ("N", "P", "U")},
        "write_report": write_report,
        "skipped_unreadable": skipped_unreadable,
        "fly_anywhere": area_report,
        "validation": validation,
    }
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return staging


def apply(args: argparse.Namespace, staging: Path) -> None:
    if wow_running():
        raise RuntimeError("Wow.exe is running; close the client before applying staged MPQs")
    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))

    for key, live in TARGETS.items():
        if sha256(live) != manifest["source_hashes"][key]:
            raise RuntimeError(f"live {live.name} changed since staging")
        staged = staging / live.name
        if sha256(staged) != manifest["staged_hashes"][key]:
            raise RuntimeError(f"staged hash mismatch: {live.name}")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = CLIENT / "Backups" / f"pre-reforged-og-restore-{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    for key, live in TARGETS.items():
        shutil.copy2(live, backup / live.name)
        if sha256(backup / live.name) != manifest["source_hashes"][key]:
            raise RuntimeError(f"backup hash mismatch: {live.name}")
    shutil.copy2(staging / "manifest.json", backup / "staging-manifest.json")

    for key, live in TARGETS.items():
        staged = staging / live.name
        temporary = live.with_suffix(live.suffix + ".esteria-next")
        shutil.copy2(staged, temporary)
        if sha256(temporary) != manifest["staged_hashes"][key]:
            raise RuntimeError(f"temporary copy hash mismatch: {live.name}")
        os.replace(temporary, live)

    after = {key: sha256(path) for key, path in TARGETS.items()}
    if after != manifest["staged_hashes"]:
        raise RuntimeError(f"post-install hash mismatch: {after}")

    result = {"backup": str(backup), "live_hashes_after": after, "staging": str(staging)}
    (backup / "install-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore Esteria OG custom assets on top of Project Reforged without reverting HD DBCs")
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--stage-only", action="store_true")
    parser.add_argument("--apply-staged", type=Path)
    args = parser.parse_args()
    if args.apply_staged:
        apply(args, args.apply_staged.resolve())
        return 0
    stage(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
