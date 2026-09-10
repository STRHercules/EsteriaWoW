-- Sidecar API tokens for Pocketmon / external clients.
-- Pair in-game with .battlemon link, exchange the code for a long-lived token.

CREATE TABLE IF NOT EXISTS `battlemon_sidecar_token` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `guid` int unsigned NOT NULL COMMENT 'characters.guid',
  `token_hash` char(64) NOT NULL COMMENT 'sha256 hex of the bearer token',
  `created_at` int unsigned NOT NULL DEFAULT '0',
  `expires_at` int unsigned NOT NULL DEFAULT '0' COMMENT '0 = no expiry',
  `revoked` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_hash` (`token_hash`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
