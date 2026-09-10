-- Idempotent: shiny support.
--   battlemon_owned.shiny         a caught Pokémon is shiny or not
--   battlemon_account.encounter_count  drives the guaranteed shiny every 10th encounter
--   drops UNIQUE KEY guid_form    so the same form can be caught more than once

DROP PROCEDURE IF EXISTS `battlemon_add_shiny`;
DELIMITER //
CREATE PROCEDURE `battlemon_add_shiny`()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'battlemon_owned'
      AND COLUMN_NAME = 'shiny'
  ) THEN
    ALTER TABLE `battlemon_owned`
      ADD COLUMN `shiny` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '1 = shiny variant';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'battlemon_account'
      AND COLUMN_NAME = 'encounter_count'
  ) THEN
    ALTER TABLE `battlemon_account`
      ADD COLUMN `encounter_count` int unsigned NOT NULL DEFAULT '0' COMMENT 'lifetime wild encounters; every 10th is shiny';
  END IF;

  -- Duplicates are allowed now, so the one-row-per-form constraint has to go.
  IF EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'battlemon_owned'
      AND INDEX_NAME = 'guid_form'
  ) THEN
    ALTER TABLE `battlemon_owned` DROP INDEX `guid_form`;
  END IF;

  -- guid_form used to serve lookups by (guid, form_id); keep a plain index.
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'battlemon_owned'
      AND INDEX_NAME = 'guid_form_shiny'
  ) THEN
    ALTER TABLE `battlemon_owned` ADD INDEX `guid_form_shiny` (`guid`, `form_id`, `shiny`);
  END IF;
END //
DELIMITER ;
CALL `battlemon_add_shiny`();
DROP PROCEDURE IF EXISTS `battlemon_add_shiny`;
