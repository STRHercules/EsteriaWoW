-- Esteria's final item migrations can remove or reclassify recovered CoA items.
-- Preserve authored tiers/weights and item stats; exclude entries that fail the runtime pool contract.
UPDATE `manastorm_greedy_demon_loot_pool` AS `pool`
LEFT JOIN `item_template` AS `item` ON `item`.`entry` = `pool`.`item_entry`
SET `pool`.`enabled` = 0
WHERE `pool`.`enabled` = 1
  AND (`item`.`entry` IS NULL OR `item`.`Quality` <> `pool`.`quality_tier`);
