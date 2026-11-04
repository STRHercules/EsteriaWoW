#!/usr/bin/env python3
"""Conquest of Azeroth class kits for the classless library.

Reads the CoA client's own tables and the CoA core's rank progression, and
writes three things:

  * a coverage manifest: every one of the 21 classes' advancement entries,
    what it needs from the engine, whether its spell ids are free in Esteria,
    and what this import did with it;
  * data/sql/db-world/cw_spells_coa.sql for the entries that are switched on:
    their spell rows, rank chains, the synthetic talent rows the talent grant
    path needs, and the module's own catalog tables;
  * client-patch/coa_manifest.json, which build_coa_patch.py turns into the
    client archive carrying the same spells and icons.

Nothing of CoA's is stored in the repository except what the SQL needs to run
the server: the client builder copies its rows out of the CoA client again.

Reviewed entries whose engine and script dependencies are implemented are switched on.
Every withheld entry remains in the manifest with its blocking reasons.

  python gen_coa_import.py --coa-client G:/CoAClient/Client \
      --coa-core R:/.../azerothcore-wotlk-coa --target-client "G:/3.3.5a - Dev" \
      --server-spell-dbc .../retroported-races/Spell.dbc \
      --world-spell-ids ids.txt --coverage out.json
"""
import argparse
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(MODULE, "client-patch"))
from lib import coa  # noqa: E402

SEP = "\\"

# Switched on: every candidate (stock mechanics only, ids free, nothing in the
# CoA code depends on it) that needs no other entry. The pilot pair proved the
# two shapes everything is built from: Brutal Swing, a CoA Talent whose spell
# ranks up with level, is an ability line (the rule the library applies to
# Mortal Strike); Savage Strength, ranked per point, is a talent.
PILOT_ENTRIES = (34268, 34277)

# Esteria's highest declared effect and aura (SharedDefines.h TOTAL_SPELL_EFFECTS
# and TOTAL_AURAS). Anything at or past them has no handler here.
TARGET_EFFECTS = 165
TARGET_AURAS = 317
# CoA effects and auras past stock that have a working handler in this core (ported from the CoA core). The
# tables declare every effect and aura CoA uses, so an unhandled one does not stop the server: its spell loads
# and does nothing, which is why such a spell is kept out. Auras count only where what reads them is ported too:
# 190 (apply aura to summons) has its area-aura target code; 330, 317, 319, 360 and 357 their read sites; 336,
# 340, 348 and 351 have no reader in CoA's own server either; effect 184 is only a hook target for scripts.
IMPLEMENTED_EFFECTS = {165, 166, 168, 169, 187, 171, 173, 174, 175, 176, 177, 178, 181, 183, 184, 190, 192, 193, 195, 197}
IMPLEMENTED_AURAS = {327, 328, 317, 319, 330, 333, 336, 337, 338, 340, 344, 345, 348, 350, 351, 357, 360}
# Auras that a kit's ported contracts turn into a dummy aura at load, or whose scripts hook: only in those
# families (a spell's family is its class + 6). 354 is CoA's proc-event aura; 353 is turned into a dummy by the
# Witch Doctor and Stormbringer contracts; 347 by the Barbarian, Xoroth, Necromancer, Pyromancer and Tinker ones,
# and only for a spell the ported code names.
CONVERTED_AURA_FAMILIES = {
    354: {18, 19, 20, 22, 23, 25, 26, 29, 30, 32, 33, 34, 35},
    353: {19, 22},
    347: {18, 23, 29, 30, 34},
}
CONVERTED_AURA_NAMED_ONLY = {347}
# Ranger (27) and Primalist (37) scripts hook their own aura 354 spells directly, so no contract rewrites them;
# a 354 spell is allowed there only when the ported code names its id.
NAMED_AURA_FAMILIES = {354: {27, 36, 37, 38}}
# CoA's own core leaves these auras without a handler and its kit code reads them from scripts or rewrites them at
# load (AscensionXContracts.cpp), so a spell of any kit's family carrying one is as good as CoA's when ported code
# names it or a ported script is bound to it. 337 (override spell) is read by Player::HasActiveSpell here too.
PROC_CARRIER_AURAS = {341, 347, 349, 353, 354}
KIT_FAMILIES = set(range(18, 39))
# entries that take clone ids for their rank spells (the ids are in lib/coa.py CLONES)
ENTRY_RANK_CLONES = {7131: {503748: 14000005, 504888: 14000006}}
SCRIPT_BOUND = set()   # spells CoA's SQL binds to a script the module ports (filled in main)
# one-off: Eternal Presence has family 21 but belongs to a Bloodmage entry whose script hooks aura 354
# Witch Hunter contracts dummy 354 only on Flames 803422 and Vampiric Tonic 802276
CONVERTED_AURA_SPELLS = {354: {560001, 803422, 802276}}
SPELL_MOD_AURAS = (107, 108)   # flat and percent spell modifiers
# Their op is the SpellModOp the server and the client's family tables carry (ops 0-30; 31 is CoA's own
# SPELLMOD_MAX_AURA_STACKS, kept server-side). Higher ops are read by CoA scripts only, never by the engine.
MAX_SPELLMOD_OP = 31
F_MISC_VALUE, F_CLASS_MASK = 110, 122
# Modifier spells CoA's SpellAffect.dbc names targets for: a modifier with an empty class mask is routed by that
# table (SpellInfo::SpellAffectTargets in CoA's core), which this core does not read yet.
SPELL_AFFECT_MODIFIERS = set()
STOCK_POWERS = (0, 1, 3, 0xFFFFFFFE)

# Native ids the import owns. Advancement ids are not safe talent ids, so each
# entry maps to a fixed offset of its own; tabs are per class and slot.
TALENT_ID_BASE = 100000
TAB_ID_BASE = 2000
# Spellbook tabs: one class skill line per CoA class (1000 + class: 1012-1032; stock ends at 788, the Hero line is
# 990), its SkillRaceClassInfo row, and a SkillLineAbility row per spell it files (60000-69999, clear of stock,
# elemental 22000+, forged 35000+ and the 970000s)
BOOK_LINE_BASE = 1000
BOOK_RCI_BASE = 990600
BOOK_SLA_BASE, BOOK_SLA_END = 60000, 69999
ALL_CLASSES_MASK = 0x5FF       # what the Hero tab's rows carry (client-patch/lib/dbc.py)
SKILL_CATEGORY_CLASS = 7
SKILL_RCI_FLAGS = 1040
SHARED_CLASS_TAB = 87
HIDDEN_TAB_CLASS_MASK = 2048    # bit 11: no real class, exactly as the Hero tab

# Spell.dbc 3.3.5a columns used here
F_ATTR, F_EQUIP_INV = 4, 70
F_TRIGGER, F_EFFECT, F_AURA = 116, 71, 95
F_VISUAL, F_ICON, F_ACTIVE_ICON = 131, 133, 134
F_NAME, F_POWER, F_COST, F_FAMILY = 136, 41, 42, 208
F_BONUS_MULTIPLIER = (229, 230, 231)
STRING_COLUMNS = set(range(136, 152)) | set(range(153, 169)) | set(range(170, 186)) | set(range(187, 203))
FLOAT_COLUMNS = {47, 77, 78, 79, 101, 102, 103, 119, 120, 121, 216, 217, 218, 229, 230, 231}

# Higher ranks whose own weapon subclasses contradict their slot mask; the CoA
# core clears the slot mask at load (AscensionBarbarian.cpp). Done here in the
# data, for client and server alike.
CLEAR_EQUIP_SLOT = set(range(500996, 501003)) | set(range(806905, 806909))

# Spells the CoA code names whose every mention was read and needs no port:
# Brutal Swing's ranks appear only in the slot fix above and in Relentless's
# check of which spell critted, which is Relentless's behaviour, not theirs.
# 802735-802737 are Guardian Centurion Strike ranks that ported code names as the range 802734-802738
SCRIPT_REVIEWED = {500913} | set(range(500996, 501003)) | {802735, 802736, 802737}

