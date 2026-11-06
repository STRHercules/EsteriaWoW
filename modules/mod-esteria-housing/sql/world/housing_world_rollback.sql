-- Undoes housing_world.sql. Map 35 has no map_dbc/instance_template rows in stock acore_world, so deleting them
-- restores Map.dbc's own row (type 0, not instanced).
DELETE FROM `map_dbc` WHERE `ID` = 35;
DELETE FROM `instance_template` WHERE `map` = 35;
DELETE FROM `creature` WHERE `id` = 9500100;
DELETE FROM `creature_template_model` WHERE `CreatureID` = 9500100;
DELETE FROM `creature_template` WHERE `entry` = 9500100;
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9500000 AND 9500399;
DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN 60000 AND 60399;
DROP TABLE IF EXISTS `housing_room_piece`;
DROP TABLE IF EXISTS `housing_room_kit`;
DROP TABLE IF EXISTS `housing_room_kind`;
DROP TABLE IF EXISTS `housing_room_template`;
DROP TABLE IF EXISTS `housing_decor_catalog`;
