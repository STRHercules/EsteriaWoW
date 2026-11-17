-- Loot crate receipts (mod-esteria-crates). Each row commits in the same transaction as the inventory change.

CREATE TABLE IF NOT EXISTS `esteria_crate_opening` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `guid` INT UNSIGNED NOT NULL,
    `account` INT UNSIGNED NOT NULL,
    `request` VARCHAR(16) NOT NULL COMMENT 'client idempotency id',
    `crate` INT UNSIGNED NOT NULL,
    `key_item` INT UNSIGNED NOT NULL,
    `pool` INT UNSIGNED NOT NULL,
    `reward` INT UNSIGNED NOT NULL,
    `count` INT UNSIGNED NOT NULL,
    `roll` INT UNSIGNED NOT NULL COMMENT '1..pool total weight',
    `mailed` TINYINT UNSIGNED NOT NULL COMMENT '0 bags, 1 mail, 2 Esteria storage',
    `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `guid_request` (`guid`, `request`),
    KEY `crate_pool` (`crate`, `pool`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `esteria_crate_purchase` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `guid` INT UNSIGNED NOT NULL,
    `account` INT UNSIGNED NOT NULL,
    `request` VARCHAR(16) NOT NULL,
    `item` INT UNSIGNED NOT NULL COMMENT 'key or crate bought',
    `quantity` INT UNSIGNED NOT NULL,
    `unit_price` INT UNSIGNED NOT NULL,
    `total` BIGINT UNSIGNED NOT NULL COMMENT 'copper removed from the economy',
    `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `guid_request` (`guid`, `request`),
    KEY `item_created` (`item`, `created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
