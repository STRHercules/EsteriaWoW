"""Patch the winning GlueXML character-creation files with the Freeborn third-team pick.

Adds a Freeborn CheckButton between the gender buttons and the Lua that keeps its selection
state and hands the worldserver a Freeborn.create token on CMSG_CHAR_CREATE.

The token is exactly one trailing space on the create name. The glue client holds
character-create state in C and Lua can only pass the name to CreateCharacter(), so the name
is the only field a GlueXML-only patch can reach. A space is never legal in a player name, so
the token cannot collide with a real name; the worldserver strips it before validating or
storing the name. See src/server/game/Handlers/CharacterHandler.cpp.

Both patch-Z.MPQ and patch-enUS-Z.MPQ carry these files, and the locale archive loads last,
so both are patched. Nothing here touches Wow.exe, DBCs, art assets, or packet layouts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

CLIENT_ROOT = Path(r"G:\3.3.5a - Dev")
ARCHIVE_NAME = "patch-Z.MPQ"
LOCALE_ARCHIVE_NAME = "patch-enUS-Z.MPQ"
GLUE_ROOT = "Interface\\GlueXML\\"
GLUE_FILES = (GLUE_ROOT + "CharacterCreate.xml", GLUE_ROOT + "CharacterCreate.lua")
PAYLOAD_ROOT = Path(__file__).resolve().parent / "freeborn_client"
BACKUP_DIR_NAME = "_freeborn-backups"

FREEBORN_BUTTON_NAME = "CharacterCreateFreebornButton"
# The Lua payload is written as one managed block. Every injected revision is appended after the
# stock code, so the earliest revision marker also marks where the stock file ends.
LUA_BEGIN = "-- >>> freeborn-third-team (managed block, do not edit) >>>"
LUA_END = "-- <<< freeborn-third-team (managed block) <<<"
LUA_MARKER = LUA_BEGIN
# The first shipped revision predates the sentinels, so its header line has to be a marker too.
# Without it, re-running the packer appended a SECOND copy instead of replacing it: the stale copy
# indexed the not-yet-created CharacterCreate frame at load time, which aborted the whole chunk and
# prevented the good copy from defining anything.
LUA_HEADER_MARKER = "-- Freeborn third player team: character-creation selection."
LUA_REVISION_MARKERS = (LUA_HEADER_MARKER, LUA_BEGIN)

# The gender-button container closes right before the class container. The trailing
# "de clase" comment makes this anchor unique in the file.
XML_ANCHOR = (
    "                                </CheckButton>\n"
    "                            </Frames>\n"
    "                        </Frame>\n"
    "                        <!-- Frame contenedor para botones de clase -->"
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _injected_start(text: str) -> int | None:
    """Offset of the earliest injected Freeborn revision, or None for a stock file.

    A revision opens with a `-- =====` banner above its header line, so the walk goes back over
    any banner and blank lines. Leaving the banner behind would be harmless at runtime but it
    would mean a repack no longer reproduces a byte-clean stock prefix, which is how this is
    verified. The walk stops at the first line that is neither blank nor a banner, which is the
    last line of the stock file.
    """
    starts = [index for marker in LUA_REVISION_MARKERS if (index := text.find(marker)) != -1]
    if not starts:
        return None

    line_start = text.rfind("\n", 0, min(starts)) + 1
    while line_start > 0:
        previous_start = text.rfind("\n", 0, line_start - 1) + 1
        previous = text[previous_start : line_start - 1].strip()
        if previous and not (previous.startswith("--") and set(previous) <= set("-= ")):
            break
        line_start = previous_start
    return line_start


def patch_character_create_xml(data: bytes) -> bytes:
    """Write exactly one canonical Freeborn button, replacing any earlier revision."""
    text = data.decode("utf-8")
    button = _read_text(PAYLOAD_ROOT / "CharacterCreate.freeborn.xml").strip("\n")

    start = text.find(f'<CheckButton name="{FREEBORN_BUTTON_NAME}"')
    if start != -1:
        end = text.find("</CheckButton>", start)
        if end == -1:
            raise ValueError("the installed Freeborn button is not terminated")
        end += len("</CheckButton>")
        # Replace whole lines: the payload carries its own indentation, and the existing block
        # already has the surrounding indentation before it.
        line_start = text.rfind("\n", 0, start) + 1
        if text[line_start:end] == button:
            return data
        return (text[:line_start] + button + text[end:]).encode("utf-8")

    if XML_ANCHOR not in text:
        raise ValueError("CharacterCreate.xml is missing the gender-button container anchor")

    replacement = (
        "                                </CheckButton>\n"
        + button
        + "\n"
        + "                            </Frames>\n"
        + "                        </Frame>\n"
        + "                        <!-- Frame contenedor para botones de clase -->"
    )
    return text.replace(XML_ANCHOR, replacement, 1).encode("utf-8")


def patch_character_create_lua(data: bytes) -> bytes:
    """Write exactly one canonical Freeborn block, replacing every earlier revision.

    The stock definitions it wraps are never rewritten. Any previously injected revision is
    removed wholesale rather than patched in place, so a file carrying a stale copy -- or several
    -- converges on the single current block.
    """
    text = data.decode("utf-8")
    body = _read_text(PAYLOAD_ROOT / "CharacterCreate.freeborn.lua").strip("\n")
    block = f"{LUA_BEGIN}\n{body}\n{LUA_END}\n"

    start = _injected_start(text)
    if start is None:
        prefix = text if text.endswith("\n") else text + "\n"
        return (prefix + "\n" + block).encode("utf-8")

    prefix = text[:start].rstrip("\n") + "\n\n"
    if LUA_BEGIN in prefix or LUA_HEADER_MARKER in prefix:
        raise ValueError("a stale Freeborn revision survived canonicalisation")

    result = prefix + block
    return data if result == text else result.encode("utf-8")


TRANSFORMS = {
    GLUE_ROOT + "CharacterCreate.xml": patch_character_create_xml,
    GLUE_ROOT + "CharacterCreate.lua": patch_character_create_lua,
}

ADDON_ROOT = "Interface\\AddOns\\FreebornClaim\\"
ADDON_FILES = ("FreebornClaim.toc", "FreebornClaim.lua")
ADDON_SOURCE = PAYLOAD_ROOT / "addon" / "FreebornClaim"

# The Freeborn button plate. TEXTURE_REFERENCE is what the button's OnLoad passes to SetTexture,
# which omits the extension; TEXTURE_KEY is the archive entry. They are derived from one name so
# they cannot drift apart.
TEXTURE_ROOT = "Interface\\Glues\\CharacterCreate\\"
TEXTURE_FILE = "UI-CharacterCreate-Freeborn.blp"
TEXTURE_REFERENCE = TEXTURE_ROOT + "UI-CharacterCreate-Freeborn"
TEXTURE_KEY = TEXTURE_ROOT + TEXTURE_FILE
TEXTURE_SOURCE = PAYLOAD_ROOT / "textures" / TEXTURE_FILE

# The same plate again, beside a Freeborn character's name on the character-select screen. Same
# bytes, different archive entry, so the two cannot drift apart.
BADGE_ROOT = "Interface\\Glues\\CharacterSelect\\"
BADGE_FILE = "FreebornLogo.blp"
BADGE_REFERENCE = BADGE_ROOT + "FreebornLogo"
BADGE_KEY = BADGE_ROOT + BADGE_FILE


def _glue_updates(storm: Storm, archive: Path) -> dict[str, bytes]:
    """Return the patched GlueXML entries for `archive`, omitting no-op ones."""
    handle = storm.open_archive(archive)
    try:
        updates = {}
        for entry, transform in TRANSFORMS.items():
            try:
                original = storm.read(handle, entry)
            except OSError as error:
                raise ValueError(f"{archive.name} is missing required entry {entry}") from error
            patched = transform(original)
            if patched != original:
                updates[entry] = patched
        return updates
    finally:
        storm.dll.SFileCloseArchive(handle)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _exe_interface_patched(client_root: Path) -> bool:
    """GlueXML overrides only load when the client accepts custom interface files."""
    manifest = client_root / "ClasslessWildcard-install.json"
    try:
        return bool(json.loads(manifest.read_text(encoding="utf-8")).get("exe_patched"))
    except (OSError, ValueError):
        return (client_root / "Wow.exe.classless-bak").is_file()


def _client_asset_updates() -> dict[str, bytes]:
    """The Freeborn button plate and the claim addon.

    Shipped only in the root archive: nothing under Interface\\AddOns or at this texture path
    exists in the locale archives, so there is nothing to shadow.
    """
    updates = {ADDON_ROOT + name: (ADDON_SOURCE / name).read_bytes() for name in ADDON_FILES}
    updates[TEXTURE_KEY] = TEXTURE_SOURCE.read_bytes()
    updates[BADGE_KEY] = TEXTURE_SOURCE.read_bytes()
    return updates


def _write_patched_archive(storm: Storm, archive: Path, updates: dict[str, bytes]) -> None:
    """Write `updates` into `archive` atomically, after verifying the staged result."""
    handle = archive.parent / f".{archive.name}.freeborn-tmp"
    shutil.copy2(archive, handle)
    try:
        storm.replace_archive_entries(handle, updates)
        verify = storm.open_archive(handle)
        try:
            for entry, expected in updates.items():
                if storm.read(verify, entry) != expected:
                    raise ValueError(f"staged {archive.name} failed to round-trip {entry}")
        finally:
            storm.dll.SFileCloseArchive(verify)
        os.replace(handle, archive)
    except BaseException:
        handle.unlink(missing_ok=True)
        raise


@dataclass
class PackReport:
    root_archive: str
    locale_archive: str
    root_updates: tuple[str, ...] = ()
    locale_updates: tuple[str, ...] = ()
    backup_dir: str = ""
    backup_sha256: dict[str, str] = field(default_factory=dict)
    exe_interface_patched: bool = False
    changed: bool = True


def contract() -> dict:
    """The client/server contract this patch depends on."""
    return {
        "create_signal": "none; the create name is sent exactly as typed",
        "claim": {
            "cvar": "freebornPending",
            "addon_prefix": "FREEBORN",
            "addon_body": "claim",
            "channel": "addon message, WHISPER to self",
        },
        "button": FREEBORN_BUTTON_NAME,
        "glue_files": list(GLUE_FILES),
        "addon_files": [ADDON_ROOT + name for name in ADDON_FILES],
        "archives": [ARCHIVE_NAME, LOCALE_ARCHIVE_NAME],
        "server_side_effect": "characters.teamId = TEAM_FREEBORN (3)",
    }


def build_freeborn_team_pack(
    root_archive: Path,
    locale_archive: Path,
    output_root: Path,
    stormlib: Path = DLL_DEFAULT,
) -> PackReport:
    """Stage patched copies of both archives into a fresh `output_root`."""
    root_archive = Path(root_archive).resolve()
    locale_archive = Path(locale_archive).resolve()
    output_root = Path(output_root).resolve()
    if root_archive == locale_archive:
        raise ValueError("root and locale archives must be different")
    if output_root.exists():
        raise ValueError(f"output_root must be fresh: {output_root}")
    if not root_archive.is_file() or not locale_archive.is_file():
        raise FileNotFoundError("both source archives are required")

    storm = Storm(stormlib)
    root_updates = _glue_updates(storm, root_archive)
    root_updates.update(_client_asset_updates())
    locale_updates = _glue_updates(storm, locale_archive)

    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.tmp-", dir=output_root.parent))
    try:
        for source, name, updates in (
            (root_archive, ARCHIVE_NAME, root_updates),
            (locale_archive, LOCALE_ARCHIVE_NAME, locale_updates),
        ):
            destination = staging / name
            shutil.copy2(source, destination)
            if updates:
                storm.replace_archive_entries(destination, updates)
        os.replace(staging, output_root)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return PackReport(
        root_archive=str(root_archive),
        locale_archive=str(locale_archive),
        root_updates=tuple(sorted(root_updates)),
        locale_updates=tuple(sorted(locale_updates)),
        changed=bool(root_updates or locale_updates),
    )


def install_freeborn_team_pack(
    root_archive: Path,
    locale_archive: Path,
    stormlib: Path = DLL_DEFAULT,
    backup_base: Path | None = None,
) -> PackReport:
    """Back both archives up, then patch them in place."""
    root_archive = Path(root_archive).resolve()
    locale_archive = Path(locale_archive).resolve()
    if not root_archive.is_file() or not locale_archive.is_file():
        raise FileNotFoundError("both source archives are required")

    storm = Storm(stormlib)
    root_updates = _glue_updates(storm, root_archive)
    root_updates.update(_client_asset_updates())
    locale_updates = _glue_updates(storm, locale_archive)

    report = PackReport(
        root_archive=str(root_archive),
        locale_archive=str(locale_archive),
        root_updates=tuple(sorted(root_updates)),
        locale_updates=tuple(sorted(locale_updates)),
        exe_interface_patched=_exe_interface_patched(root_archive.parent.parent),
        changed=bool(root_updates or locale_updates),
    )
    if not report.changed:
        return report

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = (backup_base or (root_archive.parent / BACKUP_DIR_NAME)) / stamp
    backup_dir.mkdir(parents=True, exist_ok=False)

    for archive in (root_archive, locale_archive):
        copy = backup_dir / archive.name
        shutil.copy2(archive, copy)
        report.backup_sha256[archive.name] = _sha256(copy)
    report.backup_dir = str(backup_dir)

    for archive, updates in ((root_archive, root_updates), (locale_archive, locale_updates)):
        if updates:
            _write_patched_archive(storm, archive, updates)

    return report


def _report_json(report: PackReport) -> str:
    return json.dumps(
        {
            "root_archive": report.root_archive,
            "locale_archive": report.locale_archive,
            "root_updates": list(report.root_updates),
            "locale_updates": list(report.locale_updates),
            "backup_dir": report.backup_dir,
            "backup_sha256": report.backup_sha256,
            "exe_interface_patched": report.exe_interface_patched,
            "changed": report.changed,
        },
        indent=2,
        sort_keys=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-root", type=Path, default=CLIENT_ROOT)
    parser.add_argument("--root-archive", type=Path)
    parser.add_argument("--locale-archive", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--print-contract", action="store_true")
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    args = parser.parse_args()

    if args.print_contract:
        print(json.dumps(contract(), sort_keys=True))
        return 0

    root_archive = args.root_archive or args.client_root / "Data" / ARCHIVE_NAME
    locale_archive = args.locale_archive or args.client_root / "Data" / "enUS" / LOCALE_ARCHIVE_NAME

    if args.install:
        report = install_freeborn_team_pack(root_archive, locale_archive, args.stormlib)
    elif args.output_root is not None:
        report = build_freeborn_team_pack(root_archive, locale_archive, args.output_root, args.stormlib)
    else:
        parser.error("either --install or --output-root is required")

    print(_report_json(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
