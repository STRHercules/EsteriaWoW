-- Esteria: the endgame (depth) cache ladder is only used at the level cap, 80, but CoA themed it on Classic raids
-- (item level 55-99). Re-point it to WotLK, keeping every cache, roll group, chance, depth and unlock as they are:
-- only the contents of the shared pools (the 9002xxx/9003xxx references) and the cache names change.
--
--   Classic slot      -> WotLK pool                       Normal         Heroic              Mythic
--   dungeons          -> WotLK five-player dungeons        normal, stock  heroic, +5 copies   heroic, +10 copies
--   Zul'Gurub         -> Naxxramas + Obsidian Sanctum + Eye of Eternity
--   Molten Core       -> Ulduar
--   Onyxia            -> Onyxia's Lair (80)
--   MC/Onyxia union   -> Ulduar + Onyxia's Lair
--   Blackwing Lair    -> Trial of the Crusader
--   Ruins of AQ       -> Icecrown Citadel (everything but the Frostwing Halls)
--   Temple of AQ      -> Frostwing Halls (Valithria, Sindragosa, Lich King) + Ruby Sanctum
--   Naxxramas         -> all of Icecrown Citadel + Ruby Sanctum
--   raids: Normal = 10-player stock items; Heroic = 25-player loot copied +5 item levels; Mythic = 25-player heroic
--   loot copied +10 (25-player when the raid has no heroic; Ulduar: its 25-player hard-mode drops).
--   Ranked "Mythic N" dungeon caches take the Heroic pool of the raid beside them on the ladder.
--
-- Copies: same item, new entry (+5: 4500000 + entry, +10: 4600000 + entry), item level raised, stats scaled the way
-- WotLK scales the same item between item levels (fitted on 901 stock pairs: stats ilvl^2.46, armor and block
-- ilvl^0.88, weapon damage ilvl^1.94). Gear only: weapons and armour, no tokens. Sorts last; re-runnable.

-- ------------------------------------------------------------------------------------------------ sources
DROP TEMPORARY TABLE IF EXISTS esteria_wl_map;
CREATE TEMPORARY TABLE esteria_wl_map (map SMALLINT UNSIGNED PRIMARY KEY, raid VARCHAR(8) NOT NULL);
INSERT INTO esteria_wl_map VALUES (533,'naxx'),(615,'osee'),(616,'osee'),(603,'uld'),(249,'ony'),(649,'toc'),(631,'icc'),(724,'rs'),
    (574,'dun'),(575,'dun'),(576,'dun'),(578,'dun'),(595,'dun'),(599,'dun'),(600,'dun'),(601,'dun'),(602,'dun'),(604,'dun'),
    (608,'dun'),(619,'dun'),(632,'dun'),(650,'dun'),(658,'dun'),(668,'dun');

-- lowest item level that is real raid loot (drops trash and quest leftovers)
DROP TEMPORARY TABLE IF EXISTS esteria_wl_floor;
CREATE TEMPORARY TABLE esteria_wl_floor (raid VARCHAR(8) PRIMARY KEY, floor_ilvl SMALLINT UNSIGNED NOT NULL);
INSERT INTO esteria_wl_floor VALUES ('dun',180),('naxx',200),('osee',200),('uld',219),('ony',232),('toc',232),('icc',251),('rs',258);

