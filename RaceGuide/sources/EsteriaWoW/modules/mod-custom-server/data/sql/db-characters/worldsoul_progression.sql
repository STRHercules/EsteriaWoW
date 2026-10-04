-- Empty-state schema for the active Worldsoul stat pipeline.
CREATE TABLE IF NOT EXISTS `ap_mastery` (
  `account_id` INT UNSIGNED NOT NULL,
  `mastery` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ap_talents` (
  `account_id` INT UNSIGNED NOT NULL,
  `stat_index` TINYINT UNSIGNED NOT NULL,
  `rank` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`account_id`, `stat_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ap_item_snapshot` (
  `account_id` INT UNSIGNED NOT NULL,
  `item_entry` INT UNSIGNED NOT NULL,
  `str` FLOAT NOT NULL DEFAULT 0,
  `agi` FLOAT NOT NULL DEFAULT 0,
  `sta` FLOAT NOT NULL DEFAULT 0,
  `int` FLOAT NOT NULL DEFAULT 0,
  `spi` FLOAT NOT NULL DEFAULT 0,
  `armor` FLOAT NOT NULL DEFAULT 0,
  `weapon_dps` FLOAT NOT NULL DEFAULT 0,
  PRIMARY KEY (`account_id`, `item_entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ap_item_attune` (
  `guid` INT UNSIGNED NOT NULL,
  `item_entry` INT UNSIGNED NOT NULL,
  `attuned` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`, `item_entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `ap_aether_sinks` (
  `account_id` INT UNSIGNED NOT NULL,
  `category` VARCHAR(32) NOT NULL,
  `invested` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`account_id`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
