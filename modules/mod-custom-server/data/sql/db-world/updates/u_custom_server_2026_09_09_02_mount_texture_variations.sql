-- Repair blank M2 skin slots through CreatureDisplayInfo texture variations.
-- The matching BLPs are packaged beside each mount M2 in PATCH-X.MPQ.

UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'beemount',
    `TextureVariation_2` = 'beemount_armor',
    `TextureVariation_3` = ''
WHERE `ID` = 94058;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'AlliancePVPMountBlue1',
    `TextureVariation_2` = 'AlliancePVPMountBlue2',
    `TextureVariation_3` = 'AlliancePVPMountBlue3'
WHERE `ID` = 94059;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'CraneBlue',
    `TextureVariation_2` = 'CraneMount_Blue_2',
    `TextureVariation_3` = ''
WHERE `ID` = 94062;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'dragondeepholmmount1blue',
    `TextureVariation_2` = 'dragondeepholmmount2blue',
    `TextureVariation_3` = 'dragondeepholmmount3blue'
WHERE `ID` = 94065;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'dragonhawkskin',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94066;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'dragonhawkskin',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94069;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'faeriedragonmount01_noalpha',
    `TextureVariation_2` = 'faeriedragonmountsaddle',
    `TextureVariation_3` = ''
WHERE `ID` = 94070;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'HordePVPMountBodyGreen',
    `TextureVariation_2` = 'HordePVPMountArmorGreen',
    `TextureVariation_3` = 'HordePVPMountBannerGreen'
WHERE `ID` = 94077;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'MushanBeastMount1Brown',
    `TextureVariation_2` = 'MushanBeastMount2Brown',
    `TextureVariation_3` = ''
WHERE `ID` = 94085;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'PandarenPhoenixMountBody',
    `TextureVariation_2` = 'PandarenPhoenixMountSaddle',
    `TextureVariation_3` = 'PandarenPhoenixMountWing'
WHERE `ID` = 94086;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'pandarenserpent',
    `TextureVariation_2` = 'PandarenSerpentMountSaddle_black',
    `TextureVariation_3` = ''
WHERE `ID` = 94087;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'pandarenserpent',
    `TextureVariation_2` = 'PandarenSerpentMountSaddle_red',
    `TextureVariation_3` = ''
WHERE `ID` = 94088;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'korkronprotodrake_body1',
    `TextureVariation_2` = 'korkronprotodrake_armor',
    `TextureVariation_3` = ''
WHERE `ID` = 94091;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'RedDrakeMountRed1',
    `TextureVariation_2` = 'RedDrakeMountRed2',
    `TextureVariation_3` = 'RedDrakeMountRed3'
WHERE `ID` = 94096;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'saber2',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94099;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'saber2mount',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94100;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'Seahorse_purple',
    `TextureVariation_2` = 'Seahorse_saddle_gold',
    `TextureVariation_3` = 'SeahorseMount_purple'
WHERE `ID` = 94103;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'SkeletalRaptorBone',
    `TextureVariation_2` = 'SkeletalRaptorSaddle',
    `TextureVariation_3` = ''
WHERE `ID` = 94106;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'suramarmount_skin',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94112;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'WaterStriderMount_Blue1',
    `TextureVariation_2` = 'WaterStriderMount_Blue2',
    `TextureVariation_3` = 'WaterStriderMount_Blue_Pulse'
WHERE `ID` = 94116;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'eagle2windmount',
    `TextureVariation_2` = 'eagle2windmount_saddle_1',
    `TextureVariation_3` = ''
WHERE `ID` = 94118;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'foxwyvernmount_black',
    `TextureVariation_2` = 'foxwyvernmount_saddle_black',
    `TextureVariation_3` = ''
WHERE `ID` = 94119;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'kirinmount_blue',
    `TextureVariation_2` = 'kirinmount_saddle_blue_1',
    `TextureVariation_3` = 'kirinmount_blue'
