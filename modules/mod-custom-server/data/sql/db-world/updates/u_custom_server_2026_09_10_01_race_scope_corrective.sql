-- Preflight existing characters before correcting the custom race playability flags.
SELECT race, COUNT(*) AS character_count
FROM acore_characters.characters
WHERE race IN (15, 18, 20, 26)
GROUP BY race
ORDER BY race;

SELECT ID, Flags, FactionID, Alliance, MaleDisplayId, FemaleDisplayId
FROM chrraces_dbc
WHERE ID IN (15, 18, 20, 26)
ORDER BY ID;

UPDATE chrraces_dbc
SET Flags = Flags - (Flags & 1)
WHERE ID IN (18, 20) AND (Flags & 1) = 1;

UPDATE chrraces_dbc
SET Flags = Flags | 1
WHERE ID = 26 AND (Flags & 1) = 0;

-- Report missing player creation rows for every enabled race and supported class.
SELECT expected.RaceID, expected.ClassID
FROM (SELECT 18 AS RaceID UNION ALL SELECT 20) AS expected
CROSS JOIN (SELECT 1 AS ClassID UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
            UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9 UNION ALL SELECT 11) AS classes
LEFT JOIN playercreateinfo AS actual
    ON actual.race = expected.RaceID AND actual.class = classes.ClassID
WHERE actual.race IS NULL
ORDER BY expected.RaceID, classes.ClassID;

SELECT expected.RaceID, expected.ClassID
FROM (SELECT 18 AS RaceID UNION ALL SELECT 20) AS expected
CROSS JOIN (SELECT 1 AS ClassID UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
            UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9 UNION ALL SELECT 11) AS classes
LEFT JOIN playercreateinfo_item AS actual
    ON actual.race = expected.RaceID AND actual.class = classes.ClassID
WHERE actual.race IS NULL
GROUP BY expected.RaceID, classes.ClassID
ORDER BY expected.RaceID, classes.ClassID;

SELECT expected.RaceID, expected.ClassID
FROM (SELECT 18 AS RaceID UNION ALL SELECT 20) AS expected
CROSS JOIN (SELECT 1 AS ClassID UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
            UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9 UNION ALL SELECT 11) AS classes
LEFT JOIN playercreateinfo_action AS actual
    ON actual.race = expected.RaceID AND actual.class = classes.ClassID
WHERE actual.race IS NULL
GROUP BY expected.RaceID, classes.ClassID
ORDER BY expected.RaceID, classes.ClassID;

SELECT expected.RaceID
FROM (SELECT 18 AS RaceID UNION ALL SELECT 20) AS expected
LEFT JOIN player_race_stats AS actual ON actual.Race = expected.RaceID
WHERE actual.Race IS NULL
ORDER BY expected.RaceID;

SELECT races.RaceID, classes.ClassID, sexes.SexID
FROM (SELECT 18 AS RaceID UNION ALL SELECT 20) AS races
CROSS JOIN (SELECT 1 AS ClassID UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
            UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9 UNION ALL SELECT 11) AS classes
CROSS JOIN (SELECT 0 AS SexID UNION ALL SELECT 1) AS sexes
LEFT JOIN charstartoutfit_dbc AS actual
    ON actual.RaceID = races.RaceID
    AND actual.ClassID = classes.ClassID
    AND actual.SexID = sexes.SexID
WHERE actual.ID IS NULL
ORDER BY races.RaceID, classes.ClassID, sexes.SexID;

-- Report missing race/class coverage in custom starting spells without changing it.
SELECT expected.RaceID, expected.ClassID
FROM (SELECT 18 AS RaceID UNION ALL SELECT 20) AS expected
CROSS JOIN (SELECT 1 AS ClassID UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
            UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9 UNION ALL SELECT 11) AS classes
LEFT JOIN playercreateinfo_spell_custom AS actual
    ON (actual.racemask & (1 << (expected.RaceID - 1))) <> 0
    AND (actual.classmask = 0 OR (actual.classmask & (1 << (classes.ClassID - 1))) <> 0)
WHERE actual.racemask IS NULL
GROUP BY expected.RaceID, classes.ClassID
ORDER BY expected.RaceID, classes.ClassID;

-- Report missing race/class skill coverage without changing the skill table.
SELECT expected.RaceID, expected.ClassID
FROM (SELECT 18 AS RaceID UNION ALL SELECT 20) AS expected
CROSS JOIN (SELECT 1 AS ClassID UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
            UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9 UNION ALL SELECT 11) AS classes
LEFT JOIN skillraceclassinfo_dbc AS actual
    ON (actual.RaceMask & (1 << (expected.RaceID - 1))) <> 0
    AND (actual.ClassMask = 0 OR (actual.ClassMask & (1 << (classes.ClassID - 1))) <> 0)
WHERE actual.ID IS NULL
GROUP BY expected.RaceID, classes.ClassID
ORDER BY expected.RaceID, classes.ClassID;
