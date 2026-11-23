ALTER TABLE `character_world_pvp_bounty`
  DROP CHECK `chk_world_pvp_bounty_source`,
  DROP CHECK `chk_world_pvp_bounty_settlement`,
  MODIFY COLUMN `state` tinyint unsigned NOT NULL DEFAULT 0
    COMMENT '0 pending, 1 funded, 2 refunded, 3 claimed, 4 redeemed, 5 expired, 6 refund queued',
  ADD COLUMN `refund_mail_id` int unsigned DEFAULT NULL,
  ADD KEY `idx_world_pvp_bounty_expiration` (`state`, `expires_at`);
UPDATE `character_world_pvp_bounty` SET `expires_at` =
  UTC_TIMESTAMP() + INTERVAL 7 DAY
WHERE `sponsor_guid` <> 0 AND `state` = 1 AND `expires_at` IS NULL;
ALTER TABLE `character_world_pvp_bounty`
  ADD CONSTRAINT `chk_world_pvp_bounty_source` CHECK (
    (`sponsor_guid` <> 0 AND `sponsor_account` <> 0 AND `amount` >= 1000000
      AND `state` IN (0, 1, 2, 3, 4, 6) AND (`state` NOT IN (1, 6) OR `expires_at` IS NOT NULL))
    OR (`sponsor_guid` = 0 AND `sponsor_account` = 0 AND `amount` BETWEEN 250000 AND 2500000
      AND `state` IN (1, 3, 4, 5) AND `expires_at` IS NOT NULL)
  ),
  ADD CONSTRAINT `chk_world_pvp_bounty_settlement` CHECK (
    (`state` IN (0, 1, 2, 5, 6) AND `hunter_guid` IS NULL AND `hunter_account` IS NULL
      AND `target_account` IS NULL AND `claimed_at` IS NULL)
    OR (`state` IN (3, 4) AND `hunter_guid` IS NOT NULL AND `hunter_account` IS NOT NULL
      AND `target_account` IS NOT NULL AND `claimed_at` IS NOT NULL)
  ),
  ADD CONSTRAINT `chk_world_pvp_bounty_refund_mail` CHECK (
    `refund_mail_id` IS NULL OR (`sponsor_guid` <> 0 AND `state` = 2)
  );
ALTER TABLE `character_world_pvp_bounty_murder`
  ADD COLUMN `counts_for_bounty` tinyint unsigned NOT NULL DEFAULT 1;
