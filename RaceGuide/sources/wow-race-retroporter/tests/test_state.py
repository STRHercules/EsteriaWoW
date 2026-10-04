from pathlib import Path

from raceporter.state import PipelineState


def test_completed_stage_is_skipped_unless_forced(tmp_path: Path):
    state = PipelineState(tmp_path / "state.json")
    assert state.should_run("discover", force=False)
    state.mark_complete("discover", summary="ok")
    assert not state.should_run("discover", force=False)
    assert state.should_run("discover", force=True)


def test_state_persists_between_instances(tmp_path: Path):
    path = tmp_path / "state.json"
    PipelineState(path).mark_complete("extract", summary="files exported")
    loaded = PipelineState(path)
    assert loaded.is_complete("extract")
    assert loaded.data["stages"]["extract"]["summary"] == "files exported"
