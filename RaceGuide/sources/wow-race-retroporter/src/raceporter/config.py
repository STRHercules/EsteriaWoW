from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import ProjectConfig, RaceManifest, RetailSourceConfig


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return data


def _resolve(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (root / path).resolve()


def _load_retail_source(root: Path, project_data: dict[str, Any]) -> RetailSourceConfig:
    paths = project_data.get("paths", {})
    manifest_path = _resolve(root, paths.get("retail_source_manifest", "sources/retail/build.yaml"))
    data = _load_yaml(manifest_path)
    mode = str(data.get("mode", "online")).lower()
    local_value = data.get("local_client_root")
    local_root = _resolve(root, local_value) if local_value else None
    build = data.get("build", {}) if isinstance(data.get("build", {}), dict) else {}
    source = RetailSourceConfig(
        mode=mode,
        product=str(data.get("product", "wow")),
        region=str(data.get("region", "us")),
        locale=str(data.get("locale", "enUS")),
        build_version=str(build.get("version", "auto")),
        build_key=str(build.get("build_key", "auto")),
        local_client_root=local_root,
        raw=data,
    )
    errors = source.validate()
    if errors:
        raise ValueError("Invalid Retail source configuration: " + "; ".join(errors))
    return source


def load_project_config(project_root: Path | str) -> ProjectConfig:
    root = Path(project_root).resolve()
    data = _load_yaml(root / "config" / "project.yaml")
    paths = data.get("paths", {})
    workspace = _resolve(root, paths.get("workspace_root", "workspace"))
    sources = _resolve(root, paths.get("sources_root", "sources"))
    retail_sources = _resolve(root, paths.get("retail_sources_root", sources / "retail"))
    cache = _resolve(root, paths.get("cache_root", "cache"))
    return ProjectConfig(
        project_root=root,
        retail_source=_load_retail_source(root, data),
        sources_root=sources,
        retail_sources_root=retail_sources,
        retail_db2_root=_resolve(root, paths.get("retail_db2_root", retail_sources / "db2")),
        retail_races_root=_resolve(root, paths.get("retail_races_root", retail_sources / "races")),
        cache_root=cache,
        casc_cache_root=_resolve(root, paths.get("casc_cache_root", cache / "casc")),
        workspace_root=workspace,
        extracted_root=_resolve(root, paths.get("extracted_root", workspace / "extracted")),
        converted_root=_resolve(root, paths.get("converted_root", workspace / "converted")),
        generated_root=_resolve(root, paths.get("generated_root", workspace / "generated")),
        packages_root=_resolve(root, paths.get("packages_root", workspace / "packages")),
        state_root=_resolve(root, paths.get("state_root", workspace / "state")),
        logs_root=_resolve(root, paths.get("logs_root", workspace / "logs")),
        raw=data,
    )


def load_race_manifest(project_root: Path | str, race_slug: str) -> RaceManifest:
    root = Path(project_root).resolve()
    data = _load_yaml(root / "races" / f"{race_slug}.yaml")
    manifest = RaceManifest(
        slug=str(data.get("slug", "")),
        display_name=str(data.get("display_name", "")),
        retail_race_id=int(data.get("retail_race_id", 0)),
        target_race_id=int(data.get("target_race_id", 0)),
        faction=str(data.get("faction", "")).lower(),
        base_race=str(data.get("base_race", "")),
        raw=data,
    )
    if manifest.slug != race_slug:
        raise ValueError(f"Manifest slug {manifest.slug!r} does not match filename slug {race_slug!r}")
    errors = manifest.validate()
    if errors:
        raise ValueError("Invalid race manifest: " + "; ".join(errors))
    return manifest
