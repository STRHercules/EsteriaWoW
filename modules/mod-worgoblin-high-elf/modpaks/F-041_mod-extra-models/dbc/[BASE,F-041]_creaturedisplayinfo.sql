-- [F-041] mod-extra-models: creaturedisplayinfo: 4 inserts, 0 updates, 0 deletes

-- New entries
/* Vulpera Mounts */
DELETE FROM `creaturedisplayinfo` WHERE `id` = 94211;
INSERT INTO `creaturedisplayinfo` (`id`, `model_id`, `sound_id`, `extended_display_info_id`, `creature_model_scale`, `creature_model_alpha`, `texture_variation_1`, `texture_variation_2`, `texture_variation_3`, `portrait_texture_name`, `blood_level`, `blood_id`, `npc_sound_id`, `praticle_color_id`, `creature_geoset_data`, `obj_effect_package_id`) VALUES (94211, 4888, 0, 0, 1, 255, 'caravan_hyena1_tan', 'caravan_hyena1_saddle', '', '', 1, 0, 0, 0, 0, 0);
DELETE FROM `creaturedisplayinfo` WHERE `id` = 94212;
INSERT INTO `creaturedisplayinfo` (`id`, `model_id`, `sound_id`, `extended_display_info_id`, `creature_model_scale`, `creature_model_alpha`, `texture_variation_1`, `texture_variation_2`, `texture_variation_3`, `portrait_texture_name`, `blood_level`, `blood_id`, `npc_sound_id`, `praticle_color_id`, `creature_geoset_data`, `obj_effect_package_id`) VALUES (94212, 4889, 0, 0, 1, 255, 'caravan_hyena2_tan', 'caravan_hyena2_saddle', '', '', 1, 0, 0, 0, 0, 0);

/* Vehicles */
DELETE FROM `creaturedisplayinfo` WHERE `id` = 94213;
INSERT INTO `creaturedisplayinfo` (`id`, `model_id`, `sound_id`, `extended_display_info_id`, `creature_model_scale`, `creature_model_alpha`, `texture_variation_1`, `texture_variation_2`, `texture_variation_3`, `portrait_texture_name`, `blood_level`, `blood_id`, `npc_sound_id`, `praticle_color_id`, `creature_geoset_data`, `obj_effect_package_id`) VALUES (94213, 4890, 0, 0, 1, 255, '', '', '', '', 0, 0, 0, 0, 0, 0); -- Gyrocopter
DELETE FROM `creaturedisplayinfo` WHERE `id` = 94215;
INSERT INTO `creaturedisplayinfo` (`id`, `model_id`, `sound_id`, `extended_display_info_id`, `creature_model_scale`, `creature_model_alpha`, `texture_variation_1`, `texture_variation_2`, `texture_variation_3`, `portrait_texture_name`, `blood_level`, `blood_id`, `npc_sound_id`, `praticle_color_id`, `creature_geoset_data`, `obj_effect_package_id`) VALUES (94215, 4891, 0, 0, 1, 255, '', '', '', '', 0, 0, 0, 0, 0, 0); -- Explorer Gyrocopter
