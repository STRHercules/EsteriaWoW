"""Stage Eunoia's working Vulpera package into the dev client's Patch-C.

Source: G:\\Eunoia\\Client\\data\\Patch-5.mpq (opened read-only, since that
client may be running) plus its CharSections.dbc.

Writes into R:\\...\\3.3.5a - Dev\\Data\\Patch-C.MPQ:
  * HD models and their four skin LODs, per gender
  * every Vulpera texture their CharSections references, plus the two hardcoded
    eye textures baked into their models
  * CharSections.dbc race-20 rows repointed at the tail / naked-torso layers
  * CharHairGeosets.dbc and CharHairTextures.dbc race-20 rows replaced with
    their race-9 rows, so hair follows the HD model's geoset numbering

Patch-C is backed up before anything is written.
"""

from __future__ import annotations

import ctypes as c
import shutil
import struct
import sys
import time
from pathlib import Path

REPO = Path(r"R:\Users\Zach\Documents\GitHub\EsteriaWoW")
sys.path.insert(0, str(REPO / "tools"))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc  # noqa: E402

PLAN = REPO / ".agents/plans/vulpera-pandaren-playable-races"
PATCH_C = REPO / "3.3.5a - Dev/Data/Patch-C.MPQ"
EUNOIA_PATCH5 = Path(r"G:\Eunoia\Client\data\Patch-5.mpq")
EUNOIA_DBC = PLAN / "eunoia-dbc"
RACE_OURS = 20
RACE_THEIRS = 9
MPQ_OPEN_READ_ONLY = 0x00000100
MPQ_FILE_REPLACEEXISTING = 0x80000000
MPQ_COMPRESSION_ZLIB = 0x00000002
CHARSECTIONS = "DBFilesClient\\CharSections.dbc"
HAIRGEOSETS = "DBFilesClient\\CharHairGeosets.dbc"
HAIRTEXTURES = "DBFilesClient\\CharHairTextures.dbc"


def open_archive(storm: Storm, path: Path, flags: int = MPQ_OPEN_READ_ONLY):
    handle = H()
    if not storm.dll.SFileOpenArchive(str(path), 0, flags, c.byref(handle)):
        raise OSError(f"SFileOpenArchive failed: {path} ({c.get_last_error()})")
    return handle


def try_read(storm: Storm, archive, name: str) -> bytes | None:
    try:
        return storm.read(archive, name)
    except Exception:  # noqa: BLE001
        return None


def write_entries(storm: Storm, path: Path, entries: dict[str, bytes]) -> None:
    archive = open_archive(storm, path, flags=0)
    try:
        storm.ensure_capacity(archive, len(entries))
        for name, payload in entries.items():
            probe = H()
            exists = bool(storm.dll.SFileOpenFileEx(archive, name.encode("ascii"), 0, c.byref(probe)))
            if exists:
                storm.dll.SFileCloseFile(probe)
            handle = H()
            flags = MPQ_FILE_REPLACEEXISTING if exists else 0
            if not storm.dll.SFileCreateFile(
                archive, name.encode("ascii"), 0, len(payload), 0, flags, c.byref(handle)
            ):
                raise OSError(f"SFileCreateFile failed: {name} ({c.get_last_error()})")
            try:
                buffer = c.create_string_buffer(payload or b"\0")
                if not storm.dll.SFileWriteFile(handle, buffer, len(payload), MPQ_COMPRESSION_ZLIB):
                    raise OSError(f"SFileWriteFile failed: {name} ({c.get_last_error()})")
            finally:
                storm.dll.SFileCloseFile(handle)
    finally:
        storm.dll.SFileCloseArchive(archive)


def patch_string_fields(data: bytes, edits: list[tuple[int, int, str]]) -> bytes:
    """Append strings to the DBC string block and repoint the given fields."""
    magic, count, fields, record_size, _string_size = struct.unpack_from("<4s4I", data, 0)
    if magic != b"WDBC":
        raise ValueError("not a WDBC")
    body_end = 20 + count * record_size
    buffer = bytearray(data)
    strings = bytearray(buffer[body_end:])
    for row_index, field_index, value in edits:
        offset = 0
        if value:
            offset = len(strings)
            strings.extend(value.encode("utf-8") + b"\0")
        struct.pack_into("<I", buffer, 20 + row_index * record_size + field_index * 4, offset)
    struct.pack_into("<I", buffer, 16, len(strings))
    return bytes(buffer[:body_end]) + bytes(strings)


def replace_race_rows(data: bytes, race: int, new_rows: list[list[int]]) -> bytes:
    """Drop every row of `race` and append `new_rows` with fresh ids."""
    dbc = Wdbc(data)
    kept = [row.copy() for row in dbc.rows if row[1] != race]
    next_id = max(row[0] for row in kept) + 1
    for row in new_rows:
        row = row.copy()
        row[0] = next_id
        row[1] = race
        kept.append(row)
        next_id += 1
    body = b"".join(struct.pack(f"<{dbc.fields}I", *row) for row in kept)
    return struct.pack("<4s4I", b"WDBC", len(kept), dbc.fields, dbc.record_size, len(dbc.strings)) + body + dbc.strings


def vulpera_texture_names(charsections: bytes) -> list[str]:
    dbc = Wdbc(charsections)
    names: list[str] = []
    for row in dbc.rows:
        if row[1] != RACE_THEIRS:
            continue
        for field in (4, 5, 6):
            text = dbc.text(row[field])
            if text:
                names.append(text)
    return sorted(set(names))


