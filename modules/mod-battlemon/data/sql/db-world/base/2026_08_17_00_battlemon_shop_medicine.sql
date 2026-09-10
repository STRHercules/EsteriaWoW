-- Medicine for the Battlemon shop (acore_world).
--
-- Fainting now sticks between battles, so there has to be something to spend
-- Battlemon Points on that fixes it. A Revive brings one back at half health, a
-- Max Revive at full; both skip the automatic Battlemon.FaintReviveHours wait.
-- The sprays are priced as cheap convenience: a status lasts one battle, so
-- curing it is worth less than a heal.
--
-- Every internal_name here already exists in battlemon_items
-- (2026_08_13_03_battlemon_catalog_items.sql). Safe to run repeatedly.

CREATE TABLE IF NOT EXISTS `battlemon_shop` (
  `item_internal_name` varchar(64) NOT NULL COMMENT 'battlemon_items.internal_name',
  `cost` int unsigned NOT NULL COMMENT 'Battlemon Points',
  `sort_order` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`item_internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sorts after the balls (10-40) and potions (50-80) from the original file.
REPLACE INTO `battlemon_shop` (`item_internal_name`, `cost`, `sort_order`) VALUES
('REVIVE',       10,  90),
('MAXREVIVE',    25,  100),
('AWAKENING',    5,   110),
('ANTIDOTE',     5,   120),
('BURNHEAL',     5,   130),
('PARALYZEHEAL', 5,   140),
('ICEHEAL',      5,   150),
('FULLHEAL',     12,  160),
('FULLRESTORE',  60,  170);
