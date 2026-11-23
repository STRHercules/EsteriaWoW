UPDATE `creature_template` SET `npcflag` = 128, `ScriptName` = ''
WHERE `entry` = 9510704 AND `ScriptName` = 'npc_esteria_fence';
UPDATE `item_template` SET `SellPrice` = 10000,
  `description` = 'Right-click to read the record of this kill. Only the Underbelly Fence buys these.'
WHERE `entry` = 9510710;
DELETE FROM `itemextendedcost_dbc` WHERE `ID` IN (951071, 951072);
INSERT INTO `itemextendedcost_dbc` (`ID`, `ItemID_1`, `ItemCount_1`) VALUES
  (951071, 9510710, 1),
  (951072, 9510710, 3);
DELETE FROM `npc_vendor` WHERE `entry` = 9510704 AND `item` IN (951076, 9510713);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `ExtendedCost`) VALUES
  (9510704, 0, 951076, 951071),
  (9510704, 1, 9510713, 951072);
