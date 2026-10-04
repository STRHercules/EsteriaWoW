-- Backfill the remaining languages for existing custom-race characters.
INSERT IGNORE INTO `character_spell` (`guid`, `spell`, `specMask`)
SELECT `guid`, s.`spell`, 1 FROM `characters` JOIN (SELECT 814 AS `spell` UNION ALL SELECT 815 AS `spell` UNION ALL SELECT 816 AS `spell` UNION ALL SELECT 817 AS `spell`) s
WHERE `race` IN (16, 17, 19, 21, 22, 23, 28, 29, 30);

INSERT IGNORE INTO `character_skills` (`guid`, `skill`, `value`, `max`)
SELECT `guid`, k.`skill`, 300, 300 FROM `characters` JOIN (SELECT 138 AS `skill` UNION ALL SELECT 139 AS `skill` UNION ALL SELECT 140 AS `skill` UNION ALL SELECT 141 AS `skill`) k
WHERE `race` IN (16, 17, 19, 21, 22, 23, 28, 29, 30);
