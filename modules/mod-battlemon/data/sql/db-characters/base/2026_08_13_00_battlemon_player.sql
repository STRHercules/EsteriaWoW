-- Battlemon per-character progress (acore_characters)
-- Collection is unique per form (Front sprite). Party is up to 6; slot 1 is the lead.

CREATE TABLE IF NOT EXISTS `battlemon_account` (
  `guid` int unsigned NOT NULL COMMENT 'characters.guid',
  `next_encounter_at` int unsigned NOT NULL DEFAULT '0' COMMENT 'unix time; 0 = Fight ready',
  `pokeballs` int unsigned NOT NULL DEFAULT '10',
  `points` int unsigned NOT NULL DEFAULT '0' COMMENT 'Battlemon Points for shops / NPC rewards',
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_owned` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `guid` int unsigned NOT NULL COMMENT 'characters.guid',
  `form_id` int unsigned NOT NULL,
  `species_id` int unsigned NOT NULL,
  `sprite` varchar(128) NOT NULL,
  `level` tinyint unsigned NOT NULL DEFAULT '1',
  `exp` int unsigned NOT NULL DEFAULT '0',
  `gender` char(1) NOT NULL DEFAULT 'M',
  `hp` int unsigned NOT NULL DEFAULT '0',
  `move1` varchar(64) DEFAULT NULL,
  `move2` varchar(64) DEFAULT NULL,
  `move3` varchar(64) DEFAULT NULL,
  `move4` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guid_form` (`guid`,`form_id`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_party` (
  `guid` int unsigned NOT NULL COMMENT 'characters.guid',
  `slot` tinyint unsigned NOT NULL COMMENT '1-6; slot 1 is the lead',
  `owned_id` int unsigned NOT NULL,
  PRIMARY KEY (`guid`,`slot`),
  KEY `owned_id` (`owned_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
