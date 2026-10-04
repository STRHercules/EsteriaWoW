from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .assets import build_asset_plan, convert_asset_plan, write_asset_plan
from .config import DEFAULT
from .discovery import discover_race
from .player_runtime import prepare_maghar_runtime
from .races import RACES
from .wotlk import extract_db2


def doctor() -> int:
    checks = {
        "Retail root": DEFAULT.retail_root,
        "Wrath client": DEFAULT.wrath_root,
        "Listfile": DEFAULT.listfile,
        "WoWDBDefs": DEFAULT.dbd_dir,
        "TACT keys": DEFAULT.keys,
    }
    failed = False
    for label, path in checks.items():
        exists = path.exists()
        failed |= not exists
        print(f"{'OK' if exists else 'MISSING':7} {label:14} {path}")
    try:
        import wotlkconv  # noqa: F401
        print("OK      wotlkconv      importable")
    except ImportError:
        print("MISSING wotlkconv      install Bar3b0n3s/Converter")
        failed = True
    return 1 if failed else 0


def cmd_extract(args: argparse.Namespace) -> int:
    spec = RACES[args.race]
    source_root = Path(args.source_root) if args.source_root else None
    out = extract_db2(
        DEFAULT,
        spec.slug,
        source_root=source_root,
        source_product=args.source_product,
    )
    print(out)
    return 0


def cmd_discover(args: argparse.Namespace) -> int:
    spec = RACES[args.race]
    manifest = discover_race(DEFAULT, spec)
    reports = DEFAULT.work_root / spec.slug / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    target = reports / "discovery.json"
    target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    if len(manifest.get("race_ids", [])) > 1:
        print("RaceIDs:", ", ".join(str(value) for value in manifest["race_ids"]))
    else:
        print(f"RaceID: {manifest['race_id']}")
    print("ChrModel IDs:", ", ".join(str(value) for value in sorted({row['ChrModelID'] for row in manifest['model_links']})))
    print("Display IDs:", ", ".join(str(row['DisplayID']) for row in manifest['models']))
    print(f"Customization options: {len(manifest['options'])}")
    print(f"Customization choices: {len(manifest['choices'])}")
    print(f"Customization elements: {len(manifest['elements'])}")
    print(f"FileDataIDs found: {len(manifest['file_data_ids'])}")
    print(f"Manifest: {target}")
    return 0


def cmd_plan_assets(args: argparse.Namespace) -> int:
    spec = RACES[args.race]
    source_root = Path(args.source_root) if args.source_root else None
    plan = build_asset_plan(
        DEFAULT,
        spec,
        source_root=source_root,
        source_product=args.source_product,
    )
    path = write_asset_plan(DEFAULT, spec, plan)
    print(f"Selected assets: {len(plan['selected_file_ids'])}")
    print(f"Unsupported Retail-only assets: {len(plan['unsupported'])}")
    print(f"Plan: {path}")
    return 0


def cmd_convert_assets(args: argparse.Namespace) -> int:
    spec = RACES[args.race]
    source_root = Path(args.source_root) if args.source_root else None
    plan = build_asset_plan(
        DEFAULT,
        spec,
        source_root=source_root,
        source_product=args.source_product,
    )
    write_asset_plan(DEFAULT, spec, plan)
    out = convert_asset_plan(
        DEFAULT,
        spec,
        plan,
        dry_run=args.dry_run,
        source_root=source_root,
        source_product=args.source_product,
    )
    print(f"Output: {out}")
    return 0


def cmd_prepare_player_runtime(args: argparse.Namespace) -> int:
    if args.race != "maghar":
        raise NotImplementedError("Retail player-material splitting is validated with Mag'har first")
    report = prepare_maghar_runtime(DEFAULT)
    print(report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="retroporter")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")

    extract = sub.add_parser("extract-db2")
    extract.add_argument("--race", choices=sorted(RACES), default="maghar")
    extract.add_argument("--source-root")
    extract.add_argument("--source-product")

    discover = sub.add_parser("discover")
    discover.add_argument("--race", choices=sorted(RACES), default="maghar")

    plan_assets = sub.add_parser("plan-assets")
    plan_assets.add_argument("--race", choices=sorted(RACES), default="maghar")
    plan_assets.add_argument("--source-root")
    plan_assets.add_argument("--source-product")

    convert = sub.add_parser("convert-assets")
    convert.add_argument("--race", choices=sorted(RACES), default="maghar")
    convert.add_argument("--dry-run", action="store_true")
    convert.add_argument("--source-root")
    convert.add_argument("--source-product")

    runtime = sub.add_parser("prepare-player-runtime")
    runtime.add_argument("--race", choices=sorted(RACES), default="maghar")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        return doctor()
    if args.command == "extract-db2":
        return cmd_extract(args)
    if args.command == "discover":
        return cmd_discover(args)
    if args.command == "plan-assets":
        return cmd_plan_assets(args)
    if args.command == "convert-assets":
        return cmd_convert_assets(args)
    if args.command == "prepare-player-runtime":
        return cmd_prepare_player_runtime(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
