INSERT INTO `item_template`
  (`entry`, `class`, `subclass`, `name`, `displayid`, `Quality`, `AllowableClass`, `maxcount`, `stackable`,
   `bonding`, `description`)
VALUES (9510713, 15, 0, 'Underbelly Pickpocket Kit', 7411, 1, 8, 1, 1, 1,
  'While carried in your bags, your chance to pickpocket players rises from 60% to 70%.') AS `kit`
ON DUPLICATE KEY UPDATE `class` = `kit`.`class`, `subclass` = `kit`.`subclass`, `name` = `kit`.`name`,
  `displayid` = `kit`.`displayid`, `Quality` = `kit`.`Quality`, `AllowableClass` = `kit`.`AllowableClass`,
  `maxcount` = `kit`.`maxcount`, `stackable` = `kit`.`stackable`, `bonding` = `kit`.`bonding`,
  `description` = `kit`.`description`;
