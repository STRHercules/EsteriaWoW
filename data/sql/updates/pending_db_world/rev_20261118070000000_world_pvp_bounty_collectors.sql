INSERT INTO `creature_template`
  (`entry`, `name`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `BaseAttackTime`, `RangeAttackTime`,
   `unit_class`, `unit_flags`, `type`, `ScriptName`)
SELECT 9510700, 'Bounty Collector', 60, 60, 35, 1, 2000, 2000, 1, 768, 7, 'npc_esteria_bounty_collector'
WHERE NOT EXISTS (
  SELECT 1 FROM `creature_template` WHERE `entry` = 9510700 AND `ScriptName` = 'npc_esteria_bounty_collector'
);
DELETE FROM `creature_template_model` WHERE `CreatureID` = 9510700;
INSERT INTO `creature_template_model`
  (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
VALUES (9510700, 0, 25605, 1, 1, 12340);
DELETE FROM `creature` WHERE `guid` IN (9510701, 9510702, 9510703) AND `id` = 9510700;
INSERT INTO `creature`
  (`guid`, `id`, `map`, `position_x`, `position_y`, `position_z`, `orientation`, `Comment`)
VALUES
  (9510701, 9510700, 0, -8933.25, 609.468, 99.606, 0.45, 'Bounty Collector - Stormwind bank'),
  (9510702, 9510700, 1, 1629.855, -4379.02, 12.05, 3.50, 'Bounty Collector - Orgrimmar bank'),
  (9510703, 9510700, 571, 5848.5, 636.9, 647.574, 1.05, 'Bounty Collector - Dalaran, Legerdemain Lounge');
