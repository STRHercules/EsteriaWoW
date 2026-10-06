-- Cosmetic wings pilot: grant the dedicated Cosmetics skill line to existing characters.
DELETE FROM `character_skills` WHERE `skill` = 779;
INSERT INTO `character_skills` (`guid`, `skill`, `value`, `max`)
SELECT `guid`, 779, 1, 400 FROM `characters`;
