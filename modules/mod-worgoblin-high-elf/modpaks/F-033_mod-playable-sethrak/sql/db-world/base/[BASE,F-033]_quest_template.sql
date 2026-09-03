/* Ensures that faction-restricted quests include Sethrak. */
UPDATE `quest_template`
SET `AllowableRaces` = `AllowableRaces` | @SethrakMask
WHERE (`AllowableRaces` & @OrcMask) != 0;
