from __future__ import annotations

import hashlib
import os
import re
import shutil
import sys
import tempfile
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from cars_mount_pack import DLL_DEFAULT, Storm
import freeborn_team_pack as freeborn

CLIENT = Path(r"G:\3.3.5a - Dev")
DATA = CLIENT / "Data"
ROOT_ARCHIVE = DATA / "patch-Z.MPQ"
LOCALE_ARCHIVE = DATA / "enUS" / "patch-enUS-Z.MPQ"
CONFIG = CLIENT / "WTF" / "Config.wtf"

GLUE = "Interface\\GlueXML\\"
SOURCE_GLUE = ROOT / ".agents" / "plans" / "character-select-redesign" / "src" / "GlueXML"
LOGIN_SOURCE = ROOT / ".agents" / "plans" / "login-persistence-fix" / "stage" / "AccountLogin.lua"

DIRECT_GLUE_SOURCES = {
    GLUE + "AccountLogin.lua": LOGIN_SOURCE,
    GLUE + "ECS_Constants.lua": SOURCE_GLUE / "ECS_Constants.lua",
    GLUE + "ECS_Persistence.lua": SOURCE_GLUE / "ECS_Persistence.lua",
    GLUE + "ECS_Integrate.lua": SOURCE_GLUE / "ECS_Integrate.lua",
}

DELIMITER = "#&|&#"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_updates(storm: Storm, archive: Path, include_assets: bool) -> dict[str, bytes]:
    updates = freeborn._glue_updates(storm, archive)
    if include_assets:
        updates.update(freeborn._client_asset_updates())
    for entry, source in DIRECT_GLUE_SOURCES.items():
        updates[entry] = source.read_bytes()
    return updates


def read_entry(storm: Storm, archive: Path, entry: str) -> bytes:
    handle = storm.open_archive(archive)
    try:
        return storm.read(handle, entry)
    finally:
        storm.dll.SFileCloseArchive(handle)


def patch_archive(storm: Storm, archive: Path, updates: dict[str, bytes]) -> None:
    temporary = archive.parent / f".{archive.name}.login-persistence-tmp"
    shutil.copy2(archive, temporary)
    try:
        storm.replace_archive_entries(temporary, updates)
        handle = storm.open_archive(temporary)
        try:
            for entry, expected in updates.items():
                actual = storm.read(handle, entry)
                if actual != expected:
                    raise RuntimeError(f"staged readback mismatch: {archive.name}: {entry}")
        finally:
            storm.dll.SFileCloseArchive(handle)
        os.replace(temporary, archive)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def parse_config_value(lines: list[str], key: str) -> str | None:
    prefix = f'SET {key} "'
    for line in lines:
        if line.startswith(prefix) and line.endswith('"'):
            return line[len(prefix):-1]
    return None


def recover_login_payload(raw_voice_line: str, existing_account: str | None) -> str | None:
    candidates: list[str] = []
    for encoded in re.findall(r"(?:^|[|;])a=([^|]+)", raw_voice_line):
        decoded = urllib.parse.unquote(encoded)
        if DELIMITER in decoded:
            candidates.append(decoded)

    recovered = next((value for value in candidates if value.split(DELIMITER, 1)[0]), None)
    if not recovered:
        return None

    fields = recovered.split(DELIMITER)
    while len(fields) < 4:
        fields.append("")

    existing_fields = (existing_account or "").split(DELIMITER)
    scene = fields[3]
    if not scene and len(existing_fields) >= 4:
        scene = existing_fields[3]
    if not scene:
        scene = "ww"

    account, password, auto_login = fields[0], fields[1], fields[2] or "0"
    if not account:
        return None
    return DELIMITER.join((account, password, auto_login, scene))


def config_line(key: str, value: str) -> str:
    # The recovered values in this client are ordinary CVar-safe strings. Keep
    # the serialization conservative for a quoted Config.wtf assignment.
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'SET {key} "{value}"'


