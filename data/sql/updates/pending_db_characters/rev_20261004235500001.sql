-- Cosmetics: stop granting the four ribbon-only wing effects to characters (970300..970303).
DELETE FROM `character_spell`
 WHERE `spell` IN (970300, 970301, 970302, 970303);
