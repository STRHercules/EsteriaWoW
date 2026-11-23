INSERT INTO `creature_template`
  (`entry`, `name`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `BaseAttackTime`, `RangeAttackTime`,
   `unit_class`, `unit_flags`, `type`, `ScriptName`)
VALUES (9510704, 'Underbelly Fence', 60, 60, 35, 1, 2000, 2000, 1, 768, 7, 'npc_esteria_fence') AS fence
ON DUPLICATE KEY UPDATE `name` = fence.`name`, `minlevel` = fence.`minlevel`, `maxlevel` = fence.`maxlevel`,
  `faction` = fence.`faction`, `npcflag` = fence.`npcflag`, `BaseAttackTime` = fence.`BaseAttackTime`,
  `RangeAttackTime` = fence.`RangeAttackTime`, `unit_class` = fence.`unit_class`, `unit_flags` = fence.`unit_flags`,
  `type` = fence.`type`, `ScriptName` = fence.`ScriptName`;
DELETE FROM `creature_template_model` WHERE `CreatureID` = 9510704;
INSERT INTO `creature_template_model`
  (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
VALUES (9510704, 0, 27912, 1, 1, 12340);
DELETE FROM `creature` WHERE `guid` = 9510705 AND `id` = 9510704;
INSERT INTO `creature`
  (`guid`, `id`, `map`, `position_x`, `position_y`, `position_z`, `orientation`, `Comment`)
VALUES (9510705, 9510704, 571, 5830.88, 646.813, 610.666, 2.63545, 'Underbelly Fence - Dalaran');
