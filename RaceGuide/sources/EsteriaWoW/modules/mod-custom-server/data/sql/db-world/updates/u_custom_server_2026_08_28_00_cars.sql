-- Additive car mounts extracted from Patch-B, Patch-F, Patch-S, and Patch-L.
-- The four IDs are intentionally above the audited live ranges.

DELETE FROM `creature_template_model` WHERE `CreatureID` IN (3460604, 3460605, 3460606, 3460607);
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(3460604, 0, 94229, 1, 1, 51831),
(3460605, 0, 94230, 1, 1, 51831),
(3460606, 0, 94231, 1, 1, 51831),
(3460607, 0, 94232, 1, 1, 51831);

REPLACE INTO `creature_template` (`entry`, `name`, `IconName`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`, `rank`, `dmgschool`, `BaseAttackTime`, `RangeAttackTime`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `type_flags`, `lootid`, `skinloot`, `VehicleId`, `AIName`, `MovementType`, `HoverHeight`, `ExperienceModifier`, `RacialLeader`, `movementId`, `RegenHealth`, `flags_extra`, `ScriptName`) VALUES
(3460604, 'Bentley Continental GT', 'vehichleCursor', 80, 80, 0, 35, 0, 0, 0, 2000, 2000, 1, 2181300224, 2048, 9, 0, 0, 0, 318, '', 0, 1, 1, 0, 180, 1, 0, ''),
(3460605, 'Ferrari Enzo', 'vehichleCursor', 80, 80, 0, 35, 0, 0, 0, 2000, 2000, 1, 2181300224, 2048, 9, 0, 0, 0, 318, '', 0, 1, 1, 0, 180, 1, 0, ''),
(3460606, 'Nissan Skyline GT-R R34', 'vehichleCursor', 80, 80, 0, 35, 0, 0, 0, 2000, 2000, 1, 2181300224, 2048, 9, 0, 0, 0, 318, '', 0, 1, 1, 0, 180, 1, 0, ''),
(3460607, 'Lamborghini Aventador', 'vehichleCursor', 80, 80, 0, 35, 0, 0, 0, 2000, 2000, 1, 2181300224, 2048, 9, 0, 0, 0, 318, '', 0, 1, 1, 0, 180, 1, 0, '');

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` IN (4892, 4893, 4894, 4895);
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`) VALUES
(4892, 1027, 'Creature\\\\CustomCars\\\\Bentley\\\\Bentley.mdx', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0),
(4893, 1027, 'Creature\\\\CustomCars\\\\Ferrari\\\\Ferrari.mdx', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0),
(4894, 1027, 'Creature\\\\CustomCars\\\\NissanSkylineR34\\\\SkylineR34.mdx', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0),
(4895, 1027, 'Creature\\\\CustomCars\\\\Lamborghini\\\\Lamborghini.mdx', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0);

DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (94229, 94230, 94231, 94232);
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES
(94229, 4892, 0, 0, 1, 255, 'Bentley_01', 'Bentley_02', 'Bentley_02glow', '', 1, 0, 0, 0, 0, 161),
(94230, 4893, 0, 0, 1, 255, 'Ferrari_01', 'Ferrari_02', 'Ferrari_02glow', '', 1, 0, 0, 0, 0, 161),
(94231, 4894, 0, 0, 1, 255, 'SkylineR34_01', 'SkylineR34_02', 'SkylineR34_02glow', '', 1, 0, 0, 0, 0, 161),
(94232, 4895, 0, 0, 1, 255, 'Lamborghini_01', 'Lamborghini_02', 'Lamborghini_02glow', '', 1, 0, 0, 0, 0, 161);

DELETE FROM `spell_dbc` WHERE `ID` IN (200101, 200102, 200103, 200104);
INSERT INTO `spell_dbc` (`ID`, `Mechanic`, `Attributes`, `AttributesEx6`, `AttributesEx7`, `CastingTimeIndex`, `InterruptFlags`, `ProcChance`, `SpellLevel`, `DurationIndex`, `RangeIndex`, `EquippedItemClass`, `Effect_1`, `Effect_2`, `EffectDieSides_1`, `EffectDieSides_2`, `EffectBasePoints_1`, `EffectBasePoints_2`, `ImplicitTargetA_1`, `ImplicitTargetA_2`, `EffectAura_1`, `EffectAura_2`, `EffectMiscValue_1`, `SpellVisualID_1`, `SpellIconID`, `Name_Lang_enUS`, `Name_Lang_enGB`, `Name_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`, `Description_Lang_Mask`, `AuraDescription_Lang_enUS`, `AuraDescription_Lang_enGB`, `AuraDescription_Lang_Mask`, `StartRecoveryCategory`, `EffectChainAmplitude_1`, `EffectChainAmplitude_2`, `EffectChainAmplitude_3`, `SchoolMask`) VALUES
(200101, 21, 269582608, 131072, 256, 16, 31, 101, 1, 21, 1, -1, 6, 6, 1, 1, -1, 159, 1, 1, 78, 32, 3460604, 14418, 514642, 'Bentley Continental GT', 'Bentley Continental GT', 16712190, 'Rides and parks your Bentley Continental GT.  This is a very fast set of wheels.', 'Rides and parks your Bentley Continental GT.  This is a very fast set of wheels.', 16712190, 'Increases movement speed by $s2%.', 'Increases movement speed by $s2%.', 16712190, 330, 1, 1, 1, 1),
(200102, 21, 269582608, 131072, 256, 16, 31, 101, 1, 21, 1, -1, 6, 6, 1, 1, -1, 159, 1, 1, 78, 32, 3460605, 14418, 514643, 'Ferrari Enzo', 'Ferrari Enzo', 16712190, 'Rides and parks your Ferrari Enzo.  This is a very fast set of wheels.', 'Rides and parks your Ferrari Enzo.  This is a very fast set of wheels.', 16712190, 'Increases movement speed by $s2%.', 'Increases movement speed by $s2%.', 16712190, 330, 1, 1, 1, 1),
(200103, 21, 269582608, 131072, 256, 16, 31, 101, 1, 21, 1, -1, 6, 6, 1, 1, -1, 159, 1, 1, 78, 32, 3460606, 14418, 514644, 'Nissan Skyline GT-R R34', 'Nissan Skyline GT-R R34', 16712190, 'Rides and parks your Nissan Skyline GT-R R34.  This is a very fast set of wheels.', 'Rides and parks your Nissan Skyline GT-R R34.  This is a very fast set of wheels.', 16712190, 'Increases movement speed by $s2%.', 'Increases movement speed by $s2%.', 16712190, 330, 1, 1, 1, 1),
(200104, 21, 269582608, 131072, 256, 16, 31, 101, 1, 21, 1, -1, 6, 6, 1, 1, -1, 159, 1, 1, 78, 32, 3460607, 14418, 514645, 'Lamborghini Aventador', 'Lamborghini Aventador', 16712190, 'Rides and parks your Lamborghini Aventador.  This is a very fast set of wheels.', 'Rides and parks your Lamborghini Aventador.  This is a very fast set of wheels.', 16712190, 'Increases movement speed by $s2%.', 'Increases movement speed by $s2%.', 16712190, 330, 1, 1, 1, 1);

REPLACE INTO `item_template` (`entry`, `class`, `subclass`, `SoundOverrideSubclass`, `name`, `displayid`, `Quality`, `Flags`, `FlagsExtra`, `BuyCount`, `BuyPrice`, `SellPrice`, `InventoryType`, `AllowableClass`, `AllowableRace`, `ItemLevel`, `RequiredLevel`, `RequiredSkill`, `RequiredSkillRank`, `maxcount`, `stackable`, `ContainerSlots`, `bonding`, `description`, `Material`, `sheath`, `RandomProperty`, `RandomSuffix`, `block`, `itemset`, `MaxDurability`, `area`, `Map`, `BagFamily`, `TotemCategory`, `duration`, `ItemLimitCategory`, `HolidayId`, `ScriptName`, `DisenchantID`, `FoodType`, `minMoneyLoot`, `maxMoneyLoot`, `flagsCustom`, `VerifiedBuild`, `spellid_1`, `spelltrigger_1`, `spellcharges_1`, `spellppmRate_1`, `spellcooldown_1`, `spellcategory_1`, `spellcategorycooldown_1`, `spellid_2`, `spelltrigger_2`, `spellcharges_2`, `spellppmRate_2`, `spellcooldown_2`, `spellcategory_2`, `spellcategorycooldown_2`) VALUES
(900137, 15, 5, -1, 'Keys to the Bentley Continental GT', 134239, 4, 0, 0, 1, 50000, 0, 0, 262143, -1, 80, 40, 762, 150, 0, 1, 0, 0, 'Teaches you how to ride the Bentley Continental GT.', 4, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, '', 0, 0, 0, 0, 0, 12340, 483, 0, -1, 0, -1, 330, 3000, 200101, 6, 0, 0, 0, 0, 0),
(900138, 15, 5, -1, 'Keys to the Ferrari Enzo', 134240, 4, 0, 0, 1, 50000, 0, 0, 262143, -1, 80, 40, 762, 150, 0, 1, 0, 0, 'Teaches you how to ride the Ferrari Enzo.', 4, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, '', 0, 0, 0, 0, 0, 12340, 483, 0, -1, 0, -1, 330, 3000, 200102, 6, 0, 0, 0, 0, 0),
(900139, 15, 5, -1, 'Keys to the Nissan Skyline GT-R R34', 134241, 4, 0, 0, 1, 50000, 0, 0, 262143, -1, 80, 40, 762, 150, 0, 1, 0, 0, 'Teaches you how to ride the Nissan Skyline GT-R R34.', 4, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, '', 0, 0, 0, 0, 0, 12340, 483, 0, -1, 0, -1, 330, 3000, 200103, 6, 0, 0, 0, 0, 0),
(900140, 15, 5, -1, 'Keys to the Lamborghini Aventador', 134242, 4, 0, 0, 1, 50000, 0, 0, 262143, -1, 80, 40, 762, 150, 0, 1, 0, 0, 'Teaches you how to ride the Lamborghini Aventador.', 4, 0, 0, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, '', 0, 0, 0, 0, 0, 12340, 483, 0, -1, 0, -1, 330, 3000, 200104, 6, 0, 0, 0, 0, 0);

DELETE FROM `item_dbc` WHERE `ID` IN (900137, 900138, 900139, 900140);
INSERT INTO `item_dbc` (`ID`, `ClassID`, `SubclassID`, `Sound_Override_Subclassid`, `Material`, `DisplayInfoID`, `InventoryType`, `SheatheType`) VALUES
(900137, 15, 5, -1, 4, 134239, 0, 0),
(900138, 15, 5, -1, 4, 134240, 0, 0),
(900139, 15, 5, -1, 4, 134241, 0, 0),
(900140, 15, 5, -1, 4, 134242, 0, 0);

DELETE FROM `itemdisplayinfo_dbc` WHERE `ID` IN (134239, 134240, 134241, 134242);
INSERT INTO `itemdisplayinfo_dbc` (`ID`, `ModelName_1`, `ModelName_2`, `ModelTexture_1`, `ModelTexture_2`, `InventoryIcon_1`, `InventoryIcon_2`, `GeosetGroup_1`, `GeosetGroup_2`, `GeosetGroup_3`, `Flags`, `SpellVisualID`, `GroupSoundIndex`, `HelmetGeosetVis_1`, `HelmetGeosetVis_2`, `Texture_1`, `Texture_2`, `Texture_3`, `Texture_4`, `Texture_5`, `Texture_6`, `Texture_7`, `Texture_8`, `ItemVisual`, `ParticleColorID`) VALUES
(134239, '', '', '', '', 'INV_Misc_Key_Bentley', '', 0, 0, 0, 0, 0, 10, 0, 0, '', '', '', '', '', '', '', '', 0, 0),
(134240, '', '', '', '', 'INV_Misc_Key_Ferrari', '', 0, 0, 0, 0, 0, 10, 0, 0, '', '', '', '', '', '', '', '', 0, 0),
(134241, '', '', '', '', 'INV_Misc_Key_NissanR34', '', 0, 0, 0, 0, 0, 10, 0, 0, '', '', '', '', '', '', '', '', 0, 0),
(134242, '', '', '', '', 'INV_Misc_Key_Lamborghini', '', 0, 0, 0, 0, 0, 10, 0, 0, '', '', '', '', '', '', '', '', 0, 0);
