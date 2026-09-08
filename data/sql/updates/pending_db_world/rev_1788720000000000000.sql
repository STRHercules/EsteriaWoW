-- Repair custom race starting skills, quests, and Broken racials.
SET @GoblinMask = 256;
SET @WorgenMask = 2048;
SET @HighElfMask = 4096;
SET @BrokenMask = 8192;

UPDATE `playercreateinfo_skills` SET
    `raceMask` = `raceMask` | @GoblinMask | @BrokenMask
WHERE `skill` = 109 AND (`raceMask` & 2) != 0;

UPDATE `playercreateinfo_skills` SET
    `raceMask` = `raceMask` | @WorgenMask | @HighElfMask
WHERE `skill` = 98 AND (`raceMask` & 1) != 0;

UPDATE `playercreateinfo_skills` SET
    `raceMask` = `raceMask` | @HighElfMask
WHERE `skill` = 137 AND (`raceMask` & 512) != 0;

UPDATE `playercreateinfo_skills` SET
    `raceMask` = `raceMask` | @GoblinMask | @WorgenMask | @HighElfMask | @BrokenMask
WHERE `skill` = 160 AND `classMask` IN (1, 3) AND `raceMask` != 0;

DELETE FROM `skillraceclassinfo_dbc` WHERE `ID` = 1142;
INSERT INTO `skillraceclassinfo_dbc`
    (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`)
VALUES (1142, 137, 4608, 1535, 128, 0, 0, 0);

UPDATE `skillraceclassinfo_dbc` SET
    `RaceMask` = `RaceMask` | @GoblinMask | @WorgenMask | @HighElfMask | @BrokenMask
WHERE `SkillID` IN (43, 44, 46, 54, 136, 160, 172, 173, 228, 229, 293, 413, 414, 415, 433);

UPDATE `skillraceclassinfo_dbc` SET
    `RaceMask` = `RaceMask` | @GoblinMask | @BrokenMask
WHERE `SkillID` = 109;

UPDATE `skillraceclassinfo_dbc` SET
    `RaceMask` = `RaceMask` | @WorgenMask | @HighElfMask
WHERE `SkillID` = 98;

UPDATE `skilllineability_dbc` SET
    `RaceMask` = `RaceMask` | @GoblinMask | @BrokenMask
WHERE `SkillLine` = 109 AND (`RaceMask` & 2) != 0;

UPDATE `skilllineability_dbc` SET
    `RaceMask` = `RaceMask` | @WorgenMask | @HighElfMask
WHERE `SkillLine` = 98 AND (`RaceMask` & 1) != 0;

UPDATE `skilllineability_dbc` SET
    `RaceMask` = `RaceMask` | @HighElfMask
WHERE `SkillLine` = 137 AND (`RaceMask` & 512) != 0;

UPDATE `skilllineability_dbc` SET
    `RaceMask` = `RaceMask` | @GoblinMask | @WorgenMask | @HighElfMask | @BrokenMask
WHERE `SkillLine` IN (43, 44, 45, 46, 54, 136, 160, 172, 173, 228, 229, 293, 413, 414, 415, 433);

UPDATE `quest_template` SET
    `AllowableRaces` = `AllowableRaces` | @GoblinMask | @BrokenMask
WHERE (`AllowableRaces` & 2) != 0
  AND `AllowableRaces` NOT IN (-1, 2147483647, 2047, 4095, 8191, 16383, 32767, 65535,
      131071, 262143, 524287, 1048575, 2097151);

UPDATE `quest_template` SET
    `AllowableRaces` = `AllowableRaces` | @HighElfMask
WHERE (`AllowableRaces` & 1) != 0
  AND `AllowableRaces` NOT IN (-1, 2147483647, 2047, 4095, 8191, 16383, 32767, 65535,
      131071, 262143, 524287, 1048575, 2097151);

UPDATE `quest_template` SET
    `AllowableRaces` = `AllowableRaces` | @WorgenMask
WHERE `ID` IN (26, 29, 272, 1703, 3116, 3117, 3118, 3119, 3120, 5061,
    5621, 5622, 5627, 5628, 5629, 5630, 5631, 5632, 5633, 5672, 5673,
    5674, 5675, 5842, 5921, 5923, 5924, 5925, 5929, 5931, 6001, 6063,
    6071, 6072, 6073, 6101, 6102, 6103, 6121, 6122, 6123, 6124, 6125,
    6341, 6342, 6343, 6344, 6721, 6722, 9591, 9592, 9593, 9675);

DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = 14
    AND `Spell` IN (669, 110001, 110002, 110003, 110004);

DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = @BrokenMask AND `Spell` IN (20549, 20550, 20551, 20552, 110001, 110002, 110003, 110004);
INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES
(@BrokenMask, 0, 669, 'Broken - Language Orcish'),
(@BrokenMask, 0, 110001, 'Broken - Salvager'),
(@BrokenMask, 0, 110002, 'Broken - Krokul Cunning'),
(@BrokenMask, 0, 110003, 'Broken - Fel-Scarred'),
(@BrokenMask, 0, 110004, 'Broken - Echo of the Naaru');

UPDATE `playercreateinfo_action` SET `action` = 110004
WHERE `race` = 14 AND `action` IN (110001, 20549, 59752) AND `type` = 0;

DELETE FROM `skilllineability_dbc` WHERE `ID` IN (31459, 31460, 31461, 31462);
INSERT INTO `skilllineability_dbc`
    (`ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`,
     `MinSkillLineRank`, `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`,
     `TrivialSkillLineRankLow`, `CharacterPoints_1`, `CharacterPoints_2`) VALUES
(31459, 792, 110001, @BrokenMask, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31460, 792, 110002, @BrokenMask, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31461, 792, 110003, @BrokenMask, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31462, 792, 110004, @BrokenMask, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0);

DELETE FROM `spell_script_names` WHERE `spell_id` = 110004;
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`)
VALUES (110004, 'spell_broken_echo_of_the_naaru');

