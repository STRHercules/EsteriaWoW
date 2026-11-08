-- One-time, only while the first shop tables hold no stock or sales (checked at deploy). The shop tables are then recreated
-- by the commerce section of housing_characters.sql.
DROP TABLE IF EXISTS `housing_service`;
DROP TABLE IF EXISTS `housing_shop_sale`;
DROP TABLE IF EXISTS `housing_shop_listing`;
DROP TABLE IF EXISTS `housing_shop`;
