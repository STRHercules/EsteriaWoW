-- mod-seasonpass v4: Verlorene Orte (Entdeckungs-System)
DROP TABLE IF EXISTS `seasonpass_discoveries`;
CREATE TABLE `seasonpass_discoveries` (
  `id` INT UNSIGNED NOT NULL,
  `zone` INT UNSIGNED NOT NULL,
  `points` INT UNSIGNED NOT NULL DEFAULT 25,
  `name` VARCHAR(80) NOT NULL DEFAULT '',
  `name_en` VARCHAR(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_discoveries` (`id`,`zone`,`points`,`name`,`name_en`) VALUES
(1,41,25,'Gebirgspass der Totenwinde','Deadwind Pass'),
(2,618,25,'Winterquell','Winterspring'),
(3,1377,25,'Silithus','Silithus'),
(4,490,25,'Krater von Un''Goro','Un''Goro Crater'),
(5,361,25,'Teufelswald','Felwood'),
(6,16,25,'Azshara','Azshara'),
(7,493,25,'Moonglade','Moonglade'),
(8,47,25,'Hinterland','The Hinterlands'),
(9,357,25,'Feralas','Feralas'),
(10,4,25,'Verwüstete Lande','Blasted Lands'),
(11,51,25,'Sengende Schlucht','Searing Gorge'),
(12,46,25,'Brennende Steppe','Burning Steppes'),
(13,3,25,'Ödland','Badlands'),
(14,8,25,'Sümpfe des Elends','Swamp of Sorrows'),
(15,139,25,'Östliche Pestländer','Eastern Plaguelands'),
(16,28,25,'Westliche Pestländer','Western Plaguelands'),
(17,440,25,'Tanaris','Tanaris'),
(18,400,25,'Tausend Nadeln','Thousand Needles');
