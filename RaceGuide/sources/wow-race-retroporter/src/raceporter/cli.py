from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from .config import load_project_config, load_race_manifest
from .pipeline import FETCH_STAGE_NAMES, PIPELINE_STAGE_NAMES, PipelineRunner
from .state import PipelineState


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "config" / "project.yaml").exists() and (candidate / "races").exists():
            return candidate
    raise FileNotFoundError("Could not find project root containing config/project.yaml and races/")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="raceporter", description="Retail WoW race retroport pipeline scaffold")
    parser.add_argument("--project-root", type=Path, help="Repository root; auto-detected by default")
    subs = parser.add_subparsers(dest="command", required=True)

    subs.add_parser("doctor", help="Validate repository, Retail source profile, and configured tools")

    fetch = subs.add_parser("fetch", help="Discover and cache source assets for a race")
    fetch.add_argument("race")
    fetch.add_argument("--dry-run", action="store_true")
    fetch.add_argument("--force", action="store_true")

    plan = subs.add_parser("plan", help="Show stage status for a race")
    plan.add_argument("race")

    build = subs.add_parser("build", help="Run/resume the full retroport pipeline")
    build.add_argument("race")
    build.add_argument("--dry-run", action="store_true")
    build.add_argument("--force", action="store_true")

    status = subs.add_parser("status", help="Print saved stage state")
    status.add_argument("race")

    reset = subs.add_parser("reset", help="Clear saved stage state")
    reset.add_argument("race")
    return parser


def _root(args: argparse.Namespace) -> Path:
    return args.project_root.resolve() if args.project_root else find_project_root()


def command_doctor(root: Path) -> int:
    project = load_project_config(root)
    source = project.retail_source
    problems: list[str] = []

    if source.mode == "local":
        local = source.local_client_root
        if local is None or not local.exists() or not (local / "Data").exists():
            problems.append(f"Local Retail CASC source is not populated at: {local or '<unset>'}")

    tools_file = root / "config" / "tools.yaml"
    tools = yaml.safe_load(tools_file.read_text(encoding="utf-8")) or {}
    missing_tools: list[str] = []
    for name, config in tools.get("tools", {}).items():
        source_modes = config.get("source_modes")
        if source_modes and source.mode not in source_modes:
            continue
        executable = Path(str(config.get("executable", "")))
        executable = executable if executable.is_absolute() else root / executable
        if not executable.exists():
            missing_tools.append(f"{name} ({config.get('mode', 'unknown')}): {executable}")

    print(f"Project: {root}")
    print(f"Retail source: {source.mode} ({source.product}/{source.region}/{source.locale})")
    print(f"Source cache: {project.retail_sources_root}")
    print(f"CASC cache:   {project.casc_cache_root}")
    if source.mode == "local":
        print(f"Local CASC:   {source.local_client_root}")
    else:
        print("Local CASC:   not required")

    for problem in problems:
        print(f"BLOCKED: {problem}")

    if missing_tools:
        print("External tools not installed/configured yet:")
        for item in missing_tools:
            print(f"  - {item}")
    else:
        print("External tools: OK")
    return 1 if problems else 0


def command_fetch(root: Path, race_slug: str, *, dry_run: bool, force: bool) -> int:
    runner = PipelineRunner(project_root=root, race_slug=race_slug)
    results = runner.run(dry_run=dry_run, force=force, stages=FETCH_STAGE_NAMES)
    blocked = False
    for result in results:
        print(f"[{result.status:8}] {result.name}: {result.summary}")
        blocked = blocked or result.status == "blocked"
    return 2 if blocked else 0


def command_plan(root: Path, race_slug: str) -> int:
    project = load_project_config(root)
    race = load_race_manifest(root, race_slug)
    state = PipelineState(project.state_root / f"{race_slug}.json")
    print(f"{race.display_name}: Retail ID {race.retail_race_id} -> target ID {race.target_race_id}")
    for name in PIPELINE_STAGE_NAMES:
        print(f"[{'complete' if state.is_complete(name) else 'pending ':8}] {name}")
    return 0


def command_build(root: Path, race_slug: str, *, dry_run: bool, force: bool) -> int:
    runner = PipelineRunner(project_root=root, race_slug=race_slug)
    results = runner.run(dry_run=dry_run, force=force)
    blocked = False
    for result in results:
        print(f"[{result.status:8}] {result.name}: {result.summary}")
        blocked = blocked or result.status == "blocked"
    return 2 if blocked else 0


def command_status(root: Path, race_slug: str) -> int:
    project = load_project_config(root)
    state = PipelineState(project.state_root / f"{race_slug}.json")
    print(yaml.safe_dump(state.data, sort_keys=False).rstrip())
    return 0


def command_reset(root: Path, race_slug: str) -> int:
    project = load_project_config(root)
    path = project.state_root / f"{race_slug}.json"
    PipelineState(path).clear()
    print(f"Cleared pipeline state: {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = _root(args)
        if args.command == "doctor":
            return command_doctor(root)
        if args.command == "fetch":
            return command_fetch(root, args.race, dry_run=args.dry_run, force=args.force)
        if args.command == "plan":
            return command_plan(root, args.race)
        if args.command == "build":
            return command_build(root, args.race, dry_run=args.dry_run, force=args.force)
        if args.command == "status":
            return command_status(root, args.race)
        if args.command == "reset":
            return command_reset(root, args.race)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1