WHERE `ID` = 94120;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'lavaslugmount_blue',
    `TextureVariation_2` = 'lavaslugmount_fx_blue',
    `TextureVariation_3` = 'lavaslugmount_fx2_blue'
WHERE `ID` = 94121;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'lavasnailmount_blue',
    `TextureVariation_2` = 'lavasnailmount_fx_blue',
    `TextureVariation_3` = 'lavasnailmount_fx2_blue'
WHERE `ID` = 94122;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'mammoth2lavamount_blue',
    `TextureVariation_2` = 'mammoth2lavamount_fx_blue',
    `TextureVariation_3` = ''
WHERE `ID` = 94123;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'mammoth2mount_blue',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94124;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'moosebullmount_black',
    `TextureVariation_2` = 'moosebullmount_saddle_black',
    `TextureVariation_3` = ''
WHERE `ID` = 94125;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'primaldragonflymount_black',
    `TextureVariation_2` = 'primaldragonflymount_saddle_1',
    `TextureVariation_3` = ''
WHERE `ID` = 94126;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'riverotterlargemount01_black',
    `TextureVariation_2` = 'riverotterlargemount01_saddle_black',
    `TextureVariation_3` = ''
WHERE `ID` = 94127;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'riverotterlargemount02_black',
    `TextureVariation_2` = 'riverotterlargemount02_saddle_black',
    `TextureVariation_3` = ''
WHERE `ID` = 94128;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'salamanderwatermount_blue',
    `TextureVariation_2` = 'salamanderwatermount_saddle_1',
    `TextureVariation_3` = ''
WHERE `ID` = 94129;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'tallstriderprimalmount_black',
    `TextureVariation_2` = 'tallstriderprimalmount_saddle_1',
    `TextureVariation_3` = ''
WHERE `ID` = 94130;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'thunderlizardprimalmount_black',
    `TextureVariation_2` = 'thunderlizardprimalmount_saddle_1',
    `TextureVariation_3` = ''
WHERE `ID` = 94131;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'GameBoyMount_Case_01',
    `TextureVariation_2` = 'GameBoyMount_Screen_DonkeyKong',
    `TextureVariation_3` = ''
WHERE `ID` = 94148;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = '',
    `TextureVariation_2` = 'Horse2MountElite_Armor_silver',
    `TextureVariation_3` = ''
WHERE `ID` = 94149;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'horse2mountHighElf',
    `TextureVariation_2` = 'Horse2_Saddle',
    `TextureVariation_3` = ''
WHERE `ID` = 94150;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'horse2mountHighElf',
    `TextureVariation_2` = 'Horse2_Saddle',
    `TextureVariation_3` = ''
WHERE `ID` = 94151;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'Horse2MountElite_Body_silver',
    `TextureVariation_2` = 'Horse2MountElite_Armor_silver',
    `TextureVariation_3` = ''
WHERE `ID` = 94152;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'paladinmount_GoldRed',
    `TextureVariation_2` = 'Horse2_Saddle_HighElf',
    `TextureVariation_3` = ''
WHERE `ID` = 94153;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'Horse2MountElite_Body_Paladin',
    `TextureVariation_2` = 'Horse2MountElite_Armor_Paladin',
    `TextureVariation_3` = ''
WHERE `ID` = 94154;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'murlocmount_body',
    `TextureVariation_2` = 'murlocmount_saddle',
    `TextureVariation_3` = ''
WHERE `ID` = 94155;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'greatwyrm_black',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94156;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'PokemonCardMount_A_01',
    `TextureVariation_2` = 'PokemonCardMount_A_02_Charizard',
    `TextureVariation_3` = ''
WHERE `ID` = 94157;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'warpstalkermountbc_teal',
    `TextureVariation_2` = 'warpstalkermountbc_armor_teal',
    `TextureVariation_3` = ''
WHERE `ID` = 94158;
UPDATE `creaturedisplayinfo_dbc` SET
    `TextureVariation_1` = 'WhimsyshireCloudMount_Happy',
    `TextureVariation_2` = '',
    `TextureVariation_3` = ''
WHERE `ID` = 94159;
