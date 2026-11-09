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
-- spawned: it is a creature (its picture is a statue's). `size` is the share of its placed size a piece is drawn at
-- (BaseScale): the stall's model is large, the mount mat shows its rug until a mount stands on it (MatHidden), the small
-- habitats are small rugs. The Trophy Wall Mount (40201) was retired.
-- go = 9506060 + n for decor 40200 + n; the later pieces (decor 40265-40273) take 9506088-9506096. The Grand Pet Rug
-- holds ten pets (HabitatPets); any habitat can hide its rug. The trophy rug, like the
-- mount mat, shows only until something stands on it.
DELETE FROM `housing_decor_catalog` WHERE `decor_id` BETWEEN 40201 AND 40216 OR `decor_id` BETWEEN 40265 AND 40299;
DROP TEMPORARY TABLE IF EXISTS `housing_collection_piece`;
CREATE TEMPORARY TABLE `housing_collection_piece` (`decor_id` INT UNSIGNED, `go` INT UNSIGNED, `borrow` INT UNSIGNED, `name` VARCHAR(64),
  `size` FLOAT);
INSERT INTO `housing_collection_piece` VALUES
  (40202, 9506062, 3836, 'Trophy Pedestal', 1), (40203, 9506063, 27617, 'Trophy Plaque', 1), (40204, 9506064, 21106, 'Trophy Case', 1),
  (40205, 9506065, 2537, 'Mount Stall', 0.4), (40206, 9506066, 14346, 'Mount Paddock', 1), (40207, 9506067, 7607, 'Mount Pedestal', 1),
  (40208, 9506068, 5564, 'Mannequin', 1), (40209, 9506069, 11895, 'Library Bookshelf', 1),
  (40210, 9506070, 3832, 'Storyteller''s Lectern', 1), (40211, 9506071, 11881, 'Explorer''s Display Table', 1),
  (40212, 9506072, 15064, 'Reading Nook', 1), (40213, 9506073, 15290, 'Pet Habitat', 1), (40214, 9506074, 12246, 'Pet Bed', 1),
  (40215, 9506075, 23548, 'Pet Ball', 1), (40216, 9506076, 23549, 'Feeding Station', 1),
  (40265, 9506088, 2094, 'Mount Mat', 1),
  (40266, 9506089, 2094, 'Small Pet Rug', 0.6), (40267, 9506090, 1698, 'Pet Cushion', 0.7), (40268, 9506091, 12194, 'Tiny Pet Rug', 0.45),
  (40269, 9506092, 14839, 'Wolf Plushie', 1), (40270, 9506093, 14838, 'Lion Plushie', 1), (40271, 9506094, 26479, 'Murloc Plushie', 1),
  (40272, 9506095, 498, 'Trophy Rug', 1), (40273, 9506096, 4026, 'Grand Pet Rug', 1);
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `ScriptName`)
  SELECT v.go, 2, c.display_id, v.name, v.size, 'go_esteria_housing_collection'
  FROM `housing_collection_piece` v JOIN `housing_decor_catalog` c ON c.decor_id = v.borrow;
INSERT INTO `housing_decor_catalog` (`decor_id`, `model_fdid`, `display_id`, `gameobject_entry`, `name`, `category`, `surface`, `budget_cost`, `min_scale`, `max_scale`, `origin`, `enabled`)
  SELECT v.decor_id, c.model_fdid, c.display_id, v.go, v.name, 8, 0, 1, 0.5, 2, 'retail', 1
  FROM `housing_collection_piece` v JOIN `housing_decor_catalog` c ON c.decor_id = v.borrow;
DROP TEMPORARY TABLE `housing_collection_piece`;
