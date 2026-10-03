-- Earthen RaceID 48: Alliance start and explicit language eligibility.
SET @EARTHEN := 48;
SET @DONOR := 3;

DELETE FROM `playercreateinfo` WHERE `race` = @EARTHEN;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @EARTHEN, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @EARTHEN;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @EARTHEN, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @EARTHEN;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @EARTHEN, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @EARTHEN;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @EARTHEN, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @EARTHEN;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @EARTHEN, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @EARTHEN;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@EARTHEN, 0, 668, 'Language Common'),
(@EARTHEN, 0, 672, 'Language Dwarven');

DELETE FROM `custom_race_start_skill` WHERE `race` = @EARTHEN;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@EARTHEN, 0, 98, 0, 'Language Common'),
(@EARTHEN, 0, 111, 0, 'Language Dwarven');

-- Earthen RaceID 49: Horde start and explicit language eligibility.
SET @EARTHEN := 49;
SET @DONOR := 2;

DELETE FROM `playercreateinfo` WHERE `race` = @EARTHEN;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @EARTHEN, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @DONOR;

DELETE FROM `player_race_stats` WHERE `Race` = @EARTHEN;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @EARTHEN, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @DONOR;

DELETE FROM `playercreateinfo_item` WHERE `race` = @EARTHEN;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @EARTHEN, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @DONOR;

DELETE FROM `playercreateinfo_action` WHERE `race` = @EARTHEN;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @EARTHEN, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @DONOR;

DELETE FROM `player_totem_model` WHERE `RaceID` = @EARTHEN;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @EARTHEN, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @DONOR;

DELETE FROM `custom_race_start_spell` WHERE `race` = @EARTHEN;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@EARTHEN, 0, 669, 'Language Orcish');

DELETE FROM `custom_race_start_skill` WHERE `race` = @EARTHEN;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@EARTHEN, 0, 109, 0, 'Language Orcish');
