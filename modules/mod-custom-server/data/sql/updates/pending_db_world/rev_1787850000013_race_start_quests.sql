-- Let every custom race take the quests of the stock race that shares its start zone.
-- `quest_template.AllowableRaces` is the same mask the client is sent, so widening it for
-- the host race's quests is what opens the Valley of Trials / Eversong / Elwynn / Azuremyst
-- / Dun Morogh starter chains to the ported races. Rows with mask 0 are unrestricted.

-- race 14 <- Orc (2)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 8192
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 2) <> 0;

-- race 16 <- Orc (2)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 32768
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 2) <> 0;

-- race 20 <- Orc (2)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 524288
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 2) <> 0;

-- race 22 <- Orc (2)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 2097152
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 2) <> 0;

-- race 28 <- Orc (2)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 134217728
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 2) <> 0;

-- race 17 <- Blood Elf (10)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 65536
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 512) <> 0;

-- race 30 <- Blood Elf (10)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 536870912
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 512) <> 0;

-- race 18 <- Human (1)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 131072
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 1) <> 0;

-- race 19 <- Human (1)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 262144
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 1) <> 0;

-- race 21 <- Draenei (11)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 1048576
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 1024) <> 0;

-- race 23 <- Dwarf (3)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 4194304
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 4) <> 0;

-- race 29 <- Dwarf (3)
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | 268435456
WHERE `AllowableRaces` <> 0 AND (`AllowableRaces` & 4) <> 0;

