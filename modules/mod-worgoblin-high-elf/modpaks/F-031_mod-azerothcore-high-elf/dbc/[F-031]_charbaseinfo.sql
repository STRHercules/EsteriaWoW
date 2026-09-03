/* ARAC additions */

DELETE FROM `charbaseinfo` WHERE `race` = 13 AND `class` = 7;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (13, 7); -- high elf shaman
DELETE FROM `charbaseinfo` WHERE `race` = 13 AND `class` = 11;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (13, 11); -- high elf druid
