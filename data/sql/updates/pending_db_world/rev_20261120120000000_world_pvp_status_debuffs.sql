DELETE FROM `spell_dbc` WHERE `ID` IN (955080, 955081, 955082, 955083);
INSERT INTO `spell_dbc`
  (`ID`, `Attributes`, `AttributesEx2`, `AttributesEx3`, `DurationIndex`, `RangeIndex`, `Effect_1`,
   `ImplicitTargetA_1`, `EffectAura_1`, `SpellIconID`, `Name_Lang_enUS`, `AuraDescription_Lang_enUS`, `SchoolMask`)
VALUES
  (955080, 2751463680, 0, 0, 21, 1, 6, 1, 4, 17122, 'Wanted', 'You are wanted for a crime.', 1),
  (955081, 2751463680, 0, 0, 21, 1, 6, 1, 4, 17301, 'Bounty', 'There is an active bounty on you.', 1),
  (955082, 2751463680, 1, 1048576, 21, 1, 6, 1, 4, 322, 'PvP Enabled', 'You are flagged for PvP.', 1),
  (955083, 2751463680, 0, 0, 21, 1, 6, 1, 4, 227, 'Thief', 'You were seen stealing.', 1);

DELETE FROM `spell_custom_attr` WHERE `spell_id` IN (955080, 955081, 955082, 955083);
INSERT INTO `spell_custom_attr` (`spell_id`, `attributes`) VALUES
  (955080, 16777216), (955081, 16777216), (955082, 16777216), (955083, 16777216);
