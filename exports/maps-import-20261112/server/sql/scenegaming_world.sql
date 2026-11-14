-- SceneGaming (maps 1410-1412, renumbered from 725-727; AreaTable ids 30001-30007; graveyards 1801-1803)
DELETE FROM `game_graveyard` WHERE `ID` IN (1801, 1802, 1803);
-- game_graveyard: 3 rows
INSERT INTO `game_graveyard` (`ID`, `Map`, `x`, `y`, `z`, `Comment`) VALUES
(1801, 1410, -1866.2421875, -1904.6954345703125, -0.0013549999566748738, 'SceneGaming The Forest Arena Graveyard'),
(1802, 1411, -2012.08544921875, -1986.0806884765625, 0.00011200000153621659, 'SceneGaming The Black Forest Graveyard'),
(1803, 1412, 11422.08984375, 11665.083984375, 0.0007650000043213367, 'SceneGaming Forest of Karma Graveyard');

DELETE FROM `graveyard_zone` WHERE `ID` IN (1801, 1802, 1803);
-- graveyard_zone: 7 rows
INSERT INTO `graveyard_zone` (`ID`, `GhostZone`, `Faction`, `Comment`) VALUES
(1801, 30001, 0, 'SceneGaming 5000'),
(1801, 30002, 0, 'SceneGaming 5001'),
(1802, 30003, 0, 'SceneGaming 5200'),
(1803, 30004, 0, 'SceneGaming 5300'),
(1803, 30005, 0, 'SceneGaming 5301'),
(1803, 30006, 0, 'SceneGaming 5302'),
(1803, 30007, 0, 'SceneGaming 5303');

DELETE FROM `creature` WHERE `guid` BETWEEN 9700901 AND 9700903;
-- creature: 3 rows
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `currentwaypoint`, `curhealth`, `curmana`, `MovementType`, `npcflag`, `unit_flags`, `dynamicflags`, `ScriptName`, `VerifiedBuild`) VALUES
(9700901, 6491, 1410, 0, 0, 1, 1, 0, -1861.11, -1904.55, 4.58434e-05, 3.13538, 300, 0, 0, 4121, 0, 0, 0, 0, 0, '', 0),
(9700902, 6491, 1411, 0, 0, 1, 1, 0, -2010.52, -1990.85, 0.000112, 1.88811, 300, 0, 0, 4121, 0, 0, 0, 0, 0, '', 0),
(9700903, 6491, 1412, 0, 0, 1, 1, 0, 11431.5, 11667.2, 0.000765, 3.34991, 300, 0, 0, 4121, 0, 0, 0, 0, 0, '', 0);

