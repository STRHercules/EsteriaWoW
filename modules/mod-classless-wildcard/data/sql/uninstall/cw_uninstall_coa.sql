-- mod-classless-wildcard: remove the imported Conquest of Azeroth kits.
-- NOT auto-applied -- run by hand, with the worldserver STOPPED. Deletes only
-- the rows cw_spells_coa.sql owns; on the client, delete
-- Data\Patch-ZZZZZZZZZZZZZZZZZZZZZZZZCoA.MPQ.

DELETE FROM `spell_ranks` WHERE `first_spell_id` IN (SELECT `first_spell` FROM `cw_coa_entries` WHERE `kind` = 0);
DELETE FROM `talent_dbc` WHERE `ID` BETWEEN 100000 AND 199999;
DELETE FROM `talenttab_dbc` WHERE `ID` BETWEEN 2000 AND 2330;
-- spell_dbc rows are listed in cw_spells_coa.sql's own DELETE, and the script,
-- proc and bonus rows in cw_coa_scripts.sql's DELETEs; run those lines too.
-- The summoned creatures and gameobjects are the rows listed by the DELETE lines of
-- cw_coa_creatures.sql (creature_template and its model, addon, spell and equipment
-- rows, gameobject_template) and of cw_coa_creatures_displays.sql (creaturedisplayinfo_dbc,
-- creaturemodeldata_dbc); run those lines too.
DROP TABLE IF EXISTS `cw_coa_taught`;
DROP TABLE IF EXISTS `cw_coa_spell_scaling`;
DROP TABLE IF EXISTS `cw_coa_automatic`;
DROP TABLE IF EXISTS `cw_coa_entries`;
DROP TABLE IF EXISTS `cw_coa_tabs`;
DROP TABLE IF EXISTS `cw_coa_classes`;
