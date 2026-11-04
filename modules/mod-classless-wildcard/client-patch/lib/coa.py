"""Client side of the imported Conquest of Azeroth kits.

The rows are copied out of the CoA client itself, not stored here: Spell.dbc
records byte for byte with their strings moved into the target's string block,
SpellIcon rows with the icon art they point at, and each spell's visual with
the kits, effect models, sounds and files it names. They go in an archive of
their own that sorts above every other patch, so deleting it is the rollback.

That archive must be rebuilt from the then-winning tables whenever another
patch changes one of the tables it carries; otherwise it hides that change.
"""
import os
import struct

from .elemental import _add_string, _ids, _join, _split
from .mpq import MPQArchive

# Highest name in PatchFiles.cpp's case-insensitive descending sort: 24 Zs
# beat Patch-ZZZZZZZZZZZZZZZZZZZZZZZDraconicArmor's 23.
ARCHIVE = "Patch-ZZZZZZZZZZZZZZZZZZZZZZZZCoA.MPQ"
SEP = "\\"
SPELL = "DBFilesClient" + SEP + "Spell.dbc"
SPELLICON = "DBFilesClient" + SEP + "SpellIcon.dbc"

SPELL_FIELDS = 234
SPELL_STRINGS = list(range(136, 152)) + list(range(153, 169)) + list(range(170, 186)) + list(range(187, 203))
SPELL_VISUAL = (131, 132)
SPELL_ICONS = (133, 134)
SPELL_EQUIP_INV = 70
NONE = 0xFFFFFFFF


class CoAError(Exception):
    pass


def target_archives(client):
    """Data\\patch-*.MPQ and the locale's, highest priority first (PatchFiles.cpp)."""
    data = os.path.join(client, "Data")
    found = [os.path.join(data, n) for n in os.listdir(data)
             if n.lower().startswith("patch-") and n.lower().endswith(".mpq")
             and os.path.isfile(os.path.join(data, n))]
    for loc in os.listdir(data):
        sub = os.path.join(data, loc)
        if os.path.isdir(sub) and len(loc) == 4:
            found += [os.path.join(sub, n) for n in os.listdir(sub)
                      if n.lower().startswith("patch-%s-" % loc.lower()) and n.lower().endswith(".mpq")]
    found.sort(key=lambda p: p.replace("/", SEP).lower(), reverse=True)
    # then the base archives, below every patch: a stock file found there is
    # already on the player's disk and is never copied
    base = []
    for root in [data] + [os.path.join(data, loc) for loc in os.listdir(data)
                          if os.path.isdir(os.path.join(data, loc)) and len(loc) == 4]:
        base += sorted((os.path.join(root, n) for n in os.listdir(root)
                        if n.lower().endswith(".mpq") and not n.lower().startswith("patch")
                        and os.path.isfile(os.path.join(root, n))), reverse=True)
    return found + base


def winning_file(archives, member, skip=(ARCHIVE.lower(),)):
    """(archive, bytes) of the first archive carrying `member`, ignoring our own."""
    for path in archives:
        if os.path.basename(path).lower() in skip:
            continue
        mpq = _open(path)
        if mpq.has_file(member):
            return path, mpq.read_file(member)
    return None, None


_OPEN = {}


def _open(path):
    """Archives stay open for the process: reading a big one's tables is the
    slow part, and a build looks dozens of files up across the same list."""
    if path not in _OPEN:
        _OPEN[path] = MPQArchive(path)
    return _OPEN[path]


# Spell.dbc columns that name another spell a row triggers
SPELL_TRIGGERS = (116, 117, 118)

# New spell ids for CoA spells whose own id Esteria already uses, or that two catalog entries both offer. Esteria's
# client and server reach 13990005 and CoA's own reach 13977920, so these sit above both. A clone is a copy of the
# CoA row under the new id; CLONE_REWRITE sends every trigger of CoA's rows to the clone instead of the stock spell.
CLONES = {
    14000001: 1604,      # Dazed, triggered by a Pyromancer ability
    14000002: 35764,     # Astral Armor Visual, triggered by a Starcaller ability
    14000003: 65633,     # Arcane Cast Visual, triggered by a Chronomancer ability
    14000004: 32991,     # Nature Cast Visual, triggered by a Stormbringer ability
    14000005: 503748,    # Potent Mixes rank 1, which the Witch Doctor ability line and talent both offered
    14000006: 504888,    # Potent Mixes rank 2
    14000007: 5325,      # Strength of Isha Awak, triggered by a CoA spell
    14000008: 29878,     # Instakill Self
    14000009: 50259,     # Dazed (the second stock Dazed)
    14000010: 54350,     # Cosmetic 1h Attack
    14000011: 57842,     # Killing Spree
    14000012: 59832,     # Hooked
    14000013: 42208,     # Blizzard, which CoA's Blizzard variants trigger
}
CLONE_REWRITE = {1604: 14000001, 35764: 14000002, 65633: 14000003, 32991: 14000004, 5325: 14000007, 29878: 14000008,
                 50259: 14000009, 54350: 14000010, 57842: 14000011, 59832: 14000012, 42208: 14000013}


