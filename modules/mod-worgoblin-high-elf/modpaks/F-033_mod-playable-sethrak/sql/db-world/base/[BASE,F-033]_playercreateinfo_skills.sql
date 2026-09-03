/* Include Sethrak in every existing Orc-specific starting-skill row. */
UPDATE `playercreateinfo_skills`
SET `raceMask` = `raceMask` | @SethrakMask
WHERE (`raceMask` & @OrcMask) != 0;

/* Special cases */
INSERT IGNORE INTO `playercreateinfo_skills` (`racemask`, `classMask`, `skill`, `rank`, `comment`) VALUES
(0, @Paladin, 160, 0, '2H-Maces - Paladins'); -- 2H-Maces

/* Add appropriate faction language to Sethraks */
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask` | @SethrakMask WHERE `skill` = 109; -- Orcish language

/* Add racial skills */
DELETE FROM `playercreateinfo_skills` WHERE `raceMask` IN (16384) AND `classMask` = 0;
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@SethrakMask, 0, 793, 0, 'Sethrak - Racial');