# Spells whose ported code is fenced off (#ifdef ESTERIA_COA_*) because it
# needs an engine feature this realm does not have yet. Entries containing
# them stay blocked under that reason until the feature lands.
UNPORTED_ENGINE = {
}

# CharacterAdvancement.dbc, the fields AscensionCoATalentData.cpp reads
CA_ID, CA_TYPE, CA_REQUIRED, CA_SPELLS = 0, 1, 2, 5
CA_AE, CA_TE, CA_LEVEL, CA_GROUP, CA_CLASS_TYPE, CA_TAB = 14, 15, 26, 29, 32, 33
CA_TAB_AE, CA_TAB_TE = 38, 39
SPEC_PRIMARY_STAT, SPEC_SIGNATURE, SPEC_IDENTITY, SPEC_NAME = 8, 24, 28, 29


class Dbc:
    def __init__(self, data):
        magic, self.n, self.fields, self.size, _ = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC":
            raise ValueError("not a WDBC table")
        self.data = data
        self.strings = data[20 + self.n * self.size:]
        self.index = {self.u(i, 0): i for i in range(self.n)}

    def u(self, row, col):
        return struct.unpack_from("<I", self.data, 20 + row * self.size + col * 4)[0]

    def s(self, row, col):
        off = self.u(row, col)
        return self.strings[off:self.strings.index(b"\0", off)].decode("utf-8", "replace")

    def raw(self, row):
        return self.data[20 + row * self.size:20 + (row + 1) * self.size]


def read_table(archives, table):
    _path, data = coa.winning_file(archives, "DBFilesClient" + SEP + table + ".dbc")
    if data is None:
        raise SystemExit("no archive carries %s.dbc" % table)
    return data


def load_progression(core):
    """{first spell: [(rank spell, level), ...]} from AscensionSpellProgressionData.h."""
    text = open(os.path.join(core, "src", "server", "coa", "AscensionSpellProgressionData.h"),
                encoding="utf-8").read()
    chains = {}
    for cls, first, spell, level in re.findall(r"\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}", text):
        chains.setdefault(int(first), []).append((int(spell), int(level)))
    for ranks in chains.values():
        ranks.sort(key=lambda r: r[1])
    return chains


# CoA files that name spells without giving them behaviour: test scenarios,
# release history, acquisition lists. A mention there blocks nothing.
INERT_FILES = re.compile(r"Contract|Changelog|Collect|Manastorm|CustomClassData|LiveBaseline|Catalog|Checkpoint")
# Generic tables carried across as data (AscensionStockCoefficients.cpp zeroes
# the listed spells' coefficients; AscensionScalingBase.cpp curves the listed
# effects' base points by level, ported as cw_coa_spell_scaling).
STOCK_COEFFICIENT_FILE = "AscensionStockCoefficientData.h"
SCALING_FILE = "AscensionScalingBaseData.h"
# "learning X also teaches Y", carried as spell_learn_spell
TAUGHT_FILE = "AscensionTaughtAbilityData.h"
# CoA code that has no meaning here (AscensionAuraAmounts is ported: it sends on 0x535, SMSG_ESTERIA_AURA_AMOUNT).
# AscensionRunePouches.cpp opens pouches of CoA's Rune of Ascension currency item, which Esteria does not have;
# the pouch item ids only collide with a few spell ids. AscensionSummonAvoidance.cpp keeps CoA summons out of
# harm's way and is ported (CoAGlue registers it); the NPC ids it lists only collide with Reaper spell ids.
# CoADungeonBossSpells.cpp is what dungeon bosses cast (its scripts act only for creature casters); the spells it
# names that a kit shares (Sun Cleric Divine Retribution) behave for a player as their data says.
NOT_APPLICABLE_FILES = {"AscensionRunePouches.cpp",
                        "AscensionSummonAvoidance.cpp", "CoADungeonBossSpells.cpp"}
# CoA files this module carries split up and rewritten rather than copied (AscensionClassMechanics.cpp became
# the 12To17, 19To25 and 26To32 slices and the CoAGlue<Class> files). A spell they name still counts as
# unported when no ported code mentions its id.
COUNTED_DATA = {"AscensionCustomResourceData.h", "AscensionTalentReplacementData.h"}
SPLIT_PORTED_FILES = {"AscensionClassMechanics.cpp", "AscensionCompat.cpp"}
# Entries of a class whose package is not ported (Felsworn, Reaper, Chronomancer, Runemaster) that only a file
# ported for another class's sake would have cleared: AscensionResourceTalents.cpp and the talent replacement
# table carry Felsworn, Reaper and Chronomancer rows whose resource service and abilities are not here.
HELD_KIT_ENTRIES = set()
PORT_DIR = os.path.join(MODULE, "src", "coa")


# A copied file alone does not establish a working class package. These packages
# have explicit registration and contract entry points in CoAGlue.cpp.
WIRED_PACKAGES = {
    "WitchHunter": "AddCoAWitchHunterPackage", "Guardian": "AddCoAGuardianPackage",
    "Ranger": "AddCoARangerPackage", "Cultist": "AddCoACultistPackage", "Primalist": "AddCoAPrimalistPackage",
}


def ported_files():
    names = {n for n in os.listdir(PORT_DIR) if n.startswith("Ascension") and n.endswith((".cpp", ".h"))}
    glue = open(os.path.join(PORT_DIR, "CoAGlue.cpp"), encoding="utf-8").read()
    for package, entry in WIRED_PACKAGES.items():
        if not re.search(r"^    " + entry + r"\(\);", glue, re.M):
            names = {n for n in names if not n.startswith("Ascension" + package)}
    return names


def script_helpers(spell):
    """Spells the ported code casts or checks by id. Nothing in the spell data
    points at most of them (an energize a talent's script casts), so without
    this they would be missing and the cast would silently do nothing."""
    out = set()
    for name in ported_files():
        text = open(os.path.join(PORT_DIR, name), encoding="utf-8", errors="replace").read()
        out.update(int(x) for x in re.findall(r"\b(\d{5,7})\b", text) if int(x) in spell.index)
    # a number in the code that happens to match a stock spell id (a creature,
    # an item) is not a helper: keep CoA's own range and class families
    return {s for s in out if (s >= 300000 or spell.u(spell.index[s], F_FAMILY) >= 18) and well_formed(spell, s)}


def well_formed(spell, sid):
    """A row whose string offsets all land inside the string block."""
    row = spell.index[sid]
    return all(spell.u(row, c) < len(spell.strings) for c in STRING_COLUMNS)


def script_bound_spells(spell, core):
    """Spells CoA's world updates bind to a script this module ports (spell_script_names). The
    script is inert without its spell; nothing in the spell data or the ported code's numbers
    reaches most of them (a spell granted by CoA's class tables, a child of a scripted spell)."""
    names = set()
    for name in os.listdir(PORT_DIR):
        if name.endswith(".cpp") and (not name.startswith("Ascension") or name in ported_files()):
            text = open(os.path.join(PORT_DIR, name), encoding="utf-8", errors="replace").read()
            names.update(re.findall(r"RegisterSpell\w*\(\s*(\w+)", text))
            names.update(re.findall(r"RegisterSpellScriptWithArgs\(\s*\w+\s*,\s*\"(\w+)\"", text))
    out = set()
    root = os.path.join(core, "data", "sql", "updates")
    for folder in ("db_world", "pending_db_world"):
        for fname in sorted(os.listdir(os.path.join(root, folder))):
            if not fname.endswith(".sql"):
                continue
            text = open(os.path.join(root, folder, fname), encoding="utf-8", errors="replace").read()
            for sid, script in re.findall(r"\(\s*(-?\d+)\s*,\s*'(\w+)'\s*\)", text):
                if script in names and abs(int(sid)) in spell.index and well_formed(spell, abs(int(sid))):
                    out.add(abs(int(sid)))
    return out


