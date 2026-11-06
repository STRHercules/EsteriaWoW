-- Held items for the Battlemon shop (acore_world), in Battlemon Points. A win earns 10 points, a Master Ball is 500.
-- Every item here is one src/BattlemonHeldItems.h gives an effect to; the berries (Oran, Sitrus, Lum and the
-- status ones) are already sold and can be held too. Safe to run repeatedly.

DELETE FROM `battlemon_shop` WHERE `item_internal_name` IN
  ('CHARCOAL', 'MYSTICWATER', 'MIRACLESEED', 'MAGNET', 'NEVERMELTICE', 'BLACKBELT', 'POISONBARB', 'SOFTSAND',
   'SHARPBEAK', 'TWISTEDSPOON', 'SILVERPOWDER', 'HARDSTONE', 'SPELLTAG', 'DRAGONFANG', 'BLACKGLASSES', 'METALCOAT',
   'SILKSCARF', 'MUSCLEBAND', 'WISEGLASSES', 'EXPERTBELT', 'CHOICEBAND', 'CHOICESPECS', 'CHOICESCARF', 'LIFEORB',
   'LEFTOVERS', 'BLACKSLUDGE', 'FOCUSSASH', 'LUCKYEGG', 'EVERSTONE', 'DESTINYKNOT');
INSERT INTO `battlemon_shop` (`item_internal_name`, `cost`, `sort_order`) VALUES
('FOCUSSASH',    80,  400),
('LEFTOVERS',    150, 410),
('BLACKSLUDGE',  100, 420),
('LIFEORB',      200, 430),
('CHOICEBAND',   150, 440),
('CHOICESPECS',  150, 450),
('CHOICESCARF',  150, 460),
('EXPERTBELT',   120, 470),
('MUSCLEBAND',   60,  480),
('WISEGLASSES',  60,  490),
('CHARCOAL',     60,  500),
('MYSTICWATER',  60,  510),
('MIRACLESEED',  60,  520),
('MAGNET',       60,  530),
('NEVERMELTICE', 60,  540),
('BLACKBELT',    60,  550),
('POISONBARB',   60,  560),
('SOFTSAND',     60,  570),
('SHARPBEAK',    60,  580),
('TWISTEDSPOON', 60,  590),
('SILVERPOWDER', 60,  600),
('HARDSTONE',    60,  610),
('SPELLTAG',     60,  620),
('DRAGONFANG',   60,  630),
('BLACKGLASSES', 60,  640),
('METALCOAT',    60,  650),
('SILKSCARF',    60,  660),
('LUCKYEGG',     150, 670),
('EVERSTONE',    40,  680),
('DESTINYKNOT',  120, 690);
