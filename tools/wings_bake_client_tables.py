"""Bake the cosmetic-wing rows (and four server-only spells) into every client archive that shadows them.

wings_cosmetic_pack ships the batch wings only as ``.dbc1-wings*`` continuations in PATCH-X.  The
late archives (Patch-Zzz*) carry their own full ``Spell.dbc`` / ``SpellVisual.dbc`` / ``SpellIcon.dbc``
and override everything earlier, so the wings must be merged into each of them, and into
patch-Z / patch-enUS-Z.  Also adds client Spell rows for 201111 and 970100-970102 (known by the
character, absent from the client, which skews the spellbook tab counts).

Usage: python tools/wings_bake_client_tables.py [--apply]    (dry run by default; close the game first)
Rebuilding the Esteria / Ethereal / Kyrian client packs rewrites Spell.dbc and undoes this; rerun it.
"""

from __future__ import annotations

import argparse
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wing_cosmetic_pack as pilot  # noqa: E402
from cars_mount_pack import DLL_DEFAULT, Storm, Wdbc, build_wdbc  # noqa: E402

CLIENT = pilot.CLIENT
DATA = CLIENT / "Data"
BACKUP = CLIENT / "_backups" / "wings-bake"
TABLES = ("SpellVisualEffectName", "SpellVisualKit", "SpellVisualKitModelAttach", "SpellVisual",
          "Spell", "SkillLineAbility", "SpellIcon")
SLUGS = ("wings-batch", "wings-batch2")
SERVER_ONLY_SPELLS = (201111, 970100, 970101, 970102)
DB_EXEC = ["docker", "exec", "ac-database", "sh", "-c"]
pilot.DBC_LAYOUT["SpellIcon"] = (2, 8, (1,))


def merge_table(base: bytes, extra: bytes, table: str) -> bytes:
    """Like wing_cosmetic_pack.merge_table, but empty string cells get offset 0 (stock rows keep stale ones)."""
    left, right = Wdbc(base), Wdbc(extra)
    assert (left.fields, left.record_size) == (right.fields, right.record_size), table
    source = {id(row): left for row in left.rows} | {id(row): right for row in right.rows}
    added = {row[0]: row for row in right.rows}
    rows = [added.pop(row[0], row) for row in left.rows] + list(added.values())
    key = pilot.row_order_key(table, left.rows)
    if key is not None:
        rows = sorted(rows, key=key)
    strings = {}
    for index, row in enumerate(rows):
        for field in pilot.DBC_LAYOUT[table][2]:
            text = source[id(row)].text(row[field]) if row[field] else ""
            if text:
                strings[(index, field)] = text
            else:
                row[field] = 0
    merged = build_wdbc(rows, left.fields, left.record_size, strings)
    check = Wdbc(merged)
    by_id = {row[0]: row for row in check.rows}
    for row in left.rows:
        for field in pilot.DBC_LAYOUT[table][2]:
            assert left.text(row[field]) == check.text(by_id[row[0]][field]), (table, row[0], field)
    return merged


def mysql(sql: str) -> str:
    script = 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" --batch --raw -N -e "%s"' % sql
    return subprocess.run(DB_EXEC + [script], capture_output=True, text=True, check=True).stdout


def server_spell_rows() -> bytes:
    """Spell.dbc rows for SERVER_ONLY_SPELLS, built from the world DB's spell_dbc (same column order)."""
    kinds = [line.split("\t") for line in mysql(
        "select COLUMN_NAME,DATA_TYPE from information_schema.columns where table_schema='acore_world' "
        "and table_name='spell_dbc' order by ordinal_position").splitlines()]
    ids = ",".join(map(str, SERVER_ONLY_SPELLS))
    rows, strings = [], {}
    for index, line in enumerate(mysql(f"select * from acore_world.spell_dbc where ID in ({ids})").splitlines()):
        values = line.split("\t")
        assert len(values) == len(kinds) == 234
        row = []
        for field, ((_, kind), value) in enumerate(zip(kinds, values)):
            if kind in ("varchar", "text"):
                row.append(0)
                if value not in ("", "NULL"):
                    strings[(index, field)] = value
            elif kind == "float":
                row.append(struct.unpack("<I", struct.pack("<f", float(value)))[0])
            else:
                row.append(int(value) & 0xFFFFFFFF)
        rows.append(row)
    return build_wdbc(rows, 234, 936, strings)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    apply = parser.parse_args().apply
    storm = Storm(DLL_DEFAULT)

    handle = storm.open_archive(pilot.CLIENT_ARCHIVE)
    continuations = {}
    for table in TABLES:
        for slug in SLUGS:
            try:
                continuations.setdefault(table, []).append(storm.read(handle, f"DBFilesClient/{table}.dbc1-{slug}"))
            except OSError:
                pass
    storm.dll.SFileCloseArchive(handle)
    continuations.setdefault("Spell", []).append(server_spell_rows())

    late = [p for p in sorted(DATA.glob("*.[mM][pP][qQ]")) if p.name.lower().startswith("patch-zzz")]
    for archive in (*pilot.CLIENT_Z_ARCHIVES, *late):
        handle = storm.open_archive(archive)
        entries = {}
        for table in TABLES:
            name = f"DBFilesClient\\{table}.dbc"
            try:
                base = storm.read(handle, name)
            except OSError:
                continue
            merged = base
            for extra in continuations.get(table, []):
                merged = merge_table(merged, extra, table)
            print(f"{archive.name:40} {table:28} {Wdbc(base).count} -> {Wdbc(merged).count}")
            if merged != base:
                entries[name] = merged
                if apply:
                    saved = BACKUP / archive.name / f"{table}.dbc"
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    if not saved.exists():
                        saved.write_bytes(base)
        storm.dll.SFileCloseArchive(handle)
        if apply and entries:
            storm.replace_archive_entries(archive, entries)
            pilot.verify_entry(storm, archive, entries)
            print("written", archive.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
