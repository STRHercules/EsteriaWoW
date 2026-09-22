-- Starter skills, spells, action bars and auto-cast spells for every custom race.
-- Each race takes the block of the stock race that shares its starting zone, so the
-- weapon and armour skill lines `Player::CanUseItem()` checks exist before the first
-- item is equipped (Vulpera Hunters need Axes 44 / Bows 45, for example).

-- race 14 <- Orc (2)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    8192, `classMask`, `skill`, `rank`,
    CONCAT('race 14 inherits Orc: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 2) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    14, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 2;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    8192, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 2) <> 0;

INSERT IGNORE INTO `playercreateinfo_spell_custom`
    (`racemask`, `classmask`, `Spell`, `Note`)
SELECT
    8192, `classmask`, `Spell`, `Note`
FROM `playercreateinfo_spell_custom`
WHERE (`racemask` & 2) <> 0;

-- race 16 <- Orc (2)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    32768, `classMask`, `skill`, `rank`,
    CONCAT('race 16 inherits Orc: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 2) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    16, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 2;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    32768, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 2) <> 0;

-- race 20 <- Orc (2)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    524288, `classMask`, `skill`, `rank`,
    CONCAT('race 20 inherits Orc: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 2) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    20, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 2;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    524288, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 2) <> 0;

INSERT IGNORE INTO `playercreateinfo_spell_custom`
    (`racemask`, `classmask`, `Spell`, `Note`)
SELECT
    524288, `classmask`, `Spell`, `Note`
FROM `playercreateinfo_spell_custom`
WHERE (`racemask` & 2) <> 0;

-- race 22 <- Orc (2)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    2097152, `classMask`, `skill`, `rank`,
    CONCAT('race 22 inherits Orc: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 2) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    22, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 2;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    2097152, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 2) <> 0;

-- race 28 <- Orc (2)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    134217728, `classMask`, `skill`, `rank`,
    CONCAT('race 28 inherits Orc: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 2) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    28, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 2;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    134217728, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 2) <> 0;

-- race 17 <- Blood Elf (10)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    65536, `classMask`, `skill`, `rank`,
    CONCAT('race 17 inherits Blood Elf: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 512) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    17, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 10;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    65536, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 512) <> 0;

-- race 30 <- Blood Elf (10)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    536870912, `classMask`, `skill`, `rank`,
    CONCAT('race 30 inherits Blood Elf: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 512) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    30, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 10;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    536870912, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 512) <> 0;

-- race 18 <- Human (1)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    131072, `classMask`, `skill`, `rank`,
    CONCAT('race 18 inherits Human: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 1) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    18, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 1;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    131072, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 1) <> 0;

INSERT IGNORE INTO `playercreateinfo_spell_custom`
    (`racemask`, `classmask`, `Spell`, `Note`)
SELECT
    131072, `classmask`, `Spell`, `Note`
FROM `playercreateinfo_spell_custom`
WHERE (`racemask` & 1) <> 0;

-- race 19 <- Human (1)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    262144, `classMask`, `skill`, `rank`,
    CONCAT('race 19 inherits Human: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 1) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    19, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 1;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    262144, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 1) <> 0;

-- race 21 <- Draenei (11)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    1048576, `classMask`, `skill`, `rank`,
    CONCAT('race 21 inherits Draenei: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 1024) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    21, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 11;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    1048576, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 1024) <> 0;

-- race 23 <- Dwarf (3)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    4194304, `classMask`, `skill`, `rank`,
    CONCAT('race 23 inherits Dwarf: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 4) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    23, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 3;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    4194304, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 4) <> 0;

-- race 29 <- Dwarf (3)
INSERT IGNORE INTO `playercreateinfo_skills`
    (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT
    268435456, `classMask`, `skill`, `rank`,
    CONCAT('race 29 inherits Dwarf: ', COALESCE(`comment`, ''))
FROM `playercreateinfo_skills`
WHERE (`raceMask` & 4) <> 0;

INSERT IGNORE INTO `playercreateinfo_action`
    (`race`, `class`, `button`, `action`, `type`)
SELECT
    29, `class`, `button`, `action`, `type`
FROM `playercreateinfo_action`
WHERE `race` = 3;

INSERT IGNORE INTO `playercreateinfo_cast_spell`
    (`raceMask`, `classMask`, `spell`, `note`)
SELECT
    268435456, `classMask`, `spell`, `note`
FROM `playercreateinfo_cast_spell`
WHERE (`raceMask` & 4) <> 0;

