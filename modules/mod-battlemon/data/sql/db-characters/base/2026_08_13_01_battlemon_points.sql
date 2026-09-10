-- Idempotent: 2026_08_13_00_battlemon_player.sql already creates `points`.
-- This only adds the column if an older battlemon_account exists without it.

DROP PROCEDURE IF EXISTS `battlemon_add_points_column`;
DELIMITER //
CREATE PROCEDURE `battlemon_add_points_column`()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'battlemon_account'
      AND COLUMN_NAME = 'points'
  ) THEN
    ALTER TABLE `battlemon_account`
      ADD COLUMN `points` int unsigned NOT NULL DEFAULT '0' COMMENT 'Battlemon Points for shops / NPC rewards';
  END IF;
END //
DELIMITER ;
CALL `battlemon_add_points_column`();
DROP PROCEDURE IF EXISTS `battlemon_add_points_column`;
