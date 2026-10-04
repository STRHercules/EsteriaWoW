-- Vulpera codec v2: preserve source choices while adding all authored eye palettes/styles.
UPDATE `characters` SET `hairColor`=38, `facialStyle`=0
WHERE `guid`=423 AND `race`=20 AND `class`=2 AND `gender`=0
    AND `skin`=6
    AND `face`=7
    AND `hairStyle`=3
    AND `hairColor`=20
    AND `facialStyle`=0 AND `extraAppearance`=0;
UPDATE `characters` SET `hairColor`=33, `facialStyle`=0
WHERE `guid`=499 AND `race`=20 AND `class`=2 AND `gender`=0
    AND `skin`=10
    AND `face`=17
    AND `hairStyle`=2
    AND `hairColor`=15
    AND `facialStyle`=0 AND `extraAppearance`=0;
