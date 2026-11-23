ALTER TABLE `character_wilderness_pouch`
  ADD COLUMN `xp_loss` int unsigned NOT NULL DEFAULT 0 AFTER `copper`,
  DROP CHECK `chk_wilderness_pouch_copper`,
  ADD CONSTRAINT `chk_wilderness_death_loss` CHECK (`copper` > 0 OR `xp_loss` > 0);
