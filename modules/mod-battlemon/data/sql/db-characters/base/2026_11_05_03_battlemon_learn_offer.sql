-- Moves waiting for an answer (acore_characters): a Pokemon that already knows four moves reached the level a
-- fifth is learned at. After the battle the player is asked which move to forget, or to skip it (mainline
-- behaviour). A skipped move stays learnable from the move manager. Offers whose Pokemon is gone are ignored
-- and cleaned up on the next prompt. Safe to run repeatedly.

CREATE TABLE IF NOT EXISTS `battlemon_learn_offer` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT 'order the offers were made in',
  `owned_id` int unsigned NOT NULL COMMENT 'battlemon_owned.id',
  `move_internal_name` varchar(64) NOT NULL COMMENT 'battlemon_moves.internal_name',
  `level` tinyint unsigned NOT NULL DEFAULT '1' COMMENT 'level it was learnable at',
  PRIMARY KEY (`id`),
  UNIQUE KEY `owned_move` (`owned_id`, `move_internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
