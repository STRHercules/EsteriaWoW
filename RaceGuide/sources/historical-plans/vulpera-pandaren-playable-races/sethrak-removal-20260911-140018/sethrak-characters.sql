
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `characters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `characters` (
  `guid` int unsigned NOT NULL DEFAULT '0' COMMENT 'Global Unique Identifier',
  `account` int unsigned NOT NULL DEFAULT '0' COMMENT 'Account Identifier',
  `name` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `race` tinyint unsigned NOT NULL DEFAULT '0',
  `class` tinyint unsigned NOT NULL DEFAULT '0',
  `gender` tinyint unsigned NOT NULL DEFAULT '0',
  `level` tinyint unsigned NOT NULL DEFAULT '0',
  `xp` int unsigned NOT NULL DEFAULT '0',
  `money` int unsigned NOT NULL DEFAULT '0',
  `skin` tinyint unsigned NOT NULL DEFAULT '0',
  `face` tinyint unsigned NOT NULL DEFAULT '0',
  `hairStyle` tinyint unsigned NOT NULL DEFAULT '0',
  `hairColor` tinyint unsigned NOT NULL DEFAULT '0',
  `facialStyle` tinyint unsigned NOT NULL DEFAULT '0',
  `bankSlots` tinyint unsigned NOT NULL DEFAULT '0',
  `restState` tinyint unsigned NOT NULL DEFAULT '0',
  `playerFlags` int unsigned NOT NULL DEFAULT '0',
  `position_x` float NOT NULL DEFAULT '0',
  `position_y` float NOT NULL DEFAULT '0',
  `position_z` float NOT NULL DEFAULT '0',
  `map` smallint unsigned NOT NULL DEFAULT '0' COMMENT 'Map Identifier',
  `instance_id` int unsigned NOT NULL DEFAULT '0',
  `instance_mode_mask` tinyint unsigned NOT NULL DEFAULT '0',
  `orientation` float NOT NULL DEFAULT '0',
  `taximask` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `online` tinyint unsigned NOT NULL DEFAULT '0',
  `cinematic` tinyint unsigned NOT NULL DEFAULT '0',
  `totaltime` int unsigned NOT NULL DEFAULT '0',
  `leveltime` int unsigned NOT NULL DEFAULT '0',
  `logout_time` int unsigned NOT NULL DEFAULT '0',
  `is_logout_resting` tinyint unsigned NOT NULL DEFAULT '0',
  `rest_bonus` float NOT NULL DEFAULT '0',
  `resettalents_cost` int unsigned NOT NULL DEFAULT '0',
  `resettalents_time` int unsigned NOT NULL DEFAULT '0',
  `trans_x` float NOT NULL DEFAULT '0',
  `trans_y` float NOT NULL DEFAULT '0',
  `trans_z` float NOT NULL DEFAULT '0',
  `trans_o` float NOT NULL DEFAULT '0',
  `transguid` int DEFAULT '0',
  `extra_flags` smallint unsigned NOT NULL DEFAULT '0',
  `stable_slots` tinyint unsigned NOT NULL DEFAULT '0',
  `at_login` smallint unsigned NOT NULL DEFAULT '0',
  `zone` smallint unsigned NOT NULL DEFAULT '0',
  `death_expire_time` int unsigned NOT NULL DEFAULT '0',
  `taxi_path` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `arenaPoints` int unsigned NOT NULL DEFAULT '0',
  `totalHonorPoints` int unsigned NOT NULL DEFAULT '0',
  `todayHonorPoints` int unsigned NOT NULL DEFAULT '0',
  `yesterdayHonorPoints` int unsigned NOT NULL DEFAULT '0',
  `totalKills` int unsigned NOT NULL DEFAULT '0',
  `todayKills` smallint unsigned NOT NULL DEFAULT '0',
  `yesterdayKills` smallint unsigned NOT NULL DEFAULT '0',
  `chosenTitle` int unsigned NOT NULL DEFAULT '0',
  `knownCurrencies` bigint unsigned NOT NULL DEFAULT '0',
  `watchedFaction` int unsigned NOT NULL DEFAULT '0',
  `drunk` tinyint unsigned NOT NULL DEFAULT '0',
  `health` int unsigned NOT NULL DEFAULT '0',
  `power1` int unsigned NOT NULL DEFAULT '0',
  `power2` int unsigned NOT NULL DEFAULT '0',
  `power3` int unsigned NOT NULL DEFAULT '0',
  `power4` int unsigned NOT NULL DEFAULT '0',
  `power5` int unsigned NOT NULL DEFAULT '0',
  `power6` int unsigned NOT NULL DEFAULT '0',
  `power7` int unsigned NOT NULL DEFAULT '0',
  `latency` int unsigned DEFAULT '0',
  `talentGroupsCount` tinyint unsigned NOT NULL DEFAULT '1',
  `activeTalentGroup` tinyint unsigned NOT NULL DEFAULT '0',
  `exploredZones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `equipmentCache` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `ammoId` int unsigned NOT NULL DEFAULT '0',
  `knownTitles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `actionBars` tinyint unsigned NOT NULL DEFAULT '0',
  `grantableLevels` tinyint unsigned NOT NULL DEFAULT '0',
  `order` tinyint DEFAULT NULL,
  `creation_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `deleteInfos_Account` int unsigned DEFAULT NULL,
  `deleteInfos_Name` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `deleteDate` int unsigned DEFAULT NULL,
  `innTriggerId` int unsigned NOT NULL,
  `extraBonusTalentCount` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`guid`),
  KEY `idx_account` (`account`),
  KEY `idx_online` (`online`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Player System';
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `characters` WRITE;
/*!40000 ALTER TABLE `characters` DISABLE KEYS */;
INSERT INTO `characters` VALUES (127,24,'Dalfond',2,1,0,1,0,0,0,0,0,0,0,0,2,0,-618.518,-4251.67,38.718,1,0,0,0,'0 0 0 4 0 0 0 0 0 0 0 0 0 0 ',0,2,0,0,1788455947,0,0,0,0,0,0,0,0,0,4,0,0,0,0,'',0,0,0,0,0,0,0,0,0,4294967295,0,70,0,0,0,100,0,0,0,0,1,0,'0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ','0 0 0 0 0 0 38 0 0 0 0 0 0 0 40 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ',0,'0 0 0 0 0 0 ',0,0,NULL,'2026-09-03 17:19:35',NULL,NULL,NULL,0,0),(129,24,'Ilucy',2,3,1,1,0,0,0,0,0,0,0,0,2,0,-618.518,-4251.67,38.718,1,0,0,0,'0 0 0 4 0 0 0 0 0 0 0 0 0 0 ',0,2,0,0,1788455947,0,0,0,0,0,0,0,0,0,4,0,0,0,0,'',0,0,0,0,0,0,0,0,0,4294967295,0,66,80,0,0,100,0,0,0,0,1,0,'0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ','0 0 0 0 0 0 148 0 0 0 0 0 0 0 129 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2101 0 0 0 0 0 0 0 ',2512,'0 0 0 0 0 0 ',0,0,NULL,'2026-09-03 17:19:35',NULL,NULL,NULL,0,0),(299,11,'Kara',15,11,1,81,0,50000,3,0,0,0,0,0,2,0,-606.683,-4273.61,37.8113,1,0,0,5.9768,'0 0 0 4 0 0 1048576 0 0 0 0 0 0 0 ',0,1,999,147,1788677559,0,0,0,0,0,0,0,0,0,0,0,0,14,0,'',0,0,0,0,0,0,0,0,0,4294967295,0,9867,7221,0,0,100,0,0,0,2,1,0,'0 0 33554432 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ','900134 0 34249 0 42985 0 38 0 48691 0 3599 0 6124 0 2117 0 3600 0 2119 0 50255 0 7339 0 42991 0 42991 0 51994 0 3661 0 0 0 0 0 900135 0 0 0 0 0 0 0 0 0 ',0,'0 0 0 0 8192 0 ',0,0,NULL,'2026-09-03 22:23:44',NULL,NULL,NULL,0,0),(300,11,'Dorbo',15,2,0,1,40,50000,5,0,0,0,0,0,1,0,-715.8,-4276.81,41.5099,1,0,0,6.06317,'0 0 0 4 0 0 0 0 0 0 0 0 0 0 ',0,1,385,385,1788900949,0,36.5915,0,0,0,0,0,0,0,0,0,0,14,1788477388,'',0,0,0,0,0,0,0,0,0,4294967295,0,78,76,0,0,100,0,0,0,2,1,0,'0 0 100663296 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ','0 0 0 0 0 0 45 0 0 0 0 0 44 0 43 0 0 0 0 0 0 0 0 0 900136 0 0 0 0 0 2361 0 0 0 0 0 900135 0 0 0 0 0 0 0 0 0 ',0,'0 0 0 0 8192 0 ',0,0,NULL,'2026-09-03 22:47:09',NULL,NULL,NULL,0,0);
/*!40000 ALTER TABLE `characters` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `character_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `character_inventory` (
  `guid` int unsigned NOT NULL DEFAULT '0' COMMENT 'Global Unique Identifier',
  `bag` int unsigned NOT NULL DEFAULT '0',
  `slot` tinyint unsigned NOT NULL DEFAULT '0',
  `item` int unsigned NOT NULL DEFAULT '0' COMMENT 'Item Global Unique Identifier',
  PRIMARY KEY (`item`),
  UNIQUE KEY `guid` (`guid`,`bag`,`slot`),
  KEY `idx_guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Player System';
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `character_inventory` WRITE;
/*!40000 ALTER TABLE `character_inventory` DISABLE KEYS */;
INSERT INTO `character_inventory` VALUES (127,0,3,1687),(127,0,7,1691),(127,0,23,1689),(127,0,24,1693),(127,0,25,1695),(129,0,3,1707),(129,0,7,1711),(129,0,19,1715),(129,0,23,1709),(129,0,24,1713),(129,0,25,1717),(129,0,26,1721),(129,1715,0,1719),(299,0,0,4072),(299,0,1,4053),(299,0,2,4045),(299,0,3,4058),(299,0,4,4047),(299,0,5,4050),(299,0,6,4041),(299,0,7,4052),(299,0,8,4048),(299,0,9,4049),(299,0,10,4054),(299,0,11,4055),(299,0,12,4057),(299,0,13,4056),(299,0,14,4046),(299,0,15,4037),(299,0,18,4073),(299,0,23,4051),(299,0,25,4043),(299,0,27,4039),(299,0,28,4074),(300,0,3,4060),(300,0,6,4064),(300,0,7,4062),(300,0,12,4071),(300,0,15,4068),(300,0,18,4070),(300,0,23,4066),(300,0,24,4069);
/*!40000 ALTER TABLE `character_inventory` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `item_instance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_instance` (
  `guid` int unsigned NOT NULL DEFAULT '0',
  `itemEntry` int unsigned DEFAULT '0',
  `owner_guid` int unsigned NOT NULL DEFAULT '0',
  `creatorGuid` int unsigned NOT NULL DEFAULT '0',
  `giftCreatorGuid` int unsigned NOT NULL DEFAULT '0',
  `count` int unsigned NOT NULL DEFAULT '1',
  `duration` int NOT NULL DEFAULT '0',
  `charges` tinytext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `flags` int unsigned DEFAULT '0',
  `enchantments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `randomPropertyId` smallint NOT NULL DEFAULT '0',
  `durability` smallint unsigned NOT NULL DEFAULT '0',
  `playedTime` int unsigned NOT NULL DEFAULT '0',
  `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`guid`),
  KEY `idx_owner_guid` (`owner_guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Item System';
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `item_instance` WRITE;
/*!40000 ALTER TABLE `item_instance` DISABLE KEYS */;
INSERT INTO `item_instance` VALUES (127,23347,11,0,0,1,0,'0 0 0 0 0 ',0,'0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ',0,20,0,''),(129,2512,11,0,0,200,0,'0 0 0 0 0 ',0,'0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ',0,0,0,''),(299,6948,23,0,0,1,0,'0 0 0 0 0 ',1,'0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ',0,0,0,'');
/*!40000 ALTER TABLE `item_instance` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `character_skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `character_skills` (
  `guid` int unsigned NOT NULL COMMENT 'Global Unique Identifier',
  `skill` smallint unsigned NOT NULL,
  `value` smallint unsigned NOT NULL,
  `max` smallint unsigned NOT NULL,
  PRIMARY KEY (`guid`,`skill`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Player System';
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `character_skills` WRITE;
/*!40000 ALTER TABLE `character_skills` DISABLE KEYS */;
INSERT INTO `character_skills` VALUES (127,26,1,5),(127,43,1,5),(127,44,1,5),(127,95,1,5),(127,109,300,300),(127,125,1,5),(127,162,1,5),(127,172,1,5),(127,183,5,5),(127,256,5,5),(127,257,5,5),(127,413,1,1),(127,414,1,1),(127,415,1,1),(127,433,1,5),(127,777,1,5),(127,778,1,5),(127,793,1,5),(129,44,1,5),(129,45,1,5),(129,50,1,5),(129,51,5,5),(129,95,1,5),(129,109,300,300),(129,125,1,5),(129,162,1,5),(129,163,5,5),(129,183,5,5),(129,414,1,1),(129,415,1,1),(129,777,1,5),(129,778,1,5),(129,793,1,5),(299,95,1,405),(299,109,300,300),(299,125,405,405),(299,134,1,405),(299,136,1,405),(299,162,1,405),(299,183,405,405),(299,414,1,1),(299,415,1,1),(299,573,405,405),(299,574,405,405),(299,777,1,405),(299,778,1,405),(299,793,405,405),(300,54,1,5),(300,95,5,5),(300,109,300,300),(300,125,5,5),(300,160,2,5),(300,162,1,5),(300,183,5,5),(300,184,1,5),(300,267,5,5),(300,413,1,1),(300,414,1,1),(300,415,1,1),(300,594,5,5),(300,777,1,5),(300,778,1,5);
/*!40000 ALTER TABLE `character_skills` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `character_reputation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `character_reputation` (
  `guid` int unsigned NOT NULL DEFAULT '0' COMMENT 'Global Unique Identifier',
  `faction` smallint unsigned NOT NULL DEFAULT '0',
  `standing` int NOT NULL DEFAULT '0',
  `flags` smallint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guid`,`faction`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Player System';
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `character_reputation` WRITE;
/*!40000 ALTER TABLE `character_reputation` DISABLE KEYS */;
INSERT INTO `character_reputation` VALUES (299,21,0,0),(299,46,0,0),(299,47,0,0),(299,54,0,0),(299,59,0,0),(299,67,0,0),(299,68,0,0),(299,69,0,0),(299,70,0,0),(299,72,0,0),(299,76,0,0),(299,81,0,0),(299,83,0,0),(299,86,0,0),(299,87,0,0),(299,92,0,0),(299,93,0,0),(299,169,0,0),(299,270,0,0),(299,289,0,0),(299,349,0,0),(299,369,0,0),(299,469,0,0),(299,470,0,0),(299,471,0,0),(299,509,0,0),(299,510,0,0),(299,529,0,0),(299,530,0,0),(299,549,0,0),(299,550,0,0),(299,551,0,0),(299,569,0,0),(299,570,0,0),(299,571,0,0),(299,574,0,0),(299,576,0,0),(299,577,0,0),(299,589,0,0),(299,609,0,0),(299,729,0,0),(299,730,0,0),(299,749,0,0),(299,809,0,0),(299,889,0,0),(299,890,0,0),(299,891,0,0),(299,892,0,0),(299,909,0,0),(299,910,0,0),(299,911,0,0),(299,922,0,0),(299,930,0,0),(299,932,0,0),(299,933,0,0),(299,934,0,0),(299,935,0,0),(299,936,0,0),(299,941,0,0),(299,942,0,0),(299,946,0,0),(299,947,0,0),(299,948,0,8),(299,949,0,24),(299,952,0,0),(299,967,0,0),(299,970,0,0),(299,978,0,0),(299,980,0,0),(299,989,0,0),(299,990,0,0),(299,1005,0,4),(299,1011,0,16),(299,1012,0,0),(299,1015,0,0),(299,1031,0,0),(299,1037,0,0),(299,1038,0,0),(299,1050,0,0),(299,1052,0,0),(299,1064,0,0),(299,1067,0,0),(299,1068,0,0),(299,1073,0,0),(299,1077,0,16),(299,1082,0,0),(299,1085,0,0),(299,1090,0,0),(299,1091,0,0),(299,1094,0,0),(299,1097,0,0),(299,1098,0,16),(299,1104,0,0),(299,1105,0,0),(299,1106,0,16),(299,1117,0,0),(299,1118,0,0),(299,1119,0,0),(299,1124,0,0),(299,1126,0,0),(299,1136,0,4),(299,1137,0,4),(299,1154,0,4),(299,1155,0,4),(299,1156,0,16),(300,21,0,0),(300,46,0,0),(300,47,0,0),(300,54,0,0),(300,59,0,0),(300,67,0,0),(300,68,25,1),(300,69,0,0),(300,70,0,0),(300,72,0,0),(300,76,63,1),(300,81,25,1),(300,83,0,0),(300,86,0,0),(300,87,0,0),(300,92,0,0),(300,93,0,0),(300,169,0,0),(300,270,0,0),(300,289,0,0),(300,349,0,0),(300,369,0,0),(300,469,0,0),(300,470,0,0),(300,471,0,0),(300,509,0,0),(300,510,0,0),(300,529,0,0),(300,530,62,1),(300,549,0,0),(300,550,0,0),(300,551,0,0),(300,569,0,0),(300,570,0,0),(300,571,0,0),(300,574,0,0),(300,576,0,0),(300,577,0,0),(300,589,0,0),(300,609,0,0),(300,729,0,0),(300,730,0,0),(300,749,0,0),(300,809,0,0),(300,889,0,0),(300,890,0,0),(300,891,0,0),(300,892,0,0),(300,909,0,0),(300,910,0,0),(300,911,25,1),(300,922,0,0),(300,930,0,0),(300,932,0,0),(300,933,0,0),(300,934,0,0),(300,935,0,0),(300,936,0,0),(300,941,0,0),(300,942,0,0),(300,946,0,0),(300,947,0,0),(300,948,0,8),(300,949,0,24),(300,952,0,0),(300,967,0,0),(300,970,0,0),(300,978,0,0),(300,980,0,0),(300,989,0,0),(300,990,0,0),(300,1005,0,4),(300,1011,0,16),(300,1012,0,0),(300,1015,0,0),(300,1031,0,0),(300,1037,0,0),(300,1038,0,0),(300,1050,0,0),(300,1052,0,0),(300,1064,0,0),(300,1067,0,0),(300,1068,0,0),(300,1073,0,0),(300,1077,0,16),(300,1082,0,0),(300,1085,0,0),(300,1090,0,0),(300,1091,0,0),(300,1094,0,0),(300,1097,0,0),(300,1098,0,16),(300,1104,0,0),(300,1105,0,0),(300,1106,0,16),(300,1117,0,0),(300,1118,0,0),(300,1119,0,0),(300,1124,0,0),(300,1126,0,0),(300,1136,0,4),(300,1137,0,4),(300,1154,0,4),(300,1155,0,4),(300,1156,0,16);
/*!40000 ALTER TABLE `character_reputation` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `character_spell`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `character_spell` (
  `guid` int unsigned NOT NULL DEFAULT '0' COMMENT 'Global Unique Identifier',
  `spell` int unsigned NOT NULL DEFAULT '0' COMMENT 'Spell Identifier',
  `specMask` tinyint unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`guid`,`spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Player System';
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `character_spell` WRITE;
/*!40000 ALTER TABLE `character_spell` DISABLE KEYS */;
INSERT INTO `character_spell` VALUES (127,669,255),(129,669,255),(299,669,255),(300,472,255),(300,669,255);
/*!40000 ALTER TABLE `character_spell` ENABLE KEYS */;
UNLOCK TABLES;
DROP TABLE IF EXISTS `mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mail` (
  `id` int unsigned NOT NULL DEFAULT '0' COMMENT 'Identifier',
  `messageType` tinyint unsigned NOT NULL DEFAULT '0',
  `stationery` tinyint NOT NULL DEFAULT '41',
  `mailTemplateId` smallint unsigned NOT NULL DEFAULT '0',
  `sender` int unsigned NOT NULL DEFAULT '0' COMMENT 'Character Global Unique Identifier',
  `receiver` int unsigned NOT NULL DEFAULT '0' COMMENT 'Character Global Unique Identifier',
  `subject` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `body` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `has_items` tinyint unsigned NOT NULL DEFAULT '0',
  `expire_time` int unsigned NOT NULL DEFAULT '0',
  `deliver_time` int unsigned NOT NULL DEFAULT '0',
  `money` int unsigned NOT NULL DEFAULT '0',
  `cod` int unsigned NOT NULL DEFAULT '0',
  `checked` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_receiver` (`receiver`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Mail System';
/*!40101 SET character_set_client = @saved_cs_client */;

