CREATE TABLE IF NOT EXISTS `character_world_pvp_pickpocket` (
  `thief_account` int unsigned NOT NULL,
  `victim_account` int unsigned NOT NULL,
  `nonce` bigint unsigned NOT NULL,
  `thief_guid` int unsigned NOT NULL,
  `victim_guid` int unsigned NOT NULL,
  `amount` int unsigned NOT NULL,
  `settled` tinyint unsigned NOT NULL DEFAULT 0,
  `attempted_at` datetime NOT NULL,
  PRIMARY KEY (`thief_account`, `victim_account`, `nonce`),
  KEY `idx_world_pvp_pickpocket_cooldown` (`thief_account`, `victim_account`, `attempted_at`),
  KEY `idx_world_pvp_pickpocket_exposure` (`thief_guid`, `thief_account`, `attempted_at`),
  CONSTRAINT `chk_world_pvp_pickpocket_accounts` CHECK (`thief_account` <> `victim_account`),
  CONSTRAINT `chk_world_pvp_pickpocket_characters` CHECK (`thief_guid` <> `victim_guid`),
  CONSTRAINT `chk_world_pvp_pickpocket_amount` CHECK (`amount` <= 50000),
  CONSTRAINT `chk_world_pvp_pickpocket_settlement` CHECK (`settled` IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
