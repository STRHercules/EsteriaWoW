-- Mechagnome RaceID 47: Gnome-compatible start and explicit language eligibility.
SET @MECHAGNOME := 47;
SET @GNOME := 7;

DELETE FROM `playercreateinfo` WHERE `race` = @MECHAGNOME;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @MECHAGNOME, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` = @GNOME;

DELETE FROM `player_race_stats` WHERE `Race` = @MECHAGNOME;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @MECHAGNOME, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` = @GNOME;

DELETE FROM `playercreateinfo_item` WHERE `race` = @MECHAGNOME;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @MECHAGNOME, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` = @GNOME;

DELETE FROM `playercreateinfo_action` WHERE `race` = @MECHAGNOME;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @MECHAGNOME, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` = @GNOME;

DELETE FROM `player_totem_model` WHERE `RaceID` = @MECHAGNOME;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @MECHAGNOME, `ModelID` FROM `player_totem_model` WHERE `RaceID` = @GNOME;

DELETE FROM `custom_race_start_spell` WHERE `race` = @MECHAGNOME;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@MECHAGNOME, 0, 668, 'Language Common'),
(@MECHAGNOME, 0, 7340, 'Language Gnomish');

DELETE FROM `custom_race_start_skill` WHERE `race` = @MECHAGNOME;
INSERT INTO `custom_race_start_skill` (`race`, `classMask`, `skill`, `rank`, `comment`) VALUES
(@MECHAGNOME, 0, 98, 0, 'Language Common'),
(@MECHAGNOME, 0, 313, 0, 'Language Gnomish');
