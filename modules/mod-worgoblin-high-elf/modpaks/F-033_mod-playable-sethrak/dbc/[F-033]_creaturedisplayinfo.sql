-- creaturedisplayinfo: 0 inserts, 2 updates, 0 deletes

-- New entries
UPDATE `creaturedisplayinfo` SET `extended_display_info_id` = 45439 WHERE `id` = 94233; -- male unspecified entry (morph with gear)
UPDATE `creaturedisplayinfo` SET `extended_display_info_id` = 45440 WHERE `id` = 94234; -- female unspecified entry (morph with gear)
UPDATE `creaturedisplayinfo` SET `model_id` = 2370, `extended_display_info_id` = 45445, `creature_model_scale` = '1.0000000000000000' WHERE `id` = 94233; -- preserve morph-with-gear
UPDATE `creaturedisplayinfo` SET `model_id` = 2594, `extended_display_info_id` = 45446, `creature_model_scale` = '1.0000000000000000' WHERE `id` = 94234; -- preserve morph-with-gear