def load_taught(core):
    """[(parent spell, taught spell)] from AscensionTaughtAbilityData.h."""
    text = open(os.path.join(core, "src", "server", "coa", TAUGHT_FILE), encoding="utf-8").read()
    rows = re.findall(r"\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}", text)
    return [(int(parent), int(child)) for _cls, _spec, _lvl, parent, child in rows]


TEAM_ALLIANCE, TEAM_HORDE, TEAM_ANY = 0, 1, 2     # TeamId
BASELINE_ENTRY = 3000000000     # cw_coa_automatic entry ids of baseline rows: never a CharacterAdvancement id
# Felsworn rifts to capital cities, by the faction their SkillLineAbility.RaceMask allows (1101 Alliance,
# 690 Horde). CoA gates them by race; Esteria's Heroes include races CoA has no mask for, so they go by faction.
# 535602 (Stonard) is never granted in CoA and has no destination in AscensionFelswornData.h.
RIFT_TEAMS = {535595: TEAM_ALLIANCE, 535596: TEAM_ALLIANCE, 535597: TEAM_ALLIANCE, 535601: TEAM_ALLIANCE,
              535598: TEAM_HORDE, 535599: TEAM_HORDE, 535600: TEAM_HORDE}


def class_baseline(core):
    """[(class, level, spell, baseline, team)]: CoA's ClassSpells rows (baseline 1) and the Felsworn rifts
    (baseline 0, so they follow the automatic-entry switch): the Alliance ones are ClassSpells rows, the Horde
    ones AscensionCompat.cpp's FelswornHordeCapitalRifts."""
    coa_dir = os.path.join(core, "src", "server", "coa")
    text = open(os.path.join(coa_dir, "AscensionCustomClassData.h"), encoding="utf-8").read()
    body = re.search(r"\bClassSpells\s*=\s*\{\{(.*?)\}\};", text, re.S).group(1)
    rows = [tuple(int(x) for x in m) for m in re.findall(r"\{\s*(\d+),\s*(\d+),\s*(\d+)\s*\}", body)]
    compat = open(os.path.join(coa_dir, "AscensionCompat.cpp"), encoding="utf-8").read()
    horde = re.search(r"FelswornHordeCapitalRifts\s*=\s*\{\{(.*?)\}\};", compat, re.S).group(1)
    rows += [(14, int(level), int(sid)) for sid, level in re.findall(r"\{\s*(\d+),\s*(\d+)\s*\}", horde)]
    assert rows and all(sid in RIFT_TEAMS for _c, _l, sid in rows[-3:]), "CoA rift tables changed shape"
    return [(cls, level, sid, 0 if sid in RIFT_TEAMS else 1, RIFT_TEAMS.get(sid, TEAM_ANY))
            for cls, level, sid in rows]


def load_scripted(core):
    """Spell ids the CoA class code names, and the two generic tables.

    A spell named in class code has behaviour the data alone does not carry, so
    it is not imported without that code. Returns (scripted ids, ids whose
    coefficient CoA zeroes, {id: scaled effect mask}); the first is a dict of
    id -> the files naming it, which is the porting worklist."""
    ids = {}
    root = os.path.join(core, "src", "server", "coa")
    for name in sorted(os.listdir(root)):
        if not name.endswith((".cpp", ".h")) or "Progression" in name or INERT_FILES.search(name) \
                or name in (STOCK_COEFFICIENT_FILE, SCALING_FILE, TAUGHT_FILE) or name in ported_files() \
                or name in NOT_APPLICABLE_FILES:
            continue
        text = open(os.path.join(root, name), encoding="utf-8", errors="replace").read()
        code = ported_code_numbers() if name in SPLIT_PORTED_FILES else ()
        for x in set(re.findall(r"\b(\d{5,7})\b", text)):
            if int(x) not in code:
                ids.setdefault(int(x), []).append(name)
    stock = open(os.path.join(root, STOCK_COEFFICIENT_FILE), encoding="utf-8").read()
    stock_ids = {int(x) for x in re.findall(r"\b(\d{5,7})\b", stock.split("=", 1)[1])}
    scaling = open(os.path.join(root, SCALING_FILE), encoding="utf-8").read()
    scaled = {int(s): int(m) for s, m in re.findall(r"\{\s*(\d+),\s*(\d+)\s*\}", scaling)}
    return ids, stock_ids, scaled


def join_entries(tables):
    """The CoA core's own join (AscensionCoATalentData.cpp LoadCoATalentData)."""
    classes, ctypes, tabtypes, specs, adv = (tables[k] for k in
                                             ("ChrClasses", "CharacterAdvancementClassTypes",
                                              "CharacterAdvancementTabTypes", "ChrSpecs",
                                              "CharacterAdvancement"))
    class_token = {classes.u(r, 0): classes.s(r, 55) for r in range(classes.n)}
    class_name = {classes.u(r, 0): classes.s(r, 4) for r in range(classes.n)}
    ctype = {ctypes.u(r, 0): (ctypes.u(r, 2), ctypes.u(r, 4) != 0) for r in range(ctypes.n)}
    tab_token = {tabtypes.u(r, 0): tabtypes.s(r, 1).upper() for r in range(tabtypes.n)}
    spec_by = {}
    spec_info = {}
    for r in range(specs.n):
        sid = specs.u(r, 0)
        key = (specs.s(r, 1), specs.s(r, 2).upper())
        spec_by[key] = sid
        spec_info[sid] = dict(id=sid, token=specs.s(r, 2), name=specs.s(r, SPEC_NAME),
                              identity=specs.u(r, SPEC_IDENTITY), signature=specs.u(r, SPEC_SIGNATURE))
    entries = []
    for r in range(adv.n):
        cls, custom = ctype.get(adv.u(r, CA_CLASS_TYPE), (0, False))
        if not custom or not 12 <= cls <= 32:
            continue
        tab = adv.u(r, CA_TAB)
        spec = 0
        if tab != SHARED_CLASS_TAB:
            spec = spec_by.get((class_token[cls], tab_token.get(tab, "")))
            if spec is None:
                continue
        ranks = [adv.u(r, CA_SPELLS + i) for i in range(5) if adv.u(r, CA_SPELLS + i)]
        entries.append(dict(
            id=adv.u(r, CA_ID), cls=cls, spec=spec, tab=tab, type=adv.s(r, CA_TYPE), ranks=ranks,
            ae=adv.u(r, CA_AE), te=adv.u(r, CA_TE), level=adv.u(r, CA_LEVEL),
            requires=[adv.u(r, CA_REQUIRED + i) for i in range(3) if adv.u(r, CA_REQUIRED + i)],
            group=adv.u(r, CA_GROUP), tab_ae=adv.u(r, CA_TAB_AE), tab_te=adv.u(r, CA_TAB_TE)))
    entries.sort(key=lambda e: e["id"])
    used_specs = {e["spec"] for e in entries if e["spec"]}
    return entries, {c: class_name[c] for c in sorted({e["cls"] for e in entries})}, \
        {s: spec_info[s] for s in sorted(used_specs)}


def load_budgets(essence):
    """{class: [(level, AE, TE)]}: the essence a CoA character of that class
    has by each level (AscensionCoATalentData.cpp's CoATalentBudgets)."""
    out = {}
    for r in range(essence.n):
        cls, level = essence.u(r, 2), essence.u(r, 1)
        if not 12 <= cls <= 32 or not level or any(essence.u(r, c) for c in range(3, 7)):
            continue
        out.setdefault(cls, []).append((level, essence.u(r, 7), essence.u(r, 8)))
    for rows in out.values():
        rows.sort()
    return out


