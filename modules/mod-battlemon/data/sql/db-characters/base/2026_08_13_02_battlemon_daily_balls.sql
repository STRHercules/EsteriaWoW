-- Idempotent: add balls_granted_day (YYYYMMDD) for the daily Poké Ball grant.

DROP PROCEDURE IF EXISTS `battlemon_add_balls_granted_day`;
DELIMITER //
CREATE PROCEDURE `battlemon_add_balls_granted_day`()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'battlemon_account'
      AND COLUMN_NAME = 'balls_granted_day'
  ) THEN
    ALTER TABLE `battlemon_account`
      ADD COLUMN `balls_granted_day` int unsigned NOT NULL DEFAULT '0' COMMENT 'YYYYMMDD last daily Poké Ball grant';
  END IF;
END //
DELIMITER ;
CALL `battlemon_add_balls_granted_day`();
DROP PROCEDURE IF EXISTS `battlemon_add_balls_granted_day`;
