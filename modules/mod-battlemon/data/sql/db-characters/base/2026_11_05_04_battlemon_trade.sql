-- Completed Pokemon trades (acore_characters): an audit trail for settling disputes. One row per trade;
-- owned_a / owned_b are battlemon_owned.id, 0 when that side gave nothing (a gift). The Pokemon keep their
-- original trainer (battlemon_owned.ot_guid), so the history of any one of them is also visible there.
-- Safe to run repeatedly.

CREATE TABLE IF NOT EXISTS `battlemon_trade_log` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `guid_a` int unsigned NOT NULL COMMENT 'characters.guid that started the trade',
  `owned_a` int unsigned NOT NULL DEFAULT '0',
  `guid_b` int unsigned NOT NULL COMMENT 'characters.guid that was invited',
  `owned_b` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `owned_a` (`owned_a`),
  KEY `owned_b` (`owned_b`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
