-- Esteria caps at 80, CoA at 60. Normal-track caches stopped at 60, and a level with no bracket gets no cache,
-- so levels 61-79 earned nothing. Add four bands that work like 97877-97883: one cache item per band, one
-- equal-chance group of the green/blue gear that TBC and WotLK five-player dungeons drop at that required level.
-- Endgame (depth track) starts at the realm cap, 80, and is unchanged.
-- Sorts last so the zz snapshot files can't overwrite it. Re-runnable.

DROP TEMPORARY TABLE IF EXISTS esteria_band;
CREATE TEMPORARY TABLE esteria_band
(
    bracket_id INT UNSIGNED PRIMARY KEY,
    entry      INT UNSIGNED NOT NULL,
    min_level  TINYINT UNSIGNED NOT NULL,
    max_level  TINYINT UNSIGNED NOT NULL,
    max_ilvl   SMALLINT UNSIGNED NOT NULL,
    name       VARCHAR(64) NOT NULL
);
INSERT INTO esteria_band VALUES
    (8,  3390001, 61, 65, 115, 'Manastorm Cache (61-65)'),
    (9,  3390002, 66, 70, 115, 'Manastorm Cache (66-70)'), -- 115 = TBC heroic blues; drops a few odd higher rows
    (10, 3390003, 71, 75, 200, 'Manastorm Cache (71-75)'),
    (11, 3390004, 76, 79, 200, 'Manastorm Cache (76-79)');

-- cache items: copies of Manastorm Cache (51-59), which already carries item_manastorm_cache
DELETE i FROM item_template i JOIN esteria_band b ON b.entry = i.entry;
DROP TEMPORARY TABLE IF EXISTS esteria_cache;
CREATE TEMPORARY TABLE esteria_cache SELECT * FROM item_template WHERE entry = 97882;
UPDATE esteria_cache SET entry = 3390001, name = 'Manastorm Cache (61-65)';
INSERT INTO item_template SELECT * FROM esteria_cache;
UPDATE esteria_cache SET entry = 3390002, name = 'Manastorm Cache (66-70)';
INSERT INTO item_template SELECT * FROM esteria_cache;
UPDATE esteria_cache SET entry = 3390003, name = 'Manastorm Cache (71-75)';
INSERT INTO item_template SELECT * FROM esteria_cache;
UPDATE esteria_cache SET entry = 3390004, name = 'Manastorm Cache (76-79)';
INSERT INTO item_template SELECT * FROM esteria_cache;
DROP TEMPORARY TABLE esteria_cache;

-- gear dropped in TBC + WotLK five-player dungeons, directly or through one reference
DROP TEMPORARY TABLE IF EXISTS esteria_map;
CREATE TEMPORARY TABLE esteria_map (map SMALLINT UNSIGNED PRIMARY KEY);
INSERT INTO esteria_map VALUES
    (269),(540),(542),(543),(545),(546),(547),(552),(553),(554),(555),(556),(557),(558),(560),(585),
    (574),(575),(576),(578),(595),(599),(600),(601),(602),(604),(608),(619),(632),(650),(658),(668);

DROP TEMPORARY TABLE IF EXISTS esteria_drop;
CREATE TEMPORARY TABLE esteria_drop (entry INT UNSIGNED PRIMARY KEY);
INSERT IGNORE INTO esteria_drop
SELECT l.Item
FROM creature_loot_template l
JOIN creature_template ct ON ct.lootid = l.Entry
JOIN creature c ON c.id = ct.entry
JOIN esteria_map m ON m.map = c.map
WHERE l.Reference = 0;
INSERT IGNORE INTO esteria_drop
SELECT r.Item
FROM creature_loot_template l
JOIN reference_loot_template r ON r.Entry = l.Reference AND r.Reference = 0
JOIN creature_template ct ON ct.lootid = l.Entry
JOIN creature c ON c.id = ct.entry
JOIN esteria_map m ON m.map = c.map
WHERE l.Reference <> 0;

DELETE l FROM item_loot_template l JOIN esteria_band b ON b.entry = l.Entry;
INSERT INTO item_loot_template
    (Entry, Item, Reference, Chance, QuestRequired, LootMode, GroupId, MinCount, MaxCount, Comment)
SELECT b.entry, i.entry, 0, 0, 0, 1, 1, 1, 1, 'Manastorm dungeon equipment'
FROM esteria_band b
JOIN item_template i ON i.RequiredLevel BETWEEN b.min_level AND b.max_level AND i.ItemLevel <= b.max_ilvl
JOIN esteria_drop d ON d.entry = i.entry
WHERE i.Quality IN (2, 3) AND i.class IN (2, 4) AND i.InventoryType > 0;

-- brackets (1-7 are CoA's 11-60 bands)
INSERT INTO manastorm_cache_bracket
    (bracket_id, track, selector_kind, min_value, max_value, cache_item_entry, enabled, comment)
SELECT bracket_id, 1, 1, min_level, max_level, entry, 1, CONCAT('LEVEL_BAND: ', name, ' (Esteria)')
FROM esteria_band
ON DUPLICATE KEY UPDATE
    track = VALUES(track), selector_kind = VALUES(selector_kind), min_value = VALUES(min_value),
    max_value = VALUES(max_value), cache_item_entry = VALUES(cache_item_entry), enabled = VALUES(enabled),
    comment = VALUES(comment);

-- self-check: every band has a cache item, a bracket and a non-empty pool
SELECT b.name, (SELECT COUNT(*) FROM item_template WHERE entry = b.entry) AS item_rows,
       (SELECT COUNT(*) FROM manastorm_cache_bracket WHERE bracket_id = b.bracket_id) AS bracket_rows,
       (SELECT COUNT(*) FROM item_loot_template WHERE Entry = b.entry) AS pool
FROM esteria_band b;

DROP TEMPORARY TABLE esteria_band;
DROP TEMPORARY TABLE esteria_map;
DROP TEMPORARY TABLE esteria_drop;
