-- Esteria casino (mod-esteria-casino): the house account, rounds and the gold ledger.
-- Every gold move commits in the same transaction as the player's saved money, so a crash keeps all of it or none.
-- The worldserver creates the single casino_house row on first start.

CREATE TABLE IF NOT EXISTS `casino_house` (
    `id` TINYINT UNSIGNED NOT NULL,
    `bankroll` BIGINT NOT NULL DEFAULT 0 COMMENT 'copper the house owns: GM deposits plus net player losses',
    `earned` BIGINT NOT NULL DEFAULT 0 COMMENT 'net copper won from players since creation',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `casino_round` (
    `id` BIGINT UNSIGNED NOT NULL,
    `game` VARCHAR(16) NOT NULL,
    `guid` INT UNSIGNED NOT NULL,
    `account` INT UNSIGNED NOT NULL,
    `dealer` INT UNSIGNED NOT NULL COMMENT 'creature entry that hosted the round',
    `wagered` BIGINT UNSIGNED NOT NULL COMMENT 'copper held in escrow, doubles and splits included',
    `paid` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'copper returned to the player, stake included',
    `state` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 open (escrowed), 1 settled, 2 refunded',
    `result` VARCHAR(128) NOT NULL DEFAULT '' COMMENT 'final cards, for audit',
    `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `settled` TIMESTAMP NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `state` (`state`),
    KEY `guid_created` (`guid`, `created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `casino_ledger` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `round` BIGINT UNSIGNED NOT NULL COMMENT '0 for house deposits and withdrawals',
    `guid` INT UNSIGNED NOT NULL,
    `player_delta` BIGINT NOT NULL COMMENT 'copper into (+) or out of (-) the character',
    `house_delta` BIGINT NOT NULL COMMENT 'copper into (+) or out of (-) the house bankroll',
    `reason` VARCHAR(16) NOT NULL COMMENT 'bet, double, split, settle, mailed, refund, fund, withdraw',
    `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `round` (`round`),
    KEY `guid_created` (`guid`, `created`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `casino_player` (
    `account` INT UNSIGNED NOT NULL,
    `day` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'UTC days since 1970 that `wagered` counts',
    `wagered` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `excluded_until` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'unix time; self-exclusion cannot be shortened',
    PRIMARY KEY (`account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- The lottery: one state row (created by the worldserver), every ticket, and every draw.
CREATE TABLE IF NOT EXISTS `casino_lottery` (
    `id` TINYINT UNSIGNED NOT NULL,
    `pool` BIGINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'copper held for prizes: ticket sales plus the house share',
    `draw` INT UNSIGNED NOT NULL DEFAULT 1 COMMENT 'number of the next draw',
    `next_draw` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'unix time',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `casino_lottery_ticket` (
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `draw` INT UNSIGNED NOT NULL,
    `guid` INT UNSIGNED NOT NULL,
    `account` INT UNSIGNED NOT NULL,
    `numbers` VARCHAR(16) NOT NULL COMMENT 'four numbers, ascending, comma separated',
    `cost` BIGINT UNSIGNED NOT NULL,
    `matched` TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `prize` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `draw_guid` (`draw`, `guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `casino_lottery_draw` (
    `draw` INT UNSIGNED NOT NULL,
    `numbers` VARCHAR(16) NOT NULL,
    `tickets` INT UNSIGNED NOT NULL,
    `pool` BIGINT UNSIGNED NOT NULL COMMENT 'pool before the draw',
    `paid` BIGINT UNSIGNED NOT NULL,
    `rollover` BIGINT UNSIGNED NOT NULL,
    `jackpot_winners` INT UNSIGNED NOT NULL,
    `three_winners` INT UNSIGNED NOT NULL,
    `drawn` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`draw`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
