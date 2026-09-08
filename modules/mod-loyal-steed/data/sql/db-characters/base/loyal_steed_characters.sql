-- mod-loyal-steed character SQL

-- Owner tracking table
CREATE TABLE IF NOT EXISTS `rangers_war_horse_owner` (
  `owner_guid` int unsigned NOT NULL,
  `horse_guid` int unsigned NOT NULL DEFAULT 0,
  `display_id` int unsigned NOT NULL DEFAULT 28918,
  `mount_spell_id` int unsigned NOT NULL DEFAULT 22717,
  `logged_out_mounted` tinyint unsigned NOT NULL DEFAULT 0,
  `is_camping` tinyint unsigned NOT NULL DEFAULT 0,
  `camp_x` float NOT NULL DEFAULT 0,
  `camp_y` float NOT NULL DEFAULT 0,
  `camp_z` float NOT NULL DEFAULT 0,
  `camp_o` float NOT NULL DEFAULT 0,
  `camp_map` int unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`owner_guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Fast travel points table
CREATE TABLE IF NOT EXISTS `rangers_horse_travel_points` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `owner_guid` int unsigned NOT NULL,
  `name` varchar(64) NOT NULL DEFAULT 'Unknown',
  `map_id` smallint unsigned NOT NULL DEFAULT 0,
  `x` float NOT NULL DEFAULT 0,
  `y` float NOT NULL DEFAULT 0,
  `z` float NOT NULL DEFAULT 0,
  `orientation` float NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `owner_guid` (`owner_guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
