-- Backfill: give existing custom-race characters the same languages new ones learn.
INSERT IGNORE INTO `character_spell` (`guid`, `spell`, `specMask`)
SELECT c.`guid`, s.`spell`, 1
FROM `characters` c
JOIN (
    SELECT 668 AS `spell` UNION ALL SELECT 669 UNION ALL SELECT 670 UNION ALL SELECT 671 UNION ALL SELECT 672
    UNION ALL SELECT 7340 UNION ALL SELECT 7341 UNION ALL SELECT 813 UNION ALL SELECT 17737 UNION ALL SELECT 29932
) s
WHERE c.`race` IN (16, 17, 19, 21, 22, 23, 28, 29, 30);

INSERT IGNORE INTO `character_skills` (`guid`, `skill`, `value`, `max`)
SELECT c.`guid`, k.`skill`, 300, 300
FROM `characters` c
JOIN (
    SELECT 98 AS `skill` UNION ALL SELECT 109 UNION ALL SELECT 115 UNION ALL SELECT 113 UNION ALL SELECT 111
    UNION ALL SELECT 313 UNION ALL SELECT 315 UNION ALL SELECT 137 UNION ALL SELECT 673 UNION ALL SELECT 759
) k
WHERE c.`race` IN (16, 17, 19, 21, 22, 23, 28, 29, 30);
