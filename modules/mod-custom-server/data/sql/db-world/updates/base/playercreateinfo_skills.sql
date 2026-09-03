/* AC Defaults
REPLACE INTO `playercreateinfo_skills` (`racemask`, `classMask`, `skill`, `rank`, `comment`) VALUES
(0,0,95,0,'Defense'),
(0,0,162,0,'Unarmed'),
(0,0,183,0,'GENERIC (DND)'),
(0,0,415,0,'Cloth'),
(0,0,777,0,'Mounts'),
(0,0,778,0,'Companion Pets'),
(0,1,26,0,'Warrior - Arms'),
(0,1,256,0,'Warrior - Fury'),
(0,1,257,0,'Warrior - Protection'),
(0,2,184,0,'Paladin - Retribution'),
(0,2,267,0,'Paladin - Protection'),
(0,2,594,0,'Paladin - Holy'),
(0,4,50,0,'Hunter - Beast Mastery'),
(0,4,51,0,'Hunter - Survival'),
(0,4,163,0,'Hunter - Marksmanship'),
(0,8,38,0,'Rogue - Combat'),
(0,8,39,0,'Rogue - Subtlety'),
(0,8,253,0,'Rogue - Assassination'),
(0,9,176,0,'Thrown'),
(0,16,56,0,'Priest - Holy'),
(0,16,78,0,'Priest - Shadow'),
(0,16,613,0,'Priest - Discipline'),
(0,32,129,4,'Death Knight - First Aid'),
(0,32,229,0,'Polearms'),
(0,32,293,0,'Plate'),
(0,32,762,1,'Death Knight - Riding'),
(0,32,770,0,'Death Knight - Blood'),
(0,32,771,0,'Death Knight - Frost'),
(0,32,772,0,'Death Knight - Unholy'),
(0,35,55,0,'Two-Handed Swords'),
(0,35,413,0,'Mail'),
(0,37,44,0,'Axes'),
(0,37,172,0,'Two-Handed Axes'),
(0,39,43,0,'Swords'),
(0,40,118,0,'Dual Wield'),
(0,64,373,0,'Shaman - Enhancement'),
(0,64,374,0,'Shaman - Restoration'),
(0,64,375,0,'Shaman - Elemental'),
(0,67,433,0,'Shield'),
(0,128,6,0,'Mage - Frost'),
(0,128,8,0,'Mage - Fire'),
(0,128,237,0,'Mage - Arcane'),
(0,256,354,0,'Warlock - Demonology'),
(0,256,355,0,'Warlock - Affliction'),
(0,256,593,0,'Warlock - Destruction'),
(0,400,228,0,'Wands'),
(0,1024,134,0,'Druid - Feral'),
(0,1024,573,0,'Druid - Restoration'),
(0,1024,574,0,'Druid - Balance'),
(0,1107,54,0,'Maces'),
(0,1135,414,0,'Leather'),
(0,1488,136,0,'Staves'),
(1,0,754,0,'Human - Racial'),
(2,0,125,0,'Orc - Racial'),
(4,0,101,0,'Dwarf - Racial'),
(4,0,111,0,'Language: Dwarven'),
(8,0,113,0,'Language: Darnassian'),
(8,0,126,0,'Night Elf - Racial'),
(16,0,220,0,'Undead - Racial'),
(16,0,673,0,'Language: Forsaken'),
(32,0,115,0,'Language: Taurahe'),
(32,0,124,0,'Tauren - Racial'),
(36,4,46,0,'Guns'),
(64,0,313,0,'Language: Gnomish'),
(64,0,753,0,'Gnome - Racial'),
(128,0,315,0,'Language: Troll'),
(128,0,733,0,'Troll - Racial'),
(512,0,137,0,'Language: Thalassian'),
(512,0,756,0,'Blood Elf - Racial'),
(650,4,45,0,'Bows'),
(690,0,109,0,'Language: Orcish'),
(735,1293,173,0,'Daggers'),
(1024,0,759,0,'Language: Draenei'),
(1024,0,760,0,'Draenei - Racial'),
(1024,4,226,0,'Crossbows'),
(1061,3,160,0,'Two-Handed Maces'),
(1101,0,98,0,'Language: Common');
*/

/*Updates existing starting skills to include Worgen, Goblins, and High Elves where relevant*/
/* Only update skill if it has the default racemask to prevent conflict with other modules that change starting weapon skills. */
/* I have commented out Guns for High Elves and Bows for Worgen and Goblins because other Hunters in WotLK start with only one ranged weapon skill. */
-- UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|256|2048|4096 WHERE `skill` = 45 AND `racemask` = 650; -- Bows
-- UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|256|2048|4096 WHERE `skill` = 46 AND `racemask` = 36; -- Guns
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|4096|8192 WHERE `skill` = 45 AND `racemask` = 650; -- Bows for Orcs, Night Elves, Trolls, Blood Elves, High Elves, and Mag'har Orcs
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|64|256|2048 WHERE `skill` = 46 AND `racemask` = 36; -- Guns for Dwarves, Tauren, Gnomes, Goblins, and Worgen
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|1|5 WHERE `skill` = 226 AND `racemask` = 1024; -- Crossbows for Humans, Undead, and Draenei
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|256|2048|4096|8192 WHERE `skill` = 173 AND `racemask` = 735; -- Daggers for everyone except Tauren and Draenei
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|256|2048 WHERE `skill` = 160 AND `racemask` = 1061; -- 2H-maces for Humans, Dwarves, Tauren, Goblins, Draenei, and Worgen Warriors

/* Special cases */ 
INSERT IGNORE INTO `playercreateinfo_skills` (`racemask`, `classMask`, `skill`, `rank`, `comment`) VALUES
(0, 8, 173, 0, 'Daggers - Rogues'), -- Tauren and Draenei Rogues need Daggers
(0, 2, 160, 0, '2H-Maces - Paladins'); -- 2H-Maces for all Paladins

/* Add appropriate faction language to Worgen, Goblins, and High Elves */
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|256|8192 WHERE `skill` = 109; -- Orcish language for Goblins and Mag'har Orcs
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|2048|4096 WHERE `skill` = 98; -- Common language for Worgen and High Elves
UPDATE `playercreateinfo_skills` SET `racemask` = `racemask`|4096 WHERE `skill` = 137; -- Thalassian language for High Elves

/* Add racial skills */
DELETE FROM `playercreateinfo_skills` WHERE `raceMask` IN (256, 2048, 4096, 8192) AND `classMask` = 0;
INSERT IGNORE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES
(256, 0, 790, 0, 'Goblin - Racial'),
(2048, 0, 789, 0, 'Worgen - Racial'),
(4096, 0, 791, 0, 'High Elf - Racial'),
(8192, 0, 792, 0, 'Mag''har Orc - Racial');