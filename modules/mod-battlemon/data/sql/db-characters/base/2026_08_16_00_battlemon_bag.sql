-- Idempotent: the bag replaces battlemon_account.pokeballs as the one place
-- inventory lives, now that there is more than one kind of ball.

CREATE TABLE IF NOT EXISTS `battlemon_bag` (
  `guid` int unsigned NOT NULL,
  `item_internal_name` varchar(64) NOT NULL COMMENT 'battlemon_items.internal_name',
  `count` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guid`,`item_internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fold the old flat counter in. The ON DUPLICATE no-op is what makes this safe
-- to re-run: a second pass must not stack another copy on top of balls the
-- player has since spent or bought.
INSERT INTO `battlemon_bag` (`guid`, `item_internal_name`, `count`)
  SELECT `guid`, 'POKEBALL', `pokeballs` FROM `battlemon_account` WHERE `pokeballs` > 0
  ON DUPLICATE KEY UPDATE `count` = `count`;
