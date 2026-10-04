from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PipelineState:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.data: dict[str, Any] = {"version": 1, "stages": {}}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.data = loaded
                self.data.setdefault("version", 1)
                self.data.setdefault("stages", {})

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def is_complete(self, stage: str) -> bool:
        return self.data.get("stages", {}).get(stage, {}).get("status") == "complete"

    def should_run(self, stage: str, *, force: bool) -> bool:
        return force or not self.is_complete(stage)

    def mark_complete(self, stage: str, *, summary: str = "") -> None:
        self.data.setdefault("stages", {})[stage] = {
            "status": "complete",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
        }
        self.save()

    def clear(self) -> None:
        if self.path.exists():
            self.path.unlink()
        self.data = {"version": 1, "stages": {}}
