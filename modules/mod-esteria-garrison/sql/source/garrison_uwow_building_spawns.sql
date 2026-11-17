-- Normalized from UWoW 2015_10_30_00_world_garrison_building_spawn.sql

--
-- Структура таблицы `garrison_building_creature`
--

DROP TABLE IF EXISTS `garrison_building_creature`;
CREATE TABLE `garrison_building_creature` (
  `plotID` mediumint(8) unsigned NOT NULL,
  `BuildID` mediumint(8) unsigned NOT NULL,
  `id` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT 'Creature Identifier',
  `map` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT 'Map Identifier',
  `position_x` float NOT NULL DEFAULT '0',
  `position_y` float NOT NULL DEFAULT '0',
  `position_z` float NOT NULL DEFAULT '0',
  `orientation` float NOT NULL DEFAULT '0',
  `building` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `idx` int(11) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Garrison building spawn System';

--
-- Дамп данных таблицы `garrison_building_creature`
--

INSERT INTO `garrison_building_creature` (`plotID`, `BuildID`, `id`, `map`, `position_x`, `position_y`, `position_z`, `orientation`, `idx`) VALUES
-- Barrack lvl1. 26 instance.
(23, 26, 79812, 1152, 5576.35, 4460.13, 130.826, 0.95993, 1),
(23, 26, 79781, 1152, 5583.54, 4465.59, 130.779, 3.49343, 2),
(23, 26, 80571, 1152, 5596.58, 4463.71, 130.501, 2.09985, 3),
(23, 26, 80569, 1152, 5586.86, 4453.04, 130.779, 2.1951, 4),
(23, 26, 80571, 1152, 5589.37, 4467.52, 130.779, 5.63951, 5),
(23, 26, 80569, 1152, 5591.84, 4467.31, 130.779, 0.0105276, 6),
(23, 26, 80299, 1152, 5579.26, 4468.18, 130.784, 5.65445, 7),
(23, 26, 80299, 1152, 5581.39, 4466.27, 130.779, 2.17006, 8),
(23, 26, 80569, 1152, 5594.32, 4466.94, 130.779, 3.09207, 9),
(23, 26, 80569, 1152, 5594.29, 4455.23, 130.779, 1.74426, 10),
(23, 26, 80571, 1152, 5575.39, 4479.17, 130.789, 0.189679, 11),
(23, 26, 80572, 1152, 5582.73, 4479.78, 130.779, 0.262985, 12);

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `garrison_building_creature`
--
ALTER TABLE `garrison_building_creature`
  ADD PRIMARY KEY (`idx`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `garrison_building_creature`
--
ALTER TABLE `garrison_building_creature`
  MODIFY `idx` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=13;

--
-- Структура таблицы `garrison_building_gameobject`
--

DROP TABLE IF EXISTS `garrison_building_gameobject`;
CREATE TABLE IF NOT EXISTS `garrison_building_gameobject` (
  `plotID` mediumint(8) unsigned NOT NULL,
  `BuildID` mediumint(8) unsigned NOT NULL,
  `id` mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT 'Gameobject Identifier',
  `map` smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT 'Map Identifier',
  `position_x` float NOT NULL DEFAULT '0',
  `position_y` float NOT NULL DEFAULT '0',
  `position_z` float NOT NULL DEFAULT '0',
  `orientation` float NOT NULL DEFAULT '0',
  `rotation0` float NOT NULL DEFAULT '0',
  `rotation1` float NOT NULL DEFAULT '0',
  `rotation2` float NOT NULL DEFAULT '0',
  `rotation3` float NOT NULL DEFAULT '0',
  `building` tinyint(1) unsigned NOT NULL DEFAULT '1',
  `idx` int(11) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC COMMENT='Garrison building spawn System';

--
-- Дамп данных таблицы `garrison_building_gameobject`
--

INSERT INTO `garrison_building_gameobject` (`plotID`, `BuildID`, `id`, `map`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `idx`) VALUES
-- Horde. Big. empty building
(23, 0, 231012, 1152, 5579.41, 4464.98, 132.137, 0.958846, 0, 0, 0, 1, 1),
-- Barrack lvl1. 26 instance.
(23, 26, 236297, 1152, 5576.58, 4470.37, 130.71, 5.79449, 0, 0, 0.461748, 0.887011, 2),
(23, 26, 236298, 1152, 5577.53, 4464.96, 130.695, 5.16617, 0, 0, 0.461748, 0.887011, 3),
(23, 26, 236299, 1152, 5576.66, 4463.07, 130.757, 0.584684, 0, 0, 0.461748, 0.887011, 4),
(23, 26, 236300, 1152, 5578.8, 4461.31, 130.742, 1.76278, 0, 0, 0.461748, 0.887011, 5),
(23, 26, 238790, 1152, 5566.97, 4461.79, 130.368, 3.2376, 0, 0, 0.461748, 0.887011, 6),
(23, 26, 238791, 1152, 5567.65, 4468.12, 130.368, 2.67908, 0, 0, 0.461748, 0.887011, 7),
(23, 26, 238796, 1152, 5580.14, 4453.97, 132.247, 4.95674, 0, 0, 0.461748, 0.887011, 8),
(23, 26, 238797, 1152, 5568.37, 4450.02, 130.368, 0.261796, 0, 0, 0.461748, 0.887011, 9),
(23, 26, 238798, 1152, 5571.33, 4448.41, 130.368, 2.19038, 0, 0, 0.461748, 0.887011, 10);

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `garrison_building_gameobject`
--
ALTER TABLE `garrison_building_gameobject`
  ADD PRIMARY KEY (`idx`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `garrison_building_gameobject`
--
ALTER TABLE `garrison_building_gameobject`
  MODIFY `idx` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=11;
  
-- update 24.11.2015


DELETE FROM `garrison_building_gameobject` WHERE plotID = 23 AND BuildID = 26 AND building = 1;
INSERT INTO `garrison_building_gameobject` (`plotID`, `BuildID`, `id`, `map`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `building`) VALUES
-- Alliance barrack Plot 23
(23, 26, 230867, 1158, 1909.361, 237.7349, 80.03348, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1893.265, 231.7484, 80.21535, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1904.725, 242.6158, 79.78568, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1919.835, 224.4023, 80.13195, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1913.38, 226.366, 80.04122, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1924.563, 235.8465, 86.97174, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1920.161, 233.0135, 93.84232, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1906.375, 241.5055, 85.95805, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1899.869, 239.3909, 79.69661, 2.792518, 0, 0, 0, 1, 1),
(23, 26, 230867, 1158, 1920.248, 223.9522, 86.29936, 2.792518, 0, 0, 0, 1, 1),
-- Horde barrack Plot 23
(23, 26, 230867, 1152, 5579.406, 4464.98, 132.1373, 0.9588462, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5584.206, 4456.809, 132.4475, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5568.307, 4464.964, 132.4534, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5583.352, 4455.21, 132.4464, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5577.282, 4468.669, 133.6842, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5575.202, 4457.563, 132.448, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5584.125, 4464.841, 133.4761, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5570.659, 4460.041, 134.1874, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5593.054, 4455.943, 132.448, 0.9599279, 0, 0, 0, 1, 1),
(23, 26, 230867, 1152, 5570.245, 4458.582, 133.6908, 0.9599279, 0, 0, 0, 1, 1);




DELETE FROM `garrison_building_creature` WHERE plotID = 23 AND BuildID = 26 AND building = 1;
INSERT INTO `garrison_building_creature` (`plotID`, `BuildID`, `id`, `map`, `position_x`, `position_y`, `position_z`, `orientation`, `building`) VALUES
-- Alliance barrack Plot 23
(23, 26, 81653, 1158, 1919.737, 237.8879, 78.69244, 3.114007, 1), -- @CGUID+2694
(23, 26, 81653, 1158, 1897.866, 248.1321, 79.6972, 4.345179, 1),
(23, 26, 81653, 1158, 1917.008, 235.4857, 78.64996, 3.771088, 1),
(23, 26, 81653, 1158, 1904.42, 241.5841, 78.69262, 1.350547, 1),
(23, 26, 81653, 1158, 1919.857, 233.8233, 92.994, 5.530943, 1),
(23, 26, 81653, 1158, 1924.944, 236.9001, 85.67538, 4.04794, 1),
(23, 26, 81653, 1158, 1900.13, 235.9665, 78.69247, 5.734275, 1),
(23, 26, 81653, 1158, 1893.808, 232.5319, 78.87403, 3.922893, 1),
(23, 26, 81653, 1158, 1919.697, 222.2468, 85.67538, 1.446597, 1),
(23, 26, 81653, 1158, 1905.121, 242.7867, 85.67538, 5.459328, 1),
(23, 26, 81653, 1158, 1907.602, 237.4362, 78.69247, 0.242609, 1),
(23, 26, 81653, 1158, 1912.478, 226.9975, 78.69247, 5.624393, 1),
(23, 26, 81653, 1158, 1919.376, 224.8721, 78.67632, 5.561766, 1), -- @CGUID+2706
--
(23, 26, 78467, 1152, 5562.094, 4477.225, 139.3227, 1.137771, 1),
(23, 26, 78467, 1152, 5584.014, 4466.735, 132.5313, 4.880752, 1),
(23, 26, 78467, 1152, 5570.71, 4473.859, 132.5312, 2.315711, 1),
(23, 26, 78467, 1152, 5579.246, 4469.841, 132.5313, 3.68408, 1),
(23, 26, 78467, 1152, 5571.561, 4459.44, 132.5313, 3.653688, 1),
(23, 26, 78467, 1152, 5574.634, 4458.65, 132.5313, 4.890327, 1),
(23, 26, 78467, 1152, 5591.001, 4456.408, 132.5313, 5.53311, 1),
(23, 26, 78467, 1152, 5589.817, 4467.72, 142.0054, 4.291895, 1),
(23, 26, 78467, 1152, 5569.113, 4465.934, 132.5307, 4.010014, 1),
(23, 26, 78467, 1152, 5588.601, 4466.676, 138.978, 0.1016312, 1),
(23, 26, 78467, 1152, 5588.601, 4466.676, 138.978, 0.1016312, 1);

UPDATE `garrison_building_creature` SET `building` = 1 WHERE `building` = 0 AND `BuildID` <> 0;
UPDATE `garrison_building_gameobject` SET `building` = IF(`BuildID` = 0, 0, 1);
