SET @HighElf          =   13;
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
SET @EasternKingdoms  =    0;
SET @ElwynnForest     =   12;
SET @Northrend        =  609;
SET @ScarletEnclave   = 4298;
INSERT IGNORE INTO `playercreateinfo` VALUES
/* High Elf starting zone (Elwynn Forest) */
(@HighElf, @Warrior, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Warrior
(@HighElf, @Paladin, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Paladin
(@HighElf, @Hunter, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Hunter
(@HighElf, @Rogue, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Rogue
(@HighElf, @Priest, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Priest
(@HighElf, @DeathKnight, @Northrend, @ScarletEnclave, 2358.44, -5666.9, 426.023, 3.65997), -- High Elf Death Knight
(@HighElf, @Shaman, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Shaman (ARAC)
(@HighElf, @Mage, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Mage
(@HighElf, @Warlock, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0), -- High Elf Warlock
(@HighElf, @Druid, @EasternKingdoms, @ElwynnForest, -8949.95, -132.493, 83.5312, 0); -- High Elf Druid (ARAC)
