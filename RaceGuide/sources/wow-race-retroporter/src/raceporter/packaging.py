from __future__ import annotations

from pathlib import Path


UNSAFE_TOP_LEVEL = {"sources", "cache", "tools"}


def is_package_safe_path(project_root: Path | str, candidate: Path | str) -> bool:
    root = Path(project_root).resolve()
    path = Path(candidate).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    if not relative.parts:
        return False
    if relative.parts[0].lower() in UNSAFE_TOP_LEVEL:
        return False
    return True
