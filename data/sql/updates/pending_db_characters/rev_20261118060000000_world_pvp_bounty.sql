CREATE TABLE IF NOT EXISTS `character_world_pvp_bounty` (
  `id` bigint unsigned NOT NULL,
  `sponsor_guid` int unsigned NOT NULL,
  `sponsor_account` int unsigned NOT NULL,
  `target_guid` int unsigned NOT NULL,
  `amount` int unsigned NOT NULL,
  `state` tinyint unsigned NOT NULL DEFAULT 0 COMMENT '0 pending, 1 funded, 2 refunded',
  PRIMARY KEY (`sponsor_guid`, `id`),
  KEY `idx_world_pvp_bounty_target` (`target_guid`, `state`),
  CONSTRAINT `chk_world_pvp_bounty_state` CHECK (`state` <= 2),
  CONSTRAINT `chk_world_pvp_bounty_minimum` CHECK (`amount` >= 1000000),
  CONSTRAINT `chk_world_pvp_bounty_distinct_characters` CHECK (`sponsor_guid` <> `target_guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
