-- Keep the legacy player Broken contract aligned with its client assets.
-- Race 14 is the Broken race used by the creator and Worgoblin scripts.

UPDATE `chrraces_dbc`
SET `Flags` = 12,
    `FactionID` = 2,
    `ExplorationSoundID` = 4141,
    `MaleDisplayId` = 60002,
    `FemaleDisplayId` = 60003,
    `ClientPrefix` = 'Bk',
    `BaseLanguage` = 1,
    `CreatureType` = 7,
    `ResSicknessSpellID` = 15007,
    `SplashSoundID` = 1096,
    `ClientFilestring` = 'Broken',
    `CinematicSequenceID` = 0,
    `Alliance` = 1,
    `Name_Lang_enUS` = 'Broken',
    `Name_Lang_enGB` = 'Broken',
    `Name_Female_Lang_enUS` = 'Broken',
    `Name_Female_Lang_enGB` = 'Broken',
    `Name_Male_Lang_enUS` = 'Broken',
    `Name_Male_Lang_enGB` = 'Broken',
    `FacialHairCustomization_1` = 'NORMAL',
    `FacialHairCustomization_2` = 'HORNS',
    `HairCustomization` = 'NORMAL',
    `Required_Expansion` = 0
WHERE `ID` = 14;
