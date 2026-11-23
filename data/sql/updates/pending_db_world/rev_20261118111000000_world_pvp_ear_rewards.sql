INSERT INTO `item_template`
  (`entry`, `class`, `subclass`, `name`, `displayid`, `Quality`, `InventoryType`, `stackable`, `bonding`)
VALUES
  (9510711, 4, 0, 'Wilderness Tabard', 3865, 1, 19, 1, 1),
  (9510712, 4, 1, 'Wilderness Cloak', 26202, 1, 16, 1, 1)
ON DUPLICATE KEY UPDATE `class` = VALUES(`class`), `subclass` = VALUES(`subclass`), `name` = VALUES(`name`),
  `displayid` = VALUES(`displayid`), `Quality` = VALUES(`Quality`), `InventoryType` = VALUES(`InventoryType`),
  `stackable` = VALUES(`stackable`), `bonding` = VALUES(`bonding`);
