-- Preserve existing six-byte profiles; Haranir uses up to eight extension bytes.
ALTER TABLE `characters` MODIFY COLUMN `extraAppearance` BIGINT UNSIGNED NOT NULL DEFAULT 0;