def repair_config(path: Path) -> dict[str, bool]:
    if not path.is_file():
        return {"config_present": False, "login_recovered": False, "realm_recovered": False}

    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    voice_prefix = 'SET Sound_VoiceChatInputDriverName "'
    voice_index = next((i for i, line in enumerate(lines) if line.startswith(voice_prefix)), None)
    if voice_index is None:
        return {"config_present": True, "login_recovered": False, "realm_recovered": False}

    voice_line = lines[voice_index]
    existing_account = parse_config_value(lines, "accountName")
    recovered_login = recover_login_payload(voice_line, existing_account)

    badge_match = re.search(r"fb:([0-9,]+)\|", voice_line)
    if badge_match:
        clean_voice = f"fb:{badge_match.group(1)}|System Default"
    else:
        clean_voice = "System Default"
    lines[voice_index] = config_line("Sound_VoiceChatInputDriverName", clean_voice)

    embedded_realm = re.search(r'SET realmName "([^"]+)"', voice_line)
    existing_realm = parse_config_value(lines, "realmName")
    recovered_realm = existing_realm or (embedded_realm.group(1) if embedded_realm else None)

    def replace_or_append(key: str, value: str | None) -> None:
        if value is None:
            return
        prefix = f"SET {key} "
        replacement = config_line(key, value)
        indexes = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if indexes:
            lines[indexes[0]] = replacement
            for extra in reversed(indexes[1:]):
                del lines[extra]
        else:
            lines.append(replacement)

    replace_or_append("realmName", recovered_realm)
    replace_or_append("accountName", recovered_login or existing_account)

    repaired = "\n".join(lines).rstrip("\n") + "\n"
    path.write_text(repaired, encoding="utf-8", newline="\n")

    # Structural validation: accountName and realmName must each be their own
    # physical SET line, and no ECS envelope/control separator may remain in the
    # dedicated Freeborn CVar.
    final_lines = repaired.splitlines()
    voice = parse_config_value(final_lines, "Sound_VoiceChatInputDriverName") or ""
    if "ecs" in voice or "\x1e" in voice or "\x1f" in voice or "SET accountName" in voice or "SET realmName" in voice:
        raise RuntimeError("Config.wtf repair validation failed for voice CVar")
    if recovered_login and parse_config_value(final_lines, "accountName") != recovered_login:
        raise RuntimeError("Config.wtf repair validation failed for accountName")
    if recovered_realm and parse_config_value(final_lines, "realmName") != recovered_realm:
        raise RuntimeError("Config.wtf repair validation failed for realmName")

    return {
        "config_present": True,
        "login_recovered": bool(recovered_login),
        "realm_recovered": bool(recovered_realm),
    }


def main() -> None:
    for required in (ROOT_ARCHIVE, LOCALE_ARCHIVE):
        if not required.is_file():
            raise FileNotFoundError(required)

    storm = Storm(DLL_DEFAULT)
    root_updates = archive_updates(storm, ROOT_ARCHIVE, include_assets=True)
    locale_updates = archive_updates(storm, LOCALE_ARCHIVE, include_assets=False)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = DATA / "_login-persistence-backups" / stamp
    backup_dir.mkdir(parents=True, exist_ok=False)

    originals = {}
    for source in (ROOT_ARCHIVE, LOCALE_ARCHIVE):
        destination = backup_dir / source.name
        shutil.copy2(source, destination)
        if sha256(source) != sha256(destination):
            raise RuntimeError(f"backup hash mismatch: {source}")
        originals[source] = destination

    config_backup = None
    if CONFIG.is_file():
        config_backup = backup_dir / "Config.wtf"
        shutil.copy2(CONFIG, config_backup)
        if sha256(CONFIG) != sha256(config_backup):
            raise RuntimeError("Config.wtf backup hash mismatch")

    changed: list[Path] = []
    try:
        patch_archive(storm, ROOT_ARCHIVE, root_updates)
        changed.append(ROOT_ARCHIVE)
        patch_archive(storm, LOCALE_ARCHIVE, locale_updates)
        changed.append(LOCALE_ARCHIVE)
        config_result = repair_config(CONFIG)
    except BaseException:
        for archive in changed:
            shutil.copy2(originals[archive], archive)
        if config_backup and config_backup.is_file():
            shutil.copy2(config_backup, CONFIG)
        raise

    # Final live readback of every deployed source in BOTH archives.
    for archive, updates in ((ROOT_ARCHIVE, root_updates), (LOCALE_ARCHIVE, locale_updates)):
        for entry, expected in updates.items():
            if read_entry(storm, archive, entry) != expected:
                raise RuntimeError(f"live readback mismatch: {archive.name}: {entry}")

    print(f"backup_dir={backup_dir}")
    print(f"root_entries={len(root_updates)} locale_entries={len(locale_updates)}")
    print(f"config_present={config_result['config_present']}")
    print(f"login_recovered={config_result['login_recovered']}")
    print(f"realm_recovered={config_result['realm_recovered']}")
    # Deliberately never print the recovered account/password payload.


if __name__ == "__main__":
    main()
