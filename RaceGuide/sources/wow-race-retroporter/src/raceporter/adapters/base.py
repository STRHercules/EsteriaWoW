from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def run_external_command(
    executable: Path,
    args: Sequence[str],
    *,
    cwd: Path,
    timeout: int | None = None,
) -> CommandResult:
    command = (str(executable), *args)
    process = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return CommandResult(command, process.returncode, process.stdout, process.stderr)
