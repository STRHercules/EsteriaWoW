ALTER TABLE `character_world_pvp_bounty`
  DROP CHECK `chk_world_pvp_bounty_state`,
  MODIFY COLUMN `state` tinyint unsigned NOT NULL DEFAULT 0
    COMMENT '0 pending, 1 funded, 2 refunded, 3 claimed, 4 redeemed',
  ADD COLUMN `hunter_guid` int unsigned DEFAULT NULL,
  ADD COLUMN `hunter_account` int unsigned DEFAULT NULL,
  ADD COLUMN `target_account` int unsigned DEFAULT NULL,
  ADD COLUMN `claimed_at` datetime DEFAULT NULL,
  ADD KEY `idx_world_pvp_bounty_hunter` (`hunter_guid`, `hunter_account`, `state`),
  ADD KEY `idx_world_pvp_bounty_repeat` (`hunter_account`, `target_account`, `claimed_at`),
  ADD CONSTRAINT `chk_world_pvp_bounty_claim_state` CHECK (
    (`state` IN (0, 1, 2) AND `hunter_guid` IS NULL AND `hunter_account` IS NULL
      AND `target_account` IS NULL AND `claimed_at` IS NULL)
    OR (`state` IN (3, 4) AND `hunter_guid` IS NOT NULL AND `hunter_account` IS NOT NULL
      AND `target_account` IS NOT NULL AND `claimed_at` IS NOT NULL)
  );
