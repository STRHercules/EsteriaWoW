from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm


DATA = Path(r"G:\3.3.5a - Dev\Data")
ARCHIVES = (DATA / "patch-Z.MPQ", DATA / "enUS" / "patch-enUS-Z.MPQ")
ENTRY = r"Interface\GlueXML\AccountLogin.lua"
SAMPLE = r"Interface\GlueXML\AccountLogin.xml"
EXPECTED_LIVE_ENTRY_SHA256 = "45b5f96c4e7679dfe3110af78440a90ed26194ffdd093cbcbde5aedfe1ef86f3"
SOURCE = ROOT / ".agents" / "plans" / "login-persistence-fix" / "stage" / "AccountLogin.lua"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_entries(storm: Storm, archive_path: Path) -> tuple[bytes, bytes]:
    archive = storm.open_archive(archive_path)
    try:
        return storm.read(archive, ENTRY), storm.read(archive, SAMPLE)
    finally:
        storm.dll.SFileCloseArchive(archive)


def main() -> None:
    patched_lua = SOURCE.read_bytes()
    storm = Storm(DLL_DEFAULT)
    before = {path: read_entries(storm, path) for path in ARCHIVES}
    for path, (lua, _) in before.items():
        if hashlib.sha256(lua).hexdigest() != EXPECTED_LIVE_ENTRY_SHA256:
            raise RuntimeError(f"refusing unexpected login script in {path}")

    backup_dir = DATA / "_login-persistence-backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir.mkdir(parents=True, exist_ok=False)
    for path in ARCHIVES:
        backup = backup_dir / path.name
        shutil.copy2(path, backup)
        if sha256(path) != sha256(backup):
            raise RuntimeError(f"backup mismatch: {backup}")

    changed: list[Path] = []
    try:
        for path in ARCHIVES:
            changed.append(path)
            storm.replace_archive_entries(path, {ENTRY: patched_lua})
            lua, sample = read_entries(storm, path)
            if lua != patched_lua or sample != before[path][1]:
                raise RuntimeError(f"archive readback failed: {path}")
    except BaseException:
        for path in changed:
            shutil.copy2(backup_dir / path.name, path)
            if sha256(path) != sha256(backup_dir / path.name):
                raise RuntimeError(f"rollback verification failed: {path}")
        raise

    print(f"verified backups: {backup_dir}")
    for path in ARCHIVES:
        print(f"{path.name}: archive sha256={sha256(path)}; login entry readback exact")


if __name__ == "__main__":
    main()
