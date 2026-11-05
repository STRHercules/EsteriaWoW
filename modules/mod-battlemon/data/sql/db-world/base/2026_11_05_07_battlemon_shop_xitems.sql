-- X items for the Battlemon shop (acore_world): +2 stages for the Pokemon that is out, one battle.
--
-- They were held back until the addon's battle bag could list them (UI/BattleFrame.lua now accepts the
-- OnBattler X items). Prices follow the existing ratio of 4 points per 100 of the catalog price, which makes
-- X Defense and X Sp. Def the expensive ones. Safe to run repeatedly.

DELETE FROM `battlemon_shop` WHERE `item_internal_name` IN
  ('XATTACK', 'XSPATK', 'XSPEED', 'XACCURACY', 'XDEFENSE', 'XSPDEF');
INSERT INTO `battlemon_shop` (`item_internal_name`, `cost`, `sort_order`) VALUES
('XATTACK',   40, 300),
('XSPATK',    40, 310),
('XSPEED',    40, 320),
('XACCURACY', 40, 330),
('XDEFENSE',  80, 340),
('XSPDEF',    80, 350);
