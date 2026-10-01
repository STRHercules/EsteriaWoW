-- Highmountain Tauren RaceID 46: Tauren-compatible start and explicit language eligibility.
SET @HIGHMOUNTAIN := 46;
SET @TAUREN := 6;

DELETE FROM `playercreateinfo` WHERE `race` = @HIGHMOUNTAIN;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @HIGHMOUNTAIN, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @TAUREN;

DELETE FROM `player_race_stats` WHERE `Race` = @HIGHMOUNTAIN;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @HIGHMOUNTAIN, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @TAUREN;

DELETE FROM `playercreateinfo_item` WHERE `race` = @HIGHMOUNTAIN;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @HIGHMOUNTAIN, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @TAUREN;

DELETE FROM `playercreateinfo_action` WHERE `race` = @HIGHMOUNTAIN;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @HIGHMOUNTAIN, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @TAUREN;

DELETE FROM `player_totem_model` WHERE `RaceID` = @HIGHMOUNTAIN;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @HIGHMOUNTAIN, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @TAUREN;

DELETE FROM `custom_race_start_spell` WHERE `race` = @HIGHMOUNTAIN;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@HIGHMOUNTAIN, 0, 669, 'Language Orcish'),
(@HIGHMOUNTAIN, 0, 670, 'Language Taurahe');

DELETE FROM `custom_race_start_skill` WHERE `race` = @HIGHMOUNTAIN;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@HIGHMOUNTAIN, 0, 109, 0, 'Language Orcish'),
(@HIGHMOUNTAIN, 0, 115, 0, 'Language Taurahe');
