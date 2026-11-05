-- Berries, drinks and the menu shop (acore_world).
--
-- Oran and Sitrus Berries had no heal amount in the catalog, so they could not be used at all. Oran heals
-- a flat 10 HP; Sitrus heals a quarter of max HP ("quarter" is understood by BattlemonMgr::UseItem).
--
-- Prices are in Battlemon Points and keep the existing ratio (Potion 200 = 8 points, i.e. 4 points per 100).
-- Status berries only cure the one status they name, so they sit just under the matching spray's price.
-- Every internal_name already exists in battlemon_items. X items are deliberately not sold yet: the server
-- supports them, but the addon's battle bag only lists battle_use = OnPokemon items.
-- Safe to run repeatedly.

UPDATE `battlemon_items` SET `heal_amount` = '10' WHERE `internal_name` = 'ORANBERRY';
UPDATE `battlemon_items` SET `heal_amount` = 'quarter' WHERE `internal_name` = 'SITRUSBERRY';

DELETE FROM `battlemon_shop` WHERE `item_internal_name` IN
  ('FRESHWATER', 'SODAPOP', 'LEMONADE', 'MOOMOOMILK', 'CHERIBERRY', 'CHESTOBERRY', 'PECHABERRY', 'RAWSTBERRY',
   'ASPEARBERRY', 'ORANBERRY', 'SITRUSBERRY', 'LUMBERRY');
INSERT INTO `battlemon_shop` (`item_internal_name`, `cost`, `sort_order`) VALUES
('FRESHWATER',  8,  180),
('SODAPOP',     12, 190),
('LEMONADE',    14, 200),
('MOOMOOMILK',  24, 210),
('ORANBERRY',   3,  220),
('CHERIBERRY',  4,  230),
('CHESTOBERRY', 4,  240),
('PECHABERRY',  4,  250),
('RAWSTBERRY',  4,  260),
('ASPEARBERRY', 4,  270),
('SITRUSBERRY', 12, 280),
('LUMBERRY',    12, 290);
