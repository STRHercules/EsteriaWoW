-- Sealed Pokemon (acore_characters): which Poke Ball item holds which Pokemon.
--
-- A sealed Pokemon keeps its battlemon_owned row but with guid = 0, so it belongs to nobody and shows up in
-- nobody's collection until its ball is used. item_guid is item_instance.guid. Rows are created and removed
-- together with the item inside one transaction (src/BattlemonBall.cpp).
--
-- Orphans (ball destroyed by a mail purge or a GM; Pokemon left at guid = 0 with no live item) are listed by:
--   SELECT o.id, o.species_id, o.level, o.ot_guid FROM battlemon_owned o
--   LEFT JOIN battlemon_ball_item b ON b.owned_id = o.id
--   LEFT JOIN item_instance i ON i.guid = b.item_guid
--   WHERE o.guid = 0 AND i.guid IS NULL;
-- and can be handed back by setting battlemon_owned.guid to a character guid.
--
-- Safe to run as many times as you like.

CREATE TABLE IF NOT EXISTS `battlemon_ball_item` (
  `item_guid` int unsigned NOT NULL COMMENT 'item_instance.guid of the Poke Ball',
  `owned_id` int unsigned NOT NULL COMMENT 'battlemon_owned.id of the sealed Pokemon',
  PRIMARY KEY (`item_guid`),
  UNIQUE KEY `owned_id` (`owned_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
