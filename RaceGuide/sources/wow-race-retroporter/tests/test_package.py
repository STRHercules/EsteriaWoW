from pathlib import Path

from raceporter.packaging import is_package_safe_path


def test_retail_source_assets_are_never_package_safe(project_root: Path):
    source_asset = project_root / "sources" / "retail" / "races" / "maghar_orc" / "male" / "model.m2"
    assert not is_package_safe_path(project_root, source_asset)


def test_casc_cache_is_never_package_safe(project_root: Path):
    cached_asset = project_root / "cache" / "casc" / "data" / "example"
    assert not is_package_safe_path(project_root, cached_asset)


def test_generated_output_is_package_safe(project_root: Path):
    generated = project_root / "workspace" / "generated" / "maghar_orc" / "sql" / "race.sql"
    assert is_package_safe_path(project_root, generated)
