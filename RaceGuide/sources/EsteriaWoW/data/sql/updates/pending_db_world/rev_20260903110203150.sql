-- Convert playable race ID 15 to Sethrak.
UPDATE `chrraces_dbc` SET `Flags` = 12,
    `FactionID` = 2241,
    `ExplorationSoundID` = 4141,
    `MaleDisplayId` = 60000,
    `FemaleDisplayId` = 60001,
    `ClientPrefix` = 'Se',
    `BaseLanguage` = 1,
    `CreatureType` = 7,
    `ResSicknessSpellID` = 15007,
    `SplashSoundID` = 1096,
    `ClientFilestring` = 'Sethrak',
    `CinematicSequenceID` = 21,
    `Alliance` = 1,
    `Name_Lang_enUS` = 'Sethrak',
    `Name_Female_Lang_enUS` = 'Sethrak',
    `Name_Male_Lang_enUS` = 'Sethrak',
    `FacialHairCustomization_1` = 'NORMAL',
    `FacialHairCustomization_2` = 'PIERCINGS',
    `HairCustomization` = 'NORMAL'
WHERE `ID` = 15;

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` IN (3000000, 3000001, 4896, 4897);
INSERT INTO `creaturemodeldata_dbc` (
    `ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`,
    `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`,
    `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`,
    `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`,
    `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`,
    `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`,
    `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`
) VALUES
    (4896, 2052, 'Character\\Sethrak\\Male\\SethrakMale.mdx', 1, 1, 4, 3, 22, 16, 2, 0, 0, 0, 3111, 0.86650002, 2.54099989, 1.37602603, -1.24910104, -0.808191001, 0.000836000021, 0.594403028, 0.758364022, 2.69475389, 1, 1, 0, 0, 0),
    (4897, 2052, 'Character\\Sethrak\\Female\\SethrakFemale.mdx', 1, 1, 4, 3, 10, 10, 1, 0, 0, 0, 3112, 0.711399972, 2.46399999, 1.286726, -0.971180975, -0.530313015, -0.0133560002, 0.365669012, 0.599041998, 2.52493906, 1, 1, 0, 0, 0);

DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (3000000, 3000001, 60000, 60001);
INSERT INTO `creaturedisplayinfo_dbc` (
    `ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`,
    `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`,
    `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`,
    `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`
) VALUES
    (60000, 4896, 0, 45439, 1.16999996, 255, '', '', '', '', 1, 0, 0, 0, 0, 0),
    (60001, 4897, 0, 45440, 1.16999996, 255, '', '', '', '', 1, 0, 0, 0, 0, 0);

DELETE FROM `creaturedisplayinfoextra_dbc` WHERE `ID` IN (45439, 45440);
INSERT INTO `creaturedisplayinfoextra_dbc` (
    `ID`, `DisplayRaceID`, `DisplaySexID`, `SkinID`, `FaceID`, `HairStyleID`,
    `HairColorID`, `FacialHairID`, `NPCItemDisplay1`, `NPCItemDisplay2`,
    `NPCItemDisplay3`, `NPCItemDisplay4`, `NPCItemDisplay5`, `NPCItemDisplay6`,
    `NPCItemDisplay7`, `NPCItemDisplay8`, `NPCItemDisplay9`, `NPCItemDisplay10`,
    `NPCItemDisplay11`, `Flags`, `BakeName`
) VALUES
    (45439, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, ''),
    (45440, 15, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, '');

DELETE FROM `soundentries_dbc` WHERE `ID` IN (3000300, 3000301, 3000302, 3000303, 3000304, 3000305, 3000306, 3000307, 18070, 18071, 18072, 18073, 18074, 18075, 18076, 18077);
INSERT INTO `soundentries_dbc` (`ID`, `SoundType`, `Name`, `File_1`, `File_2`, `File_3`, `File_4`, `File_5`, `File_6`, `File_7`, `File_8`, `File_9`, `File_10`, `Freq_1`, `Freq_2`, `Freq_3`, `Freq_4`, `Freq_5`, `Freq_6`, `Freq_7`, `Freq_8`, `Freq_9`, `Freq_10`, `DirectoryBase`, `Volumefloat`, `Flags`, `MinDistance`, `DistanceCutoff`, `EAXDef`, `SoundEntriesAdvancedID`) VALUES
    (18070, 10, 'SethrakMalePCAttack', 'SethrakMalePCAttackA.wav', 'SethrakMalePCAttackB.wav', 'SethrakMalePCAttackC.wav', 'SethrakMalePCAttackD.wav', 'SethrakMalePCAttackE.wav', 'SethrakMalePCAttackF.wav', 'SethrakMalePCAttackG.wav', '', '', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakMalePC', 0.6899999976, 0, 8, 45, 0, 0),
    (18071, 10, 'SethrakMalePCWound', 'SethrakMalePCWoundA.wav', 'SethrakMalePCWoundB.wav', 'SethrakMalePCWoundC.wav', 'SethrakMalePCWoundE.wav', 'SethrakMalePCWoundF.wav', 'SethrakMalePCWoundG.wav', 'SethrakMalePCWoundH.wav', 'SethrakMalePCWoundI.wav', 'SethrakMalePCWoundD.wav', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakMalePC', 0.6899999976, 0, 8, 45, 0, 0),
    (18072, 10, 'SethrakMalePCWoundCrit', 'SethrakMalePCWoundCritA.wav', 'SethrakMalePCWoundCritB.wav', 'SethrakMalePCWoundCritC.wav', 'SethrakMalePCWoundCritD.wav', 'SethrakMalePCWoundCritE.wav', '', '', '', '', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakMalePC', 0.6899999976, 0, 8, 45, 0, 0),
    (18073, 10, 'SethrakMalePCDeath', 'SethrakMalePCDeath.wav', '', '', '', '', '', '', '', '', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakMalePC', 0.6899999976, 0, 8, 45, 0, 0),
    (18074, 10, 'SethrakFemalePCAttack', 'SethrakFemalePCAttackA.wav', 'SethrakFemalePCAttackB.wav', 'SethrakFemalePCAttackC.wav', 'SethrakFemalePCAttackD.wav', 'SethrakFemalePCAttackE.wav', 'SethrakFemalePCAttackF.wav', 'SethrakFemalePCAttackG.wav', '', '', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakFemalePC', 0.6899999976, 0, 8, 45, 0, 0),
    (18075, 10, 'SethrakFemalePCWound', 'SethrakFemalePCWoundA.wav', 'SethrakFemalePCWoundB.wav', 'SethrakFemalePCWoundC.wav', 'SethrakFemalePCWoundD.wav', 'SethrakFemalePCWoundE.wav', 'SethrakFemalePCWoundF.wav', 'SethrakFemalePCWoundG.wav', '', '', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakFemalePC', 0.6899999976, 0, 8, 45, 0, 0),
    (18076, 10, 'SethrakFemalePCWoundCrit', 'SethrakFemalePCWoundCritA.wav', 'SethrakFemalePCWoundCritB.wav', 'SethrakFemalePCWoundCritC.wav', '', '', '', '', '', '', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakFemalePC', 0.6899999976, 0, 8, 45, 0, 0),
    (18077, 10, 'SethrakFemalePCDeath', 'SethrakFemalePCDeath.wav', '', '', '', '', '', '', '', '', '', 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 'Sound\\Character\\SethrakFemalePC', 0.6899999976, 0, 8, 45, 0, 0);
