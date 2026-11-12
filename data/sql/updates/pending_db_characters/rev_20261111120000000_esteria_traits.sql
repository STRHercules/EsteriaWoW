-- Paths of Fate starting traits (src/server/shared/PerkTraitRules.h): a character now holds a set of traits, not one.
-- One row per chosen trait; no rows means Unmarked. character_esteria_perk_profile.trait stays for v1 clients: it
-- holds the trait when the build is exactly one original background (1-8), else 0.
CREATE TABLE IF NOT EXISTS `character_esteria_trait_selection` (
  `guid` int unsigned NOT NULL,
  `trait_id` smallint unsigned NOT NULL,
  `selected_at` int unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`, `trait_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- respecs: trait rechooses done (the first is free); counted apart from perk respecs.
CREATE TABLE IF NOT EXISTS `character_esteria_trait_state` (
  `guid` int unsigned NOT NULL,
  `respecs` smallint unsigned NOT NULL DEFAULT 0,
  `changed` int unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ledger of builds. Kept when the character is deleted.
-- action: 2 rechoose, 3 GM reset. before/after: trait ids, comma separated. gold: copper paid.
CREATE TABLE IF NOT EXISTS `esteria_trait_audit` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `guid` int unsigned NOT NULL,
  `time` int unsigned NOT NULL,
  `action` tinyint unsigned NOT NULL,
  `before` varchar(64) NOT NULL DEFAULT '',
  `after` varchar(64) NOT NULL DEFAULT '',
  `gold` int unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Characters made before this keep their background as their one trait. Running it again adds nothing: a build
-- that is not exactly one background has trait 0 in the profile.
INSERT IGNORE INTO `character_esteria_trait_selection` (`guid`, `trait_id`, `selected_at`)
SELECT `guid`, `trait`, UNIX_TIMESTAMP() FROM `character_esteria_perk_profile` WHERE `trait` BETWEEN 1 AND 8;
