CREATE TABLE IF NOT EXISTS `character_world_pvp_murder_log` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `killer_guid` int unsigned NOT NULL,
  `victim_guid` int unsigned NOT NULL,
  `zone_id` int unsigned NOT NULL DEFAULT 0,
  `occurred_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_world_pvp_murder_log_killer` (`killer_guid`, `occurred_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
