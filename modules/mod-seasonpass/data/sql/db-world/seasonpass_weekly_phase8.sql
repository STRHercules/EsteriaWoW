CREATE TABLE IF NOT EXISTS `seasonpass_weekly_rotation` (
  `season` INT UNSIGNED NOT NULL,
  `week` INT UNSIGNED NOT NULL,
  `slot` TINYINT UNSIGNED NOT NULL,
  `objective` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`season`, `week`, `slot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
