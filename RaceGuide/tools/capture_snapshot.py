"""Capture source and provenance into RaceGuide; never build, install, or change live data."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys


SUFFIXES = {".py", ".cpp", ".h", ".hpp", ".inl", ".def", ".bat", ".ps1", ".sh", ".lua", ".xml",
            ".toc", ".sql", ".md", ".json", ".yaml", ".yml", ".toml", ".cmake", ".txt", ".dist"}
SKIP = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", "cache", "workspace",
        "build", "deps", "raw", "output", "patch-root", "retail-db2", "source-audit", "cdn-source", "sources"}
BASELINE = "a29b5dc"


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def git(root, *args):
    result = subprocess.run(["rtk", "proxy", "git", *args], cwd=root, capture_output=True, check=True)
    return result.stdout.decode("utf-8", errors="replace")


def files(root):
    if root.is_file():
        yield root
        return
    for directory, folders, names in os.walk(root):
        folders[:] = sorted(n for n in folders if n not in SKIP and not n.endswith(".egg-info"))
        for name in sorted(names):
            path = Path(directory) / name
            if path.suffix.lower() in SUFFIXES or name in {"LICENSE", "COPYING", "AUTHORS"}:
                yield path


def python_entry(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    arguments = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"add_argument", "add_parser"}:
                arguments.append(ast.unparse(node))
    imports = sorted({n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module})
    return {"summary": ast.get_docstring(tree), "arguments": arguments, "imports": imports}


def capture(args):
    out = Path(__file__).resolve().parents[1]
    evidence = out / "evidence"
    copied = []
    missing = []
    index = []

    def copy(source, relative):
        if not source.is_file():
            missing.append(str(source))
            return
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        digest = sha256(source)
        sanitized = source.name == "docker-compose.override.yml"
        if sanitized:
            content = target.read_text(encoding="utf-8")
            content = re.sub(r'(?m)^(\s*AzerothCore__SoapPassword:).*$',
                             r'\1 "${ESTERIA_SOAP_PASSWORD}"', content)
            target.write_text(content, encoding="utf-8", newline="\n")
        if not sanitized and sha256(target) != digest:
            raise RuntimeError(f"Snapshot copy differs: {source}")
        copied.append({"source": str(source), "snapshot": relative.as_posix(),
                       "bytes": target.stat().st_size, "sha256": sha256(target),
                       "source_sha256": digest, "credentials_redacted": sanitized})
        if source.suffix == ".py":
            try:
                index.append({"snapshot": relative.as_posix(), "source": str(source), **python_entry(source)})
            except (SyntaxError, UnicodeError) as error:
                index.append({"snapshot": relative.as_posix(), "parse_error": str(error)})

    server = args.server
    trees = [(server / name, Path("sources/EsteriaWoW") / name) for name in (
        "tools", "client-customization", "wxl-races-patcher", "docs", "data/retroported-races",
        "data/sql/updates/pending_db_world", "data/sql/updates/pending_db_characters",
        "modules/mod-custom-server", "modules/mod-wxl-dbc", "modules/mod-classless-wildcard",
        "modules/mod-worgoblin-high-elf/src", "modules/mod-playerbots/src/Bot/Factory")]
    trees += [(server / ".agents/plans" / name, Path("sources/historical-plans") / name) for name in (
        "character-select-redesign", "races-9-port", "ascension-customization", "100-character-support",
        "race-retroport-pipeline", "appearance-expansion-direct-dbc", "appearancebuddy-global-eluna",
        "car-mounts", "character-create-race-art", "creature-races-port", "custom-race-initialization",
        "darkfallen-hd", "darkfallen-playable-race", "dreadlord-override", "elvui-glue-reskin",
        "esteria-mount-import", "eunoia-race-port", "forgotten-race-name", "freeborn-client",
        "freeborn-hostility", "freeborn-login-crash", "freeborn-teamid", "freeborn-third-teamid",
        "freeborn-tooltip", "highmountain-port", "login-persistence-fix", "mount-render-fix",
        "races-64-esteria", "sethrak-client-deployment", "sethrak-race-migration", "sethrak-skill-fix",
        "tauren-third-gender", "tuskarr-feet-robe", "vulpera-pandaren-playable-races", "vulpera-port",
        "wxl-vulpera-head-diagnostic")]
    trees += [(args.scaffold, Path("sources/wow-race-retroporter")),
              (args.retroporter, Path("sources/RetroPorter")),
              (args.wxl / "extensions/races-64-esteria", Path("sources/WarcraftXL/extensions/races-64-esteria")),
              (args.wxl / "include", Path("sources/WarcraftXL/include")),
              (args.wxl / "src", Path("sources/WarcraftXL/src"))]
    trees += [(args.client / "Extensions/races-64-esteria", Path("sources/client-active/Extensions/races-64-esteria")),
              (args.client / "Extensions/z-darkfallen-character-select",
               Path("sources/client-active/Extensions/z-darkfallen-character-select"))]
    trees += [(args.wxl / "extensions", Path("sources/WarcraftXL/extensions")),
              (args.wxl / "docs", Path("sources/WarcraftXL/docs"))]
    for source, relative in trees:
        if not source.exists():
            missing.append(str(source))
        for path in files(source):
            copy(path, relative / path.relative_to(source))
    for name in ("CMakeLists.txt", "build.ps1", "README.md", "LICENSE", "COPYING"):
        copy(args.wxl / name, Path("sources/WarcraftXL") / name)
    for name in ("build.yaml", "README.md", "db2/README.md", "races/README.md"):
        copy(args.scaffold / "sources/retail" / name, Path("sources/wow-race-retroporter/sources/retail") / name)
    for name in ("LICENSE", "docker-compose.yml", "docker-compose.override.yml", "Modules.md", "ModuleStatus.md",
                 "CUSTOM_SERVER.md", "DARKFALLEN-REBOOT-HANDOFF.md", "RACIALS.md", "WODMODELS.md", "UI.md"):
        copy(server / name, Path("sources/EsteriaWoW") / name)

    core_paths = ["src", "conf/dist", "apps/docker", "CMakeLists.txt", "modules/CMakeLists.txt"]
    names = git(server, "diff", "--name-only", BASELINE, "--", *core_paths).splitlines()
    for name in names:
        source = server / name
        if source.is_dir():
            for path in files(source):
                copy(path, Path("sources/EsteriaWoW") / path.relative_to(server))
        else:
            copy(source, Path("sources/EsteriaWoW") / name)
    patch_paths = core_paths + ["modules/mod-custom-server/src", "modules/mod-wxl-dbc",
                              "modules/mod-classless-wildcard/src", "modules/mod-playerbots/src/Bot/Factory"]
    patch = git(server, "diff", "--no-ext-diff", "--no-color", BASELINE, "--", *patch_paths)
    (evidence / "server-since-core-import.patch").write_text(patch, encoding="utf-8", newline="\n")
    (evidence / "core-changed-files.tsv").write_text(
        git(server, "diff", "--numstat", BASELINE, "--", *core_paths), encoding="utf-8", newline="\n")

    for race in sorted(p for p in args.work.iterdir() if p.is_dir()):
        for path in race.glob("*.py"):
            copy(path, Path("sources/RetroPorterWork") / path.relative_to(args.work))
        for folder in (race / "reports", race / "integration"):
            for path in sorted(folder.glob("*.json")):
                copy(path, Path("evidence/workspaces") / path.relative_to(args.work))

    conversations = json.loads((evidence / "conversations.json").read_text(encoding="utf-8"))
    extra = {s for c in conversations for s in c["source_paths"] + c["script_tokens"]}
    normalized = {Path(s.replace("\\", "/")) for s in extra if ":" in s and s.endswith(".py")}
    for path in sorted(normalized):
        text = path.as_posix()
        if "/.codex/tmp/" in text or "/Local/Temp/maghar-face-investigation/" in text:
            marker = "/.codex/tmp/" if "/.codex/tmp/" in text else "/Local/Temp/"
            copy(path, Path("sources/historical-diagnostics") / text.split(marker, 1)[1])
    copy(server / ".agents/plans/races-9-port/verify_helm_coverage.py",
         Path("sources/historical-diagnostics/verify_helm_coverage.py"))

    converter = importlib.util.find_spec("wotlkconv")
    packages = {}
    if converter and converter.submodule_search_locations:
        package_root = Path(next(iter(converter.submodule_search_locations)))
        for path in files(package_root):
            copy(path, Path("sources/Converter/wotlkconv") / path.relative_to(package_root))
    for name in ("wotlkconv", "Pillow", "lupa", "PyYAML", "minidump", "esteria-retroporter",
                 "wow-race-retroporter", "capstone"):
        try:
            dist = importlib.metadata.distribution(name)
            packages[name] = {"version": dist.version, "direct_url": dist.read_text("direct_url.json"),
                              "requires": dist.requires}
        except importlib.metadata.PackageNotFoundError:
            packages[name] = {"available": False}

    artifacts = []
    paths = list(args.client.glob("Esteria*.bin")) + list(args.client.glob("*.dll"))
    paths += [args.client / "Wow.exe"] + list((args.client / "Extensions").glob("*/*.dll"))
    for path in sorted(set(paths)):
        row = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
        if path.suffix == ".bin":
            with path.open("rb") as handle:
                head = handle.read(12)
            row["header_u32"] = list(struct.unpack("<III", head)) if len(head) == 12 else None
        artifacts.append(row)
    archives = [{"path": str(p), "bytes": p.stat().st_size} for p in sorted((args.client / "Data").rglob("*.MPQ"))]
    portraits = [{"path": str(p), "bytes": p.stat().st_size, "sha256": sha256(p)}
                for p in sorted(args.portraits.rglob("*.png"))]
    for item in portraits:
        path = Path(item["path"])
        copy(path, Path("sources/Portraits") / path.relative_to(args.portraits))
    modules = [{"name": p.name, "readme": str(p / "README.md"),
                "source_files": sum(1 for _ in files(p))}
               for p in sorted((server / "modules").iterdir()) if p.is_dir() and p.name.startswith("mod-")]
    write_json(evidence / "client-artifacts.json", {"artifacts": artifacts, "archives_sizes_only": archives})
    write_json(evidence / "portraits.json", portraits)
    write_json(evidence / "modules.json", modules)
    write_json(evidence / "python-environment.json", {"python": sys.version, "packages": packages})
    write_json(evidence / "tool-index.json", index)
    write_json(evidence / "snapshot-manifest.json", {"baseline": BASELINE,
        "server_head": git(server, "rev-parse", "HEAD").strip(), "files": copied,
        "missing_sources": sorted(set(missing)), "server_status": git(server, "status", "--short")})
    print(json.dumps({"copied_files": len(copied), "source_bytes": sum(c["bytes"] for c in copied),
                      "missing_sources": len(set(missing)), "python_entries": len(index)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Verify saved copies without reading live sources")
    parser.add_argument("--server", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--scaffold", type=Path, default=Path(r"R:\Users\Zach\Documents\GitHub\wow-race-retroporter"))
    parser.add_argument("--retroporter", type=Path, default=Path(r"R:\Users\Zach\Documents\GitHub\RetroPorter"))
    parser.add_argument("--work", type=Path, default=Path(r"G:\RetroPorterWork"))
    parser.add_argument("--client", type=Path, default=Path(r"G:\3.3.5a - Dev"))
    parser.add_argument("--portraits", type=Path, default=Path(r"R:\Users\Zach\Pictures\Portraits"))
    parser.add_argument("--wxl", type=Path,
                        default=Path(r"R:\Users\Zach\Documents\GitHub\AzerothPlex\build\wxl-core"))
    args = parser.parse_args()
    if args.verify:
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "evidence/snapshot-manifest.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            if sha256(root / item["snapshot"]) != item["sha256"]:
                raise RuntimeError(f"Snapshot differs: {item['snapshot']}")
        print(f"Verified {len(manifest['files'])} snapshot copies")
    else:
        capture(args)


if __name__ == "__main__":
    main()
