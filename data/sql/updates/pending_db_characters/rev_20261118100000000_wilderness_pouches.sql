CREATE TABLE IF NOT EXISTS `character_wilderness_pouch` (
  `id` bigint unsigned NOT NULL,
  `owner_guid` int unsigned NOT NULL,
  `owner_account` int unsigned NOT NULL,
  `map_id` smallint unsigned NOT NULL,
  `phase_mask` int unsigned NOT NULL,
  `x` float NOT NULL,
  `y` float NOT NULL,
  `z` float NOT NULL,
  `copper` int unsigned NOT NULL,
  `owner_until` datetime(6) NOT NULL,
  `funded` tinyint unsigned NOT NULL DEFAULT 0,
  `claimant_guid` int unsigned NOT NULL DEFAULT 0,
  `claim_nonce` bigint unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_wilderness_pouch_location` (`map_id`, `funded`, `claimant_guid`, `x`),
  CONSTRAINT `chk_wilderness_pouch_copper` CHECK (`copper` > 0),
  CONSTRAINT `chk_wilderness_pouch_funded` CHECK (`funded` IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
