-- mod-seasonpass v4: Dungeon der Woche
DROP TABLE IF EXISTS `seasonpass_dungeons`;
CREATE TABLE `seasonpass_dungeons` (
  `id` INT UNSIGNED NOT NULL,
  `map` INT UNSIGNED NOT NULL,
  `points` INT UNSIGNED NOT NULL DEFAULT 300,
  `name` VARCHAR(80) NOT NULL DEFAULT '',
  `name_en` VARCHAR(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_dungeons` (`id`,`map`,`points`,`name`,`name_en`) VALUES
(1,389,300,'Der Flammenschlund','Ragefire Chasm'),
(2,36,300,'Die Todesminen','The Deadmines'),
(3,43,300,'Die Höhlen des Wehklagens','Wailing Caverns'),
(4,33,300,'Burg Schattenfang','Shadowfang Keep'),
(5,48,300,'Tiefschwarze Grotte','Blackfathom Deeps'),
(6,90,300,'Gnomeregan','Gnomeregan'),
(7,189,300,'Das Scharlachrote Kloster','Scarlet Monastery'),
(8,209,300,'Zul''Farrak','Zul''Farrak'),
(9,109,350,'Der Versunkene Tempel','The Temple of Atal''Hakkar'),
(10,230,350,'Schwarzfelstiefen','Blackrock Depths'),
(11,329,400,'Stratholme','Stratholme'),
(12,289,400,'Scholomance','Scholomance');
