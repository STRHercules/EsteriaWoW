-- mod-seasonpass v4: 20 Saison-Erfolge
DROP TABLE IF EXISTS `seasonpass_achievements`;
CREATE TABLE `seasonpass_achievements` (
  `id` INT UNSIGNED NOT NULL,
  `kind` TINYINT UNSIGNED NOT NULL,
  `goal` INT UNSIGNED NOT NULL DEFAULT 1,
  `points` INT UNSIGNED NOT NULL DEFAULT 100,
  `name` VARCHAR(120) NOT NULL DEFAULT '',
  `name_en` VARCHAR(120) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_achievements` (`id`,`kind`,`goal`,`points`,`name`,`name_en`) VALUES
(1,7,10,100,'Der Anfang: Erreiche Stufe 10','The Beginning: Reach tier 10'),
(2,7,25,200,'Viertelmeister: Erreiche Stufe 25','Quarter Master: Reach tier 25'),
(3,7,50,300,'Halbzeitheld: Erreiche Stufe 50','Halftime Hero: Reach tier 50'),
(4,7,75,400,'Dranbleiber: Erreiche Stufe 75','Persister: Reach tier 75'),
(5,7,100,500,'Vollender: Erreiche Stufe 100','Completionist: Reach tier 100'),
(6,0,1,150,'Alptraumtaufe: Besiege 1 Saison-Weltboss','Nightmare Baptism: Defeat 1 season world boss'),
(7,0,10,400,'Drachenschreck: Besiege 10 Saison-Weltbosse','Dragon Terror: Defeat 10 season world bosses'),
(8,0,25,800,'Weltenretter: Besiege 25 Saison-Weltbosse','World Savior: Defeat 25 season world bosses'),
(9,1,1,100,'Steckbrief: Erlege 1 Kopfgeld','Wanted: Claim 1 bounty'),
(10,1,10,400,'Kopfgeldkönig: Erlege 10 Kopfgelder','Bounty King: Claim 10 bounties'),
(11,2,3,100,'Runenlehrling: Graviere 3 Runen','Rune Apprentice: Engrave 3 runes'),
(12,2,10,300,'Runenmeister: Graviere 10 Runen','Rune Master: Engrave 10 runes'),
(13,3,10,200,'Wochenheld: Schließe 10 Wochenziele ab','Weekly Hero: Complete 10 weekly goals'),
(14,3,50,600,'Wochenlegende: Schließe 50 Wochenziele ab','Weekly Legend: Complete 50 weekly goals'),
(15,4,25,200,'Duellkönig: Gewinne 25 Duelle','Duel King: Win 25 duels'),
(16,5,25,300,'Raritätenjäger: Besiege 25 seltene Gegner','Rarity Hunter: Slay 25 rare enemies'),
(17,6,5,300,'Dungeonwanderer: 5x Dungeon der Woche','Dungeon Wanderer: 5x dungeon of the week'),
(18,8,1,500,'Wiedergänger: Erreiche Prestige 1','Revenant: Reach prestige 1'),
(19,9,7,200,'Stammgast: 7 Login-Tage in Folge','Regular: 7 login days in a row'),
(20,10,18,500,'Entdecker Azeroths: Finde alle verlorenen Orte','Explorer of Azeroth: Find all lost places'),
(21,12,10,200,'Lieferant: Erfülle 10 Versorgungsaufträge','Supplier: Complete 10 supply runs'),
(22,12,50,600,'Handelsprinz: Erfülle 50 Versorgungsaufträge','Trade Prince: Complete 50 supply runs'),
(23,13,10,200,'Kistenknacker: Öffne 10 Traumkisten','Chest Cracker: Open 10 dream chests'),
(24,13,50,600,'Traumsammler: Öffne 50 Traumkisten','Dream Hoarder: Open 50 dream chests');
