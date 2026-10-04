from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable

from .config import load_project_config, load_race_manifest
from .state import PipelineState
from .stages.base import StageContext, StageResult
from .stages.preflight import run_preflight
from .stages.scaffold import run_scaffold_stage


PIPELINE_STAGE_NAMES = [
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

FETCH_STAGE_NAMES = PIPELINE_STAGE_NAMES[:4]


class PipelineRunner:
    def __init__(self, *, project_root: Path | str, race_slug: str, state: PipelineState | None = None):
        self.project_root = Path(project_root).resolve()
        self.project = load_project_config(self.project_root)
        self.race = load_race_manifest(self.project_root, race_slug)
        self.state = state or PipelineState(self.project.state_root / f"{race_slug}.json")
        self.context = StageContext(self.project_root, self.project, self.race)

    def run(
        self,
        *,
        dry_run: bool = False,
        force: bool = False,
        stages: Iterable[str] | None = None,
    ) -> list[StageResult]:
        selected = list(stages) if stages is not None else PIPELINE_STAGE_NAMES
        unknown = [name for name in selected if name not in PIPELINE_STAGE_NAMES]
        if unknown:
            raise ValueError(f"Unknown pipeline stage(s): {', '.join(unknown)}")

        results: list[StageResult] = []
        for name in selected:
            if dry_run:
                status = "complete" if self.state.is_complete(name) and not force else "planned"
                results.append(StageResult(name, status, "dry-run"))
                continue

            if not self.state.should_run(name, force=force):
                results.append(StageResult(name, "skipped", "already complete"))
                continue

            result = run_preflight(self.context) if name == "preflight" else run_scaffold_stage(name, self.context)
            results.append(result)
            if result.status == "complete":
                self.state.mark_complete(name, summary=result.summary)
                continue
            if result.status == "blocked":
                break
        return results
