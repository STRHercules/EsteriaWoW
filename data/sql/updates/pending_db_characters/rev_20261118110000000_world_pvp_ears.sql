CREATE TABLE IF NOT EXISTS `character_world_pvp_ear` (
  `item_guid` int unsigned NOT NULL,
  `mail_id` int unsigned NOT NULL,
  `killer_guid` int unsigned NOT NULL,
  `victim_guid` int unsigned NOT NULL,
  `account_low` int unsigned NOT NULL,
  `account_high` int unsigned NOT NULL,
  `awarded_at` datetime(6) NOT NULL,
  PRIMARY KEY (`item_guid`),
  UNIQUE KEY `uq_world_pvp_ear_mail` (`mail_id`),
  KEY `idx_world_pvp_ear_pair` (`account_low`, `account_high`, `awarded_at`),
  CONSTRAINT `chk_world_pvp_ear_accounts` CHECK (`account_low` < `account_high`),
  CONSTRAINT `chk_world_pvp_ear_characters` CHECK (`killer_guid` <> `victim_guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
