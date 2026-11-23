ALTER TABLE `character_wilderness_pouch`
  ADD COLUMN `item_guid` int unsigned DEFAULT NULL,
  ADD COLUMN `item_entry` int unsigned NOT NULL DEFAULT 0,
  ADD COLUMN `item_value` int unsigned NOT NULL DEFAULT 0,
  ADD COLUMN `owner_only_item` tinyint unsigned NOT NULL DEFAULT 0,
  ADD COLUMN `active_item_guid` int unsigned GENERATED ALWAYS AS
    (IF(`claimant_guid` = 0, `item_guid`, NULL)) STORED,
  ADD UNIQUE KEY `uq_wilderness_pouch_active_item` (`active_item_guid`),
  DROP CHECK `chk_wilderness_death_loss`,
  DROP CHECK `chk_wilderness_pouch_claim_fee`,
  ADD CONSTRAINT `chk_wilderness_death_loss` CHECK (`copper` > 0 OR `xp_loss` > 0 OR `item_guid` IS NOT NULL),
  ADD CONSTRAINT `chk_wilderness_pouch_claim_fee` CHECK (`claim_fee` <= `copper` + `item_value`),
  ADD CONSTRAINT `chk_wilderness_gear_only` CHECK (`item_guid` IS NULL OR (`copper` = 0 AND `item_entry` > 0));
