from pathlib import Path

from raceporter.config import load_project_config, load_race_manifest
from raceporter.stages.base import StageContext
from raceporter.stages.preflight import run_preflight


def test_online_preflight_does_not_require_local_retail_client(project_root: Path):
    project = load_project_config(project_root)
    race = load_race_manifest(project_root, "maghar_orc")
    result = run_preflight(StageContext(project_root, project, race))
    assert result.status == "complete"
    assert "online Retail source" in result.summary


def test_local_preflight_requires_casc_like_client(tmp_path: Path):
    (tmp_path / "config").mkdir()
    (tmp_path / "races").mkdir()
    (tmp_path / "sources" / "retail").mkdir(parents=True)
    (tmp_path / "sources" / "retail" / "build.yaml").write_text(
        "mode: local\nproduct: wow\nregion: us\nlocale: enUS\nlocal_client_root: local-retail\n",
        encoding="utf-8",
    )
    (tmp_path / "config" / "project.yaml").write_text(
        "paths:\n  retail_source_manifest: sources/retail/build.yaml\n",
        encoding="utf-8",
    )
    (tmp_path / "races" / "maghar_orc.yaml").write_text(
        "slug: maghar_orc\ndisplay_name: Maghar\nretail_race_id: 36\ntarget_race_id: 19\nfaction: horde\nbase_race: orc\n",
        encoding="utf-8",
    )
    project = load_project_config(tmp_path)
    race = load_race_manifest(tmp_path, "maghar_orc")
    result = run_preflight(StageContext(tmp_path, project, race))
    assert result.status == "blocked"
    assert "local Retail CASC source" in result.summary
