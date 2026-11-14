DELETE FROM `game_tele` WHERE `id` BETWEEN 2000 AND 2006;
-- game_tele: 7 rows
INSERT INTO `game_tele` (`id`, `position_x`, `position_y`, `position_z`, `orientation`, `map`, `name`) VALUES
(2000, 6006.94, 1534.93, 34.5823, 0, 1405, 'expisland'),
(2001, -1866.2421875, -1904.6954345703125, 0.9986450000433251, 0, 1410, 'forestarena'),
(2002, -2012.08544921875, -1986.0806884765625, 1.0001120000015362, 0, 1411, 'blackforest'),
(2003, 11422.08984375, 11665.083984375, 1.0007650000043213, 0, 1412, 'cityofkarma'),
(2004, -13950, 2877, 9, 0, 5000, 'morza'),
(2005, 10461, -9574, 22, 0, 5000, 'valleyofbetrayal'),
(2006, -661.0789794921875, -527.5889892578125, 2.0, 0, 1430, 'risendepths');