def apply_clones(data: bytes, clones=None, rewrite=None) -> bytes:
    """CoA's Spell.dbc with the clone rows added and the triggers of every row sent to the clones."""
    clones = CLONES if clones is None else clones
    rewrite = CLONE_REWRITE if rewrite is None else rewrite
    count, fields, rec, records, strings = _split(data, SPELL_FIELDS, "CoA Spell.dbc")
    ids = _ids(records, rec, count)
    records = bytearray(records)
    for new_id, source_id in sorted(clones.items()):
        if new_id in ids:
            raise CoAError("Clone id %d is already a CoA spell" % new_id)
        row = bytearray(records[ids[source_id] * rec:(ids[source_id] + 1) * rec])
        struct.pack_into("<I", row, 0, new_id)
        records += row
        count += 1
    for offset in range(0, len(records), rec):
        for col in SPELL_TRIGGERS:
            old = struct.unpack_from("<I", records, offset + col * 4)[0]
            if old in rewrite:
                struct.pack_into("<I", records, offset + col * 4, rewrite[old])
    return _join(count, fields, rec, bytes(records), strings)


def append_spells(target: bytes, source: bytes, spell_ids, clear_equip_slot=(), visual_map=None, icon_map=None):
    """Copy CoA Spell.dbc rows into the target. Returns (bytes, added).
    `visual_map`/`icon_map` move a visual or icon to the id it was copied
    under (0 = left off); ids absent from them are kept."""
    visual_map, icon_map = visual_map or {}, icon_map or {}
    count, fields, rec, records, strings = _split(target, SPELL_FIELDS, "Spell.dbc")
    scount, _f, srec, srecords, sstrings = _split(source, SPELL_FIELDS, "CoA Spell.dbc")
    ids, sids = _ids(records, rec, count), _ids(srecords, srec, scount)
    added = 0
    for sid in spell_ids:
        if sid in ids:
            raise CoAError("Spell %d is already in the target Spell.dbc; the import never overwrites" % sid)
        if sid not in sids:
            raise CoAError("Spell %d is not in the CoA Spell.dbc" % sid)
        row = bytearray(srecords[sids[sid] * srec:(sids[sid] + 1) * srec])
        for col in SPELL_STRINGS:
            off = struct.unpack_from("<I", row, col * 4)[0]
            if off:
                text = sstrings[off:sstrings.index(b"\0", off)].decode("utf-8")
                struct.pack_into("<I", row, col * 4, _add_string(strings, text))
        for cols, mapping in ((SPELL_VISUAL, visual_map), (SPELL_ICONS, icon_map)):
            for col in cols:
                old = struct.unpack_from("<I", row, col * 4)[0]
                if old in mapping:
                    struct.pack_into("<I", row, col * 4, mapping[old])
        if sid in clear_equip_slot:
            struct.pack_into("<I", row, SPELL_EQUIP_INV * 4, 0)
        records += row
        count += 1
        added += 1
    return _join(count, fields, rec, records, strings), added


# Visual tables, 3.3.5a: field count, string columns, and which columns name
# rows of which table. A reference of 0 or 0xFFFFFFFF names nothing.
VISUAL_TABLES = {
    "SpellVisual": (32, (), {"SpellVisualKit": (1, 2, 3, 4, 5, 6, 14, 15, 22, 23, 24, 25),
                             "SpellVisualEffectName": (8,), "SoundEntries": (11, 12),
                             "SpellMissileMotion": (21,)}),
    "SpellVisualKit": (38, (), {"AnimationData": (1, 2), "SpellVisualEffectName": tuple(range(3, 15)),
                                "SoundEntries": (15,), "CameraShakes": (16,)}),
    "SpellVisualEffectName": (7, (1, 2), {}),
    "SoundEntries": (30, (2,) + tuple(range(3, 13)) + (23,), {}),
    "SpellMissileMotion": (5, (1, 2), {}),
    "CameraShakes": (8, (), {}),
}
# Animations are player-model sequences, not data to copy: a kit naming one
# this client does not know plays none (-1) rather than "Stand" (0).
REQUIRED_PRESENT = ("AnimationData",)


