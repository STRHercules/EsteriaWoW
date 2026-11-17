-- Core prepared statements require these tables before the module starts.
-- Recovered schemas only; no character selections, receipts or balances are imported.
CREATE TABLE IF NOT EXISTS `ascension_manastorm_loadout` (
  `guid` INT UNSIGNED NOT NULL,
  `slot` TINYINT UNSIGNED NOT NULL,
  `spell` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`, `slot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `manastorm_weekly_cache_lockout` (
  `guid` INT UNSIGNED NOT NULL,
  `reset_at` INT UNSIGNED NOT NULL,
  `caches_received` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`),
  CONSTRAINT `chk_manastorm_weekly_reset` CHECK (`reset_at` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `character_manastorm_stage_receipt` (
  `guid` INT UNSIGNED NOT NULL,
  `run_seed` BIGINT UNSIGNED NOT NULL,
  `run_id` BIGINT UNSIGNED NOT NULL,
  `depth` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`guid`, `run_seed`, `run_id`, `depth`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
