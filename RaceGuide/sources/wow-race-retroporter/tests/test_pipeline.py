from pathlib import Path

from raceporter.pipeline import PIPELINE_STAGE_NAMES, PipelineRunner
from raceporter.state import PipelineState


def test_pipeline_stage_order_is_stable():
    assert PIPELINE_STAGE_NAMES == [
        "preflight",
        "discover",
        "extract",
        "inventory",
        "convert-model",
        "convert-textures",
        "build-customization",
        "generate-dbc",
        "generate-acore-sql",
        "generate-glue",
        "validate",
        "package",
    ]


def test_dry_run_does_not_mark_stages_complete(project_root: Path, tmp_path: Path):
    state = PipelineState(tmp_path / "state.json")
    runner = PipelineRunner(project_root=project_root, race_slug="maghar_orc", state=state)
    results = runner.run(dry_run=True)
    assert [result.name for result in results] == PIPELINE_STAGE_NAMES
    assert not state.is_complete("preflight")


def test_fetch_stage_subset_stops_after_inventory():
    from raceporter.pipeline import FETCH_STAGE_NAMES

    assert FETCH_STAGE_NAMES == ["preflight", "discover", "extract", "inventory"]


def test_fetch_dry_run_only_plans_source_stages(project_root: Path, tmp_path: Path):
    from raceporter.pipeline import FETCH_STAGE_NAMES

    state = PipelineState(tmp_path / "state.json")
    runner = PipelineRunner(project_root=project_root, race_slug="maghar_orc", state=state)
    results = runner.run(dry_run=True, stages=FETCH_STAGE_NAMES)
    assert [result.name for result in results] == FETCH_STAGE_NAMES
    assert all(result.status == "planned" for result in results)
