"""Build the Freeborn player-hostility FactionTemplate rows and deploy them.

Why this exists
---------------
The 3.3.5a client decides player-versus-player friendliness entirely from the two units'
`UNIT_FIELD_FACTIONTEMPLATE` update fields: the value is used directly as a `FactionTemplate.dbc`
row id (`Wow.exe` `0x0071f770`, reached from the reaction core `0x007251c0` and from `CanAttack`
`0x00729740`). The deployed table is the Faction-Free package, where every player template is
`friendlyMask 6 / hostileMask 8` - friendly to both player groups - so a Freeborn character, which
still wears its race's template, renders Friendly to everyone.

The rows this module writes:

* a fifth faction group bit `V = 16` (`FREEBORN_GROUP_MASK`) is added to the `ourMask` of every
  template a player can wear, so "is a player" is addressable by a bit no NPC has;
* a dedicated Freeborn template row (new id `FREEBORN_TEMPLATE_ID`) with
  `ourMask 1|8`, `friendlyMask 6`, `hostileMask 8|16`, which is hostile to players both ways,
  hostile to monsters both ways (so PvE is unchanged), friendly to both sides' NPCs, and hostile
  to other Freeborn.

Everything else in the table is copied byte-for-byte; the contract test proves that.

Deployment
----------
* server: `mod-wxl-dbc` registers `sFactionTemplateStore` (`WxlDbcRegistry.cpp:90`), so the
  continuation file (`FactionTemplate.dbc1-freeborn`) dropped into `data/dbc-continuations/` is
  merged at startup - no worldserver rebuild.
* client: `wxl-extended-dbc`'s supported-table list does not name `FactionTemplate`, so the full
  patched table is written into the project's own highest-priority archive (`patch-Z.MPQ`) with a
  SHA-256-verified backup, the same workflow `tools/freeborn_team_pack.py` uses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, Storm  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CLIENT_ROOT = Path(r"G:\3.3.5a - Dev")
ARCHIVE_NAME = "patch-Z.MPQ"
DBC_ENTRY = "DBFilesClient\\FactionTemplate.dbc"
BACKUP_DIR_NAME = "_freeborn-hostility-backups"

# Base table: the deployed FactionTemplate.dbc (Faction-Free package). The client copy in
# Patch-F.MPQ and the server copy in env/dist/data/dbc/ are both this exact file.
BASE_CANDIDATES = (
    REPO_ROOT / "modules" / "mod-Faction-Free" / "dbc" / "FactionTemplate.dbc",
    REPO_ROOT / "modules" / "mod-custom-server" / "data" / "dbc" / "FactionTemplate.dbc",
)
BASE_SHA256 = "a344d5546ce50f977170606f24a193066663c0675cdb893a93a6a6a9f21e3c5a"

# Fifth faction group bit. The client's mask comparison is a plain 32-bit test
# (`test [edi+0x14], esi` at Wow.exe 0x0071544e / 0x007154aa), so a bit above the four stock
# groups is honoured; the "four bits" limit reported for this client is inside the
# race-availability function used by the character-create screen, which this change does not touch.
FREEBORN_GROUP_MASK = 16

# Every FactionID the deployed ChrRaces.dbc hands to a playable race, plus the generic
# Alliance/Horde player templates (`InstanceScript.cpp` uses 1/1610; the generics are included
# defensively). All of these must be hostile to the Freeborn template in both directions.
PLAYER_TEMPLATE_IDS = (1, 2, 3, 4, 5, 6, 83, 84, 115, 116, 1610, 1629, 1801, 1802)

# A player template is hostile to a Freeborn because the Freeborn's `ourMask` carries the monster
# group bit, which every stock player row already has in `hostileMask`. The two generic templates
# (83 Horde Generic, 84 Alliance Generic) start with `hostileMask 0`; they get the same
# monster-hostility bit as every other player row so the rule stays uniform. No
# creature_template or gameobject_template row uses either id.
PLAYER_MONSTER_HOSTILITY_BIT = 8

# New row id, appended after the table's current maximum (2236).
FREEBORN_TEMPLATE_ID = 2237
# Faction reference for that row: a Faction.dbc id with `reputationListID < 0` that no
# FactionTemplate row references, so `IsFriendlyTo`'s `faction ==` shortcut and the client's
# reputation lookup both stay out of the way and the masks decide.
FREEBORN_FACTION_ID = 893
FREEBORN_FLAGS = 0x48
FREEBORN_OUR_MASK = 1 | 8
FREEBORN_FRIENDLY_MASK = 6
FREEBORN_HOSTILE_MASK = 8 | FREEBORN_GROUP_MASK
FACTION_TEMPLATE_FIELDS = 14
FACTION_TEMPLATE_RECORD_SIZE = FACTION_TEMPLATE_FIELDS * 4


@dataclass
class Table:
    records: list[tuple[int, ...]]
    strings: bytes

    @property
    def by_id(self) -> dict[int, tuple[int, ...]]:
        return {row[0]: row for row in self.records}


def parse_wdbc(data: bytes) -> Table:
    magic, count, fields, record_size, string_size = struct.unpack_from("<4sIIII", data, 0)
    if magic != b"WDBC":
        raise ValueError("not a WDBC file")
    if fields != FACTION_TEMPLATE_FIELDS or record_size != FACTION_TEMPLATE_RECORD_SIZE:
        raise ValueError(f"unexpected FactionTemplate layout: {fields} fields of {record_size} bytes")
    records = [
        struct.unpack_from(f"<{fields}I", data, 20 + index * record_size) for index in range(count)
    ]
    string_start = 20 + count * record_size
    return Table(records, data[string_start:string_start + string_size])


def build_wdbc(table: Table) -> bytes:
    body = b"".join(struct.pack(f"<{FACTION_TEMPLATE_FIELDS}I", *row) for row in table.records)
    header = struct.pack("<4sIIII", b"WDBC", len(table.records), FACTION_TEMPLATE_FIELDS,
                         FACTION_TEMPLATE_RECORD_SIZE, len(table.strings))
    return header + body + table.strings


def base_table_bytes(explicit: Path | None) -> bytes:
    candidates = (explicit,) if explicit else BASE_CANDIDATES
    for candidate in candidates:
        if candidate and candidate.is_file():
            data = candidate.read_bytes()
            if hashlib.sha256(data).hexdigest() != BASE_SHA256:
                raise ValueError(f"{candidate} is not the expected deployed table")
            return data
    raise FileNotFoundError(f"no base FactionTemplate.dbc found in {candidates}")


def build_rows(base: bytes) -> tuple[bytes, bytes]:
    """Return (full patched table, continuation file with only the changed rows)."""
    table = parse_wdbc(base)
    by_id = table.by_id

    for template_id in PLAYER_TEMPLATE_IDS:
        if template_id not in by_id:
            raise ValueError(f"player template {template_id} is missing from the base table")

    records: list[tuple[int, ...]] = []
    changed: list[tuple[int, ...]] = []
    for row in table.records:
        if row[0] in PLAYER_TEMPLATE_IDS:
            patched = list(row)
            patched[3] |= FREEBORN_GROUP_MASK
            patched[5] |= PLAYER_MONSTER_HOSTILITY_BIT
            new_row = tuple(patched)
            records.append(new_row)
            changed.append(new_row)
        else:
            records.append(row)

    freeborn_row = (
        FREEBORN_TEMPLATE_ID, FREEBORN_FACTION_ID, FREEBORN_FLAGS,
        FREEBORN_OUR_MASK, FREEBORN_FRIENDLY_MASK, FREEBORN_HOSTILE_MASK,
        0, 0, 0, 0, 0, 0, 0, 0,
    )
    records.append(freeborn_row)
    changed.append(freeborn_row)

    full = build_wdbc(Table(records, table.strings))
    continuation = build_wdbc(Table(changed, table.strings))
    return full, continuation


def verify(base: bytes, full: bytes) -> dict:
    """Prove that only the intended rows differ."""
    before_rows = parse_wdbc(base).by_id
    after = parse_wdbc(full).by_id
    added = sorted(set(after) - set(before_rows))
    removed = sorted(set(before_rows) - set(after))
    modified = sorted(i for i in set(before_rows) & set(after) if before_rows[i] != after[i])
    if added != [FREEBORN_TEMPLATE_ID]:
        raise AssertionError(f"unexpected added rows: {added}")
    if removed:
        raise AssertionError(f"rows disappeared: {removed}")
    if sorted(modified) != sorted(PLAYER_TEMPLATE_IDS):
        raise AssertionError(f"unexpected modified rows: {modified}")
    for template_id in PLAYER_TEMPLATE_IDS:
        before, patched = before_rows[template_id], after[template_id]
        if patched[3] != before[3] | FREEBORN_GROUP_MASK:
            raise AssertionError(f"row {template_id}: ourMask did not just gain the group bit")
        if patched[5] != before[5] | PLAYER_MONSTER_HOSTILITY_BIT:
            raise AssertionError(f"row {template_id}: hostileMask did not just gain the monster bit")
        if patched[:3] != before[:3] or patched[4] != before[4] or patched[6:] != before[6:]:
            raise AssertionError(f"row {template_id}: an unrelated field changed")
    row = after[FREEBORN_TEMPLATE_ID]
    if row[3:] != (FREEBORN_OUR_MASK, FREEBORN_FRIENDLY_MASK, FREEBORN_HOSTILE_MASK) + (0,) * 8:
        raise AssertionError(f"Freeborn row is not as specified: {row}")
    return {"added": added, "modified": modified, "record_count": len(after)}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def install_client(client_root: Path, full: bytes, stormlib: Path = DLL_DEFAULT) -> dict:
    """Write the patched table into the client's highest-priority archive, with a backup."""
    archive = client_root / "Data" / ARCHIVE_NAME
    if not archive.is_file():
        raise FileNotFoundError(archive)

    storm = Storm(stormlib)
    handle = storm.open_archive(archive)
    try:
        try:
            before = storm.read(handle, DBC_ENTRY)
        except OSError:
            # The archive does not shadow FactionTemplate.dbc yet: the base table is loaded from
            # Patch-F.MPQ, and this entry is what makes patch-Z win for it.
            before = None
    finally:
        storm.dll.SFileCloseArchive(handle)
    if before == full:
        return {"archive": str(archive), "changed": False}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = client_root / "Data" / BACKUP_DIR_NAME / stamp
    backup_dir.mkdir(parents=True, exist_ok=False)
    backup = backup_dir / archive.name
    shutil.copy2(archive, backup)

    staged = archive.parent / f".{archive.name}.freeborn-hostility-tmp"
    shutil.copy2(archive, staged)
    try:
        storm.replace_archive_entries(staged, {DBC_ENTRY: full})
        verify_handle = storm.open_archive(staged)
        try:
            if storm.read(verify_handle, DBC_ENTRY) != full:
                raise AssertionError("staged archive did not round-trip the patched table")
        finally:
            storm.dll.SFileCloseArchive(verify_handle)
        os.replace(staged, archive)
    except BaseException:
        staged.unlink(missing_ok=True)
        raise

    return {
        "archive": str(archive),
        "changed": True,
        "backup": str(backup),
        "backup_sha256": _sha256(backup),
        "restored_sha256": _sha256(archive),
    }


