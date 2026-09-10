-- Battlemon catalog schema (acore_world).
-- Row data is seeded by 2026_08_13_01 .. 06 (generated from addon Data/csv).
-- After updates apply, restart worldserver or run .battlemon reload.

CREATE TABLE IF NOT EXISTS `battlemon_types` (
  `id` int unsigned NOT NULL,
  `internal_name` varchar(32) NOT NULL,
  `name` varchar(32) NOT NULL,
  `icon_position` int DEFAULT NULL,
  `is_pseudo` tinyint unsigned NOT NULL DEFAULT '0',
  `is_special` tinyint unsigned NOT NULL DEFAULT '0',
  `weaknesses` varchar(255) DEFAULT NULL,
  `resistances` varchar(255) DEFAULT NULL,
  `immunities` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `internal_name` (`internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_type_chart` (
  `id` int unsigned NOT NULL,
  `attacker` varchar(32) NOT NULL,
  `defender` varchar(32) NOT NULL,
  `multiplier` decimal(3,2) NOT NULL DEFAULT '1.00',
  PRIMARY KEY (`id`),
  KEY `attacker_defender` (`attacker`,`defender`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_abilities` (
  `id` int unsigned NOT NULL,
  `internal_name` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `internal_name` (`internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_moves` (
  `id` int unsigned NOT NULL,
  `internal_name` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(32) NOT NULL,
  `move_category` varchar(16) NOT NULL,
  `power` int DEFAULT NULL,
  `accuracy` int DEFAULT NULL,
  `pp` int DEFAULT NULL,
  `target` varchar(32) DEFAULT NULL,
  `function_code` varchar(64) DEFAULT NULL,
  `flags` varchar(255) DEFAULT NULL,
  `priority` int NOT NULL DEFAULT '0',
  `effect_chance` int NOT NULL DEFAULT '0',
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `internal_name` (`internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `battlemon_items` (
  `id` int unsigned NOT NULL,
  `internal_name` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `name_plural` varchar(64) DEFAULT NULL,
  `pocket` int DEFAULT NULL,
  `price` int DEFAULT NULL,
  `field_use` varchar(32) DEFAULT NULL,
  `battle_use` varchar(32) DEFAULT NULL,
  `flags` varchar(255) DEFAULT NULL,
  `heal_amount` varchar(16) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `internal_name` (`internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CSV header:
-- id,internal_name,name,type1,type2,hp,atk,def,spa,spd,spe,gender_ratio,growth_rate,
-- base_exp,catch_rate,happiness,ability1,ability2,hidden_ability,egg_groups,hatch_steps,
-- height,weight,color,shape,habitat,category,pokedex,generation,evolutions,sprite
CREATE TABLE IF NOT EXISTS `battlemon_species` (
  `id` int unsigned NOT NULL,
  `internal_name` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type1` varchar(32) NOT NULL,
  `type2` varchar(32) DEFAULT NULL,
  `hp` int NOT NULL DEFAULT '1',
  `atk` int NOT NULL DEFAULT '1',
  `def` int NOT NULL DEFAULT '1',
  `spa` int NOT NULL DEFAULT '1',
  `spd` int NOT NULL DEFAULT '1',
  `spe` int NOT NULL DEFAULT '1',
  `gender_ratio` varchar(32) DEFAULT NULL,
  `growth_rate` varchar(32) DEFAULT NULL,
  `base_exp` int unsigned NOT NULL DEFAULT '0',
  `catch_rate` int unsigned DEFAULT NULL,
  `happiness` int DEFAULT NULL,
  `ability1` varchar(64) DEFAULT NULL,
  `ability2` varchar(64) DEFAULT NULL,
  `hidden_ability` varchar(64) DEFAULT NULL,
  `egg_groups` varchar(64) DEFAULT NULL,
  `hatch_steps` int DEFAULT NULL,
  `height` decimal(6,2) DEFAULT NULL,
  `weight` decimal(8,2) DEFAULT NULL,
  `color` varchar(32) DEFAULT NULL,
  `shape` varchar(32) DEFAULT NULL,
  `habitat` varchar(32) DEFAULT NULL,
  `category` varchar(64) DEFAULT NULL,
  `pokedex` text,
  `generation` varchar(8) DEFAULT NULL,
  `evolutions` varchar(255) DEFAULT NULL,
  `sprite` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `internal_name` (`internal_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CSV header: id,species_id,level,move_internal_name
CREATE TABLE IF NOT EXISTS `battlemon_species_moves` (
  `id` int unsigned NOT NULL,
  `species_id` int unsigned NOT NULL,
  `level` int unsigned NOT NULL,
  `move_internal_name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `species_level` (`species_id`,`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CSV header: id,species_id,sprite,variant,name,back_sprite
-- One row per Front sprite (including gender/form variants).
CREATE TABLE IF NOT EXISTS `battlemon_forms` (
  `id` int unsigned NOT NULL,
  `species_id` int unsigned NOT NULL,
  `sprite` varchar(128) NOT NULL,
  `variant` varchar(64) DEFAULT NULL,
  `name` varchar(128) NOT NULL,
  `back_sprite` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sprite` (`sprite`),
  KEY `species_id` (`species_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Future trainer NPCs (not wired yet). Place creatures in the world later and
-- fill this table: beating them can award points and/or a specific form.
CREATE TABLE IF NOT EXISTS `battlemon_npc` (
  `creature_id` int unsigned NOT NULL COMMENT 'creature_template.entry',
  `name` varchar(64) DEFAULT NULL,
  `reward_form_id` int unsigned DEFAULT NULL COMMENT 'battlemon_forms.id granted on win; NULL = points only',
  `reward_points` int unsigned NOT NULL DEFAULT '0',
  `notes` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`creature_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
