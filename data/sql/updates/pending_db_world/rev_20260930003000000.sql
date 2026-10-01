-- Initial curated Skyborne: High Order (52) and Windshaper (53).
-- Intentionally inherits the existing High Elf/Blood Elf class, language, and racial profiles.
-- Dedicated Skyborne racials are a separate content pass; no new spells are invented here.

DELETE FROM `playercreateinfo` WHERE `race` IN (52, 53);
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT IF(`race` = 13, 52, 53), `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo` WHERE `race` IN (10, 13);

DELETE FROM `player_race_stats` WHERE `Race` IN (52, 53);
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT IF(`Race` = 13, 52, 53), `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats` WHERE `Race` IN (10, 13);

DELETE FROM `playercreateinfo_item` WHERE `race` IN (52, 53);
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT IF(`race` = 13, 52, 53), `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item` WHERE `race` IN (10, 13);

DELETE FROM `playercreateinfo_action` WHERE `race` IN (52, 53);
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT IF(`race` = 13, 52, 53), `class`, `button`, `action`, `type`
FROM `playercreateinfo_action` WHERE `race` IN (10, 13);

DELETE FROM `player_totem_model` WHERE `RaceID` IN (52, 53);
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, IF(`RaceID` = 13, 52, 53), `ModelID`
FROM `player_totem_model` WHERE `RaceID` IN (10, 13);
