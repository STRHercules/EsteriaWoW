-- ExplorationSoundID (ChrRaces field 3) must be non-zero: every race the client renders
-- portraits for carries 4140-4147, and races 16-30 shipped 0 (no portrait, no languages).
UPDATE `chrraces_dbc` SET `ExplorationSoundID` = 4141 WHERE `ID` IN (16, 17, 20, 22, 28, 30);
UPDATE `chrraces_dbc` SET `ExplorationSoundID` = 4140 WHERE `ID` IN (18, 19, 21, 23, 29);
