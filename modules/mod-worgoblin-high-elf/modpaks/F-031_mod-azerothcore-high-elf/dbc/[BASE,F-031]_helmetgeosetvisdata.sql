-- [F-031] mod-azerothcore-high-elf: helmetgeosetvisdata: 0 inserts, 8 updates, 0 deletes

-- Changed values
UPDATE `helmetgeosetvisdata` SET `hide_geoset_5` = `hide_geoset_5` & ~8192 WHERE `id` = 246; -- -high elf
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | 8192 WHERE `id` = 285; -- +high elf
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | 8192 WHERE `id` = 305; -- +high elf
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | 8192 WHERE `id` = 306; -- +high elf
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | 8192 WHERE `id` = 307; -- +high elf
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | 8192 WHERE `id` = 345; -- +high elf
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | 8192 WHERE `id` = 366; -- +high elf
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | 8192 WHERE `id` = 367; -- +high elf
