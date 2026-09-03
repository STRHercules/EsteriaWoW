-- mod-seasonpass v4: Wochen-Mutatoren (Open-World-Affixe)
DROP TABLE IF EXISTS `seasonpass_mutators`;
CREATE TABLE `seasonpass_mutators` (
  `id` INT UNSIGNED NOT NULL,
  `kind` TINYINT UNSIGNED NOT NULL,
  `value` INT UNSIGNED NOT NULL DEFAULT 200 COMMENT 'Prozent',
  `name` VARCHAR(120) NOT NULL DEFAULT '',
  `name_en` VARCHAR(120) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_mutators` (`id`,`kind`,`value`,`name`,`name_en`) VALUES
(1,0,200,'Woche der Gelehrten: Questpunkte x2','Week of Scholars: quest points x2'),
(2,1,200,'Woche der Riesen: Elitepunkte x2','Week of Giants: elite points x2'),
(3,2,200,'Woche der Jäger: Rare-Punkte x2','Week of Hunters: rare points x2'),
(4,3,200,'Woche des Blutes: PvP- und Duellpunkte x2','Week of Blood: PvP and duel points x2'),
(5,4,125,'Woche der Weisheit: +25% Erfahrung','Week of Wisdom: +25% experience'),
(6,5,200,'Kistenwoche: doppelte Kistenchance','Chest Week: double chest chance'),
(7,6,200,'Woche der Pflicht: Wochenziel-Punkte x2','Week of Duty: weekly goal points x2'),
(8,7,200,'Woche der Wanderer: Entdeckungspunkte x2','Week of Wanderers: discovery points x2');
