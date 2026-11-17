-- Swords of Fire and Steel main/off-hand and Halo Energy Sword, with native animated material loops.
START TRANSACTION;
DELETE FROM `item_template` WHERE `entry` IN (3430084,3430085,3430086);
INSERT INTO `item_template` (`entry`,`class`,`subclass`,`name`,`displayid`,`Quality`,`InventoryType`,`AllowableClass`,`AllowableRace`,`ItemLevel`,`RequiredLevel`,`stackable`,`maxcount`,`bonding`,`dmg_min1`,`dmg_max1`,`delay`,`sheath`,`description`) VALUES
(3430084,2,7,'Swords of Fire and Steel (Main Hand)',3430084,4,21,-1,-1,1,0,1,1,1,1,1,2400,3,'Animated cosmetic sword appearance.'),
(3430085,2,7,'Swords of Fire and Steel (Off Hand)',3430085,4,22,-1,-1,1,0,1,1,1,1,1,2400,3,'Animated cosmetic sword appearance.'),
(3430086,2,7,'Halo Energy Sword',3430086,4,13,-1,-1,1,0,1,1,1,1,1,2400,3,'Animated cosmetic sword appearance.');
COMMIT;
