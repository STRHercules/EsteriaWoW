-- Give the four additive car mounts independent vehicle and seat definitions.

DELETE FROM `vehicle_dbc` WHERE `ID` IN (900301, 900302, 900303, 900304);
INSERT INTO `vehicle_dbc` (`ID`, `Flags`, `TurnSpeed`, `PitchSpeed`, `PitchMin`, `PitchMax`, `SeatID_1`, `SeatID_2`, `SeatID_3`, `SeatID_4`, `SeatID_5`, `SeatID_6`, `SeatID_7`, `SeatID_8`, `MouseLookOffsetPitch`, `CameraFadeDistScalarMin`, `CameraFadeDistScalarMax`, `CameraPitchOffset`, `FacingLimitRight`, `FacingLimitLeft`, `MsslTrgtTurnLingering`, `MsslTrgtPitchLingering`, `MsslTrgtMouseLingering`, `MsslTrgtEndOpacity`, `MsslTrgtArcSpeed`, `MsslTrgtArcRepeat`, `MsslTrgtArcWidth`, `MsslTrgtImpactRadius_1`, `MsslTrgtImpactRadius_2`, `MsslTrgtArcTexture`, `MsslTrgtImpactTexture`, `MsslTrgtImpactModel_1`, `MsslTrgtImpactModel_2`, `CameraYawOffset`, `UilocomotionType`, `MsslTrgtImpactTexRadius`, `VehicleUIIndicatorID`, `PowerDisplayID_1`, `PowerDisplayID_2`, `PowerDisplayID_3`) VALUES
(900301, 1073741824, 3.142, 3.142, 0, 0, 0, 900401, 0, 0, 0, 0, 0, 0, 0, 1, 1.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0, 224, 0, 0, 0),
(900302, 1073741824, 3.142, 3.142, 0, 0, 0, 900402, 0, 0, 0, 0, 0, 0, 0, 1, 1.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0, 224, 0, 0, 0),
(900303, 1073741824, 3.142, 3.142, 0, 0, 0, 900403, 0, 0, 0, 0, 0, 0, 0, 1, 1.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0, 224, 0, 0, 0),
(900304, 1073741824, 3.142, 3.142, 0, 0, 0, 900404, 0, 0, 0, 0, 0, 0, 0, 1, 1.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', '', '', 0, 0, 0, 224, 0, 0, 0);

DELETE FROM `vehicleseat_dbc` WHERE `ID` IN (900401, 900402, 900403, 900404);
INSERT INTO `vehicleseat_dbc` (`ID`, `Flags`, `AttachmentID`, `AttachmentOffsetX`, `AttachmentOffsetY`, `AttachmentOffsetZ`, `EnterPreDelay`, `EnterSpeed`, `EnterGravity`, `EnterMinDuration`, `EnterMaxDuration`, `EnterMinArcHeight`, `EnterMaxArcHeight`, `EnterAnimStart`, `EnterAnimLoop`, `RideAnimStart`, `RideAnimLoop`, `RideUpperAnimStart`, `RideUpperAnimLoop`, `ExitPreDelay`, `ExitSpeed`, `ExitGravity`, `ExitMinDuration`, `ExitMaxDuration`, `ExitMinArcHeight`, `ExitMaxArcHeight`, `ExitAnimStart`, `ExitAnimLoop`, `ExitAnimEnd`, `PassengerYaw`, `PassengerPitch`, `PassengerRoll`, `PassengerAttachmentID`, `VehicleEnterAnim`, `VehicleExitAnim`, `VehicleRideAnimLoop`, `VehicleEnterAnimBone`, `VehicleExitAnimBone`, `VehicleRideAnimLoopBone`, `VehicleEnterAnimDelay`, `VehicleExitAnimDelay`, `VehicleAbilityDisplay`, `EnterUISoundID`, `ExitUISoundID`, `UiSkin`, `FlagsB`, `CameraEnteringDelay`, `CameraEnteringDuration`, `CameraExitingDelay`, `CameraExitingDuration`, `CameraOffsetX`, `CameraOffsetY`, `CameraOffsetZ`, `CameraPosChaseRate`, `CameraFacingChaseRate`, `CameraEnteringZoom`, `CameraSeatZoomMin`, `CameraSeatZoomMax`) VALUES
(900401, -632389621, 14, 0, 0, 0, 0, 10, 19.29, 0.75, 1.5, 1, 3, 37, 38, -1, 500, 128, 123, 0, 10, 19.29, 0.5, 1, 1, 4, 37, 38, 39, 0, 0, 0, -1, 226, 107, 158, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1073741872, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(900402, -632389621, 14, 0, 0, 0, 0, 10, 19.29, 0.75, 1.5, 1, 3, 37, 38, -1, 500, 128, 123, 0, 10, 19.29, 0.5, 1, 1, 4, 37, 38, 39, 0, 0, 0, -1, 226, 107, 158, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1073741872, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(900403, -632389621, 14, 0, 0, 0, 0, 10, 19.29, 0.75, 1.5, 1, 3, 37, 38, -1, 500, 128, 123, 0, 10, 19.29, 0.5, 1, 1, 4, 37, 38, 39, 0, 0, 0, -1, 226, 107, 158, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1073741872, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
(900404, -632389621, 14, 0, 0, 0, 0, 10, 19.29, 0.75, 1.5, 1, 3, 37, 38, -1, 500, 128, 123, 0, 10, 19.29, 0.5, 1, 1, 4, 37, 38, 39, 0, 0, 0, -1, 226, 107, 158, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1073741872, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

UPDATE `creature_template` SET `VehicleId` = CASE `entry`
    WHEN 3460604 THEN 900301
    WHEN 3460605 THEN 900302
    WHEN 3460606 THEN 900303
    WHEN 3460607 THEN 900304
END WHERE `entry` IN (3460604, 3460605, 3460606, 3460607);

DELETE FROM `creaturemodeldata_dbc` WHERE `ID` IN (4892, 4893, 4894, 4895);
INSERT INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, `FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, `DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, `MissileCollisionPush`, `MissileCollisionRaise`) VALUES
(4892, 1027, 'Creature\\Cars\\Bentley\\Bentley.m2', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0),
(4893, 1027, 'Creature\\Cars\\Ferrari\\Ferrari.m2', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0),
(4894, 1027, 'Creature\\Cars\\NissanSkylineR34\\NissanSkylineR34.m2', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0),
(4895, 1027, 'Creature\\Cars\\Lamborghini\\Lamborghini.m2', 0, 1, 3, 4, 18, 12, 1, 0, 0, 0, 2694, 0.6111, 2.031, 0.762392, -1.922838, -0.779004, -0.074658, 2.814294, 1.031971, 2.075215, 1, 1, 0, 0, 0);

DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` IN (94229, 94230, 94231, 94232);
INSERT INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, `CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, `BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES
(94229, 4892, 0, 0, 1, 255, 'B01', 'B02', 'B02Glow', '', 1, 0, 0, 0, 0, 161),
(94230, 4893, 0, 0, 1, 255, 'F01', 'F02', 'F02Glow', '', 1, 0, 0, 0, 0, 161),
(94231, 4894, 0, 0, 1, 255, 'N01', 'N02', 'N02Glow', '', 1, 0, 0, 0, 0, 161),
(94232, 4895, 0, 0, 1, 255, 'L01', 'L02', 'L02Glow', '', 1, 0, 0, 0, 0, 161);
