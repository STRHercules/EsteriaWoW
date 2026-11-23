ALTER TABLE `character_world_pvp_pickpocket`
  ADD COLUMN `item_guid` int unsigned NOT NULL DEFAULT 0 AFTER `amount`,
  ADD COLUMN `item_count` int unsigned NOT NULL DEFAULT 0 AFTER `item_guid`,
  ADD COLUMN `mail_id` int unsigned NOT NULL DEFAULT 0 AFTER `item_count`,
  ADD CONSTRAINT `chk_world_pvp_pickpocket_item` CHECK (
    (`item_guid` = 0 AND `item_count` = 0 AND `mail_id` = 0) OR
    (`item_guid` > 0 AND `item_count` BETWEEN 1 AND 5 AND `mail_id` > 0)
  );
