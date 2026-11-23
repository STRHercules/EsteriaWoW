-- The Fence checks for learned Pick Pocket before listing or selling the kit.
UPDATE `item_template` SET `AllowableClass` = -1 WHERE `entry` = 9510713;
