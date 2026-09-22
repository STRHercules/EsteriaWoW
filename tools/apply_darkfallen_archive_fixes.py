"""Apply the Darkfallen archive content to the live client Z archives.

This is the in-place deployment path for an already-staged Z pair: it patches only the
entries whose content changed and leaves everything else (the multi-hundred-MB HD and
asset payloads) untouched. Every entry comes from the transforms in
``tools/darkfallen_race_pack.py``, so the result matches a fresh packer run.

Entries covered per archive:

* ``CharacterInfo.lua`` - race metadata and the racial spell list (the list changed when
  Endurance was replaced by Crimson Thirst).
* ``GlueParent.lua`` / ``CharacterCreate.lua`` / ``CharacterSelect.lua`` - backdrop, fog,
  lighting, portraits and faction detection (repairs the earlier Void Elf
  ``Races_Informations[19]`` alias and the missing TemporaryPortrait pair).
* ``ChrRaces.dbc`` - the two race rows, including the per-faction client file strings.
* ``Spell.dbc`` - the Darkfallen racial spells (Crimson Thirst, Children of the Night)
  and the Cannibalize -> Vampiric Sustenance rename.
* ``GlueStrings.lua`` (locale archive only) - localized race and ability text.

Archives are SHA-256 backed up before they are touched, and read back afterwards.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm, Wdbc
from playable_race_pack import RawWdbc

from darkfallen_race_pack import (
    DARKFALLEN_FILE_STRINGS,
    SPELL_CHILDREN_GHOST_SPEED,
    SPELL_CHILDREN_OF_THE_NIGHT,
    SPELL_CHILDREN_STEALTH_SPEED,
    SPELL_CRIMSON_THIRST,
    SPELL_CRIMSON_THIRST_HEAL,
    SPELL_NAME,
    SPELL_VAMPIRIC_SUSTENANCE,
    merge_spell_table,
    patch_character_create,
    patch_character_info,
    patch_character_select,
    patch_glue_parent,
    patch_glue_strings,
)


GLUE_ENTRY = "Interface\\GlueXML\\CharacterInfo.lua"
GLUE_PARENT_ENTRY = "Interface\\GlueXML\\GlueParent.lua"
CHAR_CREATE_ENTRY = "Interface\\GlueXML\\CharacterCreate.lua"
CHAR_SELECT_ENTRY = "Interface\\GlueXML\\CharacterSelect.lua"
GLUE_STRINGS_ENTRY = "Interface\\GlueXML\\GlueStrings.lua"
CHRRACES_ENTRY = "DBFilesClient\\ChrRaces.dbc"
SPELL_ENTRY = "DBFilesClient\\Spell.dbc"


def patch_chrraces_file_strings(data: bytes) -> bytes:
    """Give the Horde Darkfallen race its own ClientFileString (backdrop and portrait key)."""
    races = RawWdbc(data)

    def value(record: bytes, index: int) -> int:
        return int.from_bytes(record[index * 4 : index * 4 + 4], "little")

    def string(record: bytes, index: int) -> str:
        offset = value(record, index)
        return races.strings[offset:].split(b"\0", 1)[0].decode("ascii", "replace") if offset else ""

    records = list(races.records)
    pool = bytearray(races.strings)
    changed = False
    for index, record in enumerate(records):
        expected = DARKFALLEN_FILE_STRINGS.get(int.from_bytes(record[:4], "little"))
        if expected is None or string(record, 11) == expected:
            continue
        offset = len(pool)
        pool.extend(expected.encode("ascii") + b"\0")
        row = bytearray(record)
        row[11 * 4 : 11 * 4 + 4] = offset.to_bytes(4, "little")
        records[index] = bytes(row)
        changed = True
    return races.build(records, bytes(pool)) if changed else data


# (entry, transform, may be absent from this archive)
PATCHES = (
    (GLUE_ENTRY, patch_character_info, False),
    (GLUE_PARENT_ENTRY, patch_glue_parent, False),
    (CHAR_CREATE_ENTRY, patch_character_create, False),
    (CHAR_SELECT_ENTRY, patch_character_select, False),
    (CHRRACES_ENTRY, patch_chrraces_file_strings, False),
    (SPELL_ENTRY, merge_spell_table, False),
    (GLUE_STRINGS_ENTRY, patch_glue_strings, True),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(storm: Storm, archive: Path, updates: dict[str, bytes]) -> None:
    handle = storm.open_archive(archive)
    try:
        check = {name: storm.read(handle, name) for name in updates}
    finally:
        storm.dll.SFileCloseArchive(handle)

    for name, payload in updates.items():
        assert check[name] == payload, f"{archive.name}: readback mismatch for {name}"

    if GLUE_ENTRY in check:
        text = check[GLUE_ENTRY].decode("utf-8")
        assert "Races_Informations[19] = Races_Informations[18]" not in text
        assert 'Races_Informations[19] = { Name = "Void Elf"' in text
        assert '    [19] = {token = "DARKFALLEN"' not in text
        assert '    [18] = {token = "DARKFALLEN"' in text
        assert 'spells = {"Shadow Resistance", "Cannibalize"}' not in text
        assert "Crimson Thirst" in text
        assert '_G.RACE_19 = "Darkfallen"' in text
    if GLUE_PARENT_ENTRY in check:
        parent = check[GLUE_PARENT_ENTRY].decode("utf-8")
        assert '["DARKFALLEN"] = true,' in parent
        assert '["DARKFALLENHORDE"] = true,' in parent
        assert 'RaceLights["DARKFALLEN"]' in parent
        assert 'RaceLights["DARKFALLENHORDE"]' in parent
    if CHAR_CREATE_ENTRY in check:
        create = check[CHAR_CREATE_ENTRY].decode("utf-8")
        assert '"DARKFALLENHORDE_MALE"' in create
        assert '        ["DARKFALLENHORDE"] = "ORC",' in create
    if CHAR_SELECT_ENTRY in check:
        select = check[CHAR_SELECT_ENTRY].decode("utf-8")
        assert 'raceModel = strupper(GetSelectBackgroundModel(actualIndex) or "")' in select
    if GLUE_STRINGS_ENTRY in check:
        strings = check[GLUE_STRINGS_ENTRY].decode("utf-8")
        assert "ABILITY_INFO_DARKFALLEN4" in strings
        assert strings.count("RACE_INFO_DARKFALLEN =") == 1
    if CHRRACES_ENTRY in check:
        races = RawWdbc(check[CHRRACES_ENTRY])
        rows = {int.from_bytes(row[:4], "little"): row for row in races.records}
        for race, expected in DARKFALLEN_FILE_STRINGS.items():
            offset = int.from_bytes(rows[race][11 * 4 : 11 * 4 + 4], "little")
            actual = races.strings[offset:].split(b"\0", 1)[0].decode("ascii", "replace")
            assert actual == expected, f"race {race} client-file string is {actual!r}"
    if SPELL_ENTRY in check:
        table = Wdbc(check[SPELL_ENTRY])
        rows = {row[0]: row for row in table.rows}
        for spell_id in (
            SPELL_CRIMSON_THIRST,
            SPELL_CRIMSON_THIRST_HEAL,
            SPELL_CHILDREN_OF_THE_NIGHT,
            SPELL_CHILDREN_STEALTH_SPEED,
            SPELL_CHILDREN_GHOST_SPEED,
        ):
            assert spell_id in rows, f"spell {spell_id} is missing from the archive Spell.dbc"
        assert table.text(rows[SPELL_VAMPIRIC_SUSTENANCE][SPELL_NAME]) == "Vampiric Sustenance"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root-archive", required=True, type=Path)
    parser.add_argument("--locale-archive", required=True, type=Path)
    parser.add_argument("--backup-dir", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    storm = Storm(DLL_DEFAULT)
    for archive in (args.root_archive, args.locale_archive):
        handle = storm.open_archive(archive)
        try:
            # Only read the entries this tool patches: the archives carry hundreds of MB
            # of assets that are none of its business.
            listed = {name.casefold(): name for name, *_ in storm.list_files(handle)}
            updates: dict[str, bytes] = {}
            absent: list[str] = []
            for entry, transform, optional in PATCHES:
                name = listed.get(entry.casefold())
                if name is None:
                    if not optional:
                        raise FileNotFoundError(f"{archive.name}: entry missing: {entry}")
                    absent.append(entry)
                    continue
                payload = storm.read(handle, name)
                patched = transform(payload)
                if patched != payload:
                    updates[name] = patched
        finally:
            storm.dll.SFileCloseArchive(handle)

        print(f"{archive.name}: {len(updates)} of {len(PATCHES)} entries need updating")
        for entry, _, _ in PATCHES:
            if entry in absent:
                state = "skip (absent)"
            elif entry in updates:
                state = "UPDATE"
            else:
                state = "ok"
            print(f"   {state:13} {entry}")

        if not args.apply or not updates:
            continue

        args.backup_dir.mkdir(parents=True, exist_ok=True)
        backup = args.backup_dir / archive.name
        if not backup.exists():
            shutil.copy2(archive, backup)
            print(f"  backed up -> {backup}")
        assert sha256(backup) == sha256(archive), f"{archive.name}: backup does not match the live archive"

        storm.replace_archive_entries(archive, updates)
        verify(storm, archive, updates)
        print(f"  verified {archive.name}: sha256={sha256(archive)[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
