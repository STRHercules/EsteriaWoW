-- Move previously imported Battlemon shiny model-info rows out of Broken's display-ID range.
UPDATE `creature_model_info` SET `DisplayID` = `DisplayID` + 10000
WHERE `DisplayID` BETWEEN 60001 AND 61581
  AND ABS(`BoundingRadius` - 0.8) < 0.001
  AND ABS(`CombatReach` - 1.5) < 0.001
  AND `Gender` = 2
  AND `DisplayID_Other_Gender` = 0
  AND `VerifiedBuild` = 12340;
