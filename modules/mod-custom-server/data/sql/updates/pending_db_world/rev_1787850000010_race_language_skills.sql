-- Let the ported races actually learn their language skills.
--
-- `playercreateinfo_skills` already grants Common (98) to 18/19/21/23 and Orcish (109) to
-- 16/17/20/22/28, but `Player::LearnDefaultSkill()` first calls
-- `GetSkillRaceClassInfo(skill, race, class)` and bails out when no row matches
-- (`src/server/game/Entities/Player/Player.cpp`). The stock rows only mask races 1-15, so the
-- skill was never applied: existing characters only have it because the language backfill
-- scripts granted it directly, and the client refuses to send chat without it
-- (`ChatHandler.cpp`: `langDesc->skill_id && !sender->HasSkill(...)`).
--
-- Race bits for 16,17,18,19,20,21,22,23,28,29,30 = 1 << (race - 1) = 0x387F8000.

UPDATE `skillraceclassinfo_dbc`
SET `RaceMask` = `RaceMask` | 0x387F8000
WHERE `SkillID` IN (98, 109) AND `RaceMask` <> 0;

-- Same widening for the skill -> language spell mapping, so learning the skill also hands out
-- the language spell (668 Common / 669 Orcish) the client expects.

UPDATE `skilllineability_dbc`
SET `RaceMask` = `RaceMask` | 0x387F8000
WHERE `SkillLine` IN (98, 109) AND `RaceMask` <> 0;
