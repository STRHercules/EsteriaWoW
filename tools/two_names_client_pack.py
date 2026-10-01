"""Install Esteria's first + last name character-create UI into the winning GlueXML archives.

The live Esteria interface is assembled into patch-Z.MPQ and patch-enUS-Z.MPQ.  This tool patches
those winning files surgically so it does not replace unrelated race, Freeborn, or retail-style UI
work.  It creates timestamped backups and verifies every staged archive before replacing it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from cars_mount_pack import DLL_DEFAULT, Storm
from freeborn_team_pack import patch_character_create_lua as patch_freeborn_character_create_lua

CLIENT_ROOT = Path(r"G:\3.3.5a - Dev")
ROOT_ARCHIVE = Path("Data") / "patch-Z.MPQ"
LOCALE_ARCHIVE = Path("Data") / "enUS" / "patch-enUS-Z.MPQ"
XML_ENTRY = r"Interface\GlueXML\CharacterCreate.xml"
LUA_ENTRY = r"Interface\GlueXML\CharacterCreate.lua"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _replace_once(text: str, old: str, new: str, description: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{description}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def hide_name_fields(data: bytes) -> bytes:
    text = data.decode("utf-8")

    def hidden(match):
        tag = match.group(0)
        if re.search(r'\bhidden="[^"]*"', tag):
            return re.sub(r'\bhidden="[^"]*"', 'hidden="true"', tag)
        return tag[:-1] + ' hidden="true">'

    return re.sub(r'<EditBox\b[^>]*name="CharacterCreate(?:Last)?NameEdit"[^>]*>', hidden, text).encode("utf-8")


def sync_name_visibility(data: bytes) -> bytes:
    lines = data.decode("utf-8").splitlines(keepends=True)
    output = []
    for index, line in enumerate(lines):
        output.append(line)
        match = re.fullmatch(r"([ \t]*)CharacterCreateNameEdit:(Show|Hide)\(\);?[ \t]*(?:\r?\n)?", line)
        if not match:
            continue
        indent, action = match.groups()
        following = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if not re.fullmatch(rf"CharacterCreateLastNameEdit:{action}\(\);?", following):
            output.append(f"{indent}CharacterCreateLastNameEdit:{action}();\n")
    return "".join(output).encode("utf-8")


def patch_character_create_xml(data: bytes) -> bytes:
    text = data.decode("utf-8")
    if 'name="CharacterCreateLastNameEdit"' in text:
        return hide_name_fields(data)

    start = text.find('<EditBox name="CharacterCreateNameEdit"')
    if start == -1:
        raise ValueError("CharacterCreate.xml is missing CharacterCreateNameEdit")
    line_start = text.rfind("\n", 0, start) + 1
    end = text.find("</EditBox>", start)
    if end == -1:
        raise ValueError("CharacterCreateNameEdit is not terminated")
    end += len("</EditBox>")

    block = text[line_start:end]
    first = block
    first = _replace_once(first, '<Size x="156" y="40"/>', '<Size x="210" y="40"/>', "first-name width")
    first = _replace_once(first, '<Anchor point="BOTTOM" x="0" y="55"/>', '<Anchor point="BOTTOM" x="-110" y="55"/>', "first-name position")
    first = _replace_once(first, 'text="NAME"', 'text="First Name"', "first-name label")
    first = first.replace('<Size x="256" y="64"/>', '<Size x="210" y="64"/>', 1)

    last = first.replace('name="CharacterCreateNameEdit"', 'name="CharacterCreateLastNameEdit"', 1)
    last = _replace_once(last, '<Anchor point="BOTTOM" x="-110" y="55"/>', '<Anchor point="BOTTOM" x="110" y="55"/>', "last-name position")
    last = _replace_once(last, 'text="First Name"', 'text="Last Name"', "last-name label")

    text = text[:line_start] + first + "\n" + last + text[end:]
    text = text.replace(
        "CharacterCreateNameEdit:SetText(GetRandomName());",
        "CharacterCreate_RandomizeName();",
        1,
    )
    return hide_name_fields(text.encode("utf-8"))


def patch_character_create_lua(data: bytes) -> bytes:
    text = data.decode("utf-8")
    has_freeborn_block = "freeborn-third-team" in text or "Freeborn third player team: character-creation selection." in text
    if "function CharacterCreate_GetFullName()" in text:
        patched = patch_freeborn_character_create_lua(data) if has_freeborn_block else data
        return sync_name_visibility(patched)

    text = _replace_once(
        text,
        '    "CharacterCreateNameEdit",\n};',
        '    "CharacterCreateNameEdit",\n    "CharacterCreateLastNameEdit",\n};',
        "backdrop frame list",
    )

    color_anchor = (
        "    CharacterCreateNameEdit:SetBackdropBorderColor(backdropColor[1], backdropColor[2], backdropColor[3])\n"
        "    CharacterCreateNameEdit:SetBackdropColor(backdropColor[4], backdropColor[5], backdropColor[6])"
    )
    color_replacement = color_anchor + (
        "\n    CharacterCreateLastNameEdit:SetBackdropBorderColor(backdropColor[1], backdropColor[2], backdropColor[3])"
        "\n    CharacterCreateLastNameEdit:SetBackdropColor(backdropColor[4], backdropColor[5], backdropColor[6])"
    )
    text = _replace_once(text, color_anchor, color_replacement, "name-field backdrop setup")

    helper_block = '''function CharacterCreate_SetNameFields(fullName)
    local firstName = "";
    local lastName = "";
    if ( fullName and fullName ~= "" ) then
        local splitFirst, splitLast = string.match(fullName, "^([^ ]+)%s*(.*)$");
        firstName = splitFirst or fullName;
        lastName = splitLast or "";
    end
    CharacterCreateNameEdit:SetText(firstName);
    CharacterCreateLastNameEdit:SetText(lastName);
end

function CharacterCreate_GetFullName()
    local firstName = CharacterCreateNameEdit:GetText() or "";
    local lastName = CharacterCreateLastNameEdit:GetText() or "";
    if ( firstName == "" ) then
        return lastName;
    elseif ( lastName == "" ) then
        return firstName;
    end
    return firstName.." "..lastName;
end

function CharacterCreate_RandomizeName()
    CharacterCreate_SetNameFields(GetRandomName());
end

'''
    text = _replace_once(
        text,
        "function CharacterCreate_OnShow()",
        helper_block + "function CharacterCreate_OnShow()",
        "CharacterCreate_OnShow helper insertion",
    )

    text = _replace_once(
        text,
        "        CharacterCreateNameEdit:SetText( PaidChange_GetName() );",
        "        CharacterCreate_SetNameFields(PaidChange_GetName());",
        "paid service name",
    )
    text = _replace_once(
        text,
        '        CharacterCreateNameEdit:SetText("");',
        '        CharacterCreate_SetNameFields("");',
        "new character name clear",
    )
    text = _replace_once(
        text,
        "        CreateCharacter(CharacterCreateNameEdit:GetText());",
        "        CreateCharacter(CharacterCreate_GetFullName());",
        "character creation name submission",
    )
    patched = text.encode("utf-8")
    patched = patch_freeborn_character_create_lua(patched) if has_freeborn_block else patched
    return sync_name_visibility(patched)


def _read_updates(storm: Storm, archive: Path) -> dict[str, bytes]:
    handle = storm.open_archive(archive)
    try:
        updates: dict[str, bytes] = {}
        for entry, transform in ((XML_ENTRY, patch_character_create_xml), (LUA_ENTRY, patch_character_create_lua)):
            original = storm.read(handle, entry)
            patched = transform(original)
            if patched != original:
                updates[entry] = patched
        return updates
    finally:
        storm.dll.SFileCloseArchive(handle)


def _write_patched_archive(storm: Storm, archive: Path, updates: dict[str, bytes]) -> None:
    staged = archive.parent / f".{archive.name}.two-names-tmp"
    shutil.copy2(archive, staged)
    try:
        storm.replace_archive_entries(staged, updates)
        verify = storm.open_archive(staged)
        try:
            for entry, expected in updates.items():
                actual = storm.read(verify, entry)
                if actual != expected:
                    raise RuntimeError(f"staged archive failed verification: {archive.name} / {entry}")
        finally:
            storm.dll.SFileCloseArchive(verify)
        try:
            os.replace(staged, archive)
        except PermissionError:
            # Some large Esteria MPQs can be opened for mutation but Windows refuses an atomic
            # rename over the existing archive. We already have a verified backup at this point,
            # so fall back to StormLib's in-place replacement and verify the live entries again.
            staged.unlink(missing_ok=True)
            storm.replace_archive_entries(archive, updates)
            live = storm.open_archive(archive)
            try:
                for entry, expected in updates.items():
                    if storm.read(live, entry) != expected:
                        raise RuntimeError(f"live archive failed verification: {archive.name} / {entry}")
            finally:
                storm.dll.SFileCloseArchive(live)
    except BaseException:
        staged.unlink(missing_ok=True)
        raise


def install(client_root: Path, stormlib: Path = DLL_DEFAULT) -> dict:
    client_root = client_root.resolve()
    archives = (client_root / ROOT_ARCHIVE, client_root / LOCALE_ARCHIVE)
    for archive in archives:
        if not archive.is_file():
            raise FileNotFoundError(archive)

    storm = Storm(stormlib)
    updates = {archive: _read_updates(storm, archive) for archive in archives}
    if not any(updates.values()):
        return {"changed": False, "archives": [str(path) for path in archives]}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # This client mounts nested MPQs under Data, including backup copies.
    backup = client_root.parent / "3.3.5a - Backups" / f"two-names-{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    backup_hashes: dict[str, str] = {}
    for archive in archives:
        target = backup / archive.name
        shutil.copy2(archive, target)
        backup_hashes[archive.name] = _sha256(target)

    for archive in archives:
        if updates[archive]:
            _write_patched_archive(storm, archive, updates[archive])

    return {
        "changed": True,
        "backup": str(backup),
        "backup_sha256": backup_hashes,
        "updates": {path.name: sorted(entries) for path, entries in updates.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-root", type=Path, default=CLIENT_ROOT)
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    if not args.install:
        parser.error("--install is required")
    print(json.dumps(install(args.client_root, args.stormlib), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
