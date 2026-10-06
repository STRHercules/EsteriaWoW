-- Cosmetic wings pilot (see tools/wing_cosmetic_pack.py).
-- Spell 970200 applies an infinite dummy aura whose client visual is
-- SpellVisual 30112 -> kit 20218 -> effect 8145 (sirus\Wings1).
-- It is filed under skill line 779 'Cosmetics'.
-- Client rows ship as WXL continuations in Data\PATCH-X.MPQ and as merged full
-- DBFilesClient tables in patch-Z.MPQ + enUS\patch-enUS-Z.MPQ.
DELETE FROM `spell_dbc` WHERE `ID` IN (970200);
INSERT INTO `spell_dbc` (`ID`, `Mechanic`, `Attributes`, `AttributesEx4`, `AttributesEx6`, `AttributesEx7`, `CastingTimeIndex`, `InterruptFlags`, `AuraInterruptFlags`, `ProcChance`, `SpellLevel`, `DurationIndex`, `RangeIndex`, `EquippedItemClass`, `Effect_1`, `Effect_2`, `Effect_3`, `EffectDieSides_1`, `EffectDieSides_2`, `EffectDieSides_3`, `EffectBasePoints_1`, `EffectBasePoints_2`, `EffectBasePoints_3`, `ImplicitTargetA_1`, `ImplicitTargetA_2`, `EffectAura_1`, `EffectAura_2`, `EffectAura_3`, `EffectMiscValue_1`, `EffectTriggerSpell_1`, `SpellVisualID_1`, `SpellIconID`, `Name_Lang_enUS`, `Name_Lang_enGB`, `Name_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`, `Description_Lang_Mask`, `AuraDescription_Lang_enUS`, `AuraDescription_Lang_enGB`, `AuraDescription_Lang_Mask`, `StartRecoveryCategory`, `EffectChainAmplitude_1`, `EffectChainAmplitude_2`, `EffectChainAmplitude_3`, `SchoolMask`) VALUES
(970200, 0, 142606336, 0, 0, 0, 1, 0, 0, 101, 1, 21, 1, -1, 6, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 4, 0, 0, 0, 0, 30112, 153, 'Cosmetic Wings (Pilot)', 'Cosmetic Wings (Pilot)', 16712190, 'Esteria cosmetic-wings pilot.', 'Esteria cosmetic-wings pilot.', 16712190, 'Cosmetic wings.', 'Cosmetic wings.', 16712188, 0, 1, 1, 1, 1);

DELETE FROM `skilllineability_dbc` WHERE `ID` IN (970200);
INSERT INTO `skilllineability_dbc` (`ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`, `MinSkillLineRank`, `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`, `TrivialSkillLineRankLow`, `CharacterPoints_1`, `CharacterPoints_2`) VALUES
(970200, 779, 970200, 0, 1535, 0, 0, 1, 0, 0, 0, 0, 0, 0);

DELETE FROM `skillline_dbc` WHERE `ID` IN (779);
INSERT INTO `skillline_dbc` (`ID`, `CategoryID`, `SkillCostsID`, `DisplayName_Lang_enUS`, `DisplayName_Lang_Mask`, `Description_Lang_Mask`, `SpellIconID`, `AlternateVerb_Lang_Mask`, `CanLink`) VALUES
(779, 7, 0, 'Cosmetics', 16712190, 16712190, 153, 16712172, 0);

DELETE FROM `skillraceclassinfo_dbc` WHERE `ID` IN (1147);
INSERT INTO `skillraceclassinfo_dbc` (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`) VALUES
(1147, 779, 2021654527, 1535, 2, 0, 0, 0);

DELETE FROM `playercreateinfo_skills` WHERE `skill` = 779;
INSERT INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`)
SELECT `raceMask`, `classMask`, 779, `rank`, 'Cosmetics' FROM `playercreateinfo_skills` WHERE `skill` = 777;

