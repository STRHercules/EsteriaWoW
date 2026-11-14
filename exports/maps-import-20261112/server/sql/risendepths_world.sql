-- Risen Depths (map 1430). Graveyards only: the source has no creatures, quests or scripts.
DELETE FROM `game_graveyard` WHERE `ID` IN (1854,1855,1856,1857);
-- game_graveyard: 4 rows
INSERT INTO `game_graveyard` (`ID`, `Map`, `x`, `y`, `z`, `Comment`) VALUES
(1854, 1430, -903.53076171875, 32.3347282409668, -140.0, 'Risen Depths Naga Graveyard'),
(1855, 1430, -661.0789794921875, -527.5889892578125, 1.0, 'Risen Depths Naga Graveyard'),
(1856, 1430, 143.787353515625, -415.2380676269531, -65.0, 'Risen Depths Naga Graveyard'),
(1857, 1430, 143.15899658203125, 238.25399780273438, 4.0, 'Risen Depths Naga Graveyard');

DELETE FROM `graveyard_zone` WHERE `ID` IN (1854,1855,1856,1857);
-- graveyard_zone: 4 rows
INSERT INTO `graveyard_zone` (`ID`, `GhostZone`, `Faction`, `Comment`) VALUES
(1854, 10050, 0, 'Risen Depths'),
(1855, 10050, 0, 'Risen Depths'),
(1856, 10050, 0, 'Risen Depths'),
(1857, 10050, 0, 'Risen Depths');