-- bosses and chests spawned by scripts (absent from creature/gameobject); IDs from the core's instance headers.
-- upper = Frostwing Halls (Valithria's chest, Sindragosa, Lich King); hard = Ulduar hard-mode chest.
DROP TEMPORARY TABLE IF EXISTS esteria_wl_scripted;
CREATE TEMPORARY TABLE esteria_wl_scripted (raid VARCHAR(8), diff TINYINT, kind CHAR(1), id INT UNSIGNED, upper TINYINT, hard TINYINT);
INSERT INTO esteria_wl_scripted VALUES
    ('toc',0,'c',34796,0,0),('toc',0,'c',34799,0,0),('toc',0,'c',35144,0,0),('toc',0,'c',34797,0,0),
    ('toc',0,'c',34780,0,0),('toc',0,'c',34497,0,0),('toc',0,'c',34496,0,0),('toc',0,'c',34564,0,0),
    ('toc',0,'g',195631,0,0),('toc',1,'g',195632,0,0),('toc',2,'g',195633,0,0),('toc',3,'g',195635,0,0),
    ('icc',0,'g',201873,0,0),('icc',1,'g',201874,0,0),('icc',2,'g',201872,0,0),('icc',3,'g',201875,0,0),
    ('icc',0,'g',202178,0,0),('icc',1,'g',202180,0,0),('icc',2,'g',202177,0,0),('icc',3,'g',202179,0,0),
    ('icc',0,'g',202239,0,0),('icc',1,'g',202240,0,0),('icc',2,'g',202238,0,0),('icc',3,'g',202241,0,0),
    ('icc',0,'g',201959,1,0),('icc',1,'g',202339,1,0),('icc',2,'g',202338,1,0),('icc',3,'g',202340,1,0),
    ('naxx',0,'g',181366,0,0),('naxx',1,'g',193426,0,0),
    ('uld',0,'g',195046,0,0),('uld',1,'g',195047,0,0),('uld',0,'g',194312,0,0),('uld',1,'g',194314,0,0),
    ('uld',0,'g',194307,0,0),('uld',1,'g',194308,0,0),('uld',0,'g',194200,0,1),('uld',1,'g',194201,0,1),
    ('uld',0,'g',194789,0,0),('uld',1,'g',194956,0,0),('uld',0,'g',194957,0,1),('uld',1,'g',194958,0,1),
    ('uld',0,'g',194821,0,0),('uld',1,'g',194822,0,0),
    ('dun',0,'g',191349,0,0),('dun',1,'g',193603,0,0),('dun',0,'g',190586,0,0),('dun',1,'g',193996,0,0),
    -- Trial of the Champion, Pit of Saron, Halls of Reflection
    ('dun',0,'c',35451,0,0),('dun',0,'c',36658,0,0),
    ('dun',0,'g',195709,0,0),('dun',1,'g',195710,0,0),('dun',0,'g',195374,0,0),('dun',1,'g',195375,0,0),
    ('dun',0,'g',195323,0,0),('dun',1,'g',195324,0,0),
    ('dun',0,'g',201710,0,0),('dun',0,'g',202212,0,0),('dun',1,'g',202336,0,0),('dun',1,'g',202337,0,0);

-- (raid, difficulty, loot table): diff 0/1/2/3 = 10N/25N/10H/25H for raids, normal/heroic for dungeons.
-- Spawns and loot come from Esteria's world (acore_world, read the same way as the port tool's stage_rows.sql):
-- Ascension changed WotLK loot in CoA's database (e.g. Forge of Souls heroic drops item level 200 there, 232 here).
DROP TEMPORARY TABLE IF EXISTS esteria_wl_diff;
CREATE TEMPORARY TABLE esteria_wl_diff (diff TINYINT PRIMARY KEY);
INSERT INTO esteria_wl_diff VALUES (0),(1),(2),(3);

DROP TEMPORARY TABLE IF EXISTS esteria_wl_boss;
CREATE TEMPORARY TABLE esteria_wl_boss (raid VARCHAR(8), entry INT UNSIGNED, upper TINYINT, PRIMARY KEY (raid, entry));
INSERT IGNORE INTO esteria_wl_boss SELECT m.raid, c.id, c.id IN (36853, 36597)
FROM acore_world.creature c JOIN esteria_wl_map m ON m.map = c.map;
INSERT IGNORE INTO esteria_wl_boss SELECT raid, id, upper FROM esteria_wl_scripted WHERE kind = 'c';

DROP TEMPORARY TABLE IF EXISTS esteria_wl_src;
CREATE TEMPORARY TABLE esteria_wl_src (raid VARCHAR(8), diff TINYINT, kind CHAR(1), lootid INT UNSIGNED, upper TINYINT, hard TINYINT,
    KEY (kind, lootid));
