-- Idempotent event deduplication for season-pass progression.
CREATE TABLE IF NOT EXISTS `character_seasonpass_event_credit` (
  `guid` INT UNSIGNED NOT NULL,
  `season` INT UNSIGNED NOT NULL,
  `event_type` TINYINT UNSIGNED NOT NULL,
  `source_id` BIGINT UNSIGNED NOT NULL,
  `source_started_at` BIGINT UNSIGNED NOT NULL,
  `detail_id` BIGINT UNSIGNED NOT NULL,
  `claimed_at` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`guid`, `season`, `event_type`, `source_id`, `source_started_at`, `detail_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
