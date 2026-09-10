-- What the Battlemon shop sells and what it costs in Battlemon Points.
-- Deliberately separate from battlemon_items.price: that column is in Pokemon
-- dollars (a Potion is 200) which is meaningless next to WinPoints = 10.
-- Edit a row and reload the catalog to reprice without a rebuild.

CREATE TABLE IF NOT EXISTS `battlemon_shop` (
  `item_internal_name` varchar(64) NOT NULL COMMENT 'battlemon_items.internal_name',
  `cost` int unsigned NOT NULL COMMENT 'Battlemon Points',
  `sort_order` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`item_internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

REPLACE INTO `battlemon_shop` (`item_internal_name`, `cost`, `sort_order`) VALUES
('POKEBALL',    5,  10),
('GREATBALL',   12, 20),
('ULTRABALL',   25, 30),
('MASTERBALL',  500, 40),
('POTION',      8,  50),
('SUPERPOTION', 20, 60),
('HYPERPOTION', 40, 70),
('MAXPOTION',   70, 80);
