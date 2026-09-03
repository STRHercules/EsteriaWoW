-- mod-seasonpass v4: optionale Deko-NPCs (alles geht auch komplett ohne sie!)
--   Chronistin Elenya      (Traumpfad, Prestige):              .npc add 987000
--   Runenmeisterin Sela    (Runen & neue Faehigkeiten):        .npc add 987001
--   Saisonhaendlerin Jinba (Verkauf):                          .npc add 987002
--   Traumpfadhueterin Lyra (Teleporter):                       .npc add 987003
DELETE FROM `creature_template` WHERE `entry` BETWEEN 987000 AND 987004;
INSERT INTO `creature_template` (`entry`,`name`,`subname`,`minlevel`,`maxlevel`,`faction`,`npcflag`,`unit_class`,`type`,`ScriptName`)
VALUES
(987000,'Chronistin Elenya','Traumpfad',80,80,35,1,1,7,'npc_seasonpass'),
(987001,'Runenmeisterin Sela','Saisonale Runen',80,80,35,1,1,7,'npc_seasonpass_runes'),
(987002,'Saisonhaendlerin Jinba','Saisonale Waren',80,80,35,129,1,7,''),
(987003,'Traumpfadhueterin Lyra','Teleporterin',80,80,35,1,1,7,'npc_seasonpass_teleport');
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 987000 AND 987004;
INSERT INTO `creature_template_model` (`CreatureID`,`Idx`,`CreatureDisplayID`,`DisplayScale`,`Probability`,`VerifiedBuild`)
VALUES
(987000,0,28213,1,1,12340),
(987001,0,28212,1,1,12340),
(987002,0,28214,1,1,12340),
(987003,0,28215,1,1,12340);
