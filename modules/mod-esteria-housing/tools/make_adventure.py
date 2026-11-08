"""Section 3 of the housing spec (combat, training and adventure): the world rows and client DBC rows make_slice.py adds.

    sql/world/housing_adventure_world.sql  catalog rows 40101-40106 (category 7, Utility), their gameobject templates and
                                           the portal looks, the dummy creatures, the portal destinations, and the two home
                                           spells (spell_dbc, cloned from the client's Spell.dbc) with their scripts
    client patch                           CreatureModelData/CreatureDisplayInfo rows that draw the dummies with retail
                                           decor models, and Spell.dbc rows for Teleport: Home and Portal: Home

Called by make_slice.main(); every row is regenerated, so the file can be reapplied.
"""
import struct
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
OUT = MODULE / "sql/world/housing_adventure_world.sql"

UTILITY = 7  # the catalog category the Editor calls Utility
GO_BASE, LOOK_GO_BASE, CREATURE_BASE = 9506010, 9506020, 9505000
# decor id: (name, the retail decor whose model and display it borrows, kind)
DECOR = {
    40101: ("Training Dummy", 11284), 40102: ("Tank Dummy", 18485), 40103: ("Healing Dummy", 4048),
    40104: ("Boss Dummy", 15575), 40105: ("Portal", 11952), 40106: ("Meeting Stone", 14639),
}
# The portal's looks: the decor whose display each uses, or a 3.3.5 display (the mage portal)
PORTAL_LOOKS = [("K'areshi Portal", 11952, 0), ("Portal to Damnation", 4181, 0), ("Translocation Portal", 16314, 0),
                ("Mage Portal", 0, 4396)]
# The meeting stone's looks, the same way (GO entries STONE_LOOK_GO_BASE + look)
STONE_LOOK_GO_BASE = 9506030
STONE_LOOKS = [("Harandar Runestone", 14639, 0), ("Runestone Ring", 31936, 0), ("Rune Pillar", 31943, 0),
               ("Meeting Stone", 0, 5494)]
# The dummies as creatures: their retail decor model, faction (7 attackable, 35 friendly) and creature type (10 mechanical)
DUMMIES = [("Training Dummy", 6190527, 7), ("Tank Dummy", 6212435, 7), ("Healing Dummy", 533284, 35),
           ("Boss Dummy", 6210899, 7)]
DISPLAY_BASE, MODEL_BASE = 977500, 2290300  # free above the client's (977434, 2290199) and in the server's tables
DUMMY_FROM_DISPLAY = 3019                    # the 3.3.5 wooden dummy: model data and display cloned for ours
VOID_ZONE_DISPLAY = 15882                    # Naxxramas' void zone
# Portal destinations: the mage teleports' spell_target_position (faction 0 any, 1 Alliance, 2 Horde), and minimum level
DESTINATIONS = [(1, "Stormwind", 3561, 1, 1), (2, "Ironforge", 3562, 1, 1), (3, "Darnassus", 3565, 1, 1),
                (4, "The Exodar", 32271, 1, 1), (5, "Theramore", 49359, 1, 35), (6, "Orgrimmar", 3567, 2, 1),
                (7, "Undercity", 3563, 2, 1), (8, "Thunder Bluff", 3566, 2, 1), (9, "Silvermoon City", 32272, 2, 1),
                (10, "Stonard", 49358, 2, 35), (11, "Shattrath City", 33690, 1, 58), (12, "Shattrath City", 35715, 2, 58),
                (13, "Dalaran", 53140, 0, 74)]
# The Mage Portal look shows its destination, as the mage portals of 3.3.5 do (their gameobject displays): GO entries
# MAGE_PORTAL_GO_BASE + destination id; id 0 (a home, and Portal: Home) is Dalaran's violet portal.
MAGE_PORTAL_GO_BASE = 9506040
MAGE_PORTAL_DISPLAY = {0: 8111, 1: 4396, 2: 4394, 3: 4393, 4: 6955, 5: 7848, 6: 4395, 7: 4398, 8: 4397, 9: 6956, 10: 7849,
                       11: 7146, 12: 7146, 13: 8111}
TELEPORT_HOME, PORTAL_HOME = 9500100, 9500101
SPELL_FLOATS = {47, 77, 78, 79, 101, 102, 103, 216, 217, 218, 229, 230, 231}
SPELL_TEXTS = {136: 152, 153: 169, 170: 186, 187: 203}  # first locale -> its flags field
SPELLS = [
    # id, cloned from, name, description, tooltip, icon, cooldown ms
    (TELEPORT_HOME, 18960, "Teleport: Home", "Teleports you to your home's front door.",
     "Teleports you home.", 776, 15 * 60 * 1000),
    (PORTAL_HOME, 53142, "Portal: Home", "Opens a portal to your home for one minute. Members of your party can use it.",
     "Opens a portal home for your party.", 1482, 60 * 60 * 1000),
]


def q(text):
    return "'" + str(text).replace("\\", "\\\\").replace("'", "''") + "'"


