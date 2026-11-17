"""Normalize UWoW building spawn SQL for Esteria (InnoDB + building column once)."""
from pathlib import Path
import re

src = Path(r"G:\risServer\_ref\UWoW_WoD\sql\uwow\2015_10_30_00_world_garrison_building_spawn.sql")
out = Path(r"G:\risServer\EsteriaWoW\modules\mod-esteria-garrison\sql\world\garrison_uwow_building_spawns.sql")
text = src.read_text(encoding="utf-8", errors="replace")
text = text.replace("ENGINE=MyISAM", "ENGINE=InnoDB")
text = text.replace("CHARSET=utf8", "CHARSET=utf8mb4")
text = text.replace("ROW_FORMAT=FIXED", "ROW_FORMAT=DYNAMIC")
# Strip later ALTER ADD building — we bake it into CREATE
text = re.sub(
    r"ALTER TABLE `garrison_building_gameobject` ADD `building`[^;]+;",
    "",
    text,
    flags=re.I,
)
text = re.sub(
    r"ALTER TABLE `garrison_building_creature` ADD `building`[^;]+;",
    "",
    text,
    flags=re.I,
)
# Inject building into CREATE tables
text = text.replace(
    "  `orientation` float NOT NULL DEFAULT '0',\n  `idx` int(11) NOT NULL\n) ENGINE=InnoDB AUTO_INCREMENT=13",
    "  `orientation` float NOT NULL DEFAULT '0',\n"
    "  `building` tinyint(1) unsigned NOT NULL DEFAULT '1',\n"
    "  `idx` int(11) NOT NULL\n) ENGINE=InnoDB AUTO_INCREMENT=13",
)
text = text.replace(
    "  `rotation3` float NOT NULL DEFAULT '0',\n  `idx` int(11) NOT NULL\n) ENGINE=InnoDB AUTO_INCREMENT=11",
    "  `rotation3` float NOT NULL DEFAULT '0',\n"
    "  `building` tinyint(1) unsigned NOT NULL DEFAULT '1',\n"
    "  `idx` int(11) NOT NULL\n) ENGINE=InnoDB AUTO_INCREMENT=11",
)
# INSERTs that already include building column are fine; first creature INSERT has no building — OK via default
# Ensure BuildID=0 GOs are empty-plot props
footer = """
UPDATE `garrison_building_creature` SET `building` = 1 WHERE `building` = 0 AND `BuildID` <> 0;
UPDATE `garrison_building_gameobject` SET `building` = IF(`BuildID` = 0, 0, 1);
"""
out.write_text(
    "-- Normalized from UWoW 2015_10_30_00_world_garrison_building_spawn.sql\n" + text + footer,
    encoding="utf-8",
)
print("wrote", out, "bytes", out.stat().st_size)
