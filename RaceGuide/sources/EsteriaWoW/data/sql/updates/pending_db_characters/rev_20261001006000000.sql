-- Race46's sixth appearance byte has dedicated persistent storage.
ALTER TABLE `characters` ADD COLUMN `extraAppearance` TINYINT UNSIGNED NOT NULL DEFAULT 0;
