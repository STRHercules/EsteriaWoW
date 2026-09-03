/* Enable the module's custom starting-spell path for Sethrak language. */
DELETE FROM `playercreateinfo_spell_custom` WHERE `raceMask` = 16384 AND `Spell` = 669;
INSERT INTO `playercreateinfo_spell_custom` (`raceMask`, `classMask`, `Spell`, `Note`) VALUES
(16384, 1, 669, 'Language Orcish'),
(16384, 2, 669, 'Language Orcish'),
(16384, 4, 669, 'Language Orcish'),
(16384, 8, 669, 'Language Orcish'),
(16384, 16, 669, 'Language Orcish'),
(16384, 32, 669, 'Language Orcish'),
(16384, 64, 669, 'Language Orcish'),
(16384, 128, 669, 'Language Orcish'),
(16384, 256, 669, 'Language Orcish'),
(16384, 1024, 669, 'Language Orcish');

/* Preserve existing spell rows while repairing current Sethrak characters. */
/* DELETE intentionally omitted; existing spell values remain intact. */
INSERT IGNORE INTO `acore_characters`.`character_spell` (`guid`, `spell`, `specMask`)
SELECT `c`.`guid`, 669, 255
FROM `acore_characters`.`characters` AS `c`
WHERE `c`.`race` = 15;
