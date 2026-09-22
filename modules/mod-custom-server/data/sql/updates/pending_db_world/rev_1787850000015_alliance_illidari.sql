-- Alliance Illidari (race 31): the donor ships two Illidari races (its 24 is the
-- Night Elf/Alliance one, its 27 the Blood Elf/Horde one) and only the Horde half was
-- ported. This clones race 30 onto the Alliance side so both factions show the
-- same number of races in the creator. Client half:
-- `add_alliance_illidari_client.py` (ChrRaces, CreatureDisplayInfo, CharBaseInfo,
-- CharSections/CharHairGeosets/CharacterFacialHairStyles, CharStartOutfit in Patch-Y).

-- 1. ChrRaces: clone 30, Alliance faction, Common, new display rows
CREATE TEMPORARY TABLE `tmp_chrraces` AS SELECT * FROM `chrraces_dbc` WHERE `ID` = 30;
UPDATE `tmp_chrraces` SET
    `ID` = 31, `FactionID` = 1, `Alliance` = 0, `BaseLanguage` = 7,
    `MaleDisplayId` = 60026, `FemaleDisplayId` = 60027;
DELETE FROM `chrraces_dbc` WHERE `ID` = 31;
INSERT INTO `chrraces_dbc` SELECT * FROM `tmp_chrraces`;
DROP TEMPORARY TABLE `tmp_chrraces`;

-- 2. CreatureDisplayInfo rows 60026/60027 (same models as the Horde Illidari)
CREATE TEMPORARY TABLE `tmp_display` AS SELECT * FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (60024, 60025);
UPDATE `tmp_display` SET `ID` = `ID` + 2;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (60026, 60027);
INSERT INTO `creaturedisplayinfo_dbc` SELECT * FROM `tmp_display`;
DROP TEMPORARY TABLE `tmp_display`;

-- 3. Starting outfit rows
CREATE TEMPORARY TABLE `tmp_outfit` AS SELECT * FROM `charstartoutfit_dbc` WHERE `RaceID` = 30;
UPDATE `tmp_outfit` SET `ID` = `ID` + 10000, `RaceID` = 31;
DELETE FROM `charstartoutfit_dbc` WHERE `RaceID` = 31;
INSERT INTO `charstartoutfit_dbc` SELECT * FROM `tmp_outfit`;
DROP TEMPORARY TABLE `tmp_outfit`;

-- 4. Spawn points: the Night Elf start, same faction, Teldrassil
CREATE TEMPORARY TABLE `tmp_pci` AS SELECT * FROM `playercreateinfo` WHERE `race` = 4;
UPDATE `tmp_pci` SET `race` = 31;
DELETE FROM `playercreateinfo` WHERE `race` = 31;
INSERT INTO `playercreateinfo` SELECT * FROM `tmp_pci`;
DROP TEMPORARY TABLE `tmp_pci`;

-- 5. Class kit, action bars and auto-cast spells from the Night Elf block
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT 1073741824, `classMask`, `skill`, `rank`, CONCAT('race 31 inherits Night Elf: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 8) <> 0;

INSERT IGNORE INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`)
SELECT 1073741824, `classmask`, `Spell`, `Note` FROM `playercreateinfo_spell_custom`
WHERE (`racemask` & 8) <> 0;

INSERT IGNORE INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT 31, `class`, `button`, `action`, `type` FROM `playercreateinfo_action` WHERE `race` = 4;

INSERT IGNORE INTO `playercreateinfo_cast_spell` (`raceMask`, `classMask`, `spell`, `note`)
SELECT 1073741824, `classMask`, `spell`, `note` FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 8) <> 0;

-- 6. Skills demanded by the cloned starting outfit
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 1, 55, 0, 'race 31 class 1: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 1, 415, 0, 'race 31 class 1: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 2, 160, 0, 'race 31 class 2: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 2, 415, 0, 'race 31 class 2: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 4, 172, 0, 'race 31 class 3: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 4, 226, 0, 'race 31 class 3: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 4, 415, 0, 'race 31 class 3: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 8, 173, 0, 'race 31 class 4: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 8, 176, 0, 'race 31 class 4: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 8, 415, 0, 'race 31 class 4: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 16, 136, 0, 'race 31 class 5: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 16, 415, 0, 'race 31 class 5: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 32, 293, 0, 'race 31 class 6: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 32, 415, 0, 'race 31 class 6: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 64, 54, 0, 'race 31 class 7: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 64, 414, 0, 'race 31 class 7: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 64, 433, 0, 'race 31 class 7: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 128, 136, 0, 'race 31 class 8: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 128, 415, 0, 'race 31 class 8: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 256, 136, 0, 'race 31 class 9: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 256, 415, 0, 'race 31 class 9: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 1024, 136, 0, 'race 31 class 11: starting outfit');
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES (1073741824, 1024, 415, 0, 'race 31 class 11: starting outfit');

-- 7. Quests: the race takes Night Elf quests (Teldrassil/druidic chains included)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 1073741824
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 8) <> 0;

-- 8. Skill/skill-spell masks so LearnDefaultSkill() and the client accept the race
UPDATE `skillraceclassinfo_dbc` SET `RaceMask` = `RaceMask` | 0x40000000 WHERE `RaceMask` <> 0;
UPDATE `skilllineability_dbc` SET `RaceMask` = `RaceMask` | 0x40000000 WHERE `RaceMask` <> 0;
