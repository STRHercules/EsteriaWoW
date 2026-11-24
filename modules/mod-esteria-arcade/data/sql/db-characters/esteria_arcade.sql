-- Per character, per game: battery RAM and the resume state, both [u32 rawSize][zlib] blobs from the client.
CREATE TABLE IF NOT EXISTS `character_arcade_save` (
  `guid` INT UNSIGNED NOT NULL,
  `game` INT UNSIGNED NOT NULL,
  `sram` LONGBLOB NULL,
  `state` LONGBLOB NULL,
  `updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`guid`, `game`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- House cabinets: per owning account, what guests pay (copper) and the coins collected for the owner.
CREATE TABLE IF NOT EXISTS `esteria_arcade_house` (
  `account` INT UNSIGNED NOT NULL,
  `guest_price` INT UNSIGNED NOT NULL DEFAULT 5000,
  `earnings` BIGINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `character_arcade_skin` (
  `account` INT UNSIGNED NOT NULL,
  `skin` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`account`, `skin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `esteria_arcade_placed_skin` (
  `placed_id` BIGINT UNSIGNED NOT NULL COMMENT 'housing_placed_decor.placed_id',
  `skin` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`placed_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