INSERT INTO esteria_wl_src
SELECT b.raid, d.diff, 'c', CASE d.diff WHEN 0 THEN ct.lootid WHEN 1 THEN c1.lootid WHEN 2 THEN c2.lootid ELSE c3.lootid END, b.upper, 0
FROM esteria_wl_boss b
JOIN acore_world.creature_template ct ON ct.entry = b.entry
JOIN esteria_wl_diff d
LEFT JOIN acore_world.creature_template c1 ON c1.entry = ct.difficulty_entry_1
LEFT JOIN acore_world.creature_template c2 ON c2.entry = ct.difficulty_entry_2
LEFT JOIN acore_world.creature_template c3 ON c3.entry = ct.difficulty_entry_3;
INSERT INTO esteria_wl_src
SELECT DISTINCT m.raid, d.diff, 'g', gt.Data1, 0, 0
FROM acore_world.gameobject g JOIN esteria_wl_map m ON m.map = g.map
JOIN acore_world.gameobject_template gt ON gt.entry = g.id AND gt.type = 3 AND gt.Data1 > 0
JOIN esteria_wl_diff d ON g.spawnMask & (1 << d.diff);
INSERT INTO esteria_wl_src
SELECT s.raid, s.diff, 'g', gt.Data1, s.upper, s.hard
FROM esteria_wl_scripted s JOIN acore_world.gameobject_template gt ON s.kind = 'g' AND gt.entry = s.id AND gt.Data1 > 0;
DELETE FROM esteria_wl_src WHERE lootid IS NULL OR lootid = 0;

-- loot rows -> items through up to two reference levels; LootMode > 1 = Ulduar hard mode
DROP TEMPORARY TABLE IF EXISTS esteria_wl_loot;
CREATE TEMPORARY TABLE esteria_wl_loot (kind CHAR(1), Entry INT UNSIGNED, Item INT UNSIGNED, Reference INT, LootMode SMALLINT UNSIGNED,
    KEY (kind, Entry));
INSERT INTO esteria_wl_loot SELECT 'c', Entry, Item, Reference, LootMode FROM acore_world.creature_loot_template
    WHERE Entry IN (SELECT lootid FROM esteria_wl_src WHERE kind = 'c');
INSERT INTO esteria_wl_loot SELECT 'g', Entry, Item, Reference, LootMode FROM acore_world.gameobject_loot_template
    WHERE Entry IN (SELECT lootid FROM esteria_wl_src WHERE kind = 'g');

DROP TEMPORARY TABLE IF EXISTS esteria_wl_item;
CREATE TEMPORARY TABLE esteria_wl_item (raid VARCHAR(8), diff TINYINT, upper TINYINT, hard TINYINT, item INT UNSIGNED, KEY (item));
INSERT INTO esteria_wl_item
SELECT s.raid, s.diff, s.upper, s.hard OR l.LootMode > 1, COALESCE(NULLIF(r2.Item, 0), NULLIF(r1.Item, 0), l.Item)
FROM esteria_wl_src s
JOIN esteria_wl_loot l ON l.kind = s.kind AND l.Entry = s.lootid
LEFT JOIN acore_world.reference_loot_template r1 ON l.Reference <> 0 AND r1.Entry = l.Reference
LEFT JOIN acore_world.reference_loot_template r2 ON r1.Reference <> 0 AND r2.Entry = r1.Reference;

-- gear only (weapons and armour you can wear; no shirts, tabards, bags, tokens). Judged on Esteria's own rows:
-- Ascension rebalanced many WotLK items in CoA's database, and the stage keeps Esteria's row for stock items anyway.
-- (acore_world is Esteria's world; the port tool's stage_rows.sql reads it the same way.)
DROP TEMPORARY TABLE IF EXISTS esteria_wl_gear;
CREATE TEMPORARY TABLE esteria_wl_gear (raid VARCHAR(8), diff TINYINT, upper TINYINT, hard TINYINT, item INT UNSIGNED,
    PRIMARY KEY (raid, diff, upper, hard, item));
