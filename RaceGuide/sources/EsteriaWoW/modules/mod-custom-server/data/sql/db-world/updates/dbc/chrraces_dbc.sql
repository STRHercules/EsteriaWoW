-- Project-owned ChrRaces registry for the race overhaul.
-- Playable IDs 1-28 are coherent rows; legacy NPC rows are reserved at 32-42.
DELETE FROM `chrraces_dbc` WHERE `ID` IN (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42
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
) VALUES
(1, 12, 1, 4140, 49, 50, 'Hu', 7, 7, 15007, 1096, 'Human', 81, 0, 'Human', NULL, '인간', 'Humain', 'Mensch', NULL, '人类', NULL, NULL, 'Humano', 'Humano', 'Человек', NULL, NULL, NULL, NULL, 16712191, NULL, NULL, NULL, 'Humaine', NULL, NULL, NULL, NULL, NULL, 'Humana', 'Humana', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Humain', 'Mensch', NULL, NULL, NULL, NULL, 'Humano', 'Humano', 'Человек', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(2, 12, 2, 4141, 51, 52, 'Or', 1, 7, 15007, 1096, 'Orc', 21, 1, 'Orc', NULL, '오크', 'Orc', 'Orc', NULL, '兽人', NULL, NULL, 'Orco', 'Orco', 'Орк', NULL, NULL, NULL, NULL, 16712191, NULL, NULL, NULL, 'Orque', NULL, NULL, NULL, NULL, NULL, 'Orco', 'Orco', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Orc', 'Orc', NULL, NULL, NULL, NULL, 'Orco', 'Orco', 'Орк', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(3, 12, 3, 4147, 53, 54, 'Dw', 7, 7, 15007, 1090, 'Dwarf', 41, 0, 'Dwarf', NULL, '드워프', 'Nain', 'Zwerg', NULL, '矮人', NULL, NULL, 'Enano', 'Enano', 'Дворф', NULL, NULL, NULL, NULL, 16712191, NULL, NULL, NULL, 'Naine', NULL, NULL, NULL, NULL, NULL, 'Enana', 'Enana', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Nain', 'Zwerg', NULL, NULL, NULL, NULL, 'Enano', 'Enano', 'Дворф', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(4, 4, 4, 4145, 55, 56, 'Ni', 7, 7, 15007, 1096, 'NightElf', 61, 0, 'Night Elf', NULL, '나이트 엘프', 'Elfe de la nuit', 'Nachtelf', NULL, '暗夜精灵', NULL, NULL, 'Elfo de la noche', 'Elfo de la noche', 'Ночной эльф', NULL, NULL, NULL, NULL, 16712191, NULL, NULL, NULL, 'Elfe de la nuit', 'Nachtelfe', NULL, NULL, NULL, NULL, 'Elfa de la noche', 'Elfa de la noche', 'Ночная эльфийка', NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Elfe de la nuit', 'Nachtelf', NULL, NULL, NULL, NULL, 'Elfo de la noche', 'Elfo de la noche', 'Ночной эльф', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'MARKINGS', 'NORMAL', 0),
(5, 12, 5, 4142, 57, 58, 'Sc', 1, 7, 15007, 1096, 'Scourge', 2, 1, 'Undead', NULL, '언데드', 'Mort-vivant', 'Untoter', NULL, '亡灵', NULL, NULL, 'No-muerto', 'No-muerto', 'Нежить', NULL, NULL, NULL, NULL, 16712191, NULL, NULL, NULL, 'Morte-vivante', 'Untote', NULL, NULL, NULL, NULL, 'No-muerta', 'No-muerta', 'Нежить', NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Mort-vivant', 'Untoter', NULL, NULL, NULL, NULL, 'No-muerto', 'No-muerto', NULL, NULL, NULL, NULL, NULL, 16712172, 'FEATURES', 'FEATURES', 'NORMAL', 0),
(6, 14, 6, 4143, 59, 60, 'Ta', 1, 7, 15007, 1096, 'Tauren', 141, 1, 'Tauren', NULL, '타우렌', 'Tauren', 'Tauren', NULL, '牛头人', NULL, NULL, 'Tauren', 'Tauren', 'Таурен', NULL, NULL, NULL, NULL, 16712191, NULL, NULL, NULL, 'Taurène', NULL, NULL, NULL, NULL, NULL, 'Tauren', 'Tauren', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Tauren', 'Tauren', NULL, NULL, NULL, NULL, 'Tauren', 'Tauren', 'Таурен', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'HAIR', 'HORNS', 0),
(7, 12, 115, 4146, 1563, 1564, 'Gn', 7, 7, 15007, 1096, 'Gnome', 101, 0, 'Gnome', NULL, '노움', 'Gnome', 'Gnom', NULL, '侏儒', NULL, NULL, 'Gnomo', 'Gnomo', 'Гном', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Gnome', NULL, NULL, NULL, NULL, NULL, 'Gnoma', 'Gnoma', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Gnome', 'Gnom', NULL, NULL, NULL, NULL, 'Gnomo', 'Gnomo', 'Гном', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'EARRINGS', 'NORMAL', 0),
(8, 14, 116, 4144, 1478, 1479, 'Tr', 1, 7, 15007, 1096, 'Troll', 121, 1, 'Troll', NULL, '트롤', 'Troll', 'Troll', NULL, '巨魔', NULL, NULL, 'Trol', 'Trol', 'Тролль', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Trollesse', NULL, NULL, NULL, NULL, NULL, 'Trol', 'Trol', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Troll', 'Troll', NULL, NULL, NULL, NULL, 'Trol', 'Trol', 'Тролль', NULL, NULL, NULL, NULL, 16712172, 'TUSKS', 'TUSKS', 'NORMAL', 0),
(9, 12, 2, 4141, 6894, 6895, 'Go', 1, 7, 15007, 1096, 'Goblin', 21, 1, 'Goblin', NULL, '고블린', 'Gobelin', 'Goblin', NULL, '地精', NULL, NULL, 'Goblin', 'Goblin', 'Гоблин', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Gobeline', NULL, NULL, NULL, NULL, NULL, 'Goblin', 'Goblin', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Gobelin', 'Goblin', NULL, NULL, NULL, NULL, 'Goblin', 'Goblin', 'Гоблин', NULL, NULL, NULL, NULL, 16712172, 'PIERCINGS', 'PIERCINGS', 'NORMAL', 0),
(10, 12, 1610, 4142, 15476, 15475, 'Be', 1, 7, 15007, 1096, 'BloodElf', 162, 1, 'Blood Elf', NULL, '블러드 엘프', 'Elfe de sang', 'Blutelf', NULL, '血精灵', NULL, NULL, 'Elfo de sangre', 'Elfo de sangre', 'Син''Дорей', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Elfe de sang', 'Blutelfe', NULL, NULL, NULL, NULL, 'Elfa de sangre', 'Elfa de sangre', 'Син''Дорейка', NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Elfe de sang', 'Blutelf', NULL, NULL, NULL, NULL, 'Elfo de sangre', 'Elfo de sangre', 'Син''Дорей', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'EARRINGS', 'NORMAL', 1),
(11, 14, 1629, 4140, 16125, 16126, 'Dr', 7, 7, 15007, 1096, 'Draenei', 163, 0, 'Draenei', NULL, '드레나이', 'Draeneï', 'Draenei', NULL, '德莱尼', NULL, NULL, 'Draenei', 'Draenei', 'Дреней', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Draeneï', NULL, NULL, NULL, NULL, NULL, 'Draenei', 'Draenei', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Draeneï', 'Draenei', NULL, NULL, NULL, NULL, 'Draenei', 'Draenei', 'Дреней', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'HORNS', 'NORMAL', 1),
(12, 12, 1, 4143, 29422, 29423, 'Wo', 7, 7, 15007, 1096, 'Worgen', 61, 0, 'Worgen', NULL, '늑대인간', 'Worgen', 'Worgen', NULL, '狼人', NULL, NULL, 'Huargen', 'Huargen', 'Ворген', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Worgen', NULL, NULL, NULL, NULL, NULL, 'Huargen', 'Huargen', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Worgen', 'Worgen', NULL, NULL, NULL, NULL, 'Huargen', 'Huargen', 'Ворген', NULL, NULL, NULL, NULL, 16712172, 'FEATURES', 'EARS', 'NORMAL', 0),
(13, 12, 1, 4140, 15476, 15475, 'He', 7, 7, 15007, 1096, 'HighElf', 81, 0, 'High Elf', NULL, '하이 엘프', 'Elfe haut', 'Hochelf', NULL, '高精灵', NULL, NULL, 'Elfo alto', 'Elfo alto', 'Кел''Дорей', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Elfe haute', 'Hochelfe', NULL, NULL, NULL, NULL, 'Elfa alta', 'Elfa alta', 'Кел''Дорейка', NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Elfe haut', 'Hochelf', NULL, NULL, NULL, NULL, 'Elfo alto', 'Elfo alto', 'Кел''Дорей', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'EARRINGS', 'NORMAL', 1),
(14, 12, 2, 4141, 51, 52, 'Mo', 1, 7, 15007, 1096, 'Maghar', 21, 1, 'Mag''har Orc', NULL, '마가르 오크', 'Orc Mag''har', 'Mag''har-Orc', NULL, '嗎咖兽人', NULL, NULL, 'Orco Mag''har', 'Tábido', 'Орк Маг''хар', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Orque Mag''hare', NULL, NULL, NULL, NULL, NULL, 'Orco Mag''har', 'Orco Mag''har', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Orc Mag''har', 'Mag''har-Orc', NULL, NULL, NULL, NULL, 'Orco Mag''har', 'Orco Mag''har', 'Орк Маг''хар', NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(15, 13, 2241, 4141, 60000, 60001, 'Se', 1, 7, 15007, 1096, 'Sethrak', 21, 1, 'Sethrak', 'Sethrak', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712191, 'Sethrak', 'Sethrak', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Sethrak', 'Sethrak', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(16, 12, 2, 4141, 60008, 60009, 'Er', 1, 7, 15007, 1096, 'Eredar', 0, 1, 'Eredar', 'Eredar', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Eredar', 'Eredar', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Eredar', 'Eredar', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'NORMAL', 'NORMAL', 0),
(17, 12, 1610, 4141, 60010, 60011, 'Nb', 1, 7, 15007, 1096, 'Nightborne', 162, 1, 'Nightborne', 'Nightborne', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Nightborne', 'Nightborne', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Nightborne', 'Nightborne', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'EARRINGS', 'NORMAL', 0),
(18, 12, 1, 4140, 60004, 60005, 'Pa', 7, 7, 15007, 1096, 'Pandaren', 81, 0, 'Pandaren', 'Pandaren', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712191, 'Pandaren', 'Pandaren', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Pandaren', 'Pandaren', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(19, 12, 1, 4140, 60012, 60013, 'Ve', 7, 7, 15007, 1096, 'VoidElf', 81, 0, 'Void Elf', 'Void Elf', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Void Elf', 'Void Elf', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Void Elf', 'Void Elf', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'EARRINGS', 'NORMAL', 0),
(20, 12, 2, 4141, 60006, 60007, 'Vu', 1, 7, 15007, 1096, 'Vulpera', 21, 1, 'Vulpera', 'Vulpera', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Vulpera', 'Vulpera', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Vulpera', 'Vulpera', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'PIERCINGS', 'PIERCINGS', 'NORMAL', 0),
(21, 12, 1629, 4140, 60014, 60015, 'Lf', 7, 7, 15007, 1096, 'LightforgedDraenei', 163, 0, 'Lightforged Draenei', 'Lightforged Draenei', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Lightforged Draenei', 'Lightforged Draenei', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Lightforged Draenei', 'Lightforged Draenei', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'HORNS', 'NORMAL', 0),
(22, 12, 116, 4141, 60016, 60017, 'Za', 1, 7, 15007, 1096, 'ZandalariTroll', 121, 1, 'Zandalari Troll', 'Zandalari Troll', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Zandalari Troll', 'Zandalari Troll', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Zandalari Troll', 'Zandalari Troll', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'TUSKS', 'TUSKS', 'NORMAL', 0),
(23, 12, 3, 4140, 60018, 60019, 'Di', 7, 7, 15007, 1090, 'DarkIronDwarf', 41, 0, 'Dark Iron Dwarf', 'Dark Iron Dwarf', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712191, 'Dark Iron Dwarf', 'Dark Iron Dwarf', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Dark Iron Dwarf', 'Dark Iron Dwarf', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(24, 12, 1629, 0, 17576, 17577, 'Br', 7, 7, 15007, 1096, 'Broken', 0, 0, 'Broken', 'Broken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Broken', 'Broken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Broken', 'Broken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(25, 12, 1, 4142, 57, 58, 'Fo', 7, 7, 15007, 1096, 'Forsaken', 2, 0, 'Forsaken', 'Forsaken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712191, 'Forsaken', 'Forsaken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Forsaken', 'Forsaken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'FEATURES', 'FEATURES', 'NORMAL', 0),
(26, 12, 2, 4140, 49, 50, 'Pa', 1, 7, 15007, 1096, 'Pandaren', 81, 1, 'Pandaren', 'Pandaren', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712191, 'Pandaren', 'Pandaren', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Pandaren', 'Pandaren', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(27, 12, 2, 0, 17576, 17577, 'Br', 1, 7, 15007, 1096, 'Broken', 0, 1, 'Broken', 'Broken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Broken', 'Broken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Broken', 'Broken', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(28, 12, 2, 4141, 60020, 60021, 'Dr', 1, 7, 15007, 1096, 'Dracthyr', 0, 1, 'Dracthyr', 'Dracthyr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, 'Dracthyr', 'Dracthyr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'Dracthyr', 'Dracthyr', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'NORMAL', 'NORMAL', 0),
(32, 1, 1, 0, 17578, 17579, 'Sk', 7, 7, 15007, 1096, 'Skeleton', 0, 2, 'Skeleton', NULL, '해골', 'Squelette', 'Skelett', NULL, '骷髅', NULL, NULL, 'Esqueleto', 'Esqueleto', 'Скелет', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Squelette', NULL, NULL, NULL, NULL, NULL, 'Esqueleto', 'Esqueleto', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Squelette', 'Skelett', NULL, NULL, NULL, NULL, 'Esqueleto', 'Esqueleto', 'Скелет', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(33, 9, 1, 0, 21685, 21686, 'Vr', 7, 7, 15007, 1096, 'Vrykul', 0, 2, 'Vrykul', NULL, '브리쿨', 'Vrykul', 'Vrykul', NULL, '维库人', NULL, NULL, 'Vrykul', 'Vrykul', 'Врайкул', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Vrykule', NULL, NULL, NULL, NULL, NULL, 'Vrykul', 'Vrykul', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Vrykul', 'Vrykul', NULL, NULL, NULL, NULL, 'Vrykul', 'Vrykul', 'Врайкул', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(34, 1, 1, 0, 21780, 21781, 'Tu', 7, 7, 15007, 1096, 'Tuskarr', 0, 2, 'Tuskarr', NULL, '투스카르', 'Rohart', 'Tuskarr', NULL, '海象人', NULL, NULL, 'Colmillarr', 'Colmillarr', 'Клыкарр', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Rohart', NULL, NULL, NULL, NULL, NULL, 'Colmillarr', 'Colmillarr', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Rohart', 'Tuskarr', NULL, NULL, NULL, NULL, 'Colmillarr', 'Colmillarr', 'Клыкарр', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(35, 15, 1, 0, 21963, 21964, 'Ft', 7, 7, 15007, 1096, 'ForestTroll', 0, 2, 'Forest Troll', NULL, '숲 트롤', 'Troll des forêts', 'Waldtroll', NULL, '森林巨魔', NULL, NULL, 'Trol de bosque', 'Trol de bosque', 'Лесной тролль', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Trollesse des forêts', NULL, NULL, NULL, NULL, NULL, 'Trol de bosque', 'Trol de bosque', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Troll des forêts', 'Waldtroll', NULL, NULL, NULL, NULL, 'Trol de bosque', 'Trol de bosque', 'Лесной тролль', NULL, NULL, NULL, NULL, 16712172, 'TUSKS', 'TUSKS', 'Normal', 0),
(36, 5, 1, 0, 26316, 26317, 'Wt', 7, 7, 15007, 1096, 'Taunka', 0, 2, 'Taunka', NULL, '타운카', 'Taunka', 'Taunka', NULL, '牦牛人', NULL, NULL, 'Taunka', 'Taunka', 'Таунка', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Taunka', NULL, NULL, NULL, NULL, NULL, 'Taunka', 'Taunka', 'Таунка', NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Taunka', 'Taunka', NULL, NULL, NULL, NULL, 'Taunka', 'Taunka', 'Таунка', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(37, 5, 1, 0, 26871, 26872, 'NS', 7, 7, 15007, 1096, 'NorthrendSkeleton', 0, 2, 'Northrend Skeleton', NULL, '노스렌드 해골', 'Squelette du Norfendre', 'Skelett aus Nordend', NULL, '诺森德骷髅', NULL, NULL, 'Esqueleto de Rasganorte', 'Esqueleto de Rasganorte', 'Нордскольский скелет', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Squelette du Norfendre', NULL, NULL, NULL, NULL, NULL, 'Esqueleto de Rasganorte', 'Esqueleto de Rasganorte', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Squelette du Norfendre', 'Skelett aus Nordend', NULL, NULL, NULL, NULL, 'Esqueleto de Rasganorte', 'Esqueleto de Rasganorte', 'Нордскольский скелет', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(38, 5, 1, 0, 26873, 26874, 'It', 7, 7, 15007, 1096, 'IceTroll', 0, 2, 'Ice Troll', NULL, '얼음 트롤', 'Troll des glaces', 'Eistroll', NULL, '冰巨魔', NULL, NULL, 'Trol de hielo', 'Trol de hielo', 'Ледяной тролль', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Trollesse des glaces', NULL, NULL, NULL, NULL, NULL, 'Trol de hielo', 'Trol de hielo', NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Troll des glaces', 'Eistroll', NULL, NULL, NULL, NULL, 'Trol de hielo', 'Trol de hielo', 'Ледяной тролль', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(39, 1, 1, 0, 17402, 17403, 'Na', 7, 7, 15007, 1096, 'Naga_', 0, 2, 'Naga', NULL, '나가', 'Naga', 'Naga', NULL, '纳迦', NULL, NULL, 'Naga', 'Naga', 'Нага', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Naga', NULL, NULL, NULL, NULL, NULL, 'Naga', 'Naga', 'Нага', NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Naga', 'Naga', NULL, NULL, NULL, NULL, 'Naga', 'Naga', 'Наг', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0),
(40, 1, 1, 4143, 94135, 94136, 'Hu', 7, 7, 15007, 1096, 'Human', 61, 0, 'Gilnean', NULL, 'Gilnean', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Gilnean', NULL, NULL, NULL, NULL, NULL, 'Gilnean', NULL, NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'PIERCINGS', 'NORMAL', 0),
(41, 5, 1, 0, 16981, 16980, 'Fo', 7, 7, 15007, 1096, 'FelOrc', 0, 2, 'Fel Orc', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 16712172, 'NORMAL', 'NORMAL', 'NORMAL', 0),
(42, 5, 1, 0, 17576, 17577, 'Br', 7, 7, 15007, 1096, 'Broken', 0, 2, 'Broken', NULL, '뒤틀린 드레나이', 'Roué', 'Zerschlagener', NULL, '破碎者', NULL, NULL, 'Tábido', 'Tábido', 'Падший', NULL, NULL, NULL, NULL, 16712190, NULL, NULL, NULL, 'Rouée', NULL, NULL, NULL, NULL, NULL, 'Tábida', 'Tábida', 'Падшая', NULL, NULL, NULL, NULL, 16712172, NULL, NULL, NULL, 'Roué', 'Zerschlagener', NULL, NULL, NULL, NULL, 'Tábido', 'Tábido', 'Падший', NULL, NULL, NULL, NULL, 16712172, 'Normal', 'Normal', 'Normal', 0);
