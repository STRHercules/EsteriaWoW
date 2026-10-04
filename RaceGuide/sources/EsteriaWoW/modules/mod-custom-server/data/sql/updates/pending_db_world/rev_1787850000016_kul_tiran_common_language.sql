-- Kul Tiran (race 29) is Alliance and receives Common language only.
-- Preserve the existing custom-race widening while keeping Orcish row 592 unchanged.
UPDATE `skilllineability_dbc`
SET `RaceMask` = `RaceMask` | 0x10000000
WHERE `ID` = 590 AND (`RaceMask` & 0x10000000) = 0;

-- If the earlier broad language update already added this bit to row 592, remove only
-- the Kul Tiran bit and preserve every other race bit on the Orcish row.
UPDATE `skilllineability_dbc`
SET `RaceMask` = `RaceMask` & 0xEFFFFFFF
WHERE `ID` = 592 AND (`RaceMask` & 0x10000000) <> 0;
