-- HelmetGeosetVisData: custom race 15 (Sethrak), bit 32768
-- Sethrak needed no dedicated masks in the source mod because every mask it
-- would touch was already a "hide for nearly every race" universal mask
-- that had reused the source mod's race-14 (Mag'har Orc) bit by default -- the
-- same pattern that let race 13/14 skip explicit lines on those rows.
-- Reusing that bit as race 14 (mag'har orc) here means sethrak has to move to
-- race 15 and pick up the same columns explicitly.
-- Idempotent: safe to re-run

UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | @SethrakHelmetMask, `hide_geoset_5` = `hide_geoset_5` | @SethrakHelmetMask WHERE `id` = 246;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_2` = `hide_geoset_2` | @SethrakHelmetMask, `hide_geoset_3` = `hide_geoset_3` | @SethrakHelmetMask, `hide_geoset_4` = `hide_geoset_4` | @SethrakHelmetMask WHERE `id` = 247;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | @SethrakHelmetMask, `hide_geoset_2` = `hide_geoset_2` | @SethrakHelmetMask, `hide_geoset_3` = `hide_geoset_3` | @SethrakHelmetMask, `hide_geoset_4` = `hide_geoset_4` | @SethrakHelmetMask, `hide_geoset_5` = `hide_geoset_5` | @SethrakHelmetMask WHERE `id` = 248;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | @SethrakHelmetMask WHERE `id` = 249;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | @SethrakHelmetMask, `hide_geoset_5` = `hide_geoset_5` | @SethrakHelmetMask WHERE `id` = 265;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | @SethrakHelmetMask, `hide_geoset_2` = `hide_geoset_2` | @SethrakHelmetMask, `hide_geoset_3` = `hide_geoset_3` | @SethrakHelmetMask, `hide_geoset_4` = `hide_geoset_4` | @SethrakHelmetMask, `hide_geoset_5` = `hide_geoset_5` | @SethrakHelmetMask WHERE `id` = 368;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_2` = `hide_geoset_2` | @SethrakHelmetMask, `hide_geoset_3` = `hide_geoset_3` | @SethrakHelmetMask, `hide_geoset_4` = `hide_geoset_4` | @SethrakHelmetMask WHERE `id` = 369;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_7` = `hide_geoset_7` | @SethrakHelmetMask WHERE `id` = 370;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_5` = `hide_geoset_5` | @SethrakHelmetMask, `hide_geoset_6` = `hide_geoset_6` | @SethrakHelmetMask WHERE `id` = 371;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_5` = `hide_geoset_5` | @SethrakHelmetMask WHERE `id` = 372;
UPDATE `helmetgeosetvisdata` SET `hide_geoset_1` = `hide_geoset_1` | @SethrakHelmetMask, `hide_geoset_5` = `hide_geoset_5` | @SethrakHelmetMask WHERE `id` = 376;
