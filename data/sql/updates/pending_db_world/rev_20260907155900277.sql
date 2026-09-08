-- Restore custom-race languages and starter weapon skills.
SET @GoblinMask = 256;
SET @WorgenMask = 2048;
SET @HighElfMask = 4096;
SET @BrokenMask = 8192;
SET @CustomRaceMask = @GoblinMask | @WorgenMask | @HighElfMask | @BrokenMask;

UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | @WorgenMask | @HighElfMask WHERE `skill` = 98 AND `classMask` = 0 AND `comment` = 'Language: Common';

UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | @GoblinMask | @BrokenMask WHERE `skill` = 109 AND `classMask` = 0 AND `comment` = 'Language: Orcish';

UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | @HighElfMask WHERE `skill` = 137 AND `classMask` = 0 AND `comment` = 'Language: Thalassian';

UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | @CustomRaceMask WHERE `skill` = 226 AND `classMask` = 4;

UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | @CustomRaceMask WHERE `skill` = 55 AND `classMask` = 1;

UPDATE `playercreateinfo_skills` SET `classMask` = `classMask` | 16 | 256 WHERE `raceMask` = 0 AND `skill` = 136;

DELETE FROM `playercreateinfo_skills` WHERE `raceMask` = @CustomRaceMask AND `classMask` = 4 AND `skill` = 172;
INSERT INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
VALUES (@CustomRaceMask, 4, 172, 0, 'Custom race Hunter - Two-Handed Axes');

DELETE FROM `skillraceclassinfo_dbc` WHERE `ID` IN (1210, 1211, 1212, 1213, 1214, 1215);
INSERT INTO `skillraceclassinfo_dbc`
    (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`)
VALUES
    (1210, 55, @CustomRaceMask, 35, 128, 0, 0, 0),
    (1211, 136, @CustomRaceMask, 1488, 128, 0, 0, 0),
    (1212, 172, @CustomRaceMask, 4, 128, 0, 0, 0),
    (1213, 226, @CustomRaceMask, 4, 128, 0, 0, 0),
    (1214, 98, @WorgenMask | @HighElfMask, 1535, 128, 0, 0, 0),
    (1215, 109, @GoblinMask | @BrokenMask, 1535, 128, 0, 0, 0);

/* Backfill existing custom-race characters; saved values are never replaced. */
/* DELETE intentionally omitted; existing skill values remain intact. */
DELETE FROM `acore_characters`.`character_skills` WHERE 1 = 0;
INSERT IGNORE INTO `acore_characters`.`character_skills` (`guid`, `skill`, `value`, `max`)
SELECT
    `c`.`guid`,
    `pcs`.`skill`,
    CASE WHEN `pcs`.`skill` IN (98, 109, 137) THEN 300 ELSE 1 END,
    CASE WHEN `pcs`.`skill` IN (98, 109, 137) THEN 300 ELSE 5 END
FROM `acore_characters`.`characters` AS `c`
INNER JOIN `playercreateinfo_skills` AS `pcs`
    ON (`pcs`.`raceMask` = 0 OR (`pcs`.`raceMask` & (1 << (`c`.`race` - 1))) != 0)
    AND (`pcs`.`classMask` = 0 OR (`pcs`.`classMask` & (1 << (`c`.`class` - 1))) != 0)
WHERE `c`.`race` IN (9, 12, 13, 14);
