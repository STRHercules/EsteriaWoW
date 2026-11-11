-- Esteria incarnations: the display a character chose for each form / demon category (see Incarnations.h).
CREATE TABLE IF NOT EXISTS `character_incarnation` (
  `guid` int unsigned NOT NULL,
  `category` int unsigned NOT NULL,
  `display` int unsigned NOT NULL,
  PRIMARY KEY (`guid`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
