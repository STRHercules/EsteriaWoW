-- mod-seasonpass v4: Zonen-Events
DROP TABLE IF EXISTS `seasonpass_zones`;
CREATE TABLE `seasonpass_zones` (
  `id` INT UNSIGNED NOT NULL,
  `zone` INT UNSIGNED NOT NULL,
  `name` VARCHAR(80) NOT NULL DEFAULT '',
  `name_en` VARCHAR(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_zones` (`id`,`zone`,`name`,`name_en`) VALUES
(1,33,'Schlingendorntal (Blutmond!)','Stranglethorn Vale (Blood Moon!)'),
(2,331,'Eschental (Schlacht um Eschental!)','Ashenvale (Battle for Ashenvale!)'),
(3,40,'Westfall','Westfall'),
(4,267,'Vorgebirge von Hügelsbrunn','Hillsbrad Foothills'),
(5,490,'Krater von Un''Goro','Un''Goro Crater'),
(6,618,'Winterquell','Winterspring'),
(7,3,'Ödland','Badlands'),
(8,47,'Hinterland','The Hinterlands'),
(9,400,'Tausend Nadeln','Thousand Needles'),
(10,139,'Östliche Pestländer','Eastern Plaguelands'),
(11,357,'Feralas','Feralas'),
(12,65,'Drachenöde','Dragonblight');
