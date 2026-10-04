-- Move the nine ported races out of the 900xx player display-id band.
--
-- AzerothCore keeps a player's display id in a uint16 (`PlayerInfo::displayId_m/f`,
-- src/server/game/Entities/Player/Player.h) while `ChrRaces` itself is uint32, so 90004
-- wrapped to 24468 and a Nightborne was drawn with Creature\LasherOrchid\LasherOrchid.mdx
-- (Zandalari 90014 -> 24478 -> Creature\Lasher\Lasher.mdx). 60000-60007 already belong to
-- Sethrak/Broken/Pandaren/Vulpera, so the ported races take the free 60008-60025 slots.
--
-- Idempotent: a display row only moves while its old id still exists.

DROP TEMPORARY TABLE IF EXISTS `tmp_race_display_map`;
CREATE TEMPORARY TABLE `tmp_race_display_map` (
    `OldID` INT NOT NULL,
    `NewID` INT NOT NULL,
    PRIMARY KEY (`OldID`),
    UNIQUE KEY `NewID` (`NewID`)
);
INSERT INTO `tmp_race_display_map` (`OldID`, `NewID`) VALUES
(90002, 60008), (90003, 60009),
(90004, 60010), (90005, 60011),
(90008, 60012), (90009, 60013),
(90012, 60014), (90013, 60015),
(90014, 60016), (90015, 60017),
(90016, 60018), (90017, 60019),
(90022, 60020), (90023, 60021),
(90024, 60022), (90025, 60023),
(90026, 60024), (90027, 60025);

DELETE d
    FROM `creaturedisplayinfo_dbc` AS d
    JOIN `tmp_race_display_map` AS m ON d.`ID` = m.`NewID`
    JOIN `creaturedisplayinfo_dbc` AS s ON s.`ID` = m.`OldID`;

UPDATE `creaturedisplayinfo_dbc` AS d
    JOIN `tmp_race_display_map` AS m ON d.`ID` = m.`OldID`
    SET d.`ID` = m.`NewID`;

DROP TEMPORARY TABLE IF EXISTS `tmp_race_display_map`;

UPDATE `chrraces_dbc` SET
    `MaleDisplayId` = CASE `ID`
        WHEN 16 THEN 60008 WHEN 17 THEN 60010 WHEN 19 THEN 60012
        WHEN 21 THEN 60014 WHEN 22 THEN 60016 WHEN 23 THEN 60018
        WHEN 28 THEN 60020 WHEN 29 THEN 60022 WHEN 30 THEN 60024 END,
    `FemaleDisplayId` = CASE `ID`
        WHEN 16 THEN 60009 WHEN 17 THEN 60011 WHEN 19 THEN 60013
        WHEN 21 THEN 60015 WHEN 22 THEN 60017 WHEN 23 THEN 60019
        WHEN 28 THEN 60021 WHEN 29 THEN 60023 WHEN 30 THEN 60025 END
WHERE `ID` IN (16, 17, 19, 21, 22, 23, 28, 29, 30);