INSERT IGNORE INTO esteria_wl_gear
SELECT w.raid, w.diff, w.upper, w.hard, i.entry
FROM esteria_wl_item w
JOIN acore_world.item_template i ON i.entry = w.item
JOIN item_template coa ON coa.entry = w.item
JOIN esteria_wl_floor f ON f.raid = w.raid AND i.ItemLevel >= f.floor_ilvl
WHERE i.class IN (2, 4) AND i.InventoryType NOT IN (0, 4, 18, 19)
  AND i.Quality IN (3, 4) AND (w.raid = 'dun' OR i.Quality = 4);

-- ------------------------------------------------------------------------------------------------ pools
-- upper: NULL = whole raid, 0 = without Frostwing Halls, 1 = Frostwing Halls only
DROP TEMPORARY TABLE IF EXISTS esteria_wl_pool;
CREATE TEMPORARY TABLE esteria_wl_pool (pool VARCHAR(8), raid VARCHAR(8), upper TINYINT NULL);
INSERT INTO esteria_wl_pool VALUES
    ('dun','dun',NULL),('t7','naxx',NULL),('t7','osee',NULL),('uld','uld',NULL),('ony','ony',NULL),
    ('uldony','uld',NULL),('uldony','ony',NULL),('toc','toc',NULL),('iccl','icc',0),('iccu','icc',1),('iccu','rs',NULL),
    ('iccall','icc',NULL),('iccall','rs',NULL);

DROP TEMPORARY TABLE IF EXISTS esteria_wl_has_d3;
CREATE TEMPORARY TABLE esteria_wl_has_d3 (raid VARCHAR(8) PRIMARY KEY) SELECT DISTINCT raid FROM esteria_wl_gear WHERE diff = 3;

DROP TEMPORARY TABLE IF EXISTS esteria_wl_member;
CREATE TEMPORARY TABLE esteria_wl_member (pool VARCHAR(8), tier CHAR(1), item INT UNSIGNED, bump TINYINT,
    PRIMARY KEY (pool, tier, item));
INSERT IGNORE INTO esteria_wl_member
SELECT p.pool, t.tier, g.item, CASE t.tier WHEN 'N' THEN 0 WHEN 'H' THEN 5 ELSE 10 END
FROM esteria_wl_pool p
JOIN esteria_wl_gear g ON g.raid = p.raid AND (p.upper IS NULL OR g.upper = p.upper)
JOIN (SELECT 'N' tier UNION SELECT 'H' UNION SELECT 'M') t
WHERE (t.tier = 'N' AND g.diff = 0)
   OR (t.tier = 'H' AND g.diff = 1)
   OR (t.tier = 'M' AND (g.diff = 3 OR (g.diff = 1 AND g.raid NOT IN (SELECT raid FROM esteria_wl_has_d3)
                                       AND (g.raid <> 'uld' OR g.hard = 1))));

-- every Classic pool the enabled endgame caches roll -> WotLK pool and tier
DROP TEMPORARY TABLE IF EXISTS esteria_wl_ref;
CREATE TEMPORARY TABLE esteria_wl_ref (ref INT UNSIGNED PRIMARY KEY, pool VARCHAR(8), tier CHAR(1));
INSERT INTO esteria_wl_ref VALUES
    (9003001,'dun','N'),(9003101,'dun','N'),
    (9003002,'dun','H'),(9003102,'dun','H'),(9003204,'dun','H'),
    (9003103,'dun','M'),(9002030,'dun','M'),(9003205,'dun','M'),
    (9003201,'t7','N'),(9003202,'t7','H'),(9003203,'t7','M'),(9002022,'t7','M'),
    (9002001,'uld','N'),(9002002,'uld','H'),(9002003,'uld','M'),(9003404,'uld','M'),
    (9002010,'ony','N'),(9003406,'ony','H'),(9003405,'ony','M'),
    (9002040,'uldony','N'),(9002041,'uldony','H'),(9002042,'uldony','M'),
    (9003401,'toc','N'),(9003402,'toc','H'),(9003403,'toc','M'),(9003504,'toc','M'),
    (9003501,'iccl','N'),(9003502,'iccl','H'),(9003503,'iccl','M'),(9003604,'iccl','M'),
    (9003601,'iccu','N'),(9003602,'iccu','H'),(9003603,'iccu','M'),(9003704,'iccu','M'),
    (9003701,'iccall','N'),(9003702,'iccall','H'),(9003703,'iccall','M'),
    -- ranked Mythic dungeon caches: the Heroic pool of the raid beside them
    (9003801,'uld','H'),(9002031,'uld','H'),
    (9003802,'uldony','H'),(9003407,'uldony','H'),(9003505,'uldony','H'),
    (9003803,'iccl','H'),(9003506,'iccl','H'),(9003605,'iccl','H'),(9003705,'iccl','H'),
    (9003804,'iccall','H'),(9003706,'iccall','H');

