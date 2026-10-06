"""Cosmetic-wings pilot: bridge one Sirus wing model into Esteria.

Donor (Sirus client, ``patch-4.MPQ`` / ``ruRU/patch-ruRU-4.mpq``):

* ``sirus\\Wings1.m2`` (MD20 v264, 94 vertices), ``sirus\\Wings100.skin``,
  ``sirus\\Am.blp`` and ``sirus\\Pa.blp`` (the model's two texture slots).
* The DBC chain that renders it - ``SpellVisualEffectName 8685`` ->
  ``SpellVisualKitModelAttach 6128`` (AttachmentID 16, zero offsets) ->
  ``SpellVisualKit 17883`` -> ``SpellVisual 19032`` (StateKit) -> spell 313553.
  Sirus rows are copied verbatim and re-numbered instead of re-authored.

Client delivery (two layers, because a spell the client cannot place or see is
unusable):

1. assets + WXL ``.dbc1-wings`` continuations + merged ``wxl-dbc.manifest`` in
   ``Data\\PATCH-X.MPQ`` (the additive-content archive), and
2. the same rows merged into the full ``Spell``, ``SpellVisual``,
   ``SpellVisualEffectName``, ``SpellVisualKit``, ``SpellVisualKitModelAttach``,
   ``SkillLineAbility`` and ``SkillLine`` tables inside both ``Data\\patch-Z.MPQ``
   and ``Data\\enUS\\patch-enUS-Z.MPQ`` - those two archives hold Esteria's
   effective client tables.

The spell is filed under a dedicated skill line 779 "Cosmetics" (category 7, the
same tab family as Mounts/Companions), granted to every character.

Server: ``spell_dbc``, ``skilllineability_dbc``, ``skillline_dbc`` and
``playercreateinfo_skills`` (world) plus a ``character_skills`` backfill
(characters) so existing characters get the tab too.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import (  # noqa: E402
    DLL_DEFAULT,
    Storm,
    Wdbc,
    _blank_spell_strings,
    _sql_insert,
    build_wdbc,
    merge_wxl_manifest,
)

REPO = Path(__file__).resolve().parents[1]

SIRUS_DATA = Path(r"D:\Sirus\_client\World of Warcraft Sirus\Data")
SIRUS_ASSET_ARCHIVE = SIRUS_DATA / "patch-4.MPQ"
SIRUS_DBC_ARCHIVE = SIRUS_DATA / "ruRU" / "patch-ruRU-4.mpq"

CLIENT = Path(r"G:\3.3.5a - Dev")
CLIENT_ARCHIVE_ROOT = CLIENT / "Data"  # never scan CLIENT/Backups: this file writes into every copy it finds
CLIENT_ARCHIVE = CLIENT / "Data" / "PATCH-X.MPQ"
CLIENT_BASE_SPELL_ARCHIVE = CLIENT / "Data" / "enUS" / "patch-enUS-Z.MPQ"
CLIENT_Z_ARCHIVES = (CLIENT / "Data" / "patch-Z.MPQ", CLIENT / "Data" / "enUS" / "patch-enUS-Z.MPQ")
# The client ships several copies of these two tables (root + locale chain) and this client has no
# SkillRaceClassInfo.dbc, so which copy wins for the spellbook tab cannot be pinned down: write the
# pilot rows into every copy instead.
SKILL_TABLES = ("SkillLine", "SkillLineAbility", "SkillRaceClassInfo")

Q = chr(96)


def quoted(name: str) -> str:
    return Q + name + Q


# One pilot family. Visual-table IDs sit just above the effective client maxima
# (effect 8144, kit 20217, attach 5028, visual 30111); the spell reuses Esteria's
# 9701xx custom band and stays below the client's current Spell.dbc maximum.
SLUG = "wings"
SPELL_ID = 970200
EFFECT_NAME_ID = 8145
KIT_ID = 20218
KIT_ATTACH_ID = 5029
VISUAL_ID = 30112
ATTACHMENT_ID = 16
SKILL_LINE = 779  # dedicated "Cosmetics" tab (778/780+ are taken by stock/custom lines)
SKILL_LINE_NAME = "Cosmetics"
SKILL_LINE_CATEGORY = 7  # same tab category as Mounts (777) / Companions (778)
SKILL_LINE_ICON = 153  # borrowed SpellIcon; replaced by a real wing icon when the batch lands
# The client fixes a class's spellbook TAB SET from SkillLineAbility: a category-7 line is in a
# class's tab set only if one of its rows carries that class bit in ClassMask, and a row with
# ClassMask 0 contributes nothing (see mod-classless-wildcard client-patch/lib/dbc.py).
ALL_CLASSES_MASK = 0x5FF
ALL_RACES_MASK = 0xFFFFFFFF
# Client-side SkillRaceClassInfo id. Esteria's classless patch hands out ids from 990000 upward for
# its class skill lines, so keep clear of that run.
CLIENT_SKILL_RACE_CLASS_ID = 990900
SPELL_TEMPLATE_ID = 6606  # "Self Visual - Sleep Until Cancelled (DND)": infinite dummy aura
SPELL_TEMPLATE_SKILL_LINE = 777  # cloned as the shape for the Cosmetics line
SPELL_NAME = "Cosmetic Wings (Pilot)"
SPELL_DESCRIPTION = "Esteria cosmetic-wings pilot."
AURA_DESCRIPTION = "Cosmetic wings."

DONOR_ASSETS = (r"sirus\Wings1.m2", r"sirus\Wings100.skin", r"sirus\Am.blp", r"sirus\Pa.blp")
DONOR_EFFECT_NAME_ID = 8685
DONOR_KIT_ID = 17883
DONOR_KIT_ATTACH_ID = 6128
DONOR_VISUAL_ID = 19032

# (fields, record size, string field indices) per the 3.3.5a layout.
DBC_LAYOUT = {
    "SpellVisualEffectName": (7, 28, (1, 2)),
    "SpellVisualKit": (38, 152, ()),
    "SpellVisualKitModelAttach": (10, 40, ()),
    "SpellVisual": (32, 128, ()),
    "Spell": (234, 936, tuple(range(136, 152)) + tuple(range(153, 169)) + tuple(range(170, 186)) + tuple(range(187, 203))),
    "SkillLineAbility": (14, 56, ()),
    "SkillLine": (56, 224, tuple(range(3, 19)) + tuple(range(20, 36)) + tuple(range(38, 54))),
    "SkillRaceClassInfo": (8, 32, ()),
}

SKILL_RACE_CLASS_ID = 1147  # one above the mounted SkillRaceClassInfo.dbc maximum (1146)
SKILL_RACE_CLASS_MASK = 2021654527  # same race mask the Mounts/Companions lines use
SKILL_RACE_CLASS_CLASSES = 1535     # same class mask the Mounts/Companions lines use

SKILLRC_COLUMNS = (
    "ID", "SkillID", "RaceMask", "ClassMask", "Flags", "MinLevel", "SkillTierID", "SkillCostIndex",
)

SKILLLINE_LINE_COLUMNS = (
    "ID", "CategoryID", "SkillCostsID", "DisplayName_Lang_enUS", "DisplayName_Lang_Mask",
    "Description_Lang_Mask", "SpellIconID", "AlternateVerb_Lang_Mask", "CanLink",
)

SKILLLINE_COLUMNS = (
    "ID", "SkillLine", "Spell", "RaceMask", "ClassMask", "ExcludeRace", "ExcludeClass", "MinSkillLineRank",
    "SupercededBySpell", "AcquireMethod", "TrivialSkillLineRankHigh", "TrivialSkillLineRankLow",
    "CharacterPoints_1", "CharacterPoints_2",
)

SPELL_COLUMNS = (
    "ID", "Mechanic", "Attributes", "AttributesEx4", "AttributesEx6", "AttributesEx7", "CastingTimeIndex",
    "InterruptFlags", "AuraInterruptFlags", "ProcChance", "SpellLevel", "DurationIndex", "RangeIndex",
    "EquippedItemClass", "Effect_1", "Effect_2", "Effect_3", "EffectDieSides_1", "EffectDieSides_2",
    "EffectDieSides_3", "EffectBasePoints_1", "EffectBasePoints_2", "EffectBasePoints_3", "ImplicitTargetA_1",
    "ImplicitTargetA_2", "EffectAura_1", "EffectAura_2", "EffectAura_3", "EffectMiscValue_1",
    "EffectTriggerSpell_1", "SpellVisualID_1", "SpellIconID", "Name_Lang_enUS", "Name_Lang_enGB",
    "Name_Lang_Mask", "Description_Lang_enUS", "Description_Lang_enGB", "Description_Lang_Mask",
    "AuraDescription_Lang_enUS", "AuraDescription_Lang_enGB", "AuraDescription_Lang_Mask",
    "StartRecoveryCategory", "EffectChainAmplitude_1", "EffectChainAmplitude_2", "EffectChainAmplitude_3",
    "SchoolMask",
)


class PilotError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def _f32(value: int) -> float:
    return struct.unpack("<f", struct.pack("<I", value & 0xFFFFFFFF))[0]


def _i32(value: int) -> int:
    return struct.unpack("<i", struct.pack("<I", value & 0xFFFFFFFF))[0]


def spell_row_for_pilot(template: list) -> list:
    """Re-point a donor visual template at the pilot chain and make it a normal, visible spell."""
    row = list(template)
    row[0] = SPELL_ID
    row[131] = VISUAL_ID
    row[132] = 0
    # Client-only UI hiding inherited from the template:
    #   Attr0 0x80 DO_NOT_DISPLAY  -> hidden from the spellbook and the aura bar
    #   Attr0 0x100 DO_NOT_LOG     -> hidden from the combat log
    #   Attr1 0x10000000 NO_AURA_ICON -> hidden from the aura bar
    row[4] &= ~0x180
    row[5] = 0
    # 0x2 AURA_INTERRUPT_FLAG_NOT_SEATED makes the core sit the caster on apply.
    row[32] = 0
    _blank_spell_strings(row)
    row[152], row[169], row[186], row[203] = 16712190, 0, 16712190, 16712188
    return row


def spell_strings() -> dict:
    return {
        (0, 136): SPELL_NAME,
        (0, 137): SPELL_NAME,
        (0, 170): SPELL_DESCRIPTION,
        (0, 171): SPELL_DESCRIPTION,
        (0, 187): AURA_DESCRIPTION,
        (0, 188): AURA_DESCRIPTION,
    }


def spell_sql_row(row: list) -> tuple:
    """Same column/value mapping the shipped mount pack uses, minus mount-only fields."""
    return (
        row[0], row[3], row[4], 0, row[10], row[11], row[28], row[31], row[32], row[35], row[39], row[40],
        row[46], _i32(row[68]), row[71], row[72], 0, row[74], row[75], 0, row[80], row[81], 0, row[86],
        row[87], row[95], row[96], 0, row[110], 0, row[131], row[133], SPELL_NAME, SPELL_NAME, 16712190,
        SPELL_DESCRIPTION, SPELL_DESCRIPTION, 16712190, AURA_DESCRIPTION, AURA_DESCRIPTION, 16712188,
        row[205], _f32(row[216]), _f32(row[217]), _f32(row[218]), row[225],
    )


def skill_line_ability_row() -> list:
    """Files the spell into the dedicated Cosmetics tab for every class.

    ClassMask 0 would leave the line out of every class's tab set, so the spell would land in
    General and no Cosmetics tab would be drawn at all.
    """
    return [SPELL_ID, SKILL_LINE, SPELL_ID, 0, ALL_CLASSES_MASK, 0, 0, 1, 0, 0, 0, 0, 0, 0]


def client_skill_race_class_row() -> list:
    """The client only draws a tab for a line its own SkillRaceClassInfo allows the class."""
    return [CLIENT_SKILL_RACE_CLASS_ID, SKILL_LINE, ALL_RACES_MASK, ALL_CLASSES_MASK, 2, 0, 0, 0]


def skill_race_class_row() -> tuple:
    """Without this row Player::_LoadSkills deletes the skill on login ("invalid for race/class")."""
    return (SKILL_RACE_CLASS_ID, SKILL_LINE, SKILL_RACE_CLASS_MASK, SKILL_RACE_CLASS_CLASSES, 2, 0, 0, 0)


def skill_line_sql_row() -> tuple:
    return (SKILL_LINE, SKILL_LINE_CATEGORY, 0, SKILL_LINE_NAME, 16712190, 16712190, SKILL_LINE_ICON, 16712172, 0)


def characters_sql_text() -> str:
    table = quoted("character_skills")
    return (
        "-- Cosmetic wings pilot: grant the dedicated Cosmetics skill line to existing characters.\n"
        f"DELETE FROM {table} WHERE {quoted('skill')} = {SKILL_LINE};\n"
        f"INSERT INTO {table} ({quoted('guid')}, {quoted('skill')}, {quoted('value')}, {quoted('max')})\n"
        f"SELECT {quoted('guid')}, {SKILL_LINE}, 1, 400 FROM {quoted('characters')};\n"
    )


def skill_line_row(template: list) -> list:
    """Clone the Mounts line shape into a Cosmetics line (name/description/verbs re-authored)."""
    row = list(template)
    row[0] = SKILL_LINE
    row[1] = SKILL_LINE_CATEGORY
    row[2] = 0
    row[3:19] = [0] * 16
    row[19] = 16712190
    row[20:36] = [0] * 16
    row[36] = 16712190
    row[37] = SKILL_LINE_ICON
    row[38:54] = [0] * 16
    row[54] = 16712172
    row[55] = 0
    return row


def build_continuations(rows: dict) -> dict:
    strings = {
        "SpellVisualEffectName": {(0, 1): f"Esteria {SLUG}", (0, 2): r"sirus\Wings1.mdx"},
        "Spell": spell_strings(),
        "SkillLine": {(0, 3): SKILL_LINE_NAME},
    }
    entries = {}
    for table in DBC_LAYOUT:
        fields, record_size, _ = DBC_LAYOUT[table]
        entries[f"DBFilesClient/{table}.dbc1-{SLUG}"] = build_wdbc(
            [rows[table]], fields, record_size, strings.get(table),
        )
    return entries


def row_order_key(table: str, rows: list):
    """Match the base file's own ordering; reordering a DBC the client scans in order breaks it.

    The SkillRaceClassInfo copies in this client are ordered by SkillID, not by row id. Sorting
    them by id made the client drop every spellbook tab, so all spells fell into General.
    """
    ids = [row[0] for row in rows]
    if ids == sorted(ids):
        return lambda row: row[0]
    if table == "SkillRaceClassInfo":
        skills = [row[1] for row in rows]
        if skills == sorted(skills):
            return lambda row: row[1]
    return None


def merge_table(base: bytes, extra: bytes, table: str) -> bytes:
    """Rebase two same-layout tables into one, later rows winning on equal id, order preserved."""
    left, right = Wdbc(base), Wdbc(extra)
    if (left.fields, left.record_size) != (right.fields, right.record_size):
        raise PilotError(f"layout mismatch while merging {table}")
    sources = {}
    for row in left.rows:
        sources[id(row)] = left
    for row in right.rows:
        sources[id(row)] = right
    additions = {row[0]: row for row in right.rows}
    rows = [additions.pop(row[0], row) for row in left.rows]
    rows.extend(additions.values())
    key = row_order_key(table, left.rows)
    if key is not None:
        rows = sorted(rows, key=key)
    strings = {}
    string_fields = DBC_LAYOUT[table][2]
    for index, row in enumerate(rows):
        source = sources[id(row)]
        for field in string_fields:
            if row[field]:
                text = source.text(row[field])
                if text:
                    strings[(index, field)] = text
    result = build_wdbc(rows, left.fields, left.record_size, strings)
    verify_string_cells(table, left, result)
    return result


def verify_string_cells(table: str, base: Wdbc, merged: bytes) -> None:
    """A rebase that forgets a string column leaves stale offsets -> garbled client text."""
    rebuilt = Wdbc(merged)
    by_id = {row[0]: row for row in rebuilt.rows}
    for row in base.rows:
        new = by_id.get(row[0])
        if new is None:
            raise PilotError(f"{table}: row {row[0]} lost during merge")
        for field in DBC_LAYOUT[table][2]:
            if base.text(row[field]) != rebuilt.text(new[field]):
                raise PilotError(f"{table}: row {row[0]} field {field} text changed during merge")


def base_table(storm: Storm, table: str) -> bytes:
    """Largest client copy of a table is the safest merge base (it is a superset of the tuned ones)."""
    best = None
    for archive in sorted(CLIENT_ARCHIVE_ROOT.rglob("*.mpq"), key=lambda path: str(path).casefold()):
        try:
            handle = storm.open_archive(archive)
        except OSError:
            continue
        try:
            try:
                blob = storm.read(handle, f"DBFilesClient\\{table}.dbc")
            except OSError:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
        if best is None or Wdbc(blob).count > Wdbc(best).count:
            best = blob
    if best is None:
        raise PilotError(f"no client copy of {table}.dbc")
    return best


def client_row(storm: Storm, table: str, row_id: int) -> list:
    """Row from the largest client copy of `table` (the merged Z copies win over stock ones)."""
    return Wdbc(base_table(storm, table)).row(row_id)


def donor_assets(storm: Storm) -> dict:
    handle = storm.open_archive(SIRUS_ASSET_ARCHIVE)
    try:
        assets = {}
        for name in DONOR_ASSETS:
            try:
                assets[name] = storm.read(handle, name)
            except OSError as exc:
                raise PilotError(f"donor asset missing: {name}") from exc
    finally:
        storm.dll.SFileCloseArchive(handle)
    model = assets[r"sirus\Wings1.m2"]
    if model[:4] != b"MD20" or struct.unpack_from("<I", model, 4)[0] != 264:
        raise PilotError("donor model is not WotLK MD20/264")
    return assets


def donor_rows(storm: Storm) -> dict:
    wanted = {
        "SpellVisualEffectName": DONOR_EFFECT_NAME_ID,
        "SpellVisualKit": DONOR_KIT_ID,
        "SpellVisualKitModelAttach": DONOR_KIT_ATTACH_ID,
        "SpellVisual": DONOR_VISUAL_ID,
    }
    handle = storm.open_archive(SIRUS_DBC_ARCHIVE)
    try:
        rows = {}
        for table, row_id in wanted.items():
            blob = storm.read(handle, f"DBFilesClient\\{table}.dbc")
            rows[table] = Wdbc(blob).row(row_id)
    finally:
        storm.dll.SFileCloseArchive(handle)
    return rows


def client_spell_template(storm: Storm) -> list:
    handle = storm.open_archive(CLIENT_BASE_SPELL_ARCHIVE)
    try:
        blob = storm.read(handle, "DBFilesClient\\Spell.dbc")
    finally:
        storm.dll.SFileCloseArchive(handle)
    row = Wdbc(blob).row(SPELL_TEMPLATE_ID)
    if row[40] != 21 or row[71] != 6 or row[95] != 4 or row[86] != 1:
        raise PilotError(f"spell {SPELL_TEMPLATE_ID} is not the expected infinite dummy aura")
    return row


def pilot_rows(storm: Storm) -> dict:
    donor = donor_rows(storm)

    effect = donor["SpellVisualEffectName"]
    effect[0] = EFFECT_NAME_ID

    kit = donor["SpellVisualKit"]
    kit[0] = KIT_ID

    attach = donor["SpellVisualKitModelAttach"]
    attach[0] = KIT_ATTACH_ID
    attach[1] = KIT_ID
    attach[2] = EFFECT_NAME_ID
    attach[3] = ATTACHMENT_ID

    visual = donor["SpellVisual"]
    visual[0] = VISUAL_ID
    visual[1] = visual[2] = visual[3] = visual[5] = visual[6] = 0
    visual[4] = KIT_ID

    return {
        "SpellVisualEffectName": effect,
        "SpellVisualKit": kit,
        "SpellVisualKitModelAttach": attach,
        "SpellVisual": visual,
        "Spell": spell_row_for_pilot(client_spell_template(storm)),
        "SkillLineAbility": skill_line_ability_row(),
        "SkillRaceClassInfo": client_skill_race_class_row(),
        "SkillLine": skill_line_row(client_row(storm, "SkillLine", SPELL_TEMPLATE_SKILL_LINE)),
    }


def archive_dbc_entries(storm: Storm, archive: Path, continuations: dict) -> dict:
    """Merge the pilot rows into THIS archive's own copies, never another archive's variant.

    A different copy can be a different vintage (Patch-Y carries extra classless
    SkillRaceClassInfo rows) and a different row order, so the base must be the file the client
    would read from this archive.
    """
    merged = {}
    handle = storm.open_archive(archive)
    try:
        for table in DBC_LAYOUT:
            entry = f"DBFilesClient\\{table}.dbc"
            try:
                blob = storm.read(handle, entry)
            except OSError:
                # This archive has no copy of the table (e.g. the visual tables live in
                # common.mpq / patch-P). Seed it from the client's best copy so the merged table
                # wins over the original once this archive loads.
                blob = base_table(storm, table)
            merged[entry] = merge_table(blob, continuations[f"DBFilesClient/{table}.dbc1-{SLUG}"], table)
    finally:
        storm.dll.SFileCloseArchive(handle)
    return merged


def sql_text(row: list) -> str:
    body = _sql_insert("spell_dbc", SPELL_COLUMNS, [spell_sql_row(row)], [SPELL_ID])
    body += "\n\n" + _sql_insert("skilllineability_dbc", SKILLLINE_COLUMNS, [skill_line_ability_row()], [SPELL_ID])
    body += "\n\n" + _sql_insert("skillline_dbc", SKILLLINE_LINE_COLUMNS, [skill_line_sql_row()], [SKILL_LINE])
    body += "\n\n" + _sql_insert("skillraceclassinfo_dbc", SKILLRC_COLUMNS, [skill_race_class_row()], [SKILL_RACE_CLASS_ID])
    table = quoted("playercreateinfo_skills")
    body += (
        f"\n\nDELETE FROM {table} WHERE {quoted('skill')} = {SKILL_LINE};\n"
        f"INSERT INTO {table} ({quoted('raceMask')}, {quoted('classMask')}, {quoted('skill')}, {quoted('rank')}, {quoted('comment')})\n"
        f"SELECT {quoted('raceMask')}, {quoted('classMask')}, {SKILL_LINE}, {quoted('rank')}, '{SKILL_LINE_NAME}'"
        f" FROM {table} WHERE {quoted('skill')} = {SPELL_TEMPLATE_SKILL_LINE};\n"
    )
    return (
        "-- Cosmetic wings pilot (see tools/wing_cosmetic_pack.py).\n"
        f"-- Spell {SPELL_ID} applies an infinite dummy aura whose client visual is\n"
        f"-- SpellVisual {VISUAL_ID} -> kit {KIT_ID} -> effect {EFFECT_NAME_ID} (sirus\\Wings1).\n"
        f"-- It is filed under skill line {SKILL_LINE} '{SKILL_LINE_NAME}'.\n"
        "-- Client rows ship as WXL continuations in Data\\PATCH-X.MPQ and as merged full\n"
        "-- DBFilesClient tables in patch-Z.MPQ + enUS\\patch-enUS-Z.MPQ.\n"
        f"{body}\n"
    )


def manifest_entry_names() -> list:
    return [f"DBFilesClient/{table}.dbc1-{SLUG}" for table in DBC_LAYOUT]


def read_manifest(storm: Storm, archive: Path) -> bytes:
    handle = storm.open_archive(archive)
    try:
        try:
            return storm.read(handle, "wxl-dbc.manifest")
        except OSError:
            return b""
    finally:
        storm.dll.SFileCloseArchive(handle)


def build(apply: bool) -> int:
    storm = Storm(DLL_DEFAULT)
    rows = pilot_rows(storm)
    continuations = build_continuations(rows)
    entries = dict(donor_assets(storm))
    entries.update(continuations)
    additions = ("# Esteria cosmetic wings pilot\n" + "\n".join(manifest_entry_names()) + "\n").encode("utf-8")
    entries["wxl-dbc.manifest"] = merge_wxl_manifest(read_manifest(storm, CLIENT_ARCHIVE), additions)
    z_entries = {path: archive_dbc_entries(storm, path, continuations) for path in CLIENT_Z_ARCHIVES}

    print(f"archive      {CLIENT_ARCHIVE}")
    for name, payload in sorted(entries.items()):
        print(f"  {len(payload):>9}  {name}")
    print("full tables  " + ", ".join(f"{k.split(chr(92))[-1]}={len(v)}B" for k, v in sorted(z_entries[CLIENT_Z_ARCHIVES[0]].items())))
    print(f"spell        {SPELL_ID}  visual {VISUAL_ID}  kit {KIT_ID}  effect {EFFECT_NAME_ID}  attach {ATTACHMENT_ID}  tab {SKILL_LINE} {SKILL_LINE_NAME}")

    report = {
        "donor": {
            "asset_archive": str(SIRUS_ASSET_ARCHIVE),
            "dbc_archive": str(SIRUS_DBC_ARCHIVE),
            "assets": {name: sha256_bytes(payload) for name, payload in donor_assets(storm).items()},
            "rows": {table: row[0] for table, row in donor_rows(storm).items()},
        },
        "pilot": {
            "spell": SPELL_ID, "spell_visual": VISUAL_ID, "visual_kit": KIT_ID,
            "effect_name": EFFECT_NAME_ID, "kit_attach": KIT_ATTACH_ID, "attachment": ATTACHMENT_ID,
            "skill_line": SKILL_LINE, "skill_line_name": SKILL_LINE_NAME,
        },
        "archive": str(CLIENT_ARCHIVE),
        "entries": sorted(entries),
        "merged_dbc": sorted(z_entries[CLIENT_Z_ARCHIVES[0]]),
        "applied": False,
        "sql": None,
        "sql_characters": None,
        "live_visual_test": "not run",
    }
    if not apply:
        print("\ndry run: pass --apply to back up, write the archives and emit the SQL")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    targets = (CLIENT_ARCHIVE,) + CLIENT_Z_ARCHIVES
    before = {path: sha256_file(path) for path in targets}
    backup_dir = CLIENT / "Backups" / f"wing-pilot-{stamp}-{before[CLIENT_ARCHIVE][:8]}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for path in targets:
        backup = backup_dir / path.name
        if not backup.exists():
            shutil.copy2(path, backup)
        if sha256_file(backup) != before[path]:
            raise PilotError(f"backup does not match live archive: {backup}")
    print(f"\nbackup       {backup_dir}")

    storm.replace_archive_entries(CLIENT_ARCHIVE, entries)
    verify_entry(storm, CLIENT_ARCHIVE, entries)
    for path in CLIENT_Z_ARCHIVES:
        storm.replace_archive_entries(path, z_entries[path])
        verify_entry(storm, path, z_entries[path])
    swept = deploy_skill_tables(storm, continuations, backup_dir, before)
    touched = (*targets, *swept)
    after = {path: sha256_file(path) for path in touched}
    for path in touched:
        print(f"  {path.name:24} {before[path][:12]} -> {after[path][:12]}")
    if swept:
        print("skill tables " + ", ".join(f"{path.name}(+{len(names)})" for path, names in swept.items()))

    stamp = f"{datetime.now():%Y%m%d%H%M%S%f}"[:17]
    sql_path = REPO / "data" / "sql" / "updates" / "pending_db_world" / f"rev_{stamp}.sql"
    sql_path.write_text(sql_text(rows["Spell"]), encoding="utf-8")
    char_sql_path = REPO / "data" / "sql" / "updates" / "pending_db_characters" / f"rev_{stamp}.sql"
    char_sql_path.write_text(characters_sql_text(), encoding="utf-8")
    print(f"sql world    {sql_path.relative_to(REPO)}")
    print(f"sql chars    {char_sql_path.relative_to(REPO)}")

    report["applied"] = True
    report["archive_sha256"] = {str(path): {"before": before[path], "after": after[path]} for path in touched}
    report["skill_table_sweep"] = {str(path): names for path, names in swept.items()}
    report["backup"] = str(backup_dir)
    report["sql"] = str(sql_path.relative_to(REPO))
    report["sql_characters"] = str(char_sql_path.relative_to(REPO))
    out = REPO / "var" / "wing-pilot"
    out.mkdir(parents=True, exist_ok=True)
    (out / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"report       {(out / 'build-report.json').relative_to(REPO)}")
    print(f"\nnext: import the SQL, restart the worldserver, then relaunch the client ({SKILL_LINE_NAME} tab)")
    return 0


def archives_with_table(storm: Storm, table: str) -> list:
    found = []
    for archive in sorted(CLIENT_ARCHIVE_ROOT.rglob("*.mpq"), key=lambda path: str(path).casefold()):
        try:
            handle = storm.open_archive(archive)
        except OSError:
            continue
        try:
            try:
                blob = storm.read(handle, f"DBFilesClient\\{table}.dbc")
            except OSError:
                continue
        finally:
            storm.dll.SFileCloseArchive(handle)
        found.append((archive, blob))
    return found


def deploy_skill_tables(storm: Storm, continuations: dict, backup_dir: Path, before: dict) -> dict:
    """Write the Cosmetic skill rows into every client copy of SkillLine/SkillLineAbility."""
    swept = {}
    for table in SKILL_TABLES:
        entry = f"DBFilesClient\\{table}.dbc"
        continuation = continuations[f"DBFilesClient/{table}.dbc1-{SLUG}"]
        for archive, blob in archives_with_table(storm, table):
            if archive in CLIENT_Z_ARCHIVES:
                continue
            merged = merge_table(blob, continuation, table)
            if merged == blob:
                continue
            if archive not in before:
                before[archive] = sha256_file(archive)
            backup = backup_dir / "entries" / archive.name / entry.replace("\\", "_")
            if not backup.exists():
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_bytes(blob)
            storm.replace_archive_entries(archive, {entry: merged})
            verify_entry(storm, archive, {entry: merged})
            swept.setdefault(archive, []).append(entry)
    return swept


def verify_entry(storm: Storm, archive: Path, expected: dict) -> None:
    handle = storm.open_archive(archive)
    try:
        for name, payload in expected.items():
            if storm.read(handle, name) != payload:
                raise PilotError(f"readback mismatch: {archive.name}:{name}")
    finally:
        storm.dll.SFileCloseArchive(handle)


def check() -> int:
    storm = Storm(DLL_DEFAULT)
    report = json.loads((REPO / "var" / "wing-pilot" / "build-report.json").read_text(encoding="utf-8"))
    if not report["applied"]:
        raise PilotError("report says the archives were never applied")
    continuations = build_continuations(pilot_rows(storm))
    entries = dict(donor_assets(storm))
    entries.update(continuations)
    verify_entry(storm, CLIENT_ARCHIVE, entries)
    handle = storm.open_archive(CLIENT_ARCHIVE)
    try:
        manifest = storm.read(handle, "wxl-dbc.manifest").decode("utf-8")
    finally:
        storm.dll.SFileCloseArchive(handle)
    if not all(name in manifest for name in manifest_entry_names()):
        raise PilotError("wxl-dbc.manifest is missing pilot entries")
    for table, (fields, record_size, _) in DBC_LAYOUT.items():
        parsed = Wdbc(continuations[f"DBFilesClient/{table}.dbc1-{SLUG}"])
        if (parsed.fields, parsed.record_size, parsed.count) != (fields, record_size, 1):
            raise PilotError(f"bad continuation layout: {table}")
    for archive in CLIENT_Z_ARCHIVES:
        handle = storm.open_archive(archive)
        try:
            spell = Wdbc(storm.read(handle, "DBFilesClient\\Spell.dbc")).row(SPELL_ID)
            if (spell[131], spell[95], spell[71], spell[40]) != (VISUAL_ID, 4, 6, 21):
                raise PilotError(f"{archive.name}: merged Spell.dbc row is wrong")
            if spell[4] & 0x180:
                raise PilotError(f"{archive.name}: DO_NOT_DISPLAY/DO_NOT_LOG still set")
            visual = Wdbc(storm.read(handle, "DBFilesClient\\SpellVisual.dbc")).row(VISUAL_ID)
            if visual[4] != KIT_ID:
                raise PilotError(f"{archive.name}: merged SpellVisual.dbc row is wrong")
            if Wdbc(storm.read(handle, "DBFilesClient\\SpellVisualKit.dbc")).row(KIT_ID)[0] != KIT_ID:
                raise PilotError(f"{archive.name}: merged SpellVisualKit.dbc row is missing")
            attach = Wdbc(storm.read(handle, "DBFilesClient\\SpellVisualKitModelAttach.dbc")).row(KIT_ATTACH_ID)
            if (attach[1], attach[2], attach[3]) != (KIT_ID, EFFECT_NAME_ID, ATTACHMENT_ID):
                raise PilotError(f"{archive.name}: merged attach row is wrong")
            effect = Wdbc(storm.read(handle, "DBFilesClient\\SpellVisualEffectName.dbc")).row(EFFECT_NAME_ID)
            if effect[0] != EFFECT_NAME_ID:
                raise PilotError(f"{archive.name}: merged effect row is missing")
            sla = Wdbc(storm.read(handle, "DBFilesClient\\SkillLineAbility.dbc"))
            if not [r for r in sla.rows if r[2] == SPELL_ID and r[1] == SKILL_LINE]:
                raise PilotError(f"{archive.name}: SkillLineAbility row for {SPELL_ID} is missing")
            lines = Wdbc(storm.read(handle, "DBFilesClient\\SkillLine.dbc"))
            line = lines.row(SKILL_LINE)
            if line[1] != SKILL_LINE_CATEGORY or lines.text(line[3]) != SKILL_LINE_NAME:
                raise PilotError(f"{archive.name}: SkillLine row {SKILL_LINE} is wrong")
        finally:
            storm.dll.SFileCloseArchive(handle)
    sql = (REPO / report["sql"]).read_text(encoding="utf-8")
    if f"DELETE FROM {quoted('spell_dbc')} WHERE {quoted('ID')} IN ({SPELL_ID});" not in sql:
        raise PilotError("SQL spell delete missing")
    if f"({SPELL_ID}," not in sql:
        raise PilotError("SQL spell insert missing")
    if "skilllineability_dbc" not in sql or f"{SPELL_ID}, {SKILL_LINE}, {SPELL_ID}" not in sql:
        raise PilotError("SQL skill line ability row missing")
    if "skillline_dbc" not in sql or f"({SKILL_LINE}, {SKILL_LINE_CATEGORY}, 0, '{SKILL_LINE_NAME}'" not in sql:
        raise PilotError("SQL Cosmetics skill line row missing")
    if "playercreateinfo_skills" not in sql:
        raise PilotError("SQL playercreateinfo_skills grant missing")
    if "skillraceclassinfo_dbc" not in sql or f"({SKILL_RACE_CLASS_ID}, {SKILL_LINE}," not in sql:
        raise PilotError("SQL SkillRaceClassInfo row missing")
    for table, marker_index, marker in (
        ("SkillLine", 0, SKILL_LINE),
        ("SkillLineAbility", 2, SPELL_ID),
        ("SkillRaceClassInfo", 1, SKILL_LINE),
    ):
        for archive, blob in archives_with_table(storm, table):
            rows = Wdbc(blob)
            if not [r for r in rows.rows if r[marker_index] == marker]:
                raise PilotError(f"{archive.name}: {table} is missing the pilot row")
    chars_sql = (REPO / report["sql_characters"]).read_text(encoding="utf-8")
    if f"SELECT {quoted('guid')}, {SKILL_LINE}, 1, 400 FROM {quoted('characters')}" not in chars_sql:
        raise PilotError("characters SQL backfill missing")
    print(f"wing pilot check: PASS (spell {SPELL_ID}; tab {SKILL_LINE} {SKILL_LINE_NAME}; PATCH-X + both Z archives)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    parser.add_argument("--apply", action="store_true", help="write the archives and emit the SQL")
    args = parser.parse_args()
    return build(args.apply) if args.action == "build" else check()


if __name__ == "__main__":
    raise SystemExit(main())