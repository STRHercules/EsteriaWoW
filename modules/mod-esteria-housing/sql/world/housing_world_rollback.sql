-- Undoes housing_world.sql. Map 35 has no map_dbc/instance_template rows in stock acore_world, so deleting them
-- restores Map.dbc's own row (type 0, not instanced).
DELETE FROM `map_dbc` WHERE `ID` = 35;
DELETE FROM `map_dbc` WHERE `ID` IN (2783, 2735);
DELETE FROM `areatable_dbc` WHERE `ID` IN (16105, 16300);
DELETE FROM `instance_template` WHERE `map` = 35;
DELETE FROM `creature` WHERE `id` = 9500100;
DELETE FROM `creature_template_model` WHERE `CreatureID` = 9500100;
DELETE FROM `creature_template` WHERE `entry` = 9500100;
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9500000 AND 9500399;
DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN 60000 AND 60399;
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9501000 AND 9505999;
DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN 61000 AND 65999;
DELETE FROM `gameobject` WHERE `id` BETWEEN 9501000 AND 9505999; -- outdoor decor and swapped house parts
DELETE FROM `gameobject` WHERE `id` BETWEEN 9500000 AND 9500399; -- cornerstones and saved house exteriors
DROP TABLE IF EXISTS `housing_plot`;
DROP TABLE IF EXISTS `housing_exterior_piece`;
DROP TABLE IF EXISTS `housing_exterior_style`;
DROP TABLE IF EXISTS `housing_exterior_fixture`;
DROP TABLE IF EXISTS `housing_exterior_fixture_hook`;
DROP TABLE IF EXISTS `housing_room_piece`;
DROP TABLE IF EXISTS `housing_room_kit`;
DROP TABLE IF EXISTS `housing_room_kit_theme`;
DROP TABLE IF EXISTS `housing_room_theme`;
DROP TABLE IF EXISTS `housing_room_stairs`;
DROP TABLE IF EXISTS `housing_room_kind`;
DROP TABLE IF EXISTS `housing_room_template`;
DROP TABLE IF EXISTS `housing_decor_catalog`;
