from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from raceporter.models import ProjectConfig, RaceManifest


@dataclass(frozen=True)
class StageContext:
    project_root: Path
    project: ProjectConfig
    race: RaceManifest


@dataclass(frozen=True)
class StageResult:
    name: str
    status: str
    summary: str


class StageBlocked(RuntimeError):
    """Raised when a stage needs a human/tool implementation checkpoint."""