class Table:
    """A DBC split into an id index, records and strings, appendable in place."""

    def __init__(self, data, fields, name):
        self.name = name
        self.count, self.fields, self.rec, self.records, self.strings = _split(data, fields, name)
        self.ids = _ids(self.records, self.rec, self.count)

    def row(self, row_id):
        i = self.ids[row_id]
        return bytearray(self.records[i * self.rec:(i + 1) * self.rec])

    def text(self, off):
        return self.strings[off:self.strings.index(b"\0", off)].decode("utf-8")

    def cell(self, row_id, col):
        return struct.unpack_from("<I", self.records, self.ids[row_id] * self.rec + col * 4)[0]

    def resolved(self, row_id, string_cols):
        """The row with its strings read out, for comparing across tables."""
        row = self.row(row_id)
        cells = list(struct.unpack("<%dI" % self.fields, row))
        for col in string_cols:
            cells[col] = self.text(cells[col]).lower()
        return cells

    def append(self, row):
        self.records += row
        self.ids[struct.unpack_from("<I", row, 0)[0]] = self.count
        self.count += 1

    def data(self):
        return _join(self.count, self.fields, self.rec, self.records, self.strings)


def gameobject_displays(source, target, wanted):
    """Copy model display rows under free IDs, preserving every target row."""
    mapping, rows, models = {}, [], []
    for old in sorted(wanted):
        if old not in source.ids:
            raise CoAError("CoA GameObjectDisplayInfo has no row %d" % old)
        if old in target.ids and source.resolved(old, (1,)) == target.resolved(old, (1,)):
            mapping[old] = old
            continue
        new = old if old not in target.ids else max(max(source.ids), max(target.ids)) + 1
        mapping[old] = new
        row = source.row(old)
        model = source.text(source.cell(old, 1))
        struct.pack_into("<I", row, 0, new)
        struct.pack_into("<I", row, 4, _add_string(target.strings, model) if model else 0)
        target.append(row)
        rows.append((new, bytes(row), target))
        if model:
            models.append(model_path(model))
    return mapping, rows, models


def visual_closure(source: dict, target: dict, visual_ids):
    """Copy the visuals, and everything they name, that the target lacks.

    `source`/`target` map table name -> Table (target ones are appended to).
    A row the target has identically is reused. A row whose id the target uses
    for something else is copied under a fresh id, above both clients' ids, and
    what pointed at it follows. A reference CoA's own data cannot resolve is
    dropped. Returns ({table: rows added}, [model paths], [sound paths],
    {visual: target visual id})."""
    plan, order, taken = {}, [], {}
    todo = [("SpellVisual", v) for v in visual_ids if v not in (0, NONE)]
    while todo:
        key = todo.pop()
        name, row_id = key
        if key in plan:
            continue
        if name in REQUIRED_PRESENT:
            plan[key] = row_id if row_id in target[name].ids else NONE
            continue
        strings, refs = VISUAL_TABLES[name][1:]
        src, dst = source[name], target[name]
        if row_id not in src.ids:
            plan[key] = 0
            continue
        for ref_table, cols in refs.items():
            for col in cols:
                ref = src.cell(row_id, col)
                if ref not in (0, NONE):
                    todo.append((ref_table, ref))
        if row_id in dst.ids and dst.resolved(row_id, strings) == src.resolved(row_id, strings):
            plan[key] = row_id
            continue
        used = taken.setdefault(name, set())
        new_id = row_id
        if row_id in dst.ids or row_id in used:
            new_id = max(max(src.ids), max(dst.ids), max(used, default=0)) + 1
        used.add(new_id)
        plan[key] = new_id
        order.append(key)

    added = {name: 0 for name in VISUAL_TABLES}
    models, sounds = [], []
    for name, row_id in order:
        strings, refs = VISUAL_TABLES[name][1:]
        src, dst = source[name], target[name]
        row = src.row(row_id)
        struct.pack_into("<I", row, 0, plan[(name, row_id)])
        for ref_table, cols in refs.items():
            for col in cols:
                ref = struct.unpack_from("<I", row, col * 4)[0]
                if ref not in (0, NONE):
                    struct.pack_into("<I", row, col * 4, plan[(ref_table, ref)])
        for col in strings:
            off = struct.unpack_from("<I", row, col * 4)[0]
            text = src.text(off) if off else ""
            struct.pack_into("<I", row, col * 4, _add_string(dst.strings, text) if text else 0)
            if text and name == "SpellVisualEffectName" and col == 2:
                models.append(text)
            if text and name == "SoundEntries" and 3 <= col <= 12:
                directory = src.text(src.cell(row_id, 23))
                sounds.append(directory.rstrip(SEP) + SEP + text if directory else text)
        dst.append(row)
        added[name] += 1
    return added, models, sounds, {v: plan[("SpellVisual", v)] for v in visual_ids if ("SpellVisual", v) in plan}


