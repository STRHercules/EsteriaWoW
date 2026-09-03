SET @Goblin           =    9;
SET @Worgen           =   12;
SET @Warrior          =    1;
SET @Paladin          =    2;
SET @Hunter           =    3;
SET @Rogue            =    4;
SET @Priest           =    5;
SET @DeathKnight      =    6;
SET @Shaman           =    7;
SET @Mage             =    8;
SET @Warlock          =    9;
SET @Druid            =   11;
SET @Kalimdor         =    1;
SET @Durotar          =   14;
SET @Teldrassil       =  141;
SET @Northrend        =  609;
SET @ScarletEnclave   = 4298;
INSERT IGNORE INTO `playercreateinfo` VALUES
/* Goblin starting zone (Durotar) */
(@Goblin, @Warrior, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Warrior
(@Goblin, @Hunter, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Hunter
(@Goblin, @Rogue, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Rogue
(@Goblin, @Priest, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Priest
(@Goblin, @DeathKnight, @Northrend, @ScarletEnclave, 2358.44, -5666.9, 426.023, 3.65997), -- Goblin Death Knight
(@Goblin, @Shaman, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Shaman
(@Goblin, @Mage, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Mage
(@Goblin, @Warlock, @Kalimdor, @Durotar, -618.518, -4251.67, 38.718, 0), -- Goblin Warlock

/* Worgen starting zone (Teldrassil) */
(@Worgen, @Warrior, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632), -- Worgen Warrior
(@Worgen, @Hunter, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632), -- Worgen Hunter
(@Worgen, @Rogue, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632), -- Worgen Rogue
(@Worgen, @Priest, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632), -- Worgen Priest
(@Worgen, @DeathKnight, @Northrend, @ScarletEnclave, 2358.44, -5666.9, 426.023, 3.65997), -- Worgen Death Knight
(@Worgen, @Mage, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632), -- Worgen Mage
(@Worgen, @Warlock, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632), -- Worgen Warlock
(@Worgen, @Druid, @Kalimdor, @Teldrassil, 10311.3, 832.463, 1326.41, 5.69632); -- Worgen Druid
