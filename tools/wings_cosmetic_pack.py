"""Batch port of the remaining Sirus wing cosmetics into the Cosmetics tab (skill line 779).

Reuses the pilot's helpers from wing_cosmetic_pack.  Per wing:

* pull the M2 + ``00.skin`` + its textures from the Sirus donor archives (the paths are unlisted,
  so they are opened by name),
* add rows for SpellVisualEffectName -> SpellVisualKitModelAttach (AttachmentID 16) ->
  SpellVisualKit -> SpellVisual -> Spell -> SkillLineAbility (+ a SpellIcon when the donor ships a
  matching ``inv_*_wings.blp``),
* ship the assets plus ``.dbc1-*`` continuations in ``Data\\PATCH-X.MPQ`` (the client's
  wxl-extended-dbc merges those at startup -- proven with the pilot),
* emit world SQL (spell_dbc, skilllineability_dbc, an exclusive spell group, the starting-spell
  grant) and characters SQL (grant every wing spell to every character).
"""

from __future__ import annotations

import argparse
import ctypes as c
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cars_mount_pack import DLL_DEFAULT, H, Storm, Wdbc, build_wdbc, merge_wxl_manifest  # noqa: E402
from wotlkconv.m2 import M2Model, parse_m2  # noqa: E402
from wotlkconv.m2.write import write_md20  # noqa: E402

import wing_cosmetic_pack as pilot  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SIRUS = Path(r"D:\Sirus\_client\World of Warcraft Sirus\Data")
SIRUS_DBC = SIRUS / "ruRU" / "patch-ruRU-4.mpq"
DONORS = tuple(SIRUS / name for name in (
    "patch-s.mpq", "patch-t.mpq", "patch-4.MPQ", "patch-6.MPQ", "patch-h.mpq", "patch-n.mpq",
    "patch-c.mpq", "patch-5.MPQ", "common.mpq",
))
ICON_ARCHIVES = (SIRUS / "ruRU" / "patch-ruRU-c.mpq",) + DONORS

SLUG = "wings-batch"
CLIENT = pilot.CLIENT
CLIENT_ARCHIVE = pilot.CLIENT_ARCHIVE          # PATCH-X
PILOT_EFFECT_ID = 8685                         # already shipped by wing_cosmetic_pack

EFFECT_BASE = 8300
KIT_BASE = 21000
ATTACH_BASE = 5300
VISUAL_BASE = 30200
SPELL_BASE = 970300
ICON_BASE = 515000
ATTACHMENT_ID = 16
SKILL_LINE = pilot.SKILL_LINE                  # 779 Cosmetics
DEFAULT_ICON_ID = pilot.SKILL_LINE_ICON        # 153
SPELL_TABLE_TEMPLATE = pilot.SPELL_TEMPLATE_ID # 6606 infinite dummy aura
SPELL_GROUP_ID = 9100
STACK_RULE_EXCLUSIVE_FROM_SAME_CASTER = 2

# The pilot never shipped icons; SpellIcon.dbc is 2 fields (ID, texture path).
LAYOUT = dict(pilot.DBC_LAYOUT)
LAYOUT["SpellIcon"] = (2, 8, (1,))


# The client only ever reads its effective SpellVisualEffectName / SpellVisualKit /
# SpellVisualKitModelAttach rows out of patch-Z and enUS\patch-enUS-Z.  Logs\wxl-core.log shows
# the wxl-extended-dbc mount merging continuations for Spell, SkillLine, SkillLineAbility,
# SpellVisual, SpellIcon, Vehicle and VehicleSeat, and never a "merged
# 'DBFilesClient\SpellVisualKit.dbc'" line for these three.  A PATCH-X continuation on its own
# therefore leaves the kit/attach/effect rows invisible and every spell casts with no model at all
# (only the default cast animation/effect fires).  wing_cosmetic_pack ships the pilot the same
# two-layer way, which is why the pilot is the one wing that renders.
BAKED_TABLES = ("SpellVisualEffectName", "SpellVisualKit", "SpellVisualKitModelAttach")

