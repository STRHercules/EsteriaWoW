-- Move pools for the out-of-combat move manager.
--   battlemon_species_tutor_moves  TM/tutor pool; costs Battlemon Points to teach
--   battlemon_form_moves           per-form overrides (Alolan, Galarian, ...)
-- Data rows ship in the dated _07_ and _08_ catalog files.

-- CSV header: id,species_id,move_internal_name
CREATE TABLE IF NOT EXISTS `battlemon_species_tutor_moves` (
  `id` int unsigned NOT NULL,
  `species_id` int unsigned NOT NULL,
  `move_internal_name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `species` (`species_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CSV header: id,form_id,method,level,move_internal_name
-- method is 'level' or 'tutor'; a form with any row here replaces its species
-- pool for that method rather than adding to it.
CREATE TABLE IF NOT EXISTS `battlemon_form_moves` (
  `id` int unsigned NOT NULL,
  `form_id` int unsigned NOT NULL,
  `method` varchar(8) NOT NULL,
  `level` int unsigned NOT NULL DEFAULT '0',
  `move_internal_name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `form_method` (`form_id`,`method`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
