-- Vulpera Retail five-byte codec; guarded against changed saved appearances.
-- Legacy ring/ear mismatches become the matching authored Retail accessory combination.
UPDATE `characters`
SET `skin`=6, `face`=7, `hairStyle`=3, `hairColor`=20, `facialStyle`=0, `extraAppearance`=0
WHERE `guid`=423 AND `race`=20
    AND `skin`=6
    AND `face`=1
    AND `hairStyle`=1
    AND `hairColor`=5
    AND `facialStyle`=52
    AND `extraAppearance`=0;
UPDATE `characters`
SET `skin`=10, `face`=17, `hairStyle`=2, `hairColor`=15, `facialStyle`=0, `extraAppearance`=0
WHERE `guid`=499 AND `race`=20
    AND `skin`=10
    AND `face`=5
    AND `hairStyle`=1
    AND `hairColor`=0
    AND `facialStyle`=31
    AND `extraAppearance`=0;
