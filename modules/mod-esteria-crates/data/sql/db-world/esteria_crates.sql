-- Loot crates (mod-esteria-crates). Item IDs 3450000-3459999 are reserved for crates and keys.
--
-- An edition is a crate item pinned to one pool version. Never edit the rows of a pool that has shipped: to rotate,
-- add a new crate item, a new pool number and a new edition row, so crates already in bags keep the table they
-- advertised. Weights are integers; the client shows weight / total, so the odds always add up to 100%.

CREATE TABLE IF NOT EXISTS `esteria_crate_key` (
    `item` INT UNSIGNED NOT NULL,
    `price` INT UNSIGNED NOT NULL COMMENT 'copper per key, destroyed on purchase',
    `max_per_purchase` INT UNSIGNED NOT NULL DEFAULT 10,
    PRIMARY KEY (`item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `esteria_crate_edition` (
    `crate` INT UNSIGNED NOT NULL COMMENT 'crate item entry, ScriptName item_esteria_crate',
    `key_item` INT UNSIGNED NOT NULL COMMENT 'esteria_crate_key.item; one key per crate tier',
    `pool` INT UNSIGNED NOT NULL,
    `price` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'copper per crate in the crate window, 0 = not sold',
    `enabled` TINYINT UNSIGNED NOT NULL DEFAULT 1,
    PRIMARY KEY (`crate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `esteria_crate_reward` (
    `pool` INT UNSIGNED NOT NULL,
    `idx` TINYINT UNSIGNED NOT NULL COMMENT 'display order',
    `item` INT UNSIGNED NOT NULL,
    `count` INT UNSIGNED NOT NULL DEFAULT 1,
    `weight` INT UNSIGNED NOT NULL,
    `rarity` TINYINT UNSIGNED NOT NULL COMMENT 'display grade: 3 rare, 4 epic, 5 legendary, 6 artifact',
    PRIMARY KEY (`pool`, `idx`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DELETE FROM `item_template` WHERE `entry` IN (3450001, 3450101);
INSERT INTO `item_template` (`entry`, `class`, `subclass`, `name`, `displayid`, `Quality`, `InventoryType`,
`ItemLevel`, `stackable`, `maxcount`, `bonding`, `BuyPrice`, `SellPrice`, `spellid_1`, `spelltrigger_1`,
`spellcharges_1`, `ScriptName`, `description`) VALUES
(3450001, 15, 4, 'Epic Crate Key', 3450001, 4, 0, 1, 100, 0, 0, 0, 0, 0, 0, 0, '',
 'Unlocks one Epic-tier crate.'),
(3450101, 15, 4, 'Starfall Cache: Season One', 3450101, 4, 0, 1, 100, 0, 0, 0, 0, 3420001, 0, 0, 'item_esteria_crate',
 'Use: View the contents. Needs an Epic Crate Key to unlock.');

DELETE FROM `esteria_crate_key` WHERE `item` = 3450001;
INSERT INTO `esteria_crate_key` (`item`, `price`, `max_per_purchase`) VALUES
(3450001, 1000000, 10);

DELETE FROM `esteria_crate_edition` WHERE `crate` = 3450101;
INSERT INTO `esteria_crate_edition` (`crate`, `key_item`, `pool`, `price`, `enabled`) VALUES
(3450101, 3450001, 1, 250000, 1);

-- Pool 1 (Starfall Cache: Season One), out of 10000: 7 x 12%, 1 x 10%, 3 x 2%.
DELETE FROM `esteria_crate_reward` WHERE `pool` = 1;
INSERT INTO `esteria_crate_reward` (`pool`, `idx`, `item`, `count`, `weight`, `rarity`) VALUES
(1, 0, 33224, 1, 1200, 3),
(1, 1, 25535, 1, 1200, 3),
(1, 2, 34492, 1, 1200, 3),
(1, 3, 34425, 1, 1200, 3),
(1, 4, 3410101, 1, 1200, 4),
(1, 5, 3410102, 1, 1200, 4),
(1, 6, 3410103, 1, 1200, 4),
(1, 7, 32858, 1, 1000, 4),
(1, 8, 3430084, 1, 200, 5),
(1, 9, 3430085, 1, 200, 5),
(1, 10, 3430086, 1, 200, 5);
