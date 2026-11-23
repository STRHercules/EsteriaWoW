INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`)
VALUES (701950, 10, 6484, 'Wilderness Pouch', 1)
ON DUPLICATE KEY UPDATE `type` = 10, `displayId` = 6484, `name` = 'Wilderness Pouch', `size` = 1;
