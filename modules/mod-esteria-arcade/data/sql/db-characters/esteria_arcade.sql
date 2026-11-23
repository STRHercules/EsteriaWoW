-- Per character, per game: battery RAM and the resume state, both [u32 rawSize][zlib] blobs from the client.
CREATE TABLE IF NOT EXISTS `character_arcade_save` (
  `guid` INT UNSIGNED NOT NULL,
  `game` INT UNSIGNED NOT NULL,
  `sram` LONGBLOB NULL,
  `state` LONGBLOB NULL,
  `updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`guid`, `game`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
