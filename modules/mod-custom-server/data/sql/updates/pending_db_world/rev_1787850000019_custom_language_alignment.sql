-- Keep the server's full language set coherent for the custom races.
-- The custom spell backfill already grants these language spells, but only Common,
-- Orcish, and part of Thalassian had matching custom-race skill rows/masks. When the
-- client selects another known language, ChatHandler checks the missing skill and
-- rejects the message.

SET @LanguageRaceMask = CAST(0x787FA000 AS UNSIGNED);

-- Existing language skill rows must accept every supported custom race.
UPDATE `skillraceclassinfo_dbc`
SET `RaceMask` = `RaceMask` | @LanguageRaceMask
WHERE `SkillID` IN (98, 109, 111, 113, 115, 137, 138, 139, 140, 141, 313, 315, 673, 759)
  AND `RaceMask` <> 0;

DELETE FROM `skillraceclassinfo_dbc`
WHERE `ID` IN (1220, 1221, 1222, 1223, 1224, 1225, 1226);
INSERT INTO `skillraceclassinfo_dbc`
    (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`)
VALUES
    (1220, 111, @LanguageRaceMask, 1535, 128, 0, 0, 0),
    (1221, 113, @LanguageRaceMask, 1535, 128, 0, 0, 0),
    (1222, 115, @LanguageRaceMask, 1535, 128, 0, 0, 0),
    (1223, 313, @LanguageRaceMask, 1535, 128, 0, 0, 0),
    (1224, 315, @LanguageRaceMask, 1535, 128, 0, 0, 0),
    (1225, 673, @LanguageRaceMask, 1535, 128, 0, 0, 0),
    (1226, 759, @LanguageRaceMask, 1535, 128, 0, 0, 0);

UPDATE `skilllineability_dbc`
SET `RaceMask` = `RaceMask` | @LanguageRaceMask
WHERE `SkillLine` IN (98, 109, 111, 113, 115, 137, 138, 139, 140, 141, 313, 315, 673, 759)
  AND `RaceMask` <> 0;

DELETE FROM `skilllineability_dbc`
WHERE `ID` BETWEEN 970110 AND 970120;
INSERT INTO `skilllineability_dbc`
    (`ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`,
     `MinSkillLineRank`, `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`,
     `TrivialSkillLineRankLow`, `CharacterPoints_1`, `CharacterPoints_2`)
VALUES
    (970110, 111, 672,   @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970111, 113, 671,   @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970112, 115, 670,   @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970113, 138, 814,   @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970114, 139, 815,   @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970115, 140, 816,   @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970116, 141, 817,   @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970117, 313, 7340,  @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970118, 315, 7341,  @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970119, 673, 17737, @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0),
    (970120, 759, 29932, @LanguageRaceMask, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0);

-- Race 29 remains Common-only by design. All other custom races receive the same
-- language skills that the existing custom language-spell backfill already grants.
DELETE FROM `playercreateinfo_skills`
WHERE `raceMask` IN (8192, 32768, 65536, 131072, 262144, 524288, 1048576,
                     2097152, 4194304, 134217728, 536870912, 1073741824)
  AND `classMask` = 0
  AND `skill` IN (98, 109, 111, 113, 115, 137, 138, 139, 140, 141, 313, 315, 673, 759);

INSERT INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT `r`.`raceMask`, 0, `s`.`skill`, 0, CONCAT('Custom race language ', `s`.`skill`)
FROM (
    SELECT 8192 AS `raceMask`
    UNION ALL SELECT 32768
    UNION ALL SELECT 65536
    UNION ALL SELECT 131072
    UNION ALL SELECT 262144
    UNION ALL SELECT 524288
    UNION ALL SELECT 1048576
    UNION ALL SELECT 2097152
    UNION ALL SELECT 4194304
    UNION ALL SELECT 134217728
    UNION ALL SELECT 536870912
    UNION ALL SELECT 1073741824
) AS `r`
CROSS JOIN (
    SELECT 98 AS `skill`
    UNION ALL SELECT 109
    UNION ALL SELECT 111
    UNION ALL SELECT 113
    UNION ALL SELECT 115
    UNION ALL SELECT 137
    UNION ALL SELECT 138
    UNION ALL SELECT 139
    UNION ALL SELECT 140
    UNION ALL SELECT 141
    UNION ALL SELECT 313
    UNION ALL SELECT 315
    UNION ALL SELECT 673
    UNION ALL SELECT 759
) AS `s`;

-- Backfill existing characters without replacing saved values.
DELETE FROM `acore_characters`.`character_skills` WHERE 1 = 0;
INSERT IGNORE INTO `acore_characters`.`character_skills` (`guid`, `skill`, `value`, `max`)
SELECT DISTINCT `c`.`guid`, `pcs`.`skill`, 300, 300
FROM `acore_characters`.`characters` AS `c`
JOIN `acore_world`.`playercreateinfo_skills` AS `pcs`
  ON (`pcs`.`raceMask` & (1 << (`c`.`race` - 1))) != 0
 AND `pcs`.`classMask` = 0
WHERE `c`.`race` IN (14, 16, 17, 18, 19, 20, 21, 22, 23, 28, 30, 31)
  AND `pcs`.`skill` IN (98, 109, 111, 113, 115, 137, 138, 139, 140, 141, 313, 315, 673, 759);

DELETE FROM `acore_characters`.`character_spell` WHERE 1 = 0;
INSERT IGNORE INTO `acore_characters`.`character_spell` (`guid`, `spell`, `specMask`)
SELECT DISTINCT `c`.`guid`, `pcs`.`Spell`, 255
FROM `acore_characters`.`characters` AS `c`
JOIN `acore_world`.`playercreateinfo_spell_custom` AS `pcs`
  ON (`pcs`.`racemask` & (1 << (`c`.`race` - 1))) != 0
 AND (`pcs`.`classmask` = 0 OR (`pcs`.`classmask` & (1 << (`c`.`class` - 1))) != 0)
WHERE `c`.`race` IN (14, 16, 17, 18, 19, 20, 21, 22, 23, 28, 30, 31)
  AND `pcs`.`Spell` IN (668, 669, 670, 671, 672, 7340, 7341, 813, 814, 815, 816, 817, 17737, 29932);
