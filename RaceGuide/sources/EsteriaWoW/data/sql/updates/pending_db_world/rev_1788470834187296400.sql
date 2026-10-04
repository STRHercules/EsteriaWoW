/* Make Sethrak use the Orc starting path and default skills. */
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 16384
WHERE (`AllowableRaces` & 2) != 0;

UPDATE `playercreateinfo_skills`
SET `raceMask` = `raceMask` | 16384
WHERE (`raceMask` & 2) != 0;

DELETE FROM `playercreateinfo_skills` WHERE `raceMask` = 16384 AND `classMask` = 0 AND `skill` = 793;
INSERT INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
VALUES (16384, 0, 793, 0, 'Sethrak - Racial');

/* Backfill existing Sethrak without replacing any saved skill values. */
/* DELETE intentionally omitted; existing values remain intact. */
INSERT IGNORE INTO `acore_characters`.`character_skills` (`guid`, `skill`, `value`, `max`)
SELECT DISTINCT
    `c`.`guid`,
    `pcs`.`skill`,
    CASE WHEN `pcs`.`skill` = 109 THEN 300 ELSE 1 END,
    CASE
        WHEN `pcs`.`skill` = 109 THEN 300
        WHEN `pcs`.`skill` IN (413, 414, 415) THEN 1
        ELSE 5
    END
FROM `acore_characters`.`characters` AS `c`
INNER JOIN `playercreateinfo_skills` AS `pcs`
    ON (`pcs`.`raceMask` = 0 OR (`pcs`.`raceMask` & 16384) != 0)
    AND (`pcs`.`classMask` = 0 OR (`pcs`.`classMask` & (1 << (`c`.`class` - 1))) != 0)
WHERE `c`.`race` = 15;
