/* Add model info for mounts and other NPCs */
DELETE FROM `creature_model_info` WHERE `DisplayID` IN (94133, 94134, 94135, 94136);
INSERT INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) VALUES
(94133, 0.406, 1.5, 0, 0), -- Running Wild Male
(94134, 0.406, 1.5, 1, 0), -- Running Wild Female
(94135, 0.306, 1.5, 0, 0), -- Gilnean Male
(94136, 0.306, 1.5, 1, 0); -- Gilnean Female
