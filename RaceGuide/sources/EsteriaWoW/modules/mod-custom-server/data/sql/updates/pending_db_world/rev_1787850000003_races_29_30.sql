-- Kul Tiran (29, Alliance) and Illidari (30, Horde): playable race rows, models,
-- displays and starting data. Clone-based so every column stays consistent.

-- 1. model rows
DROP TEMPORARY TABLE IF EXISTS `tmp_race_model`;
CREATE TEMPORARY TABLE `tmp_race_model` AS SELECT * FROM `creaturemodeldata_dbc` WHERE `ID` = 3632;
UPDATE `tmp_race_model` SET `ID` = 3654, `ModelName` = 'CHARACTER\\Naga_\\male\\kultiranmale.mdx';
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3654;
INSERT INTO `creaturemodeldata_dbc` SELECT * FROM `tmp_race_model`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_model`;
CREATE TEMPORARY TABLE `tmp_race_model` AS SELECT * FROM `creaturemodeldata_dbc` WHERE `ID` = 3633;
UPDATE `tmp_race_model` SET `ID` = 3655, `ModelName` = 'CHARACTER\\Naga_\\Female\\kultiranfemale.mdx';
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3655;
INSERT INTO `creaturemodeldata_dbc` SELECT * FROM `tmp_race_model`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_model`;
CREATE TEMPORARY TABLE `tmp_race_model` AS SELECT * FROM `creaturemodeldata_dbc` WHERE `ID` = 3638;
UPDATE `tmp_race_model` SET `ID` = 3656, `ModelName` = 'Character\\BloodElf_Dh\\Male\\BloodElfMale_DH.mdx';
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3656;
INSERT INTO `creaturemodeldata_dbc` SELECT * FROM `tmp_race_model`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_model`;
CREATE TEMPORARY TABLE `tmp_race_model` AS SELECT * FROM `creaturemodeldata_dbc` WHERE `ID` = 3639;
UPDATE `tmp_race_model` SET `ID` = 3657, `ModelName` = 'Character\\BloodElf_Dh\\Female\\BloodElfFemale_DH.mdx';
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3657;
INSERT INTO `creaturemodeldata_dbc` SELECT * FROM `tmp_race_model`;
DROP TEMPORARY TABLE IF EXISTS `tmp_race_model`;

-- 2. display rows
DROP TEMPORARY TABLE IF EXISTS `tmp_race_display`;
CREATE TEMPORARY TABLE `tmp_race_display` AS SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60008;
UPDATE `tmp_race_display` SET `ID` = 60022, `ModelID` = 3654;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60022;
INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_race_display`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_display`;
CREATE TEMPORARY TABLE `tmp_race_display` AS SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60009;
UPDATE `tmp_race_display` SET `ID` = 60023, `ModelID` = 3655;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60023;
INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_race_display`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_display`;
CREATE TEMPORARY TABLE `tmp_race_display` AS SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60012;
UPDATE `tmp_race_display` SET `ID` = 60024, `ModelID` = 3656;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60024;
INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_race_display`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_display`;
CREATE TEMPORARY TABLE `tmp_race_display` AS SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60013;
UPDATE `tmp_race_display` SET `ID` = 60025, `ModelID` = 3657;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60025;
INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_race_display`;
DROP TEMPORARY TABLE IF EXISTS `tmp_race_display`;

-- 3. chrraces rows
DROP TEMPORARY TABLE IF EXISTS `tmp_race_chr`;
CREATE TEMPORARY TABLE `tmp_race_chr` AS SELECT * FROM `chrraces_dbc` WHERE `ID` = 19;
UPDATE `tmp_race_chr` SET `ID` = 29, `FactionID` = 1, `Alliance` = 0, `BaseLanguage` = 7,
    `ClientPrefix` = 'Kt', `ClientFilestring` = 'KulTiran',
    `MaleDisplayId` = 60022, `FemaleDisplayId` = 60023,
    `Name_Lang_enUS` = 'Kul Tiran', `Name_Lang_enGB` = 'Kul Tiran';
