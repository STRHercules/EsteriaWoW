-- Player shops and commissions: the pooled merchant templates (the module names one per shop) and the placeable objects.
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9501000 AND 9504999;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9501000 AND 9504999;
SET SESSION cte_max_recursion_depth = 5000;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `unit_class`, `unit_flags`, `type`, `ScriptName`)
  WITH RECURSIVE n AS (SELECT 9501000 AS e UNION ALL SELECT e + 1 FROM n WHERE e < 9504999)
  SELECT e, 'Shopkeeper', 'General Goods', 80, 80, 35, 1, 1, 2, 7, 'npc_esteria_housing_merchant' FROM n;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`)
  SELECT `entry`, 0, 3649, 1, 1 FROM `creature_template` WHERE `entry` BETWEEN 9501000 AND 9504999;

-- Type 2 (questgiver) with no quests: using it opens the script's gossip, as the cornerstone does. Each borrows the model of a
-- retail decor piece and is sold as decor of its own (category 6, Shops). The merchant's object is never spawned: it is an NPC.
DELETE FROM `housing_decor_catalog` WHERE `decor_id` BETWEEN 40001 AND 40007;
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9506000 AND 9506006;
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`)
  SELECT 9506000 + v.n, 2, c.display_id, v.name, 1, 'go_esteria_housing_service'
  FROM (SELECT 0 n, 4428 decor, 'Commission Board' name UNION ALL SELECT 1, 4422, 'Shop Sign' UNION ALL SELECT 2, 16098, 'Display Case'
        UNION ALL SELECT 3, 15061, 'Display Shelf' UNION ALL SELECT 4, 26483, 'Display Rack' UNION ALL SELECT 5, 3985, 'Shop Counter'
        UNION ALL SELECT 6, 16098, 'Merchant') v
  JOIN `housing_decor_catalog` c ON c.decor_id = v.decor;
INSERT INTO `housing_decor_catalog` (`decor_id`, `model_fdid`, `display_id`, `gameobject_entry`, `name`, `category`, `surface`, `budget_cost`, `min_scale`, `max_scale`, `origin`, `enabled`)
  SELECT v.id, IF(v.fdid, v.fdid, c.model_fdid), c.display_id, v.go, v.name, 6, 0, 1, 0.5, 2, 'retail', 1
  FROM (SELECT 40001 id, 16098 decor, 9506006 go, 'Merchant' name, 1011653 fdid UNION ALL SELECT 40002, 4428, 9506000, 'Commission Board', 0
        UNION ALL SELECT 40003, 4422, 9506001, 'Shop Sign', 0 UNION ALL SELECT 40004, 16098, 9506002, 'Display Case', 0
        UNION ALL SELECT 40005, 15061, 9506003, 'Display Shelf', 0 UNION ALL SELECT 40006, 26483, 9506004, 'Display Rack', 0
        UNION ALL SELECT 40007, 3985, 9506005, 'Shop Counter', 0) v
  JOIN `housing_decor_catalog` c ON c.decor_id = v.decor;
