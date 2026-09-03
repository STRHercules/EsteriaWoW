DELETE FROM `chrraces_dbc` WHERE `ID` IN (
	9, -- Delete existing race 9 (if any)
	12, -- Delete existing race 12 (if any)
	13 -- Delete existing race 13 (if any)
);
INSERT INTO `chrraces_dbc` (
	`ID`, -- Primary key (referenced by many DBCs and tables)
	`Flags`, -- 1: Not playable, 2: Bare feet, 4: Can mount, 8: Has bald
	`FactionID`, -- Faction template ID. (Also decides creation screen order.)
	`ExplorationSoundID`,
	`MaleDisplayId`, -- References CreatureDisplayInfo.dbc (for character creation screen only)
	`FemaleDisplayId`,
	`ClientPrefix`, -- For helmet models
	`BaseLanguage`, -- 1: Horde, 7: Alliance (and Not playable)
	`CreatureType`, -- 7: Humanoid
	`ResSicknessSpellID`, -- Always 15007
	`SplashSoundID`, -- 1090 for Dwarves, 1096 for everyone else
	`ClientFilestring`, -- Same as the one used in model filepaths.
	`CinematicSequenceID`, -- Opening cinematic
	`Alliance`, -- Faction. 0: Alliance, 1: Horde, 2: Not available
	`Name_Lang_enUS`,
	`Name_Lang_enGB`, -- Many custom DBCs put Korean here, moving everything over by one.
	`Name_Lang_koKR`,
	`Name_Lang_frFR`,
	`Name_Lang_deDE`,
	`Name_Lang_enCN`,
	`Name_Lang_zhCN`,
	`Name_Lang_enTW`,
	`Name_Lang_zhTW`,
	`Name_Lang_esES`,
	`Name_Lang_esMX`,
	`Name_Lang_ruRU`,
	`Name_Lang_ptPT`,
	`Name_Lang_ptBR`,
	`Name_Lang_itIT`,
	`Name_Lang_Unk`,
	`Name_Lang_Mask`, -- Unused, always 16712190
	`Name_Female_Lang_enUS`,
	`Name_Female_Lang_enGB`,
	`Name_Female_Lang_koKR`,
	`Name_Female_Lang_frFR`,
	`Name_Female_Lang_deDE`,
	`Name_Female_Lang_enCN`,
	`Name_Female_Lang_zhCN`, -- Always NULL
	`Name_Female_Lang_enTW`,
	`Name_Female_Lang_zhTW`,
	`Name_Female_Lang_esES`,
	`Name_Female_Lang_esMX`,
	`Name_Female_Lang_ruRU`,
	`Name_Female_Lang_ptPT`,
	`Name_Female_Lang_ptBR`,
	`Name_Female_Lang_itIT`,
	`Name_Female_Lang_Unk`,
	`Name_Female_Lang_Mask`, -- Unused, always 16712172
	`Name_Male_Lang_enUS`,
	`Name_Male_Lang_enGB`,
	`Name_Male_Lang_koKR`,
	`Name_Male_Lang_frFR`,
	`Name_Male_Lang_deDE`,
	`Name_Male_Lang_enCN`,
	`Name_Male_Lang_zhCN`,
	`Name_Male_Lang_enTW`,
	`Name_Male_Lang_zhTW`,
	`Name_Male_Lang_esES`,
	`Name_Male_Lang_esMX`,
	`Name_Male_Lang_ruRU`,
	`Name_Male_Lang_ptPT`,
	`Name_Male_Lang_ptBR`,
	`Name_Male_Lang_itIT`,
	`Name_Male_Lang_Unk`,
	`Name_Male_Lang_Mask`, -- Unused, always 16712172
	`FacialHairCustomization_1`, -- Internal names for facial features.
	`FacialHairCustomization_2`, -- Localized ones in luas.
	`HairCustomization`, -- Internal name for hair customization. Horns for Tauren, normal for others.
	`Required_Expansion` -- 1: Burning Crusade, 0: Classic & Not playable
) VALUES (
	9, -- ID
	12, -- Flags
	2, -- FactionID
	4141, -- ExplorationSoundID
	6894, -- MaleDisplayId
	6895, -- FemaleDisplayId
	'Go', -- ClientPrefix
	1, -- BaseLanguage
	7, -- CreatureType
	15007, -- ResSicknessSpellID
	1096, -- SplashSoundID
	'Goblin', -- ClientFilestring
	21, -- CinematicSequenceID
	1, -- Alliance
	'Goblin', -- Name_Lang_enUS
	'Goblin', -- Name_Lang_enGB
	'고블린', -- Name_Lang_koKR
	'Gobelin', -- Name_Lang_frFR
	'Goblin', -- Name_Lang_deDE
	NULL, -- Name_Lang_enCN
	'地精', -- Name_Lang_zhCN
	NULL, -- Name_Lang_enTW
	'地精', -- Name_Lang_zhTW
	'Goblin', -- Name_Lang_esES
	'Goblin', -- Name_Lang_esMX
	'Гоблин', -- Name_Lang_ruRU
	NULL, -- Name_Lang_ptPT
	NULL, -- Name_Lang_ptBR
	NULL, -- Name_Lang_itIT
	NULL, -- Name_Lang_Unk
	16712190, -- Name_Lang_Mask
	NULL, -- Name_Female_Lang_enUS
	NULL, -- Name_Female_Lang_enGB
	NULL, -- Name_Female_Lang_koKR
	'Gobeline', -- Name_Female_Lang_frFR
	NULL, -- Name_Female_Lang_deDE
	NULL, -- Name_Female_Lang_enCN
	NULL, -- Name_Female_Lang_zhCN
	NULL, -- Name_Female_Lang_enTW
    NULL, -- Name_Female_Lang_zhTW
	'Goblin', -- Name_Female_Lang_esES
	'Goblin', -- Name_Female_Lang_esMX
	NULL, -- Name_Female_Lang_ruRU
	NULL, -- Name_Female_Lang_ptPT
	NULL, -- Name_Female_Lang_ptBR
	NULL, -- Name_Female_Lang_itIT
    NULL, -- Name_Female_Lang_Unk
	16712172, -- Name_Female_Lang_Mask
	NULL, -- Name_Male_Lang_enUS
	NULL, -- Name_Male_Lang_enGB
	NULL, -- Name_Male_Lang_koKR
	'Gobelin', -- Name_Male_Lang_frFR
	'Goblin', -- Name_Male_Lang_deDE
	NULL, -- Name_Male_Lang_enCN
	NULL, -- Name_Male_Lang_zhCN
	NULL, -- Name_Male_Lang_enTW
	NULL, -- Name_Male_Lang_zhTW
	'Goblin', -- Name_Male_Lang_esES
	'Goblin', -- Name_Male_Lang_esMX
	'Гоблин', -- Name_Male_Lang_ruRU
	NULL, -- Name_Male_Lang_ptPT
	NULL, -- Name_Male_Lang_ptBR
	NULL, -- Name_Male_Lang_itIT
	NULL, -- Name_Male_Lang_Unk
	16712172, -- Name_Male_Lang_Mask
	'PIERCINGS', -- FacialHairCustomization_1
	'PIERCINGS', -- FacialHairCustomization_2
	'NORMAL', -- HairCustomization
	0 -- Required_Expansion
), (
	12, -- ID
	12, -- Flags
	1, -- FactionID
	4143, -- ExplorationSoundID
	29422, -- MaleDisplayID
	29423, -- FemaleDisplayID
	'Wo', -- ClientPrefix
	7, -- BaseLanguage
	7, -- CreatureType
	15007, -- ResSicknessSpellID
	1096, -- SplashSoundID
	'Worgen', -- ClientFilestring
	61, -- CinematicSequenceID
	0, -- Alliance
	'Worgen', -- Name_Lang_enUS
	'Worgen', -- Name_Lang_enGB
	'늑대인간', -- Name_Lang_koKR
	'Worgen', -- Name_Lang_frFR
	'Worgen', -- Name_Lang_deDE
	NULL, -- Name_Lang_enCN
	'狼人', -- Name_Lang_zhCN
	NULL, -- Name_Lang_enTW
	'狼人', -- Name_Lang_zhTW
	'Huargen', -- Name_Lang_esES
	'Huargen', -- Name_Lang_esMX
	'Ворген', -- Name_Lang_ruRU
	NULL, -- Name_Lang_ptPT
	NULL, -- Name_Lang_ptBR
	NULL, -- Name_Lang_itIT
	NULL, -- Name_Lang_Unk
	16712190, -- Name_Lang_Mask
	NULL, -- Name_Female_Lang_enUS
	NULL, -- Name_Female_Lang_enGB
	NULL, -- Name_Female_Lang_koKR
	'Worgen', -- Name_Female_Lang_frFR
	NULL, -- Name_Female_Lang_deDE
	NULL, -- Name_Female_Lang_enCN
	NULL, -- Name_Female_Lang_zhCN
	NULL, -- Name_Female_Lang_enTW
    NULL, -- Name_Female_Lang_zhTW
	'Huargen', -- Name_Female_Lang_esES
	'Huargen', -- Name_Female_Lang_esMX
	NULL, -- Name_Female_Lang_ruRU
	NULL, -- Name_Female_Lang_ptPT
	NULL, -- Name_Female_Lang_ptBR
	NULL, -- Name_Female_Lang_itIT
    NULL, -- Name_Female_Lang_Unk
	16712172, -- Name_Female_Lang_Mask
	NULL, -- Name_Male_Lang_enUS
	NULL, -- Name_Male_Lang_enGB
	NULL, -- Name_Male_Lang_koKR
	'Worgen', -- Name_Male_Lang_frFR
	'Worgen', -- Name_Male_Lang_deDE
	NULL, -- Name_Male_Lang_enCN
	NULL, -- Name_Male_Lang_zhCN
	NULL, -- Name_Male_Lang_enTW
	NULL, -- Name_Male_Lang_zhTW
	'Huargen', -- Name_Male_Lang_esES
	'Huargen', -- Name_Male_Lang_esMX
	'Ворген', -- Name_Male_Lang_ruRU
	NULL, -- Name_Male_Lang_ptPT
	NULL, -- Name_Male_Lang_ptBR
	NULL, -- Name_Male_Lang_itIT
	NULL, -- Name_Male_Lang_Unk
	16712172, -- Name_Male_Lang_Mask
	'FEATURES', -- FacialHairCustomization_1
	'EARS', -- FacialHairCustomization_2
	'NORMAL', -- HairCustomization
	0 -- Required_Expansion
), (
	13, -- ID
	12, -- Flags
	1, -- FactionID
	4140, -- ExplorationSoundID
	15476, -- MaleDisplayId
	15475, -- FemaleDisplayId
	'He', -- ClientPrefix
	7, -- BaseLanguage
	7, -- CreatureType
	15007, -- ResSicknessSpellID
	1096, -- SplashSoundID
	'HighElf', -- ClientFilestring
	81, -- CinematicSequenceID
	0, -- Alliance
	'High Elf', -- Name_Lang_enUS
	'High Elf', -- Name_Lang_enGB
	'하이 엘프', -- Name_Lang_koKR
	'Elfe haut', -- Name_Lang_frFR
	'Hochelf', -- Name_Lang_deDE
	NULL, -- Name_Lang_enCN
	'高精灵', -- Name_Lang_zhCN
	NULL, -- Name_Lang_enTW
	'高精靈', -- Name_Lang_zhTW
	'Elfo alto', -- Name_Lang_esES
	'Elfo alto', -- Name_Lang_esMX
	'Кел’Дорей', -- Name_Lang_ruRU
	NULL, -- Name_Lang_ptPT
	NULL, -- Name_Lang_ptBR
	NULL, -- Name_Lang_itIT
	NULL, -- Name_Lang_Unk
	16712190, -- Name_Lang_Mask
	NULL, -- Name_Female_Lang_enUS
	NULL, -- Name_Female_Lang_enGB
	NULL, -- Name_Female_Lang_koKR
	'Elfe haute', -- Name_Female_Lang_frFR
	'Hochelfe', -- Name_Female_Lang_deDE
	NULL, -- Name_Female_Lang_enCN
	NULL, -- Name_Female_Lang_zhCN
	NULL, -- Name_Female_Lang_enTW
    NULL, -- Name_Female_Lang_zhTW
	'Elfa alta', -- Name_Female_Lang_esES
	'Elfa alta', -- Name_Female_Lang_esMX
	'Кел’Дорейка', -- Name_Female_Lang_ruRU
	NULL, -- Name_Female_Lang_ptPT
	NULL, -- Name_Female_Lang_ptBR
	NULL, -- Name_Female_Lang_itIT
    NULL, -- Name_Female_Lang_Unk
	16712172, -- Name_Female_Lang_Mask
	NULL, -- Name_Male_Lang_enUS
	NULL, -- Name_Male_Lang_enGB
	NULL, -- Name_Male_Lang_koKR
	'Elfe haut', -- Name_Male_Lang_frFR
	'Hochelf', -- Name_Male_Lang_deDE
	NULL, -- Name_Male_Lang_enCN
	NULL, -- Name_Male_Lang_zhCN
	NULL, -- Name_Male_Lang_enTW
	NULL, -- Name_Male_Lang_zhTW
	'Elfo alto', -- Name_Male_Lang_esES
	'Elfo alto', -- Name_Male_Lang_esMX
	'Кел’Дорей', -- Name_Male_Lang_ruRU
	NULL, -- Name_Male_Lang_ptPT
	NULL, -- Name_Male_Lang_ptBR
	NULL, -- Name_Male_Lang_itIT
	NULL, -- Name_Male_Lang_Unk
	16712172, -- Name_Male_Lang_Mask
	'NORMAL', -- FacialHairCustomization_1
	'EARRINGS', -- FacialHairCustomization_2
	'NORMAL', -- HairCustomization
	0 -- Required_Expansion
);