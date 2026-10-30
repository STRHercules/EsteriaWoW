-- Freeborn is a faction of its own, decided by race (IsFreebornRace in SharedDefines.h).
-- Characters of the Freeborn races join TEAM_FREEBORN (3); characters of other races that had
-- claimed Freeborn go back to their race's ChrRaces team (Horde 1, otherwise Alliance 0).
UPDATE `characters` SET `teamId` = 3
WHERE `race` IN (15, 16, 54, 56, 57, 58, 59, 60, 61, 62, 63, 64, 68, 69, 70, 71, 72, 73, 74, 77, 78);

UPDATE `characters`
SET `teamId` = IF(`race` IN (2, 5, 6, 8, 9, 10, 14, 17, 20, 22, 28, 30, 44, 45, 46, 49, 51, 53, 67, 76), 1, 0)
WHERE `teamId` = 3
  AND `race` NOT IN (15, 16, 54, 56, 57, 58, 59, 60, 61, 62, 63, 64, 68, 69, 70, 71, 72, 73, 74, 77, 78);
