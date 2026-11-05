-- Day Care and eggs (acore_characters).
--
-- battlemon_daycare  the (at most two) Pokemon a trainer has left at the Day Care. While there, the Pokemon's
--                    battlemon_owned row sits at guid = 0 (like a sealed Pokemon), so nothing else can touch it;
--                    this table remembers whose it is. checked_at is when eggs were last rolled for the pair.
-- battlemon_egg      eggs a trainer is holding. Everything about the baby (species, form, IVs, nature, ability,
--                    moves, shiny, gender) is rolled when the egg is made; hatch_at is when it may hatch.
--
-- Safe to run repeatedly.

CREATE TABLE IF NOT EXISTS `battlemon_daycare` (
  `guid` int unsigned NOT NULL COMMENT 'characters.guid of the trainer',
  `slot` tinyint unsigned NOT NULL COMMENT '1 or 2',
  `owned_id` int unsigned NOT NULL COMMENT 'battlemon_owned.id (its guid is 0 while here)',
  `checked_at` int unsigned NOT NULL DEFAULT '0' COMMENT 'unix time eggs were last rolled for this pair',
  PRIMARY KEY (`guid`, `slot`),
  UNIQUE KEY `owned_id` (`owned_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_egg` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `guid` int unsigned NOT NULL COMMENT 'characters.guid holding the egg',
  `species_id` int unsigned NOT NULL,
  `form_id` int unsigned NOT NULL,
  `shiny` tinyint unsigned NOT NULL DEFAULT '0',
  `gender` char(1) NOT NULL DEFAULT 'M',
  `iv_hp` tinyint unsigned NOT NULL DEFAULT '0',
  `iv_atk` tinyint unsigned NOT NULL DEFAULT '0',
  `iv_def` tinyint unsigned NOT NULL DEFAULT '0',
  `iv_spa` tinyint unsigned NOT NULL DEFAULT '0',
  `iv_spd` tinyint unsigned NOT NULL DEFAULT '0',
  `iv_spe` tinyint unsigned NOT NULL DEFAULT '0',
  `nature` tinyint unsigned NOT NULL DEFAULT '0',
  `ability_slot` tinyint unsigned NOT NULL DEFAULT '0',
  `move1` varchar(64) DEFAULT NULL,
  `move2` varchar(64) DEFAULT NULL,
  `move3` varchar(64) DEFAULT NULL,
  `move4` varchar(64) DEFAULT NULL,
  `hatch_at` int unsigned NOT NULL COMMENT 'unix time it can hatch',
  PRIMARY KEY (`id`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
