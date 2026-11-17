-- Recovered CoA item data uses long descriptions and 32-bit ItemLimitCategory IDs.
-- Widen only; preserve installations that already allow longer text.
SET @needs_description := (SELECT `CHARACTER_MAXIMUM_LENGTH` < 1024 FROM `information_schema`.`COLUMNS`
    WHERE `TABLE_SCHEMA` = DATABASE() AND `TABLE_NAME` = 'item_template' AND `COLUMN_NAME` = 'description');
SET @sql := IF(@needs_description,
    'ALTER TABLE `item_template` MODIFY `description` VARCHAR(1024) NOT NULL DEFAULT ''''', 'DO 0');
PREPARE `item_reference_fields` FROM @sql;
EXECUTE `item_reference_fields`;
DEALLOCATE PREPARE `item_reference_fields`;

SET @needs_limit := (SELECT `DATA_TYPE` = 'smallint' FROM `information_schema`.`COLUMNS`
    WHERE `TABLE_SCHEMA` = DATABASE() AND `TABLE_NAME` = 'item_template' AND `COLUMN_NAME` = 'ItemLimitCategory');
SET @sql := IF(@needs_limit,
    'ALTER TABLE `item_template` MODIFY `ItemLimitCategory` INT UNSIGNED NOT NULL DEFAULT 0', 'DO 0');
PREPARE `item_reference_fields` FROM @sql;
EXECUTE `item_reference_fields`;
DEALLOCATE PREPARE `item_reference_fields`;
