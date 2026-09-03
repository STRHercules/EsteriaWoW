-- Horde default totems is the Orc ones.
SET @SethrakFireTotem := 30758;
SET @SethrakEarthTotem := 30757;
SET @SethrakWaterTotem := 30759;
SET @SethrakAirTotem := 30756;

-- Sethrak
DELETE FROM player_totem_model WHERE RaceID IN (15);
INSERT INTO player_totem_model (TotemID, RaceID, ModelID) VALUES
(1, @Sethrak, @SethrakFireTotem),
(2, @Sethrak, @SethrakEarthTotem),
(3, @Sethrak, @SethrakWaterTotem),
(4, @Sethrak, @SethrakAirTotem);
