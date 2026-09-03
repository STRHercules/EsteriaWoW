-- mod-seasonpass v4: Teleport-Ziele der Traumpfadhüterin
DROP TABLE IF EXISTS `seasonpass_teleports`;
CREATE TABLE `seasonpass_teleports` (
  `id` INT UNSIGNED NOT NULL,
  `name` VARCHAR(60) NOT NULL DEFAULT '',
  `name_en` VARCHAR(60) NOT NULL DEFAULT '',
  `map` INT UNSIGNED NOT NULL DEFAULT 0,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `o` FLOAT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_teleports` (`id`,`name`,`name_en`,`map`,`x`,`y`,`z`,`o`) VALUES
(1,'Sturmwind','Stormwind',0,-8833.4,628.6,94.0,1.06),
(2,'Eisenschmiede','Ironforge',0,-4981.3,-881.5,501.7,5.40),
(3,'Darnassus','Darnassus',1,9947.5,2482.7,1316.2,0.00),
(4,'Die Exodar','The Exodar',530,-3965.7,-11653.6,-138.8,0.85),
(5,'Orgrimmar','Orgrimmar',1,1601.1,-4378.7,10.0,2.14),
(6,'Unterstadt','Undercity',0,1633.8,240.2,-43.1,6.26),
(7,'Donnerfels','Thunder Bluff',1,-1277.4,124.8,131.3,5.22),
(8,'Silbermond','Silvermoon',530,9738.3,-7454.2,13.6,0.04),
(9,'Shattrath','Shattrath',530,-1887.6,5359.1,-12.4,4.40),
(10,'Dalaran','Dalaran',571,5809.6,448.9,658.8,5.26),
(11,'Gadgetzan','Gadgetzan',1,-7176.6,-3785.3,8.4,5.80),
(12,'Beutebucht','Booty Bay',0,-14297.2,518.0,8.8,3.90);