def investment_level(budgets, e):
    """CoA gates a tree entry on essence already spent in that tree. The Hero
    spends from one pool across every tree, so the gate becomes the first
    level at which a CoA character could have spent that much."""
    level = e["level"]
    need_ae, need_te = e["tab_ae"], e["tab_te"]
    if need_ae or need_te:
        reach = [lv for lv, ae, te in budgets.get(e["cls"], []) if ae >= need_ae and te >= need_te]
        level = max(level, reach[0] if reach else 80)
    return level


def closure(spell, root, chains):
    """The entry's own spells: its ranks, their level progression, and what they trigger."""
    out, todo = [], list(root)
    for first in root:
        todo += [s for s, _lvl in chains.get(first, [])]
    while todo:
        sid = todo.pop()
        if sid in out or sid not in spell.index:
            continue
        out.append(sid)
        row = spell.index[sid]
        todo += [spell.u(row, F_TRIGGER + i) for i in range(3) if spell.u(row, F_TRIGGER + i)]
    return sorted(out)


_PORTED_NUMBERS = []


def ported_numbers():
    """Every number the ported code writes: the spells it names."""
    if not _PORTED_NUMBERS:
        found = set()
        for name in ported_files():
            text = open(os.path.join(PORT_DIR, name), encoding="utf-8", errors="replace").read()
            found.update(int(x) for x in re.findall(r"\b(\d{5,7})\b", text))
        found |= ported_code_numbers()   # the CoAGlue files carry rewritten CoA code too
        _PORTED_NUMBERS.append(found)
    return _PORTED_NUMBERS[0]


def ported_code_numbers():
    """Spell ids that ported code (not the data tables) names, in src/coa and its CoAGlue files."""
    found = set()
    for name in os.listdir(PORT_DIR):
        # these tables count: CoAResourceService.cpp and CoAGlueReplacements.cpp run their rows
        if name.endswith((".cpp", ".h")) and (not name.endswith("Data.h") or name in COUNTED_DATA):
            text = open(os.path.join(PORT_DIR, name), encoding="utf-8", errors="replace").read()
            found.update(int(x) for x in re.findall(r"\b(\d{5,7})\b", text))
    return found


def load_script_bound(coa_core):
    """Spell ids that CoA's world updates bind (spell_script_names) to a script class this module registers."""
    ported = set()
    for name in ported_files():
        text = open(os.path.join(PORT_DIR, name), encoding="utf-8", errors="replace").read()
        ported.update(re.findall(r"Register(?:Spell|Aura)\w*\(\s*(\w+)", text))
    bound = set()
    root = os.path.join(coa_core, "data", "sql", "updates")
    for folder in ("db_world", "pending_db_world"):
        for name in sorted(os.listdir(os.path.join(root, folder))):
            if not name.endswith(".sql"):
                continue
            current = None
            for line in open(os.path.join(root, folder, name), encoding="utf-8", errors="replace"):
                m = re.match(r"\s*SET\s+@ScriptName\s*=\s*'(\w+)'", line, re.I)
                if m:
                    current = m.group(1)
                for sid, script in re.findall(r"\(\s*(-?\d+)\s*,\s*('\w+'|@ScriptName)\s*\)", line):
                    script = current if script == "@ScriptName" else script.strip("'")
                    if script in ported:
                        bound.add(abs(int(sid)))
    return bound


def converted_aura(spell, row, sid, aura):
    """An aura past stock that a ported kit makes work (see CONVERTED_AURA_FAMILIES)."""
    if sid in CONVERTED_AURA_SPELLS.get(aura, ()):
        return True
    if aura in PROC_CARRIER_AURAS and spell.u(row, F_FAMILY) in KIT_FAMILIES and             (sid in ported_numbers() or sid in SCRIPT_BOUND):
        return True
    if spell.u(row, F_FAMILY) in NAMED_AURA_FAMILIES.get(aura, ()):
        return sid in ported_numbers() or sid in SCRIPT_BOUND
    if spell.u(row, F_FAMILY) not in CONVERTED_AURA_FAMILIES.get(aura, ()):
        return False
    return aura not in CONVERTED_AURA_NAMED_ONLY or sid in ported_numbers()


def blockers(spell, ids, scripted):
    found = set()
    for sid in ids:
        row = spell.index[sid]
        if sid in scripted and sid not in SCRIPT_REVIEWED:
            found.add("script")
        if sid in UNPORTED_ENGINE:
            found.add("engine:" + UNPORTED_ENGINE[sid])
        for i in range(3):
            effect, aura = spell.u(row, F_EFFECT + i), spell.u(row, F_AURA + i)
            if effect in (28, 56) and spell.u(row, F_MISC_VALUE + i) in (50047, 50070, 50146, 50329, 55066):
                found.add("summon:missing-template")
            if effect >= TARGET_EFFECTS and effect not in IMPLEMENTED_EFFECTS:
                found.add("effect:%d" % effect)
            if aura >= TARGET_AURAS and aura not in IMPLEMENTED_AURAS and \
                    not converted_aura(spell, row, sid, aura):
                found.add("aura:%d" % aura)
            if aura in SPELL_MOD_AURAS:
                op = spell.u(row, F_MISC_VALUE + i)
                # an op past the engine's is read only by CoA's kit code, which rewrites or reads it by spell id
                if op > MAX_SPELLMOD_OP and not (sid in ported_numbers() or sid in SCRIPT_BOUND):
                    found.add("spellmod-op")
        # Focus costs belong to the Ranger (family 27), Runic Power costs to the Necromancer (29) and Reaper (36):
        # owning the kit makes the power type active (CoAGlueRanger.cpp, CoAGlueRunicPower.cpp)
        power, family = spell.u(row, F_POWER), spell.u(row, F_FAMILY)
        if power not in STOCK_POWERS and spell.u(row, F_COST) and not (power == 2 and family == 27) and not \
                (power == 6 and family in (29, 36)):
            found.add("power:%d" % power)
    return sorted(found)


def is_passive(spell, sid):
    return bool(spell.u(spell.index[sid], F_ATTR) & 0x40)


# spell_dbc's signed INT columns; every other INT column is UNSIGNED
SIGNED_COLUMNS = {0, 13, 15, 41, 224, 228} | set(range(52, 71)) | set(range(74, 77)) | set(range(80, 83)) \
    | set(range(110, 116))


def sql_value(col, raw):
    if col in FLOAT_COLUMNS:
        return repr(round(struct.unpack("<f", struct.pack("<I", raw))[0], 6))
    if col in SIGNED_COLUMNS:
        return str(struct.unpack("<i", struct.pack("<I", raw))[0])
    return str(raw)


def esc(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "''").replace("\r", "\\r").replace("\n", "\\n") + "'"


TEXT_LIMITS = {"Name": 100, "NameSubtext": 100, "AuraDescription": 550}


def spell_row_sql(spell, sid, columns, stock_coefficient=()):
    row = spell.index[sid]
    vals = []
    for col in range(234):
        raw = spell.u(row, col)
        if col == F_EQUIP_INV and sid in CLEAR_EQUIP_SLOT:
            raw = 0
        if col in F_BONUS_MULTIPLIER and sid in stock_coefficient:
            raw = 0                        # CoA zeroes these at load (AscensionStockCoefficients.cpp)
        if col in (F_VISUAL, F_VISUAL + 1):
            raw = 0                        # drawn by the client only; build_coa_patch.py carries them
        if col in STRING_COLUMNS:
            # spell_dbc keeps names to 100 characters and aura text to 550, where the client table holds more
            limit = TEXT_LIMITS.get(columns[col].rsplit("_Lang_", 1)[0], 0)
            text = spell.s(row, col) if raw else ""
            vals.append(esc(text[:limit] if limit else text) if raw else "''")
        else:
            vals.append(sql_value(col, raw))
    return "(" + ", ".join(vals) + ")"


