-- Pocketmon sidecar session tokens (acore_characters).
-- Hashed at rest. expires_at = 0 means no expiry.
-- Rerunnable.

CREATE TABLE IF NOT EXISTS `battlemon_sidecar_token` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `guid` int unsigned NOT NULL COMMENT 'characters.guid',
  `token_hash` char(64) NOT NULL COMMENT 'sha256 hex of the bearer token',
  `created_at` int unsigned NOT NULL DEFAULT '0' COMMENT 'unix time',
  `expires_at` int unsigned NOT NULL DEFAULT '0' COMMENT 'unix time; 0 = never',
  `revoked` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_hash` (`token_hash`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
