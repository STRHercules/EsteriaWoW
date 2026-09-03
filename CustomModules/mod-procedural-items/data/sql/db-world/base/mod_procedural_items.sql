-- mod-procedural-items v0.1 scaffold
-- World database metadata for permanent procedural item identities.

CREATE TABLE IF NOT EXISTS `mod_procedural_id_range` (
  `pool_key` VARCHAR(64) NOT NULL,
  `start_entry` MEDIUMINT UNSIGNED NOT NULL,
  `end_entry` MEDIUMINT UNSIGNED NOT NULL,
  `item_class` TINYINT UNSIGNED NOT NULL,
  `subclass` TINYINT UNSIGNED NOT NULL,
  `inventory_type` TINYINT UNSIGNED NOT NULL,
  `enabled` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (`pool_key`),
  UNIQUE KEY `uq_mod_proc_range_start` (`start_entry`),
  UNIQUE KEY `uq_mod_proc_range_end` (`end_entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `mod_procedural_display_pool` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `pool_key` VARCHAR(64) NOT NULL,
  `display_id` MEDIUMINT UNSIGNED NOT NULL,
  `min_level` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `max_level` TINYINT UNSIGNED NOT NULL DEFAULT 80,
  `weight` INT UNSIGNED NOT NULL DEFAULT 100,
  `enabled` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_mod_proc_display` (`pool_key`, `display_id`),
  KEY `idx_mod_proc_display_pool` (`pool_key`, `enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `mod_procedural_item` (
  `item_entry` MEDIUMINT UNSIGNED NOT NULL,
  `seed` BIGINT UNSIGNED NOT NULL,
  `generation_version` INT UNSIGNED NOT NULL,
  `pool_key` VARCHAR(64) NOT NULL,
  `role` VARCHAR(24) NOT NULL,
  `quality` TINYINT UNSIGNED NOT NULL,
  `source` VARCHAR(64) NOT NULL DEFAULT 'unknown',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`item_entry`),
  KEY `idx_mod_proc_seed` (`seed`),
  KEY `idx_mod_proc_pool` (`pool_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Starter reservation map. These are identities the client patch must mirror
-- in Item.dbc. They are intentionally modest ranges for development.
INSERT IGNORE INTO `mod_procedural_id_range`
(`pool_key`, `start_entry`, `end_entry`, `item_class`, `subclass`, `inventory_type`) VALUES
('leather_chest', 2000000, 2000999, 4, 2, 5),
('leather_legs',  2001000, 2001999, 4, 2, 7),
('mail_chest',    2002000, 2002999, 4, 3, 5),
('bow',           2003000, 2003999, 2, 2, 15),
('gun',           2004000, 2004999, 2, 3, 26),
('sword_1h',      2005000, 2005999, 2, 7, 13);

-- No display IDs are seeded here on purpose. Populate mod_procedural_display_pool
-- only with ItemDisplayInfo.dbc IDs verified against the exact client build/patch.
