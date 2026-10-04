-- Darkfallen (43 Alliance / 44 Horde): additive playable-race contract.
-- Both rows share one high-bit mask; ObjectMgr filters the faction language by race ID.

SET @DarkfallenMask = 2147483648;

-- Body model data and display rows.
DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_model`;
CREATE TEMPORARY TABLE `tmp_darkfallen_model` AS
    SELECT * FROM `creaturemodeldata_dbc` WHERE `ID` = 3638;
UPDATE `tmp_darkfallen_model`
SET `ID` = 3658, `ModelName` = 'Character\\Darkfallen\\Male\\DarkfallenMale.m2';
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3658;
INSERT INTO `creaturemodeldata_dbc` SELECT * FROM `tmp_darkfallen_model`;

DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_model`;
CREATE TEMPORARY TABLE `tmp_darkfallen_model` AS
    SELECT * FROM `creaturemodeldata_dbc` WHERE `ID` = 3639;
UPDATE `tmp_darkfallen_model`
SET `ID` = 3659, `ModelName` = 'Character\\Darkfallen\\Female\\DarkfallenFemale.m2';
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3659;
INSERT INTO `creaturemodeldata_dbc` SELECT * FROM `tmp_darkfallen_model`;
DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_model`;

DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_display`;
CREATE TEMPORARY TABLE `tmp_darkfallen_display` AS
    SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60012;
UPDATE `tmp_darkfallen_display` SET `ID` = 60028, `ModelID` = 3658;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60028;
INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_darkfallen_display`;

DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_display`;
CREATE TEMPORARY TABLE `tmp_darkfallen_display` AS
    SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60013;
UPDATE `tmp_darkfallen_display` SET `ID` = 60029, `ModelID` = 3659;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60029;
INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_darkfallen_display`;
DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_display`;

-- ChrRaces rows: High Elf identity for Alliance, Blood Elf identity for Horde.
DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_chr`;
CREATE TEMPORARY TABLE `tmp_darkfallen_chr` AS
    SELECT * FROM `chrraces_dbc` WHERE `ID` = 13;
UPDATE `tmp_darkfallen_chr` SET `ID` = 43, `FactionID` = 1, `BaseLanguage` = 7, `Alliance` = 0, `ClientPrefix` = 'Be',
    `ClientFilestring` = 'Darkfallen', `MaleDisplayId` = 60028, `FemaleDisplayId` = 60029,
    `Name_Lang_enUS` = 'Darkfallen', `Name_Lang_enGB` = 'Darkfallen';
DELETE FROM `chrraces_dbc` WHERE `ID` = 43;
INSERT INTO `chrraces_dbc` SELECT * FROM `tmp_darkfallen_chr`;

DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_chr`;
CREATE TEMPORARY TABLE `tmp_darkfallen_chr` AS
    SELECT * FROM `chrraces_dbc` WHERE `ID` = 10;
UPDATE `tmp_darkfallen_chr` SET `ID` = 44, `FactionID` = 1610, `BaseLanguage` = 1, `Alliance` = 1,
    `ClientPrefix` = 'Be',
    `ClientFilestring` = 'Darkfallen', `MaleDisplayId` = 60028, `FemaleDisplayId` = 60029,
    `Name_Lang_enUS` = 'Darkfallen', `Name_Lang_enGB` = 'Darkfallen';
DELETE FROM `chrraces_dbc` WHERE `ID` = 44;
INSERT INTO `chrraces_dbc` SELECT * FROM `tmp_darkfallen_chr`;
DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_chr`;

-- Start locations, actions, items, and base stats. Keep the contract's ten classes.
-- Both factions rise in the Scourge starting area (Tirisfal Glades) and take the
-- Undead (race 5) start position; the quest mask widening below opens that zone's
-- starter chains to the shared Darkfallen bit.
DELETE FROM `playercreateinfo` WHERE `race` IN (43, 44);
INSERT INTO `playercreateinfo`
    (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT 43, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo`
WHERE `race` = 5
  AND `class` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11);
DELETE FROM `playercreateinfo` WHERE `race` = 44;
INSERT INTO `playercreateinfo`
    (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT 44, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo`
WHERE `race` = 5
  AND `class` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11);

-- Scourge starter quests: `quest_template.AllowableRaces` is the mask the client is
-- sent, so widening the Undead (race 5, bit 16) rows opens Brill/Tirisfal to both
-- Darkfallen races. Rows with mask 0 are unrestricted already.
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | @DarkfallenMask
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 16) <> 0;

DELETE FROM `playercreateinfo_action` WHERE `race` IN (43, 44);
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT 43, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 13
  AND `class` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11)
  AND `action` NOT IN (110005, 110006);
DELETE FROM `playercreateinfo_action` WHERE `race` = 44;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT 44, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 10
  AND `class` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11)
  AND `action` NOT IN (28730, 25046, 50613, 80866, 80867, 80868);

DELETE FROM `playercreateinfo_item` WHERE `race` IN (43, 44);
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT 43, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item`
WHERE `race` = 13
  AND `class` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11);