def model_files(path: str, data: bytes):
    """The files a WotLK (v264) M2 needs beside itself: its skins, external
    animation files and textures. `path` is the model's own archive path."""
    base = os.path.splitext(path)[0]
    if data[:4] != b"MD20":
        raise CoAError("%s is not an MD20 model" % path)
    out = []
    n_seq, ofs_seq = struct.unpack_from("<II", data, 28)
    for i in range(n_seq):
        anim_id, variation = struct.unpack_from("<HH", data, ofs_seq + i * 64)
        flags = struct.unpack_from("<I", data, ofs_seq + i * 64 + 12)[0]
        # 0x20: data inside the model; 0x40: an alias of another sequence
        if not flags & 0x60:
            out.append("%s%04d-%02d.anim" % (base, anim_id, variation))
    n_views = struct.unpack_from("<I", data, 68)[0]
    out += ["%s%02d.skin" % (base, v) for v in range(n_views)]
    n_tex, ofs_tex = struct.unpack_from("<II", data, 80)
    for i in range(n_tex):
        kind, _flags, length, ofs = struct.unpack_from("<IIII", data, ofs_tex + i * 16)
        if kind == 0 and length > 1:
            out.append(data[ofs:ofs + length].split(b"\0")[0].decode("utf-8"))
    return out


def model_path(effect_file: str):
    """Spell effect names may say .mdx or .mdl; the client loads the .m2."""
    root, ext = os.path.splitext(effect_file)
    return root + ".m2" if ext.lower() in (".mdx", ".mdl", ".m2") else effect_file


def append_icons(target: bytes, icon_paths: dict, source_max=0):
    """Add the SpellIcon rows the target lacks. Returns (bytes, {new id: path},
    {CoA id: new id}). An id the target uses for another file is copied under
    a fresh id above both clients' (`source_max` is CoA's highest)."""
    count, fields, rec, records, strings = _split(target, 2, "SpellIcon.dbc")
    ids = _ids(records, rec, count)
    new, moved = {}, {}
    for icon_id, path in sorted(icon_paths.items(), key=lambda kv: int(kv[0])):
        icon_id = int(icon_id)
        if icon_id in ids:
            off = struct.unpack_from("<I", records, ids[icon_id] * rec + 4)[0]
            have = strings[off:strings.index(b"\0", off)].decode("utf-8")
            if have.lower() == path.lower():
                continue
            moved[icon_id] = new_id = max(max(ids), source_max) + 1
            icon_id = new_id
        records += struct.pack("<II", icon_id, _add_string(strings, path))
        ids[icon_id] = count
        count += 1
        new[icon_id] = path
    return _join(count, fields, rec, records, strings), new, moved


# Creature display tables, 3.3.5a: field count, string columns, and the column
# that names a row of another table.
CREATURE_DISPLAY = ("CreatureDisplayInfo", 16, (6, 7, 8, 9))
CREATURE_MODEL = ("CreatureModelData", 28, (2,))
# CreatureModelData columns holding floats; every other non-string cell is a signed int
CREATURE_MODEL_FLOATS = {4, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27}
CREATURE_DISPLAY_FLOATS = {4}