DELETE FROM `chrraces_dbc` WHERE `ID` = 29;
INSERT INTO `chrraces_dbc` SELECT * FROM `tmp_race_chr`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_chr`;
CREATE TEMPORARY TABLE `tmp_race_chr` AS SELECT * FROM `chrraces_dbc` WHERE `ID` = 16;
UPDATE `tmp_race_chr` SET `ID` = 30, `FactionID` = 2, `Alliance` = 1, `BaseLanguage` = 1,
    `ClientPrefix` = 'Il', `ClientFilestring` = 'Illidari',
    `MaleDisplayId` = 60024, `FemaleDisplayId` = 60025,
    `Name_Lang_enUS` = 'Illidari', `Name_Lang_enGB` = 'Illidari';
DELETE FROM `chrraces_dbc` WHERE `ID` = 30;
INSERT INTO `chrraces_dbc` SELECT * FROM `tmp_race_chr`;
DROP TEMPORARY TABLE IF EXISTS `tmp_race_chr`;

-- 4. start data (Kul Tiran from Dwarf, Illidari from Blood Elf)
DELETE FROM `playercreateinfo` WHERE `race` = 29;
INSERT INTO `playercreateinfo` SELECT 29, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation` FROM `playercreateinfo` WHERE `race` = 3;
DELETE FROM `playercreateinfo` WHERE `race` = 30;
INSERT INTO `playercreateinfo` SELECT 30, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation` FROM `playercreateinfo` WHERE `race` = 10;

DELETE FROM `playercreateinfo_action` WHERE `race` = 29;
INSERT INTO `playercreateinfo_action` SELECT 29, `class`, `button`, `action`, `type` FROM `playercreateinfo_action` WHERE `race` = 3;
DELETE FROM `playercreateinfo_action` WHERE `race` = 30;
INSERT INTO `playercreateinfo_action` SELECT 30, `class`, `button`, `action`, `type` FROM `playercreateinfo_action` WHERE `race` = 10;

DELETE FROM `playercreateinfo_item` WHERE `race` = 29;
INSERT INTO `playercreateinfo_item` SELECT 29, `class`, `itemid`, `amount`, `Note` FROM `playercreateinfo_item` WHERE `race` = 3;
DELETE FROM `playercreateinfo_item` WHERE `race` = 30;
INSERT INTO `playercreateinfo_item` SELECT 30, `class`, `itemid`, `amount`, `Note` FROM `playercreateinfo_item` WHERE `race` = 10;

DELETE FROM `player_race_stats` WHERE `race` = 29;
INSERT INTO `player_race_stats` SELECT 29, `strength`, `agility`, `stamina`, `intellect`, `spirit` FROM `player_race_stats` WHERE `race` = 3;
DELETE FROM `player_race_stats` WHERE `race` = 30;
INSERT INTO `player_race_stats` SELECT 30, `strength`, `agility`, `stamina`, `intellect`, `spirit` FROM `player_race_stats` WHERE `race` = 10;

-- 5. starting skills/spells (race bitmasks: 3 = 0x4, 10 = 0x200, 29 = 0x10000000, 30 = 0x20000000)
DELETE FROM `playercreateinfo_skills` WHERE `raceMask` = 0x10000000;
INSERT INTO `playercreateinfo_skills`
SELECT (0x10000000 | (`raceMask` & ~0x4)), `classMask`, `skill`, `rank`, `comment`
    FROM `playercreateinfo_skills` WHERE `raceMask` = 0x4;
DELETE FROM `playercreateinfo_skills` WHERE `raceMask` = 0x20000000;
INSERT INTO `playercreateinfo_skills`
SELECT (0x20000000 | (`raceMask` & ~0x200)), `classMask`, `skill`, `rank`, `comment`
    FROM `playercreateinfo_skills` WHERE `raceMask` = 0x200;

DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = 0x10000000;
INSERT INTO `playercreateinfo_spell_custom`
SELECT (0x10000000 | (`racemask` & ~0x4)), `classmask`, `Spell`, `Note`
    FROM `playercreateinfo_spell_custom` WHERE `racemask` = 0x4;
DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = 0x20000000;
INSERT INTO `playercreateinfo_spell_custom`
SELECT (0x20000000 | (`racemask` & ~0x200)), `classmask`, `Spell`, `Note`
    FROM `playercreateinfo_spell_custom` WHERE `racemask` = 0x200;

-- 6. start outfits (new ids to avoid primary-key clashes)
DROP TEMPORARY TABLE IF EXISTS `tmp_race_outfit`;
CREATE TEMPORARY TABLE `tmp_race_outfit` AS SELECT * FROM `charstartoutfit_dbc` WHERE `RaceID` = 3;
UPDATE `tmp_race_outfit` SET `ID` = `ID` + 1000000, `RaceID` = 29;
DELETE FROM `charstartoutfit_dbc` WHERE `RaceID` = 29;
INSERT INTO `charstartoutfit_dbc` SELECT * FROM `tmp_race_outfit`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_outfit`;
CREATE TEMPORARY TABLE `tmp_race_outfit` AS SELECT * FROM `charstartoutfit_dbc` WHERE `RaceID` = 10;
UPDATE `tmp_race_outfit` SET `ID` = `ID` + 1000000, `RaceID` = 30;
DELETE FROM `charstartoutfit_dbc` WHERE `RaceID` = 30;
INSERT INTO `charstartoutfit_dbc` SELECT * FROM `tmp_race_outfit`;
DROP TEMPORARY TABLE IF EXISTS `tmp_race_outfit`;