def main() -> None:
    storm = Storm(DLL_DEFAULT)
    existing = sorted((REPO / "3.3.5a - Dev/Backups").glob("patch-c-before-eunoia-vulpera-*"))
    backup = existing[-1] if existing else (
        REPO / "3.3.5a - Dev/Backups" / f"patch-c-before-eunoia-vulpera-{time.strftime('%Y%m%d-%H%M%S')}"
    )
    backup.mkdir(parents=True, exist_ok=True)
    if not (backup / "Patch-C.MPQ").exists():
        shutil.copy2(PATCH_C, backup / "Patch-C.MPQ")
    print(f"backup: {backup / 'Patch-C.MPQ'} ({PATCH_C.stat().st_size:,} bytes)")

    theirs_archive = open_archive(storm, EUNOIA_PATCH5)
    ours_archive = open_archive(storm, PATCH_C)
    try:
        eunoia_sections = (EUNOIA_DBC / "CharSections.dbc").read_bytes()
        eunoia_geosets = (EUNOIA_DBC / "CharHairGeosets.dbc").read_bytes()
        eunoia_hair_tex = (EUNOIA_DBC / "CharHairTextures.dbc").read_bytes()
        ours_sections = try_read(storm, ours_archive, CHARSECTIONS)
        ours_geosets = try_read(storm, ours_archive, HAIRGEOSETS)
        ours_hair_tex = try_read(storm, ours_archive, HAIRTEXTURES)
    finally:
        storm.dll.SFileCloseArchive(theirs_archive)
        storm.dll.SFileCloseArchive(ours_archive)
    if not eunoia_sections or not ours_sections:
        raise SystemExit("CharSections.dbc missing on one side")

    entries: dict[str, bytes] = {}
    missing: list[str] = []

    source = open_archive(storm, EUNOIA_PATCH5)
    try:
        # 1. models and skins
        for gender, stem in (("male", "vulperamale"), ("female", "vulperafemale")):
            wanted = [f"character\\vulpera\\{gender}\\{stem}.m2"]
            wanted += [f"character\\vulpera\\{gender}\\{stem}0{index}.skin" for index in range(4)]
            for name in wanted:
                payload = try_read(storm, source, name)
                if payload is None:
                    missing.append(name)
                else:
                    entries[name] = payload

        # 2. every texture their CharSections references, plus the eye textures baked into their M2s
        texture_names = vulpera_texture_names(eunoia_sections)
        texture_names += [
            "character\\vulpera\\male\\vulperamale_3257674.blp",
            "character\\vulpera\\male\\vulperamale_3285331.blp",
            "character\\vulpera\\female\\vulperafemale_3257673.blp",
            "character\\vulpera\\female\\vulperafemale_3285330.blp",
        ]
        for name in sorted(set(texture_names)):
            payload = try_read(storm, source, name)
            if payload is None and not name.lower().endswith(".blp"):
                alternate = name + ".blp"
                payload = try_read(storm, source, alternate)
                if payload is not None:
                    name = alternate
            if payload is None:
                missing.append(name)
                continue
            entries[name] = payload
    finally:
        storm.dll.SFileCloseArchive(source)

    # 3. CharSections: point the second skin layer at the tail, and give males a bare torso overlay
    our_sections_table = Wdbc(ours_sections)
    edits: list[tuple[int, int, str]] = []
    tail_count = torso_count = 0
    for index, row in enumerate(our_sections_table.rows):
        if row[1] != RACE_OURS:
            continue
        gender = "male" if row[2] == 0 else "female"
        color = row[9] % 8
        if row[3] == 0:
            tail = f"character\\vulpera\\{gender}\\vulpera{gender}skintail00_{color:02d}.blp"
            edits.append((index, 5, tail))
            tail_count += 1
        elif row[3] == 4 and row[2] == 0 and not our_sections_table.text(row[5]):
            torso = f"character\\vulpera\\male\\vulperamalenakedtorsoskin00_{color:02d}.blp"
            edits.append((index, 5, torso))
            torso_count += 1
    entries[CHARSECTIONS] = patch_string_fields(ours_sections, edits)
    print(f"CharSections: {tail_count} tail bindings, {torso_count} male torso bindings")

    # 4. hair geosets/textures follow the HD model's numbering
    for payload, ours_payload, label in (
        (eunoia_geosets, ours_geosets, "CharHairGeosets"),
        (eunoia_hair_tex, ours_hair_tex, "CharHairTextures"),
    ):
        if not payload or not ours_payload:
            continue
        their_rows = [row for row in Wdbc(payload).rows if row[1] == RACE_THEIRS]
        if not their_rows:
            continue
        entries[{"CharHairGeosets": HAIRGEOSETS, "CharHairTextures": HAIRTEXTURES}[label]] = replace_race_rows(
            ours_payload, RACE_OURS, their_rows
        )
        print(f"{label}: replaced race {RACE_OURS} rows with {len(their_rows)} rows from race {RACE_THEIRS}")

    write_entries(storm, PATCH_C, entries)
    manifest = PLAN / "eunoia-vulpera-staged-manifest.txt"
    manifest.write_text(
        "\n".join(f"{name}\t{len(payload)}" for name, payload in sorted(entries.items())) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(entries)} entries into {PATCH_C.name}; manifest {manifest}")
    if missing:
        print(f"missing on their side ({len(missing)}):")
        for name in missing:
            print("   ", name)


if __name__ == "__main__":
    main()
