-- Cosmetics: retire the four ribbon-only entries from the wing batch (970300..970303).
-- sirus\Wings1..Wings5 are one recoloured ribbon-only effect (94 verts, six ribbon emitters,
-- no wing mesh), so on this client they render as a swirl instead of wings.  See
-- tools/wings_cosmetic_pack.py, which no longer ships ribbon-only models.
DELETE FROM `playercreateinfo_spell_custom`
 WHERE `Spell` IN (970300, 970301, 970302, 970303) AND `Note` = 'Cosmetics';
DELETE FROM `spell_group`
 WHERE `id` = 9100 AND `spell_id` IN (970300, 970301, 970302, 970303);
