-- Align Broken racial cost, cooldown, target, and range metadata with the client spell records.
UPDATE `spell_dbc` SET
    `PowerType` = 0,
    `ManaCost` = 0,
    `ManaCostPerLevel` = 0,
    `ManaPerSecond` = 0,
    `ManaPerSecondPerLevel` = 0,
    `ManaCostPct` = 0,
    `CategoryRecoveryTime` = 0,
    `StartRecoveryCategory` = 0,
    `StartRecoveryTime` = 0
WHERE `ID` IN (110001, 110002, 110003, 110004);

UPDATE `spell_dbc` SET
    `RangeIndex` = 1,
    `ImplicitTargetA_1` = 1,
    `ImplicitTargetB_1` = 0
WHERE `ID` IN (110001, 110002, 110003);

UPDATE `spell_dbc` SET
    `RangeIndex` = 1,
    `ImplicitTargetA_1` = 1,
    `ImplicitTargetB_1` = 0
WHERE `ID` = 110004;
