INSERT INTO `item_template`
  (`entry`, `class`, `subclass`, `name`, `displayid`, `Quality`, `stackable`, `bonding`, `description`)
VALUES (9510710, 15, 0, 'Ear Trophy', 7612, 1, 1, 1, 'Right-click to read the record of this kill.')
ON DUPLICATE KEY UPDATE `class` = 15, `subclass` = 0, `name` = 'Ear Trophy', `displayid` = 7612,
  `Quality` = 1, `stackable` = 1, `bonding` = 1, `description` = 'Right-click to read the record of this kill.';
