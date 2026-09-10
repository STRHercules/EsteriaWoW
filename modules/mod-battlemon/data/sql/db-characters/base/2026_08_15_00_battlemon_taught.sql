-- Idempotent: tutor moves a Pokémon has already been taught.
-- Paying once per (owned Pokémon, move) means swapping a bought move out and
-- back in later is free, so players can experiment without being punished.

CREATE TABLE IF NOT EXISTS `battlemon_owned_taught` (
  `owned_id` int unsigned NOT NULL COMMENT 'battlemon_owned.id',
  `move_internal_name` varchar(64) NOT NULL,
  PRIMARY KEY (`owned_id`,`move_internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