def restore_client(client_root: Path, backup: Path, stormlib: Path = DLL_DEFAULT) -> dict:
    """Put a previously backed-up archive back, verifying the unpatched round trip."""
    archive = client_root / "Data" / ARCHIVE_NAME
    if not backup.is_file():
        raise FileNotFoundError(backup)
    storm = Storm(stormlib)
    handle = storm.open_archive(backup)
    try:
        stock = storm.read(handle, DBC_ENTRY)
    finally:
        storm.dll.SFileCloseArchive(handle)
    if hashlib.sha256(stock).hexdigest() != BASE_SHA256:
        raise AssertionError("backup does not carry the expected stock table")
    shutil.copy2(backup, archive)
    return {"archive": str(archive), "restored_from": str(backup), "sha256": _sha256(archive)}


def contract() -> dict:
    return {
        "base_sha256": BASE_SHA256,
        "freeborn_template_id": FREEBORN_TEMPLATE_ID,
        "freeborn_faction_id": FREEBORN_FACTION_ID,
        "freeborn_row": {
            "ourMask": FREEBORN_OUR_MASK,
            "friendlyMask": FREEBORN_FRIENDLY_MASK,
            "hostileMask": FREEBORN_HOSTILE_MASK,
            "factionFlags": FREEBORN_FLAGS,
        },
        "group_mask": FREEBORN_GROUP_MASK,
        "player_templates": list(PLAYER_TEMPLATE_IDS),
        "server_deploy": f"data/dbc-continuations/FactionTemplate.dbc1-freeborn",
        "client_deploy": f"{ARCHIVE_NAME}:{DBC_ENTRY}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, help="base FactionTemplate.dbc (default: deployed copy)")
    parser.add_argument("--dbc-out", type=Path, help="write the full patched table here")
    parser.add_argument("--continuation-out", type=Path, help="write the changed-rows continuation here")
    parser.add_argument("--client-root", type=Path, default=CLIENT_ROOT)
    parser.add_argument("--install-client", action="store_true")
    parser.add_argument("--restore-client", type=Path, help="restore this backed-up archive")
    parser.add_argument("--stormlib", type=Path, default=DLL_DEFAULT)
    parser.add_argument("--print-contract", action="store_true")
    parser.add_argument("--print-rows", action="store_true")
    args = parser.parse_args()

    if args.print_contract:
        print(json.dumps(contract(), indent=2, sort_keys=True))
        return 0

    if args.restore_client:
        print(json.dumps(restore_client(args.client_root, args.restore_client, args.stormlib),
                         indent=2, sort_keys=True))
        return 0

    base = base_table_bytes(args.base)
    full, continuation = build_rows(base)
    report = verify(base, full)

    if args.print_rows:
        for row in parse_wdbc(continuation).records:
            print(row)

    if args.dbc_out:
        args.dbc_out.parent.mkdir(parents=True, exist_ok=True)
        args.dbc_out.write_bytes(full)
        report["dbc_out"] = str(args.dbc_out)
    if args.continuation_out:
        args.continuation_out.parent.mkdir(parents=True, exist_ok=True)
        args.continuation_out.write_bytes(continuation)
        report["continuation_out"] = str(args.continuation_out)
    if args.install_client:
        report["client"] = install_client(args.client_root, full, args.stormlib)

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
