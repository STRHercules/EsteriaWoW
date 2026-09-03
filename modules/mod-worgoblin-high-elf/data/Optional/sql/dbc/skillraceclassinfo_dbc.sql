REPLACE INTO `skillraceclassinfo_dbc` (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`) VALUES
(21, 293, 16383, 3, 128, 40, 0, 0), -- redo this
(27, 356, 16383, 1535, 128, 0, 23, 0),
(28, 182, 16383, 1535, 160, 0, 2, 0),
(29, 186, 16383, 1535, 160, 0, 2, 0),
(30, 393, 16383, 1535, 160, 0, 161, 0),
(40, 98, 7245, 1535, 128, 0, 0, 0),
(41, 98, 930|8192, 1503, 160, 0, 21, 0),
(48, 109, 946|8192, 1535, 128, 0, 0, 0),
(49, 109, 7245, 1503, 160, 0, 21, 0),
(84, 139, 16383, 1535, 160, 0, 21, 0),
(85, 138, 16383, 1535, 128, 0, 0, 0),
(88, 141, 16383, 1535, 160, 0, 21, 0),
(93, 140, 16383, 1535, 128, 0, 0, 0),
(133, 46, 16383, 4, 128, 0, 0, 0),
(145, 413, 16383, 68, 128, 40, 0, 0),
(146, 413, 16383, 35, 128, 0, 0, 0),
(147, 414, 16383, 1135, 128, 0, 0, 0),
(148, 415, 16383, 1535, 128, 0, 0, 0),
(241, 171, 16383, 1535, 160, 0, 41, 0),
(243, 164, 16383, 1535, 160, 0, 41, 0),
(244, 202, 16383, 1535, 160, 0, 41, 0),
(246, 433, 16383, 67, 128, 0, 0, 0),
(281, 333, 16383, 1535, 160, 0, 62, 0),
(282, 185, 16383, 1535, 128, 0, 61, 0),
(284, 197, 16383, 1535, 160, 0, 62, 0),
(624, 160, 288, 1, 128, 0, 0, 0),
(625, 160, 261855, 1, 128, 0, 0, 0),
(865, 142, 16383, 1535, 0, 0, 0, 0),
(866, 755, 16383, 1535, 160, 0, 41, 0),
(899, 165, 16383, 1535, 160, 0, 41, 0),
(971, 789, 2048, 1469, 1170, 0, 0, 0), -- Worgen racials
(972, 790, 256, 509, 1170, 0, 0, 0), -- Goblin racials
(1140, 791, 4096, 1535, 1170, 0, 0, 0), -- High Elf racials
(1141, 792, 8192, 1535, 1170, 0, 0, 0); -- Mag'har Orc racials

-- Fix skill race/class validation errors for Goblin and Worgen characters
-- This resolves worldserver.exe console errors about invalid skills for race/class combinations

-- Add missing weapon skill entries for skillraceclassinfo_dbc table
-- Based on the existing playercreateinfo_skills.sql patterns:
-- RaceMask 16383 = all 14 races, ClassMask values match existing patterns

REPLACE INTO `skillraceclassinfo_dbc` (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`) VALUES
-- Skill 43 (SKILL_SWORDS) - matches pattern from playercreateinfo_skills (0,39,43,0)
(1000, 43, 16383, 39, 128, 0, 0, 0), -- Allow swords for all races, class mask 39 (Warrior, Paladin, Hunter, Death Knight)

-- Skill 44 (SKILL_AXES) - matches pattern from playercreateinfo_skills (0,37,44,0)
(1001, 44, 16383, 37, 128, 0, 0, 0), -- Allow axes for all races, class mask 37 (Warrior, Hunter, Death Knight)

-- Skill 54 (SKILL_MACES) - matches pattern from playercreateinfo_skills (0,1107,54,0)
(1002, 54, 16383, 1107, 128, 0, 0, 0), -- Allow maces for all races, class mask 1107 (Warrior, Paladin, Rogue, Shaman, Druid)

-- Skill 172 (SKILL_2H_AXES) - matches pattern from playercreateinfo_skills (0,37,172,0)
(1003, 172, 16383, 37, 128, 0, 0, 0), -- Allow 2H axes for all races, class mask 37 (Warrior, Hunter, Death Knight)

-- Skill 173 (SKILL_DAGGERS) - matches pattern from playercreateinfo_skills (735,1293,173,0)
(1004, 173, 16383, 1293, 128, 0, 0, 0); -- Allow daggers for all races, class mask 1293 (Warrior, Hunter, Rogue, Warlock, Druid)