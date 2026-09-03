/* Add totem models for races that don't currently have shaman class
DELETE FROM `player_totem_model` WHERE `TotemID` IN (1, 2, 3, 4) AND `RaceID` IN (9, 12);
INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`) VALUES
-- Worgen (Race ID 12) - Use nature-themed totems
(1, 12, 30762), -- Fire (borrowing from Troll style for nature theme)
(2, 12, 30761), -- Earth (borrowing from Troll style for nature theme)
(3, 12, 30763), -- Water (borrowing from Troll style for nature theme)
(4, 12, 30760), -- Air (borrowing from Troll style for nature theme)

-- Goblin (Race ID 9) - Use mechanical/technological totems

(1, 9, 30754), -- Fire (borrowing from Dwarf style - similar culture)
(2, 9, 30753), -- Earth (borrowing from Dwarf style - similar culture)
(3, 9, 30755), -- Water (borrowing from Dwarf style - similar culture)
(4, 9, 30736); -- Air (borrowing from Dwarf style - similar culture)

-- Use upstream totems instead
(1, 9, 4589),
(2, 9, 4588),
(3, 9, 4587),
(4, 9, 4590); */

-- Alliance default totems is the Dwarf ones
SET @WorgenFireTotem := 30754;
SET @WorgenEarthTotem := 30753;
SET @WorgenWaterTotem := 30755;
SET @WorgenAirTotem := 30736;

-- Horde default totems is the Orc ones.
SET @GoblinFireTotem := 30758;
SET @GoblinEarthTotem := 30757;
SET @GoblinWaterTotem := 30759;
SET @GoblinAirTotem := 30756;

-- Goblin and Worgen
DELETE FROM player_totem_model WHERE RaceID IN (1,4,5,7,9,10,12,13,14);
INSERT INTO player_totem_model (TotemID, RaceID, ModelID) VALUES 
(1, 9, @GoblinFireTotem),
(2, 9, @GoblinEarthTotem),
(3, 9, @GoblinWaterTotem),
(4, 9, @GoblinAirTotem),

(1, 12, @WorgenFireTotem),
(2, 12, @WorgenEarthTotem),
(3, 12, @WorgenWaterTotem),
(4, 12, @WorgenAirTotem);
