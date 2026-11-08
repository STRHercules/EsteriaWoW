-- Merchants look like player characters, and wear real equipment.
SET @has_race = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'housing_shop' AND column_name = 'race');
SET @q = IF(@has_race = 0, 'ALTER TABLE `housing_shop` ADD COLUMN `race` TINYINT UNSIGNED NOT NULL DEFAULT 1, ADD COLUMN `sex` TINYINT UNSIGNED NOT NULL DEFAULT 0, ADD COLUMN `look_hex` VARCHAR(300) NOT NULL DEFAULT \'\', ADD COLUMN `body_hex` VARCHAR(120) NOT NULL DEFAULT \'\'', 'DO 0');
PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;
CREATE TABLE IF NOT EXISTS `housing_shop_gear` (
  `placed_id` BIGINT UNSIGNED NOT NULL,
  `slot` TINYINT UNSIGNED NOT NULL,
  `item_guid` INT UNSIGNED NOT NULL,
  `owner_guid` INT UNSIGNED NOT NULL COMMENT 'the character who gave it; a bound item only goes back to them',
  PRIMARY KEY (`placed_id`, `slot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
