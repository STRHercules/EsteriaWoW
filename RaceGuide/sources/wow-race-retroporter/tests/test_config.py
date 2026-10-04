from pathlib import Path

from raceporter.config import load_project_config, load_race_manifest


def test_project_config_defaults_to_online_retail_source(project_root: Path):
    config = load_project_config(project_root)
    assert config.retail_source.mode == "online"
    assert config.retail_source.product == "wow"
    assert config.retail_source.region == "us"
    assert config.retail_source.locale == "enUS"
    assert config.retail_source.local_client_root is None


def test_project_config_resolves_source_and_cache_paths_inside_repo(project_root: Path):
    config = load_project_config(project_root)
    assert config.sources_root == project_root / "sources"
    assert config.retail_sources_root == project_root / "sources" / "retail"
    assert config.retail_db2_root == project_root / "sources" / "retail" / "db2"
    assert config.retail_races_root == project_root / "sources" / "retail" / "races"
    assert config.casc_cache_root == project_root / "cache" / "casc"


def test_local_retail_source_resolves_optional_client_path(tmp_path: Path):
    (tmp_path / "config").mkdir()
    (tmp_path / "sources" / "retail").mkdir(parents=True)
    (tmp_path / "sources" / "retail" / "build.yaml").write_text(
        "mode: local\nproduct: wow\nregion: us\nlocale: enUS\nlocal_client_root: local-retail\n",
        encoding="utf-8",
    )
    (tmp_path / "config" / "project.yaml").write_text(
        "paths:\n  retail_source_manifest: sources/retail/build.yaml\n  workspace_root: workspace\n",
        encoding="utf-8",
    )
    config = load_project_config(tmp_path)
    assert config.retail_source.mode == "local"
    assert config.retail_source.local_client_root == tmp_path / "local-retail"


def test_maghar_manifest_keeps_retail_and_target_ids_distinct(project_root: Path):
    race = load_race_manifest(project_root, "maghar_orc")
    assert race.retail_race_id == 36
    assert race.target_race_id == 45
    assert race.base_race == "orc"
