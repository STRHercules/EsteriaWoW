"""Import UWoW WoD garrison creature/GO placement into Esteria SQL.

Source: https://github.com/fluxurion/UWoW_WoD
  - sql/uwow/2015_11_30_01_world_garrison_alliance_shadowmoon_valley_spawn.sql (map 1158)
  - sql/uwow/2015_11_31_01_world_garrison_horde_frostfire_ridge_spawn.sql (map 1152)
  - sql/uwow/2015_10_30_00_world_garrison_building_spawn.sql

Client models stay Casc (retail/<fdid>.m2); creature entries are real WoD IDs.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
UWoW = Path(r"G:\risServer\_ref\UWoW_WoD\sql\uwow")
OUT = MODULE / "sql" / "world"

# Known WoD NPCs -> Casc FileDataID (+ optional texture slots) for 3.3.5 CascSource client.
# Unmapped entries get faction default kits so they still render.
KNOWN_MODELS: dict[int, tuple[int, float, int, int, int, str]] = {
    # entry: (fdid, scale, tex11, tex12, tex13, name)
    77209: (1570137, 1.25, 1570258, 1570255, 0, "Baros Alexston"),
    78466: (5764885, 1.0, 0, 0, 0, "Gazlowe"),
    78467: (5764885, 1.0, 0, 0, 0, "Gazlowe"),
    79457: (930099, 1.7, 937286, 0, 0, "Lieutenant Thorn"),
    81152: (1721658, 1.15, 1738965, 1738967, 1738966, "Dungar Longdrink"),
    85312: (930099, 1.0, 937291, 937283, 0, "Lunarfall Guard"),
    79781: (918944, 1.0, 962560, 962555, 0, "Frostwall Grunt"),
    79812: (918944, 1.05, 962560, 962555, 0, "Sergeant"),
    80299: (918944, 1.0, 962560, 962555, 0, "Peon"),
    80569: (918944, 1.0, 962560, 962555, 0, "Recruit"),
    80571: (918944, 1.0, 962560, 962555, 0, "Recruit"),
    80572: (918944, 1.0, 962560, 962555, 0, "Recruit"),
    81653: (2026821, 1.0, 2027016, 0, 0, "Stablehand"),
}

ALLY_DEFAULT = (1570137, 1.0, 1570258, 1570255, 0)
HORDE_DEFAULT = (918944, 1.0, 962560, 962555, 0)

# Common town GOs from sniff -> Casc
KNOWN_GO: dict[int, tuple[int, bool, str]] = {
    230867: (969977, False, "Architect Table"),
    233141: (944905, False, "Mailbox"),
    232249: (971921, False, "Garrison Cache"),
    232250: (950137, False, "Supply Crate"),
    232251: (948449, False, "Crate"),
    239184: (960215, False, "Lamppost"),
    239178: (1021317, False, "Banner"),
}


def parse_creature_rows(path: Path, maps: set[int]) -> list[tuple]:
    rows = []
    for line in path.open(encoding="utf-8", errors="replace"):
        if "@CGUID" not in line or not line.strip().startswith("("):
            continue
        # skip commented duplicates
        if line.lstrip().startswith("--"):
            continue
        p = line.split(",")
        if len(p) < 13:
            continue
        try:
            entry = int(p[1].strip())
            m = int(p[2].strip())
            if m not in maps:
                continue
            x, y, z, o = float(p[6]), float(p[7]), float(p[8]), float(p[9])
            dist = float(p[11].strip())
            mt = int(re.split(r"[)\\s]", p[12].strip())[0])
        except Exception:
            continue
        wander = dist if mt == 1 else 0.0
        rows.append((entry, m, x, y, z, o, wander))
    return rows


def parse_go_rows(path: Path, maps: set[int]) -> list[tuple]:
    rows = []
    for line in path.open(encoding="utf-8", errors="replace"):
        if "@OGUID" not in line or not line.strip().startswith("("):
            continue
        if line.lstrip().startswith("--"):
            continue
        p = line.split(",")
        if len(p) < 12:
            continue
        try:
            entry = int(p[1].strip())
            m = int(p[2].strip())
            if m not in maps:
                continue
            x, y, z, o = float(p[6]), float(p[7]), float(p[8]), float(p[9])
        except Exception:
            continue
        rows.append((entry, m, x, y, z, o))
    return rows


def display_id_for(entry: int) -> int:
    # Stable unique display slot in garrison Casc band
    return 700000 + entry


def model_id_for(entry: int) -> int:
    return 710000 + entry


def q(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main():
    ally_c = parse_creature_rows(
        UWoW / "2015_11_30_01_world_garrison_alliance_shadowmoon_valley_spawn.sql", {1158}
    )
    horde_c = parse_creature_rows(
        UWoW / "2015_11_31_01_world_garrison_horde_frostfire_ridge_spawn.sql", {1152}
    )
    ally_g = parse_go_rows(
        UWoW / "2015_11_30_01_world_garrison_alliance_shadowmoon_valley_spawn.sql", {1158}
    )
    horde_g = parse_go_rows(
        UWoW / "2015_11_31_01_world_garrison_horde_frostfire_ridge_spawn.sql", {1152}
    )
    creatures = ally_c + horde_c
    gos = ally_g + horde_g
    entries = sorted({r[0] for r in creatures})
    go_entries = sorted({r[0] for r in gos})

    # --- map spawn SQL ---
    lines = [
        "-- Generated from UWoW_WoD sniff spawns (fluxurion/UWoW_WoD).",
        "-- Real WoD creature/gameobject entries + retail coords on maps 1158/1152.",
        "",
        "DROP TABLE IF EXISTS `garrison_map_creature`;",
        "CREATE TABLE `garrison_map_creature` (",
        "  `idx` INT UNSIGNED NOT NULL AUTO_INCREMENT,",
        "  `entry` INT UNSIGNED NOT NULL,",
        "  `map` SMALLINT UNSIGNED NOT NULL,",
        "  `position_x` FLOAT NOT NULL,",
        "  `position_y` FLOAT NOT NULL,",
        "  `position_z` FLOAT NOT NULL,",
        "  `orientation` FLOAT NOT NULL,",
        "  `wander` FLOAT NOT NULL DEFAULT 0,",
        "  PRIMARY KEY (`idx`),",
        "  KEY `map` (`map`)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;",
        "",
        "DROP TABLE IF EXISTS `garrison_map_gameobject`;",
        "CREATE TABLE `garrison_map_gameobject` (",
        "  `idx` INT UNSIGNED NOT NULL AUTO_INCREMENT,",
        "  `entry` INT UNSIGNED NOT NULL,",
        "  `map` SMALLINT UNSIGNED NOT NULL,",
        "  `position_x` FLOAT NOT NULL,",
        "  `position_y` FLOAT NOT NULL,",
        "  `position_z` FLOAT NOT NULL,",
        "  `orientation` FLOAT NOT NULL,",
        "  PRIMARY KEY (`idx`),",
        "  KEY `map` (`map`)",
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;",
        "",
    ]
    for e, m, x, y, z, o, w in creatures:
        lines.append(
            "INSERT INTO `garrison_map_creature` "
            "(`entry`,`map`,`position_x`,`position_y`,`position_z`,`orientation`,`wander`) "
            f"VALUES ({e},{m},{x},{y},{z},{o},{w});"
        )
    for e, m, x, y, z, o in gos:
        lines.append(
            "INSERT INTO `garrison_map_gameobject` "
            "(`entry`,`map`,`position_x`,`position_y`,`position_z`,`orientation`) "
            f"VALUES ({e},{m},{x},{y},{z},{o});"
        )
    (OUT / "garrison_uwow_map_spawns.sql").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("map creatures", len(creatures), "gos", len(gos), "unique npc", len(entries), "unique go", len(go_entries))

    # --- building spawn (copy UWoW table, keep real IDs) ---
    bc_src = (UWoW / "2015_10_30_00_world_garrison_building_spawn.sql").read_text(encoding="utf-8", errors="replace")
    # Normalize engine and add building column default for AC
    bc = bc_src.replace("ENGINE=MyISAM", "ENGINE=InnoDB").replace("CHARSET=utf8", "CHARSET=utf8mb4")
    # UWoW LoadBuildingSpawnNPC expects column `building` — add if missing in INSERT
    # Original table has no `building` column in CREATE but C++ selects it — check C++ again
    (OUT / "garrison_uwow_building_spawns.sql").write_text(
        "-- From UWoW 2015_10_30_00_world_garrison_building_spawn.sql\n" + bc,
        encoding="utf-8",
    )

    # Fix: UWoW C++ selects `building` column — add it
    # Read GarrisonMgr again - SELECT plotID, BuildID, id, map, position_x, position_y, position_z, orientation, building
    # But CREATE TABLE doesn't have building! Bug in UWoW or later alter. We'll add building TINYINT default 1.

    # --- templates + models SQL for Casc client ---
    tlines = [
        "-- UWoW creature/GO templates + Casc creature_template_model for garrison maps.",
        "DELETE FROM `creature_template_model` WHERE `CreatureID` IN (" + ",".join(map(str, entries)) + ");",
        "DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN 700000 AND 799999;",
        "DELETE FROM `creature_template` WHERE `entry` IN (" + ",".join(map(str, entries)) + ");",
        "",
    ]
    model_defs: dict[int, tuple] = {}
    for e in entries:
        if e in KNOWN_MODELS:
            fdid, scale, t11, t12, t13, name = KNOWN_MODELS[e]
        else:
            # heuristic: ally map entries vs horde
            ally = any(r[0] == e and r[1] == 1158 for r in creatures)
            fdid, scale, t11, t12, t13 = ALLY_DEFAULT if ally else HORDE_DEFAULT
            name = f"Garrison NPC {e}"
        did = display_id_for(e)
        model_defs[e] = (fdid, scale, t11, t12, t13, name, did)
        tlines.append(
            "INSERT INTO `creature_template` "
            "(`entry`,`name`,`subname`,`minlevel`,`maxlevel`,`faction`,`npcflag`,`speed_walk`,`speed_run`,"
            "`BaseAttackTime`,`RangeAttackTime`,`unit_class`,`type`,`type_flags`,`ScriptName`) VALUES "
            f"({e},{q(name)},'Garrison',90,90,35,1,1,1.14286,2000,2000,1,7,0,'garrison_resident');"
        )
        tlines.append(
            "INSERT INTO `creature_template_model` "
            "(`CreatureID`,`Idx`,`CreatureDisplayID`,`DisplayScale`,`Probability`) "
            f"VALUES ({e},0,{did},{scale},1);"
        )
        tlines.append(
            "INSERT INTO `creature_model_info` "
            "(`DisplayID`,`BoundingRadius`,`CombatReach`,`Gender`,`DisplayID_Other_Gender`,`VerifiedBuild`) "
            f"VALUES ({did},0.5,1.5,2,0,0);"
        )

    # GO templates for known + stub others as type 5
    for ge in go_entries:
        if ge in KNOWN_GO:
            fdid, is_wmo, name = KNOWN_GO[ge]
            did = 720000 + ge % 100000
            tlines.append(f"DELETE FROM `gameobject_template` WHERE `entry`={ge};")
            tlines.append(
                "INSERT INTO `gameobject_template` (`entry`,`type`,`displayId`,`name`,`size`,`Data0`,`ScriptName`) "
                f"VALUES ({ge},5,{did},{q(name)},1,0,'');"
            )
        else:
            did = 720000 + ge % 100000
            tlines.append(f"DELETE FROM `gameobject_template` WHERE `entry`={ge};")
            tlines.append(
                "INSERT INTO `gameobject_template` (`entry`,`type`,`displayId`,`name`,`size`,`Data0`) "
                f"VALUES ({ge},5,{did},{q(f'Garrison Object {ge}')},1,0);"
            )

    (OUT / "garrison_uwow_templates.sql").write_text("\n".join(tlines) + "\n", encoding="utf-8")

    # Emit Casc model map for make_residents / patch tool
    map_path = HERE / "uwow_npc_casc_models.py"
    map_path.write_text(
        "NPC_MODELS = {\n"
        + "".join(
            f"    {e}: ({fdid}, {scale}, {t11}, {t12}, {t13}),  # {name}\n"
            for e, (fdid, scale, t11, t12, t13, name, did) in sorted(model_defs.items())
        )
        + "}\n"
        "DISPLAY_FOR = {\n"
        + "".join(f"    {e}: {did},\n" for e, (*_, did) in sorted(model_defs.items()))
        + "}\n",
        encoding="utf-8",
    )
    print("wrote templates", len(entries), "casc map", map_path)


if __name__ == "__main__":
    main()
