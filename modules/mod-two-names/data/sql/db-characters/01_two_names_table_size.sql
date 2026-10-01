-- SQL Migration: Expand Character Name Columns to Support Extended Names (e.g. up to 24-30 characters)
ALTER TABLE `characters` MODIFY COLUMN `name` VARCHAR(30) CHARACTER SET `utf8mb4` COLLATE `utf8mb4_bin` NOT NULL;
ALTER TABLE `characters` MODIFY COLUMN `deleteInfos_Name` VARCHAR(30) NULL DEFAULT NULL;
ALTER TABLE `gm_ticket` MODIFY COLUMN `name` VARCHAR(30) NOT NULL;
ALTER TABLE `profanity_name` MODIFY COLUMN `name` VARCHAR(30) NOT NULL;
ALTER TABLE `reserved_name` MODIFY COLUMN `name` VARCHAR(30) NOT NULL;
