-- Kul Tiran (race 29) is Alliance: retain Common language only.
DELETE FROM `playercreateinfo_spell_custom`
WHERE `racemask` = 268435456
  AND `Spell` IN (669, 670, 671, 672, 813, 814, 815, 816, 817, 7340, 7341, 17737, 29932);

DELETE FROM `playercreateinfo_skills`
WHERE `raceMask` = 268435456
  AND `skill` IN (109, 111, 113, 115, 137, 138, 139, 140, 141, 313, 315, 673, 759);
