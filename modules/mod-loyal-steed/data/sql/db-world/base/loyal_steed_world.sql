-- mod-loyal-steed world SQL
-- Credits: mod-improved-bank storage by silviu20092 (MIT License)

-- Loyal Steed NPC (creature_template)
DELETE FROM creature_template WHERE entry = 900010;
INSERT INTO creature_template (entry, name, subname, gossip_menu_id, minlevel, maxlevel, faction, npcflag, speed_walk, speed_run, speed_swim, speed_flight, detection_range, `rank`, dmgschool, DamageModifier, BaseAttackTime, RangeAttackTime, BaseVariance, RangeVariance, unit_class, unit_flags, unit_flags2, dynamicflags, family, type, lootid, pickpocketloot, skinloot, PetSpellDataId, VehicleId, mingold, maxgold, MovementType, HoverHeight, HealthModifier, ManaModifier, ArmorModifier, ExperienceModifier, RacialLeader, movementId, RegenHealth, flags_extra, ScriptName)
VALUES (900010, 'Loyal Steed', 'Loyal Companion', 0, 80, 80, 35, 1153, 1, 2.5, 1, 1, 20, 0, 0, 0, 0, 0, 1, 1, 1, 770, 2048, 0, 0, 2, 0, 0, 0, 0, 486, 0, 0, 0, 1, 10, 1, 1, 1, 0, 0, 1, 2, 'npc_rangers_war_horse');

-- Loyal Steed default display (Warhorse)
DELETE FROM creature_template_model WHERE CreatureID = 900010;
INSERT INTO creature_template_model (CreatureID, Idx, CreatureDisplayID, DisplayScale, Probability)
VALUES (900010, 0, 28918, 1, 1);

-- Loyal Steed Deed item
DELETE FROM item_template WHERE entry = 900001;
INSERT INTO item_template (entry, class, subclass, SoundOverrideSubclass, name, displayid, Quality, Flags, BuyCount, BuyPrice, SellPrice, InventoryType, AllowableClass, AllowableRace, ItemLevel, RequiredLevel, bonding, description, stackable, spellid_1, spelltrigger_1, spellcharges_1, ScalingStatDistribution, ScriptName)
VALUES (900001, 12, 0, -1, 'Loyal Steed Deed', 13956, 1, 64, 1, 1000000, 500000, 0, -1, -1, 1, 1, 1, 'Use to bond with your Loyal Steed companion. Visit your racial mount vendor to purchase.', 1, 900012, 0, 0, 0, 'item_rangers_war_horse_deed');

-- Companion spell script
DELETE FROM spell_script_names WHERE spell_id = 900012;
INSERT INTO spell_script_names (spell_id, ScriptName) VALUES (900012, 'spell_rangers_war_horse_summon');

-- Add deed to all racial mount vendors
DELETE FROM npc_vendor WHERE item = 900001;
INSERT INTO npc_vendor (entry, item, maxcount, incrtime, ExtendedCost, VerifiedBuild) VALUES
(384,   900001, 0, 0, 0, 0),  -- Katie Hunter (Human)
(1261,  900001, 0, 0, 0, 0),  -- Veron Amberstill (Dwarf)
(7955,  900001, 0, 0, 0, 0),  -- Milli Featherwhistle (Gnome)
(4730,  900001, 0, 0, 0, 0),  -- Lelanai (Night Elf)
(17584, 900001, 0, 0, 0, 0),  -- Torallius the Pack Handler (Draenei)
(3362,  900001, 0, 0, 0, 0),  -- Ogunaro Wolfrunner (Orc)
(7952,  900001, 0, 0, 0, 0),  -- Zjolnir (Troll)
(3685,  900001, 0, 0, 0, 0),  -- Harb Clawhoof (Tauren)
(4731,  900001, 0, 0, 0, 0),  -- Zachariah Post (Undead)
(16264, 900001, 0, 0, 0, 0);  -- Winaestra (Blood Elf)

-- Custom spells via spell_dbc (no DBC file modification needed)
DELETE FROM spell_dbc WHERE ID IN (900011, 900012);
INSERT INTO spell_dbc (ID, Attributes, AttributesEx3, CastingTimeIndex, DurationIndex, RangeIndex, Effect_1, ImplicitTargetA_1, EffectMiscValue_1, SpellIconID, Name_Lang_enUS)
VALUES (900011, 262416, 536870912, 1, 21, 1, 28, 0, 900010, 1812, 'Loyal Steed');

INSERT INTO spell_dbc (ID, Attributes, AttributesEx3, CastingTimeIndex, DurationIndex, RangeIndex, InterruptFlags, ProcChance, EquippedItemClass, Effect_1, EffectDieSides_1, ImplicitTargetA_1, EffectMultipleValue_1, EffectMiscValue_1, EffectMiscValueB_1, SpellVisualID_1, SpellIconID, Name_Lang_Mask, NameSubtext_Lang_Mask, Description_Lang_Mask, AuraDescription_Lang_Mask, Description_Lang_enUS, StartRecoveryCategory, StartRecoveryTime, SchoolMask, EffectChainAmplitude_1, EffectChainAmplitude_2, EffectChainAmplitude_3)
VALUES (900012, 262416, 536870912, 1, 21, 1, 31, 101, -1, 28, 1, 32, 1000, 900010, 41, 353, 1522, 16712190, 16712190, 16712190, 16712190, 'Right Click to summon and dismiss your steed.', 133, 1500, 1, 1, 1, 1);