def spell_columns():
    text = open(os.path.join(MODULE, "data", "sql", "db-world", "cw_spells_forged.sql"), encoding="utf-8").read()
    cols = re.search(r"INSERT INTO `spell_dbc` \(([^)]*)\)", text).group(1)
    names = [c.strip(" `\n") for c in cols.split(",")]
    assert len(names) == 234, len(names)
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coa-client", required=True)
    ap.add_argument("--coa-core", required=True)
    ap.add_argument("--target-client", required=True)
    ap.add_argument("--server-spell-dbc", required=True)
    ap.add_argument("--world-spell-ids", required=True,
                    help="one spell_dbc ID per line from the target world database")
    ap.add_argument("--coverage", required=True, help="where to write the coverage manifest")
    args = ap.parse_args()

    source = coa.target_archives(args.coa_client)
    tables = {t: Dbc(read_table(source, t))
              for t in ("ChrClasses", "CharacterAdvancementClassTypes", "CharacterAdvancementTabTypes",
                        "ChrSpecs", "CharacterAdvancement")}
    # clone rows for the CoA spells whose id Esteria already uses or that two entries both offer (lib/coa.py)
    spell = Dbc(coa.apply_clones(read_table(source, "Spell")))
    affect = Dbc(read_table(source, "SpellAffect"))
    SPELL_AFFECT_MODIFIERS.update(affect.u(r, 1) for r in range(affect.n))
    # Only these exact Cultist event/driver records and Guardian records are dummied by their contracts.
    cultist_data = open(os.path.join(PORT_DIR, "AscensionCultistData.h"), encoding="utf-8").read()
    cultist_proc = set()
    for name in ("CultistEvents", "CultistDrivers"):
        body = re.search(name + r"\[\]\s*=\s*\{([^}]+)\}", cultist_data).group(1)
        cultist_proc.update(int(value) for value in re.findall(r"\d+", body))
    for aura in (353, 354):
        CONVERTED_AURA_SPELLS.setdefault(aura, set()).update(cultist_proc)
    SCRIPT_BOUND.update(load_script_bound(args.coa_core))
    CONVERTED_AURA_SPELLS[354].update({706807, 705379, 524694, 804891, 801778})
    icons = Dbc(read_table(source, "SpellIcon"))
    entries, class_names, specs = join_entries(tables)
    for e in entries:
        # the Witch Doctor talent and ability line offered the same two spells: the talent takes the clones
        if e["id"] in ENTRY_RANK_CLONES:
            e["ranks"] = [ENTRY_RANK_CLONES[e["id"]].get(r, r) for r in e["ranks"]]
    assert len(class_names) == 21, len(class_names)
    assert len(specs) == 70, len(specs)
    assert len(entries) == 3616, len(entries)

    budgets = load_budgets(Dbc(read_table(source, "CharacterAdvancementEssence")))
    chains = load_progression(args.coa_core)
    scripted, stock_coefficient, scaled = load_scripted(args.coa_core)

    tgt_client = set(Dbc(read_table(coa.target_archives(args.target_client), "Spell")).index)
    tgt_server = set(Dbc(open(args.server_spell_dbc, "rb").read()).index)
    tgt_world = {int(x) for x in open(args.world_spell_ids).read().split() if x.strip()}

    coverage = []
    pilot = []
    for e in entries:
        ids = closure(spell, e["ranks"], chains)
        occupied = sorted(set(ids) & (tgt_client | tgt_server | tgt_world))
        found = blockers(spell, ids, scripted)
        if e["id"] in HELD_KIT_ENTRIES:
            found = sorted(set(found) | {"kit:unported"})
        # an entry that costs nothing and sits in a group is one of a free choice (pick one, the others go);
        # one that costs nothing and is in no group is granted automatically
        e["free"] = bool(not e["ae"] and not e["te"] and e["group"])
        if not e["ae"] and not e["te"] and not e["group"]:
            disposition = "support"
        elif occupied:
            disposition = "id-collision"
        elif found:
            disposition = "blocked"
        else:
            disposition = "candidate"
        if e["id"] in PILOT_ENTRIES and disposition != "candidate":
            raise SystemExit("pilot entry %d is %s: %s %s" % (e["id"], disposition, found, occupied))
        if disposition == "candidate":
            disposition = "enabled"
        if disposition == "enabled":
            e["req_level"] = investment_level(budgets, e)
            pilot.append((e, ids))
        named_in = sorted({f for sid in ids if sid not in SCRIPT_REVIEWED for f in scripted.get(sid, [])})
        coverage.append(dict(e, spells=ids, blockers=found, occupied=occupied, disposition=disposition,
                             named_in=named_in,
                             progression=[list(r) for r in chains.get(e["ranks"][0], [])] if e["ranks"] else []))

    # CoA entries need up to three others, all of them owned. A required entry that is itself offered counts, and
    # so does an automatic one (a specialisation's signature ability), which the module grants once the Hero owns
    # something of that specialisation; a required entry that is blocked or held takes its dependants with it.
    disp = {c["id"]: c["disposition"] for c in coverage}
    # an automatic entry is only a usable prerequisite when nothing blocks its own spells
    unblocked_support = {c["id"] for c in coverage if c["disposition"] == "support" and not c["blockers"]}
    changed = True
    while changed:
        changed = False
        for c in coverage:
            if c["disposition"] == "enabled" and c["requires"] and                     not all(disp.get(r) == "enabled" or r in unblocked_support for r in c["requires"]):
                c["disposition"] = disp[c["id"]] = "needs-prerequisite"
                changed = True
    held = {i for i, d in disp.items() if d == "needs-prerequisite"}
    pilot = [(e, ids) for e, ids in pilot if e["id"] not in held]
    # Automatic entries (cost nothing, in no choice group): CoA grants them with the class and specialisation
    # once the level and the entries they require are there. A Hero gets them with the specialisation the same way
    # (cw_coa_automatic), and the entries that require one (a specialisation's signature ability) find it granted.
    automatic_entries = {c["id"] for c in coverage if c["id"] in unblocked_support and
                         all(r in unblocked_support or disp.get(r) == "enabled" for r in c["requires"])}

    # Two entries whose own rank spells overlap (a talent whose rank 1 is also an
    # ability) cannot both be owned apart: one would hand out or take away the
    # other's spell. Both wait for a decision. Shared helper spells are fine.
    root_owner = {}
    for e, _ids in pilot:
        for sid in e["ranks"]:
            root_owner.setdefault(sid, []).append(e["id"])
    shared = {i for owners in root_owner.values() if len(owners) > 1 for i in owners}
    pilot = [(e, ids) for e, ids in pilot if e["id"] not in shared]
    for c in coverage:
        if c["id"] in shared:
            c["disposition"] = "shared-root"

    # Spells nothing in the data reaches: what the ported code casts by id, and
    # what an owned spell teaches. They ride along as support, never picked.
    enabled_spells = {sid for _e, ids in pilot for sid in ids}
    extra = set()
    # (entry, class, spec, spell, level, requires, baseline, team): an automatic entry's ranks
    signatures = []
    for e in entries:
        if e["id"] in automatic_entries and e["ranks"]:
            first = e["ranks"][0]
            level = max(e["level"], spell.u(spell.index[first], 39), 1)
            for sid, lvl in [(first, level)] + [(s, l) for s, l in chains.get(first, [])]:
                signatures.append((e["id"], e["cls"], e["spec"], sid, max(lvl, 1),
                                   " ".join(str(r) for r in e["requires"]), 0, TEAM_ANY))
                extra.update(closure(spell, [sid], {}))
    for sid in script_helpers(spell) | script_bound_spells(spell, args.coa_core):
        extra.update(closure(spell, [sid], {}))
    taught = [(p, c) for p, c in load_taught(args.coa_core) if p in enabled_spells and c in spell.index]
    for _p, c in taught:
        extra.update(closure(spell, [c], chains))
    taken = tgt_client | tgt_server | tgt_world
    # CoA's class baseline (AscensionCustomClassData.h ClassSpells) and the Felsworn capital rifts, granted with
    # the class (spec 0) like the automatic entries above. Left out: ids Esteria already has (stock Dodge, Block,
    # ...: Esteria's own), spells a sold entry or a taught spell owns (the sync would take away a bought spell).
    taught_children = {c for _p, c in load_taught(args.coa_core)}
    baseline_count = 0
    for i, (cls, level, sid, baseline, team) in enumerate(class_baseline(args.coa_core)):
        ranks = [(sid, level)] + [(s, max(l, level)) for s, l in chains.get(sid, [])]
        # also left out: a row with broken strings, or an effect/aura past this core's range (SpellMgr asserts)
        if any(s not in spell.index or s in taken or s in enabled_spells or s in taught_children or
               not well_formed(spell, s) or any(b.startswith(("effect:", "aura:")) for b in blockers(spell, [s], {}))
               for s, _l in ranks):
            continue
        for s, lvl in ranks:
            signatures.append((BASELINE_ENTRY + i, cls, 0, s, max(lvl, 1), "", baseline, team))
            extra.update(t for t in closure(spell, [s], {}) if well_formed(spell, t))
        baseline_count += 1
    print("class baseline: %d of the ClassSpells rows and rifts granted with their class" % baseline_count)
    clash = sorted(s for s in extra - enabled_spells if s in taken)
    for s_ in clash:
        print("  clash %d: %s" % (s_, spell.s(spell.index[s_], F_NAME)))
    extra -= enabled_spells | taken
    # An effect or aura past this core's range is not just unhandled: SpellMgr
    # asserts on it at load and the worldserver does not start.
    beyond = {s for s in extra
              if any(b.startswith(("effect:", "aura:")) for b in blockers(spell, [s], {}))}
    extra -= beyond
    if beyond:
        print("support spells left out for effects/auras this core lacks: %d" % len(beyond))
        for s_ in sorted(beyond):
            print("  left out %d: %s" % (s_, ",".join(blockers(spell, [s_], {}))))
    print("support spells: %d from ported code and taught abilities, %d left out (id in use here)"
          % (len(extra), len(clash)))

    counts = {}
    for c in coverage:
        counts[c["disposition"]] = counts.get(c["disposition"], 0) + 1
    with open(args.coverage, "w", encoding="utf-8") as out:
        json.dump(dict(classes=class_names, specs=specs, counts=counts, entries=coverage), out, indent=1)
    print("coverage:", counts)

    class_specs = {}
    for e in entries:
        if e["spec"]:
            class_specs.setdefault(e["cls"], set()).add(e["spec"])
    # Spells a description names only for a number ($653216h, $500022s1, @s:...): the client needs their rows to
    # print the tooltip; the server never casts them, so they go to the client patch alone
    text_spells = text_references(spell, {sid for _e, ids in pilot for sid in ids} | extra, taken)
    print("text-only spells (client patch only): %d" % len(text_spells))
    write_outputs(spell, icons, pilot, class_names, specs, {c: sorted(s) for c, s in class_specs.items()}, chains,
                  stock_coefficient, scaled, extra, taught, source, affect, args.coa_core, signatures, text_spells)


