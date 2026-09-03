SET @Goblin           =    9;
SET @Worgen           =   12;
SET @Paladin          =    2;
SET @Shaman           =    7;
SET @Druid            =   11;
SET @Kalimdor         =    1;
SET @Durotar          =   14;
SET @Teldrassil       =  141;
INSERT IGNORE INTO `playercreateinfo` VALUES
/* Goblin starting zone (Durotar) */
(@Goblin, @Paladin, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Paladin (ARAC)
(@Goblin, @Druid, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Druid (ARAC)

/* Worgen starting zone (Teldrassil) */
(@Worgen, @Paladin, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632), -- Worgen Paladin (ARAC)
(@Worgen, @Shaman, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632); -- Worgen Shaman (ARAC)
