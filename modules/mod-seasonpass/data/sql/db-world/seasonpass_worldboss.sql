-- mod-seasonpass v4: Weltboss-Rotation (Koordinaten per .gps anpassbar)
DROP TABLE IF EXISTS `seasonpass_worldboss`;
CREATE TABLE `seasonpass_worldboss` (
  `id` INT UNSIGNED NOT NULL,
  `entry` INT UNSIGNED NOT NULL,
  `map` INT UNSIGNED NOT NULL DEFAULT 0,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `o` FLOAT NOT NULL DEFAULT 0,
  `name` VARCHAR(60) NOT NULL DEFAULT '',
  `zone` VARCHAR(80) NOT NULL DEFAULT '',
  `zone_en` VARCHAR(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_worldboss` (`id`,`entry`,`map`,`x`,`y`,`z`,`o`,`name`,`zone`,`zone_en`) VALUES
(1,14890,0,-10432.0,-392.0,43.0,0.0,'Taerar','Düsterwald (Zwielichthain)','Duskwood (Twilight Grove)'),
(2,14888,0,815.0,-510.0,180.0,0.0,'Lethon','Hinterland (Seradane)','The Hinterlands (Seradane)'),
(3,14887,1,-2882.0,1930.0,60.0,0.0,'Ysondre','Feralas (Traumzweig)','Feralas (Dream Bough)'),
(4,14889,1,3050.0,-3460.0,140.0,0.0,'Emeriss','Eschental (Schattenast)','Ashenvale (Bough Shadow)'),
(5,12397,0,-11800.0,-3190.0,6.0,0.0,'Lord Kazzak','Verwüstete Lande','Blasted Lands'),
(6,6109,1,2550.0,-5670.0,100.0,0.0,'Azuregos','Azshara','Azshara');