def dbc_rows(data):
    count, fields, size, _ = struct.unpack_from("<4I", data, 4)
    strings = data[20 + count * size:]
    rows = {}
    for i in range(count):
        w = list(struct.unpack_from(f"<{fields}I", data, 20 + i * size))
        rows[w[0]] = w
    return rows, lambda o: strings[o:strings.index(b"\0", o)].decode("utf-8", "replace")


def spell_row(base, sid, name, desc, tip, icon, cooldown):
    w = list(base)
    w[0], w[1] = sid, 0                      # no category
    w[29], w[30] = cooldown, 0
    w[37:40] = [0, 0, 0]                     # no levels
    w[42], w[204] = 0, 0                     # no mana
    w[52:68] = [0] * 16                      # no reagents
    w[71:74] = [3, 0, 0]                     # one dummy effect: the module's spell script does the travel
    w[74:77] = [0, 0, 0]
    w[80:83] = [0, 0, 0]
    w[86:92] = [1, 0, 0, 0, 0, 0]            # on the caster
    w[95:98] = [0, 0, 0]
    w[107:119] = [0] * 12                    # no item, misc value or triggered spell
    w[133] = icon
    w[208:212] = [0, 0, 0, 0]                # no class family
    return w, {136: name, 153: "", 170: desc, 187: tip}


def spell_sql(w, texts, text_of):
    values = []
    for i, v in enumerate(w):
        locale = next((first for first, flags in SPELL_TEXTS.items() if first <= i < flags), None)
        if locale is not None:
            values.append(q(texts[locale]) if i == locale else "''")
        elif i in SPELL_FLOATS:
            values.append(repr(struct.unpack("<f", struct.pack("<I", v))[0]))
        else:
            values.append(str(struct.unpack("<i", struct.pack("<I", v))[0]))
    return f"INSERT INTO `spell_dbc` VALUES ({', '.join(values)});"


def world_sql(display_of, spell_dbc):
    """display_of: decor id -> its GameObjectDisplayInfo id (make_slice's catalog). spell_dbc: the client's Spell.dbc."""
    spells, text_of = dbc_rows(spell_dbc)
    lines = ["-- Generated by modules/mod-esteria-housing/tools/make_adventure.py (make_slice.py). Do not edit.",
             "-- Housing section 3: training dummies, portals, meeting stones, Teleport: Home and Portal: Home.", ""]
    lines += [f"DELETE FROM `housing_decor_catalog` WHERE `decor_id` BETWEEN 40101 AND 40199;",
              f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {GO_BASE} AND {MAGE_PORTAL_GO_BASE + 19};"]
    for i, (decor, (name, borrow)) in enumerate(sorted(DECOR.items())):
        go = GO_BASE + i
        lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`) VALUES "
                     f"({go}, 2, {display_of[borrow][0]}, {q(name)}, 1, 'go_esteria_housing_adventure');")
        lines.append(f"INSERT INTO `housing_decor_catalog` (`decor_id`, `model_fdid`, `display_id`, `gameobject_entry`, `name`, "
                     f"`category`, `surface`, `min_scale`, `max_scale`, `origin`, `enabled`) VALUES ({decor}, {display_of[borrow][1]}, "
                     f"{display_of[borrow][0]}, {go}, {q(name)}, {UTILITY}, 0, 0.5, 2, 'retail', 1);")
    for dest, display in MAGE_PORTAL_DISPLAY.items():
        lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`) VALUES "
                     f"({MAGE_PORTAL_GO_BASE + dest}, 2, {display}, 'Mage Portal', 1, 'go_esteria_housing_adventure');")
    for base, looks in ((LOOK_GO_BASE, PORTAL_LOOKS), (STONE_LOOK_GO_BASE, STONE_LOOKS)):
        for i, (name, borrow, display) in enumerate(looks):
            lines.append(f"INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`) VALUES "
                         f"({base + i}, 2, {display or display_of[borrow][0]}, {q(name)}, 1, 'go_esteria_housing_adventure');")

    lines += ["", f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {CREATURE_BASE} AND {CREATURE_BASE + 9};",
              f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {CREATURE_BASE} AND {CREATURE_BASE + 9};",
              f"DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN {DISPLAY_BASE} AND {DISPLAY_BASE + 9};",
              f"DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` BETWEEN {DISPLAY_BASE} AND {DISPLAY_BASE + 9};",
              f"DELETE FROM `creaturemodeldata_dbc` WHERE `ID` BETWEEN {MODEL_BASE} AND {MODEL_BASE + 9};"]
    for i, (name, fdid, faction) in enumerate(DUMMIES):
        entry, display = CREATURE_BASE + i, DISPLAY_BASE + i
        # flags_extra 64: no experience; unit_flags 0x40000 (stunned look off), 0: the AI keeps it in place
        lines.append(f"INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, "
                     f"`unit_class`, `unit_flags`, `type`, `flags_extra`, `ScriptName`) VALUES ({entry}, {q(name)}, 'Training Hall', "
                     f"80, 80, {faction}, 0, 1, 0, 10, 64, 'npc_esteria_housing_dummy');")
        lines.append(f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) "
                     f"VALUES ({entry}, 0, {display}, 1, 1);")
        lines.append(f"INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`) VALUES "
                     f"({display}, 0.6, 1.5, 2);")
    void = CREATURE_BASE + len(DUMMIES)
    lines.append(f"INSERT INTO `creature_template` (`entry`, `name`, `minlevel`, `maxlevel`, `faction`, `unit_class`, `unit_flags`, "
                 f"`type`, `flags_extra`) VALUES ({void}, 'Void Zone', 80, 80, 35, 1, {0x02000000 | 0x2}, 10, 64);")
    lines.append(f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) "
                 f"VALUES ({void}, 0, {VOID_ZONE_DISPLAY}, 1, 1);")
    return lines, spells, text_of