-- ------------------------------------------------------------------------------------------------ copies
DELETE FROM item_template WHERE entry BETWEEN 4500000 AND 4699999;

DROP TEMPORARY TABLE IF EXISTS esteria_wl_copy;
CREATE TEMPORARY TABLE esteria_wl_copy SELECT i.* FROM item_template i WHERE 0;
ALTER TABLE esteria_wl_copy ADD COLUMN wl_bump TINYINT NOT NULL DEFAULT 0;
-- Esteria's stats, CoA's display ID: the port pipeline translates CoA display IDs to Esteria's client art
INSERT INTO esteria_wl_copy
SELECT i.*, b.bump FROM acore_world.item_template i
JOIN (SELECT DISTINCT m.item, m.bump FROM esteria_wl_member m JOIN esteria_wl_ref r ON r.pool = m.pool AND r.tier = m.tier
      WHERE m.bump > 0) b ON b.item = i.entry;
UPDATE esteria_wl_copy c JOIN item_template coa ON coa.entry = c.entry SET c.displayid = coa.displayid;
-- MySQL applies SET left to right, so ItemLevel goes last
UPDATE esteria_wl_copy SET
    stat_value1  = ROUND(stat_value1  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value2  = ROUND(stat_value2  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value3  = ROUND(stat_value3  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value4  = ROUND(stat_value4  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value5  = ROUND(stat_value5  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value6  = ROUND(stat_value6  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value7  = ROUND(stat_value7  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value8  = ROUND(stat_value8  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value9  = ROUND(stat_value9  * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    stat_value10 = ROUND(stat_value10 * POW((ItemLevel + wl_bump) / ItemLevel, 2.46)),
    armor        = ROUND(armor        * POW((ItemLevel + wl_bump) / ItemLevel, 0.88)),
    block        = ROUND(block        * POW((ItemLevel + wl_bump) / ItemLevel, 0.88)),
    dmg_min1     = dmg_min1 * POW((ItemLevel + wl_bump) / ItemLevel, 1.94),
    dmg_max1     = dmg_max1 * POW((ItemLevel + wl_bump) / ItemLevel, 1.94),
    dmg_min2     = dmg_min2 * POW((ItemLevel + wl_bump) / ItemLevel, 1.94),
    dmg_max2     = dmg_max2 * POW((ItemLevel + wl_bump) / ItemLevel, 1.94),
    description  = IF(wl_bump = 5, 'Manastorm Heroic', 'Manastorm Mythic'),
    entry        = entry + IF(wl_bump = 5, 4500000, 4600000),
    ItemLevel    = ItemLevel + wl_bump;
ALTER TABLE esteria_wl_copy DROP COLUMN wl_bump;
INSERT INTO item_template SELECT * FROM esteria_wl_copy;
DROP TEMPORARY TABLE esteria_wl_copy;

-- ------------------------------------------------------------------------------------------------ pools refilled
DELETE t FROM reference_loot_template t JOIN esteria_wl_ref r ON r.ref = t.Entry;
INSERT INTO reference_loot_template (Entry, Item, Reference, Chance, QuestRequired, LootMode, GroupId, MinCount, MaxCount, Comment)
SELECT r.ref, m.item + CASE m.bump WHEN 5 THEN 4500000 WHEN 10 THEN 4600000 ELSE 0 END, 0, 0, 0, 1, 1, 1, 1,
       CONCAT('Esteria WotLK Manastorm pool ', r.pool, ' ', r.tier)
FROM esteria_wl_ref r JOIN esteria_wl_member m ON m.pool = r.pool AND m.tier = r.tier;

-- Normal Dungeons cache lists its gear directly
DELETE FROM item_loot_template WHERE Entry = 1278050 AND Reference = 0;
INSERT INTO item_loot_template (Entry, Item, Reference, Chance, QuestRequired, LootMode, GroupId, MinCount, MaxCount, Comment)
SELECT 1278050, item, 0, 0, 0, 1, 1, 1, 1, 'Esteria WotLK Manastorm pool dun N'
FROM esteria_wl_member WHERE pool = 'dun' AND tier = 'N';

-- ------------------------------------------------------------------------------------------------ names
DROP TEMPORARY TABLE IF EXISTS esteria_wl_name;
CREATE TEMPORARY TABLE esteria_wl_name (entry INT UNSIGNED PRIMARY KEY, name VARCHAR(80));
INSERT INTO esteria_wl_name VALUES
    (1278052,'Naxxramas'),(1278053,'Heroic Naxxramas'),(1278055,'Mythic Naxxramas'),
    (1278056,'Ulduar'),(1278058,'Heroic Ulduar'),(1278060,'Mythic Ulduar'),
    (1278061,'Onyxia & Ulduar'),(1278063,'Heroic Onyxia & Ulduar'),(1278065,'Mythic Onyxia & Ulduar'),
    (1278066,'Trial of the Crusader'),(1278068,'Heroic Trial of the Crusader'),(1278069,'Mythic Trial of the Crusader'),
    (1278070,'Icecrown Citadel'),(1278072,'Heroic Icecrown Citadel'),(1278074,'Mythic Icecrown Citadel'),
    (1278075,'Frostwing Halls & Ruby Sanctum'),(1278077,'Heroic Frostwing Halls & Ruby Sanctum'),
    (1278078,'Mythic Frostwing Halls & Ruby Sanctum'),
    (1278079,'Icecrown & Ruby Sanctum'),(1278081,'Heroic Icecrown & Ruby Sanctum'),(1278083,'Mythic Icecrown & Ruby Sanctum');
UPDATE item_template i JOIN esteria_wl_name n ON n.entry = i.entry SET i.name = CONCAT('Manastorm Cache: ', n.name);

-- tooltips: written from the cache's own depth bracket and roll groups (CoA's named Classic raids)
DROP TEMPORARY TABLE IF EXISTS esteria_wl_label;
CREATE TEMPORARY TABLE esteria_wl_label (pool VARCHAR(8) PRIMARY KEY, label VARCHAR(48));
INSERT INTO esteria_wl_label VALUES ('dun','Dungeon'),('t7','Naxxramas'),('uld','Ulduar'),('ony','Onyxia''s Lair'),
    ('uldony','Onyxia & Ulduar'),('toc','Trial of the Crusader'),('iccl','Icecrown Citadel'),
    ('iccu','Frostwing Halls & Ruby Sanctum'),('iccall','Icecrown & Ruby Sanctum');
-- an ordinary table: MySQL can't open one temporary table twice in a statement
DROP TABLE IF EXISTS esteria_wl_line;
CREATE TABLE esteria_wl_line (entry INT UNSIGNED, sure TINYINT, grp TINYINT, line VARCHAR(80), KEY (entry));
-- a group whose chances add up to 100 always rolls once, so its lines count as "Contains"
INSERT INTO esteria_wl_line
SELECT l.Entry, g.total >= 100, l.GroupId,
       CONCAT('+ ', CASE r.tier WHEN 'N' THEN 'Normal' WHEN 'H' THEN 'Heroic' ELSE 'Mythic' END, ' ', b.label, ' Gear')
FROM item_loot_template l
JOIN (SELECT Entry, GroupId, SUM(Chance) total FROM item_loot_template WHERE Reference <> 0 GROUP BY Entry, GroupId) g
    ON g.Entry = l.Entry AND g.GroupId = l.GroupId
JOIN esteria_wl_ref r ON r.ref = l.Reference JOIN esteria_wl_label b ON b.pool = r.pool;
INSERT INTO esteria_wl_line VALUES (1278050, 1, 1, '+ Normal Dungeon Gear');
UPDATE item_template i
JOIN manastorm_cache_bracket k ON k.cache_item_entry = i.entry AND k.track = 2 AND k.enabled = 1
SET i.description = CONCAT('Obtained from Manastorm depths ', k.min_value,
        IF(k.max_value = 4294967295, ' and deeper', CONCAT(' to ', k.max_value)), CHAR(10), 'Contains:',
        COALESCE((SELECT GROUP_CONCAT(DISTINCT CONCAT(CHAR(10), x.line) ORDER BY x.grp SEPARATOR '')
         FROM esteria_wl_line x WHERE x.entry = i.entry AND x.sure = 1), ''),
        COALESCE((SELECT CONCAT(CHAR(10), 'Chance to contain:', GROUP_CONCAT(DISTINCT CONCAT(CHAR(10), x.line) ORDER BY x.grp SEPARATOR ''))
         FROM esteria_wl_line x WHERE x.entry = i.entry AND x.sure = 0
           AND x.line NOT IN (SELECT y.line FROM esteria_wl_line y WHERE y.entry = i.entry AND y.sure = 1)
         HAVING COUNT(*) > 0), ''))
WHERE EXISTS (SELECT 1 FROM esteria_wl_line x WHERE x.entry = i.entry);
DROP TEMPORARY TABLE esteria_wl_label;
DROP TABLE esteria_wl_line;

-- ------------------------------------------------------------------------------------------------ self-check
-- every mapped pool non-empty; copies exist for every copied row; nothing points at a missing item
SELECT r.pool, r.tier, COUNT(DISTINCT r.ref) refs, COUNT(*) / COUNT(DISTINCT r.ref) items_per_pool,
       MIN(i.ItemLevel) min_ilvl, MAX(i.ItemLevel) max_ilvl
FROM esteria_wl_ref r JOIN reference_loot_template t ON t.Entry = r.ref JOIN item_template i ON i.entry = t.Item
GROUP BY r.pool, r.tier ORDER BY r.pool, r.tier;
SELECT 'missing items' chk, COUNT(*) FROM reference_loot_template t JOIN esteria_wl_ref r ON r.ref = t.Entry
    LEFT JOIN item_template i ON i.entry = t.Item WHERE i.entry IS NULL;
SELECT 'empty pools' chk, COUNT(*) FROM esteria_wl_ref r WHERE NOT EXISTS (SELECT 1 FROM reference_loot_template t WHERE t.Entry = r.ref);

DROP TEMPORARY TABLE esteria_wl_map;
DROP TEMPORARY TABLE esteria_wl_floor;
DROP TEMPORARY TABLE esteria_wl_scripted;
DROP TEMPORARY TABLE esteria_wl_diff;
DROP TEMPORARY TABLE esteria_wl_boss;
DROP TEMPORARY TABLE esteria_wl_src;
DROP TEMPORARY TABLE esteria_wl_loot;
DROP TEMPORARY TABLE esteria_wl_item;
DROP TEMPORARY TABLE esteria_wl_gear;
DROP TEMPORARY TABLE esteria_wl_pool;
DROP TEMPORARY TABLE esteria_wl_has_d3;
DROP TEMPORARY TABLE esteria_wl_member;
DROP TEMPORARY TABLE esteria_wl_ref;
DROP TEMPORARY TABLE esteria_wl_name;
