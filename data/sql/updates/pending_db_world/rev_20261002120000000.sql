-- Haranir 50/51 use existing Night Elf/Troll compatibility profiles and explicit languages.
SET @HARANIR := 50;
SET @DONOR := 4;

DELETE FROM `playercreateinfo` WHERE `race` = @HARANIR;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @HARANIR, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @HARANIR;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @HARANIR, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @HARANIR;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @HARANIR, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @HARANIR;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @HARANIR, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @HARANIR;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @HARANIR, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @HARANIR;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@HARANIR, 0, 668, 'Language Common'),
(@HARANIR, 0, 671, 'Language Darnassian');

DELETE FROM `custom_race_start_skill` WHERE `race` = @HARANIR;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@HARANIR, 0, 98, 0, 'Language Common'),
(@HARANIR, 0, 113, 0, 'Language Darnassian');

SET @HARANIR := 51;
SET @DONOR := 8;

DELETE FROM `playercreateinfo` WHERE `race` = @HARANIR;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @HARANIR, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @HARANIR;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @HARANIR, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @HARANIR;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @HARANIR, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @HARANIR;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @HARANIR, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @HARANIR;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @HARANIR, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @HARANIR;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@HARANIR, 0, 669, 'Language Orcish'),
(@HARANIR, 0, 7341, 'Language Troll');

DELETE FROM `custom_race_start_skill` WHERE `race` = @HARANIR;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@HARANIR, 0, 109, 0, 'Language Orcish'),
(@HARANIR, 0, 315, 0, 'Language Troll');