def kind_of(spell, e, chains):
    """0 ability line, 1 talent. A line that ranks up with level, or anything
    castable, is an ability; a passive ranked per point is a talent."""
    first = e["ranks"][0]
    if e["type"] == "Ability" or chains.get(first) or not is_passive(spell, first):
        return 0
    return 1


TEXT_REFERENCE = re.compile(r"\$(\d+)[a-zA-Z]|@[sa]:(\d+):")


def text_references(spell, shipped, taken):
    """Spells the shipped descriptions name ($653216h, $500022s1, @s:1257670:0@), and the ones those name in turn,
    that neither the import nor this realm already has."""
    found, todo = set(), list(shipped)
    while todo:
        row = spell.index[todo.pop()]
        for m in TEXT_REFERENCE.finditer(spell.s(row, 170) + " " + spell.s(row, 187)):
            ref = int(m.group(1) or m.group(2))
            if ref in shipped or ref in found or ref in taken or ref not in spell.index or not well_formed(spell, ref):
                continue
            found.add(ref)
            todo.append(ref)
    return sorted(found)


def spellbook_tabs(spell, pilot, chains, signatures, taught, imported, class_names):
    """([line], [SkillLineAbility row]): a class skill line per CoA class and a row per spell it files, so the
    spellbook shows a Venomancer tab rather than putting everything under General. Every rank of a line (the next
    one supersedes it, so the book shows the highest), a talent's own castable spells, what CoA hands out with the
    class, and what learning one of those also teaches. Hidden spells get none, like the stock tables."""
    owner, chain_of = {}, []
    for e, _ids in pilot:
        if kind_of(spell, e, chains) == 0:
            chain_of.append((e["cls"], [e["ranks"][0]] + [s for s, _lvl in chains.get(e["ranks"][0], [])]))
        else:
            chain_of += [(e["cls"], [s]) for s in e["ranks"] if s and not is_passive(spell, s)]
    automatic = {}
    for entry, cls, _spec, sid, level, *_rest in sorted(signatures, key=lambda r: (r[0], r[4])):
        automatic.setdefault((entry, cls), []).append(sid)
    chain_of += [(cls, ranks) for (_entry, cls), ranks in automatic.items()]
    superseded = {}
    for cls, ranks in chain_of:
        ranks = [s for s in ranks if s in imported]
        for n, sid in enumerate(ranks):
            owner.setdefault(sid, cls)
            if n + 1 < len(ranks):
                superseded.setdefault(sid, ranks[n + 1])
    for parent, child in taught:
        if parent in owner and child in imported:
            owner.setdefault(child, owner[parent])
    visible = sorted(s for s in owner if not spell.u(spell.index[s], F_ATTR) & 0x80)     # SPELL_ATTR0_DO_NOT_DISPLAY
    assert BOOK_SLA_BASE + len(visible) <= BOOK_SLA_END, "the spellbook rows outgrew their id block"
    classes = sorted({owner[s] for s in visible})
    lines = [dict(id=BOOK_LINE_BASE + c, rci=BOOK_RCI_BASE + c, cls=c, name=class_names[c],
                  icon_spell=next(e["ranks"][0] for e, _ids in pilot if e["cls"] == c)) for c in classes]
    rows = [[BOOK_SLA_BASE + n, BOOK_LINE_BASE + owner[s], s, 0, ALL_CLASSES_MASK, 0, 0, 1, superseded.get(s, 0),
             0, 0, 0, 0, 0] for n, s in enumerate(visible)]
    return lines, rows


