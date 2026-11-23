CREATE TABLE IF NOT EXISTS `character_world_pvp_bounty_murder` (
  `offender_account` int unsigned NOT NULL,
  `victim_account` int unsigned NOT NULL,
  `offender_guid` int unsigned NOT NULL,
  `occurred_at` datetime NOT NULL,
  PRIMARY KEY (`offender_account`, `victim_account`),
  KEY `idx_world_pvp_bounty_murder_character` (`offender_guid`, `occurred_at`),
  CONSTRAINT `chk_world_pvp_bounty_murder_accounts` CHECK (`offender_account` <> `victim_account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `character_world_pvp_bounty`
  DROP CHECK `chk_world_pvp_bounty_minimum`,
  DROP CHECK `chk_world_pvp_bounty_claim_state`,
  MODIFY COLUMN `state` tinyint unsigned NOT NULL DEFAULT 0
    COMMENT '0 pending, 1 funded, 2 refunded, 3 claimed, 4 redeemed, 5 expired',
  ADD COLUMN `expires_at` datetime DEFAULT NULL,
  ADD COLUMN `automatic_target` int unsigned GENERATED ALWAYS AS (
    IF(`sponsor_guid` = 0 AND `state` = 1, `target_guid`, NULL)
  ) STORED,
  ADD UNIQUE KEY `idx_world_pvp_bounty_open_automatic` (`automatic_target`),
  ADD CONSTRAINT `chk_world_pvp_bounty_source` CHECK (
    (`sponsor_guid` <> 0 AND `sponsor_account` <> 0 AND `amount` >= 1000000
      AND `state` IN (0, 1, 2, 3, 4) AND `expires_at` IS NULL)
    OR (`sponsor_guid` = 0 AND `sponsor_account` = 0 AND `amount` BETWEEN 250000 AND 2500000
      AND `state` IN (1, 3, 4, 5) AND `expires_at` IS NOT NULL)
  ),
  ADD CONSTRAINT `chk_world_pvp_bounty_settlement` CHECK (
    (`state` IN (0, 1, 2, 5) AND `hunter_guid` IS NULL AND `hunter_account` IS NULL
      AND `target_account` IS NULL AND `claimed_at` IS NULL)
    OR (`state` IN (3, 4) AND `hunter_guid` IS NOT NULL AND `hunter_account` IS NOT NULL
      AND `target_account` IS NOT NULL AND `claimed_at` IS NOT NULL)
  );
