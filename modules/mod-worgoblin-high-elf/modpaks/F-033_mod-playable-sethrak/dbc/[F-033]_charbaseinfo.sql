-- ARAC additions

DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Paladin;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Paladin); -- sethrak paladin
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Rogue;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Rogue); -- sethrak rogue
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Priest;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Priest); -- sethrak priest
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @DeathKnight;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @DeathKnight); -- sethrak death knight
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Druid;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Druid); -- sethrak druid
