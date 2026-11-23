ALTER TABLE `character_wilderness_pouch`
  ADD COLUMN `auction_at` datetime(6) DEFAULT NULL AFTER `owner_until`,
  ADD COLUMN `claim_fee` int unsigned NOT NULL DEFAULT 0 AFTER `claim_nonce`,
  ADD KEY `idx_wilderness_pouch_auction` (`funded`, `claimant_guid`, `auction_at`),
  ADD CONSTRAINT `chk_wilderness_pouch_claim_fee` CHECK (`claim_fee` <= `copper`);
UPDATE `character_wilderness_pouch` SET
  `auction_at` = GREATEST(`owner_until` + INTERVAL 13 MINUTE, UTC_TIMESTAMP(6) + INTERVAL 15 MINUTE)
WHERE `funded` = 1 AND `claimant_guid` = 0 AND `copper` > 0 AND `auction_at` IS NULL;
