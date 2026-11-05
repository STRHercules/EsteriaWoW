-- Following Pokemon (acore_characters): which Pokemon walks behind its trainer.
-- owned_id is battlemon_owned.id. One row per character; deleted when the player turns it off, and dropped by
-- the server if the Pokemon is traded away, sealed in a ball or deleted. Safe to run repeatedly.

CREATE TABLE IF NOT EXISTS `battlemon_follower` (
  `guid` int unsigned NOT NULL COMMENT 'characters.guid',
  `owned_id` int unsigned NOT NULL COMMENT 'battlemon_owned.id',
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
