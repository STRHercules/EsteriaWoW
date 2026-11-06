-- Held items (acore_characters): the item a Pokemon holds, by battlemon_items.internal_name; empty = nothing.
-- Existing Pokemon hold nothing. The 2D->3D migration's backup table is widened too, because
-- data/3d/rollback-characters.sql copies rows back with SELECT * and the two tables must keep the same columns.
-- Safe to run repeatedly.

DROP PROCEDURE IF EXISTS `battlemon_add_held_item`;
DELIMITER $$
CREATE PROCEDURE `battlemon_add_held_item`()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM `INFORMATION_SCHEMA`.`COLUMNS`
    WHERE `TABLE_SCHEMA` = DATABASE() AND `TABLE_NAME` = 'battlemon_owned' AND `COLUMN_NAME` = 'held_item'
  ) THEN
    ALTER TABLE `battlemon_owned`
      ADD COLUMN `held_item` varchar(32) NOT NULL DEFAULT '' COMMENT 'battlemon_items.internal_name held, empty = none';
  END IF;

  IF EXISTS (
    SELECT 1 FROM `INFORMATION_SCHEMA`.`TABLES`
    WHERE `TABLE_SCHEMA` = DATABASE() AND `TABLE_NAME` = 'battlemon_3d_removed_owned'
  ) AND NOT EXISTS (
    SELECT 1 FROM `INFORMATION_SCHEMA`.`COLUMNS`
    WHERE `TABLE_SCHEMA` = DATABASE() AND `TABLE_NAME` = 'battlemon_3d_removed_owned' AND `COLUMN_NAME` = 'held_item'
  ) THEN
    ALTER TABLE `battlemon_3d_removed_owned`
      ADD COLUMN `held_item` varchar(32) NOT NULL DEFAULT '' COMMENT 'battlemon_items.internal_name held, empty = none';
  END IF;
END$$
DELIMITER ;
CALL `battlemon_add_held_item`();
DROP PROCEDURE IF EXISTS `battlemon_add_held_item`;
