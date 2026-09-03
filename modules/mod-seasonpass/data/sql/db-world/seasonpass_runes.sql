-- mod-seasonpass v4: 24 Runen (12 Dauerbuffs + 12 neue Fähigkeiten)
DROP TABLE IF EXISTS `seasonpass_runes`;
CREATE TABLE `seasonpass_runes` (
  `id` INT UNSIGNED NOT NULL,
  `classmask` INT UNSIGNED NOT NULL DEFAULT 0,
  `kind` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0=Aura,1=Fähigkeit',
  `spell` INT UNSIGNED NOT NULL,
  `cost` INT UNSIGNED NOT NULL DEFAULT 0,
  `name` VARCHAR(120) NOT NULL DEFAULT '',
  `name_en` VARCHAR(120) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO `seasonpass_runes` (`id`,`classmask`,`kind`,`spell`,`cost`,`name`,`name_en`) VALUES
(1,0,0,1126,500000,'Rune der Wildnis','Rune of the Wild'),
(2,0,0,1243,500000,'Rune der Seelenstärke','Rune of Fortitude'),
(3,0,0,1459,500000,'Rune der Intelligenz','Rune of Intellect'),
(4,0,0,14752,500000,'Rune des Willens','Rune of Spirit'),
(5,0,0,20217,1000000,'Rune der Könige','Rune of Kings'),
(6,0,0,19740,1000000,'Rune der Macht','Rune of Might'),
(7,0,0,19742,1000000,'Rune der Weisheit','Rune of Wisdom'),
(8,0,0,467,750000,'Rune der Dornen','Rune of Thorns'),
(9,0,0,976,750000,'Rune des Schattenschutzes','Rune of Shadow Protection'),
(10,0,0,20911,1500000,'Rune des Refugiums','Rune of Sanctuary'),
(11,0,0,19506,1500000,'Rune des Scharfschützen','Rune of Trueshot'),
(12,0,0,24932,1500000,'Rune des Rudels','Rune of the Pack'),
(13,0,1,355,1000000,'Rune des Spotts','Rune of Taunt'),
(14,0,1,25780,1000000,'Rune des rechtschaffenen Zorns','Rune of Righteous Fury'),
(15,0,1,6346,1000000,'Rune der Furchtabwehr','Rune of Fear Ward'),
(16,0,1,1953,1500000,'Rune des Blinzelns','Rune of Blink'),
(17,0,1,11305,1500000,'Rune des Sprints','Rune of Sprint'),
(18,0,1,1787,2000000,'Rune des Schleichens','Rune of Stealth'),
(19,0,1,556,1000000,'Rune des astralen Rückrufs','Rune of Astral Recall'),
(20,0,1,546,750000,'Rune des Wasserwandelns','Rune of Water Walking'),
(21,0,1,5697,750000,'Rune der Unterwasseratmung','Rune of Water Breathing'),
(22,0,1,48788,2000000,'Rune der Handauflegung','Rune of Lay on Hands'),
(23,0,1,6197,750000,'Rune des Adlerauges','Rune of Eagle Eye'),
(24,0,1,2825,2500000,'Rune des Kampfrauschs','Rune of Bloodlust');
