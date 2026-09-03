-- Removes generated reference pools and any rows pointing at them.
START TRANSACTION;
DELETE FROM `reference_loot_template` WHERE `Entry` IN (3000000, 3000001, 3000002, 3000003, 3000004, 3000005) OR `Reference` IN (3000000, 3000001, 3000002, 3000003, 3000004, 3000005);
COMMIT;
