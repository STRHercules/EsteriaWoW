-- Battlemon overworld: one gossip critter used by .npc add / .bmo spawn.
-- Display 50037 = form 37 Pikachu (see tools/patch_dbc_csv.py).
-- Rerunnable.

REPLACE INTO `creature_template` (
  `entry`, `difficulty_entry_1`, `difficulty_entry_2`, `difficulty_entry_3`,
  `KillCredit1`, `KillCredit2`, `name`, `subname`, `IconName`, `gossip_menu_id`,
  `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,
  `speed_walk`, `speed_run`, `speed_swim`, `speed_flight`, `detection_range`,
  `rank`, `dmgschool`, `DamageModifier`, `BaseAttackTime`, `RangeAttackTime`,
  `BaseVariance`, `RangeVariance`, `unit_class`, `unit_flags`, `unit_flags2`,
  `dynamicflags`, `family`, `type`, `type_flags`, `lootid`, `pickpocketloot`,
  `skinloot`, `PetSpellDataId`, `VehicleId`, `mingold`, `maxgold`,
  `AIName`, `MovementType`, `HoverHeight`, `HealthModifier`, `ManaModifier`,
  `ArmorModifier`, `ExperienceModifier`, `RacialLeader`, `movementId`,
  `RegenHealth`, `CreatureImmunitiesId`, `flags_extra`, `ScriptName`, `VerifiedBuild`
) VALUES (
  60000, 0, 0, 0,
  0, 0, 'Wild Battlemon', '', NULL, 0,
  1, 1, 0, 35, 1,
  1, 1.14286, 1, 1, 20,
  0, 0, 1, 2000, 2000,
  1, 1, 1, 258, 0,
  0, 0, 8, 0, 0, 0,
  0, 0, 0, 0, 0,
  '', 0, 1, 1, 1,
  1, 0, 0, 0,
  1, 0, 16785474, 'npc_battlemon_overworld', 12340
);

REPLACE INTO `creature_template_model` (
  `CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`
) VALUES (
  60000, 0, 50037, 1, 1, 12340
);

REPLACE INTO `creature_model_info` (
  `DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`, `VerifiedBuild`
) VALUES (
  50037, 0.5, 1, 2, 0, 12340
);