DELETE FROM `playercreateinfo_item` WHERE `race` = 44;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT 44, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item`
WHERE `race` = 10
  AND `class` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11);

DELETE FROM `player_race_stats` WHERE `Race` IN (43, 44);
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT 43, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats`
WHERE `Race` = 13;
DELETE FROM `player_race_stats` WHERE `Race` = 44;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT 44, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats`
WHERE `Race` = 10;

-- Use the High Elf class kit for both factions, without High Elf-only racial spells.
DELETE FROM `playercreateinfo_skills` WHERE `raceMask` = @DarkfallenMask;
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT @DarkfallenMask, `classMask`, `skill`, `rank`, `comment`
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 4096) <> 0
  AND `skill` NOT IN (98, 109, 137, 789, 791, 792);
DELETE FROM `playercreateinfo_skills` WHERE `raceMask` = @DarkfallenMask AND `skill` IN (98, 109);
INSERT INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES
    (@DarkfallenMask, 0, 98, 0, 'Darkfallen Alliance - Language Common'),
    (@DarkfallenMask, 0, 109, 0, 'Darkfallen Horde - Language Orcish');

DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = @DarkfallenMask;
INSERT IGNORE INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`)
SELECT @DarkfallenMask, `classmask`, `Spell`, `Note`
FROM `playercreateinfo_spell_custom`
WHERE (`racemask` & 4096) <> 0
  AND `Spell` NOT IN (668, 669, 813, 110005, 110006);
-- Racial kit: Shadow Resistance, Cannibalize renamed to Vampiric Sustenance, Crimson
-- Thirst in place of Endurance, and Children of the Night. 110040-110044 are defined
-- in rev_1787850000021_darkfallen_racials.sql (Spell.dbc rows + the proc cooldown).
DELETE FROM `playercreateinfo_spell_custom`
WHERE `racemask`=@DarkfallenMask AND `Spell` IN (668,669,20550,20579,20577,110040,110042);
INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES
    (@DarkfallenMask, 0, 668, 'Darkfallen Alliance - Language Common'),
    (@DarkfallenMask, 0, 669, 'Darkfallen Horde - Language Orcish'),
    (@DarkfallenMask, 0, 20579, 'Darkfallen - Shadow Resistance'),
    (@DarkfallenMask, 0, 20577, 'Darkfallen - Vampiric Sustenance'),
    (@DarkfallenMask, 0, 110040, 'Darkfallen - Crimson Thirst'),
    (@DarkfallenMask, 0, 110042, 'Darkfallen - Children of the Night');

DELETE FROM `playercreateinfo_cast_spell` WHERE `raceMask` = @DarkfallenMask;
INSERT IGNORE INTO `playercreateinfo_cast_spell` (`raceMask`, `classMask`, `spell`, `note`)
SELECT @DarkfallenMask, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 4096) <> 0;
INSERT IGNORE INTO `playercreateinfo_cast_spell` (`raceMask`, `classMask`, `spell`, `note`)
SELECT @DarkfallenMask, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 512) <> 0;

-- These DBC mask columns are signed INTs: store the 0x80000000 bit pattern as a negative value.
UPDATE `skillraceclassinfo_dbc` SET
    `RaceMask` = CASE WHEN `RaceMask` >= 0 THEN `RaceMask` - 2147483648 ELSE `RaceMask` END
WHERE `SkillID` IN (98, 109)
  AND `RaceMask` <> 0;
UPDATE `skilllineability_dbc` SET
    `RaceMask` = CASE WHEN `RaceMask` >= 0 THEN `RaceMask` - 2147483648 ELSE `RaceMask` END
WHERE `SkillLine` IN (98, 109)
  AND `RaceMask` <> 0;

-- The Undead racial skill line (220) is what Vampiric Sustenance (20577) and Shadow
-- Resistance (20579) hang off in SkillLineAbility.dbc. Player::CheckSkillLearnedBySpell()
-- deletes any granted spell whose skill line rejects the character's race, and the stock
-- 220 rows carry the custom-race mask without the Darkfallen bit - so without this row the
-- two racials are stripped again on every login. The overlay row wins over the server
-- SkillRaceClassInfo.dbc, the same way the language rows above do.
REPLACE INTO `skillraceclassinfo_dbc`
    (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`)
VALUES
    (72, 220, -125853680, 1535, 1170, 0, 0, 0);

-- Unique IDs are required by CharStartOutfit.dbc; use separate ranges per faction.
DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_outfit`;
CREATE TEMPORARY TABLE `tmp_darkfallen_outfit` AS
    SELECT * FROM `charstartoutfit_dbc` WHERE `RaceID` = 13;
UPDATE `tmp_darkfallen_outfit` SET `ID` = `ID` + 3000000, `RaceID` = 43
WHERE `ClassID` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11);
DELETE FROM `charstartoutfit_dbc` WHERE `RaceID` = 43;
INSERT INTO `charstartoutfit_dbc` SELECT * FROM `tmp_darkfallen_outfit`;

DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_outfit`;
CREATE TEMPORARY TABLE `tmp_darkfallen_outfit` AS
    SELECT * FROM `charstartoutfit_dbc` WHERE `RaceID` = 10;
UPDATE `tmp_darkfallen_outfit` SET `ID` = `ID` + 4000000, `RaceID` = 44
WHERE `ClassID` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 11);
DELETE FROM `charstartoutfit_dbc` WHERE `RaceID` = 44;
INSERT INTO `charstartoutfit_dbc` SELECT * FROM `tmp_darkfallen_outfit`;
DROP TEMPORARY TABLE IF EXISTS `tmp_darkfallen_outfit`;
