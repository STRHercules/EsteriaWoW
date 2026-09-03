-- mod-seasonpass v4: Kopfgeld des Tages
DROP TABLE IF EXISTS `seasonpass_bounty`;
CREATE TABLE `seasonpass_bounty` (
  `id` INT UNSIGNED NOT NULL,
  `entry` INT UNSIGNED NOT NULL,
  `points` INT UNSIGNED NOT NULL DEFAULT 150,
  `name` VARCHAR(80) NOT NULL DEFAULT '',
  `name_en` VARCHAR(80) NOT NULL DEFAULT '',
  `zone` VARCHAR(60) NOT NULL DEFAULT '',
  `zone_en` VARCHAR(60) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_bounty` (`id`,`entry`,`points`,`name`,`name_en`,`zone`,`zone_en`) VALUES
(1,448,150,'Hogger','Hogger','Elwynn','Elwynn Forest'),
(2,522,150,'Mor''Ladim','Mor''Ladim','Düsterwald','Duskwood'),
(3,5828,150,'Humar der Stolzherr','Humar the Pridelord','Brachland','The Barrens'),
(4,5827,150,'Der Rechen','The Rake','Mulgore','Mulgore'),
(5,6584,200,'König Mosh','King Mosh','Un''Goro','Un''Goro Crater'),
(6,3581,150,'Kanalkrokilisk','Sewer Beast','Sturmwind','Stormwind'),
(7,7846,250,'Teremus der Verschlinger','Teremus the Devourer','Verwüstete Lande','Blasted Lands'),
(8,14445,200,'Riesengrizzly','Giant Grizzly','Dun Morogh','Dun Morogh');
