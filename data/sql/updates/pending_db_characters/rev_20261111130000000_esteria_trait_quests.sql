-- High Roller: quests that were in the log when the character died, until they are handed in or abandoned.
CREATE TABLE IF NOT EXISTS `character_esteria_trait_questdeath` (
  `guid` int unsigned NOT NULL,
  `quest` int unsigned NOT NULL,
  PRIMARY KEY (`guid`, `quest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
