-- Upgrade pre-2026 character_nemesis rows; base schema already includes these columns.

SET @col_exists := (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'character_nemesis'
      AND COLUMN_NAME = 'zone_id'
);
SET @sql := IF(@col_exists = 0,
    'ALTER TABLE `character_nemesis` ADD COLUMN `zone_id` int unsigned NOT NULL DEFAULT 0 AFTER `map_id`',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'character_nemesis'
      AND COLUMN_NAME = 'last_seen_at'
);
SET @sql := IF(@col_exists = 0,
    'ALTER TABLE `character_nemesis` ADD COLUMN `last_seen_at` int unsigned NOT NULL DEFAULT 0 AFTER `last_victim_guid`',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'character_nemesis'
      AND INDEX_NAME = 'idx_character_nemesis_last_seen'
);
SET @sql := IF(@idx_exists = 0,
    'ALTER TABLE `character_nemesis` ADD KEY `idx_character_nemesis_last_seen` (`last_seen_at`)',
    'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
