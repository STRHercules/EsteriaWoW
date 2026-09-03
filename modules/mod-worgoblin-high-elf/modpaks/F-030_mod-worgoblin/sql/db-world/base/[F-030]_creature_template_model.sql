/* Add models for racial mounts and goblin racial bank NPC */
DELETE FROM `creature_template_model` WHERE `CreatureID` IN (55274, 55275, 55276, 55277);
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
	(55274, 0, 94133, 1, 1, 12340), -- Running Wild Male
	(55275, 0, 94134, 1, 1, 12340), -- Running Wild Female
	(55276, 0, 94135, 1, 1, 12340), -- Gilnean Male
	(55277, 0, 94136, 1, 1, 12340); -- Gilnean Female
