-- Retail utility mounts carry service NPCs, as the Traveler's Tundra Mammoth does: the mount creature names a vehicle
-- (Vehicle.dbc 910001-910006, client and server, seats on the retail model's attachments 40+) and its passengers.
-- Gossip for every service NPC and prop lives in lua_scripts/mount_services.lua.

DELETE FROM vehicle_template_accessory WHERE entry IN (4500040, 4500558, 4500208, 4500256, 4501008, 4500251);
DELETE FROM npc_vendor WHERE entry BETWEEN 4600001 AND 4600030;
DELETE FROM creature_template_model WHERE CreatureID BETWEEN 4600001 AND 4600030;
DELETE FROM creature_template WHERE entry BETWEEN 4600001 AND 4600030;

-- entry, source NPC (model and template), name, subname, npcflag (1 gossip, 0x80 vendor, 0x1000 repair,
-- 0x200000 auctioneer, 0x4000000 mailbox)
DROP TEMPORARY TABLE IF EXISTS mount_service;
CREATE TEMPORARY TABLE mount_service (entry INT UNSIGNED, source INT UNSIGNED, name VARCHAR(100), subname VARCHAR(100), npcflag INT UNSIGNED);
INSERT INTO mount_service VALUES
(4600001, 32639, 'Cousin Slowhands', 'Traveling Merchant', 0x1081),
(4600002, 8661, 'Caravan Auctioneer', 'Auctioneer', 0x200001),
(4600003, 8661, 'Caravan Merchant', 'Traveling Merchant', 0x1081),
(4600008, 8661, 'Caravan Postmaster', 'Postmaster', 0x4000001),
(4600004, 8661, 'Caravan Broker', 'Auctioneer & Merchant', 0x201081),
(4600005, 8661, 'Gilded Broker', 'Auctioneer & Postmaster', 0x4200001),
(4600006, 8661, 'Sporebearer Broker', 'Auctioneer, Merchant & Postmaster', 0x4201081),
(4600007, 32638, 'Hearthkeeper Porter', 'Merchant & Postmaster', 0x4001081),
(4600010, 32641, 'Mystic Birdhat', 'Transmogrifier', 0x1);
-- Birdhat is a goblin (Drix Blackwrench's look); its gossip casts mod-transmog's portable transmogrifier.

-- one clone per service row (8661 feeds three entries)
DROP TEMPORARY TABLE IF EXISTS mount_service_rows;
CREATE TEMPORARY TABLE mount_service_rows SELECT t.*, s.entry AS service_entry, s.name AS service_name,
    s.subname AS service_subname, s.npcflag AS service_npcflag
    FROM creature_template t JOIN mount_service s ON s.source = t.entry;
-- type_flags cleared: the Warpweaver's (190010) kept its transmogrifier clone from showing as a passenger.
UPDATE mount_service_rows SET entry = service_entry, name = service_name, subname = service_subname,
    npcflag = service_npcflag, faction = 35, gossip_menu_id = 0, type_flags = 0, ScriptName = '';
ALTER TABLE mount_service_rows DROP COLUMN service_entry, DROP COLUMN service_name, DROP COLUMN service_subname,
    DROP COLUMN service_npcflag;
INSERT INTO creature_template SELECT * FROM mount_service_rows;

INSERT INTO creature_template_model (CreatureID, Idx, CreatureDisplayID, DisplayScale, Probability, VerifiedBuild)
SELECT s.entry, m.Idx, m.CreatureDisplayID, m.DisplayScale, m.Probability, m.VerifiedBuild
FROM mount_service s JOIN creature_template_model m ON m.CreatureID = s.source;

-- Retail's mount pieces, as passengers: Yak sidecars and stalls (display 205001-205004, not selectable), and the
-- Packmaster's anvil (vendor and repair) and bag (transmog), which retail makes clickable instead of carrying NPCs.
-- Displays come from Tools/RetailAssets/mount_passengers.py (client registry rows + server dbc-continuations).
DROP TEMPORARY TABLE IF EXISTS mount_prop;
CREATE TEMPORARY TABLE mount_prop (entry INT UNSIGNED, source INT UNSIGNED, display INT UNSIGNED, name VARCHAR(100),
    subname VARCHAR(100), npcflag INT UNSIGNED, unit_flags INT UNSIGNED);
INSERT INTO mount_prop VALUES
(4600020, 4600001, 205001, 'Expedition Sidecar', '', 0, 0x02000002),
(4600021, 4600001, 205002, 'Expedition Sidecar', '', 0, 0x02000002),
(4600022, 4600001, 205003, 'Expedition Stall', '', 0, 0x02000002),
(4600023, 4600001, 205004, 'Expedition Stall', '', 0, 0x02000002),
-- The Packmaster's anvil and satchel: a blank name (a non-breaking space; MySQL trims a plain one) shows nothing overhead; an empty one reads "Unknown".
(4600024, 4600001, 205005, X'C2A0', '', 0x1081, 0x2),
(4600025, 4600001, 205006, X'C2A0', '', 0x1, 0x2);
DROP TEMPORARY TABLE IF EXISTS mount_prop_rows;
CREATE TEMPORARY TABLE mount_prop_rows SELECT t.*, p.entry AS prop_entry, p.name AS prop_name, p.subname AS prop_subname,
    p.npcflag AS prop_npcflag, p.unit_flags AS prop_unit_flags FROM creature_template t JOIN mount_prop p ON p.source = t.entry;
UPDATE mount_prop_rows SET entry = prop_entry, name = prop_name, subname = prop_subname, npcflag = prop_npcflag,
    unit_flags = prop_unit_flags, type_flags = 0, ScriptName = '';
ALTER TABLE mount_prop_rows DROP COLUMN prop_entry, DROP COLUMN prop_name, DROP COLUMN prop_subname,
    DROP COLUMN prop_npcflag, DROP COLUMN prop_unit_flags;
INSERT INTO creature_template SELECT * FROM mount_prop_rows;
INSERT INTO creature_template_model (CreatureID, Idx, CreatureDisplayID, DisplayScale, Probability, VerifiedBuild)
SELECT entry, 0, display, 1, 1, 12340 FROM mount_prop;
DELETE FROM creature_model_info WHERE DisplayID BETWEEN 205001 AND 205006;
INSERT INTO creature_model_info (DisplayID, BoundingRadius, CombatReach, Gender, DisplayID_Other_Gender, VerifiedBuild)
SELECT display, 0.5, 1, 2, 0, 12340 FROM mount_prop;

-- Merchants sell the Mammoth tinker's goods.
INSERT INTO npc_vendor (entry, slot, item, maxcount, incrtime, ExtendedCost, VerifiedBuild)
SELECT s.entry, v.slot, v.item, v.maxcount, v.incrtime, v.ExtendedCost, v.VerifiedBuild
FROM mount_service s JOIN npc_vendor v ON v.entry = 32639 WHERE s.npcflag & 0x80;
INSERT INTO npc_vendor (entry, slot, item, maxcount, incrtime, ExtendedCost, VerifiedBuild)
SELECT 4600024, slot, item, maxcount, incrtime, ExtendedCost, VerifiedBuild FROM npc_vendor WHERE entry = 32639;

UPDATE creature_template SET VehicleId = 910001 WHERE entry = 4500040; -- Grand Expedition Yak
UPDATE creature_template SET VehicleId = 910002 WHERE entry = 4500558; -- Mighty Caravan Brutosaur
UPDATE creature_template SET VehicleId = 910003 WHERE entry = 4500208; -- Trader's Gilded Brutosaur
UPDATE creature_template SET VehicleId = 910004 WHERE entry = 4500256; -- Sporebearer Fungal Strider
UPDATE creature_template SET VehicleId = 910005 WHERE entry = 4501008; -- Grizzly Hills Packmaster
UPDATE creature_template SET VehicleId = 910006 WHERE entry = 4500251; -- Hearthkeeper's Wandering Caravan (seat 2 is a player perch)

-- The core drops a vehicle's accessories unless the vehicle creature has a spell-click entry; 61424 is the Mammoth's
-- passenger ride, which also lets a friend take the Hearthkeeper's perch.
DELETE FROM npc_spellclick_spells WHERE npc_entry IN (4500040, 4500558, 4500208, 4500256, 4501008, 4500251);
INSERT INTO npc_spellclick_spells (npc_entry, spell_id, cast_flags, user_type) VALUES
(4500040, 61424, 1, 0), (4500558, 61424, 1, 0), (4500208, 61424, 1, 0),
(4500256, 61424, 1, 0), (4501008, 61424, 1, 0), (4500251, 61424, 1, 0);

-- minion 1 marks them accessories, which the core unsummons when they leave the seat (the rider dismounts).
INSERT INTO vehicle_template_accessory (entry, accessory_entry, seat_id, minion, description, summontype, summontimer) VALUES
(4500040, 4600020, 1, 1, 'Grand Expedition Yak - Sidecar', 6, 30000),
(4500040, 4600021, 2, 1, 'Grand Expedition Yak - Sidecar', 6, 30000),
(4500040, 4600022, 3, 1, 'Grand Expedition Yak - Stall', 6, 30000),
(4500040, 4600023, 4, 1, 'Grand Expedition Yak - Stall', 6, 30000),
(4500040, 4600001, 5, 1, 'Grand Expedition Yak - Merchant', 6, 30000),
(4500040, 4600010, 6, 1, 'Grand Expedition Yak - Transmogrifier', 6, 30000),
(4500558, 4600002, 1, 1, 'Mighty Caravan Brutosaur - Auctioneer', 6, 30000),
(4500558, 4600003, 2, 1, 'Mighty Caravan Brutosaur - Merchant', 6, 30000),
(4500208, 4600002, 1, 1, 'Trader''s Gilded Brutosaur - Auctioneer', 6, 30000),
(4500208, 4600008, 2, 1, 'Trader''s Gilded Brutosaur - Postmaster', 6, 30000),
(4500256, 4600006, 1, 1, 'Sporebearer Fungal Strider - Auctioneer, Merchant & Postmaster', 6, 30000),
(4501008, 4600024, 1, 1, 'Grizzly Hills Packmaster - Anvil (merchant)', 6, 30000),
(4501008, 4600025, 2, 1, 'Grizzly Hills Packmaster - Satchel (transmogrifier)', 6, 30000),
(4500251, 4600007, 1, 1, 'Hearthkeeper''s Wandering Caravan - Merchant & Postmaster', 6, 30000);
