-- Custom mounts must be in the shared Mounts skill line so the client can
-- place the learned spells in the Pets/Mounts tab. Keep the row ID equal to
-- the spell ID; this is collision-free in the current SkillLineAbility table
-- and keeps the server/client continuation rows identical.
DELETE FROM `skilllineability_dbc`
WHERE (`ID` BETWEEN 200101 AND 200104)
   OR (`ID` BETWEEN 201000 AND 201111);

INSERT INTO `skilllineability_dbc`
    (`ID`, `SkillLine`, `Spell`, `RaceMask`, `ClassMask`, `ExcludeRace`, `ExcludeClass`,
     `MinSkillLineRank`, `SupercededBySpell`, `AcquireMethod`, `TrivialSkillLineRankHigh`,
     `TrivialSkillLineRankLow`, `CharacterPoints_1`, `CharacterPoints_2`)
SELECT `ID`, 777, `ID`, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0
FROM `spell_dbc`
WHERE (`ID` BETWEEN 200101 AND 200104)
   OR (`ID` BETWEEN 201000 AND 201111);
