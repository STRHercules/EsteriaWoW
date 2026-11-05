-- Zone-aware wild spawns (acore_world): the knobs and the starting zone table.
--
-- battlemon_spawn_setting   runtime knobs, edited from the admin panel (/bm admin) or here, then
--                           `.battlemon reload`. A key with no row uses the default in BattlemonSpawns.cpp.
-- battlemon_spawn_zone      per WoW zone: the level range and which Pokemon types live there. `types` is
--                           TYPE:weight pairs ("GRASS:3,BUG:2"); a type not listed gets the `leak` weight
--                           (0 keeps it out). A zone with no row spawns exactly as before.
-- battlemon_spawn_species   global per-species multiplier on top of that (0 bans a species, 2 doubles it).
--
-- The seed covers the standard Azeroth, Outland and Northrend zones; zone ids are AreaTable.dbc ids (the
-- zone, not the sub-area). Add rows for your custom zones. Re-running replaces ONLY the seeded zone ids and
-- never touches settings or species overrides, so admin edits to those survive.

CREATE TABLE IF NOT EXISTS `battlemon_spawn_setting` (
  `name` varchar(48) NOT NULL,
  `value` varchar(32) NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_spawn_zone` (
  `zone_id` int unsigned NOT NULL COMMENT 'AreaTable.dbc zone id',
  `min_level` tinyint unsigned NOT NULL DEFAULT '1',
  `max_level` tinyint unsigned NOT NULL DEFAULT '100',
  `types` varchar(255) NOT NULL DEFAULT '' COMMENT 'TYPE:weight,TYPE:weight',
  `note` varchar(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`zone_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_spawn_species` (
  `species_id` int unsigned NOT NULL COMMENT 'battlemon_species.id',
  `multiplier` float NOT NULL DEFAULT '1',
  PRIMARY KEY (`species_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DELETE FROM `battlemon_spawn_zone` WHERE `zone_id` IN (1, 3, 4, 8, 10, 11, 12, 14, 15, 16, 17, 28, 33, 36, 38, 40, 41, 44, 45, 46, 47, 51, 65, 66, 67, 85, 130, 139, 141, 148, 210, 215, 267, 331, 357, 361, 394, 400, 405, 406, 440, 490, 493, 495, 618, 1377, 3430, 3433, 3483, 3518, 3519, 3520, 3521, 3522, 3523, 3524, 3525, 3537, 3711);
INSERT INTO `battlemon_spawn_zone` (`zone_id`, `min_level`, `max_level`, `types`, `note`) VALUES
(1, 1, 10, 'NORMAL:3,ICE:3,ROCK:2,GROUND:2,WATER:1', 'Dun Morogh'),
(3, 35, 45, 'ROCK:3,GROUND:3,FIRE:2,FIGHTING:1', 'Badlands'),
(4, 45, 55, 'FIRE:3,DARK:3,ROCK:2,GROUND:2,STEEL:1', 'Blasted Lands'),
(8, 35, 45, 'POISON:3,WATER:3,GHOST:2,DRAGON:2,GRASS:2', 'Swamp of Sorrows'),
(10, 18, 30, 'GHOST:3,DARK:3,BUG:2,POISON:2,GRASS:2', 'Duskwood'),
(11, 20, 30, 'WATER:3,POISON:2,GRASS:2,GROUND:2', 'Wetlands'),
(12, 1, 10, 'NORMAL:3,GRASS:3,BUG:3,FLYING:2,POISON:1', 'Elwynn Forest'),
(14, 1, 10, 'FIRE:3,GROUND:3,ROCK:2,NORMAL:2,POISON:1', 'Durotar'),
(15, 35, 45, 'WATER:3,POISON:3,GRASS:2,DRAGON:2,GHOST:1', 'Dustwallow Marsh'),
(16, 45, 55, 'WATER:3,FAIRY:2,DARK:2,ROCK:1,PSYCHIC:1', 'Azshara'),
(17, 10, 25, 'NORMAL:3,GROUND:3,FIGHTING:2,FIRE:1,POISON:1,FLYING:1', 'The Barrens'),
(28, 51, 58, 'GHOST:3,POISON:3,GRASS:2,BUG:2', 'Western Plaguelands'),
(33, 30, 45, 'GRASS:3,POISON:3,BUG:2,WATER:2,DRAGON:1', 'Stranglethorn Vale'),
(36, 30, 40, 'ICE:3,ROCK:3,FLYING:2,NORMAL:1', 'Alterac Mountains'),
(38, 10, 20, 'ROCK:3,WATER:3,NORMAL:2,GROUND:2', 'Loch Modan'),
(40, 10, 20, 'NORMAL:3,GROUND:3,GRASS:2,BUG:2,FIGHTING:1', 'Westfall'),
(41, 55, 60, 'GHOST:3,DARK:3,POISON:2', 'Deadwind Pass'),
(44, 15, 25, 'ROCK:3,GROUND:3,NORMAL:2,FIRE:1,FLYING:1', 'Redridge Mountains'),
(45, 30, 40, 'NORMAL:3,FIGHTING:2,ROCK:2,GRASS:2,GROUND:2', 'Arathi Highlands'),
(46, 50, 58, 'FIRE:3,ROCK:3,DRAGON:3,GROUND:2', 'Burning Steppes'),
(47, 40, 50, 'GRASS:3,FLYING:3,NORMAL:2,BUG:2,FIGHTING:1', 'The Hinterlands'),
(51, 43, 50, 'FIRE:3,STEEL:3,ROCK:3,GROUND:2', 'Searing Gorge'),
(65, 71, 75, 'DRAGON:3,ICE:3,FLYING:2,ROCK:1', 'Dragonblight'),
(66, 74, 77, 'POISON:3,GRASS:3,DRAGON:2,GHOST:2,FIGHTING:2', 'Zul''Drak'),
(67, 77, 80, 'ICE:3,ROCK:3,STEEL:2,ELECTRIC:2,FIGHTING:2', 'The Storm Peaks'),
(85, 1, 10, 'GHOST:3,DARK:2,NORMAL:2,BUG:2,POISON:2', 'Tirisfal Glades'),
(130, 10, 20, 'DARK:3,GRASS:2,BUG:2,NORMAL:2,GHOST:2', 'Silverpine Forest'),
(139, 53, 60, 'GHOST:3,POISON:3,DARK:2,BUG:2', 'Eastern Plaguelands'),
(141, 1, 10, 'GRASS:3,BUG:2,NORMAL:2,FAIRY:2,PSYCHIC:2,FLYING:1', 'Teldrassil'),
(148, 10, 20, 'WATER:3,GRASS:2,NORMAL:2,DARK:1,FAIRY:1', 'Darkshore'),
(210, 77, 80, 'ICE:3,GHOST:3,DARK:3,STEEL:2,DRAGON:2', 'Icecrown'),
(215, 1, 10, 'NORMAL:3,GRASS:3,FIGHTING:2,FLYING:2,GROUND:1', 'Mulgore'),
(267, 20, 30, 'NORMAL:3,GRASS:2,WATER:2,BUG:2,FIGHTING:1', 'Hillsbrad Foothills'),
(331, 18, 30, 'GRASS:3,FAIRY:2,BUG:2,DARK:2,FLYING:2,WATER:1', 'Ashenvale'),
(357, 40, 50, 'GRASS:3,BUG:2,DRAGON:2,FAIRY:2,WATER:2', 'Feralas'),
(361, 48, 55, 'DARK:3,POISON:3,GRASS:2,GHOST:2,FIRE:1', 'Felwood'),
(394, 73, 75, 'GRASS:3,NORMAL:3,BUG:2,FIGHTING:2,FLYING:1', 'Grizzly Hills'),
(400, 25, 35, 'ROCK:3,FLYING:3,GROUND:3,STEEL:1', 'Thousand Needles'),
(405, 30, 40, 'GROUND:3,ROCK:2,GHOST:2,FIGHTING:2,GRASS:1', 'Desolace'),
(406, 15, 27, 'ROCK:3,FLYING:3,GROUND:2,GRASS:1', 'Stonetalon Mountains'),
(440, 40, 50, 'GROUND:3,FIRE:2,ROCK:2,WATER:2,DRAGON:1,BUG:1', 'Tanaris'),
(490, 48, 55, 'GRASS:3,ROCK:3,DRAGON:2,FIRE:2,BUG:2', 'Un''Goro Crater'),
(493, 55, 60, 'FAIRY:3,GRASS:3,PSYCHIC:2,WATER:2,FLYING:2', 'Moonglade'),
(495, 68, 72, 'ICE:3,WATER:3,FIGHTING:2,GHOST:1,DRAGON:1', 'Howling Fjord'),
(618, 53, 60, 'ICE:3,FLYING:2,PSYCHIC:2,FAIRY:2', 'Winterspring'),
(1377, 55, 60, 'BUG:3,ROCK:3,GROUND:3,PSYCHIC:2', 'Silithus'),
(3430, 1, 10, 'FAIRY:3,GRASS:2,PSYCHIC:2,FIRE:2,NORMAL:2', 'Eversong Woods'),
(3433, 10, 20, 'GHOST:3,DARK:2,PSYCHIC:2,POISON:2,NORMAL:1', 'Ghostlands'),
(3483, 58, 63, 'FIRE:3,ROCK:3,DARK:3,FIGHTING:2,DRAGON:1', 'Hellfire Peninsula'),
(3518, 64, 67, 'GRASS:3,NORMAL:3,GROUND:2,FLYING:2,FIGHTING:2', 'Nagrand'),
(3519, 62, 65, 'GRASS:3,GHOST:3,DARK:2,FLYING:2,BUG:2', 'Terokkar Forest'),
(3520, 67, 70, 'DARK:3,GHOST:3,FIRE:2,DRAGON:2,PSYCHIC:1', 'Shadowmoon Valley'),
(3521, 60, 64, 'WATER:3,GRASS:3,POISON:3,BUG:2,FAIRY:2', 'Zangarmarsh'),
(3522, 65, 68, 'ROCK:3,DRAGON:3,FLYING:2,FIGHTING:2,STEEL:2', 'Blade''s Edge Mountains'),
(3523, 67, 70, 'PSYCHIC:3,ELECTRIC:3,STEEL:2,DARK:2,DRAGON:1', 'Netherstorm'),
(3524, 1, 10, 'WATER:3,PSYCHIC:2,FAIRY:2,NORMAL:2,GRASS:2', 'Azuremyst Isle'),
(3525, 10, 20, 'GRASS:3,POISON:3,BUG:2,PSYCHIC:2,FAIRY:1', 'Bloodmyst Isle'),
(3537, 68, 72, 'ICE:3,WATER:2,NORMAL:2,FLYING:2,BUG:1', 'Borean Tundra'),
(3711, 76, 78, 'GRASS:3,WATER:3,BUG:3,POISON:2,DRAGON:2,FIRE:1', 'Sholazar Basin');
