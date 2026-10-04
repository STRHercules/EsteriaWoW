-- Keep both Illidari variants named Illidari in the character panel.
-- The donor clone left the gendered name fields as Eredar.
UPDATE `chrraces_dbc`
SET `Name_Lang_enUS` = 'Illidari',
    `Name_Female_Lang_enUS` = 'Illidari',
    `Name_Male_Lang_enUS` = 'Illidari',
    `Name_Lang_enGB` = 'Illidari',
    `Name_Female_Lang_enGB` = 'Illidari',
    `Name_Male_Lang_enGB` = 'Illidari'
WHERE `ID` IN (30, 31);
