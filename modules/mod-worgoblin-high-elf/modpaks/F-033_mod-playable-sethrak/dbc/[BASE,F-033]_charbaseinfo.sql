-- charbaseinfo: 5 inserts, 0 updates, 0 deletes

-- New entries
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Warrior;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Warrior); -- sethrak warrior
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Hunter;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Hunter); -- sethrak hunter
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Shaman;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Shaman); -- sethrak shaman
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Mage;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Mage); -- sethrak mage
DELETE FROM `charbaseinfo` WHERE `race` = @Sethrak AND `class` = @Warlock;
INSERT INTO `charbaseinfo` (`race`, `class`) VALUES (@Sethrak, @Warlock); -- sethrak warlock
