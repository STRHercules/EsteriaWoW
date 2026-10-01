-- Esteria RaceID 45: Mag'har Orc.
-- Uses the Orc start profile and legacy mask for compatible generic content, while exact-race
-- exclusion/addition tables prevent Orc racials from leaking onto the Mag'har character.

SET @MAGHAR := 45;
SET @ORC := 2;
SET @ANCESTRAL_CALL := 110100;

DELETE FROM `playercreateinfo` WHERE `race` = @MAGHAR;
INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`)
SELECT @MAGHAR, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`
FROM `playercreateinfo`
WHERE `race` = @ORC AND `class` IN (1,2,3,4,5,6,7,8,9,11);

DELETE FROM `player_race_stats` WHERE `Race` = @MAGHAR;
INSERT INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`)
SELECT @MAGHAR, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`
FROM `player_race_stats`
WHERE `Race` = @ORC;

DELETE FROM `playercreateinfo_item` WHERE `race` = @MAGHAR;
INSERT INTO `playercreateinfo_item` (`race`, `class`, `itemid`, `amount`, `Note`)
SELECT @MAGHAR, `class`, `itemid`, `amount`, `Note`
FROM `playercreateinfo_item`
WHERE `race` = @ORC AND `class` IN (1,2,3,4,5,6,7,8,9,11);

DELETE FROM `playercreateinfo_action` WHERE `race` = @MAGHAR;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`)
SELECT @MAGHAR, `class`, `button`,
       CASE WHEN `action` IN (20572, 33697, 33702) THEN @ANCESTRAL_CALL ELSE `action` END,
       `type`
FROM `playercreateinfo_action`
WHERE `race` = @ORC AND `class` IN (1,2,3,4,5,6,7,8,9,11);

DELETE FROM `player_totem_model` WHERE `RaceID` = @MAGHAR;
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`)
SELECT `TotemID`, @MAGHAR, `ModelID`
FROM `player_totem_model`
WHERE `RaceID` = @ORC;

DELETE FROM `custom_race_start_spell_exclude` WHERE `race` = @MAGHAR;
INSERT INTO `custom_race_start_spell_exclude` (`race`, `spell`, `comment`) VALUES
(@MAGHAR, 20572, 'Orc Blood Fury: Maghar uses Ancestral Call'),
(@MAGHAR, 33697, 'Orc Blood Fury caster variant'),
(@MAGHAR, 33702, 'Orc Blood Fury caster variant'),
(@MAGHAR, 20573, 'Orc Hardiness'),
(@MAGHAR, 20574, 'Orc Axe Specialization'),
(@MAGHAR, 20575, 'Orc Command'),
(@MAGHAR, 20576, 'Orc Command');

DELETE FROM `custom_race_start_spell` WHERE `race` = @MAGHAR;
INSERT INTO `custom_race_start_spell` (`race`, `classMask`, `spell`, `comment`) VALUES
(@MAGHAR, 0, 110100, 'Ancestral Call'),
(@MAGHAR, 0, 110101, 'Savage Blood'),
(@MAGHAR, 0, 110102, 'Sympathetic Vigor'),
(@MAGHAR, 0, 110103, 'Unwavering Will');

-- Mag'har deliberately inherits Orcish and generic Orc-compatible skill rows. No exact skill
-- exclusions are currently required; keep the table clean so future race phases can add their own.
DELETE FROM `custom_race_start_skill` WHERE `race` = @MAGHAR;
DELETE FROM `custom_race_start_skill_exclude` WHERE `race` = @MAGHAR;
