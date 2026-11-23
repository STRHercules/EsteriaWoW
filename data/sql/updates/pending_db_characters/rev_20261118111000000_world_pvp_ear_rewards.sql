CREATE TABLE IF NOT EXISTS `character_world_pvp_ear_purchase` (
  `reward_guid` int unsigned NOT NULL,
  `mail_id` int unsigned NOT NULL,
  `buyer_guid` int unsigned NOT NULL,
  `reward_entry` int unsigned NOT NULL,
  `ear_cost` tinyint unsigned NOT NULL,
  `funded` tinyint unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`reward_guid`),
  UNIQUE KEY `uq_world_pvp_ear_purchase_mail` (`mail_id`),
  CONSTRAINT `chk_world_pvp_ear_purchase_cost` CHECK (`ear_cost` > 0),
  CONSTRAINT `chk_world_pvp_ear_purchase_funded` CHECK (`funded` IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
ALTER TABLE `character_world_pvp_ear`
  ADD COLUMN `spent_reward_guid` int unsigned NOT NULL DEFAULT 0,
  ADD KEY `idx_world_pvp_ear_spend` (`killer_guid`, `spent_reward_guid`, `awarded_at`),
  ADD KEY `idx_world_pvp_ear_spent_reward` (`spent_reward_guid`);