UPDATE `spell_dbc` SET
    `Attributes` = 80, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 0, `RecoveryTime` = 0, `DurationIndex` = 0,
    `Effect_1` = 6, `Effect_2` = 6, `Effect_3` = 0,
    `EffectBasePoints_1` = 9, `EffectBasePoints_2` = 9, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 30, `EffectAura_2` = 30, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 0, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 202, `EffectMiscValue_2` = 186, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Salvager', `NameSubtext_Lang_enUS` = 'Racial Passive',
    `Description_Lang_enUS` = 'Engineering and Mining skill increased by 10, and repair costs reduced by 10%.',
    `AuraDescription_Lang_enUS` = 'Engineering and Mining skill increased by 10.',
    `SchoolMask` = 1
WHERE `ID` = 110001;

UPDATE `spell_dbc` SET
    `Attributes` = 80, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 0, `RecoveryTime` = 0, `DurationIndex` = 0,
    `Effect_1` = 6, `Effect_2` = 0, `Effect_3` = 0,
    `EffectBasePoints_1` = -5, `EffectBasePoints_2` = 0, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 154, `EffectAura_2` = 0, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 0, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 0, `EffectMiscValue_2` = 0, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Krokul Cunning', `NameSubtext_Lang_enUS` = 'Racial Passive',
    `Description_Lang_enUS` = 'Reduces the radius at which enemies detect you by 5 yards.',
    `AuraDescription_Lang_enUS` = 'Enemy detection radius reduced by 5 yards.',
    `SchoolMask` = 1
WHERE `ID` = 110002;

UPDATE `spell_dbc` SET
    `Attributes` = 80, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 0, `RecoveryTime` = 0, `DurationIndex` = 0,
    `Effect_1` = 6, `Effect_2` = 0, `Effect_3` = 0,
    `EffectBasePoints_1` = 9, `EffectBasePoints_2` = 0, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 22, `EffectAura_2` = 0, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 0, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 32, `EffectMiscValue_2` = 0, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Fel-Scarred', `NameSubtext_Lang_enUS` = 'Racial Passive',
    `Description_Lang_enUS` = 'Mana-draining magic is 10% less effective, and Shadow resistance is increased by 10.',
    `AuraDescription_Lang_enUS` = 'Shadow resistance increased by 10.',
    `SchoolMask` = 1
WHERE `ID` = 110003;

UPDATE `spell_dbc` SET
    `Attributes` = 16, `AttributesEx` = 0, `AttributesEx2` = 0, `AttributesEx3` = 0,
    `CastingTimeIndex` = 1, `RecoveryTime` = 180000, `DurationIndex` = 28,
    `Effect_1` = 6, `Effect_2` = 0, `Effect_3` = 0,
    `EffectBasePoints_1` = 0, `EffectBasePoints_2` = 0, `EffectBasePoints_3` = 0,
    `EffectAura_1` = 8, `EffectAura_2` = 0, `EffectAura_3` = 0,
    `EffectAuraPeriod_1` = 2000, `EffectAuraPeriod_2` = 0, `EffectAuraPeriod_3` = 0,
    `EffectMiscValue_1` = 0, `EffectMiscValue_2` = 0, `EffectMiscValue_3` = 0,
    `EffectMiscValueB_1` = 0, `EffectMiscValueB_2` = 0, `EffectMiscValueB_3` = 0,
    `Name_Lang_enUS` = 'Echo of the Naaru', `NameSubtext_Lang_enUS` = 'Racial',
    `Description_Lang_enUS` = 'Restore 15% maximum health over 10 seconds.',
    `AuraDescription_Lang_enUS` = 'Restoring health over 10 seconds.',
    `SchoolMask` = 1
WHERE `ID` = 110004;