def creature_closure(src_display: Table, dst_display: Table, src_model: Table, dst_model: Table, display_ids):
    """Plan the creature displays, and the model rows they name, that the target lacks.

    A display the target has identically (same model, textures, scale) is reused. One whose id
    the target uses for something else is copied under a fresh id above both clients' ids, and
    what pointed at it follows; one the target lacks is copied under its own id. The same holds
    for model rows. A display CoA's own data does not define is left alone: a stock display.
    Appends to `dst_display` and `dst_model`. Returns (display map {CoA id: target id},
    [new display rows], [new model rows], [(model path, texture paths)])."""
    model_plan, new_models = {}, []
    taken_models = set()

    def plan_model(model_id):
        if model_id in model_plan:
            return model_plan[model_id]
        if model_id not in src_model.ids:
            model_plan[model_id] = model_id
            return model_id
        if model_id in dst_model.ids and dst_model.resolved(model_id, CREATURE_MODEL[2]) == \
                src_model.resolved(model_id, CREATURE_MODEL[2]):
            model_plan[model_id] = model_id
            return model_id
        new_id = model_id
        if model_id in dst_model.ids or model_id in taken_models:
            new_id = max(max(src_model.ids), max(dst_model.ids), max(taken_models, default=0)) + 1
        taken_models.add(new_id)
        model_plan[model_id] = new_id
        new_models.append((model_id, new_id))
        return new_id

    display_plan, new_displays = {}, []
    taken = set()
    for display_id in sorted(display_ids):
        if display_id not in src_display.ids:
            display_plan[display_id] = display_id
            continue
        cells = src_display.resolved(display_id, CREATURE_DISPLAY[2])
        cells[1] = plan_model(cells[1])
        if display_id in dst_display.ids and dst_display.resolved(display_id, CREATURE_DISPLAY[2]) == cells:
            display_plan[display_id] = display_id
            continue
        new_id = display_id
        if display_id in dst_display.ids or display_id in taken:
            new_id = max(max(src_display.ids), max(dst_display.ids), max(taken, default=0)) + 1
        taken.add(new_id)
        display_plan[display_id] = new_id
        new_displays.append((display_id, new_id))

    def copy(src, dst, row_id, new_id, strings, fix):
        row = src.row(row_id)
        struct.pack_into("<I", row, 0, new_id)
        for col, value in fix.items():
            struct.pack_into("<I", row, col * 4, value)
        for col in strings:
            off = struct.unpack_from("<I", row, col * 4)[0]
            text = src.text(off) if off else ""
            struct.pack_into("<I", row, col * 4, _add_string(dst.strings, text) if text else 0)
        dst.append(row)
        return bytes(row)

    model_rows, display_rows, files = [], [], []
    for old, new in new_models:
        model_rows.append((new, copy(src_model, dst_model, old, new, CREATURE_MODEL[2], {}), dst_model))
    for old, new in new_displays:
        fix = {1: model_plan[src_display.cell(old, 1)]}
        display_rows.append((new, copy(src_display, dst_display, old, new, CREATURE_DISPLAY[2], fix), dst_display))
        model = src_model.text(src_model.cell(src_display.cell(old, 1), 2)) if \
            src_display.cell(old, 1) in src_model.ids else ""
        if model:
            directory = model.rsplit(SEP, 1)[0] + SEP if SEP in model else ""
            names = [src_display.text(src_display.cell(old, col)) for col in (6, 7, 8) if src_display.cell(old, col)]
            textures = [directory + name + ".blp" for name in names if name]
            files.append((model_path(model), textures))
    return display_plan, display_rows, model_rows, files


def dbc_row_sql(name, row: bytes, table: Table, strings, floats):
    """One appended DBC record as an INSERT into the server's `<name>_dbc` table. `table` is the
    one the record was appended to: its string block holds the record's strings."""
    cells = []
    for col in range(len(row) // 4):
        if col in strings:
            off = struct.unpack_from("<I", row, col * 4)[0]
            text = table.text(off) if off else ""
            cells.append("'%s'" % text.replace("\\", "\\\\").replace("'", "''"))
        elif col in floats:
            cells.append(repr(round(struct.unpack_from("<f", row, col * 4)[0], 6)))
        else:
            cells.append(str(struct.unpack_from("<i", row, col * 4)[0]))
    return "INSERT INTO `%s_dbc` VALUES (%s);" % (name.lower(), ", ".join(cells))


# SpellItemEnchantment.dbc, 3.3.5a: 38 fields, the 16 locale names are strings
ENCHANTMENT = ("SpellItemEnchantment", 38, tuple(range(14, 30)))


def append_enchantments(src: Table, dst: Table, enchantment_ids):
    """Copy the SpellItemEnchantment rows the target lacks, under their own ids. An id the target
    has identically is kept; one it uses for something else is an error, never overwritten (CoA
    re-uses many stock ids with other meanings, so a copy under a fresh id would not be what the
    spell names). Appends to `dst`. Returns [(id, row, dst)] for the rows added."""
    added = []
    for enchantment_id in sorted(enchantment_ids):
        if enchantment_id not in src.ids:
            raise CoAError("SpellItemEnchantment %d is not in CoA's table" % enchantment_id)
        if enchantment_id in dst.ids:
            if dst.resolved(enchantment_id, ENCHANTMENT[2]) != src.resolved(enchantment_id, ENCHANTMENT[2]):
                raise CoAError("SpellItemEnchantment %d means something else in the target" % enchantment_id)
            continue
        row = src.row(enchantment_id)
        for col in ENCHANTMENT[2]:
            off = struct.unpack_from("<I", row, col * 4)[0]
            text = src.text(off) if off else ""
            struct.pack_into("<I", row, col * 4, _add_string(dst.strings, text) if text else 0)
        dst.append(row)
        added.append((enchantment_id, bytes(row), dst))
    return added
