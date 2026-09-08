-- Replace playable Maghar race 14 with Horde Broken; deploy matching client/server DBCs.

DELETE FROM `chrraces_dbc` WHERE `ID` = 14;
INSERT INTO `chrraces_dbc` (
    `ID`, `Flags`, `FactionID`, `ExplorationSoundID`, `MaleDisplayId`, `FemaleDisplayId`, `ClientPrefix`,
    `BaseLanguage`, `CreatureType`, `ResSicknessSpellID`, `SplashSoundID`, `ClientFilestring`,
    `CinematicSequenceID`, `Alliance`, `Name_Lang_enUS`, `Name_Lang_enGB`, `Name_Lang_koKR`, `Name_Lang_frFR`,
    `Name_Lang_deDE`, `Name_Lang_enCN`, `Name_Lang_zhCN`, `Name_Lang_enTW`, `Name_Lang_zhTW`, `Name_Lang_esES`,
    `Name_Lang_esMX`, `Name_Lang_ruRU`, `Name_Lang_ptPT`, `Name_Lang_ptBR`, `Name_Lang_itIT`, `Name_Lang_Unk`,
    `Name_Lang_Mask`, `Name_Female_Lang_enUS`, `Name_Female_Lang_enGB`, `Name_Female_Lang_koKR`,
    `Name_Female_Lang_frFR`, `Name_Female_Lang_deDE`, `Name_Female_Lang_enCN`, `Name_Female_Lang_zhCN`,
    `Name_Female_Lang_enTW`, `Name_Female_Lang_zhTW`, `Name_Female_Lang_esES`, `Name_Female_Lang_esMX`,
    `Name_Female_Lang_ruRU`, `Name_Female_Lang_ptPT`, `Name_Female_Lang_ptBR`, `Name_Female_Lang_itIT`,
    `Name_Female_Lang_Unk`, `Name_Female_Lang_Mask`, `Name_Male_Lang_enUS`, `Name_Male_Lang_enGB`,
    `Name_Male_Lang_koKR`, `Name_Male_Lang_frFR`, `Name_Male_Lang_deDE`, `Name_Male_Lang_enCN`,
    `Name_Male_Lang_zhCN`, `Name_Male_Lang_enTW`, `Name_Male_Lang_zhTW`, `Name_Male_Lang_esES`,
    `Name_Male_Lang_esMX`, `Name_Male_Lang_ruRU`, `Name_Male_Lang_ptPT`, `Name_Male_Lang_ptBR`,
    `Name_Male_Lang_itIT`, `Name_Male_Lang_Unk`, `Name_Male_Lang_Mask`, `FacialHairCustomization_1`,
    `FacialHairCustomization_2`, `HairCustomization`, `Required_Expansion`
) VALUES (
    14, 12, 2, 4141, 60002, 60003, 'Bk', 1, 7, 15007, 1096, 'Broken', 0, 1, 'Broken', 'Broken', 'Broken', 'Broken',
    'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken',
    'Broken', 16712190, 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken',
    'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 16712172, 'Broken', 'Broken', 'Broken',
    'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken', 'Broken',
    'Broken', 'Broken', 16712172, 'NORMAL', 'HORNS', 'NORMAL', 0
);

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 4898;
INSERT INTO `creaturemodeldata_dbc` (
    `ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`,
    `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`,
    `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`,
    `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`,
    `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`
) VALUES (
    4898, 2052, 'Character\\EsteriaBroken\\Male\\BrokenMale.mdx', 0, 1.0, 1, 1, 0.0, 0.0, 0.0, 0, 0, 0, 3113,
    0.6111000180244446, 2.0309998989105225, 0.987214982509613, -1.3760000467300415, -0.8284569978713989,
    -0.003823000006377697, 0.6388900279998779, 0.8293709754943848, 2.4796628952026367, 1.0, 1.0, 0.0, 0.0, 0.0
);

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 4899;
INSERT INTO `creaturemodeldata_dbc` (
    `ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`,
    `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`,
    `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`,
    `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`,
    `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`
) VALUES (
    4899, 2052, 'Character\\EsteriaBroken\\Female\\BrokenFemale.mdx', 0, 1.0, 1, 1, 0.0, 0.0, 0.0, 0, 0, 0, 3114,
    0.666700005531311, 2.1110000610351562, 0.0, -0.7557650208473206, -0.7049469947814941, -0.0007340000011026859,
    0.3308210074901581, 0.7049469947814941, 2.1455399990081787, 1.0, 1.0, 0.0, 0.0, 0.0
);

DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60002;
INSERT INTO `creaturedisplayinfo_dbc` (
    `ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`,
    `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`,
    `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`
) VALUES (
    60002, 4898, 0, 0, 1.0, 255, '', '', '', '', 0, 0, 0, 0, 0, 0
);

DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` = 60003;
INSERT INTO `creaturedisplayinfo_dbc` (
    `ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`,
    `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`,
    `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`
) VALUES (
    60003, 4899, 0, 0, 1.0, 255, '', '', '', '', 0, 0, 0, 0, 0, 0
);

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

DELETE FROM `skilllineability_dbc` WHERE `ID` = 31459;
INSERT INTO `skilllineability_dbc` (
    `ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`, `MinSkillLineRank`,
    `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`, `TrivialSkillLineRankLow`,
    `CharacterPoints_1`, `CharacterPoints_2`
) VALUES (
    31459, 792, 20549, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0
);

DELETE FROM `skilllineability_dbc` WHERE `ID` = 31460;
INSERT INTO `skilllineability_dbc` (
    `ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`, `MinSkillLineRank`,
    `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`, `TrivialSkillLineRankLow`,
    `CharacterPoints_1`, `CharacterPoints_2`
) VALUES (
    31460, 792, 20550, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0
);

DELETE FROM `skilllineability_dbc` WHERE `ID` = 31461;
INSERT INTO `skilllineability_dbc` (
    `ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`, `MinSkillLineRank`,
    `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`, `TrivialSkillLineRankLow`,
    `CharacterPoints_1`, `CharacterPoints_2`
) VALUES (
    31461, 792, 20551, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0
);

DELETE FROM `skilllineability_dbc` WHERE `ID` = 31462;
INSERT INTO `skilllineability_dbc` (
    `ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`, `MinSkillLineRank`,
    `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`, `TrivialSkillLineRankLow`,
    `CharacterPoints_1`, `CharacterPoints_2`
) VALUES (
    31462, 792, 20552, 8192, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0
);

DELETE FROM `achievement_dbc` WHERE `ID` = 1432;
INSERT INTO `achievement_dbc` (
    `ID`, `Faction`, `Instance_Id`, `Supercedes`, `Title_Lang_enUS`, `Title_Lang_enGB`, `Title_Lang_koKR`,
    `Title_Lang_frFR`, `Title_Lang_deDE`, `Title_Lang_enCN`, `Title_Lang_zhCN`, `Title_Lang_enTW`,
    `Title_Lang_zhTW`, `Title_Lang_esES`, `Title_Lang_esMX`, `Title_Lang_ruRU`, `Title_Lang_ptPT`,
    `Title_Lang_ptBR`, `Title_Lang_itIT`, `Title_Lang_Unk`, `Title_Lang_Mask`, `Description_Lang_enUS`,
    `Description_Lang_enGB`, `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`,
    `Description_Lang_enCN`, `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`,
    `Description_Lang_esES`, `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`,
    `Description_Lang_ptBR`, `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Category`,
    `Points`, `Ui_Order`, `Flags`, `IconID`, `Reward_Lang_enUS`, `Reward_Lang_enGB`, `Reward_Lang_koKR`,
    `Reward_Lang_frFR`, `Reward_Lang_deDE`, `Reward_Lang_enCN`, `Reward_Lang_zhCN`, `Reward_Lang_enTW`,
    `Reward_Lang_zhTW`, `Reward_Lang_esES`, `Reward_Lang_esMX`, `Reward_Lang_ruRU`, `Reward_Lang_ptPT`,
    `Reward_Lang_ptBR`, `Reward_Lang_itIT`, `Reward_Lang_Unk`, `Reward_Lang_Mask`, `Minimum_Criteria`,
    `Shares_Criteria`
) VALUES (
    1432, -1, -1, 0, 'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken',
    'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken',
    'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken',
    'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken',
    'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken',
    'Realm First! Level 80 Broken', 'Realm First! Level 80 Broken', 16712190,
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.',
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.',
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.',
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.',
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.',
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.',
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.',
    'First Broken on the realm to achieve level 80.', 'First Broken on the realm to achieve level 80.', 16712190,
    81, 0, 163, 256, 3323, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712174, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `Race` = 14;
DELETE FROM `charsections_dbc` WHERE `ID` = 30000;
DELETE FROM `charsections_dbc` WHERE `ID` = 30001;
DELETE FROM `charsections_dbc` WHERE `ID` = 30002;
DELETE FROM `charsections_dbc` WHERE `ID` = 30003;
DELETE FROM `charsections_dbc` WHERE `ID` = 30004;
DELETE FROM `charsections_dbc` WHERE `ID` = 30005;
DELETE FROM `charsections_dbc` WHERE `ID` = 30006;
DELETE FROM `charsections_dbc` WHERE `ID` = 30007;
DELETE FROM `charsections_dbc` WHERE `ID` = 30008;
DELETE FROM `charsections_dbc` WHERE `ID` = 30009;
DELETE FROM `charsections_dbc` WHERE `ID` = 30010;
DELETE FROM `charsections_dbc` WHERE `ID` = 30011;
DELETE FROM `charsections_dbc` WHERE `ID` = 30012;
DELETE FROM `charsections_dbc` WHERE `ID` = 30013;
DELETE FROM `charsections_dbc` WHERE `ID` = 30014;
DELETE FROM `charsections_dbc` WHERE `ID` = 30015;
DELETE FROM `charsections_dbc` WHERE `ID` = 30016;
DELETE FROM `charsections_dbc` WHERE `ID` = 30017;
DELETE FROM `charsections_dbc` WHERE `ID` = 30018;
DELETE FROM `charsections_dbc` WHERE `ID` = 30019;
DELETE FROM `charsections_dbc` WHERE `ID` = 30020;
DELETE FROM `charsections_dbc` WHERE `ID` = 30021;
DELETE FROM `charsections_dbc` WHERE `ID` = 30022;
DELETE FROM `charsections_dbc` WHERE `ID` = 30023;
DELETE FROM `charsections_dbc` WHERE `ID` = 30024;
DELETE FROM `charsections_dbc` WHERE `ID` = 30025;
DELETE FROM `charsections_dbc` WHERE `ID` = 30026;
DELETE FROM `charsections_dbc` WHERE `ID` = 30027;
DELETE FROM `charsections_dbc` WHERE `ID` = 30028;
DELETE FROM `charsections_dbc` WHERE `ID` = 30029;
DELETE FROM `charsections_dbc` WHERE `ID` = 30030;
DELETE FROM `charsections_dbc` WHERE `ID` = 30031;
DELETE FROM `charsections_dbc` WHERE `ID` = 30032;
DELETE FROM `charsections_dbc` WHERE `ID` = 30033;
DELETE FROM `charsections_dbc` WHERE `ID` = 30034;
DELETE FROM `charsections_dbc` WHERE `ID` = 30035;
DELETE FROM `charsections_dbc` WHERE `ID` = 30036;
DELETE FROM `charsections_dbc` WHERE `ID` = 30037;
DELETE FROM `charsections_dbc` WHERE `ID` = 30038;
DELETE FROM `charsections_dbc` WHERE `ID` = 30039;
DELETE FROM `charsections_dbc` WHERE `ID` = 30040;
DELETE FROM `charsections_dbc` WHERE `ID` = 30041;
DELETE FROM `charsections_dbc` WHERE `ID` = 30042;
DELETE FROM `charsections_dbc` WHERE `ID` = 30043;
DELETE FROM `charsections_dbc` WHERE `ID` = 30044;
DELETE FROM `charsections_dbc` WHERE `ID` = 30045;
DELETE FROM `charsections_dbc` WHERE `ID` = 30046;
DELETE FROM `charsections_dbc` WHERE `ID` = 30047;
DELETE FROM `charsections_dbc` WHERE `ID` = 30048;
DELETE FROM `charsections_dbc` WHERE `ID` = 30049;
DELETE FROM `charsections_dbc` WHERE `ID` = 30050;
DELETE FROM `charsections_dbc` WHERE `ID` = 30051;
DELETE FROM `charsections_dbc` WHERE `ID` = 30052;
DELETE FROM `charsections_dbc` WHERE `ID` = 30053;
DELETE FROM `charsections_dbc` WHERE `ID` = 30054;
DELETE FROM `charsections_dbc` WHERE `ID` = 30055;
DELETE FROM `charsections_dbc` WHERE `ID` = 30056;
DELETE FROM `charsections_dbc` WHERE `ID` = 30057;
DELETE FROM `charsections_dbc` WHERE `ID` = 30058;
DELETE FROM `charsections_dbc` WHERE `ID` = 30059;
DELETE FROM `charsections_dbc` WHERE `ID` = 30060;
DELETE FROM `charsections_dbc` WHERE `ID` = 30061;
DELETE FROM `charsections_dbc` WHERE `ID` = 30062;
DELETE FROM `charsections_dbc` WHERE `ID` = 30063;
DELETE FROM `charsections_dbc` WHERE `ID` = 30064;
DELETE FROM `charsections_dbc` WHERE `ID` = 30065;
DELETE FROM `charsections_dbc` WHERE `ID` = 30066;
DELETE FROM `charsections_dbc` WHERE `ID` = 30067;
DELETE FROM `charsections_dbc` WHERE `ID` = 30068;
DELETE FROM `charsections_dbc` WHERE `ID` = 30069;
DELETE FROM `charsections_dbc` WHERE `ID` = 30070;
DELETE FROM `charsections_dbc` WHERE `ID` = 30071;
DELETE FROM `charsections_dbc` WHERE `ID` = 30072;
DELETE FROM `charsections_dbc` WHERE `ID` = 30073;
DELETE FROM `charsections_dbc` WHERE `ID` = 30074;
DELETE FROM `charsections_dbc` WHERE `ID` = 30075;
DELETE FROM `charsections_dbc` WHERE `ID` = 30076;
DELETE FROM `charsections_dbc` WHERE `ID` = 30077;
DELETE FROM `charsections_dbc` WHERE `ID` = 30078;
DELETE FROM `charsections_dbc` WHERE `ID` = 30079;
DELETE FROM `charsections_dbc` WHERE `ID` = 30080;
DELETE FROM `charsections_dbc` WHERE `ID` = 30081;
DELETE FROM `charsections_dbc` WHERE `ID` = 30082;
DELETE FROM `charsections_dbc` WHERE `ID` = 30083;
DELETE FROM `charsections_dbc` WHERE `ID` = 30084;
DELETE FROM `charsections_dbc` WHERE `ID` = 30085;
DELETE FROM `charsections_dbc` WHERE `ID` = 30086;
DELETE FROM `charsections_dbc` WHERE `ID` = 30087;
DELETE FROM `charsections_dbc` WHERE `ID` = 30088;
DELETE FROM `charsections_dbc` WHERE `ID` = 30089;
DELETE FROM `charsections_dbc` WHERE `ID` = 30090;
DELETE FROM `charsections_dbc` WHERE `ID` = 30091;
DELETE FROM `charsections_dbc` WHERE `ID` = 30092;
DELETE FROM `charsections_dbc` WHERE `ID` = 30093;
DELETE FROM `charsections_dbc` WHERE `ID` = 30094;
DELETE FROM `charsections_dbc` WHERE `ID` = 30095;
DELETE FROM `charsections_dbc` WHERE `ID` = 30096;
DELETE FROM `charsections_dbc` WHERE `ID` = 30097;
DELETE FROM `charsections_dbc` WHERE `ID` = 30098;
DELETE FROM `charsections_dbc` WHERE `ID` = 30099;
DELETE FROM `charsections_dbc` WHERE `ID` = 30100;
DELETE FROM `charsections_dbc` WHERE `ID` = 30101;
DELETE FROM `charsections_dbc` WHERE `ID` = 30102;
DELETE FROM `charsections_dbc` WHERE `ID` = 30103;
DELETE FROM `charsections_dbc` WHERE `ID` = 30104;
DELETE FROM `charsections_dbc` WHERE `ID` = 30105;
DELETE FROM `charsections_dbc` WHERE `ID` = 30106;
DELETE FROM `charsections_dbc` WHERE `ID` = 30107;
DELETE FROM `charsections_dbc` WHERE `ID` = 30108;
DELETE FROM `charsections_dbc` WHERE `ID` = 30109;
DELETE FROM `charsections_dbc` WHERE `ID` = 30110;
DELETE FROM `charsections_dbc` WHERE `ID` = 30111;
DELETE FROM `charsections_dbc` WHERE `ID` = 30112;
DELETE FROM `charsections_dbc` WHERE `ID` = 30113;
DELETE FROM `charsections_dbc` WHERE `ID` = 30114;
DELETE FROM `charsections_dbc` WHERE `ID` = 30115;
DELETE FROM `charsections_dbc` WHERE `ID` = 30116;
DELETE FROM `charsections_dbc` WHERE `ID` = 30117;
DELETE FROM `charsections_dbc` WHERE `ID` = 30118;
DELETE FROM `charsections_dbc` WHERE `ID` = 30119;
DELETE FROM `charsections_dbc` WHERE `ID` = 30120;
DELETE FROM `charsections_dbc` WHERE `ID` = 30121;
DELETE FROM `charsections_dbc` WHERE `ID` = 30122;
DELETE FROM `charsections_dbc` WHERE `ID` = 30123;
DELETE FROM `charsections_dbc` WHERE `ID` = 30124;
DELETE FROM `charsections_dbc` WHERE `ID` = 30125;
DELETE FROM `charsections_dbc` WHERE `ID` = 30126;
DELETE FROM `charsections_dbc` WHERE `ID` = 30127;
DELETE FROM `charsections_dbc` WHERE `ID` = 30128;
DELETE FROM `charsections_dbc` WHERE `ID` = 30129;
DELETE FROM `charsections_dbc` WHERE `ID` = 30130;
DELETE FROM `charsections_dbc` WHERE `ID` = 30131;
DELETE FROM `charsections_dbc` WHERE `ID` = 30132;
DELETE FROM `charsections_dbc` WHERE `ID` = 30133;
DELETE FROM `charsections_dbc` WHERE `ID` = 30134;
DELETE FROM `charsections_dbc` WHERE `ID` = 30135;
DELETE FROM `charsections_dbc` WHERE `ID` = 30136;
DELETE FROM `charsections_dbc` WHERE `ID` = 30137;
DELETE FROM `charsections_dbc` WHERE `ID` = 30138;
DELETE FROM `charsections_dbc` WHERE `ID` = 30139;
DELETE FROM `charsections_dbc` WHERE `ID` = 30140;
DELETE FROM `charsections_dbc` WHERE `ID` = 30141;
DELETE FROM `charsections_dbc` WHERE `ID` = 30142;
DELETE FROM `charsections_dbc` WHERE `ID` = 30143;
DELETE FROM `charsections_dbc` WHERE `ID` = 30144;
DELETE FROM `charsections_dbc` WHERE `ID` = 30145;
DELETE FROM `charsections_dbc` WHERE `ID` = 30146;
DELETE FROM `charsections_dbc` WHERE `ID` = 30147;
DELETE FROM `charsections_dbc` WHERE `ID` = 30148;
DELETE FROM `charsections_dbc` WHERE `ID` = 30149;
DELETE FROM `charsections_dbc` WHERE `ID` = 30150;
DELETE FROM `charsections_dbc` WHERE `ID` = 30151;
DELETE FROM `charsections_dbc` WHERE `ID` = 30152;
DELETE FROM `charsections_dbc` WHERE `ID` = 30153;
DELETE FROM `charsections_dbc` WHERE `ID` = 30154;
DELETE FROM `charsections_dbc` WHERE `ID` = 30155;
DELETE FROM `charsections_dbc` WHERE `ID` = 30156;
DELETE FROM `charsections_dbc` WHERE `ID` = 30157;
DELETE FROM `charsections_dbc` WHERE `ID` = 30158;
DELETE FROM `charsections_dbc` WHERE `ID` = 30159;
DELETE FROM `charsections_dbc` WHERE `ID` = 30160;
DELETE FROM `charsections_dbc` WHERE `ID` = 30161;
DELETE FROM `charsections_dbc` WHERE `ID` = 30162;
DELETE FROM `charsections_dbc` WHERE `ID` = 30163;
DELETE FROM `charsections_dbc` WHERE `ID` = 30164;
DELETE FROM `charsections_dbc` WHERE `ID` = 30165;
DELETE FROM `charsections_dbc` WHERE `ID` = 30166;
DELETE FROM `charsections_dbc` WHERE `ID` = 30167;
DELETE FROM `charsections_dbc` WHERE `ID` = 30168;
DELETE FROM `charsections_dbc` WHERE `ID` = 30169;
DELETE FROM `charsections_dbc` WHERE `ID` = 30170;
DELETE FROM `charsections_dbc` WHERE `ID` = 30171;
DELETE FROM `charsections_dbc` WHERE `ID` = 30172;
DELETE FROM `charsections_dbc` WHERE `ID` = 30173;
DELETE FROM `charsections_dbc` WHERE `ID` = 30174;
DELETE FROM `charsections_dbc` WHERE `ID` = 30175;
DELETE FROM `charsections_dbc` WHERE `ID` = 30176;
DELETE FROM `charsections_dbc` WHERE `ID` = 30177;
DELETE FROM `charsections_dbc` WHERE `ID` = 30178;
DELETE FROM `charsections_dbc` WHERE `ID` = 30179;
DELETE FROM `charsections_dbc` WHERE `ID` = 30180;
DELETE FROM `charsections_dbc` WHERE `ID` = 30181;
DELETE FROM `charsections_dbc` WHERE `ID` = 30182;
DELETE FROM `charsections_dbc` WHERE `ID` = 30183;
DELETE FROM `charsections_dbc` WHERE `ID` = 30184;
DELETE FROM `charsections_dbc` WHERE `ID` = 30185;
DELETE FROM `charsections_dbc` WHERE `ID` = 30186;
DELETE FROM `charsections_dbc` WHERE `ID` = 30187;
DELETE FROM `charsections_dbc` WHERE `ID` = 30188;
DELETE FROM `charsections_dbc` WHERE `ID` = 30189;
DELETE FROM `charsections_dbc` WHERE `ID` = 30190;
DELETE FROM `charsections_dbc` WHERE `ID` = 30191;
DELETE FROM `charsections_dbc` WHERE `ID` = 30192;
DELETE FROM `charsections_dbc` WHERE `ID` = 30193;
DELETE FROM `charsections_dbc` WHERE `ID` = 30194;
DELETE FROM `charsections_dbc` WHERE `ID` = 30195;
DELETE FROM `charsections_dbc` WHERE `ID` = 30196;
DELETE FROM `charsections_dbc` WHERE `ID` = 30197;
DELETE FROM `charsections_dbc` WHERE `ID` = 30198;
DELETE FROM `charsections_dbc` WHERE `ID` = 30199;
DELETE FROM `charsections_dbc` WHERE `ID` = 30200;
DELETE FROM `charsections_dbc` WHERE `ID` = 30201;
DELETE FROM `charsections_dbc` WHERE `ID` = 30202;
DELETE FROM `charsections_dbc` WHERE `ID` = 30203;
DELETE FROM `charsections_dbc` WHERE `ID` = 30204;
DELETE FROM `charsections_dbc` WHERE `ID` = 30205;
DELETE FROM `charsections_dbc` WHERE `ID` = 30206;
DELETE FROM `charsections_dbc` WHERE `ID` = 30207;
DELETE FROM `charsections_dbc` WHERE `ID` = 30208;
DELETE FROM `charsections_dbc` WHERE `ID` = 30209;
DELETE FROM `charsections_dbc` WHERE `ID` = 30210;
DELETE FROM `charsections_dbc` WHERE `ID` = 30211;
DELETE FROM `charsections_dbc` WHERE `ID` = 30212;
DELETE FROM `charsections_dbc` WHERE `ID` = 30213;
DELETE FROM `charsections_dbc` WHERE `ID` = 30214;
DELETE FROM `charsections_dbc` WHERE `ID` = 30215;
DELETE FROM `charsections_dbc` WHERE `ID` = 30216;
DELETE FROM `charsections_dbc` WHERE `ID` = 30217;
DELETE FROM `charsections_dbc` WHERE `ID` = 30218;
DELETE FROM `charsections_dbc` WHERE `ID` = 30219;
DELETE FROM `charsections_dbc` WHERE `ID` = 30220;
DELETE FROM `charsections_dbc` WHERE `ID` = 30221;
DELETE FROM `charsections_dbc` WHERE `ID` = 30222;
DELETE FROM `charsections_dbc` WHERE `ID` = 30223;
DELETE FROM `charsections_dbc` WHERE `ID` = 30224;
DELETE FROM `charsections_dbc` WHERE `ID` = 30225;
DELETE FROM `charsections_dbc` WHERE `ID` = 30226;
DELETE FROM `charsections_dbc` WHERE `ID` = 30227;
DELETE FROM `charsections_dbc` WHERE `ID` = 30228;
DELETE FROM `charsections_dbc` WHERE `ID` = 30229;
DELETE FROM `charsections_dbc` WHERE `ID` = 30230;
DELETE FROM `charsections_dbc` WHERE `ID` = 30231;
DELETE FROM `charsections_dbc` WHERE `ID` = 30232;
DELETE FROM `charsections_dbc` WHERE `ID` = 30233;
DELETE FROM `charsections_dbc` WHERE `ID` = 30234;
DELETE FROM `charsections_dbc` WHERE `ID` = 30235;
DELETE FROM `charsections_dbc` WHERE `ID` = 30236;
DELETE FROM `charsections_dbc` WHERE `ID` = 30237;
DELETE FROM `charsections_dbc` WHERE `ID` = 30238;
DELETE FROM `charsections_dbc` WHERE `ID` = 30239;
DELETE FROM `charsections_dbc` WHERE `ID` = 30240;
DELETE FROM `charsections_dbc` WHERE `ID` = 30241;
DELETE FROM `charsections_dbc` WHERE `ID` = 30242;
DELETE FROM `charsections_dbc` WHERE `ID` = 30243;
DELETE FROM `charsections_dbc` WHERE `ID` = 30244;
DELETE FROM `charsections_dbc` WHERE `ID` = 30245;
DELETE FROM `charsections_dbc` WHERE `ID` = 30246;
DELETE FROM `charsections_dbc` WHERE `ID` = 30247;
DELETE FROM `charsections_dbc` WHERE `ID` = 30248;
DELETE FROM `charsections_dbc` WHERE `ID` = 30249;
DELETE FROM `charsections_dbc` WHERE `ID` = 30250;
DELETE FROM `charsections_dbc` WHERE `ID` = 30251;
DELETE FROM `charsections_dbc` WHERE `ID` = 30252;
DELETE FROM `charsections_dbc` WHERE `ID` = 30253;
DELETE FROM `charsections_dbc` WHERE `ID` = 30254;
DELETE FROM `charsections_dbc` WHERE `ID` = 30255;
DELETE FROM `charsections_dbc` WHERE `ID` = 30256;
DELETE FROM `charsections_dbc` WHERE `ID` = 30257;
DELETE FROM `charsections_dbc` WHERE `ID` = 30258;
DELETE FROM `charsections_dbc` WHERE `ID` = 30259;
DELETE FROM `charsections_dbc` WHERE `ID` = 30260;
DELETE FROM `charsections_dbc` WHERE `ID` = 30261;
DELETE FROM `charsections_dbc` WHERE `ID` = 30262;
DELETE FROM `charsections_dbc` WHERE `ID` = 30263;
DELETE FROM `charsections_dbc` WHERE `ID` = 30264;
DELETE FROM `charsections_dbc` WHERE `ID` = 30265;
DELETE FROM `charsections_dbc` WHERE `ID` = 30266;
DELETE FROM `charsections_dbc` WHERE `ID` = 30267;
DELETE FROM `charsections_dbc` WHERE `ID` = 30268;
DELETE FROM `charsections_dbc` WHERE `ID` = 30269;
DELETE FROM `charsections_dbc` WHERE `ID` = 30270;
DELETE FROM `charsections_dbc` WHERE `ID` = 30271;
DELETE FROM `charsections_dbc` WHERE `ID` = 30272;
DELETE FROM `charsections_dbc` WHERE `ID` = 30273;
DELETE FROM `charsections_dbc` WHERE `ID` = 30274;
DELETE FROM `charsections_dbc` WHERE `ID` = 30275;
DELETE FROM `charsections_dbc` WHERE `ID` = 30276;
DELETE FROM `charsections_dbc` WHERE `ID` = 30277;
DELETE FROM `charsections_dbc` WHERE `ID` = 30278;
DELETE FROM `charsections_dbc` WHERE `ID` = 30279;
DELETE FROM `charsections_dbc` WHERE `ID` = 30280;
DELETE FROM `charsections_dbc` WHERE `ID` = 30281;
DELETE FROM `charsections_dbc` WHERE `ID` = 30282;
DELETE FROM `charsections_dbc` WHERE `ID` = 30283;
DELETE FROM `charsections_dbc` WHERE `ID` = 30284;
DELETE FROM `charsections_dbc` WHERE `ID` = 30285;
DELETE FROM `charsections_dbc` WHERE `ID` = 30286;
DELETE FROM `charsections_dbc` WHERE `ID` = 30287;
DELETE FROM `charsections_dbc` WHERE `ID` = 30288;
DELETE FROM `charsections_dbc` WHERE `ID` = 30289;
DELETE FROM `charsections_dbc` WHERE `ID` = 30290;
DELETE FROM `charsections_dbc` WHERE `ID` = 30291;
DELETE FROM `charsections_dbc` WHERE `ID` = 30292;
DELETE FROM `charsections_dbc` WHERE `ID` = 30293;
DELETE FROM `charsections_dbc` WHERE `ID` = 30294;
DELETE FROM `charsections_dbc` WHERE `ID` = 30295;
DELETE FROM `charsections_dbc` WHERE `ID` = 30296;
DELETE FROM `charsections_dbc` WHERE `ID` = 30297;
DELETE FROM `charsections_dbc` WHERE `ID` = 30298;
DELETE FROM `charsections_dbc` WHERE `ID` = 30299;
DELETE FROM `charsections_dbc` WHERE `ID` = 30300;
DELETE FROM `charsections_dbc` WHERE `ID` = 30301;
DELETE FROM `charsections_dbc` WHERE `ID` = 30302;
DELETE FROM `charsections_dbc` WHERE `ID` = 30303;
DELETE FROM `charsections_dbc` WHERE `ID` = 30304;
DELETE FROM `charsections_dbc` WHERE `ID` = 30305;
DELETE FROM `charsections_dbc` WHERE `ID` = 30306;
DELETE FROM `charsections_dbc` WHERE `ID` = 30307;
DELETE FROM `charsections_dbc` WHERE `ID` = 30308;
DELETE FROM `charsections_dbc` WHERE `ID` = 30309;
DELETE FROM `charsections_dbc` WHERE `ID` = 30310;
DELETE FROM `charsections_dbc` WHERE `ID` = 30311;
DELETE FROM `charsections_dbc` WHERE `ID` = 30312;
DELETE FROM `charsections_dbc` WHERE `ID` = 30313;
DELETE FROM `charsections_dbc` WHERE `ID` = 30314;
DELETE FROM `charsections_dbc` WHERE `ID` = 30315;
DELETE FROM `charsections_dbc` WHERE `ID` = 30316;
DELETE FROM `charsections_dbc` WHERE `ID` = 30317;
DELETE FROM `charsections_dbc` WHERE `ID` = 30318;
DELETE FROM `charsections_dbc` WHERE `ID` = 30319;
DELETE FROM `charsections_dbc` WHERE `ID` = 30320;
DELETE FROM `charsections_dbc` WHERE `ID` = 30321;
DELETE FROM `charsections_dbc` WHERE `ID` = 30322;
DELETE FROM `charsections_dbc` WHERE `ID` = 30323;
DELETE FROM `charsections_dbc` WHERE `ID` = 30324;
DELETE FROM `charsections_dbc` WHERE `ID` = 30325;
DELETE FROM `charsections_dbc` WHERE `ID` = 30326;
DELETE FROM `charsections_dbc` WHERE `ID` = 30327;
DELETE FROM `charsections_dbc` WHERE `ID` = 30328;
DELETE FROM `charsections_dbc` WHERE `ID` = 30329;
DELETE FROM `charsections_dbc` WHERE `ID` = 30330;
DELETE FROM `charsections_dbc` WHERE `ID` = 30331;
DELETE FROM `charsections_dbc` WHERE `ID` = 30332;
DELETE FROM `charsections_dbc` WHERE `ID` = 30333;
DELETE FROM `charsections_dbc` WHERE `ID` = 30334;
DELETE FROM `charsections_dbc` WHERE `ID` = 30335;
DELETE FROM `charsections_dbc` WHERE `ID` = 30336;
DELETE FROM `charsections_dbc` WHERE `ID` = 30337;
DELETE FROM `charsections_dbc` WHERE `ID` = 30338;
DELETE FROM `charsections_dbc` WHERE `ID` = 30339;
DELETE FROM `charsections_dbc` WHERE `ID` = 30340;
DELETE FROM `charsections_dbc` WHERE `ID` = 30341;
DELETE FROM `charsections_dbc` WHERE `ID` = 30342;
DELETE FROM `charsections_dbc` WHERE `ID` = 30343;
DELETE FROM `charsections_dbc` WHERE `ID` = 30344;
DELETE FROM `charsections_dbc` WHERE `ID` = 30345;
DELETE FROM `charsections_dbc` WHERE `ID` = 30346;
DELETE FROM `charsections_dbc` WHERE `ID` = 30347;
DELETE FROM `charsections_dbc` WHERE `ID` = 30348;
DELETE FROM `charsections_dbc` WHERE `ID` = 30349;
DELETE FROM `charsections_dbc` WHERE `ID` = 30350;
DELETE FROM `charsections_dbc` WHERE `ID` = 30351;
DELETE FROM `charsections_dbc` WHERE `ID` = 30352;
DELETE FROM `charsections_dbc` WHERE `ID` = 30353;
DELETE FROM `charsections_dbc` WHERE `ID` = 30354;
DELETE FROM `charsections_dbc` WHERE `ID` = 30355;
DELETE FROM `charsections_dbc` WHERE `ID` = 30356;
DELETE FROM `charsections_dbc` WHERE `ID` = 30357;
DELETE FROM `charsections_dbc` WHERE `ID` = 30358;
DELETE FROM `charsections_dbc` WHERE `ID` = 30359;
DELETE FROM `charsections_dbc` WHERE `ID` = 30360;
DELETE FROM `charsections_dbc` WHERE `ID` = 30361;
DELETE FROM `charsections_dbc` WHERE `ID` = 30362;
DELETE FROM `charsections_dbc` WHERE `ID` = 30363;
DELETE FROM `charsections_dbc` WHERE `ID` = 30364;
DELETE FROM `charsections_dbc` WHERE `ID` = 30365;
DELETE FROM `charsections_dbc` WHERE `ID` = 30366;
DELETE FROM `charsections_dbc` WHERE `ID` = 30367;
DELETE FROM `charsections_dbc` WHERE `ID` = 30368;
DELETE FROM `charsections_dbc` WHERE `ID` = 30369;
DELETE FROM `charsections_dbc` WHERE `ID` = 30370;
DELETE FROM `charsections_dbc` WHERE `ID` = 30371;
DELETE FROM `charsections_dbc` WHERE `ID` = 30372;
DELETE FROM `charsections_dbc` WHERE `ID` = 30373;
DELETE FROM `charsections_dbc` WHERE `ID` = 30374;
DELETE FROM `charsections_dbc` WHERE `ID` = 30375;
DELETE FROM `charsections_dbc` WHERE `ID` = 30376;
DELETE FROM `charsections_dbc` WHERE `ID` = 30377;
DELETE FROM `charsections_dbc` WHERE `ID` = 30378;
DELETE FROM `charsections_dbc` WHERE `ID` = 30379;
DELETE FROM `charsections_dbc` WHERE `ID` = 30380;
DELETE FROM `charsections_dbc` WHERE `ID` = 30381;
DELETE FROM `charsections_dbc` WHERE `ID` = 30382;
DELETE FROM `charsections_dbc` WHERE `ID` = 30383;
DELETE FROM `charsections_dbc` WHERE `ID` = 30384;
DELETE FROM `charsections_dbc` WHERE `ID` = 30385;
DELETE FROM `charsections_dbc` WHERE `ID` = 30386;
DELETE FROM `charsections_dbc` WHERE `ID` = 30387;
DELETE FROM `charsections_dbc` WHERE `ID` = 30388;
DELETE FROM `charsections_dbc` WHERE `ID` = 30389;
DELETE FROM `charsections_dbc` WHERE `ID` = 30390;
DELETE FROM `charsections_dbc` WHERE `ID` = 30391;
DELETE FROM `charsections_dbc` WHERE `ID` = 30392;
DELETE FROM `charsections_dbc` WHERE `ID` = 30393;
DELETE FROM `charsections_dbc` WHERE `ID` = 30394;
DELETE FROM `charsections_dbc` WHERE `ID` = 30395;
DELETE FROM `charsections_dbc` WHERE `ID` = 30396;
DELETE FROM `charsections_dbc` WHERE `ID` = 30397;
DELETE FROM `charsections_dbc` WHERE `ID` = 30398;
DELETE FROM `charsections_dbc` WHERE `ID` = 30399;
DELETE FROM `charsections_dbc` WHERE `ID` = 30400;
DELETE FROM `charsections_dbc` WHERE `ID` = 30401;
DELETE FROM `charsections_dbc` WHERE `ID` = 30402;
DELETE FROM `charsections_dbc` WHERE `ID` = 30403;
DELETE FROM `charsections_dbc` WHERE `ID` = 30404;
DELETE FROM `charsections_dbc` WHERE `ID` = 30405;
DELETE FROM `charsections_dbc` WHERE `ID` = 30406;
DELETE FROM `charsections_dbc` WHERE `ID` = 30407;
DELETE FROM `charsections_dbc` WHERE `ID` = 30408;
DELETE FROM `charsections_dbc` WHERE `ID` = 30409;
DELETE FROM `charsections_dbc` WHERE `ID` = 30410;
DELETE FROM `charsections_dbc` WHERE `ID` = 30411;
DELETE FROM `charsections_dbc` WHERE `ID` = 30412;
DELETE FROM `charsections_dbc` WHERE `ID` = 30413;
DELETE FROM `charsections_dbc` WHERE `ID` = 30414;
DELETE FROM `charsections_dbc` WHERE `ID` = 30415;
DELETE FROM `charsections_dbc` WHERE `ID` = 30416;
DELETE FROM `charsections_dbc` WHERE `ID` = 30417;
DELETE FROM `charsections_dbc` WHERE `ID` = 30418;
DELETE FROM `charsections_dbc` WHERE `ID` = 30419;
DELETE FROM `charsections_dbc` WHERE `ID` = 30420;
DELETE FROM `charsections_dbc` WHERE `ID` = 30421;
DELETE FROM `charsections_dbc` WHERE `ID` = 30422;
DELETE FROM `charsections_dbc` WHERE `ID` = 30423;
DELETE FROM `charsections_dbc` WHERE `ID` = 30424;
DELETE FROM `charsections_dbc` WHERE `ID` = 30425;

DELETE FROM `charsections_dbc` WHERE `ID` = 30466;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30466, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_00_Extra.blp', '', 17, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30467;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30467, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_01_Extra.blp', '', 17, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30468;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30468, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_02_Extra.blp', '', 17, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30469;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30469, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_03_Extra.blp', '', 17, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30470;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30470, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_04_Extra.blp', '', 17, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30471;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30471, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_05_Extra.blp', '', 17, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30472;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30472, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_06_Extra.blp', '', 17, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30473;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30473, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_07_Extra.blp', '', 17, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30474;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30474, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_08_Extra.blp', '', 17, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30475;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30475, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_09_Extra.blp', '', 17, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30476;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30476, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_10_Extra.blp', '', 17, 0, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30477;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30477, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_11_Extra.blp', '', 17, 0, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30478;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30478, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_12_Extra.blp', '', 17, 0, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30479;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30479, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_13_Extra.blp', '', 17, 0, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30480;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30480, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_14.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_14_Extra.blp', '', 5, 0, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30481;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30481, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_15.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_15_Extra.blp', '', 5, 0, 15
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30482;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30482, 14, 0, 0, 'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_16.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleSkin00_16_Extra.blp', '', 5, 0, 16
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30483;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30483, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_00.blp', '', 1, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30484;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30484, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_01.blp', '', 1, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30485;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30485, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_02.blp', '', 1, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30486;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30486, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_03.blp', '', 1, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30487;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30487, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_04.blp', '', 1, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30488;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30488, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_05.blp', '', 1, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30489;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30489, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_06.blp', '', 1, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30490;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30490, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_07.blp', '', 1, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30491;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30491, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_08.blp', '', 1, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30492;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30492, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_09.blp', '', 1, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30493;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30493, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_10.blp', '', 1, 0, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30494;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30494, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_11.blp', '', 1, 0, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30495;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30495, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_12.blp', '', 1, 0, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30496;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30496, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_13.blp', '', 1, 0, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30497;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30497, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_00.blp', '', 1, 1, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30498;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30498, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_01.blp', '', 1, 1, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30499;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30499, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_02.blp', '', 1, 1, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30500;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30500, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_03.blp', '', 1, 1, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30501;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30501, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_04.blp', '', 1, 1, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30502;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30502, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_05.blp', '', 1, 1, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30503;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30503, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_06.blp', '', 1, 1, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30504;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30504, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_07.blp', '', 1, 1, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30505;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30505, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_08.blp', '', 1, 1, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30506;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30506, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_09.blp', '', 1, 1, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30507;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30507, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_10.blp', '', 1, 1, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30508;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30508, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_11.blp', '', 1, 1, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30509;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30509, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_12.blp', '', 1, 1, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30510;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30510, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_13.blp', '', 1, 1, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30511;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30511, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_14.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_14.blp', '', 5, 1, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30512;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30512, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_15.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_15.blp', '', 5, 1, 15
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30513;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30513, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_16.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_16.blp', '', 5, 1, 16
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30514;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30514, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_00.blp', '', 1, 2, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30515;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30515, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_01.blp', '', 1, 2, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30516;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30516, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_02.blp', '', 1, 2, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30517;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30517, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_03.blp', '', 1, 2, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30518;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30518, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_04.blp', '', 1, 2, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30519;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30519, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_05.blp', '', 1, 2, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30520;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30520, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_06.blp', '', 1, 2, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30521;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30521, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_07.blp', '', 1, 2, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30522;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30522, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_08.blp', '', 1, 2, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30523;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30523, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_09.blp', '', 1, 2, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30524;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30524, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_10.blp', '', 1, 2, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30525;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30525, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_11.blp', '', 1, 2, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30526;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30526, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_12.blp', '', 1, 2, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30527;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30527, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_13.blp', '', 1, 2, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30528;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30528, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_00.blp', '', 1, 3, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30529;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30529, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_01.blp', '', 1, 3, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30530;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30530, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_02.blp', '', 1, 3, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30531;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30531, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_03.blp', '', 1, 3, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30532;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30532, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_04.blp', '', 1, 3, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30533;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30533, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_05.blp', '', 1, 3, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30534;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30534, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_06.blp', '', 1, 3, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30535;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30535, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_07.blp', '', 1, 3, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30536;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30536, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_08.blp', '', 1, 3, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30537;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30537, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_09.blp', '', 1, 3, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30538;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30538, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_10.blp', '', 1, 3, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30539;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30539, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_11.blp', '', 1, 3, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30540;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30540, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_12.blp', '', 1, 3, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30541;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30541, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_13.blp', '', 1, 3, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30542;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30542, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_00.blp', '', 1, 4, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30543;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30543, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_01.blp', '', 1, 4, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30544;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30544, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_02.blp', '', 1, 4, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30545;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30545, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_03.blp', '', 1, 4, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30546;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30546, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_04.blp', '', 1, 4, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30547;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30547, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_05.blp', '', 1, 4, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30548;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30548, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_06.blp', '', 1, 4, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30549;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30549, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_07.blp', '', 1, 4, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30550;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30550, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_08.blp', '', 1, 4, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30551;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30551, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_09.blp', '', 1, 4, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30552;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30552, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_10.blp', '', 1, 4, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30553;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30553, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_11.blp', '', 1, 4, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30554;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30554, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_12.blp', '', 1, 4, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30555;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30555, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_13.blp', '', 1, 4, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30556;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30556, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_14.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_14.blp', '', 5, 4, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30557;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30557, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_15.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_15.blp', '', 5, 4, 15
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30558;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30558, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_16.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_16.blp', '', 5, 4, 16
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30559;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30559, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_00.blp', '', 1, 5, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30560;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30560, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_01.blp', '', 1, 5, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30561;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30561, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_02.blp', '', 1, 5, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30562;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30562, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_03.blp', '', 1, 5, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30563;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30563, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_04.blp', '', 1, 5, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30564;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30564, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_05.blp', '', 1, 5, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30565;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30565, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_06.blp', '', 1, 5, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30566;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30566, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_07.blp', '', 1, 5, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30567;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30567, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_08.blp', '', 1, 5, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30568;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30568, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_09.blp', '', 1, 5, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30569;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30569, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_10.blp', '', 1, 5, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30570;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30570, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_11.blp', '', 1, 5, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30571;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30571, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_12.blp', '', 1, 5, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30572;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30572, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_13.blp', '', 1, 5, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30573;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30573, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_00.blp', '', 1, 6, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30574;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30574, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_01.blp', '', 1, 6, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30575;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30575, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_02.blp', '', 1, 6, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30576;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30576, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_03.blp', '', 1, 6, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30577;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30577, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_04.blp', '', 1, 6, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30578;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30578, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_05.blp', '', 1, 6, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30579;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30579, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_06.blp', '', 1, 6, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30580;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30580, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_07.blp', '', 1, 6, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30581;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30581, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_08.blp', '', 1, 6, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30582;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30582, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_09.blp', '', 1, 6, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30583;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30583, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_10.blp', '', 1, 6, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30584;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30584, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_11.blp', '', 1, 6, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30585;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30585, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_12.blp', '', 1, 6, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30586;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30586, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_13.blp', '', 1, 6, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30587;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30587, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_00.blp', '', 1, 7, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30588;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30588, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_01.blp', '', 1, 7, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30589;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30589, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_02.blp', '', 1, 7, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30590;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30590, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_03.blp', '', 1, 7, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30591;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30591, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_04.blp', '', 1, 7, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30592;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30592, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_05.blp', '', 1, 7, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30593;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30593, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_06.blp', '', 1, 7, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30594;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30594, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_07.blp', '', 1, 7, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30595;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30595, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_08.blp', '', 1, 7, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30596;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30596, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_09.blp', '', 1, 7, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30597;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30597, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_10.blp', '', 1, 7, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30598;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30598, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_11.blp', '', 1, 7, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30599;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30599, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_12.blp', '', 1, 7, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30600;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30600, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_13.blp', '', 1, 7, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30601;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30601, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_00.blp', '', 1, 8, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30602;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30602, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_01.blp', '', 1, 8, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30603;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30603, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_02.blp', '', 1, 8, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30604;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30604, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_03.blp', '', 1, 8, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30605;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30605, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_04.blp', '', 1, 8, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30606;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30606, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_05.blp', '', 1, 8, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30607;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30607, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_06.blp', '', 1, 8, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30608;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30608, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_07.blp', '', 1, 8, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30609;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30609, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_08.blp', '', 1, 8, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30610;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30610, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_09.blp', '', 1, 8, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30611;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30611, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_10.blp', '', 1, 8, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30612;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30612, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_11.blp', '', 1, 8, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30613;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30613, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_12.blp', '', 1, 8, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30614;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30614, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_13.blp', '', 1, 8, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30615;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30615, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_00.blp', '', 1, 9, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30616;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30616, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_01.blp', '', 1, 9, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30617;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30617, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_02.blp', '', 1, 9, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30618;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30618, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_03.blp', '', 1, 9, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30619;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30619, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_04.blp', '', 1, 9, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30620;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30620, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_05.blp', '', 1, 9, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30621;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30621, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_06.blp', '', 1, 9, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30622;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30622, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_07.blp', '', 1, 9, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30623;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30623, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_08.blp', '', 1, 9, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30624;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30624, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_09.blp', '', 1, 9, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30625;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30625, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_10.blp', '', 1, 9, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30626;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30626, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_11.blp', '', 1, 9, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30627;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30627, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_12.blp', '', 1, 9, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30628;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30628, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_13.blp', '', 1, 9, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30629;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30629, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_14.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_14.blp', '', 5, 9, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30630;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30630, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_15.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_15.blp', '', 5, 9, 15
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30631;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30631, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_16.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_16.blp', '', 5, 9, 16
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30632;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30632, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_00.blp', '', 5, 10, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30633;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30633, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_01.blp', '', 5, 10, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30634;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30634, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_02.blp', '', 5, 10, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30635;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30635, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_03.blp', '', 5, 10, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30636;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30636, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_04.blp', '', 5, 10, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30637;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30637, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_05.blp', '', 5, 10, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30638;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30638, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_06.blp', '', 5, 10, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30639;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30639, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_07.blp', '', 5, 10, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30640;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30640, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_08.blp', '', 5, 10, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30641;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30641, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_09.blp', '', 5, 10, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30642;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30642, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_10.blp', '', 5, 10, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30643;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30643, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_11.blp', '', 5, 10, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30644;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30644, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_12.blp', '', 5, 10, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30645;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30645, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower00_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper00_13.blp', '', 5, 10, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30646;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30646, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_00.blp', '', 5, 11, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30647;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30647, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_01.blp', '', 5, 11, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30648;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30648, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_02.blp', '', 5, 11, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30649;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30649, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_03.blp', '', 5, 11, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30650;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30650, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_04.blp', '', 5, 11, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30651;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30651, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_05.blp', '', 5, 11, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30652;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30652, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_06.blp', '', 5, 11, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30653;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30653, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_07.blp', '', 5, 11, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30654;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30654, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_08.blp', '', 5, 11, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30655;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30655, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_09.blp', '', 5, 11, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30656;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30656, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_10.blp', '', 5, 11, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30657;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30657, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_11.blp', '', 5, 11, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30658;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30658, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_12.blp', '', 5, 11, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30659;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30659, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower01_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper01_13.blp', '', 5, 11, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30660;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30660, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_00.blp', '', 5, 12, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30661;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30661, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_01.blp', '', 5, 12, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30662;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30662, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_02.blp', '', 5, 12, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30663;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30663, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_03.blp', '', 5, 12, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30664;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30664, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_04.blp', '', 5, 12, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30665;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30665, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_05.blp', '', 5, 12, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30666;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30666, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_06.blp', '', 5, 12, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30667;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30667, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_07.blp', '', 5, 12, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30668;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30668, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_08.blp', '', 5, 12, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30669;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30669, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_09.blp', '', 5, 12, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30670;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30670, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_10.blp', '', 5, 12, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30671;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30671, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_11.blp', '', 5, 12, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30672;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30672, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_12.blp', '', 5, 12, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30673;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30673, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower02_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper02_13.blp', '', 5, 12, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30674;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30674, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_00.blp', '', 5, 13, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30675;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30675, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_01.blp', '', 5, 13, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30676;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30676, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_02.blp', '', 5, 13, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30677;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30677, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_03.blp', '', 5, 13, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30678;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30678, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_04.blp', '', 5, 13, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30679;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30679, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_05.blp', '', 5, 13, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30680;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30680, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_06.blp', '', 5, 13, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30681;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30681, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_07.blp', '', 5, 13, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30682;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30682, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_08.blp', '', 5, 13, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30683;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30683, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_09.blp', '', 5, 13, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30684;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30684, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_10.blp', '', 5, 13, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30685;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30685, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_11.blp', '', 5, 13, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30686;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30686, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_12.blp', '', 5, 13, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30687;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30687, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower03_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper03_13.blp', '', 5, 13, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30688;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30688, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_00.blp', '', 5, 14, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30689;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30689, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_01.blp', '', 5, 14, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30690;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30690, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_02.blp', '', 5, 14, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30691;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30691, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_03.blp', '', 5, 14, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30692;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30692, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_04.blp', '', 5, 14, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30693;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30693, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_05.blp', '', 5, 14, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30694;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30694, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_06.blp', '', 5, 14, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30695;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30695, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_07.blp', '', 5, 14, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30696;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30696, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_08.blp', '', 5, 14, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30697;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30697, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_09.blp', '', 5, 14, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30698;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30698, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_10.blp', '', 5, 14, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30699;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30699, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_11.blp', '', 5, 14, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30700;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30700, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_12.blp', '', 5, 14, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30701;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30701, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower04_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper04_13.blp', '', 5, 14, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30702;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30702, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_00.blp', '', 5, 15, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30703;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30703, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_01.blp', '', 5, 15, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30704;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30704, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_02.blp', '', 5, 15, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30705;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30705, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_03.blp', '', 5, 15, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30706;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30706, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_04.blp', '', 5, 15, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30707;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30707, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_05.blp', '', 5, 15, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30708;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30708, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_06.blp', '', 5, 15, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30709;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30709, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_07.blp', '', 5, 15, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30710;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30710, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_08.blp', '', 5, 15, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30711;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30711, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_09.blp', '', 5, 15, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30712;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30712, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_10.blp', '', 5, 15, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30713;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30713, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_11.blp', '', 5, 15, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30714;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30714, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_12.blp', '', 5, 15, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30715;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30715, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower05_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper05_13.blp', '', 5, 15, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30716;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30716, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_00.blp', '', 5, 16, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30717;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30717, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_01.blp', '', 5, 16, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30718;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30718, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_02.blp', '', 5, 16, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30719;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30719, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_03.blp', '', 5, 16, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30720;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30720, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_04.blp', '', 5, 16, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30721;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30721, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_05.blp', '', 5, 16, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30722;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30722, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_06.blp', '', 5, 16, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30723;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30723, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_07.blp', '', 5, 16, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30724;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30724, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_08.blp', '', 5, 16, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30725;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30725, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_09.blp', '', 5, 16, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30726;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30726, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_10.blp', '', 5, 16, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30727;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30727, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_11.blp', '', 5, 16, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30728;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30728, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_12.blp', '', 5, 16, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30729;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30729, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower06_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper06_13.blp', '', 5, 16, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30730;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30730, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_00.blp', '', 5, 17, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30731;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30731, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_01.blp', '', 5, 17, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30732;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30732, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_02.blp', '', 5, 17, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30733;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30733, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_03.blp', '', 5, 17, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30734;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30734, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_04.blp', '', 5, 17, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30735;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30735, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_05.blp', '', 5, 17, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30736;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30736, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_06.blp', '', 5, 17, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30737;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30737, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_07.blp', '', 5, 17, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30738;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30738, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_08.blp', '', 5, 17, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30739;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30739, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_09.blp', '', 5, 17, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30740;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30740, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_10.blp', '', 5, 17, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30741;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30741, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_11.blp', '', 5, 17, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30742;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30742, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_12.blp', '', 5, 17, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30743;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30743, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower07_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper07_13.blp', '', 5, 17, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30744;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30744, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_00.blp', '', 5, 18, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30745;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30745, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_01.blp', '', 5, 18, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30746;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30746, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_02.blp', '', 5, 18, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30747;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30747, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_03.blp', '', 5, 18, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30748;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30748, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_04.blp', '', 5, 18, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30749;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30749, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_05.blp', '', 5, 18, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30750;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30750, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_06.blp', '', 5, 18, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30751;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30751, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_07.blp', '', 5, 18, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30752;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30752, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_08.blp', '', 5, 18, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30753;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30753, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_09.blp', '', 5, 18, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30754;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30754, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_10.blp', '', 5, 18, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30755;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30755, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_11.blp', '', 5, 18, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30756;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30756, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_12.blp', '', 5, 18, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30757;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30757, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower08_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper08_13.blp', '', 5, 18, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30758;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30758, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_00.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_00.blp', '', 5, 19, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30759;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30759, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_01.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_01.blp', '', 5, 19, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30760;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30760, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_02.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_02.blp', '', 5, 19, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30761;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30761, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_03.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_03.blp', '', 5, 19, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30762;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30762, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_04.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_04.blp', '', 5, 19, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30763;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30763, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_05.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_05.blp', '', 5, 19, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30764;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30764, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_06.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_06.blp', '', 5, 19, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30765;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30765, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_07.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_07.blp', '', 5, 19, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30766;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30766, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_08.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_08.blp', '', 5, 19, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30767;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30767, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_09.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_09.blp', '', 5, 19, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30768;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30768, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_10.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_10.blp', '', 5, 19, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30769;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30769, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_11.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_11.blp', '', 5, 19, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30770;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30770, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_12.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_12.blp', '', 5, 19, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30771;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30771, 14, 0, 1, 'Character\\EsteriaBroken\\Male\\BrokenMaleFaceLower09_13.blp',
    'Character\\EsteriaBroken\\Male\\BrokenMaleFaceUpper09_13.blp', '', 5, 19, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30772;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30772, 14, 0, 2, '', '', '', 17, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30773;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30773, 14, 0, 2, '', '', '', 17, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30774;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30774, 14, 0, 2, '', '', '', 17, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30775;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30775, 14, 0, 2, '', '', '', 17, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30776;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30776, 14, 0, 2, '', '', '', 17, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30777;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30777, 14, 0, 2, '', '', '', 17, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30778;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30778, 14, 0, 2, '', '', '', 17, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30779;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30779, 14, 0, 2, '', '', '', 17, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30780;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30780, 14, 0, 2, '', '', '', 17, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30781;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30781, 14, 0, 2, '', '', '', 17, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30782;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30782, 14, 0, 2, '', '', '', 17, 1, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30783;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30783, 14, 0, 2, '', '', '', 17, 1, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30784;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30784, 14, 0, 2, '', '', '', 17, 1, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30785;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30785, 14, 0, 2, '', '', '', 17, 1, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30786;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30786, 14, 0, 2, '', '', '', 17, 1, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30787;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30787, 14, 0, 2, '', '', '', 17, 1, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30788;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30788, 14, 0, 2, '', '', '', 17, 1, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30789;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30789, 14, 0, 2, '', '', '', 17, 1, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30790;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30790, 14, 0, 2, '', '', '', 17, 1, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30791;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30791, 14, 0, 2, '', '', '', 17, 1, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30792;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30792, 14, 0, 2, '', '', '', 17, 2, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30793;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30793, 14, 0, 2, '', '', '', 17, 2, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30794;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30794, 14, 0, 2, '', '', '', 17, 2, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30795;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30795, 14, 0, 2, '', '', '', 17, 2, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30796;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30796, 14, 0, 2, '', '', '', 17, 2, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30797;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30797, 14, 0, 2, '', '', '', 17, 2, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30798;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30798, 14, 0, 2, '', '', '', 17, 2, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30799;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30799, 14, 0, 2, '', '', '', 17, 2, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30800;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30800, 14, 0, 2, '', '', '', 17, 2, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30801;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30801, 14, 0, 2, '', '', '', 17, 2, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30802;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30802, 14, 0, 2, '', '', '', 17, 3, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30803;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30803, 14, 0, 2, '', '', '', 17, 3, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30804;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30804, 14, 0, 2, '', '', '', 17, 3, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30805;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30805, 14, 0, 2, '', '', '', 17, 3, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30806;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30806, 14, 0, 2, '', '', '', 17, 3, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30807;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30807, 14, 0, 2, '', '', '', 17, 3, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30808;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30808, 14, 0, 2, '', '', '', 17, 3, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30809;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30809, 14, 0, 2, '', '', '', 17, 3, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30810;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30810, 14, 0, 2, '', '', '', 17, 3, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30811;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30811, 14, 0, 2, '', '', '', 17, 3, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30812;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30812, 14, 0, 2, '', '', '', 17, 4, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30813;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30813, 14, 0, 2, '', '', '', 17, 4, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30814;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30814, 14, 0, 2, '', '', '', 17, 4, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30815;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30815, 14, 0, 2, '', '', '', 17, 4, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30816;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30816, 14, 0, 2, '', '', '', 17, 4, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30817;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30817, 14, 0, 2, '', '', '', 17, 4, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30818;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30818, 14, 0, 2, '', '', '', 17, 4, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30819;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30819, 14, 0, 2, '', '', '', 17, 4, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30820;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30820, 14, 0, 2, '', '', '', 17, 4, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30821;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30821, 14, 0, 2, '', '', '', 17, 4, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30822;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30822, 14, 0, 2, '', '', '', 17, 5, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30823;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30823, 14, 0, 2, '', '', '', 17, 5, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30824;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30824, 14, 0, 2, '', '', '', 17, 5, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30825;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30825, 14, 0, 2, '', '', '', 17, 5, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30826;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30826, 14, 0, 2, '', '', '', 17, 5, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30827;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30827, 14, 0, 2, '', '', '', 17, 5, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30828;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30828, 14, 0, 2, '', '', '', 17, 5, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30829;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30829, 14, 0, 2, '', '', '', 17, 5, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30830;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30830, 14, 0, 2, '', '', '', 17, 5, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30831;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30831, 14, 0, 2, '', '', '', 17, 5, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30832;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30832, 14, 0, 2, '', '', '', 17, 6, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30833;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30833, 14, 0, 2, '', '', '', 17, 6, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30834;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30834, 14, 0, 2, '', '', '', 17, 6, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30835;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30835, 14, 0, 2, '', '', '', 17, 6, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30836;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30836, 14, 0, 2, '', '', '', 17, 6, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30837;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30837, 14, 0, 2, '', '', '', 17, 6, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30838;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30838, 14, 0, 2, '', '', '', 17, 6, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30839;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30839, 14, 0, 2, '', '', '', 17, 6, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30840;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30840, 14, 0, 2, '', '', '', 17, 6, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30841;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30841, 14, 0, 2, '', '', '', 17, 6, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30842;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30842, 14, 0, 2, '', '', '', 17, 7, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30843;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30843, 14, 0, 2, '', '', '', 17, 7, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30844;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30844, 14, 0, 2, '', '', '', 17, 7, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30845;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30845, 14, 0, 2, '', '', '', 17, 7, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30846;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30846, 14, 0, 2, '', '', '', 17, 7, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30847;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30847, 14, 0, 2, '', '', '', 17, 7, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30848;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30848, 14, 0, 2, '', '', '', 17, 7, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30849;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30849, 14, 0, 2, '', '', '', 17, 7, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30850;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30850, 14, 0, 2, '', '', '', 17, 7, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30851;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30851, 14, 0, 2, '', '', '', 17, 7, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30852;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30852, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30853;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30853, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30854;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30854, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30855;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30855, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30856;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30856, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30857;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30857, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30858;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30858, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30859;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30859, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30860;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30860, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30861;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30861, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30862;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30862, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 1, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30863;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30863, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 1, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30864;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30864, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 1, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30865;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30865, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 1, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30866;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30866, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 1, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30867;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30867, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 1, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30868;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30868, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 1, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30869;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30869, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 1, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30870;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30870, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 1, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30871;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30871, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 1, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30872;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30872, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 2, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30873;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30873, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 2, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30874;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30874, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 2, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30875;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30875, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 2, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30876;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30876, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 2, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30877;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30877, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 2, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30878;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30878, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 2, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30879;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30879, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 2, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30880;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30880, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 2, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30881;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30881, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 2, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30882;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30882, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 3, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30883;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30883, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 3, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30884;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30884, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 3, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30885;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30885, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 3, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30886;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30886, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 3, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30887;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30887, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 3, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30888;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30888, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 3, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30889;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30889, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 3, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30890;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30890, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 3, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30891;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30891, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 3, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30892;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30892, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 4, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30893;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30893, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 4, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30894;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30894, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 4, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30895;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30895, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 4, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30896;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30896, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 4, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30897;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30897, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 4, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30898;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30898, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 4, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30899;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30899, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 4, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30900;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30900, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 4, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30901;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30901, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 4, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30902;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30902, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 5, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30903;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30903, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 5, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30904;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30904, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 5, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30905;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30905, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 5, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30906;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30906, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 5, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30907;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30907, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 5, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30908;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30908, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 5, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30909;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30909, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 5, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30910;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30910, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 5, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30911;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30911, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 5, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30912;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30912, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 6, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30913;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30913, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 6, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30914;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30914, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 6, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30915;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30915, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 6, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30916;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30916, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 6, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30917;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30917, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 6, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30918;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30918, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 6, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30919;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30919, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 6, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30920;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30920, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 6, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30921;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30921, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 6, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30922;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30922, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 7, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30923;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30923, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 7, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30924;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30924, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 7, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30925;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30925, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 7, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30926;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30926, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 7, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30927;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30927, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 7, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30928;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30928, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 7, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30929;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30929, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 7, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30930;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30930, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 7, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30931;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30931, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 7, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30932;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30932, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 8, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30933;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30933, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 8, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30934;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30934, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 8, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30935;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30935, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 8, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30936;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30936, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 8, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30937;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30937, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 8, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30938;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30938, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 8, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30939;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30939, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 8, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30940;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30940, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 8, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30941;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30941, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 8, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30942;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30942, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 9, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30943;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30943, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 9, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30944;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30944, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 9, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30945;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30945, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 9, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30946;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30946, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 9, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30947;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30947, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 9, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30948;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30948, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 9, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30949;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30949, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 9, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30950;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30950, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 9, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30951;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30951, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 9, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30952;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30952, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 10, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30953;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30953, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 10, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30954;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30954, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 10, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30955;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30955, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 10, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30956;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30956, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 10, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30957;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30957, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 10, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30958;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30958, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 10, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30959;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30959, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 10, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30960;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30960, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 10, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30961;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30961, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 10, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30962;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30962, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 11, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30963;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30963, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 11, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30964;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30964, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 11, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30965;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30965, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 11, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30966;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30966, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 11, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30967;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30967, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 11, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30968;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30968, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 11, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30969;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30969, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 11, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30970;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30970, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 11, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30971;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30971, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 11, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30972;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30972, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 12, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30973;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30973, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 12, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30974;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30974, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 12, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30975;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30975, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 12, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30976;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30976, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 12, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30977;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30977, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 12, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30978;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30978, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 12, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30979;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30979, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 12, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30980;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30980, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 12, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30981;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30981, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 12, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30982;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30982, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 13, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30983;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30983, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 13, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30984;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30984, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 13, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30985;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30985, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 13, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30986;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30986, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 13, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30987;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30987, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 13, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30988;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30988, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 13, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30989;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30989, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 13, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30990;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30990, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 13, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30991;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30991, 14, 0, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 13, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30992;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30992, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_00.blp', '', '', 17, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30993;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30993, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_01.blp', '', '', 17, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30994;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30994, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_02.blp', '', '', 17, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30995;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30995, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_03.blp', '', '', 17, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30996;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30996, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_04.blp', '', '', 17, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30997;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30997, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_05.blp', '', '', 17, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30998;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30998, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_06.blp', '', '', 17, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 30999;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    30999, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_07.blp', '', '', 17, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31000;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31000, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_08.blp', '', '', 17, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31001;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31001, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_09.blp', '', '', 17, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31002;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31002, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_10.blp', '', '', 17, 0, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31003;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31003, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_11.blp', '', '', 17, 0, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31004;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31004, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_12.blp', '', '', 17, 0, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31005;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31005, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_13.blp', '', '', 17, 0, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31006;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31006, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_14.blp', '', '', 5, 0, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31007;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31007, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_15.blp', '', '', 5, 0, 15
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31008;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31008, 14, 0, 4, 'Character\\EsteriaBroken\\Male\\BrokenMaleNakedPelvisSkin00_16.blp', '', '', 5, 0, 16
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31009;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31009, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_00_Extra.blp', '', 17, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31010;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31010, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_01_Extra.blp', '', 17, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31011;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31011, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_02_Extra.blp', '', 17, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31012;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31012, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_03_Extra.blp', '', 17, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31013;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31013, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_04_Extra.blp', '', 17, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31014;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31014, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_05_Extra.blp', '', 17, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31015;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31015, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_06_Extra.blp', '', 17, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31016;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31016, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_07_Extra.blp', '', 17, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31017;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31017, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_08_Extra.blp', '', 17, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31018;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31018, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_09_Extra.blp', '', 17, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31019;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31019, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_10_Extra.blp', '', 17, 0, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31020;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31020, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_11_Extra.blp', '', 17, 0, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31021;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31021, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_12.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_12_Extra.blp', '', 5, 0, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31022;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31022, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_13.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_13_Extra.blp', '', 5, 0, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31023;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31023, 14, 1, 0, 'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_14.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleSkin00_14_Extra.blp', '', 5, 0, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31024;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31024, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_00.blp', '', 1, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31025;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31025, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_01.blp', '', 1, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31026;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31026, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_02.blp', '', 1, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31027;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31027, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_03.blp', '', 1, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31028;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31028, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_04.blp', '', 1, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31029;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31029, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_05.blp', '', 1, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31030;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31030, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_06.blp', '', 1, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31031;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31031, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_07.blp', '', 1, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31032;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31032, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_08.blp', '', 1, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31033;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31033, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_09.blp', '', 1, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31034;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31034, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_10.blp', '', 1, 0, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31035;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31035, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_11.blp', '', 1, 0, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31036;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31036, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_12.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_12.blp', '', 5, 0, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31037;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31037, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_13.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_13.blp', '', 5, 0, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31038;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31038, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower00_14.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper00_14.blp', '', 5, 0, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31039;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31039, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_00.blp', '', 1, 1, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31040;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31040, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_01.blp', '', 1, 1, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31041;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31041, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_02.blp', '', 1, 1, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31042;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31042, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_03.blp', '', 1, 1, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31043;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31043, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_04.blp', '', 1, 1, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31044;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31044, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_05.blp', '', 1, 1, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31045;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31045, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_06.blp', '', 1, 1, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31046;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31046, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_07.blp', '', 1, 1, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31047;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31047, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_08.blp', '', 1, 1, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31048;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31048, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_09.blp', '', 1, 1, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31049;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31049, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_10.blp', '', 1, 1, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31050;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31050, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower01_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper01_11.blp', '', 1, 1, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31051;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31051, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_00.blp', '', 1, 2, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31052;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31052, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_01.blp', '', 1, 2, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31053;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31053, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_02.blp', '', 1, 2, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31054;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31054, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_03.blp', '', 1, 2, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31055;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31055, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_04.blp', '', 1, 2, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31056;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31056, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_05.blp', '', 1, 2, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31057;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31057, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_06.blp', '', 1, 2, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31058;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31058, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_07.blp', '', 1, 2, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31059;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31059, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_08.blp', '', 1, 2, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31060;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31060, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_09.blp', '', 1, 2, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31061;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31061, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_10.blp', '', 1, 2, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31062;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31062, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower02_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper02_11.blp', '', 1, 2, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31063;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31063, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_00.blp', '', 1, 3, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31064;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31064, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_01.blp', '', 1, 3, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31065;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31065, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_02.blp', '', 1, 3, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31066;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31066, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_03.blp', '', 1, 3, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31067;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31067, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_04.blp', '', 1, 3, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31068;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31068, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_05.blp', '', 1, 3, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31069;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31069, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_06.blp', '', 1, 3, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31070;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31070, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_07.blp', '', 1, 3, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31071;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31071, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_08.blp', '', 1, 3, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31072;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31072, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_09.blp', '', 1, 3, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31073;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31073, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_10.blp', '', 1, 3, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31074;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31074, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower03_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper03_11.blp', '', 1, 3, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31075;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31075, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_00.blp', '', 1, 4, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31076;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31076, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_01.blp', '', 1, 4, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31077;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31077, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_02.blp', '', 1, 4, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31078;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31078, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_03.blp', '', 1, 4, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31079;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31079, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_04.blp', '', 1, 4, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31080;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31080, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_05.blp', '', 1, 4, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31081;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31081, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_06.blp', '', 1, 4, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31082;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31082, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_07.blp', '', 1, 4, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31083;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31083, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_08.blp', '', 1, 4, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31084;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31084, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_09.blp', '', 1, 4, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31085;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31085, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_10.blp', '', 1, 4, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31086;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31086, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_11.blp', '', 1, 4, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31087;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31087, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_12.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_12.blp', '', 5, 4, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31088;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31088, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_13.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_13.blp', '', 5, 4, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31089;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31089, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower04_14.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper04_14.blp', '', 5, 4, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31090;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31090, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_00.blp', '', 1, 5, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31091;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31091, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_01.blp', '', 1, 5, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31092;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31092, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_02.blp', '', 1, 5, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31093;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31093, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_03.blp', '', 1, 5, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31094;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31094, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_04.blp', '', 1, 5, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31095;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31095, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_05.blp', '', 1, 5, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31096;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31096, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_06.blp', '', 1, 5, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31097;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31097, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_07.blp', '', 1, 5, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31098;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31098, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_08.blp', '', 1, 5, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31099;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31099, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_09.blp', '', 1, 5, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31100;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31100, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_10.blp', '', 1, 5, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31101;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31101, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower05_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper05_11.blp', '', 1, 5, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31102;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31102, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_00.blp', '', 1, 6, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31103;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31103, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_01.blp', '', 1, 6, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31104;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31104, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_02.blp', '', 1, 6, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31105;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31105, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_03.blp', '', 1, 6, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31106;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31106, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_04.blp', '', 1, 6, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31107;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31107, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_05.blp', '', 1, 6, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31108;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31108, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_06.blp', '', 1, 6, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31109;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31109, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_07.blp', '', 1, 6, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31110;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31110, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_08.blp', '', 1, 6, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31111;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31111, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_09.blp', '', 1, 6, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31112;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31112, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_10.blp', '', 1, 6, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31113;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31113, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower06_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper06_11.blp', '', 1, 6, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31114;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31114, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_00.blp', '', 1, 7, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31115;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31115, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_01.blp', '', 1, 7, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31116;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31116, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_02.blp', '', 1, 7, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31117;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31117, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_03.blp', '', 1, 7, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31118;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31118, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_04.blp', '', 1, 7, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31119;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31119, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_05.blp', '', 1, 7, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31120;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31120, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_06.blp', '', 1, 7, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31121;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31121, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_07.blp', '', 1, 7, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31122;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31122, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_08.blp', '', 1, 7, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31123;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31123, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_09.blp', '', 1, 7, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31124;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31124, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_10.blp', '', 1, 7, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31125;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31125, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower07_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper07_11.blp', '', 1, 7, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31126;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31126, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_00.blp', '', 1, 8, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31127;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31127, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_01.blp', '', 1, 8, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31128;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31128, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_02.blp', '', 1, 8, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31129;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31129, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_03.blp', '', 1, 8, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31130;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31130, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_04.blp', '', 1, 8, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31131;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31131, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_05.blp', '', 1, 8, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31132;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31132, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_06.blp', '', 1, 8, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31133;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31133, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_07.blp', '', 1, 8, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31134;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31134, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_08.blp', '', 1, 8, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31135;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31135, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_09.blp', '', 1, 8, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31136;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31136, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_10.blp', '', 1, 8, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31137;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31137, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_11.blp', '', 1, 8, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31138;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31138, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_12.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_12.blp', '', 5, 8, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31139;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31139, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_13.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_13.blp', '', 5, 8, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31140;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31140, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower08_14.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper08_14.blp', '', 5, 8, 14
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31141;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31141, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_00.blp', '', 1, 9, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31142;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31142, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_01.blp', '', 1, 9, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31143;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31143, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_02.blp', '', 1, 9, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31144;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31144, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_03.blp', '', 1, 9, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31145;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31145, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_04.blp', '', 1, 9, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31146;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31146, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_05.blp', '', 1, 9, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31147;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31147, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_06.blp', '', 1, 9, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31148;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31148, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_07.blp', '', 1, 9, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31149;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31149, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_08.blp', '', 1, 9, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31150;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31150, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_09.blp', '', 1, 9, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31151;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31151, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_10.blp', '', 1, 9, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31152;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31152, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower09_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper09_11.blp', '', 1, 9, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31153;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31153, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_00.blp', '', 5, 10, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31154;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31154, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_01.blp', '', 5, 10, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31155;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31155, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_02.blp', '', 5, 10, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31156;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31156, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_03.blp', '', 5, 10, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31157;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31157, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_04.blp', '', 5, 10, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31158;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31158, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_05.blp', '', 5, 10, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31159;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31159, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_06.blp', '', 5, 10, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31160;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31160, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_07.blp', '', 5, 10, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31161;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31161, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_08.blp', '', 5, 10, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31162;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31162, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_09.blp', '', 5, 10, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31163;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31163, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_10.blp', '', 5, 10, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31164;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31164, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower10_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper10_11.blp', '', 5, 10, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31165;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31165, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_00.blp', '', 5, 11, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31166;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31166, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_01.blp', '', 5, 11, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31167;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31167, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_02.blp', '', 5, 11, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31168;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31168, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_03.blp', '', 5, 11, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31169;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31169, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_04.blp', '', 5, 11, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31170;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31170, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_05.blp', '', 5, 11, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31171;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31171, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_06.blp', '', 5, 11, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31172;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31172, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_07.blp', '', 5, 11, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31173;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31173, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_08.blp', '', 5, 11, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31174;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31174, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_09.blp', '', 5, 11, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31175;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31175, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_10.blp', '', 5, 11, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31176;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31176, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower11_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper11_11.blp', '', 5, 11, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31177;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31177, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_00.blp', '', 5, 12, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31178;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31178, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_01.blp', '', 5, 12, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31179;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31179, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_02.blp', '', 5, 12, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31180;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31180, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_03.blp', '', 5, 12, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31181;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31181, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_04.blp', '', 5, 12, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31182;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31182, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_05.blp', '', 5, 12, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31183;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31183, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_06.blp', '', 5, 12, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31184;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31184, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_07.blp', '', 5, 12, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31185;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31185, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_08.blp', '', 5, 12, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31186;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31186, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_09.blp', '', 5, 12, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31187;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31187, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_10.blp', '', 5, 12, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31188;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31188, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower12_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper12_11.blp', '', 5, 12, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31189;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31189, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_00.blp', '', 5, 13, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31190;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31190, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_01.blp', '', 5, 13, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31191;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31191, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_02.blp', '', 5, 13, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31192;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31192, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_03.blp', '', 5, 13, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31193;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31193, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_04.blp', '', 5, 13, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31194;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31194, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_05.blp', '', 5, 13, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31195;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31195, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_06.blp', '', 5, 13, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31196;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31196, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_07.blp', '', 5, 13, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31197;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31197, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_08.blp', '', 5, 13, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31198;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31198, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_09.blp', '', 5, 13, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31199;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31199, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_10.blp', '', 5, 13, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31200;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31200, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower13_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper13_11.blp', '', 5, 13, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31201;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31201, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_00.blp', '', 5, 14, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31202;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31202, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_01.blp', '', 5, 14, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31203;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31203, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_02.blp', '', 5, 14, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31204;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31204, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_03.blp', '', 5, 14, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31205;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31205, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_04.blp', '', 5, 14, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31206;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31206, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_05.blp', '', 5, 14, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31207;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31207, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_06.blp', '', 5, 14, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31208;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31208, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_07.blp', '', 5, 14, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31209;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31209, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_08.blp', '', 5, 14, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31210;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31210, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_09.blp', '', 5, 14, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31211;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31211, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_10.blp', '', 5, 14, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31212;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31212, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower14_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper14_11.blp', '', 5, 14, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31213;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31213, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_00.blp', '', 5, 15, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31214;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31214, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_01.blp', '', 5, 15, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31215;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31215, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_02.blp', '', 5, 15, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31216;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31216, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_03.blp', '', 5, 15, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31217;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31217, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_04.blp', '', 5, 15, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31218;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31218, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_05.blp', '', 5, 15, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31219;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31219, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_06.blp', '', 5, 15, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31220;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31220, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_07.blp', '', 5, 15, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31221;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31221, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_08.blp', '', 5, 15, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31222;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31222, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_09.blp', '', 5, 15, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31223;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31223, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_10.blp', '', 5, 15, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31224;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31224, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower15_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper15_11.blp', '', 5, 15, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31225;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31225, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_00.blp', '', 5, 16, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31226;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31226, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_01.blp', '', 5, 16, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31227;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31227, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_02.blp', '', 5, 16, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31228;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31228, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_03.blp', '', 5, 16, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31229;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31229, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_04.blp', '', 5, 16, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31230;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31230, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_05.blp', '', 5, 16, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31231;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31231, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_06.blp', '', 5, 16, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31232;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31232, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_07.blp', '', 5, 16, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31233;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31233, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_08.blp', '', 5, 16, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31234;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31234, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_09.blp', '', 5, 16, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31235;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31235, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_10.blp', '', 5, 16, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31236;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31236, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower16_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper16_11.blp', '', 5, 16, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31237;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31237, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_00.blp', '', 5, 17, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31238;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31238, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_01.blp', '', 5, 17, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31239;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31239, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_02.blp', '', 5, 17, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31240;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31240, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_03.blp', '', 5, 17, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31241;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31241, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_04.blp', '', 5, 17, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31242;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31242, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_05.blp', '', 5, 17, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31243;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31243, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_06.blp', '', 5, 17, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31244;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31244, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_07.blp', '', 5, 17, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31245;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31245, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_08.blp', '', 5, 17, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31246;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31246, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_09.blp', '', 5, 17, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31247;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31247, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_10.blp', '', 5, 17, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31248;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31248, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower17_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper17_11.blp', '', 5, 17, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31249;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31249, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_00.blp', '', 5, 18, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31250;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31250, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_01.blp', '', 5, 18, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31251;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31251, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_02.blp', '', 5, 18, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31252;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31252, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_03.blp', '', 5, 18, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31253;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31253, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_04.blp', '', 5, 18, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31254;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31254, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_05.blp', '', 5, 18, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31255;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31255, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_06.blp', '', 5, 18, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31256;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31256, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_07.blp', '', 5, 18, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31257;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31257, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_08.blp', '', 5, 18, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31258;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31258, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_09.blp', '', 5, 18, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31259;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31259, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_10.blp', '', 5, 18, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31260;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31260, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower18_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper18_11.blp', '', 5, 18, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31261;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31261, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_00.blp', '', 5, 19, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31262;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31262, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_01.blp', '', 5, 19, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31263;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31263, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_02.blp', '', 5, 19, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31264;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31264, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_03.blp', '', 5, 19, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31265;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31265, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_04.blp', '', 5, 19, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31266;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31266, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_05.blp', '', 5, 19, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31267;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31267, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_06.blp', '', 5, 19, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31268;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31268, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_07.blp', '', 5, 19, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31269;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31269, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_08.blp', '', 5, 19, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31270;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31270, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_09.blp', '', 5, 19, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31271;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31271, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_10.blp', '', 5, 19, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31272;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31272, 14, 1, 1, 'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceLower19_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleFaceUpper19_11.blp', '', 5, 19, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31273;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31273, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31274;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31274, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31275;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31275, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31276;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31276, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31277;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31277, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31278;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31278, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31279;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31279, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31280;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31280, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31281;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31281, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31282;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31282, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31283;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31283, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 1, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31284;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31284, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 1, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31285;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31285, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 1, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31286;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31286, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 1, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31287;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31287, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 1, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31288;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31288, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 1, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31289;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31289, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 1, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31290;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31290, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 1, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31291;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31291, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 1, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31292;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31292, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 1, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31293;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31293, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 2, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31294;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31294, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 2, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31295;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31295, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 2, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31296;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31296, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 2, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31297;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31297, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 2, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31298;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31298, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 2, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31299;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31299, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 2, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31300;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31300, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 2, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31301;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31301, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 2, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31302;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31302, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 2, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31303;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31303, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 3, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31304;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31304, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 3, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31305;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31305, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 3, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31306;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31306, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 3, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31307;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31307, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 3, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31308;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31308, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 3, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31309;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31309, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 3, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31310;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31310, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 3, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31311;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31311, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 3, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31312;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31312, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 3, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31313;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31313, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 4, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31314;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31314, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 4, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31315;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31315, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 4, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31316;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31316, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 4, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31317;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31317, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 4, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31318;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31318, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 4, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31319;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31319, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 4, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31320;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31320, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 4, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31321;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31321, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 4, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31322;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31322, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 4, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31323;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31323, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 5, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31324;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31324, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 5, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31325;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31325, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 5, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31326;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31326, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 5, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31327;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31327, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 5, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31328;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31328, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 5, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31329;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31329, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 5, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31330;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31330, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 5, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31331;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31331, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 5, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31332;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31332, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 5, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31333;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31333, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 6, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31334;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31334, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 6, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31335;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31335, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 6, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31336;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31336, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 6, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31337;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31337, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 6, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31338;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31338, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 6, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31339;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31339, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 6, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31340;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31340, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 6, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31341;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31341, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 6, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31342;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31342, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 6, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31343;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31343, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 7, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31344;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31344, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 7, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31345;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31345, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 7, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31346;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31346, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 7, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31347;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31347, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 7, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31348;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31348, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 7, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31349;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31349, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 7, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31350;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31350, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 7, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31351;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31351, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 7, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31352;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31352, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 7, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31353;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31353, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 8, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31354;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31354, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 8, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31355;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31355, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 8, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31356;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31356, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 8, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31357;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31357, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 8, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31358;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31358, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 8, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31359;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31359, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 8, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31360;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31360, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 8, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31361;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31361, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 8, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31362;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31362, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 8, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31363;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31363, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 9, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31364;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31364, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 9, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31365;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31365, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 9, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31366;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31366, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 9, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31367;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31367, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 9, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31368;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31368, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 9, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31369;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31369, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 9, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31370;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31370, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 9, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31371;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31371, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 9, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31372;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31372, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 9, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31373;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31373, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 17, 10, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31374;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31374, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 17, 10, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31375;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31375, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 17, 10, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31376;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31376, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 17, 10, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31377;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31377, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 17, 10, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31378;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31378, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 17, 10, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31379;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31379, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 17, 10, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31380;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31380, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 17, 10, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31381;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31381, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 17, 10, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31382;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31382, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 17, 10, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31383;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31383, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 11, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31384;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31384, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 11, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31385;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31385, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 11, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31386;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31386, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 11, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31387;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31387, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 11, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31388;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31388, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 11, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31389;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31389, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 11, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31390;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31390, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 11, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31391;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31391, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 11, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31392;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31392, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 11, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31393;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31393, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 12, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31394;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31394, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 12, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31395;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31395, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 12, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31396;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31396, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 12, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31397;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31397, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 12, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31398;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31398, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 12, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31399;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31399, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 12, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31400;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31400, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 12, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31401;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31401, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 12, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31402;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31402, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 12, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31403;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31403, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 13, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31404;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31404, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 13, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31405;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31405, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 13, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31406;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31406, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 13, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31407;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31407, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 13, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31408;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31408, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 13, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31409;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31409, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 13, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31410;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31410, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 13, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31411;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31411, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 13, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31412;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31412, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 13, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31413;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31413, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 14, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31414;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31414, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 14, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31415;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31415, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 14, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31416;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31416, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 14, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31417;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31417, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 14, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31418;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31418, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 14, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31419;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31419, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 14, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31420;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31420, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 14, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31421;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31421, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 14, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31422;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31422, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 14, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31423;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31423, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_00.blp', '', '', 18, 15, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31424;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31424, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_01.blp', '', '', 18, 15, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31425;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31425, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_02.blp', '', '', 18, 15, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31426;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31426, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_03.blp', '', '', 18, 15, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31427;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31427, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_04.blp', '', '', 18, 15, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31428;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31428, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_05.blp', '', '', 18, 15, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31429;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31429, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_06.blp', '', '', 18, 15, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31430;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31430, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_07.blp', '', '', 18, 15, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31431;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31431, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_08.blp', '', '', 18, 15, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31432;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31432, 14, 1, 3, 'Character\\EsteriaBroken\\Hair00_09.blp', '', '', 18, 15, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31433;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31433, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_00.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_00.blp', '', 17, 0, 0
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31434;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31434, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_01.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_01.blp', '', 17, 0, 1
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31435;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31435, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_02.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_02.blp', '', 17, 0, 2
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31436;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31436, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_03.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_03.blp', '', 17, 0, 3
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31437;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31437, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_04.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_04.blp', '', 17, 0, 4
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31438;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31438, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_05.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_05.blp', '', 17, 0, 5
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31439;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31439, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_06.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_06.blp', '', 17, 0, 6
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31440;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31440, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_07.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_07.blp', '', 17, 0, 7
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31441;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31441, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_08.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_08.blp', '', 17, 0, 8
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31442;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31442, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_09.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_09.blp', '', 17, 0, 9
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31443;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31443, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_10.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_10.blp', '', 17, 0, 10
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31444;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31444, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_11.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_11.blp', '', 17, 0, 11
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31445;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31445, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_12.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_12.blp', '', 5, 0, 12
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31446;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31446, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_13.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_13.blp', '', 5, 0, 13
);

DELETE FROM `charsections_dbc` WHERE `ID` = 31447;
INSERT INTO `charsections_dbc` (
    `Id`, `Race`, `Gender`, `GenType`, `TexturePath1`, `TexturePath2`, `TexturePath3`, `Flags`, `Type`, `Color`
) VALUES (
    31447, 14, 1, 4, 'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedPelvisSkin00_14.blp',
    'Character\\EsteriaBroken\\Female\\BrokenFemaleNakedTorsoSkin00_14.blp', '', 5, 0, 14
);

DELETE FROM `barbershopstyle_dbc` WHERE `Race` = 14;

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1356;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1356, 0, 'Broken 0 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1357;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1357, 0, 'Broken 0 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1358;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1358, 0, 'Broken 0 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1359;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1359, 0, 'Broken 0 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1360;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1360, 0, 'Broken 0 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1361;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1361, 0, 'Broken 0 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1362;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1362, 0, 'Broken 0 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1363;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1363, 0, 'Broken 0 7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 7
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1364;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1364, 0, 'Broken 0 8', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 8
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1365;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1365, 0, 'Broken 0 9', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 9
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1366;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1366, 1, 'Broken 1 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1367;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1367, 1, 'Broken 1 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1368;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1368, 1, 'Broken 1 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1369;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1369, 1, 'Broken 1 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1370;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1370, 1, 'Broken 1 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1371;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1371, 1, 'Broken 1 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1372;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1372, 1, 'Broken 1 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1373;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1373, 1, 'Broken 1 7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 7
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1374;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1374, 1, 'Broken 1 8', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 8
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1375;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1375, 1, 'Broken 1 9', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 9
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1376;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1376, 2, 'Broken 2 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1377;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1377, 2, 'Broken 2 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1378;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1378, 2, 'Broken 2 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1379;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1379, 2, 'Broken 2 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1380;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1380, 2, 'Broken 2 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1381;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1381, 2, 'Broken 2 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1382;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1382, 2, 'Broken 2 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1383;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1383, 2, 'Broken 2 7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 7
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1384;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1384, 3, 'Broken 3 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1385;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1385, 3, 'Broken 3 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1386;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1386, 3, 'Broken 3 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1387;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1387, 3, 'Broken 3 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1388;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1388, 3, 'Broken 3 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1389;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1389, 3, 'Broken 3 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1390;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1390, 3, 'Broken 3 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1391;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1391, 3, 'Broken 3 7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 7
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1392;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1392, 3, 'Broken 3 8', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 8
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1393;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1393, 3, 'Broken 3 9', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 9
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1394;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1394, 3, 'Broken 3 10', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 10
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1395;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1395, 3, 'Broken 3 11', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 11
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1396;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1396, 3, 'Broken 3 12', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 12
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1397;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1397, 3, 'Broken 3 13', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 13
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1398;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1398, 3, 'Broken 3 14', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 14
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1399;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1399, 3, 'Broken 3 15', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 15
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1400;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1400, 3, 'Broken 3 16', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 0, 16
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1401;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1401, 0, 'Broken 0 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1402;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1402, 0, 'Broken 0 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1403;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1403, 0, 'Broken 0 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1404;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1404, 0, 'Broken 0 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1405;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1405, 0, 'Broken 0 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1406;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1406, 0, 'Broken 0 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1407;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1407, 0, 'Broken 0 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1408;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1408, 0, 'Broken 0 7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 7
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1409;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1409, 0, 'Broken 0 8', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 8
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1410;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1410, 0, 'Broken 0 9', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 9
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1411;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1411, 0, 'Broken 0 10', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 10
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1412;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1412, 1, 'Broken 1 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1413;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1413, 1, 'Broken 1 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1414;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1414, 1, 'Broken 1 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1415;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1415, 1, 'Broken 1 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1416;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1416, 1, 'Broken 1 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1417;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1417, 1, 'Broken 1 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1418;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1418, 1, 'Broken 1 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1419;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1419, 1, 'Broken 1 7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 7
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1420;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1420, 1, 'Broken 1 8', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 8
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1421;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1421, 1, 'Broken 1 9', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 9
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1422;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1422, 2, 'Broken 2 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1423;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1423, 2, 'Broken 2 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1424;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1424, 2, 'Broken 2 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1425;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1425, 2, 'Broken 2 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1426;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1426, 2, 'Broken 2 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1427;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1427, 2, 'Broken 2 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1428;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1428, 2, 'Broken 2 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1429;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1429, 3, 'Broken 3 0', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 0
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1430;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1430, 3, 'Broken 3 1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 1
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1431;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1431, 3, 'Broken 3 2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 2
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1432;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1432, 3, 'Broken 3 3', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 3
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1433;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1433, 3, 'Broken 3 4', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 4
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1434;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1434, 3, 'Broken 3 5', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 5
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1435;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1435, 3, 'Broken 3 6', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 6
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1436;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1436, 3, 'Broken 3 7', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 7
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1437;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1437, 3, 'Broken 3 8', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 8
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1438;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1438, 3, 'Broken 3 9', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 9
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1439;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1439, 3, 'Broken 3 10', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 10
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1440;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1440, 3, 'Broken 3 11', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 11
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1441;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1441, 3, 'Broken 3 12', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 12
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1442;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1442, 3, 'Broken 3 13', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 13
);

DELETE FROM `barbershopstyle_dbc` WHERE `ID` = 1443;
INSERT INTO `barbershopstyle_dbc` (
    `ID`, `Type`, `DisplayName_Lang_enUS`, `DisplayName_Lang_enGB`, `DisplayName_Lang_koKR`,
    `DisplayName_Lang_frFR`, `DisplayName_Lang_deDE`, `DisplayName_Lang_enCN`, `DisplayName_Lang_zhCN`,
    `DisplayName_Lang_enTW`, `DisplayName_Lang_zhTW`, `DisplayName_Lang_esES`, `DisplayName_Lang_esMX`,
    `DisplayName_Lang_ruRU`, `DisplayName_Lang_ptPT`, `DisplayName_Lang_ptBR`, `DisplayName_Lang_itIT`,
    `DisplayName_Lang_Unk`, `DisplayName_Lang_Mask`, `Description_Lang_enUS`, `Description_Lang_enGB`,
    `Description_Lang_koKR`, `Description_Lang_frFR`, `Description_Lang_deDE`, `Description_Lang_enCN`,
    `Description_Lang_zhCN`, `Description_Lang_enTW`, `Description_Lang_zhTW`, `Description_Lang_esES`,
    `Description_Lang_esMX`, `Description_Lang_ruRU`, `Description_Lang_ptPT`, `Description_Lang_ptBR`,
    `Description_Lang_itIT`, `Description_Lang_Unk`, `Description_Lang_Mask`, `Cost_Modifier`, `Race`, `Sex`,
    `Data`
) VALUES (
    1443, 3, 'Broken 3 14', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, '', '', '', '',
    '', '', '', '', '', '', '', '', '', '', '', '', 16712172, 1.0, 14, 1, 14
);

-- Keep the race skill and Horde starting data; replace the old racial grants and action buttons.
UPDATE `playercreateinfo_skills` SET `Comment` = 'Broken - Racial' WHERE `raceMask` = 8192 AND `skill` = 792;
DELETE FROM `playercreateinfo_spell_custom` WHERE `racemask` = 8192 AND `Spell` IN (20549, 20550, 20551, 20552);
INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES
(8192, 0, 20549, 'Broken - War Stomp'),
(8192, 0, 20550, 'Broken - Endurance'),
(8192, 0, 20551, 'Broken - Nature Resistance'),
(8192, 0, 20552, 'Broken - Cultivation');
DELETE FROM `playercreateinfo_spell_custom`
WHERE `racemask` = 8192 AND `Spell` IN (110001, 110002, 110003, 110004);
UPDATE `playercreateinfo_action` SET `action` = 20549
WHERE `race` = 14 AND `action` = 110001 AND `type` = 0;

-- Replace the shaman template legacy Every Man for Himself button with War Stomp.
DELETE FROM `playercreateinfo_action` WHERE `race` = 14 AND `class` = 7 AND `button` = 3;
INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`) VALUES
(14, 7, 3, 20549, 0);
