-- Garrison residents and the objects they stand beside.
-- Creature/GO looks come from garrison_residents_models.sql (retail Casc FileDataIDs via make_residents.py).
-- Architect, mission officer, flight master and the mage tower use garrison_resident.
-- The cache chest uses garrison_cache. Trainers, the innkeeper, the stable and vendors use core menus.

DELETE FROM `creature_default_trainer` WHERE `CreatureId` BETWEEN 9601101 AND 9601499;
DELETE FROM `npc_vendor` WHERE `entry` BETWEEN 9601101 AND 9601499;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9601101 AND 9601499;
-- creature_template_model + gameobject_template 9602001-9602010: garrison_residents_models.sql

INSERT INTO `creature_template`
(`entry`, `name`, `subname`, `IconName`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `BaseAttackTime`, `RangeAttackTime`, `HealthModifier`, `ScriptName`) VALUES
(9601101, 'Baros Alexston', 'Garrison Architect', NULL, 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601102, 'Gazlowe', 'Garrison Architect', NULL, 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601103, 'Lieutenant Thorn', 'Command Table', NULL, 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601104, 'Warmaster Zog', 'Command Table', NULL, 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601105, 'Quartermaster', 'Garrison Supplies', 'Vendor', 70, 70, 35, 4225, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601106, 'Quartermaster', 'Garrison Supplies', 'Vendor', 70, 70, 35, 4225, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601107, 'Dungar Longdrink', 'Gryphon Master', 'Taxi', 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601108, 'Wind Rider', 'Flight Master', 'Taxi', 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601109, 'Alliance Guard', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601110, 'Horde Guard', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601111, 'Sergeant Crowley', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601112, 'Sergeant', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601120, 'Innkeeper', 'Lunarfall Inn', 'Innkeeper', 70, 70, 35, 66049, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601121, 'Innkeeper', 'Frostwall Tavern', 'Innkeeper', 70, 70, 35, 66049, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601122, 'Stable Master', '', NULL, 70, 70, 35, 4194305, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601123, 'Stable Master', '', NULL, 70, 70, 35, 4194305, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601124, 'Barn Hand', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601125, 'Barn Hand', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601126, 'Miner', 'Mining', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601127, 'Miner', 'Mining', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601128, 'Herbalist', 'Herbalism', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601129, 'Herbalist', 'Herbalism', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601130, 'Blacksmith', 'Blacksmithing', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601131, 'Blacksmith', 'Blacksmithing', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601132, 'Alchemist', 'Alchemy', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601133, 'Alchemist', 'Alchemy', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601134, 'Enchanter', 'Enchanting', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601135, 'Enchanter', 'Enchanting', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601136, 'Tailor', 'Tailoring', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601137, 'Tailor', 'Tailoring', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601138, 'Leatherworker', 'Leatherworking', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601139, 'Leatherworker', 'Leatherworking', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601140, 'Engineer', 'Engineering', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601141, 'Engineer', 'Engineering', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601142, 'Scribe', 'Inscription', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601143, 'Scribe', 'Inscription', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601144, 'Jewelcrafter', 'Jewelcrafting', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601145, 'Jewelcrafter', 'Jewelcrafting', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601146, 'Fisherman', 'Fishing', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601147, 'Fisherman', 'Fishing', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601148, 'Lumberjack', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601149, 'Lumberjack', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601150, 'Trader', 'Trading Post', 'Vendor', 70, 70, 35, 4225, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601151, 'Trader', 'Trading Post', 'Vendor', 70, 70, 35, 4225, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601152, 'Salvager', 'Salvage Yard', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601153, 'Salvager', 'Salvage Yard', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601154, 'Storekeeper', 'Storehouse', 'Vendor', 70, 70, 35, 4225, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601155, 'Storekeeper', 'Storehouse', 'Vendor', 70, 70, 35, 4225, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601156, 'Magus', 'Mage Tower', NULL, 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601157, 'Magus', 'Spirit Lodge', NULL, 70, 70, 35, 1, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, 'garrison_resident'),
(9601158, 'Gladiator', 'Gladiator''s Sanctum', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601159, 'Gladiator', 'Gladiator''s Sanctum', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601160, 'Tinker', 'Gearworks', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601161, 'Tinker', 'Workshop', 'Trainer', 70, 70, 35, 65, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601162, 'Officer', 'Barracks', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601163, 'Officer', 'Barracks', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601164, 'Bunker Guard', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601165, 'War Mill Guard', '', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601166, 'Beast Keeper', 'Menagerie', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601167, 'Beast Keeper', 'Menagerie', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601301, 'Shelly Hamby', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601302, 'Qiana Moonshadow', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601303, 'Rulkan', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601304, 'Delvar Ironfist', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601305, 'Admiral Taylor', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601306, 'Fiona', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601401, 'Olin Umberhide', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601402, 'Mulverick', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601403, 'Ka''la', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601404, 'Lantresor of the Blade', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601405, 'Shadow Hunter Rala', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, ''),
(9601406, 'Benjamin Gibb', 'Garrison Follower', NULL, 70, 70, 35, 0, 1, 1.14286, 1, 770, 7, 2000, 2000, 1, '');

-- Models: see garrison_residents_models.sql (make_residents.py → retail/<FileDataID>.m2 via Casc CDN).

INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) VALUES
(9601126, 78), (9601127, 78), (9601128, 71), (9601129, 71), (9601130, 59), (9601131, 59),
(9601132, 65), (9601133, 65), (9601134, 94), (9601135, 94), (9601136, 72), (9601137, 72),
(9601138, 63), (9601139, 63), (9601140, 89), (9601141, 89), (9601142, 119), (9601143, 119),
(9601144, 111), (9601145, 111), (9601146, 97), (9601147, 97), (9601160, 89), (9601161, 89);

INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601105, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 1291;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601106, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 1291;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601120, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 6740;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601121, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 6740;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601150, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 1291;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601151, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 1291;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601154, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 1291;
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`)
SELECT 9601155, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost` FROM `npc_vendor` WHERE `entry` = 1291;

-- GO templates + retail displays: garrison_residents_models.sql
