REPLACE INTO `player_shapeshift_model` (
    `ShapeshiftID`, -- ID from SpellShapeshiftForm.dbc or spellshapeshiftform_dbc
    `RaceID`, -- ID from ChrRaces.dbc or chrraces_dbc
    `CustomizationID`, -- hair colour or skin colour
    `GenderID`, -- 0: male, 1: female, 2: both
    `ModelID` -- ID from CreatureDisplayInfo.dbc or creaturedisplayinfo_dbc (*not* from CreatureModelData.dbc!)
) VALUES
/* Sethraks copy Tauren */
(@CatForm, @Sethrak, 255, 2, 45339), -- ModelID
(@BearForm, @Sethrak, 255,	2, 2289), -- ModelID
(@DireBearForm, @Sethrak, 255, 2, 2289), -- ModelID
(@SwiftFlightForm, @Sethrak, 255, 2, 21244), -- ModelID
(@FlightForm, @Sethrak, 255, 2, 20872), -- ModelID
(@TravelForm, @Sethrak, 255, 2, 45339); -- ModelID: DruidTravelHorde
