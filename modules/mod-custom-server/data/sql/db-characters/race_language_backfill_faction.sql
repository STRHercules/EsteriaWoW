-- Give any custom-race character that lacks one the language skill of its faction.
-- Existing characters usually have it from the earlier backfills, but characters
-- created before the creation rows in rev_1787850000011 existed do not.

INSERT INTO `character_skills` (`guid`, `skill`, `value`, `max`)
SELECT c.`guid`, 98, 300, 300
FROM `characters` c
WHERE c.`race` IN (18, 19, 21, 23, 29)
  AND NOT EXISTS (SELECT 1 FROM (SELECT `guid`, `skill` FROM `character_skills`) s
                  WHERE s.`guid` = c.`guid` AND s.`skill` = 98);

INSERT INTO `character_skills` (`guid`, `skill`, `value`, `max`)
SELECT c.`guid`, 109, 300, 300
FROM `characters` c
WHERE c.`race` IN (16, 17, 20, 22, 28, 30)
  AND NOT EXISTS (SELECT 1 FROM (SELECT `guid`, `skill` FROM `character_skills`) s
                  WHERE s.`guid` = c.`guid` AND s.`skill` = 109);
