SET @GUID := 900001; -- Make this something unoccupied!

DELETE FROM `creature`
WHERE `guid` BETWEEN @GUID AND @GUID + 21;

INSERT INTO `creature`
    (`guid`, `id`, `map`, `zoneId`, `areaId`,
     `spawnMask`, `phaseMask`, `equipment_id`,
     `position_x`, `position_y`, `position_z`, `orientation`,
     `spawntimesecs`, `wander_distance`, `currentwaypoint`,
     `curhealth`, `curmana`, `MovementType`,
     `npcflag`, `unit_flags`, `dynamicflags`,
     `ScriptName`, `VerifiedBuild`, `CreateObject`, `Comment`)
VALUES
    (@GUID,     6491, 0, 0, 0, 1, 1, 0,
     -1751.55, 1400, 20, 4,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas City - Military District'),

    (@GUID + 1, 6491, 0, 0, 0, 1, 1, 0,
     -1918, 2572, 1.39, 1.5,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - Hammond Farmstead'),

    (@GUID + 2, 6491, 0, 0, 0, 1, 1, 0,
     -1888.53, 2321.2, 39.7, 2.34,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - Duskhaven'),

    (@GUID + 3, 6491, 0, 0, 0, 1, 1, 0,
     -1192, 1151.2, 24.7, 0.8,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - Emberstone Village'),

    (@GUID + 4, 6491, 0, 0, 0, 1, 1, 0,
     -1950.65, 967.4, 77, 0.70,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - Tempest''s Reach'),

    (@GUID + 5, 6491, 0, 0, 0, 1, 1, 0,
     -2500.1, 1470.59, 17, 5.57,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - Stormglen Village'),

    (@GUID + 6, 6491, 0, 0, 0, 1, 1, 0,
     -2154.1, 1673.93, -37.9, 4.9,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - The Blackwald'),

    (@GUID + 7, 6491, 0, 0, 0, 1, 1, 0,
     -2226.4, 1845.32, 13.9, 4.7,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - Stagecoach Crash Site'),

    (@GUID + 8, 6491, 0, 0, 0, 1, 1, 0,
     -1642, 1824.1, 4.7, 1.5,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas - Aderic''s Repose'),

    (@GUID + 9, 6491, 1, 0, 0, 1, 1, 0,
     -8920, -11511, 92.87, 3.6,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Kezan - KTC Headquarters'),

    (@GUID + 10, 6491, 1, 0, 0, 1, 1, 0,
     -8657, -11280, 10.76, 6.3,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Kezan - Bilgewater Port'),

    (@GUID + 11, 6491, 1, 0, 0, 1, 1, 0,
     331.20, -10441.5, 5.713, 1.5,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Landing Site'),

    (@GUID + 12, 6491, 1, 0, 0, 1, 1, 0,
     90.6, -10839.17, 13.19, 2.74,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Ruins of Vashj''elan'),

    (@GUID + 13, 6491, 1, 0, 0, 1, 1, 0,
     177.97, -10974.16, 105.04, 0.93,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Oomlot Village'),

    (@GUID + 14, 6491, 1, 0, 0, 1, 1, 0,
     854, -11464.92, 133.86, 0.1,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Lost Caldera'),

    (@GUID + 15, 6491, 1, 0, 0, 1, 1, 0,
     926.73, -10753.83, 224.914, 1,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Lost Peak'),

    (@GUID + 16, 6491, 1, 0, 0, 1, 1, 0,
     1231.61, -10785.28, 222.97, 5.9,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Sky Falls'),

    (@GUID + 17, 6491, 1, 0, 0, 1, 1, 0,
     1533, -10485.5, 69.9, 2.3,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Verdant Highlands'),

    (@GUID + 18, 6491, 1, 0, 0, 1, 1, 0,
     1208.8, -10110, 85.31, 3,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Lost Isles - Warchief''s Lookout'),

    (@GUID + 19, 6491, 0, 0, 0, 1, 1, 0,
     -1574, 1600.6, 21.44, 2.36,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas City - Light''s Dawn Cathedral'),

    (@GUID + 20, 6491, 0, 0, 0, 1, 1, 0,
     -1766, 1656.34, 21, 1,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas City - Greymane Court'),

    (@GUID + 21, 6491, 0, 0, 0, 1, 1, 0,
     -1386, 1371.84, 35.85, 3.15,
     120, 0, 0, 1, 0, 0, 0, 0, 0, '', 0, 0, 'Gilneas City - Merchant Square');
