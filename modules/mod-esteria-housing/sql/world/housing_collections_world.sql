-- Housing section 4, collections and display: the pooled display creatures (the module names one per display), the relic
-- objects a trophy can show, and the placeable pieces (category 8, Collections). Apply after housing_world.sql (which
-- rebuilds the catalog), housing_commerce_world.sql and housing_adventure_world.sql. Every row is replaced, so it reapplies.

-- A trophy's replica or name, a stalled mount, a mannequin: npcflag 1 opens its window (npc_esteria_housing_display).
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 9507100 AND 9509999;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 9507100 AND 9509999;
SET SESSION cte_max_recursion_depth = 5000;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `unit_class`, `unit_flags`, `type`, `flags_extra`, `ScriptName`)
  WITH RECURSIVE n AS (SELECT 9507100 AS e UNION ALL SELECT e + 1 FROM n WHERE e < 9509999)
  SELECT e, 'Display', '', 80, 80, 35, 1, 1, 2, 7, 64, 'npc_esteria_housing_display' FROM n;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`)
  SELECT `entry`, 0, 3649, 1, 1 FROM `creature_template` WHERE `entry` BETWEEN 9507100 AND 9509999;

-- The relics a trophy can stand on its display (styles 1-8), drawn with retail decor models; they do nothing when used.
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 9506060 AND 9506099;
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`)
  SELECT 9506080 + v.n, 5, c.display_id, v.name, 1
  FROM (SELECT 0 n, 17629 decor, 'Aureate Trophy' name UNION ALL SELECT 1, 19197, 'Argent Trophy' UNION ALL SELECT 2, 18397, 'Gleaming Trophy'
        UNION ALL SELECT 3, 3894, 'Alliance Banner' UNION ALL SELECT 4, 3896, 'Horde Banner' UNION ALL SELECT 5, 1674, 'Head of the Broodmother'
        UNION ALL SELECT 6, 26054, 'Horrific Head of the Horseman' UNION ALL SELECT 7, 4042, 'Skeletal Dragon Head') v
  JOIN `housing_decor_catalog` c ON c.decor_id = v.decor;

-- The pieces: type 2 (questgiver) with no quests, so using one opens the script's gossip. The mannequin's object is never
-- spawned: it is a creature (its picture is the merchant's).
DELETE FROM `housing_decor_catalog` WHERE `decor_id` BETWEEN 40201 AND 40299;
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`)
  SELECT 9506060 + v.n, 2, c.display_id, v.name, 1, 'go_esteria_housing_collection'
  FROM (SELECT 1 n, 15490 decor, 'Trophy Wall Mount' name UNION ALL SELECT 2, 3836, 'Trophy Pedestal' UNION ALL SELECT 3, 27617, 'Trophy Plaque'
        UNION ALL SELECT 4, 21106, 'Trophy Case' UNION ALL SELECT 5, 2537, 'Mount Stall' UNION ALL SELECT 6, 14346, 'Mount Paddock'
        UNION ALL SELECT 7, 7607, 'Mount Pedestal' UNION ALL SELECT 8, 16098, 'Mannequin' UNION ALL SELECT 9, 11895, 'Library Bookshelf'
        UNION ALL SELECT 10, 3832, 'Storyteller''s Lectern' UNION ALL SELECT 11, 11881, 'Explorer''s Display Table'
        UNION ALL SELECT 12, 15064, 'Reading Nook' UNION ALL SELECT 13, 15290, 'Pet Habitat' UNION ALL SELECT 14, 12246, 'Pet Bed'
        UNION ALL SELECT 15, 26202, 'Pet Toy' UNION ALL SELECT 16, 23549, 'Feeding Station') v
  JOIN `housing_decor_catalog` c ON c.decor_id = v.decor;
INSERT INTO `housing_decor_catalog` (`decor_id`, `model_fdid`, `display_id`, `gameobject_entry`, `name`, `category`, `surface`, `budget_cost`, `min_scale`, `max_scale`, `origin`, `enabled`)
  SELECT 40200 + v.n, IF(v.n = 8, 1011653, c.model_fdid), c.display_id, 9506060 + v.n, v.name, 8, 0, 1, 0.5, 2, 'retail', 1
  FROM (SELECT 1 n, 15490 decor, 'Trophy Wall Mount' name UNION ALL SELECT 2, 3836, 'Trophy Pedestal' UNION ALL SELECT 3, 27617, 'Trophy Plaque'
        UNION ALL SELECT 4, 21106, 'Trophy Case' UNION ALL SELECT 5, 2537, 'Mount Stall' UNION ALL SELECT 6, 14346, 'Mount Paddock'
        UNION ALL SELECT 7, 7607, 'Mount Pedestal' UNION ALL SELECT 8, 16098, 'Mannequin' UNION ALL SELECT 9, 11895, 'Library Bookshelf'
        UNION ALL SELECT 10, 3832, 'Storyteller''s Lectern' UNION ALL SELECT 11, 11881, 'Explorer''s Display Table'
        UNION ALL SELECT 12, 15064, 'Reading Nook' UNION ALL SELECT 13, 15290, 'Pet Habitat' UNION ALL SELECT 14, 12246, 'Pet Bed'
        UNION ALL SELECT 15, 26202, 'Pet Toy' UNION ALL SELECT 16, 23549, 'Feeding Station') v
  JOIN `housing_decor_catalog` c ON c.decor_id = v.decor;
