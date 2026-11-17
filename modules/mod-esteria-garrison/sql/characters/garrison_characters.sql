-- UWoW character garrison tables (sql/uwow 2015_09_29_01, 2015_09_30_00, 2015_10_22_01, 2015_12_19_03_character_garrison_shipment).
-- Apply to the characters database. Safe to re-run: only creates missing tables, never drops player data.


CREATE TABLE IF NOT EXISTS `character_garrison` (
  `guid` int unsigned NOT NULL,
  `siteLevelId` int unsigned NOT NULL DEFAULT '0',
  `followerActivationsRemainingToday` int unsigned NOT NULL DEFAULT '0',
  `lastResTaken` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `character_garrison_blueprints` (
  `guid` int unsigned NOT NULL,
  `buildingId` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guid`, `buildingId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `character_garrison_buildings` (
  `guid` int unsigned NOT NULL,
  `plotInstanceId` int unsigned NOT NULL DEFAULT '0',
  `buildingId` int unsigned NOT NULL DEFAULT '0',
  `timeBuilt` bigint unsigned NOT NULL,
  `active` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guid`, `plotInstanceId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `character_garrison_followers` (
  `dbId` bigint unsigned NOT NULL,
  `guid` int unsigned NOT NULL,
  `followerId` int unsigned NOT NULL,
  `quality` int unsigned NOT NULL DEFAULT '2',
  `level` int unsigned NOT NULL DEFAULT '90',
  `itemLevelWeapon` int unsigned NOT NULL DEFAULT '600',
  `itemLevelArmor` int unsigned NOT NULL DEFAULT '600',
  `xp` int unsigned NOT NULL DEFAULT '0',
  `currentBuilding` int unsigned NOT NULL DEFAULT '0',
  `currentMission` int unsigned NOT NULL DEFAULT '0',
  `status` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`dbId`),
  UNIQUE KEY `idx_guid_id` (`guid`, `followerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `character_garrison_follower_abilities` (
  `dbId` bigint unsigned NOT NULL,
  `abilityId` int unsigned NOT NULL,
  `slot` tinyint unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`dbId`, `abilityId`, `slot`),
  CONSTRAINT `fk_foll_dbid` FOREIGN KEY (`dbId`) REFERENCES `character_garrison_followers` (`dbId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `character_garrison_missions` (
  `dbId` bigint unsigned NOT NULL,
  `guid` int unsigned NOT NULL,
  `missionRecID` int unsigned NOT NULL DEFAULT '0',
  `offerTime` int unsigned NOT NULL DEFAULT '0',
  `offerDuration` int unsigned NOT NULL DEFAULT '0',
  `startTime` int unsigned NOT NULL DEFAULT '0',
  `travelDuration` int unsigned NOT NULL DEFAULT '0',
  `missionDuration` int unsigned NOT NULL DEFAULT '0',
  `missionState` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`dbId`),
  UNIQUE KEY `idx_guid_id` (`guid`, `missionRecID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `character_garrison_shipment` (
  `dbId` bigint NOT NULL,
  `guid` int unsigned NOT NULL,
  `shipmentID` smallint NOT NULL,
  `orderTime` int NOT NULL,
  PRIMARY KEY (`dbId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Player::_currencyStorage for the garrison currencies (824 Garrison Resources); 3.3.5 characters have no currency table
CREATE TABLE IF NOT EXISTS `character_garrison_currency` (
  `guid` int unsigned NOT NULL,
  `currency` int unsigned NOT NULL,
  `count` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`guid`, `currency`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
