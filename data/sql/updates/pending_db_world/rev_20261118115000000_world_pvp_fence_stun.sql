-- Single-target stun derived from spell 853, with duration 39 and its own two-minute cooldown.
DELETE FROM `spell_dbc` WHERE `ID` = 951070;
INSERT INTO `spell_dbc` VALUES (
  951070, 0, 0, 12, 327680, 262144, 0, 0, 0, 0, 8388608, 2048, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  1, 120000, 0, 0, 4718592, 0, 0, 101, 0, 0, 1, 1, 39, 0, 0, 0, 0, 0, 7, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 6, 0, 0, 1, 0, 0, 0.0, 0.0, 0.0, -1, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0,
  0, 0, 12, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 322, 0, 302, 0, 0, 'Underbelly Stun Powder', '', '', '', '', '', '', '', '', '', '', '',
  '', '', '', '', 16712190, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190,
  'Stuns an attackable player for 2 sec. Open world only.', '', '', '', '', '', '', '', '', '', '', '', '', '',
  '', '', 16712190, 'Stunned.', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 16712190, 0, 133,
  1500, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0
);
INSERT INTO `item_template`
  (`entry`, `class`, `subclass`, `name`, `displayid`, `Quality`, `maxcount`, `stackable`, `bonding`,
   `spellid_1`, `spelltrigger_1`, `spellcharges_1`, `spellcooldown_1`, `description`)
VALUES
  (951076, 0, 0, 'Underbelly Stun Powder', 6378, 1, 0, 20, 1, 951070, 0, -1, 120000,
   'Open world only. Stuns an attackable player for 2 sec. Shares a 2 minute cooldown across copies.') AS `powder`
ON DUPLICATE KEY UPDATE `class` = `powder`.`class`, `subclass` = `powder`.`subclass`, `name` = `powder`.`name`,
  `displayid` = `powder`.`displayid`, `Quality` = `powder`.`Quality`, `maxcount` = `powder`.`maxcount`,
  `stackable` = `powder`.`stackable`, `bonding` = `powder`.`bonding`, `spellid_1` = `powder`.`spellid_1`,
  `spelltrigger_1` = `powder`.`spelltrigger_1`, `spellcharges_1` = `powder`.`spellcharges_1`,
  `spellcooldown_1` = `powder`.`spellcooldown_1`, `description` = `powder`.`description`;
