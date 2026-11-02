-- Paths of Fate (src/server/shared/PerkRules.h). Characters without a profile row are Unmarked with no respecs.
-- trait: the background trait picked in character creation (src/server/shared/PerkTraitWire.h; 0 = Unmarked).
-- respecs: full perk resets done; the first is free.
CREATE TABLE IF NOT EXISTS `character_esteria_perk_profile` (
  `guid` int unsigned NOT NULL,
  `trait` tinyint unsigned NOT NULL DEFAULT 0,
  `respecs` tinyint unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Purchased rank per card; card ids are PerkRules.h's.
CREATE TABLE IF NOT EXISTS `character_esteria_perks` (
  `guid` int unsigned NOT NULL,
  `perk` tinyint unsigned NOT NULL,
  `rank` tinyint unsigned NOT NULL,
  PRIMARY KEY (`guid`, `perk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ledger of purchases, respecs and repairs. Kept when the character is deleted.
-- action: 1 purchase, 2 respec, 3 repair (points spent above the level's budget, refunded), 4 GM reset.
-- spent: points spent after the action; gold: copper paid.
CREATE TABLE IF NOT EXISTS `esteria_perk_audit` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `guid` int unsigned NOT NULL,
  `time` int unsigned NOT NULL,
  `action` tinyint unsigned NOT NULL,
  `perk` tinyint unsigned NOT NULL DEFAULT 0,
  `rank` tinyint unsigned NOT NULL DEFAULT 0,
  `level` tinyint unsigned NOT NULL,
  `spent` tinyint unsigned NOT NULL,
  `gold` int unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
