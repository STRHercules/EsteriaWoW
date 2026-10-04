-- Exact-Race startup data for Esteria races that use a legacy compatibility RaceMask.
-- The legacy playercreateinfo_* tables remain authoritative for stock races. Extended races
-- inherit compatible generic/class data through their legacy mask and use these tables to
-- exclude host-race-only rows and add exact-race rows without consuming another 32-bit mask.

CREATE TABLE IF NOT EXISTS `custom_race_start_skill` (
  `race` TINYINT UNSIGNED NOT NULL,
  `classMask` INT UNSIGNED NOT NULL DEFAULT 0,
  `skill` SMALLINT UNSIGNED NOT NULL,
  `rank` SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`race`, `classMask`, `skill`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `custom_race_start_skill_exclude` (
  `race` TINYINT UNSIGNED NOT NULL,
  `skill` SMALLINT UNSIGNED NOT NULL,
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`race`, `skill`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `custom_race_start_spell` (
  `race` TINYINT UNSIGNED NOT NULL,
  `classMask` INT UNSIGNED NOT NULL DEFAULT 0,
  `spell` INT UNSIGNED NOT NULL,
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`race`, `classMask`, `spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `custom_race_start_spell_exclude` (
  `race` TINYINT UNSIGNED NOT NULL,
  `spell` INT UNSIGNED NOT NULL,
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`race`, `spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