def write_outputs(spell, icons, pilot, class_names, specs, class_specs, chains, stock_coefficient, scaled,
                  extra, taught, source, affect, core, signatures=(), text_spells=()):
    columns = spell_columns()
    tabs = {}           # synthetic tab id -> (class, spec)
    rows, ranks, talents, catalog, icon_ids, emitted = [], [], [], [], set(), set()
    for e, ids in pilot:
        cls, kind = e["cls"], kind_of(spell, e, chains)
        # slot 0 is the class-wide tree, 1-4 the specs in id order
        slot = 0 if not e["spec"] else 1 + class_specs[cls].index(e["spec"])
        tab_id = TAB_ID_BASE + cls * 10 + slot
        first = e["ranks"][0]
        # talents open with talent essence at 10; a line at its rank 1 spell level
        req_level = max(e["req_level"], 10 if kind else spell.u(spell.index[first], 39), 1)
        if kind:
            tabs[tab_id] = (cls, e["spec"])
        for sid in ids:
            if sid in emitted:
                continue                   # a helper another entry also triggers
            emitted.add(sid)
            rows.append(spell_row_sql(spell, sid, columns, stock_coefficient))
            row = spell.index[sid]
            icon_ids.update(i for i in (spell.u(row, F_ICON), spell.u(row, F_ACTIVE_ICON)) if i)
        talent_id = 0
        if kind == 0:
            chain = [(first, req_level)] + chains.get(first, [])
            for n, (sid, _lvl) in enumerate(chain, 1):
                ranks.append("(%d, %d, %d)" % (first, sid, n))
        else:
            talent_id = TALENT_ID_BASE + e["id"]
            rank_spells = (e["ranks"] + [0] * 9)[:9]
            row_tier = max(0, (req_level - 10) // 5)
            # prerequisites stay in cw_coa_entries: the native row holds one, CoA up to three
            talents.append("(%d, %d, %d, 0, %s, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)"
                           % (talent_id, tab_id, row_tier, ", ".join(str(s) for s in rank_spells)))
        catalog.append("(%d, %d, %d, %d, %d, %d, %d, %d, '%s', 0, 1, %d, %d)" % (
            e["id"], cls, e["spec"], tab_id, kind, first if kind == 0 else 0, talent_id, req_level,
            " ".join(str(r) for r in e["requires"]), e["group"] if e.get("free") else 0, 1 if e.get("free") else 0))

    for sid in sorted(extra):
        if sid not in emitted:
            emitted.add(sid)
            rows.append(spell_row_sql(spell, sid, columns, stock_coefficient))
            row = spell.index[sid]
            icon_ids.update(i for i in (spell.u(row, F_ICON), spell.u(row, F_ACTIVE_ICON)) if i)

    spell_ids = sorted({sid for _e, ids in pilot for sid in ids} | extra)
    for sid in text_spells:     # their icons show beside the spell the text embeds
        row = spell.index[sid]
        icon_ids.update(i for i in (spell.u(row, F_ICON), spell.u(row, F_ACTIVE_ICON)) if i)
    out = os.path.join(MODULE, "data", "sql", "db-world", "cw_spells_coa.sql")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(SQL_HEAD)
        f.write("DELETE FROM `cw_coa_classes`;\n")
        f.write("INSERT INTO `cw_coa_classes` (`class`, `name`, `icon_spell`) VALUES\n")
        used = sorted({e["cls"] for e, _ids in pilot})
        f.write(",\n".join("(%d, %s, %d)" % (c, esc(class_names[c]), next(
            e["ranks"][0] for e, _ids in pilot if e["cls"] == c)) for c in used) + ";\n\n")
        f.write("DELETE FROM `cw_coa_tabs`;\n")
        f.write("INSERT INTO `cw_coa_tabs` (`tab_id`, `class`, `spec`, `name`) VALUES\n")
        f.write(",\n".join("(%d, %d, %d, %s)" % (t, c, s, esc(specs[s]["name"] if s else class_names[c]))
                           for t, (c, s) in sorted(tabs.items())) + ";\n\n")
        f.write("DELETE FROM `cw_coa_entries`;\n")
        f.write("INSERT INTO `cw_coa_entries` (`entry`, `class`, `spec`, `tab_id`, `kind`, `first_spell`, "
                "`talent_id`, `req_level`, `requires`, `in_pool`, `enabled`, `choice_group`, `free`) VALUES\n")
        f.write(",\n".join(catalog) + ";\n\n")
        id_list = ", ".join(str(s) for s in spell_ids)
        f.write("DELETE FROM `spell_dbc` WHERE `ID` IN (%s);\n" % id_list)
        f.write("INSERT INTO `spell_dbc` (%s) VALUES\n" % ", ".join("`%s`" % c for c in columns))
        f.write(",\n".join(rows) + ";\n\n")
        if ranks:
            firsts = ", ".join(sorted({r.split(",")[0][1:] for r in ranks}))
            f.write("DELETE FROM `spell_ranks` WHERE `first_spell_id` IN (%s);\n" % firsts)
            f.write("INSERT INTO `spell_ranks` (`first_spell_id`, `spell_id`, `rank`) VALUES\n")
            f.write(",\n".join(ranks) + ";\n\n")
        f.write("DELETE FROM `talenttab_dbc` WHERE `ID` BETWEEN %d AND %d;\n" % (TAB_ID_BASE, TAB_ID_BASE + 330))
        f.write("INSERT INTO `talenttab_dbc` (`ID`, `Name_Lang_enUS`, `Name_Lang_Mask`, `SpellIconID`, `RaceMask`, "
                "`ClassMask`, `PetTalentMask`, `OrderIndex`, `BackgroundFile`) VALUES\n")
        f.write(",\n".join("(%d, %s, 16712190, 0, 0, %d, 0, %d, '')" % (
            t, esc(specs[s]["name"] if s else class_names[c]), HIDDEN_TAB_CLASS_MASK, t % 10)
            for t, (c, s) in sorted(tabs.items())) + ";\n\n")
        f.write("DELETE FROM `talent_dbc` WHERE `ID` BETWEEN %d AND %d;\n" % (TALENT_ID_BASE, TALENT_ID_BASE + 99999))
        if talents:
            f.write("INSERT INTO `talent_dbc` (`ID`, `TabID`, `TierID`, `ColumnIndex`, `SpellRank_1`, "
                    "`SpellRank_2`, `SpellRank_3`, `SpellRank_4`, `SpellRank_5`, `SpellRank_6`, `SpellRank_7`, "
                    "`SpellRank_8`, `SpellRank_9`, `PrereqTalent_1`, `PrereqTalent_2`, `PrereqTalent_3`, "
                    "`PrereqRank_1`, `PrereqRank_2`, `PrereqRank_3`, `Flags`, `RequiredSpellID`, "
                    "`CategoryMask_1`, `CategoryMask_2`) VALUES\n")
            f.write(",\n".join(talents) + ";\n")
        f.write("\nDELETE FROM `cw_coa_taught`;\n")
        if taught:
            f.write("INSERT INTO `cw_coa_taught` (`parent`, `spell`) VALUES\n")
            f.write(",\n".join("(%d, %d)" % row for row in sorted(set(taught))) + ";\n")
        f.write("\nDELETE FROM `cw_coa_automatic`;\n")
        if signatures:
            f.write("INSERT INTO `cw_coa_automatic` (`entry`, `class`, `spec`, `spell`, `req_level`, `requires`, "
                    "`baseline`, `team`) VALUES\n")
            f.write(",\n".join("(%d, %d, %d, %d, %d, '%s', %d, %d)" % row for row in sorted(set(signatures))) + ";\n")
        scaling = [(sid, scaled[sid]) for sid in spell_ids if sid in scaled]
        f.write("\nDELETE FROM `cw_coa_spell_scaling`;\n")
        if scaling:
            f.write("INSERT INTO `cw_coa_spell_scaling` (`spell`, `effect_mask`) VALUES\n")
            f.write(",\n".join("(%d, %d)" % row for row in scaling) + ";\n")
    print("wrote", out, len(spell_ids), "spell rows,", len(scaling), "level-scaled")

    sys.path.insert(0, os.path.join(MODULE, "tools"))
    from coa_spell_affect import imported_targets, client_targets, write_header as write_affect_header
    from coa_spell_charges import charge_rows, write_header as write_charge_header
    affect_rows = imported_targets(affect.data, spell.data, set(spell_ids))
    write_affect_header(os.path.join(PORT_DIR, "CoASpellAffectData.h"), affect_rows)
    progression = open(os.path.join(core, "src", "server", "coa",
                                   "AscensionSpellProgressionData.h"), encoding="utf-8").read()
    charges = charge_rows(read_table(source, "SpellCharges"), read_table(source, "SpellChargesCategory"),
                          set(spell_ids), progression)
    write_charge_header(os.path.join(PORT_DIR, "CoASpellChargesData.h"), charges)
    # Spells whose tooltip shows a live aura amount ($w1..$w3, CoA's client extension): the server sends their
    # amounts (SMSG_ESTERIA_AURA_AMOUNT) and nothing else's.
    amount_spells = sorted(sid for sid in spell_ids if re.search(
        r"\$[wW][1-3]", spell.s(spell.index[sid], 170) + spell.s(spell.index[sid], 187)))
    with open(os.path.join(PORT_DIR, "CoAAuraAmountSpells.h"), "w", encoding="utf-8", newline="\n") as h:
        h.write("// Generated by gen_coa_import.py; do not edit.\n#ifndef CW_COA_AURA_AMOUNT_SPELLS_H\n"
                "#define CW_COA_AURA_AMOUNT_SPELLS_H\n\n#include <array>\n#include <cstdint>\n\n"
                "// sorted: imported spells whose tooltip names a live aura amount ($w1..$w3)\n"
                "inline constexpr std::array<uint32_t, %d> CoAAuraAmountSpells = {{\n" % len(amount_spells))
        h.write("".join("    %d,\n" % sid for sid in amount_spells) + "}};\n\n#endif\n")
    print("aura amount spells:", len(amount_spells))

    book_lines, book_rows = spellbook_tabs(spell, pilot, chains, signatures, taught, set(spell_ids), class_names)
    with open(out, "a", encoding="utf-8", newline="\n") as f:
        f.write("\n-- Spellbook tabs: a class skill line per CoA class (spells filed under Venomancer, ...)\n")
        f.write("DELETE FROM `skillline_dbc` WHERE `ID` BETWEEN %d AND %d;\n" % (BOOK_LINE_BASE, BOOK_LINE_BASE + 255))
        f.write("INSERT INTO `skillline_dbc` (`ID`, `CategoryID`, `SkillCostsID`, `DisplayName_Lang_enUS`, "
                "`Description_Lang_enUS`, `SpellIconID`, `AlternateVerb_Lang_enUS`, `CanLink`) VALUES\n")
        f.write(",\n".join("(%d, %d, 0, %s, '', %d, '', 0)" % (l["id"], SKILL_CATEGORY_CLASS, esc(l["name"]),
                                                                spell.u(spell.index[l["icon_spell"]], F_ICON))
                           for l in book_lines) + ";\n")
        f.write("DELETE FROM `skillraceclassinfo_dbc` WHERE `ID` BETWEEN %d AND %d;\n"
                % (BOOK_RCI_BASE, BOOK_RCI_BASE + 99))
        f.write("INSERT INTO `skillraceclassinfo_dbc` (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, "
                "`MinLevel`, `SkillTierID`, `SkillCostIndex`) VALUES\n")
        f.write(",\n".join("(%d, %d, 0, 0, %d, 0, 0, 0)" % (l["rci"], l["id"], SKILL_RCI_FLAGS)
                           for l in book_lines) + ";\n")
        f.write("DELETE FROM `skilllineability_dbc` WHERE `ID` BETWEEN %d AND %d;\n" % (BOOK_SLA_BASE, BOOK_SLA_END))
        f.write("INSERT INTO `skilllineability_dbc` (`ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, "
                "`ExcludeRace`, `ExcludeClass`, `MinSkillLineRank`, `SupercededBySpell`, `AcquireMethod`, "
                "`TrivialSkillLineRankHigh`, `TrivialSkillLineRankLow`, `CharacterPoints_1`, `CharacterPoints_2`) "
                "VALUES\n")
        f.write(",\n".join("(%s)" % ", ".join(str(v) for v in row) for row in book_rows) + ";\n")
    print("spellbook tabs: %d class lines, %d spells filed" % (len(book_lines), len(book_rows)))

    creatures = {spell.u(spell.index[sid], 110 + i) for sid in spell_ids for i in range(3)
                 if spell.u(spell.index[sid], 71 + i) in (28, 56)} - {0}
    objects = {spell.u(spell.index[sid], 110 + i) for sid in spell_ids for i in range(3)
               if spell.u(spell.index[sid], 71 + i) in (50, 76, 104, 105, 106, 107)} - {0}
    manifest = dict(version=1, client_power_overrides={802629: 3}, spell_affect=client_targets(affect_rows, chains), charges=charges, summoned_creatures=sorted(creatures),
                    summoned_objects=sorted(objects), spells=spell_ids, clear_equip_slot=sorted(set(spell_ids) & CLEAR_EQUIP_SLOT),
                    icons=sorted(icon_ids), icon_paths={i: icons.s(icons.index[i], 1) for i in sorted(icon_ids)
                                                        if i in icons.index},
                    spellbook=dict(lines=book_lines, sla=book_rows), text_spells=list(text_spells))
    with open(os.path.join(MODULE, "client-patch", "coa_manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=1)
        f.write("\n")


SQL_HEAD = """-- mod-classless-wildcard: Conquest of Azeroth class kits, generated by
-- data/sql/generators/gen_coa_import.py. Do not hand-edit.
-- Requires a worldserver restart.

CREATE TABLE IF NOT EXISTS `cw_coa_classes` (
  `class` TINYINT UNSIGNED NOT NULL COMMENT 'CoA class id, 12-32',
  `name` VARCHAR(32) NOT NULL,
  `icon_spell` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'spell whose icon the browser shows',
  PRIMARY KEY (`class`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Classless CoA catalog classes';

CREATE TABLE IF NOT EXISTS `cw_coa_tabs` (
  `tab_id` INT UNSIGNED NOT NULL COMMENT 'talenttab_dbc id',
  `class` TINYINT UNSIGNED NOT NULL,
  `spec` SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'CoA ChrSpecs id, 0 = class-wide',
  `name` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`tab_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Classless CoA catalog trees';

DROP TABLE IF EXISTS `cw_coa_entries`;
CREATE TABLE `cw_coa_entries` (
  `entry` INT UNSIGNED NOT NULL COMMENT 'CoA CharacterAdvancement id',
  `class` TINYINT UNSIGNED NOT NULL,
  `spec` SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  `tab_id` INT UNSIGNED NOT NULL,
  `kind` TINYINT UNSIGNED NOT NULL COMMENT '0 ability line, 1 talent',
  `first_spell` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'ability: rank 1',
  `talent_id` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'talent: talent_dbc id',
  `req_level` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `requires` VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'CoA entry ids, space separated',
  `in_pool` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Wildcard can roll it',
  `enabled` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `choice_group` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'CoA choice group: owning one removes the others',
  `free` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'a free choice: costs no essence',
  PRIMARY KEY (`entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Classless CoA catalog entries';

DROP TABLE IF EXISTS `cw_coa_signatures`;
DROP TABLE IF EXISTS `cw_coa_automatic`;
CREATE TABLE `cw_coa_automatic` (
  `entry` INT UNSIGNED NOT NULL COMMENT 'CoA CharacterAdvancement id of the automatic entry',
  `class` TINYINT UNSIGNED NOT NULL,
  `spec` SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 = granted with the class',
  `spell` INT UNSIGNED NOT NULL COMMENT 'a rank of it',
  `req_level` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `requires` VARCHAR(64) NOT NULL DEFAULT '' COMMENT 'CoA entry ids that must be held, space separated',
  `baseline` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '1 = CoA ClassSpells baseline (ClasslessWildcard.CoA.ClassSpells)',
  `team` TINYINT UNSIGNED NOT NULL DEFAULT 2 COMMENT 'TeamId that gets it: 0 Alliance, 1 Horde, 2 any',
  PRIMARY KEY (`entry`, `spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Classless CoA automatic entries, granted with their specialisation';

CREATE TABLE IF NOT EXISTS `cw_coa_taught` (
  `parent` INT UNSIGNED NOT NULL COMMENT 'learning this spell',
  `spell` INT UNSIGNED NOT NULL COMMENT 'also teaches this one, and forgetting it takes it away',
  PRIMARY KEY (`parent`, `spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Classless CoA taught abilities';

CREATE TABLE IF NOT EXISTS `cw_coa_spell_scaling` (
  `spell` INT UNSIGNED NOT NULL,
  `effect_mask` TINYINT UNSIGNED NOT NULL COMMENT 'effects whose base points follow the level curve',
  PRIMARY KEY (`spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Classless CoA level-scaled spells';

"""


if __name__ == "__main__":
    main()
