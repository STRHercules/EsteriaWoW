-- ============================================================================
-- Broken race racials - standalone install (AzerothCore 3.3.5a)
--
-- Installs the four Broken racials on the Broken player race (race 14):
--   110001  Salvager           passive  +10 Engineering/Mining, -10% repair cost
--   110002  Krokul Cunning     passive  enemies detect you 5 yd closer
--   110003  Fel-Scarred        passive  +10 Shadow resist, -10% mana drain/burn
--   110004  Echo of the Naaru   active   heals 15% max health over 10s, 180s CD
--
-- Requires the mod-broken-racials module for 110004 (aura scaling + login repair)
-- and the two SpellEffects.cpp hooks for the Fel-Scarred mana-drain reduction.
-- Client Spell.dbc must carry matching 110001-110004 rows (name/icon/tooltip).
-- Idempotent: safe to re-run.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Spell definitions (server-side Spell.dbc overlay, cloned from the
--    Mag'har donor rows; sections 2-3 rewrite them to the Broken values)
-- ---------------------------------------------------------------------------
REPLACE INTO `spell_dbc` (`ID`, `Category`, `DispelType`, `Mechanic`, `Attributes`, `AttributesEx`, `AttributesEx2`, `AttributesEx3`, `AttributesEx4`, `AttributesEx5`, `AttributesEx6`, `AttributesEx7`, `ShapeshiftMask`, `unk_320_2`, `ShapeshiftExclude`, `unk_320_3`, `Targets`, `TargetCreatureType`, `RequiresSpellFocus`, `FacingCasterFlags`, `CasterAuraState`, `TargetAuraState`, `ExcludeCasterAuraState`, `ExcludeTargetAuraState`, `CasterAuraSpell`, `TargetAuraSpell`, `ExcludeCasterAuraSpell`, `ExcludeTargetAuraSpell`, `CastingTimeIndex`, `RecoveryTime`, `CategoryRecoveryTime`, `InterruptFlags`, `AuraInterruptFlags`, `ChannelInterruptFlags`, `ProcTypeMask`, `ProcChance`, `ProcCharges`, `MaxLevel`, `BaseLevel`, `SpellLevel`, `DurationIndex`, `PowerType`, `ManaCost`, `ManaCostPerLevel`, `ManaPerSecond`, `ManaPerSecondPerLevel`, `RangeIndex`, `Speed`, `ModalNextSpell`, `CumulativeAura`, `Totem_1`, `Totem_2`, `Reagent_1`, `Reagent_2`, `Reagent_3`, `Reagent_4`, `Reagent_5`, `Reagent_6`, `Reagent_7`, `Reagent_8`, `ReagentCount_1`, `ReagentCount_2`, `ReagentCount_3`, `ReagentCount_4`, `ReagentCount_5`, `ReagentCount_6`, `ReagentCount_7`, `ReagentCount_8`, `EquippedItemClass`, `EquippedItemSubclass`, `EquippedItemInvTypes`, `Effect_1`, `Effect_2`, `Effect_3`, `EffectDieSides_1`, `EffectDieSides_2`, `EffectDieSides_3`, `EffectRealPointsPerLevel_1`, `EffectRealPointsPerLevel_2`, `EffectRealPointsPerLevel_3`, `EffectBasePoints_1`, `EffectBasePoints_2`, `EffectBasePoints_3`, `EffectMechanic_1`, `EffectMechanic_2`, `EffectMechanic_3`, `ImplicitTargetA_1`, `ImplicitTargetA_2`, `ImplicitTargetA_3`, `ImplicitTargetB_1`, `ImplicitTargetB_2`, `ImplicitTargetB_3`, `EffectRadiusIndex_1`, `EffectRadiusIndex_2`, `EffectRadiusIndex_3`, `EffectAura_1`, `EffectAura_2`, `EffectAura_3`, `EffectAuraPeriod_1`, `EffectAuraPeriod_2`, `EffectAuraPeriod_3`, `EffectMultipleValue_1`, `EffectMultipleValue_2`, `EffectMultipleValue_3`, `EffectChainTargets_1`, `EffectChainTargets_2`, `EffectChainTargets_3`, `EffectItemType_1`, `EffectItemType_2`, `EffectItemType_3`, `EffectMiscValue_1`, `EffectMiscValue_2`, `EffectMiscValue_3`, `EffectMiscValueB_1`, `EffectMiscValueB_2`, `EffectMiscValueB_3`, `EffectTriggerSpell_1`, `EffectTriggerSpell_2`, `EffectTriggerSpell_3`, `EffectPointsPerCombo_1`, `EffectPointsPerCombo_2`, `EffectPointsPerCombo_3`, `EffectSpellClassMaskA_1`, `EffectSpellClassMaskA_2`, `EffectSpellClassMaskA_3`, `EffectSpellClassMaskB_1`, `EffectSpellClassMaskB_2`, `EffectSpellClassMaskB_3`, `EffectSpellClassMaskC_1`, `EffectSpellClassMaskC_2`, `EffectSpellClassMaskC_3`, `SpellVisualID_1`, `SpellVisualID_2`, `SpellIconID`, `ActiveIconID`, `SpellPriority`, `Name_Lang_enUS`, `Name_Lang_enGB`, `Name_Lang_koKR`, `Name_Lang_frFR`, `Name_Lang_deDE`, `Name_Lang_enCN`, `Name_Lang_zhCN`, `Name_Lang_enTW`, `Name_Lang_zhTW`, `Name_Lang_esES`, `Name_Lang_esMX`, `Name_Lang_ruRU`, `Name_Lang_ptPT`, `Name_Lang_ptBR`, `Name_Lang_itIT`, `Name_Lang_Unk`, `Name_Lang_Mask`, `NameSubtext_Lang_enUS`, `NameSubtext_Lang_enGB`, `NameSubtext_Lang_koKR`, `NameSubtext_Lang_frFR`, `NameSubtext_Lang_deDE`, `NameSubtext_Lang_enCN`, `NameSubtext_Lang_zhCN`, `NameSubtext_Lang_enTW`, `NameSubtext_Lang_zhTW`, `NameSubtext_Lang_esES`, `NameSubtext_Lang_esMX`, `NameSubtext_Lang_ruRU`, `NameSubtext_Lang_ptPT`, `NameSubtext_Lang_ptBR`, `NameSubtext_Lang_itIT`, `NameSubtext_Lang_Unk`, `NameSubtext_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`, `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`, `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`, `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`, `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `AuraDescription_Lang_enUS`, `AuraDescription_Lang_enGB`, `AuraDescription_Lang_koKR`, `AuraDescription_Lang_frFR`, `AuraDescription_Lang_deDE`, `AuraDescription_Lang_enCN`, `AuraDescription_Lang_zhCN`, `AuraDescription_Lang_enTW`, `AuraDescription_Lang_zhTW`, `AuraDescription_Lang_esES`, `AuraDescription_Lang_esMX`, `AuraDescription_Lang_ruRU`, `AuraDescription_Lang_ptPT`, `AuraDescription_Lang_ptBR`, `AuraDescription_Lang_itIT`, `AuraDescription_Lang_Unk`, `AuraDescription_Lang_Mask`, `ManaCostPct`, `StartRecoveryCategory`, `StartRecoveryTime`, `MaxTargetLevel`, `SpellClassSet`, `SpellClassMask_1`, `SpellClassMask_2`, `SpellClassMask_3`, `MaxTargets`, `DefenseType`, `PreventionType`, `StanceBarOrder`, `EffectChainAmplitude_1`, `EffectChainAmplitude_2`, `EffectChainAmplitude_3`, `MinFactionID`, `MinReputation`, `RequiredAuraVision`, `RequiredTotemCategoryID_1`, `RequiredTotemCategoryID_2`, `RequiredAreasID`, `SchoolMask`, `RuneCostID`, `SpellMissileID`, `PowerDisplayID`, `EffectBonusMultiplier_1`, `EffectBonusMultiplier_2`, `EffectBonusMultiplier_3`, `SpellDescriptionVariableID`, `SpellDifficultyID`) VALUES
(
	110001, -- ID
	0, -- Category
	0, -- DispelType
	0, -- Mechanic
	65552, -- Attributes
	32, -- AttributesEx
	147456, -- AttributesEx2
	0, -- AttributesEx3
	0, -- AttributesEx4
	0, -- AttributesEx5
	0, -- AttributesEx6
	0, -- AttributesEx7
	0, -- ShapeshiftMask
	0, -- unk_320_2
	0, -- ShapeshiftExclude
	0, -- unk_320_3
	0, -- Targets
	0, -- TargetCreatureType
	0, -- RequiresSpellFocus
	0, -- FacingCasterFlags
	0, -- CasterAuraState
	0, -- TargetAuraState
	0, -- ExcludeCasterAuraState
	0, -- ExcludeTargetAuraState
	0, -- CasterAuraSpell
	0, -- TargetAuraSpell
	0, -- ExcludeCasterAuraSpell
	0, -- ExcludeTargetAuraSpell
	1, -- CastingTimeIndex
	120000, -- RecoveryTime
	0, -- CategoryRecoveryTime
	0, -- InterruptFlags
	0, -- AuraInterruptFlags
	0, -- ChannelInterruptFlags
	0, -- ProcTypeMask
	101, -- ProcChance
	0, -- ProcCharges
	0, -- MaxLevel
	1, -- BaseLevel
	1, -- SpellLevel
	8, -- DurationIndex
	0, -- PowerType
	0, -- ManaCost
	0, -- ManaCostPerLevel
	0, -- ManaPerSecond
	0, -- ManaPerSecondPerLevel
	1, -- RangeIndex
	0, -- Speed
	0, -- ModalNextSpell
	0, -- CumulativeAura
	0, -- Totem_1
	0, -- Totem_2
	0, -- Reagent_1
	0, -- Reagent_2
	0, -- Reagent_3
	0, -- Reagent_4
	0, -- Reagent_5
	0, -- Reagent_6
	0, -- Reagent_7
	0, -- Reagent_8
	0, -- ReagentCount_1
	0, -- ReagentCount_2
	0, -- ReagentCount_3
	0, -- ReagentCount_4
	0, -- ReagentCount_5
	0, -- ReagentCount_6
	0, -- ReagentCount_7
	0, -- ReagentCount_8
	-1, -- EquippedItemClass
	0, -- EquippedItemSubclass
	0, -- EquippedItemInvTypes
	6, -- Effect_1
	6, -- Effect_2
	0, -- Effect_3
	1, -- EffectDieSides_1
	1, -- EffectDieSides_2
	0, -- EffectDieSides_3
	4, -- EffectRealPointsPerLevel_1
	2, -- EffectRealPointsPerLevel_2
	0, -- EffectRealPointsPerLevel_3
	5, -- EffectBasePoints_1
	4, -- EffectBasePoints_2
	0, -- EffectBasePoints_3
	0, -- EffectMechanic_1
	0, -- EffectMechanic_2
	0, -- EffectMechanic_3
	1, -- ImplicitTargetA_1
	1, -- ImplicitTargetA_2
	1, -- ImplicitTargetA_3
	0, -- ImplicitTargetB_1
	0, -- ImplicitTargetB_2
	0, -- ImplicitTargetB_3
	0, -- EffectRadiusIndex_1
	0, -- EffectRadiusIndex_2
	0, -- EffectRadiusIndex_3
	99, -- EffectAura_1
	13, -- EffectAura_2
	0, -- EffectAura_3
	0, -- EffectAuraPeriod_1
	0, -- EffectAuraPeriod_2
	0, -- EffectAuraPeriod_3
	0, -- EffectMultipleValue_1
	0, -- EffectMultipleValue_2
	0, -- EffectMultipleValue_3
	0, -- EffectChainTargets_1
	0, -- EffectChainTargets_2
	0, -- EffectChainTargets_3
	0, -- EffectItemType_1
	0, -- EffectItemType_2
	0, -- EffectItemType_3
	0, -- EffectMiscValue_1
	126, -- EffectMiscValue_2
	0, -- EffectMiscValue_3
	0, -- EffectMiscValueB_1
	0, -- EffectMiscValueB_2
	0, -- EffectMiscValueB_3
	0, -- EffectTriggerSpell_1
	0, -- EffectTriggerSpell_2
	0, -- EffectTriggerSpell_3
	0, -- EffectPointsPerCombo_1
	0, -- EffectPointsPerCombo_2
	0, -- EffectPointsPerCombo_3
	0, -- EffectSpellClassMaskA_1
	0, -- EffectSpellClassMaskA_2
	0, -- EffectSpellClassMaskA_3
	0, -- EffectSpellClassMaskB_1
	0, -- EffectSpellClassMaskB_2
	0, -- EffectSpellClassMaskB_3
	0, -- EffectSpellClassMaskC_1
	0, -- EffectSpellClassMaskC_2
	0, -- EffectSpellClassMaskC_3
	47, -- SpellVisualID_1
	0, -- SpellVisualID_2
	1465, -- SpellIconID
	0, -- ActiveIconID
	0, -- SpellPriority
	'Ancestral Call', -- Name_Lang_enUS
	'', -- Name_Lang_enGB
	'', -- Name_Lang_koKR
	'', -- Name_Lang_frFR
	'', -- Name_Lang_deDE
	'', -- Name_Lang_enCN
	'', -- Name_Lang_zhCN
	'', -- Name_Lang_enTW
	'', -- Name_Lang_zhTW
	'', -- Name_Lang_esES
	'', -- Name_Lang_esMX
	'', -- Name_Lang_ruRU
	'', -- Name_Lang_ptPT
	'', -- Name_Lang_ptBR
	'', -- Name_Lang_itIT
	'', -- Name_Lang_Unk
	16712190, -- Name_Lang_Mask
	'Racial', -- NameSubtext_Lang_enUS
	'', -- NameSubtext_Lang_enGB
	'', -- NameSubtext_Lang_koKR
	'', -- NameSubtext_Lang_frFR
	'', -- NameSubtext_Lang_deDE
	'', -- NameSubtext_Lang_enCN
	'', -- NameSubtext_Lang_zhCN
	'', -- NameSubtext_Lang_enTW
	'', -- NameSubtext_Lang_zhTW
	'', -- NameSubtext_Lang_esES
	'', -- NameSubtext_Lang_esMX
	'', -- NameSubtext_Lang_ruRU
	'', -- NameSubtext_Lang_ptPT
	'', -- NameSubtext_Lang_ptBR
	'', -- NameSubtext_Lang_itIT
	'', -- NameSubtext_Lang_Unk
	16712190, -- NameSubtext_Lang_Mask
	'Calls upon the strength of your uncorrupted ancestors,  increasing your attack power by $s1 and your spell damage by $s2. Lasts $d.', -- Description_Lang_enUS
	'', -- Description_Lang_enGB
	'', -- Description_Lang_koKR
	'', -- Description_Lang_frFR
	'', -- Description_Lang_deDE
	'', -- Description_Lang_enCN
	'', -- Description_Lang_zhCN
	'', -- Description_Lang_enTW
	'', -- Description_Lang_zhTW
	'', -- Description_Lang_esES
	'', -- Description_Lang_esMX
	'', -- Description_Lang_ruRU
	'', -- Description_Lang_ptPT
	'', -- Description_Lang_ptBR
	'', -- Description_Lang_itIT
	'', -- Description_Lang_Unk
	16712190, -- Description_Lang_Mask
	'Attack power and spell damage increased.', -- AuraDescription_Lang_enUS
	'', -- AuraDescription_Lang_enGB
	'', -- AuraDescription_Lang_koKR
	'', -- AuraDescription_Lang_frFR
	'', -- AuraDescription_Lang_deDE
	'', -- AuraDescription_Lang_enCN
	'', -- AuraDescription_Lang_zhCN
	'', -- AuraDescription_Lang_enTW
	'', -- AuraDescription_Lang_zhTW
	'', -- AuraDescription_Lang_esES
	'', -- AuraDescription_Lang_esMX
	'', -- AuraDescription_Lang_ruRU
	'', -- AuraDescription_Lang_ptPT
	'', -- AuraDescription_Lang_ptBR
	'', -- AuraDescription_Lang_itIT
	'', -- AuraDescription_Lang_Unk
	16712190, -- AuraDescription_Lang_Mask
	0, -- ManaCostPct
	0, -- StartRecoveryCategory
	0, -- StartRecoveryTime
	0, -- MaxTargetLevel
	0, -- SpellClassSet
	0, -- SpellClassMask_1
	0, -- SpellClassMask_2
	0, -- SpellClassMask_3
	0, -- MaxTargets
	0, -- DefenseType
	2, -- PreventionType
	0, -- StanceBarOrder
	1, -- EffectChainAmplitude_1
	1, -- EffectChainAmplitude_2
	1, -- EffectChainAmplitude_3
	0, -- MinFactionID
	0, -- MinReputation
	0, -- RequiredAuraVision
	0, -- RequiredTotemCategoryID_1
	0, -- RequiredTotemCategoryID_2
	0, -- RequiredAreasID
	1, -- SchoolMask
	0, -- RuneCostID
	0, -- SpellMissileID
	0, -- PowerDisplayID
	0, -- EffectBonusMultiplier_1
	0, -- EffectBonusMultiplier_2
	0, -- EffectBonusMultiplier_3
	0, -- SpellDescriptionVariableID
	0 -- SpellDifficultyID
),
(
	110002, -- ID
	0, -- Category
	0, -- DispelType
	0, -- Mechanic
	80, -- Attributes
	0, -- AttributesEx
	0, -- AttributesEx2
	0, -- AttributesEx3
	0, -- AttributesEx4
	0, -- AttributesEx5
	0, -- AttributesEx6
	0, -- AttributesEx7
	0, -- ShapeshiftMask
	0, -- unk_320_2
	0, -- ShapeshiftExclude
	0, -- unk_320_3
	0, -- Targets
	0, -- TargetCreatureType
	0, -- RequiresSpellFocus
	0, -- FacingCasterFlags
	0, -- CasterAuraState
	0, -- TargetAuraState
	0, -- ExcludeCasterAuraState
	0, -- ExcludeTargetAuraState
	0, -- CasterAuraSpell
	0, -- TargetAuraSpell
	0, -- ExcludeCasterAuraSpell
	0, -- ExcludeTargetAuraSpell
	1, -- CastingTimeIndex
	0, -- RecoveryTime
	0, -- CategoryRecoveryTime
	0, -- InterruptFlags
	0, -- AuraInterruptFlags
	0, -- ChannelInterruptFlags
	0, -- ProcTypeMask
	101, -- ProcChance
	0, -- ProcCharges
	0, -- MaxLevel
	0, -- BaseLevel
	0, -- SpellLevel
	0, -- DurationIndex
	0, -- PowerType
	0, -- ManaCost
	0, -- ManaCostPerLevel
	0, -- ManaPerSecond
	0, -- ManaPerSecondPerLevel
	1, -- RangeIndex
	0, -- Speed
	0, -- ModalNextSpell
	0, -- CumulativeAura
	0, -- Totem_1
	0, -- Totem_2
	0, -- Reagent_1
	0, -- Reagent_2
	0, -- Reagent_3
	0, -- Reagent_4
	0, -- Reagent_5
	0, -- Reagent_6
	0, -- Reagent_7
	0, -- Reagent_8
	0, -- ReagentCount_1
	0, -- ReagentCount_2
	0, -- ReagentCount_3
	0, -- ReagentCount_4
	0, -- ReagentCount_5
	0, -- ReagentCount_6
	0, -- ReagentCount_7
	0, -- ReagentCount_8
	-1, -- EquippedItemClass
	0, -- EquippedItemSubclass
	0, -- EquippedItemInvTypes
	6, -- Effect_1
	6, -- Effect_2
	6, -- Effect_3
	1, -- EffectDieSides_1
	1, -- EffectDieSides_2
	1, -- EffectDieSides_3
	0, -- EffectRealPointsPerLevel_1
	0, -- EffectRealPointsPerLevel_2
	0, -- EffectRealPointsPerLevel_3
	14, -- EffectBasePoints_1
	14, -- EffectBasePoints_2
	14, -- EffectBasePoints_3
	0, -- EffectMechanic_1
	0, -- EffectMechanic_2
	0, -- EffectMechanic_3
	1, -- ImplicitTargetA_1
	1, -- ImplicitTargetA_2
	1, -- ImplicitTargetA_3
	0, -- ImplicitTargetB_1
	0, -- ImplicitTargetB_2
	0, -- ImplicitTargetB_3
	0, -- EffectRadiusIndex_1
	0, -- EffectRadiusIndex_2
	0, -- EffectRadiusIndex_3
	178, -- EffectAura_1
	178, -- EffectAura_2
	178, -- EffectAura_3
	0, -- EffectAuraPeriod_1
	0, -- EffectAuraPeriod_2
	0, -- EffectAuraPeriod_3
	0, -- EffectMultipleValue_1
	0, -- EffectMultipleValue_2
	0, -- EffectMultipleValue_3
	0, -- EffectChainTargets_1
	0, -- EffectChainTargets_2
	0, -- EffectChainTargets_3
	0, -- EffectItemType_1
	0, -- EffectItemType_2
	0, -- EffectItemType_3
	2, -- EffectMiscValue_1
	3, -- EffectMiscValue_2
	4, -- EffectMiscValue_3
	0, -- EffectMiscValueB_1
	0, -- EffectMiscValueB_2
	0, -- EffectMiscValueB_3
	0, -- EffectTriggerSpell_1
	0, -- EffectTriggerSpell_2
	0, -- EffectTriggerSpell_3
	0, -- EffectPointsPerCombo_1
	0, -- EffectPointsPerCombo_2
	0, -- EffectPointsPerCombo_3
	0, -- EffectSpellClassMaskA_1
	0, -- EffectSpellClassMaskA_2
	0, -- EffectSpellClassMaskA_3
	0, -- EffectSpellClassMaskB_1
	0, -- EffectSpellClassMaskB_2
	0, -- EffectSpellClassMaskB_3
	0, -- EffectSpellClassMaskC_1
	0, -- EffectSpellClassMaskC_2
	0, -- EffectSpellClassMaskC_3
	0, -- SpellVisualID_1
	0, -- SpellVisualID_2
	2283, -- SpellIconID
	0, -- ActiveIconID
	0, -- SpellPriority
	'Savage Blood', -- Name_Lang_enUS
	'', -- Name_Lang_enGB
	'', -- Name_Lang_koKR
	'', -- Name_Lang_frFR
	'', -- Name_Lang_deDE
	'', -- Name_Lang_enCN
	'', -- Name_Lang_zhCN
	'', -- Name_Lang_enTW
	'', -- Name_Lang_zhTW
	'', -- Name_Lang_esES
	'', -- Name_Lang_esMX
	'', -- Name_Lang_ruRU
	'', -- Name_Lang_ptPT
	'', -- Name_Lang_ptBR
	'', -- Name_Lang_itIT
	'', -- Name_Lang_Unk
	16712190, -- Name_Lang_Mask
	'Racial Passive', -- NameSubtext_Lang_enUS
	'', -- NameSubtext_Lang_enGB
	'', -- NameSubtext_Lang_koKR
	'', -- NameSubtext_Lang_frFR
	'', -- NameSubtext_Lang_deDE
	'', -- NameSubtext_Lang_enCN
	'', -- NameSubtext_Lang_zhCN
	'', -- NameSubtext_Lang_enTW
	'', -- NameSubtext_Lang_zhTW
	'', -- NameSubtext_Lang_esES
	'', -- NameSubtext_Lang_esMX
	'', -- NameSubtext_Lang_ruRU
	'', -- NameSubtext_Lang_ptPT
	'', -- NameSubtext_Lang_ptBR
	'', -- NameSubtext_Lang_itIT
	'', -- NameSubtext_Lang_Unk
	16712190, -- NameSubtext_Lang_Mask
	'Your untainted blood grants a $s1% chance to resist Curse,  Disease and Poison effects.', -- Description_Lang_enUS
	'', -- Description_Lang_enGB
	'', -- Description_Lang_koKR
	'', -- Description_Lang_frFR
	'', -- Description_Lang_deDE
	'', -- Description_Lang_enCN
	'', -- Description_Lang_zhCN
	'', -- Description_Lang_enTW
	'', -- Description_Lang_zhTW
	'', -- Description_Lang_esES
	'', -- Description_Lang_esMX
	'', -- Description_Lang_ruRU
	'', -- Description_Lang_ptPT
	'', -- Description_Lang_ptBR
	'', -- Description_Lang_itIT
	'', -- Description_Lang_Unk
	16712190, -- Description_Lang_Mask
	'', -- AuraDescription_Lang_enUS
	'', -- AuraDescription_Lang_enGB
	'', -- AuraDescription_Lang_koKR
	'', -- AuraDescription_Lang_frFR
	'', -- AuraDescription_Lang_deDE
	'', -- AuraDescription_Lang_enCN
	'', -- AuraDescription_Lang_zhCN
	'', -- AuraDescription_Lang_enTW
	'', -- AuraDescription_Lang_zhTW
	'', -- AuraDescription_Lang_esES
	'', -- AuraDescription_Lang_esMX
	'', -- AuraDescription_Lang_ruRU
	'', -- AuraDescription_Lang_ptPT
	'', -- AuraDescription_Lang_ptBR
	'', -- AuraDescription_Lang_itIT
	'', -- AuraDescription_Lang_Unk
	16712188, -- AuraDescription_Lang_Mask
	0, -- ManaCostPct
	0, -- StartRecoveryCategory
	0, -- StartRecoveryTime
	0, -- MaxTargetLevel
	0, -- SpellClassSet
	0, -- SpellClassMask_1
	0, -- SpellClassMask_2
	0, -- SpellClassMask_3
	0, -- MaxTargets
	0, -- DefenseType
	0, -- PreventionType
	0, -- StanceBarOrder
	1, -- EffectChainAmplitude_1
	1, -- EffectChainAmplitude_2
	1, -- EffectChainAmplitude_3
	0, -- MinFactionID
	0, -- MinReputation
	0, -- RequiredAuraVision
	0, -- RequiredTotemCategoryID_1
	0, -- RequiredTotemCategoryID_2
	0, -- RequiredAreasID
	1, -- SchoolMask
	0, -- RuneCostID
	0, -- SpellMissileID
	0, -- PowerDisplayID
	1, -- EffectBonusMultiplier_1
	1, -- EffectBonusMultiplier_2
	1, -- EffectBonusMultiplier_3
	0, -- SpellDescriptionVariableID
	0 -- SpellDifficultyID
),
(
	110003, -- ID
	0, -- Category
	0, -- DispelType
	0, -- Mechanic
	208, -- Attributes
	1024, -- AttributesEx
	4194308, -- AttributesEx2
	268435456, -- AttributesEx3
	0, -- AttributesEx4
	0, -- AttributesEx5
	0, -- AttributesEx6
	0, -- AttributesEx7
	0, -- ShapeshiftMask
	0, -- unk_320_2
	0, -- ShapeshiftExclude
	0, -- unk_320_3
	0, -- Targets
	0, -- TargetCreatureType
	0, -- RequiresSpellFocus
	0, -- FacingCasterFlags
	0, -- CasterAuraState
	0, -- TargetAuraState
	0, -- ExcludeCasterAuraState
	0, -- ExcludeTargetAuraState
	0, -- CasterAuraSpell
	0, -- TargetAuraSpell
	0, -- ExcludeCasterAuraSpell
	0, -- ExcludeTargetAuraSpell
	1, -- CastingTimeIndex
	0, -- RecoveryTime
	0, -- CategoryRecoveryTime
	0, -- InterruptFlags
	0, -- AuraInterruptFlags
	0, -- ChannelInterruptFlags
	0, -- ProcTypeMask
	101, -- ProcChance
	0, -- ProcCharges
	0, -- MaxLevel
	0, -- BaseLevel
	0, -- SpellLevel
	21, -- DurationIndex
	0, -- PowerType
	0, -- ManaCost
	0, -- ManaCostPerLevel
	0, -- ManaPerSecond
	0, -- ManaPerSecondPerLevel
	6, -- RangeIndex
	0, -- Speed
	0, -- ModalNextSpell
	0, -- CumulativeAura
	0, -- Totem_1
	0, -- Totem_2
	0, -- Reagent_1
	0, -- Reagent_2
	0, -- Reagent_3
	0, -- Reagent_4
	0, -- Reagent_5
	0, -- Reagent_6
	0, -- Reagent_7
	0, -- Reagent_8
	0, -- ReagentCount_1
	0, -- ReagentCount_2
	0, -- ReagentCount_3
	0, -- ReagentCount_4
	0, -- ReagentCount_5
	0, -- ReagentCount_6
	0, -- ReagentCount_7
	0, -- ReagentCount_8
	-1, -- EquippedItemClass
	0, -- EquippedItemSubclass
	0, -- EquippedItemInvTypes
	119, -- Effect_1
	0, -- Effect_2
	0, -- Effect_3
	1, -- EffectDieSides_1
	0, -- EffectDieSides_2
	0, -- EffectDieSides_3
	0, -- EffectRealPointsPerLevel_1
	0, -- EffectRealPointsPerLevel_2
	0, -- EffectRealPointsPerLevel_3
	9, -- EffectBasePoints_1
	0, -- EffectBasePoints_2
	0, -- EffectBasePoints_3
	0, -- EffectMechanic_1
	0, -- EffectMechanic_2
	0, -- EffectMechanic_3
	1, -- ImplicitTargetA_1
	0, -- ImplicitTargetA_2
	0, -- ImplicitTargetA_3
	0, -- ImplicitTargetB_1
	0, -- ImplicitTargetB_2
	0, -- ImplicitTargetB_3
	12, -- EffectRadiusIndex_1
	12, -- EffectRadiusIndex_2
	0, -- EffectRadiusIndex_3
	133, -- EffectAura_1
	0, -- EffectAura_2
	0, -- EffectAura_3
	0, -- EffectAuraPeriod_1
	0, -- EffectAuraPeriod_2
	0, -- EffectAuraPeriod_3
	0, -- EffectMultipleValue_1
	0, -- EffectMultipleValue_2
	0, -- EffectMultipleValue_3
	0, -- EffectChainTargets_1
	0, -- EffectChainTargets_2
	0, -- EffectChainTargets_3
	0, -- EffectItemType_1
	0, -- EffectItemType_2
	0, -- EffectItemType_3
	0, -- EffectMiscValue_1
	0, -- EffectMiscValue_2
	0, -- EffectMiscValue_3
	0, -- EffectMiscValueB_1
	0, -- EffectMiscValueB_2
	0, -- EffectMiscValueB_3
	0, -- EffectTriggerSpell_1
	0, -- EffectTriggerSpell_2
	0, -- EffectTriggerSpell_3
	0, -- EffectPointsPerCombo_1
	0, -- EffectPointsPerCombo_2
	0, -- EffectPointsPerCombo_3
	0, -- EffectSpellClassMaskA_1
	0, -- EffectSpellClassMaskA_2
	0, -- EffectSpellClassMaskA_3
	0, -- EffectSpellClassMaskB_1
	0, -- EffectSpellClassMaskB_2
	0, -- EffectSpellClassMaskB_3
	0, -- EffectSpellClassMaskC_1
	0, -- EffectSpellClassMaskC_2
	0, -- EffectSpellClassMaskC_3
	0, -- SpellVisualID_1
	0, -- SpellVisualID_2
	1511, -- SpellIconID
	0, -- ActiveIconID
	0, -- SpellPriority
	'Sympathetic Vigor', -- Name_Lang_enUS
	'', -- Name_Lang_enGB
	'', -- Name_Lang_koKR
	'', -- Name_Lang_frFR
	'', -- Name_Lang_deDE
	'', -- Name_Lang_enCN
	'', -- Name_Lang_zhCN
	'', -- Name_Lang_enTW
	'', -- Name_Lang_zhTW
	'', -- Name_Lang_esES
	'', -- Name_Lang_esMX
	'', -- Name_Lang_ruRU
	'', -- Name_Lang_ptPT
	'', -- Name_Lang_ptBR
	'', -- Name_Lang_itIT
	'', -- Name_Lang_Unk
	16712190, -- Name_Lang_Mask
	'Racial Passive', -- NameSubtext_Lang_enUS
	'', -- NameSubtext_Lang_enGB
	'', -- NameSubtext_Lang_koKR
	'', -- NameSubtext_Lang_frFR
	'', -- NameSubtext_Lang_deDE
	'', -- NameSubtext_Lang_enCN
	'', -- NameSubtext_Lang_zhCN
	'', -- NameSubtext_Lang_enTW
	'', -- NameSubtext_Lang_zhTW
	'', -- NameSubtext_Lang_esES
	'', -- NameSubtext_Lang_esMX
	'', -- NameSubtext_Lang_ruRU
	'', -- NameSubtext_Lang_ptPT
	'', -- NameSubtext_Lang_ptBR
	'', -- NameSubtext_Lang_itIT
	'', -- NameSubtext_Lang_Unk
	16712190, -- NameSubtext_Lang_Mask
	'Your bond with the wilds of Draenor increases your pet’s maximum health by $s1%.', -- Description_Lang_enUS
	'', -- Description_Lang_enGB
	'', -- Description_Lang_koKR
	'', -- Description_Lang_frFR
	'', -- Description_Lang_deDE
	'', -- Description_Lang_enCN
	'', -- Description_Lang_zhCN
	'', -- Description_Lang_enTW
	'', -- Description_Lang_zhTW
	'', -- Description_Lang_esES
	'', -- Description_Lang_esMX
	'', -- Description_Lang_ruRU
	'', -- Description_Lang_ptPT
	'', -- Description_Lang_ptBR
	'', -- Description_Lang_itIT
	'', -- Description_Lang_Unk
	16712190, -- Description_Lang_Mask
	'', -- AuraDescription_Lang_enUS
	'', -- AuraDescription_Lang_enGB
	'', -- AuraDescription_Lang_koKR
	'', -- AuraDescription_Lang_frFR
	'', -- AuraDescription_Lang_deDE
	'', -- AuraDescription_Lang_enCN
	'', -- AuraDescription_Lang_zhCN
	'', -- AuraDescription_Lang_enTW
	'', -- AuraDescription_Lang_zhTW
	'', -- AuraDescription_Lang_esES
	'', -- AuraDescription_Lang_esMX
	'', -- AuraDescription_Lang_ruRU
	'', -- AuraDescription_Lang_ptPT
	'', -- AuraDescription_Lang_ptBR
	'', -- AuraDescription_Lang_itIT
	'', -- AuraDescription_Lang_Unk
	16712190, -- AuraDescription_Lang_Mask
	0, -- ManaCostPct
	0, -- StartRecoveryCategory
	0, -- StartRecoveryTime
	0, -- MaxTargetLevel
	0, -- SpellClassSet
	0, -- SpellClassMask_1
	0, -- SpellClassMask_2
	0, -- SpellClassMask_3
	0, -- MaxTargets
	0, -- DefenseType
	0, -- PreventionType
	0, -- StanceBarOrder
	1, -- EffectChainAmplitude_1
	1, -- EffectChainAmplitude_2
	1, -- EffectChainAmplitude_3
	0, -- MinFactionID
	0, -- MinReputation
	0, -- RequiredAuraVision
	0, -- RequiredTotemCategoryID_1
	0, -- RequiredTotemCategoryID_2
	0, -- RequiredAreasID
	8, -- SchoolMask
	0, -- RuneCostID
	0, -- SpellMissileID
	0, -- PowerDisplayID
	0, -- EffectBonusMultiplier_1
	0, -- EffectBonusMultiplier_2
	1, -- EffectBonusMultiplier_3
	0, -- SpellDescriptionVariableID
	0 -- SpellDifficultyID
),
(
	110004, -- ID
	0, -- Category
	0, -- DispelType
	0, -- Mechanic
	80, -- Attributes
	0, -- AttributesEx
	0, -- AttributesEx2
	0, -- AttributesEx3
	0, -- AttributesEx4
	0, -- AttributesEx5
	0, -- AttributesEx6
	0, -- AttributesEx7
	0, -- ShapeshiftMask
	0, -- unk_320_2
	0, -- ShapeshiftExclude
	0, -- unk_320_3
	0, -- Targets
	0, -- TargetCreatureType
	0, -- RequiresSpellFocus
	0, -- FacingCasterFlags
	0, -- CasterAuraState
	0, -- TargetAuraState
	0, -- ExcludeCasterAuraState
	0, -- ExcludeTargetAuraState
	0, -- CasterAuraSpell
	0, -- TargetAuraSpell
	0, -- ExcludeCasterAuraSpell
	0, -- ExcludeTargetAuraSpell
	1, -- CastingTimeIndex
	0, -- RecoveryTime
	0, -- CategoryRecoveryTime
	0, -- InterruptFlags
	0, -- AuraInterruptFlags
	0, -- ChannelInterruptFlags
	0, -- ProcTypeMask
	101, -- ProcChance
	0, -- ProcCharges
	0, -- MaxLevel
	0, -- BaseLevel
	0, -- SpellLevel
	0, -- DurationIndex
	0, -- PowerType
	0, -- ManaCost
	0, -- ManaCostPerLevel
	0, -- ManaPerSecond
	0, -- ManaPerSecondPerLevel
	1, -- RangeIndex
	0, -- Speed
	0, -- ModalNextSpell
	0, -- CumulativeAura
	0, -- Totem_1
	0, -- Totem_2
	0, -- Reagent_1
	0, -- Reagent_2
	0, -- Reagent_3
	0, -- Reagent_4
	0, -- Reagent_5
	0, -- Reagent_6
	0, -- Reagent_7
	0, -- Reagent_8
	0, -- ReagentCount_1
	0, -- ReagentCount_2
	0, -- ReagentCount_3
	0, -- ReagentCount_4
	0, -- ReagentCount_5
	0, -- ReagentCount_6
	0, -- ReagentCount_7
	0, -- ReagentCount_8
	-1, -- EquippedItemClass
	0, -- EquippedItemSubclass
	0, -- EquippedItemInvTypes
	6, -- Effect_1
	0, -- Effect_2
	0, -- Effect_3
	1, -- EffectDieSides_1
	0, -- EffectDieSides_2
	0, -- EffectDieSides_3
	0, -- EffectRealPointsPerLevel_1
	0, -- EffectRealPointsPerLevel_2
	0, -- EffectRealPointsPerLevel_3
	-16, -- EffectBasePoints_1
	0, -- EffectBasePoints_2
	0, -- EffectBasePoints_3
	0, -- EffectMechanic_1
	0, -- EffectMechanic_2
	0, -- EffectMechanic_3
	1, -- ImplicitTargetA_1
	0, -- ImplicitTargetA_2
	0, -- ImplicitTargetA_3
	0, -- ImplicitTargetB_1
	0, -- ImplicitTargetB_2
	0, -- ImplicitTargetB_3
	0, -- EffectRadiusIndex_1
	0, -- EffectRadiusIndex_2
	0, -- EffectRadiusIndex_3
	232, -- EffectAura_1
	0, -- EffectAura_2
	0, -- EffectAura_3
	0, -- EffectAuraPeriod_1
	0, -- EffectAuraPeriod_2
	0, -- EffectAuraPeriod_3
	0, -- EffectMultipleValue_1
	0, -- EffectMultipleValue_2
	0, -- EffectMultipleValue_3
	0, -- EffectChainTargets_1
	0, -- EffectChainTargets_2
	0, -- EffectChainTargets_3
	0, -- EffectItemType_1
	0, -- EffectItemType_2
	0, -- EffectItemType_3
	12, -- EffectMiscValue_1
	0, -- EffectMiscValue_2
	0, -- EffectMiscValue_3
	0, -- EffectMiscValueB_1
	0, -- EffectMiscValueB_2
	0, -- EffectMiscValueB_3
	0, -- EffectTriggerSpell_1
	0, -- EffectTriggerSpell_2
	0, -- EffectTriggerSpell_3
	0, -- EffectPointsPerCombo_1
	0, -- EffectPointsPerCombo_2
	0, -- EffectPointsPerCombo_3
	0, -- EffectSpellClassMaskA_1
	0, -- EffectSpellClassMaskA_2
	0, -- EffectSpellClassMaskA_3
	0, -- EffectSpellClassMaskB_1
	0, -- EffectSpellClassMaskB_2
	0, -- EffectSpellClassMaskB_3
	0, -- EffectSpellClassMaskC_1
	0, -- EffectSpellClassMaskC_2
	0, -- EffectSpellClassMaskC_3
	0, -- SpellVisualID_1
	0, -- SpellVisualID_2
	3722, -- SpellIconID
	0, -- ActiveIconID
	0, -- SpellPriority
	'Unwavering Will', -- Name_Lang_enUS
	'', -- Name_Lang_enGB
	'', -- Name_Lang_koKR
	'', -- Name_Lang_frFR
	'', -- Name_Lang_deDE
	'', -- Name_Lang_enCN
	'', -- Name_Lang_zhCN
	'', -- Name_Lang_enTW
	'', -- Name_Lang_zhTW
	'', -- Name_Lang_esES
	'', -- Name_Lang_esMX
	'', -- Name_Lang_ruRU
	'', -- Name_Lang_ptPT
	'', -- Name_Lang_ptBR
	'', -- Name_Lang_itIT
	'', -- Name_Lang_Unk
	16712190, -- Name_Lang_Mask
	'Racial Passive', -- NameSubtext_Lang_enUS
	'', -- NameSubtext_Lang_enGB
	'', -- NameSubtext_Lang_koKR
	'', -- NameSubtext_Lang_frFR
	'', -- NameSubtext_Lang_deDE
	'', -- NameSubtext_Lang_enCN
	'', -- NameSubtext_Lang_zhCN
	'', -- NameSubtext_Lang_enTW
	'', -- NameSubtext_Lang_zhTW
	'', -- NameSubtext_Lang_esES
	'', -- NameSubtext_Lang_esMX
	'', -- NameSubtext_Lang_ruRU
	'', -- NameSubtext_Lang_ptPT
	'', -- NameSubtext_Lang_ptBR
	'', -- NameSubtext_Lang_itIT
	'', -- NameSubtext_Lang_Unk
	16712190, -- NameSubtext_Lang_Mask
	'Your unbroken spirit reduces the duration of Stun effects by an additional $s1%.', -- Description_Lang_enUS
	'', -- Description_Lang_enGB
	'', -- Description_Lang_koKR
	'', -- Description_Lang_frFR
	'', -- Description_Lang_deDE
	'', -- Description_Lang_enCN
	'', -- Description_Lang_zhCN
	'', -- Description_Lang_enTW
	'', -- Description_Lang_zhTW
	'', -- Description_Lang_esES
	'', -- Description_Lang_esMX
	'', -- Description_Lang_ruRU
	'', -- Description_Lang_ptPT
	'', -- Description_Lang_ptBR
	'', -- Description_Lang_itIT
	'', -- Description_Lang_Unk
	16712190, -- Description_Lang_Mask
	'', -- AuraDescription_Lang_enUS
	'', -- AuraDescription_Lang_enGB
	'', -- AuraDescription_Lang_koKR
	'', -- AuraDescription_Lang_frFR
	'', -- AuraDescription_Lang_deDE
	'', -- AuraDescription_Lang_enCN
	'', -- AuraDescription_Lang_zhCN
	'', -- AuraDescription_Lang_enTW
	'', -- AuraDescription_Lang_zhTW
	'', -- AuraDescription_Lang_esES
	'', -- AuraDescription_Lang_esMX
	'', -- AuraDescription_Lang_ruRU
	'', -- AuraDescription_Lang_ptPT
	'', -- AuraDescription_Lang_ptBR
	'', -- AuraDescription_Lang_itIT
	'', -- AuraDescription_Lang_Unk
	16712188, -- AuraDescription_Lang_Mask
	0, -- ManaCostPct
	0, -- StartRecoveryCategory
	0, -- StartRecoveryTime
	0, -- MaxTargetLevel
	0, -- SpellClassSet
	0, -- SpellClassMask_1
	0, -- SpellClassMask_2
	0, -- SpellClassMask_3
	0, -- MaxTargets
	0, -- DefenseType
	0, -- PreventionType
	0, -- StanceBarOrder
	1, -- EffectChainAmplitude_1
	1, -- EffectChainAmplitude_2
	1, -- EffectChainAmplitude_3
	0, -- MinFactionID
	0, -- MinReputation
	0, -- RequiredAuraVision
	0, -- RequiredTotemCategoryID_1
	0, -- RequiredTotemCategoryID_2
	0, -- RequiredAreasID
	1, -- SchoolMask
	0, -- RuneCostID
	0, -- SpellMissileID
	0, -- PowerDisplayID
	1, -- EffectBonusMultiplier_1
	1, -- EffectBonusMultiplier_2
	1, -- EffectBonusMultiplier_3
	0, -- SpellDescriptionVariableID
	0 -- SpellDifficultyID
);

-- ---------------------------------------------------------------------------
-- 2. Broken racial runtime fields
-- ---------------------------------------------------------------------------
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

-- ---------------------------------------------------------------------------
-- 3. Cost / cooldown / target / range alignment
-- ---------------------------------------------------------------------------
-- Align Broken racial cost, cooldown, target, and range metadata with the client spell records.
UPDATE `spell_dbc` SET
    `PowerType` = 0,
    `ManaCost` = 0,
    `ManaCostPerLevel` = 0,
    `ManaPerSecond` = 0,
    `ManaPerSecondPerLevel` = 0,
    `ManaCostPct` = 0,
    `CategoryRecoveryTime` = 0,
    `StartRecoveryCategory` = 0,
    `StartRecoveryTime` = 0
WHERE `ID` IN (110001, 110002, 110003, 110004);

UPDATE `spell_dbc` SET
    `RangeIndex` = 1,
    `ImplicitTargetA_1` = 1,
    `ImplicitTargetB_1` = 0
WHERE `ID` IN (110001, 110002, 110003);

UPDATE `spell_dbc` SET
    `RangeIndex` = 1,
    `ImplicitTargetA_1` = 1,
    `ImplicitTargetB_1` = 0
WHERE `ID` = 110004;

-- ---------------------------------------------------------------------------
-- 4. Racial skill line and its race/class admission
-- ---------------------------------------------------------------------------
DELETE FROM `skillline_dbc` WHERE `ID` = 792;
INSERT INTO `skillline_dbc` (
    `ID`, `CategoryID`, `SkillCostsID`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `SpellIconID`,
    `AlternateVerb_Lang_enUS`, `AlternateVerb_Lang_enGB`, `AlternateVerb_Lang_koKR`, `AlternateVerb_Lang_frFR`,
    `AlternateVerb_Lang_deDE`, `AlternateVerb_Lang_enCN`, `AlternateVerb_Lang_zhCN`, `AlternateVerb_Lang_enTW`,
    `AlternateVerb_Lang_zhTW`, `AlternateVerb_Lang_esES`, `AlternateVerb_Lang_esMX`, `AlternateVerb_Lang_ruRU`,
    `AlternateVerb_Lang_ptPT`, `AlternateVerb_Lang_ptBR`, `AlternateVerb_Lang_itIT`, `AlternateVerb_Lang_Unk`,
    `AlternateVerb_Lang_Mask`, `CanLink`
) VALUES (
    792, 9, 0, 'Racial - Broken', 'Racial - Broken', 'Racial - Broken', 'Racial - Broken', 'Racial - Broken',
    'Racial - Broken', 'Racial - Broken', 'Racial - Broken', 'Racial - Broken', 'Racial - Broken',
    'Racial - Broken', 'Racial - Broken', 'Racial - Broken', 'Racial - Broken', 'Racial - Broken',
    'Racial - Broken', 16712190, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 133032,
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 0
);

DELETE FROM `skillraceclassinfo_dbc` WHERE `ID` = 1141;
INSERT INTO `skillraceclassinfo_dbc` (`ID`, `SkillID`, `RaceMask`, `ClassMask`, `Flags`, `MinLevel`, `SkillTierID`, `SkillCostIndex`) VALUES
(1141, 792, 8192, 1535, 1170, 0, 0, 0);

-- ---------------------------------------------------------------------------
-- 5. Grant the racial skill at character creation
-- ---------------------------------------------------------------------------
DELETE FROM `playercreateinfo_skills` WHERE `racemask` = 8192 AND `skill` = 792;
INSERT INTO `playercreateinfo_skills` (`racemask`, `classMask`, `skill`, `rank`, `comment`) VALUES
(8192, 0, 792, 0, 'Broken - Racial');

-- ---------------------------------------------------------------------------
-- 6. Make the four racial spells valid for the race
-- ---------------------------------------------------------------------------
DELETE FROM `skilllineability_dbc` WHERE `ID` IN (31459, 31460, 31461, 31462);
INSERT INTO `skilllineability_dbc` (
    `ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`, `MinSkillLineRank`,
    `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`, `TrivialSkillLineRankLow`,
    `CharacterPoints_1`, `CharacterPoints_2`
) VALUES
(31459, 792, 110001, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31460, 792, 110002, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31461, 792, 110003, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0),
(31462, 792, 110004, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0);

-- ---------------------------------------------------------------------------
-- 7. Starting spells (Orcish + the four racials)
-- ---------------------------------------------------------------------------
DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = 8192
    AND `Spell` IN (669, 20549, 20550, 20551, 20552, 110001, 110002, 110003, 110004);
INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES
(8192, 0, 669,    'Broken - Language Orcish'),
(8192, 0, 110001, 'Broken - Salvager'),
(8192, 0, 110002, 'Broken - Krokul Cunning'),
(8192, 0, 110003, 'Broken - Fel-Scarred'),
(8192, 0, 110004, 'Broken - Echo of the Naaru');

-- ---------------------------------------------------------------------------
-- 8. Put Echo of the Naaru on the action bar
--    Rewrites whichever button still holds an old racial. If your race 14 has
--    no action rows yet, add the button manually.
-- ---------------------------------------------------------------------------
UPDATE `playercreateinfo_action` SET `action` = 110004
WHERE `race` = 14 AND `action` IN (110001, 20549, 59752, 110004) AND `type` = 0;

-- ---------------------------------------------------------------------------
-- 9. Bind the Echo of the Naaru aura script (provided by mod-broken-racials)
-- ---------------------------------------------------------------------------
DELETE FROM `spell_script_names` WHERE `spell_id` = 110004;
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES
(110004, 'spell_broken_echo_of_the_naaru');