def finish_sql(lines, models, displays, spells, text_of):
    """The server's copies of the client rows patch_dbc made (models and displays as raw words), and the spells."""
    for w, name in models:
        floats = {4, 7, 8, 9, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27}
        vals = [q(name) if i == 2 else repr(struct.unpack("<f", struct.pack("<I", v))[0]) if i in floats
                else str(struct.unpack("<i", struct.pack("<I", v))[0]) for i, v in enumerate(w)]
        lines.append(f"INSERT INTO `creaturemodeldata_dbc` VALUES ({', '.join(vals)});")
    for w in displays:
        vals = ["''" if i in (6, 7, 8, 9) else repr(struct.unpack("<f", struct.pack("<I", v))[0]) if i == 4
                else str(struct.unpack("<i", struct.pack("<I", v))[0]) for i, v in enumerate(w)]
        lines.append(f"INSERT INTO `creaturedisplayinfo_dbc` VALUES ({', '.join(vals)});")
    lines += ["", "-- Portal destinations: where each mage teleport lands.",
              "CREATE TABLE IF NOT EXISTS `housing_portal_destination` (`id` INT UNSIGNED NOT NULL, `name` VARCHAR(64) NOT NULL, "
              "`spell_id` INT UNSIGNED NOT NULL, `faction` TINYINT UNSIGNED NOT NULL DEFAULT 0, `min_level` TINYINT UNSIGNED NOT NULL "
              "DEFAULT 1, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;",
              "DELETE FROM `housing_portal_destination`;"]
    for d in DESTINATIONS:
        lines.append(f"INSERT INTO `housing_portal_destination` VALUES ({d[0]}, {q(d[1])}, {d[2]}, {d[3]}, {d[4]});")
    lines += ["", "-- Teleport: Home and Portal: Home (the module's spell scripts do the travel).",
              f"DELETE FROM `spell_dbc` WHERE `ID` IN ({TELEPORT_HOME}, {PORTAL_HOME});",
              f"DELETE FROM `spell_script_names` WHERE `spell_id` IN ({TELEPORT_HOME}, {PORTAL_HOME});"]
    for w, texts in spells:
        lines.append(spell_sql(w, texts, text_of))
    lines.append(f"INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES ({TELEPORT_HOME}, 'spell_esteria_housing_home'), "
                 f"({PORTAL_HOME}, 'spell_esteria_housing_home');")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("wrote", OUT)


def patch_files(winning_dbc, append_rows, storm, client, display_of):
    """The client rows (CreatureModelData, CreatureDisplayInfo, Spell), and writes the world SQL with their server copies."""
    files = {}
    _, spell_dbc = winning_dbc(storm, client, r"DBFilesClient\Spell.dbc")
    lines, spell_rows, text_of = world_sql(display_of, spell_dbc)
    _, models_dbc = winning_dbc(storm, client, r"DBFilesClient\CreatureModelData.dbc")
    _, displays_dbc = winning_dbc(storm, client, r"DBFilesClient\CreatureDisplayInfo.dbc")
    displays, _ = dbc_rows(displays_dbc)
    models, _ = dbc_rows(models_dbc)
    base_display = displays[DUMMY_FROM_DISPLAY]
    base_model = models[base_display[1]]
    new_models, new_displays = [], []
    for i, (name, fdid, _faction) in enumerate(DUMMIES):
        m = list(base_model); m[0] = MODEL_BASE + i
        new_models.append((m, f"retail\\{fdid}.m2"))
        d = list(base_display); d[0], d[1] = DISPLAY_BASE + i, MODEL_BASE + i
        d[6:10] = [0, 0, 0, 0]  # no texture variations or portrait
        new_displays.append(d)
    files[r"DBFilesClient\CreatureModelData.dbc"] = append_rows(models_dbc, 28, 112, [(m, {2: name}) for m, name in new_models])
    files[r"DBFilesClient\CreatureDisplayInfo.dbc"] = append_rows(displays_dbc, 16, 64, [(d, {}) for d in new_displays])
    spells = [spell_row(spell_rows[src], sid, name, desc, tip, icon, cd) for sid, src, name, desc, tip, icon, cd in SPELLS]
    files[r"DBFilesClient\Spell.dbc"] = append_rows(spell_dbc, 234, 936, [(w, dict(t)) for w, t in spells])
    finish_sql(lines, new_models, new_displays, spells, text_of)
    return files
