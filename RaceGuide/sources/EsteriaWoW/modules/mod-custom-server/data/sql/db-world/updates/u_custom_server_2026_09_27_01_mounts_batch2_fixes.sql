-- Batch #2 mount corrections.
-- Flying mounts use the conventional Golden Gryphon mount behavior instead of
-- the Magnificent Flying Carpet template so riders use the normal seated pose.
UPDATE `spell_dbc`
SET `Mechanic` = 21,
    `Attributes` = 269844752,
    `AttributesEx4` = 67108864,
    `AttributesEx6` = 131072,
    `AttributesEx7` = 512,
    `CastingTimeIndex` = 16,
    `InterruptFlags` = 31,
    `AuraInterruptFlags` = 128,
    `ProcChance` = 101,
    `SpellLevel` = 1,
    `DurationIndex` = 21,
    `RangeIndex` = 1,
    `EquippedItemClass` = -1,
    `Effect_1` = 6,
    `Effect_2` = 6,
    `Effect_3` = 6,
    `EffectDieSides_1` = 0,
    `EffectDieSides_2` = 1,
    `EffectDieSides_3` = 1,
    `EffectBasePoints_1` = 0,
    `EffectBasePoints_2` = 149,
    `EffectBasePoints_3` = 59,
    `ImplicitTargetA_1` = 1,
    `ImplicitTargetA_2` = 1,
    `EffectAura_1` = 78,
    `EffectAura_2` = 207,
    `EffectAura_3` = 32,
    `EffectTriggerSpell_1` = 0,
    `SpellVisualID_1` = 8504,
    `StartRecoveryCategory` = 0,
    `EffectChainAmplitude_1` = 1,
    `EffectChainAmplitude_2` = 1,
    `EffectChainAmplitude_3` = 1,
    `SchoolMask` = 1
WHERE `ID` IN (
    201201, 201202, 201204, 201205, 201207, 201208, 201209, 201210,
    201213, 201214, 201215, 201216, 201217, 201218, 201221, 201222,
    201223, 201224, 201225, 201226, 201227, 201231, 201232, 201233,
    201234, 201235, 201236, 201237, 201241, 201242, 201243, 201244,
    201245, 201251, 201252, 201253, 201254, 201255
);

-- Infernal CreatureDisplayInfo texture slots follow the donor ordering:
-- metal, rock, FX. The donor scale is 0.9.
UPDATE `creaturedisplayinfo_dbc`
SET `CreatureModelScale` = 0.9,
    `TextureVariation_1` = 'infernalmount_metal_red',
    `TextureVariation_2` = 'infernalmount_rock_red',
    `TextureVariation_3` = 'infernalmount_fx_purple'
WHERE `ID` = 94520;

UPDATE `creaturedisplayinfo_dbc`
SET `CreatureModelScale` = 0.9,
    `TextureVariation_1` = 'infernalmount_metal_blue',
    `TextureVariation_2` = 'infernalmount_rock_blue',
    `TextureVariation_3` = 'infernalmount_fx_blue'
WHERE `ID` = 94546;

UPDATE `creaturedisplayinfo_dbc`
SET `CreatureModelScale` = 0.9,
    `TextureVariation_1` = 'infernalmount_metal_green',
    `TextureVariation_2` = 'infernalmount_rock_green',
    `TextureVariation_3` = 'infernalmount_fx_green'
WHERE `ID` = 94547;

UPDATE `creaturedisplayinfo_dbc`
SET `CreatureModelScale` = 0.9,
    `TextureVariation_1` = 'infernalmount_metal_ice',
    `TextureVariation_2` = 'infernalmount_rock_ice',
    `TextureVariation_3` = 'infernalmount_fx_ice'
WHERE `ID` = 94548;

UPDATE `creaturedisplayinfo_dbc`
SET `CreatureModelScale` = 0.9,
    `TextureVariation_1` = 'infernalmount_metal_lava',
    `TextureVariation_2` = 'infernalmount_rock_lava',
    `TextureVariation_3` = 'infernalmount_fx_lava'
WHERE `ID` = 94549;

UPDATE `creaturedisplayinfo_dbc`
SET `CreatureModelScale` = 0.9,
    `TextureVariation_1` = 'infernalmount_metal_red',
    `TextureVariation_2` = 'infernalmount_rock_red',
    `TextureVariation_3` = 'infernalmount_fx_purple'
WHERE `ID` = 94550;

-- Kukulkan's imported mesh is authored much larger than the surrounding mount
-- set. Keep the source M2 intact and correct the display scale instead.
UPDATE `creaturedisplayinfo_dbc`
SET `CreatureModelScale` = 0.3
WHERE `ID` = 94521;
