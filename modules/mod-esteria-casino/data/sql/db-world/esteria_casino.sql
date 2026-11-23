-- Esteria casino (mod-esteria-casino). Creature entries 9600000-9600099 are reserved for casino NPCs.
-- 9600000 blackjack, 9600001 slots, 9600002 Goblin Dice, 9600003 chess and checkers, 9600004 Hold'em,
-- 9600005 the lottery. No spawns here: Housing Dev spawns them in its deploy
-- script; elsewhere place them with `.npc add <entry>` until the casino venue is built.

DELETE FROM `creature_template` WHERE `entry` IN (9600000, 9600001, 9600002, 9600003, 9600004, 9600005);
INSERT INTO `creature_template`
  (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `unit_class`,
   `unit_flags`, `type`, `type_flags`, `RegenHealth`, `flags_extra`, `ScriptName`, `VerifiedBuild`)
VALUES
(9600000, 'Blackjack Dealer', 'Esteria Casino', 80, 80, 35, 1, 1, 2, 7, 0, 1, 2, 'npc_esteria_casino_blackjack', 12340),
(9600001, 'Fizzle Spinwheel', 'Slot Machine', 80, 80, 35, 1, 1, 2, 7, 0, 1, 2, 'npc_esteria_casino_slots', 12340),
(9600002, 'Grizzik Knucklebones', 'Goblin Dice', 80, 80, 35, 1, 1, 2, 7, 0, 1, 2, 'npc_esteria_casino_dice', 12340),
(9600003, 'Grandmaster Pell', 'Chess & Checkers', 80, 80, 35, 1, 1, 2, 7, 0, 1, 2, 'npc_esteria_casino_board', 12340),
(9600004, 'Card Shark Vexa', 'Texas Hold''em', 80, 80, 35, 1, 1, 2, 7, 0, 1, 2, 'npc_esteria_casino_poker', 12340),
(9600005, 'Lucky Nozzlebit', 'Esteria Lottery', 80, 80, 35, 1, 1, 2, 7, 0, 1, 2, 'npc_esteria_casino_lottery', 12340);

-- Goblin models of Baron Revilgaz (2496), Nixx Sprocketspring (8126), Krazek (773), Dirge Quikcleave (8125),
-- Gazlowe (3391) and Wrenix the Wretched (7161).
DELETE FROM `creature_template_model` WHERE `CreatureID` IN (9600000, 9600001, 9600002, 9600003, 9600004, 9600005);
INSERT INTO `creature_template_model`
  (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
VALUES
(9600000, 0, 7167, 1, 1, 12340),
(9600001, 0, 7340, 1, 1, 12340),
(9600002, 0, 7164, 1, 1, 12340),
(9600003, 0, 7338, 1, 1, 12340),
(9600004, 0, 7052, 1, 1, 12340),
(9600005, 0, 7154, 1, 1, 12340);
