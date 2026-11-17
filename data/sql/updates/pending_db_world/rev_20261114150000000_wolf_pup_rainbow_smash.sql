-- Animated Wolf Pup backpack and Rainbow Smash cosmetic weapon.
START TRANSACTION;
DELETE FROM `item_template` WHERE `entry` IN (3400100,3410100,3430001);
INSERT INTO `item_template` (`entry`,`class`,`subclass`,`name`,`displayid`,`Quality`,`InventoryType`,`AllowableClass`,`AllowableRace`,`ItemLevel`,`RequiredLevel`,`stackable`,`maxcount`,`spellid_1`,`spelltrigger_1`,`ScriptName`,`description`,`bonding`,`dmg_min1`,`dmg_max1`,`delay`,`sheath`) VALUES
(3400100,4,1,'Wolf Pup (Remus)',3400100,4,16,-1,-1,1,0,1,1,0,0,'','Animated cosmetic cloak appearance.',0,0,0,0,0),
(3410100,0,8,'Appearance: Wolf Pup (Remus)',3400100,4,0,-1,-1,1,0,1,1,3420001,0,'item_esteria_backpack_appearance','Use: Learn the animated Wolf Pup cloak appearance for your account.',1,0,0,0,0),
(3430001,2,1,'Rainbow Smash',3430001,4,17,-1,-1,1,0,1,1,0,0,'','Cosmetic two-handed axe appearance.',1,1,1,3000,1);
DELETE FROM `esteria_backpack_appearances` WHERE `source_item`=3400100;
INSERT INTO `esteria_backpack_appearances` (`source_item`,`token_item`) VALUES (3400100,3410100);
COMMIT;
