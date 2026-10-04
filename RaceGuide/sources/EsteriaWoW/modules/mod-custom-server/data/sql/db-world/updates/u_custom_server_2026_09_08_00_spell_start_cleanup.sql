-- Remove level-, trainer-, or talent-gated spells from custom character creation.
-- Their normal level-up/trainer/talent paths remain responsible for teaching them.
DELETE FROM `playercreateinfo_spell_custom`
WHERE `Spell` IN (27222, 33776, 3127, 674, 750, 5420);

-- Mail is a level-40 unlock for Hunters and Shamans, but is valid at creation for
-- Warriors and Paladins.
DELETE FROM `playercreateinfo_spell_custom`
WHERE `Spell` = 8737
  AND `classmask` IN (4, 64);
