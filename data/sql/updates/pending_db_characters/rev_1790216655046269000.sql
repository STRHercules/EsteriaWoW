-- Freeze and verify character DB backup before applying; MySQL DDL commits implicitly.
-- Mapping copied from deployed acore_world.chrraces_dbc: BaseLanguage is ChrRaces field 7 (TeamID).
-- DBC TeamID 7 maps to Alliance (0); TeamID 1 maps to Horde (1).
-- Append column to preserve positions in legacy positional PlayerDump rows.
ALTER TABLE `characters`
    ADD COLUMN `teamId` TINYINT UNSIGNED NULL,
    ADD CONSTRAINT `chk_characters_team_id` CHECK (`teamId` IN (0, 1, 3));

UPDATE `characters` SET `teamId` = CASE `race`
    WHEN 1 THEN 0
    WHEN 2 THEN 1
    WHEN 3 THEN 0
    WHEN 4 THEN 0
    WHEN 5 THEN 1
    WHEN 6 THEN 1
    WHEN 7 THEN 0
    WHEN 8 THEN 1
    WHEN 9 THEN 1
    WHEN 10 THEN 1
    WHEN 11 THEN 0
    WHEN 12 THEN 0
    WHEN 13 THEN 0
    WHEN 14 THEN 1
    WHEN 15 THEN 1
    WHEN 16 THEN 1
    WHEN 17 THEN 1
    WHEN 18 THEN 0
    WHEN 19 THEN 0
    WHEN 20 THEN 1
    WHEN 21 THEN 0
    WHEN 22 THEN 1
    WHEN 23 THEN 0
    WHEN 24 THEN 0
    WHEN 25 THEN 0
    WHEN 26 THEN 1
    WHEN 27 THEN 1
    WHEN 28 THEN 1
    WHEN 29 THEN 0
    WHEN 30 THEN 1
    WHEN 31 THEN 0
    WHEN 32 THEN 0
    WHEN 33 THEN 0
    WHEN 34 THEN 0
    WHEN 35 THEN 0
    WHEN 36 THEN 0
    WHEN 37 THEN 0
    WHEN 38 THEN 0
    WHEN 39 THEN 0
    WHEN 40 THEN 0
    WHEN 41 THEN 0
    WHEN 42 THEN 0
    WHEN 43 THEN 0
    WHEN 44 THEN 1
    ELSE NULL
END;

SELECT `guid`, `race`, `teamId`
FROM `characters`
WHERE `teamId` IS NULL OR `teamId` NOT IN (0, 1);

-- This also fails if any existing race was not mapped above.
ALTER TABLE `characters`
    MODIFY COLUMN `teamId` TINYINT UNSIGNED NOT NULL;
