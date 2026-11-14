-- Source cloak appearances share mod-transmog's account collection and visible-item persistence.
-- Converted asset tooling populates this catalog and creates its two distinct item templates.
CREATE TABLE IF NOT EXISTS `esteria_backpack_appearances` (
  `source_item` INT UNSIGNED NOT NULL,
  `token_item` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`source_item`),
  UNIQUE KEY `token_item` (`token_item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