#: Set by a pack runner before build(): restrict discovery to these donor model paths (lowercase),
#: and feed it the names and icons the donor itself uses for those models.
ONLY_MODELS = None
NAME_OVERRIDES = {}
ICON_OVERRIDES = {}


class BatchError(RuntimeError):
    pass


def humanize(stem: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", stem))
    return " ".join(word.capitalize() if word.islower() else word for word in words) or stem


class Readers:
    """Open each donor once and read unlisted entries by name."""

    def __init__(self, storm: Storm, archives):
        self.storm = storm
        self.handles = {}
        for archive in archives:
            try:
                self.handles[archive] = storm.open_archive(archive)
            except OSError:
                self.handles[archive] = None

    def read(self, name: str) -> bytes | None:
        try:
            key = name.encode("ascii")
        except UnicodeEncodeError:
            return None
        for archive, handle in self.handles.items():
            if handle is None:
                continue
            file_handle = H()
            if not self.storm.dll.SFileOpenFileEx(handle, key, 0, c.byref(file_handle)):
                continue
            try:
                size = self.storm.dll.SFileGetFileSize(file_handle, None)
                buffer = c.create_string_buffer(size or 1)
                got = c.c_ulong(0)
                if not self.storm.dll.SFileReadFile(file_handle, buffer, size, c.byref(got), None):
                    continue
                return buffer.raw[:size]
            finally:
                self.storm.dll.SFileCloseFile(file_handle)
        return None

    def has(self, name: str) -> bool:
        return self.read(name) is not None

    def close(self):
        for handle in self.handles.values():
            if handle:
                self.storm.dll.SFileCloseArchive(handle)


def strip_particles(model: M2Model) -> bytes:
    """Drop the model's own particle emitters, keeping the mesh.

    Sirus ripped these wings off bosses, so 44 of the 127 carry the boss's emitters (smoke,
    fel fire, anima wisps).  Worn as a cosmetic they read as a stray spell effect that hangs
    around for as long as the aura is up, so only the geometry ships.
    """
    model.particles = []
    return write_md20(model)


def discover(storm: Storm, readers: Readers) -> list:
    handle = storm.open_archive(SIRUS_DBC)
    try:
        effect_names = Wdbc(storm.read(handle, "DBFilesClient\\SpellVisualEffectName.dbc"))
    finally:
        storm.dll.SFileCloseArchive(handle)
    wings, skipped, partial = [], [], []
    seen_models = set()
    for row in effect_names.rows:
        path = effect_names.text(row[2])
        # Sirus spells the folder every way round -- Item\ObjectComponents\Wings, all-caps
        # OBJECTCOMPONENTS and lowercase -- so both halves of this test have to fold case.  The
        # original mixed-case test silently dropped 636 of the 763 wing models in the donor.
        lowered = path.lower()
        if not re.search(r"wings", lowered) or not ("objectcomponents" in lowered or lowered.startswith("sirus")):
            continue
        if row[0] == PILOT_EFFECT_ID:
            continue
        model = re.sub(r"\.mdx$", ".m2", path, flags=re.I).replace("/", "\\")
        if ONLY_MODELS is not None and model.lower() not in ONLY_MODELS:
            continue
        # One spell per model.  Sirus keeps several SpellVisualEffectName rows on the same mesh
        # (different names and scales), and shipping each of them gave 616 spells over 77 models.
        if model.lower() in seen_models:
            continue
        seen_models.add(model.lower())
        skin = model[:-3] + "00.skin"
        model_bytes, skin_bytes = readers.read(model), readers.read(skin)
        if not model_bytes or not skin_bytes:
            skipped.append((row[0], path, "model/skin missing"))
            continue
        parsed = parse_m2(model_bytes)
        # Sirus's own sirus\Wings*.mdx rows ("alas02".."alas06") are one recoloured ribbon-only
        # effect: 94 verts / 486 triangles and six ribbon emitters, no wing mesh at all.  Pinned to
        # the back it reads as a swirling trail, never as wings, so it is not a cosmetic wing.
        if parsed.ribbons and parsed.vertex_count < 300:
            skipped.append((row[0], path, "ribbon-only effect, no wing mesh"))
            continue
        if parsed.particles:
            model_bytes = strip_particles(parsed)
        missing = []
        assets = {model: model_bytes, skin: skin_bytes}
        texture_names = []
        for texture in parsed.textures:
            if texture["type"] != 0 or not texture["filename"]:
                continue
            name = texture["filename"].replace("/", "\\")
            texture_names.append(name)
            blob = readers.read(name)
            if blob:
                assets[name] = blob
            else:
                missing.append(name)
        if missing and texture_names and texture_names[0].casefold() in {name.casefold() for name in missing}:
            skipped.append((row[0], path, f"base texture missing: {texture_names[0]}"))
            continue
        if missing:
            partial.append((row[0], path, missing))
        wings.append({
            "fx": row[0], "name": effect_names.text(row[1]), "path": path,
            "model": model, "assets": assets, "missing_textures": missing,
        })
    return wings, skipped, partial


def icon_for(readers: Readers, wing: dict) -> tuple:
    override = ICON_OVERRIDES.get(wing["model"].lower())
    if override:
        blob = readers.read(override)
        if blob:
            return override, blob
    stem = Path(wing["model"]).stem
    candidates = [
        f"Interface\\ICONS\\inv_{wing['name']}.blp",
        f"Interface\\ICONS\\inv_{stem}.blp",
        f"Interface\\ICONS\\inv_{re.sub(r'_wings$', '', wing['name'], flags=re.I)}_wings.blp",
    ]
    for candidate in candidates:
        blob = readers.read(candidate)
        if blob:
            return candidate, blob
    return None, None



def bake_visual_tables(storm: Storm, continuations: dict, backup_dir: Path) -> dict:
    """Merge the batch's model rows into this archive's own full copies in both Z archives."""
    written = {}
    for archive in pilot.CLIENT_Z_ARCHIVES:
        handle = storm.open_archive(archive)
        try:
            payloads, previous = {}, {}
            for table in BAKED_TABLES:
                entry = "DBFilesClient\\" + table + ".dbc"
                try:
                    base = storm.read(handle, entry)
                except OSError:
                    base = pilot.base_table(storm, table)
                previous[entry] = base
                payloads[entry] = pilot.merge_table(base, continuations[table], table)
        finally:
            storm.dll.SFileCloseArchive(handle)
        dbc_backup = backup_dir / archive.name
        dbc_backup.mkdir(parents=True, exist_ok=True)
        for entry, blob in previous.items():
            out = dbc_backup / (entry.replace("\\", "_") + ".bak")
            if not out.exists():
                out.write_bytes(blob)
        storm.replace_archive_entries(archive, payloads)
        pilot.verify_entry(storm, archive, payloads)
        written[str(archive)] = {name.split("\\")[-1]: len(blob) for name, blob in payloads.items()}
    return written


def build(apply: bool) -> int:
    storm = Storm(DLL_DEFAULT)
    readers = Readers(storm, DONORS)
    icon_readers = Readers(storm, ICON_ARCHIVES)
    try:
        wings, skipped, partial = discover(storm, readers)
        print(f"wings discovered        : {len(wings)} (+{len(skipped)} skipped, {len(partial)} partial)")
        for fx, path, why in skipped:
            print(f"   skipped {fx} {path}: {why}")

        rows = {table: [] for table in ("SpellVisualEffectName", "SpellVisualKit", "SpellVisualKitModelAttach",
                                        "SpellVisual", "Spell", "SkillLineAbility", "SpellIcon")}
        strings = {table: {} for table in rows}
        template_row = pilot.client_spell_template(storm)

        # Copy the donor's own visual rows.  A hand-built SpellVisualEffectName row loses the
        # donor's Scale (1.0 in every Sirus wing row), which renders the model at scale 0 -- the
        # pilot only worked because it copied Sirus's row wholesale.
        donor = {}
        handle = storm.open_archive(SIRUS_DBC)
        try:
            donor["fx"] = {row[0]: row for row in Wdbc(storm.read(handle, "DBFilesClient\\SpellVisualEffectName.dbc")).rows}
            donor["kit"] = {row[0]: row for row in Wdbc(storm.read(handle, "DBFilesClient\\SpellVisualKit.dbc")).rows}
            donor["visual"] = {}
            for row in Wdbc(storm.read(handle, "DBFilesClient\\SpellVisual.dbc")).rows:
                if row[4]:
                    donor["visual"].setdefault(row[4], row)
            donor["attach"] = {}
            for row in Wdbc(storm.read(handle, "DBFilesClient\\SpellVisualKitModelAttach.dbc")).rows:
                donor["attach"].setdefault(row[2], row)
        finally:
            storm.dll.SFileCloseArchive(handle)

        spell_rows, sla_rows, icon_rows = [], [], []
        names, assets, missing = {}, {}, []
        for index, wing in enumerate(wings):
            effect_id = EFFECT_BASE + index
            kit_id = KIT_BASE + index
            attach_id = ATTACH_BASE + index
            visual_id = VISUAL_BASE + index
            spell_id = SPELL_BASE + index
            name = NAME_OVERRIDES.get(wing["model"].lower()) or humanize(Path(wing["model"]).stem)
            if name in names:
                name = f"{name} {index}"
            names[name] = spell_id

            icon_path, icon_blob = icon_for(icon_readers, wing)
            icon_id = DEFAULT_ICON_ID
            if icon_path and icon_blob:
                icon_id = ICON_BASE + index
                assets[icon_path] = icon_blob
                rows["SpellIcon"].append([icon_id, 0])
                strings["SpellIcon"][(len(rows["SpellIcon"]) - 1, 1)] = icon_path

            donor_fx = donor["fx"].get(wing["fx"])
            donor_attach = donor["attach"].get(wing["fx"])
            donor_kit = donor["kit"].get(donor_attach[1]) if donor_attach else None
            donor_visual = donor["visual"].get(donor_attach[1]) if donor_attach else None
            if not (donor_fx and donor_attach and donor_kit and donor_visual):
                skipped.append((wing["fx"], wing["path"], "donor visual chain incomplete"))
                continue

            effect_row = list(donor_fx)
            effect_row[0] = effect_id
            rows["SpellVisualEffectName"].append(effect_row)
            strings["SpellVisualEffectName"][(len(rows["SpellVisualEffectName"]) - 1, 1)] = name
            strings["SpellVisualEffectName"][(len(rows["SpellVisualEffectName"]) - 1, 2)] = wing["path"]

            # Normalise the wiring the way the stock character models accept it: attachment 16
            # (the back), zero offsets, and no kit-driven animation.  Sirus authored some wings for
            # its modern character models (attachment 57, translated offsets, kit animations),
            # which on this client drops the model at the feet or plays a stray animation.
            kit_row = list(donor_kit)
            kit_row[0] = kit_id
            kit_row[1] = 0xFFFFFFFF
            kit_row[2] = 0xFFFFFFFF
            rows["SpellVisualKit"].append(kit_row)

            attach_row = list(donor_attach)
            attach_row[0] = attach_id
            attach_row[1] = kit_id
            attach_row[2] = effect_id
            for index in range(3, 10):
                attach_row[index] = ATTACHMENT_ID if index == 3 else 0
            rows["SpellVisualKitModelAttach"].append(attach_row)

            visual_row = list(donor_visual)
            visual_row[0] = visual_id
            visual_row[4] = kit_id
            rows["SpellVisual"].append(visual_row)

            spell_row = pilot.spell_row_for_pilot(template_row)
            spell_row[0] = spell_id
            spell_row[131] = visual_id
            spell_row[133] = icon_id
            rows["Spell"].append(spell_row)
            strings["Spell"][(len(rows["Spell"]) - 1, 136)] = name
            strings["Spell"][(len(rows["Spell"]) - 1, 137)] = name
            strings["Spell"][(len(rows["Spell"]) - 1, 170)] = f"Esteria cosmetic wings: {name}."
            strings["Spell"][(len(rows["Spell"]) - 1, 171)] = f"Esteria cosmetic wings: {name}."
            strings["Spell"][(len(rows["Spell"]) - 1, 187)] = f"{name} wings."
            strings["Spell"][(len(rows["Spell"]) - 1, 188)] = f"{name} wings."
            rows["SkillLineAbility"].append([spell_id, SKILL_LINE, spell_id, 0, pilot.ALL_CLASSES_MASK, 0, 0, 1, 0, 0, 0, 0, 0, 0])
            spell_rows.append(spell_row)
            sla_rows.append(rows["SkillLineAbility"][-1])
            icon_rows.append(icon_id)
            assets.update(wing["assets"])
            if wing["missing_textures"]:
                missing.append((spell_id, name, wing["missing_textures"]))

        entries = dict(assets)
        for table, table_rows in rows.items():
            if not table_rows:
                continue
            fields, record_size, _ = LAYOUT[table]
            entries[f"DBFilesClient/{table}.dbc1-{SLUG}"] = build_wdbc(table_rows, fields, record_size, strings[table])
        additions = ("# Esteria cosmetic wings batch\n"
                     + "\n".join(f"DBFilesClient/{table}.dbc1-{SLUG}" for table, value in rows.items() if value)
                     + "\n").encode("utf-8")
        entries["wxl-dbc.manifest"] = merge_wxl_manifest(pilot.read_manifest(storm, CLIENT_ARCHIVE), additions)

        print(f"spells                   : {len(spell_rows)} ({names and min(names.values())}..{max(names.values())})")
        print(f"assets                   : {len(assets)} files, {sum(len(v) for v in assets.values())/1e6:.1f} MB")
        print(f"wings with missing texture: {len(missing)}")
        for spell_id, name, textures in missing[:10]:
            print(f"   {spell_id} {name}: {textures}")

        report = {
            "wings": len(wings), "skipped": skipped, "partial": partial,
            "spell_ids": [pilot.SPELL_ID] + [row[0] for row in spell_rows],
            "names": names, "assets": len(assets),
            "sql_world": None, "sql_characters": None, "applied": False,
        }
        if not apply:
            print("\ndry run: pass --apply to write the archive, asset packs and SQL")
            return 0

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        before = pilot.sha256_file(CLIENT_ARCHIVE)
        backup_dir = CLIENT / "Backups" / f"wings-batch-{stamp}-{before[:8]}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / CLIENT_ARCHIVE.name
        if not backup.exists():
            backup.write_bytes(CLIENT_ARCHIVE.read_bytes())
        storm.replace_archive_entries(CLIENT_ARCHIVE, entries)
        pilot.verify_entry(storm, CLIENT_ARCHIVE, entries)
        print(f"full tables              : "
              f"{bake_visual_tables(storm, {table: entries['DBFilesClient/' + table + '.dbc1-' + SLUG] for table in BAKED_TABLES}, backup_dir / 'full-tables')}")
        after = pilot.sha256_file(CLIENT_ARCHIVE)
        print(f"archive                  : {before[:12]} -> {after[:12]} ({len(entries)} entries)")

        stamp = f"{datetime.now():%Y%m%d%H%M%S%f}"[:17]
        world = REPO / "data" / "sql" / "updates" / "pending_db_world" / f"rev_{stamp}.sql"
        world.write_text(world_sql(spell_rows, sla_rows, icon_rows), encoding="utf-8")
        chars = REPO / "data" / "sql" / "updates" / "pending_db_characters" / f"rev_{stamp}.sql"
        chars.write_text(characters_sql(spell_rows), encoding="utf-8")
        print(f"sql world                : {world.relative_to(REPO)}")
        print(f"sql characters           : {chars.relative_to(REPO)}")

        report.update({
            "applied": True, "archive_sha256": {"before": before, "after": after},
            "backup": str(backup_dir), "sql_world": str(world.relative_to(REPO)),
            "sql_characters": str(chars.relative_to(REPO)),
        })
        out = REPO / "var" / "wings-batch"
        out.mkdir(parents=True, exist_ok=True)
        (out / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"report                   : {(out / 'build-report.json').relative_to(REPO)}")
        return 0
    finally:
        readers.close()
        icon_readers.close()


def _q(name: str) -> str:
    return pilot.quoted(name)


def world_sql(spell_rows: list, sla_rows: list, icon_rows: list) -> str:
    from cars_mount_pack import _sql_insert
    body = _sql_insert("spell_dbc", pilot.SPELL_COLUMNS, [pilot.spell_sql_row(row) for row in spell_rows], [row[0] for row in spell_rows])
    # No server-side SkillLineAbility rows on purpose.  Line 779 is a class-category line, so
    # mod-classless-wildcard drops it on login for a Hero with nothing earned on it, and
    # Player::SetSkill(line, 0, 0, 0) unlearns every spell the server maps to that line --
    # which took every wing off every classless character on every relog.  The client keeps its
    # own SkillLineAbility.dbc (shipped in the MPQ) so the tab still lists them.
    body += "\n\n" + _sql_insert("spell_group", ("id", "spell_id"),
                                 [[SPELL_GROUP_ID, row[0]] for row in spell_rows], [SPELL_GROUP_ID], "id")
    body += ("\n\nDELETE FROM " + _q("spell_group_stack_rules") + " WHERE " + _q("group_id") + f" = {SPELL_GROUP_ID};\n"
             "INSERT INTO " + _q("spell_group_stack_rules") + " (" + _q("group_id") + ", " + _q("stack_rule") + ", "
             + _q("description") + f") VALUES ({SPELL_GROUP_ID}, {STACK_RULE_EXCLUSIVE_FROM_SAME_CASTER}, "
             "'Cosmetic wings: one at a time');\n")
    spell_values = " UNION ALL ".join(f"SELECT {row[0]} AS Spell" for row in spell_rows)
    body += ("\n\nINSERT INTO " + _q("playercreateinfo_spell_custom") + " (" + _q("racemask") + ", " + _q("classmask")
             + ", " + _q("Spell") + ", " + _q("Note") + ")\n"
             "SELECT DISTINCT p." + _q("racemask") + ", p." + _q("classmask") + ", s.Spell, 'Cosmetics'\n"
             "FROM " + _q("playercreateinfo_spell_custom") + " p CROSS JOIN (\n  " + spell_values + "\n) s;\n")
    return ("-- Esteria cosmetic wings batch (see tools/wings_cosmetic_pack.py).\n"
            "-- One exclusive spell group so enabling a wing clears the previous one.\n" + body + "\n")


def characters_sql(spell_rows: list) -> str:
    spell_values = " UNION ALL ".join(f"SELECT {row[0]} AS spell" for row in spell_rows)
    return ("-- Esteria cosmetic wings batch: grant every wing spell to every character.\n"
            "DELETE cs FROM " + _q("character_spell") + " cs JOIN (\n  " + spell_values + "\n) s ON s.spell = cs.spell;\n"
            "INSERT INTO " + _q("character_spell") + " (" + _q("guid") + ", " + _q("spell") + ", " + _q("specMask") + ")\n"
            "SELECT c." + _q("guid") + ", s.spell, 255 FROM " + _q("characters") + " c CROSS JOIN (\n  "
            + spell_values + "\n) s;\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build",))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    return build(args.apply)


if __name__ == "__main__":
    raise SystemExit(main())