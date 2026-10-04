from __future__ import annotations

import json
from pathlib import Path

from .config import Config
from .races import RaceSpec
from .wotlk import output_dir, run_converter


def load_discovery(config: Config, spec: RaceSpec) -> dict:
    path = config.work_root / spec.slug / "reports" / "discovery.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run discover first.")
    return json.loads(path.read_text(encoding="utf-8"))


def _core_model_texture_file_ids(
    config: Config,
    spec: RaceSpec,
    *,
    source_root: Path | None = None,
    source_product: str | None = None,
) -> set[int]:
    """Read modern TXID chunks so converted M2 hard texture refs are shipped too."""
    from wotlkconv.casc import CascStorage, KeyRing
    from wotlkconv.m2 import parse_m2

    storage = CascStorage.open(
        source_root or config.retail_root,
        product=source_product or config.product,
        keys=KeyRing.load(config.keys),
    )
    try:
        texture_ids: set[int] = set()
        for model_file_id in spec.core_model_file_ids:
            model = parse_m2(storage.read_file_id(model_file_id), f"FileDataID {model_file_id}")
            texture_ids.update(file_id for file_id in (model.texture_file_ids or ()) if file_id)
        return texture_ids
    finally:
        storage.close()


def build_asset_plan(
    config: Config,
    spec: RaceSpec,
    *,
    source_root: Path | None = None,
    source_product: str | None = None,
) -> dict:
    if not spec.ready_for_assets:
        raise RuntimeError(
            f"{spec.retail_name} is discovery-only until its live source IDs and asset roots are verified."
        )
    discovery = load_discovery(config, spec)
    selected: list[dict] = []
    unsupported: list[dict] = []
    ignored: list[dict] = []

    assets = list(discovery["file_assets"])
    known_ids = {int(asset["file_data_id"]) for asset in assets}
    direct_texture_ids = _core_model_texture_file_ids(
        config,
        spec,
        source_root=source_root,
        source_product=source_product,
    )
    required_ids = set(spec.core_model_file_ids) | set(spec.required_file_ids) | direct_texture_ids
    missing_required = required_ids - known_ids
    if missing_required:
        from wotlkconv.listfile import Listfile

        listfile = Listfile.load(config.listfile)
        assets.extend(
            {"file_data_id": file_id, "path": listfile.path_for(file_id)}
            for file_id in sorted(missing_required)
        )

    for asset in assets:
        file_id = int(asset["file_data_id"])
        path = (asset.get("path") or "").replace("/", "\\")
        lower = path.lower()
        ext = Path(lower).suffix

        in_race_root = any(lower.startswith(root.lower()) for root in spec.asset_roots)
        if file_id in spec.core_model_file_ids:
            selected.append({**asset, "reason": "core player/customization model"})
        elif file_id in spec.required_file_ids:
            selected.append({**asset, "reason": "required race dependency"})
        elif file_id in direct_texture_ids:
            selected.append({**asset, "reason": "core M2 hard texture dependency"})
        elif in_race_root and ext == ".blp":
            selected.append({**asset, "reason": f"{spec.retail_name} customization texture"})
        elif in_race_root and ext == ".bone":
            unsupported.append({**asset, "reason": "Retail .bone override has no Wrath equivalent"})
        else:
            ignored.append({**asset, "reason": f"not part of the initial {spec.retail_name}-safe asset slice"})

    selected_ids = sorted({int(row["file_data_id"]) for row in selected})
    return {
        "race": spec.slug,
        "path_prefix": f"custom\\{spec.slug}",
        "selected_file_ids": selected_ids,
        "direct_model_texture_file_ids": sorted(direct_texture_ids),
        "selected": selected,
        "unsupported": unsupported,
        "ignored": ignored,
    }


def write_asset_plan(config: Config, spec: RaceSpec, plan: dict) -> Path:
    reports = config.work_root / spec.slug / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    path = reports / "asset-plan.json"
    path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def convert_asset_plan(
    config: Config,
    spec: RaceSpec,
    plan: dict,
    *,
    dry_run: bool = False,
    source_root: Path | None = None,
    source_product: str | None = None,
) -> Path:
    # Converter's --path-prefix rewrites references inside converted assets,
    # but does not relocate each top-level output file. Put the converter's
    # output directory at the same physical prefix so the eventual MPQ tree
    # matches the rewritten in-file paths exactly.
    out = output_dir(config, spec.slug) / "patch-root" / "custom" / spec.slug
    report = config.work_root / spec.slug / "reports" / (
        "asset-convert-dryrun.json" if dry_run else "asset-convert.json"
    )
    args = [
        "convert",
        "--casc",
        str(source_root or config.retail_root),
        "--casc-product",
        source_product or config.product,
        "--casc-keys",
        str(config.keys),
        "--listfile",
        str(config.listfile),
        "--path-prefix",
        plan["path_prefix"],
        "-o",
        str(out),
        "--report",
        str(report),
        "-j",
        "4",
    ]
    for file_id in plan["selected_file_ids"]:
        args.extend(["--fileid", str(file_id)])
    if dry_run:
        args.append("--dry-run")
    run_converter(args)
    return out
