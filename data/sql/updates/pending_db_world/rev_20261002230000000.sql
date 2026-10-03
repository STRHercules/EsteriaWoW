-- Retail NPC race starts; only new targets54-59 are changed.

SET @RACE := 54;
SET @DONOR := 10;

DELETE FROM `playercreateinfo` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @RACE, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @RACE;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @RACE, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @RACE, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @RACE, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@RACE, 0, 669, 'Language Orcish');

DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@RACE, 0, 109, 0, 'Language Orcish');

SET @RACE := 55;
SET @DONOR := 3;

DELETE FROM `playercreateinfo` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @RACE, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @RACE;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @RACE, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @RACE, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @RACE, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@RACE, 0, 668, 'Language Common');

DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@RACE, 0, 98, 0, 'Language Common');

SET @RACE := 56;
SET @DONOR := 1;

DELETE FROM `playercreateinfo` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @RACE, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @RACE;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @RACE, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @RACE, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @RACE, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@RACE, 0, 668, 'Language Common');

DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@RACE, 0, 98, 0, 'Language Common');

SET @RACE := 57;
SET @DONOR := 2;

DELETE FROM `playercreateinfo` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @RACE, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @RACE;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @RACE, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @RACE, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @RACE, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@RACE, 0, 669, 'Language Orcish');

DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@RACE, 0, 109, 0, 'Language Orcish');

SET @RACE := 58;
SET @DONOR := 1;

DELETE FROM `playercreateinfo` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @RACE, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @RACE;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @RACE, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @RACE, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @RACE, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@RACE, 0, 668, 'Language Common');

DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@RACE, 0, 98, 0, 'Language Common');

SET @RACE := 59;
SET @DONOR := 2;

DELETE FROM `playercreateinfo` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @RACE, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @RACE;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @RACE, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @RACE, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @RACE;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @RACE, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @RACE;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @RACE, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@RACE, 0, 669, 'Language Orcish');

DELETE FROM `custom_race_start_skill` WHERE `race` = @RACE;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@RACE, 0, 109, 0, 'Language Orcish');
