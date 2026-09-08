-- DB update 2026_09_01_00 -> 2026_09_03_00
-- Restore Worgen's client-compatible display references.
UPDATE `chrraces_dbc`
SET `MaleDisplayId` = 29422,
    `FemaleDisplayId` = 29423
WHERE `ID` = 12;

-- Remove obsolete Worgen Mage starting spells absent from SpellStore.
DELETE FROM `playercreateinfo_spell_custom`
WHERE `racemask` = 2048
  AND `classmask` = 128
  AND `Spell` IN (22018, 22019);
