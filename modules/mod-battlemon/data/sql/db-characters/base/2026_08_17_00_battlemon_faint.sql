-- Fainting now carries between battles (acore_characters).
--
-- battlemon_owned.hp = 0 already meant "fainted", but the encounter healed the
-- whole party on the way in so it never mattered. This records when a Pokemon
-- went down, which is what the automatic revive timer counts from
-- (Battlemon.FaintReviveHours, half health on its own, or instantly with a
-- Revive from the shop).
--
-- Safe to run as many times as you like.

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
  `fainted_at` int unsigned NOT NULL DEFAULT '0' COMMENT 'unix time it fainted; 0 = conscious',
  `move1` varchar(64) DEFAULT NULL,
  `move2` varchar(64) DEFAULT NULL,
  `move3` varchar(64) DEFAULT NULL,
  `move4` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guid_form` (`guid`,`form_id`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ADD COLUMN IF NOT EXISTS is MariaDB-only, so ask the catalog instead. This is
-- the branch that runs on an install that already has the table.
DROP PROCEDURE IF EXISTS `battlemon_add_fainted_at`;
DELIMITER $$
CREATE PROCEDURE `battlemon_add_fainted_at`()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM `INFORMATION_SCHEMA`.`COLUMNS`
    WHERE `TABLE_SCHEMA` = DATABASE()
      AND `TABLE_NAME` = 'battlemon_owned'
      AND `COLUMN_NAME` = 'fainted_at'
  ) THEN
    ALTER TABLE `battlemon_owned`
      ADD COLUMN `fainted_at` int unsigned NOT NULL DEFAULT '0'
      COMMENT 'unix time it fainted; 0 = conscious' AFTER `hp`;

    -- Everything caught before this change was stored with hp = 0, because HP
    -- out of battle was never read. Left alone the entire existing collection
    -- would now read as fainted, so bring it all round. Any positive value
    -- means "conscious"; the encounter fills it to maximum anyway.
    --
    -- This lives inside the IF on purpose. Running it unconditionally would
    -- resurrect a genuinely fainted team every time the file is reapplied.
    UPDATE `battlemon_owned` SET `hp` = 1 WHERE `hp` = 0;
  END IF;
END$$
DELIMITER ;
CALL `battlemon_add_fainted_at`();
DROP PROCEDURE IF EXISTS `battlemon_add_fainted_at`;
