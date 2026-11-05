-- Individual Pokemon (acore_characters): IVs, EVs, nature, ability and original trainer.
--
-- Existing rows keep their exact stats: IVs default to 31 and EVs to 0, which is what
-- the old fixed formula assumed, and nature 0 (Hardy) is neutral. Only the ability slot
-- is rolled, because the old code re-rolled the ability every battle anyway.
-- The original trainer of an existing row is simply its current owner.
--
-- Safe to run as many times as you like: everything sits behind the iv_hp check.

DROP PROCEDURE IF EXISTS `battlemon_add_individual`;
DELIMITER $$
CREATE PROCEDURE `battlemon_add_individual`()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM `INFORMATION_SCHEMA`.`COLUMNS`
    WHERE `TABLE_SCHEMA` = DATABASE()
      AND `TABLE_NAME` = 'battlemon_owned'
      AND `COLUMN_NAME` = 'iv_hp'
  ) THEN
    ALTER TABLE `battlemon_owned`
      ADD COLUMN `iv_hp`  tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_atk` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_def` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_spa` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_spd` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_spe` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `ev_hp`  smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_atk` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_def` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_spa` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_spd` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_spe` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `nature` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-24, mainline order; 0 = Hardy (neutral)',
      ADD COLUMN `ability_slot` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0 = ability1, 1 = ability2, 2 = hidden',
      ADD COLUMN `ot_guid` int unsigned NOT NULL DEFAULT '0' COMMENT 'original trainer characters.guid; 0 = unknown';

    UPDATE `battlemon_owned` SET `ot_guid` = `guid`, `ability_slot` = IF(RAND() < 0.5, 0, 1);
  END IF;

  -- The 2D->3D migration backs removed rows up with CREATE TABLE ... LIKE battlemon_owned, and
  -- data/3d/rollback-characters.sql copies them back with SELECT *, so the two must keep the same columns.
  IF EXISTS (
    SELECT 1 FROM `INFORMATION_SCHEMA`.`TABLES`
    WHERE `TABLE_SCHEMA` = DATABASE() AND `TABLE_NAME` = 'battlemon_3d_removed_owned'
  ) AND NOT EXISTS (
    SELECT 1 FROM `INFORMATION_SCHEMA`.`COLUMNS`
    WHERE `TABLE_SCHEMA` = DATABASE()
      AND `TABLE_NAME` = 'battlemon_3d_removed_owned'
      AND `COLUMN_NAME` = 'iv_hp'
  ) THEN
    ALTER TABLE `battlemon_3d_removed_owned`
      ADD COLUMN `iv_hp`  tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_atk` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_def` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_spa` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_spd` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `iv_spe` tinyint unsigned NOT NULL DEFAULT '31',
      ADD COLUMN `ev_hp`  smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_atk` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_def` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_spa` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_spd` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `ev_spe` smallint unsigned NOT NULL DEFAULT '0',
      ADD COLUMN `nature` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0-24, mainline order; 0 = Hardy (neutral)',
      ADD COLUMN `ability_slot` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '0 = ability1, 1 = ability2, 2 = hidden',
      ADD COLUMN `ot_guid` int unsigned NOT NULL DEFAULT '0' COMMENT 'original trainer characters.guid; 0 = unknown';
  END IF;
END$$
DELIMITER ;
CALL `battlemon_add_individual`();
DROP PROCEDURE IF EXISTS `battlemon_add_individual`;
