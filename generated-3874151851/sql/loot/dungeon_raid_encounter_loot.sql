-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3100000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3100000,200812,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Flamekeeper''s Greaves'),
(3100000,240068,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Shadowbound Battle Greatsword'),
(3100000,240400,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Rune King''s Headdress'),
(3100000,280839,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Celestial Cape of Hellfire Citadel'),
(3100000,320885,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | The Northborn Mantle'),
(3100000,360065,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Warpriest''s Seal Ring'),
(3100000,360700,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Burnished Kilt of the Last Promise'),
(3100000,360759,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Dawncaller''s Cord'),
(3100000,380220,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000464 | Tombwarden''s Handguards of the Wild Grove');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3100001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3100001,200212,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Mournful Headguard'),
(3100001,200453,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Highblade of War Banner'),
(3100001,200465,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Steelbound Shoulderguards'),
(3100001,200635,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Great Hauberk, Bloodfire Keeper'),
(3100001,200937,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Battleaxe of the Freya Garden'),
(3100001,200970,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Partisan of the Frozen Road'),
(3100001,220108,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Clasp of the Ancient Titan'),
(3100001,220119,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Shadowbound Footguards'),
(3100001,220167,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Bracers of Pale King'),
(3100001,220221,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wolfkeeper''s Footguards'),
(3100001,220364,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Leggings of the Ancient Watch'),
(3100001,220500,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Chausses of Titan Crown'),
(3100001,220558,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Greatblade of the Hidden Vault'),
(3100001,220994,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wargrips of the Final Dawn'),
(3100001,240186,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Clawmarked Mask'),
(3100001,240204,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | The Bloodforged Grips'),
(3100001,240828,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | The Hallowed Shoulderpads'),
(3100001,240838,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Gravecaller''s Vest of the Iron Crown'),
(3100001,260068,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Footguards of the Mount Hyjal'),
(3100001,260299,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Farseer''s Legwraps of the Violet Citadel'),
(3100001,260452,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Woe-bound Boots of the Emerald Grove'),
(3100001,260548,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Stonewarden''s Jeweled Clutches'),
(3100001,260621,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Hoary Cloak of Ebon March'),
(3100001,260631,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Ashen Mask of the Unquiet Dead'),
(3100001,260657,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Dreamkeeper''s Pants'),
(3100001,260706,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Bloodsoaked Backcloth of the Wild Moon'),
(3100001,260779,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | The Nightforged Bindings'),
(3100001,260794,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Ancient Queen''s Treads'),
(3100001,260854,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wind Reaver Seal Ring'),
(3100001,260895,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Assassin Blade of the Titan King'),
(3100001,260948,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Ebon Warden''s Locket'),
(3100001,280049,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Worldkeeper''s Leggings of the Violet Crown'),
(3100001,280069,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Pants of the Frozen Pact'),
(3100001,280311,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Vrykul Bindings of Wildheart'),
(3100001,280491,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Binding of the Frozen Promise'),
(3100001,280623,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Plaguekeeper''s Cloak'),
(3100001,280689,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Darkrider''s Shoulderwraps'),
(3100001,280925,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Graven Warband'),
(3100001,280981,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Lost Warden''s Breeches of the Howling Wind'),
(3100001,320037,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Deathly Gorget of Ancient Oak'),
(3100001,320139,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Colossal Handguards of Icecrown'),
(3100001,320227,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Fel Talon Headguard'),
(3100001,320349,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Tunic of Shadow Forge'),
(3100001,320611,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wristbands, Storm Chain'),
(3100001,320884,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Pants of the Bloodguard'),
(3100001,320967,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Ivory Vest of the Holy Watch'),
(3100001,340022,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Frostscarred Shawl'),
(3100001,340161,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wolfkeeper''s Skirt of the Black Temple'),
(3100001,340183,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Hexed Warder Cloak of the Bronze Flight'),
(3100001,340294,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Battlelord''s Manaforged Gloves'),
(3100001,340406,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Silent Keeper''s Wildbound Charmstone'),
(3100001,340594,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Fernwoven Binding of Iron Oath'),
(3100001,340727,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Ebon Champion''s Jeweled Neckguard'),
(3100001,360154,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wolf Vengeance Collar'),
(3100001,360175,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Patient Vest of Shadowbinder'),
(3100001,360182,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Walkers of the Dragon Wastes'),
(3100001,360211,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Runic Rod of Twilight Watch'),
(3100001,360217,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Silent Chain Chestwrap'),
(3100001,360328,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Seal Ring, Bear Vengeance'),
(3100001,360453,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Warsage''s Capelet of the Bone Wastes'),
(3100001,360488,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Lost Warden''s Kilt'),
(3100001,360533,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | The Barbed Footwraps'),
(3100001,360586,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wolfwarden''s Frostmarked Cuffs'),
(3100001,360589,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Grips of Storm Queen'),
(3100001,360673,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Wyrmkeeper''s Staff'),
(3100001,360782,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Regalia of Warsong Hold'),
(3100001,360783,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Pale Mail Footwraps'),
(3100001,360794,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Battlemaiden''s Moonbound Runestaff'),
(3100001,360869,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Plaguewarden''s Wild Band'),
(3100001,360876,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Sash of Iron King'),
(3100001,360917,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Crimson Strike Shoulderwraps'),
(3100001,360923,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Ancient Keeper''s Shoes'),
(3100001,380145,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Cowl, Rime Fist'),
(3100001,380326,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Chestguard, Star Voice'),
(3100001,380429,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Highkeeper''s Shoulderpads'),
(3100001,380457,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Cape of Mount Hyjal'),
(3100001,380558,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | The Nameless Mark'),
(3100001,380575,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Icekeeper''s Grips of the Kings Road'),
(3100001,380576,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | Enchanted Waistguard'),
(3100001,380716,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 trash | The Forgotten Seal');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3100002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3100002,200052,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Shoulderguards of Sable Crown'),
(3100002,200158,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Chausses of the Utgarde'),
(3100002,200572,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Warden Warhelm of Lordaeron Guard'),
(3100002,200826,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Longspear of the Earth Spirit'),
(3100002,220265,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Twilightwarden''s War Leggings'),
(3100002,220448,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Northwind Warbelt of the Forgotten Depths'),
(3100002,240301,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Wyrmcarved Shoulderwraps'),
(3100002,240371,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Rimewarden''s Shadowbound Warband'),
(3100002,260104,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Shoulderwraps of the Iron Giant'),
(3100002,260134,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Wildbound Headguard of the Ancient Grove'),
(3100002,260335,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Clutches of the Karazhan'),
(3100002,260432,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Gilded Pants'),
(3100002,260738,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | The Lost Coil'),
(3100002,280200,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Titanic Medallion of Crimson Banner'),
(3100002,280226,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Sunforged Moon Wand'),
(3100002,280625,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Cryptlord''s Witchbound Warcloak'),
(3100002,280738,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | The Forsworn Circlet'),
(3100002,320003,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Warder Cloak of Argent Crusade'),
(3100002,320082,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Pale Storm Capelet'),
(3100002,320663,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Undying Vest of Ghost Moon'),
(3100002,320960,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Gloves of Fallen King'),
(3100002,340067,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Snowy Headdress of Brunnhildar Village'),
(3100002,340173,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Talisman of the Wild King'),
(3100002,340206,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Nightsteel Dirk'),
(3100002,340954,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | The Crimson Runebands'),
(3100002,360184,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Sash of Kirin Tor'),
(3100002,360555,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Duskbound Trousers of Silvermoon Spires'),
(3100002,360566,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | First Queen''s Unquiet Pants'),
(3100002,360846,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Legwraps, Primal Ice'),
(3100002,380019,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Ancient Warden''s Staff'),
(3100002,380465,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Ancient Backcloth of the Freya Garden'),
(3100002,380508,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | The Timeworn Locket'),
(3100002,380679,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000465 | Runed Staff of Avalanche');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3100003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3100003,200682,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Titanwarden''s Seal'),
(3100003,220295,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Hammered Belt of the Dark Forge'),
(3100003,220314,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Runed Warbelt'),
(3100003,220358,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Unyielding War Mantle of Serpent Spirit'),
(3100003,220426,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Embersteel Gauntlets of the Darkened Sun'),
(3100003,220809,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Shieldbearer''s Warrior-forged Greaves'),
(3100003,240771,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | The Nameless Talisman'),
(3100003,260057,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Stalkers of Onslaught Harbor'),
(3100003,340200,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Cuffs, Unholy Ray'),
(3100003,360972,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Vestments of the Iron Council'),
(3100003,380594,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000466 | Obsidian Freeze Grips');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3100005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3100005,200972,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Battlesage''s Neckchain'),
(3100005,220752,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Wyrm King''s Guard of the War Banner'),
(3100005,220797,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Pathfinder''s Royal Cloak'),
(3100005,240519,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Fanged Seal of Astral Watch'),
(3100005,240915,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Spiritkeeper''s Cowl'),
(3100005,340701,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Highlord''s Tunic'),
(3100005,360213,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Blade Sorrow Torque'),
(3100005,360745,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000468 | Trousers of the White Moon');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3100006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3100006,360605,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000469 | Wyrmforged Circlet');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3100007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3100007,200138,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Chausses of Iron Forge'),
(3100007,200298,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Charm of the Silent King'),
(3100007,200533,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Undying Earthshaker'),
(3100007,220978,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Lionheart Song Iron Mace'),
(3100007,260276,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Firekeeper''s Icy Legguards'),
(3100007,280637,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Scarab of the Dragon Forge'),
(3100007,280710,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Spiritkeeper''s Seal'),
(3100007,280834,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Mark of Dalaran'),
(3100007,320140,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Figurine of Plague Lord'),
(3100007,320424,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Nightlord''s Stalkers'),
(3100007,340363,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Manaforged Pendant'),
(3100007,340735,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Shadowwoven Footwraps of the Star Forge'),
(3100007,340843,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | The Rootbound Robes'),
(3100007,360183,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Cord, Soul Knuckle'),
(3100007,380867,0,0,0,1,1,1,1,'Generated map_33_difficulty_0 boss_000470 | Unyielding Crystal of Blood Crown');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3914 AND `Item` = 2010000001 AND `Reference` = 3100000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3914,2010000001,3100000,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | boss_000464');

DELETE FROM `creature_loot_template` WHERE `Entry` = 2529 AND `Item` = 2010000002 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(2529,2010000002,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3849 AND `Item` = 2010000003 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3849,2010000003,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3850 AND `Item` = 2010000004 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3850,2010000004,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3851 AND `Item` = 2010000005 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3851,2010000005,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3853 AND `Item` = 2010000006 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3853,2010000006,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3854 AND `Item` = 2010000007 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3854,2010000007,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3855 AND `Item` = 2010000008 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3855,2010000008,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3857 AND `Item` = 2010000009 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3857,2010000009,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3859 AND `Item` = 2010000010 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3859,2010000010,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3861 AND `Item` = 2010000011 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3861,2010000011,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3862 AND `Item` = 2010000012 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3862,2010000012,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3863 AND `Item` = 2010000013 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3863,2010000013,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3864 AND `Item` = 2010000014 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3864,2010000014,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3866 AND `Item` = 2010000015 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3866,2010000015,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3868 AND `Item` = 2010000016 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3868,2010000016,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3872 AND `Item` = 2010000017 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3872,2010000017,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3873 AND `Item` = 2010000018 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3873,2010000018,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3875 AND `Item` = 2010000019 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3875,2010000019,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3877 AND `Item` = 2010000020 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3877,2010000020,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14682 AND `Item` = 2010000021 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14682,2010000021,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 36296 AND `Item` = 2010000022 AND `Reference` = 3100001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(36296,2010000022,3100001,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3886 AND `Item` = 2010000023 AND `Reference` = 3100002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3886,2010000023,3100002,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | boss_000465');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3887 AND `Item` = 2010000024 AND `Reference` = 3100003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3887,2010000024,3100003,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | boss_000466');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4279 AND `Item` = 2010000025 AND `Reference` = 3100005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4279,2010000025,3100005,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | boss_000468');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4274 AND `Item` = 2010000026 AND `Reference` = 3100006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4274,2010000026,3100006,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | boss_000469');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3927 AND `Item` = 2010000027 AND `Reference` = 3100007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3927,2010000027,3100007,2,0,1,0,1,1,'Generated encounter attachment | map_33_difficulty_0 | boss_000470');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3110000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3110000,200207,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Warboots, Grim Shine'),
(3110000,200420,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Scourgeforged Faceguard of Wind King'),
(3110000,200829,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Royal Cloak of the Prime Design'),
(3110000,240650,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Highguard''s Deathmask'),
(3110000,340029,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Clasp of Stone Crown'),
(3110000,360057,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Earthen Circlet of the First King'),
(3110000,360690,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Frozen Queen''s Ironclad Pants'),
(3110000,380942,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 boss_000537 | Legwraps of Silver Light');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3110001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3110001,200944,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Rimekeeper''s War Hatchet'),
(3110001,220004,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Mountainborn Relic of the Rune Forge'),
(3110001,220890,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Warden''s Clasp'),
(3110001,220926,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | The Ominous Titan Axe'),
(3110001,240695,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Tablet of the Altar of Sseratus'),
(3110001,260622,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Forgekeeper''s Sanctified Chestpiece'),
(3110001,260972,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | The Nameless Leggings'),
(3110001,280314,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Raiment, Earth Woe'),
(3110001,340152,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Kilt, Hallowed Ember'),
(3110001,340342,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Pitiless Traveling Cloak of Earthen King'),
(3110001,340924,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Duskkeeper''s Mitts'),
(3110001,360210,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Sanctified Medallion of the Mage Tower'),
(3110001,360962,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Waistband, Gold Mail'),
(3110001,380115,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Silent Starfall Legwraps'),
(3110001,380132,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Handguards, Titan Lament'),
(3110001,380217,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Long Blood Leggings'),
(3110001,380490,0,0,0,1,1,1,1,'Generated map_34_difficulty_0 trash | Undying Shoulderwraps of Bitter Memory');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1666 AND `Item` = 2010000028 AND `Reference` = 3110000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1666,2010000028,3110000,2,0,1,0,1,1,'Generated encounter attachment | map_34_difficulty_0 | boss_000537');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1706 AND `Item` = 2010000029 AND `Reference` = 3110001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1706,2010000029,3110001,2,0,1,0,1,1,'Generated encounter attachment | map_34_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1707 AND `Item` = 2010000030 AND `Reference` = 3110001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1707,2010000030,3110001,2,0,1,0,1,1,'Generated encounter attachment | map_34_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1708 AND `Item` = 2010000031 AND `Reference` = 3110001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1708,2010000031,3110001,2,0,1,0,1,1,'Generated encounter attachment | map_34_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1711 AND `Item` = 2010000032 AND `Reference` = 3110001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1711,2010000032,3110001,2,0,1,0,1,1,'Generated encounter attachment | map_34_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1715 AND `Item` = 2010000033 AND `Reference` = 3110001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1715,2010000033,3110001,2,0,1,0,1,1,'Generated encounter attachment | map_34_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1720 AND `Item` = 2010000034 AND `Reference` = 3110001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1720,2010000034,3110001,2,0,1,0,1,1,'Generated encounter attachment | map_34_difficulty_0 | trash');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3120000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3120000,200331,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Amulet of Borean Tundra'),
(3120000,200343,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Vanguard''s Drape'),
(3120000,200435,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | The Nightshrouded Colossal Blade'),
(3120000,200558,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Chainmail of the Unbroken Oath'),
(3120000,200574,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Worldforged Backcloth of the Earth Spirit'),
(3120000,200666,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Grips of the Skorn'),
(3120000,200671,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Greaves of Golden Light'),
(3120000,200782,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Girdle of Runed Path'),
(3120000,220181,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Deathbound Great Hauberk'),
(3120000,220189,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Howling Chausses'),
(3120000,220770,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Stonehewn Armguards'),
(3120000,220861,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Grips, Savage Ritual'),
(3120000,240265,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Strap, Hidden Singer'),
(3120000,240471,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Winterlord''s Charm of the Shadow Ritual'),
(3120000,240748,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Ruthless Great Warbow of Fallen King'),
(3120000,240872,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Harsh Veil of Scale Lord'),
(3120000,240874,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | The Patient Boots'),
(3120000,260108,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Vest, Rime Bloom'),
(3120000,260281,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Torque of the Last Dawn'),
(3120000,260375,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Warden''s Neckchain of the Scarlet Flame'),
(3120000,260471,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Shadowwoven Waistguard, Lightcaller''s Oath'),
(3120000,260703,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Stalkers of Wintergarde'),
(3120000,260824,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Blade of the Bone Gate'),
(3120000,280093,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Cuffs, Rime Ash'),
(3120000,280201,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Chestwrap of the Star Watch'),
(3120000,280242,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Shadow Slayer Tiara'),
(3120000,320052,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Jerkin of Blade Edge'),
(3120000,320172,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Night Judgment Veil'),
(3120000,320200,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Wolfsworn Longstaff'),
(3120000,320307,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | The Ebon Choker'),
(3120000,320485,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Wristguards of Scale Queen'),
(3120000,320560,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Helm, Black Lament'),
(3120000,320612,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | The Ghostly Pants'),
(3120000,320695,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Dreamwoven Striders'),
(3120000,320944,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Storm Queen''s Brassbound Longcloak'),
(3120000,340749,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Raiment of First Watch'),
(3120000,360066,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Mossbound Vestments of Argent Dawn'),
(3120000,360353,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Gray Circlet'),
(3120000,380061,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Winterwarden''s Mournbound Clutches'),
(3120000,380410,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Dwarven Battlecloak of Rime King'),
(3120000,380547,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Thornbound Warder Cloak'),
(3120000,380717,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Flameforged Girdle'),
(3120000,380842,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000161 | Silverblessed Seal Ring of the Dead King');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3120001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3120001,200076,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wolfheart Winter Spaulders'),
(3120001,200097,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Glasslike Broadsword of Dread Crown'),
(3120001,200141,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Defiant Torc of the Valgarde'),
(3120001,200152,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shadow Queen''s Emblem of the Dawn Star'),
(3120001,200155,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Flame Dream Gloves'),
(3120001,200167,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Silvered Collar'),
(3120001,200188,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | First Knight''s Surcoat'),
(3120001,200255,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Moonsteel Footguards of Last Stand'),
(3120001,200315,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Torc, Primal Covenant'),
(3120001,200328,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sable Handguards of Sun King'),
(3120001,200384,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Icy Footguards of North Wind'),
(3120001,200421,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Deathly Pendant Chain of the Ancient Grove'),
(3120001,200434,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Silent Scream Mail'),
(3120001,200489,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Buckler, Necro Fist'),
(3120001,200513,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wolfheart Mail Helm'),
(3120001,200587,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Kingsworn Legguards'),
(3120001,200594,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Void Dusk Chestguard'),
(3120001,200604,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Warlord Broad Axe of Dragon Queen'),
(3120001,200622,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ominous Backcloth'),
(3120001,200648,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mossbound Boots'),
(3120001,200697,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ethereal Gloves'),
(3120001,200728,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Falcon Beacon Hauberk'),
(3120001,200746,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ashcaller''s Girdle'),
(3120001,200774,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ringlet, Earth Hammer'),
(3120001,200791,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Watchful Circle'),
(3120001,200797,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gravewarden''s Handguards'),
(3120001,200805,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ravenbound Great Chopper of Titan Pact'),
(3120001,200808,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Hammered Footguards'),
(3120001,200834,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Rimelord''s Worldforged Helm'),
(3120001,200844,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Scarlet Templar''s Hallowed Legguards'),
(3120001,200885,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Deathwarden''s Great Battleaxe'),
(3120001,200908,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gorget, Wolfheart Veil'),
(3120001,200918,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dreambound Waistchain of the Pale King'),
(3120001,200948,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Hammerlord''s Wyrmhide Leggings'),
(3120001,220086,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Grips of Final Stand'),
(3120001,220158,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Greenwood Highblade'),
(3120001,220165,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Arcane Gauntlets'),
(3120001,220187,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Astral Handguards of Spider Wing'),
(3120001,220205,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Mountainborn Chausses'),
(3120001,220215,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Coal-black Headguard of the Ice Moon'),
(3120001,220228,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Soullord''s Warhelm of the Dragon Spirit'),
(3120001,220237,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Plagueforged Spaulders'),
(3120001,220276,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Fierce War Leggings'),
(3120001,220300,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Legmail, Bronze Echo'),
(3120001,220361,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gravekeeper''s Helm'),
(3120001,220369,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Witchlord''s Highborne Grips'),
(3120001,220371,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Blade Doom Wrist Chains'),
(3120001,220383,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dragonsteel Helm of Nesingwary Camp'),
(3120001,220424,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sorrowful Belt'),
(3120001,220433,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Illusory War Mantle of Last Stand'),
(3120001,220441,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dreadforged Armguards of the Dragonblight'),
(3120001,220534,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Storm Queen''s Moonsteel Nightcloak'),
(3120001,220572,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Northguard''s Jagged Warboots'),
(3120001,220587,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Legmail, North Hunter'),
(3120001,220601,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dreamkeeper''s Colossal Maul'),
(3120001,220628,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Frozen Shard Mantle'),
(3120001,220641,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shoulderguards, Voidshard Rune'),
(3120001,220659,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Prayerbound Grand Warhammer of Death Lord'),
(3120001,220725,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gladiatorial Promise'),
(3120001,220740,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Lionheart Bane Warcloak'),
(3120001,220786,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wyrmcaller''s Grips'),
(3120001,220819,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Bloodstained Wrist Chains'),
(3120001,220843,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Steelbound Girdle'),
(3120001,220846,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Leafwoven Surcoat'),
(3120001,220857,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Crypt Glyph Warbelt'),
(3120001,220872,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Hammer Cold Charm'),
(3120001,220896,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Legguards of Argent Dawn'),
(3120001,220910,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Battlemage''s Resolute Shoulder Guards'),
(3120001,220913,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bloodkeeper''s Titanic Surcoat'),
(3120001,220925,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Emberwrought Coif of Silver Banner'),
(3120001,220930,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Treads of the Rune Crown'),
(3120001,220935,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Heavenforged Harness of Soul Forge'),
(3120001,220979,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Luminous Great Cape of Ancient Thorn'),
(3120001,220997,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mantle of Wild Moon'),
(3120001,220998,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Sunsteel Legmail'),
(3120001,240069,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Legguards, Bright Veil'),
(3120001,240138,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Earthwoven Signet Ring'),
(3120001,240158,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Kingsworn Belt'),
(3120001,240180,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Cape of Iron Dwarf'),
(3120001,240184,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Mountainborn Crankbow'),
(3120001,240210,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Scourgebound Waistband'),
(3120001,240214,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Walkers, Star Wolf'),
(3120001,240223,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Violet Vine Band'),
(3120001,240270,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Astral Rune Band of the Death Gate'),
(3120001,240285,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Strap of the Broken Shield'),
(3120001,240289,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Goldsteel Fingerband of Iron Banner'),
(3120001,240317,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Capelet of Plague Lord'),
(3120001,240351,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bronze Winter Armguards'),
(3120001,240370,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Frozen Caller Bindings'),
(3120001,240390,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mask, East Glacier'),
(3120001,240395,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Great Cleaver of Grizzlemaw'),
(3120001,240406,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Harness, Ghost Piercer'),
(3120001,240408,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shadow King''s Earthwoven Great Warbow'),
(3120001,240414,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Snowy Bone Bow'),
(3120001,240417,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Stalkers of Ancient Watcher'),
(3120001,240451,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shawl of the Halls of Reflection'),
(3120001,240527,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Handguards, Storm Chill'),
(3120001,240558,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Coal-black Spaulders, Silent Queen''s Oath'),
(3120001,240563,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Headdress of the Burning Crown'),
(3120001,240624,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Violet Guardian''s Hornbow'),
(3120001,240646,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Goldbound Girdle'),
(3120001,240662,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wolfsworn Vest of Dragonblight'),
(3120001,240699,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Runemarked Carapace of Blue Flame'),
(3120001,240708,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Deathknight''s Claws of the Frozen Sea'),
(3120001,240729,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Spellbinder''s Moonsteel Medallion'),
(3120001,240731,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | North Watch Phylactery'),
(3120001,240779,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Treads of the Red Dawn'),
(3120001,240794,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Steelbound Wargrips'),
(3120001,240799,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Longcloak of Rune King'),
(3120001,240858,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Cap, Demon Star'),
(3120001,240861,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bitter Breaker Girdle'),
(3120001,240904,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sainted Wargrips of Scarlet Keep'),
(3120001,240916,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Ravenbound Breeches'),
(3120001,240960,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Ancestral Great Claymore'),
(3120001,240961,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Harsh Mask'),
(3120001,260015,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Corrupted Headguard'),
(3120001,260028,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sepulchral Jerkin'),
(3120001,260112,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Warcaller''s Shadowforged Slasher'),
(3120001,260252,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Headguard, Eternal Curse'),
(3120001,260289,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Graveborn Waistguard of the Rime Watch'),
(3120001,260295,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ironcaller''s Worldforged Wargrips'),
(3120001,260301,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Trousers, Silent Reaver'),
(3120001,260322,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gloves of White Crown'),
(3120001,260336,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Leafwoven Wargrips'),
(3120001,260338,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Jerkin of Mana Forge'),
(3120001,260353,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Girdle of Amberpine Lodge'),
(3120001,260399,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Arcanized Wrap of Void King'),
(3120001,260453,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Collar of the Scarlet Flame'),
(3120001,260464,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Scarlet Templar''s Bracers'),
(3120001,260555,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Headguard, Ebon Bloom'),
(3120001,260593,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dire Torment Cap'),
(3120001,260619,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Iron King''s Waistband'),
(3120001,260644,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ebon Knight''s Forsworn Wristguards'),
(3120001,260673,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Windbound Mantle of White Crown'),
(3120001,260695,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Moon Tooth Tunic'),
(3120001,260699,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shadow King''s Scattergun'),
(3120001,260757,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ebon Glaive Bracers'),
(3120001,260771,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Hollow Heart Royal Band'),
(3120001,260800,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Icewarden''s Helm of the Moon Pact'),
(3120001,260809,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Rootbound Bracers'),
(3120001,260897,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Belt of Frost Forge'),
(3120001,260908,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Celestial Great Crossbow'),
(3120001,260933,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Forgotten Cinch'),
(3120001,260945,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Pale Grave Strap'),
(3120001,260947,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Illusory Ring, Twilightwarden''s Oath'),
(3120001,280003,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Tombwarden''s Skullbound Tiara'),
(3120001,280035,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ebon Champion''s Vest of the Void Crown'),
(3120001,280043,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Soulwarden''s Raiment'),
(3120001,280045,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Grips of the Moon Path'),
(3120001,280066,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Legwraps of Sacred Flame'),
(3120001,280081,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Cracked Brooch'),
(3120001,280313,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bonewarden''s Waistwrap of the Ebon Watch'),
(3120001,280324,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Headdress, Grim Whisper'),
(3120001,280327,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shawl, Emerald Keeper'),
(3120001,280332,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Traveling Cloak, Silver Hymn'),
(3120001,280365,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Cowl, Lion Ward'),
(3120001,280370,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | White Ripper Cinch'),
(3120001,280389,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Embercaller''s Walkers of the Pale Winter'),
(3120001,280416,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Earthcaller''s Handwraps of the Last Light'),
(3120001,280438,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Manawoven Kilt'),
(3120001,280513,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Tiara of Blood Promise'),
(3120001,280514,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Skirt of Red Moon'),
(3120001,280603,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ravenbound Shaman Staff of Endless Night'),
(3120001,280631,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Darkrider''s Reinforced Band'),
(3120001,280633,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Pants of Bone Ritual'),
(3120001,280649,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Arcane Raiment'),
(3120001,280650,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dreamcaller''s Warband'),
(3120001,280653,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bloodcaller''s Mountainborn Staff'),
(3120001,280672,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mark of the Mount Hyjal'),
(3120001,280700,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ghostkeeper''s Hallowed Band'),
(3120001,280741,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Soulkeeper''s Armbands of the Holy Crown'),
(3120001,280746,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Watchkeeper''s Tiara of the Hodir Hall'),
(3120001,280747,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Witchcaller''s Treads'),
(3120001,280753,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Diadem, North Sigil'),
(3120001,280765,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Rune Queen''s Mitts of the Argent Dawn'),
(3120001,280806,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Neckchain of Endless Path'),
(3120001,280824,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | First Knight''s Heavy Waistwrap'),
(3120001,280829,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Black Woe Hood'),
(3120001,280913,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sunlit Cuffs'),
(3120001,320016,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Lightforged Pendant of the Last Stand'),
(3120001,320039,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shadowforged Harness of the Dragon Throne'),
(3120001,320040,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Handguards of Shadowmoon Valley'),
(3120001,320053,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Spellbound Scepter of the Makers Forge'),
(3120001,320069,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Deathmarked Chain of Blackrock Mountain'),
(3120001,320070,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Primal String Mantle'),
(3120001,320100,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dread Waistband of the Shadowbinder'),
(3120001,320103,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ancient Keeper''s Scourgeforged Signet Ring'),
(3120001,320128,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Lightkeeper''s Cinch'),
(3120001,320169,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Tombforged Claws of Ruby Sanctum'),
(3120001,320170,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Hallowed Will Headdress'),
(3120001,320219,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Murderous Seal'),
(3120001,320228,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Dragonlord''s Ferocious Bindings'),
(3120001,320240,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gravebound Wristbands of the Frozen Halls'),
(3120001,320250,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Scarlet Inquisitor''s Wyrmbound Headdress'),
(3120001,320270,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Warhammer of the Nexus'),
(3120001,320286,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bitter Helm of Black Anvil'),
(3120001,320302,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Red Shot Seal Ring'),
(3120001,320314,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ancient Voice Waistguard'),
(3120001,320322,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Grim Cowl'),
(3120001,320340,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Battleworn Crusher of Wyrm Queen'),
(3120001,320394,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Worldforged War Mace of Earth Spirit'),
(3120001,320497,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Warder Cloak of Military Wing'),
(3120001,320528,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Spellbinder''s Clutches'),
(3120001,320530,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shieldmaster''s Flamebound Choker'),
(3120001,320589,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Amulet of Stone Crown'),
(3120001,320631,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Thunderwarden''s Veteran Leggings'),
(3120001,320691,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Scepter, North Wrath'),
(3120001,320733,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Long String Gloves'),
(3120001,320755,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Tombforged Cinch of Wild Spirit'),
(3120001,320815,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Chestguard of Violet Watch'),
(3120001,320839,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Old Queen''s Helm of the Dusk Watch'),
(3120001,320844,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Froststeel Harness'),
(3120001,320846,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Lightkeeper''s Carapace of the Second Dawn'),
(3120001,320852,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ruthless Striders'),
(3120001,320910,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Nightlord''s Pants of the Wind King'),
(3120001,320965,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Glasslike Striders'),
(3120001,320977,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Holy Dawn Promise'),
(3120001,340027,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Moonkeeper''s Neckguard of the Spellweaver'),
(3120001,340045,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Hoary Grips'),
(3120001,340051,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gravewarden''s Ancient Branch'),
(3120001,340062,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Scalebound Gloves'),
(3120001,340077,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Ironforged Mitts'),
(3120001,340087,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Skirt of Deep Vault'),
(3120001,340119,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Armored Armbands, Warwarden''s Oath'),
(3120001,340226,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gilded Battlecloak of the Violet Watch'),
(3120001,340259,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Legwraps of the Crimson Moon'),
(3120001,340296,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Scarlet Champion''s Sinister Cinch'),
(3120001,340301,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Blackened Vestments of the Grave King'),
(3120001,340352,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shoes, Deep Fire'),
(3120001,340411,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Coldbound Robe'),
(3120001,340429,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bindings, Rune Vow'),
(3120001,340448,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Highborn''s Drape'),
(3120001,340458,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shieldguard''s Shawl'),
(3120001,340468,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Assassin Blade, Storm Plate'),
(3120001,340482,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Spellbinder''s Sunblessed Warband'),
(3120001,340486,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sandals of the Sky Crown'),
(3120001,340576,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wyrm Queen''s Tiara of the Titan Archive'),
(3120001,340606,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Seal Ring of Fallen Crown'),
(3120001,340615,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Flamekeeper''s Radiant Walkers'),
(3120001,340617,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Robe of the Old Gods'),
(3120001,340625,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Illusory Band'),
(3120001,340634,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ghoststeel Chestwrap of the Red Flight'),
(3120001,340662,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Epaulets of Twilight Flame'),
(3120001,340718,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shadowmarked Star Wand of the Makers Vault'),
(3120001,340756,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Soulkeeper''s Drakebound Kilt'),
(3120001,340849,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Cabalistic Tunic, Mooncaller''s Oath'),
(3120001,340851,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Stonekeeper''s Vrykul Gloves'),
(3120001,340903,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Warmaster''s Skirt'),
(3120001,340990,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bone of Hearthguard'),
(3120001,360003,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Watchkeeper''s Veteran Vestments'),
(3120001,360038,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Void Sigil Shoulderpads'),
(3120001,360039,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Heroic Armbands'),
(3120001,360117,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Waistwrap of the Endless Road'),
(3120001,360186,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Everfrost Circlet, Windwarden''s Oath'),
(3120001,360209,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mitts of Grave King'),
(3120001,360284,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Headdress of the Ancient Flame'),
(3120001,360287,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Cowl of the Wind Crown'),
(3120001,360306,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Runesteel Necklace'),
(3120001,360366,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Skirt, Hallowed Rune'),
(3120001,360473,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Adamant Leggings of the Winter Crown'),
(3120001,360539,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Dusklit Tiara'),
(3120001,360585,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Pale Lady''s Graspers of the Khaz Modan'),
(3120001,360590,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Cowl of War Crown'),
(3120001,360598,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Tempered Grips of Frozen Dead'),
(3120001,360601,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Warstaff, Ebon Grip'),
(3120001,360613,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Shieldguard''s Voidforged Legwraps'),
(3120001,360633,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wristwraps of Sons of Hodir'),
(3120001,360709,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wildwoven Sandals of the Violet Gate'),
(3120001,360719,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Emberwrought Graspers of the Kirin Tor'),
(3120001,360784,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Stoic Runering of the Dark Forge'),
(3120001,360842,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Conqueror Vest, Titanforger''s Oath'),
(3120001,360867,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mystic Wall Pendant Chain'),
(3120001,360907,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Stonekeeper''s Drape'),
(3120001,360924,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Tombkeeper''s Shadowsteel Robe'),
(3120001,360965,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bronze Thorn Raiment'),
(3120001,360969,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Titanforger''s Trousers of the Black Ritual'),
(3120001,360974,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Forgemaster''s Chilled Circlet'),
(3120001,380002,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Firewarden''s Pants'),
(3120001,380028,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sacred Thunder Pants'),
(3120001,380043,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Darkened Chestpiece of Crimson Moon'),
(3120001,380055,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Drape, Grim Fate'),
(3120001,380120,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Sun King''s Mask'),
(3120001,380135,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Flawless Claws of Holy Watch'),
(3120001,380152,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Trousers of Violet Citadel'),
(3120001,380196,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Watchful Wristguards'),
(3120001,380231,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Wolfguard''s Plagueforged Vest'),
(3120001,380252,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Ancient Knight''s Belt'),
(3120001,380273,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Bracers of the Argent Tournament'),
(3120001,380280,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Key, White Strike'),
(3120001,380282,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Chilled Grips, Stonefather''s Oath'),
(3120001,380365,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Baneful Chestpiece of Dark Oath'),
(3120001,380422,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Nameless Cloak'),
(3120001,380456,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Cinch of the Sun Watch'),
(3120001,380527,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Flanged Mace of the Dread March'),
(3120001,380543,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Traveling Cloak, Celestial Tooth'),
(3120001,380548,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Infused Leggings'),
(3120001,380556,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Gray Seal Ring'),
(3120001,380562,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Bloodbound Strap'),
(3120001,380676,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Blighted Chestguard of Death Lord'),
(3120001,380760,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Chilled Armguards of the Dragon Queen'),
(3120001,380781,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Heavy Hand Hammer'),
(3120001,380810,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Stonewarden''s Starbound Wargrips'),
(3120001,380814,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Royal Band of Burning Sky'),
(3120001,380895,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Vicious Jerkin'),
(3120001,380899,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | First Knight''s Wolfhide Bracers'),
(3120001,380903,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mossbound Clutches of Sun Spirit'),
(3120001,380912,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Stave, Rune Bane'),
(3120001,380937,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Mist Hammer Wristbands'),
(3120001,380958,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | The Winterborn Helm'),
(3120001,380966,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 trash | Argent Knight''s Sacred Pants');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3120002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3120002,220093,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Charmstone of Crimson Crown'),
(3120002,220501,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Greaves, Ancient Grip'),
(3120002,220565,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Stonekeeper''s Beastbound Clasp'),
(3120002,260115,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Scarab of Skorn'),
(3120002,280780,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Moon Decree Chestwrap'),
(3120002,320443,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Wild Tongue Waistguard'),
(3120002,340085,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Magekeeper''s Runeblade of the Long Road'),
(3120002,340121,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | Kilt, Demon Skull'),
(3120002,380778,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000163 | The Spectral Treads');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3120003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3120003,200075,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Leggings of Hollow King'),
(3120003,200780,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Archmage''s Moonwoven Signet Ring'),
(3120003,200816,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Dragonkeeper''s Hauberk'),
(3120003,200836,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Ringlet, Earth Grave'),
(3120003,220142,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Greataxe of the Soul Forge'),
(3120003,220589,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Bloodsoaked Wrap of Ebon Blade'),
(3120003,240266,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | The Coldforged Wargrips'),
(3120003,240891,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Unwavering Recurve'),
(3120003,260535,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Silver King''s Fearsome Warcloak'),
(3120003,320861,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Rune Band of Sun Flame'),
(3120003,340179,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Graspers, Bleak Ruin'),
(3120003,340892,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Raiment of the Zul Drak'),
(3120003,360124,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Windlord''s Shanker'),
(3120003,360393,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Earth Reach Waistwrap'),
(3120003,380073,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Shoulder Drape of Dark Crown'),
(3120003,380981,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000164 | Boots of Dark Crown');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3120005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3120005,200249,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | The Hellforged Shoulderguards'),
(3120005,220000,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Steelforged Torc of Ebon March'),
(3120005,240372,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | The Deathbound Waistguard'),
(3120005,240866,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Charm of Frozen Sea'),
(3120005,260006,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Kingsguard Reaver of Blood Tide'),
(3120005,260171,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Fingerband of Hidden Road'),
(3120005,260554,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Silent King''s Leggings'),
(3120005,260778,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Argent Champion''s Treads'),
(3120005,280192,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Pants, Sable Talon'),
(3120005,340055,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Silent Knight''s Iceforged Sash'),
(3120005,340318,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Necklace of Sable Crown'),
(3120005,340434,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Frozen Warden''s Shoes of the Dead King'),
(3120005,340792,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Ghostkeeper''s Engraved Locket'),
(3120005,340936,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Blighted Leggings of Forgotten Road'),
(3120005,360508,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Cuffs, Obsidian Reaver'),
(3120005,360596,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Broken Warden''s Bracelets'),
(3120005,380236,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | Vest of Green Flame'),
(3120005,380379,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000166 | The Magebound Spaulders');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3120006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3120006,200984,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | The Primeval Wrist Chains'),
(3120006,220159,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | The Flameforged Wargrips'),
(3120006,240096,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Thundersteel Cloak of the Light Crown'),
(3120006,240123,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Deep Brand Boomstick'),
(3120006,240959,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Cap of the Arcane Eye'),
(3120006,280883,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Mountainborn Gemmed Band'),
(3120006,280897,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Shoulderpads of the Winter King'),
(3120006,340694,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Tempered Cuffs'),
(3120006,340819,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Tiara of the Ghost King'),
(3120006,360035,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Earthen-forged Mantle'),
(3120006,360171,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Cinch, Earth Twilight'),
(3120006,360788,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Tombbound Longcloak'),
(3120006,360977,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Warmarked Mitts'),
(3120006,380807,0,0,0,1,1,1,1,'Generated map_36_difficulty_0 boss_000167 | Jerkin, Low Helm');

DELETE FROM `creature_loot_template` WHERE `Entry` = 644 AND `Item` = 2010000035 AND `Reference` = 3120000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(644,2010000035,3120000,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | boss_000161');

DELETE FROM `creature_loot_template` WHERE `Entry` = 598 AND `Item` = 2010000036 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(598,2010000036,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 622 AND `Item` = 2010000037 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(622,2010000037,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 634 AND `Item` = 2010000038 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(634,2010000038,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 636 AND `Item` = 2010000039 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(636,2010000039,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 641 AND `Item` = 2010000040 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(641,2010000040,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 642 AND `Item` = 2010000041 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(642,2010000041,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 657 AND `Item` = 2010000042 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(657,2010000042,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1725 AND `Item` = 2010000043 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1725,2010000043,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1729 AND `Item` = 2010000044 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1729,2010000044,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1731 AND `Item` = 2010000045 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1731,2010000045,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1732 AND `Item` = 2010000046 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1732,2010000046,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3586 AND `Item` = 2010000047 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3586,2010000047,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3947 AND `Item` = 2010000048 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3947,2010000048,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4416 AND `Item` = 2010000049 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4416,2010000049,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4417 AND `Item` = 2010000050 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4417,2010000050,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4418 AND `Item` = 2010000051 AND `Reference` = 3120001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4418,2010000051,3120001,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1763 AND `Item` = 2010000052 AND `Reference` = 3120002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1763,2010000052,3120002,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | boss_000163');

DELETE FROM `creature_loot_template` WHERE `Entry` = 646 AND `Item` = 2010000053 AND `Reference` = 3120003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(646,2010000053,3120003,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | boss_000164');

DELETE FROM `creature_loot_template` WHERE `Entry` = 647 AND `Item` = 2010000054 AND `Reference` = 3120005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(647,2010000054,3120005,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | boss_000166');

DELETE FROM `creature_loot_template` WHERE `Entry` = 639 AND `Item` = 2010000055 AND `Reference` = 3120006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(639,2010000055,3120006,2,0,1,0,1,1,'Generated encounter attachment | map_36_difficulty_0 | boss_000167');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130000,200340,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Chain, Holy Fury'),
(3130000,200636,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Borean Warboots'),
(3130000,220307,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Soullord''s Brittle Grips'),
(3130000,220592,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Lost Grand Warhammer of the Thunder Watch'),
(3130000,220848,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Adamant Promise of the Ruby Sanctum'),
(3130000,220879,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Blood Prince''s Great Claymore'),
(3130000,240054,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Stormcaller''s Promise'),
(3130000,240248,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Stonecaller''s Warcloak'),
(3130000,240661,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Silent Night Striders'),
(3130000,240819,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Stormwarden''s Sinister Ring'),
(3130000,240823,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Argent Oath Armguards'),
(3130000,240837,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Deathmask, Crown Wake'),
(3130000,260213,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Strap of Dark Iron Clan'),
(3130000,260271,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | East Spire Belt'),
(3130000,260360,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Loop, Holy Oath'),
(3130000,260996,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Bonecaller''s Deathmask'),
(3130000,280214,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Green Reach Runebands'),
(3130000,280262,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Frostbitten Seal of Raven Queen'),
(3130000,280264,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Eternal Fate Armbands'),
(3130000,320009,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Spiritforged Great Aegis'),
(3130000,320083,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Dawnsteel Belt of Lost Vanguard'),
(3130000,320252,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Silverforged Pants of Ancient Watch'),
(3130000,320354,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Rimecaller''s Hoary Hoop'),
(3130000,320731,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Silent Warden''s Leggings of the War Watch'),
(3130000,320954,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Dire Memory Dirk'),
(3130000,340151,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Blessed Mitts'),
(3130000,340656,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Wolfsworn Signet Ring of Mage Tower'),
(3130000,360728,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Embercaller''s Royal Band'),
(3130000,360833,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | The Sunblessed Shiv'),
(3130000,380240,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Ghostwarden''s Headdress'),
(3130000,380356,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Torc of the Scarlet Monastery'),
(3130000,380403,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | The Coldbound Neckguard'),
(3130000,380703,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Earthkeeper''s Cowl of the Wind King'),
(3130000,380925,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Earthwoven Promise'),
(3130000,380991,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000585 | Crusher of the Ancestor Spirit');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130001,200320,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Thunderkeeper''s Forgeblessed Greaves'),
(3130001,200532,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Greaves of Black Forge'),
(3130001,220144,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Chausses, Drake Whisper'),
(3130001,240361,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Vest of the Star Grove'),
(3130001,240486,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Harness of Winter Memory'),
(3130001,240531,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Dustbound Treads of Ice Crown'),
(3130001,240606,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Scarlet Champion''s Headguard'),
(3130001,240775,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Deathcaller''s Coil'),
(3130001,260676,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Graven Walkers'),
(3130001,280129,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Silver Voice Robe'),
(3130001,280818,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Ravenkeeper''s Shoulderpads'),
(3130001,280924,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Darkcaller''s Locket'),
(3130001,320221,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Frozen Keeper''s Loop'),
(3130001,320622,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Boar Stone Torque'),
(3130001,320659,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | The Deathless Gloves'),
(3130001,320848,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Effigy, Light Glaive'),
(3130001,340083,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Moonforged Shoes'),
(3130001,340102,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Dragonlord''s Emberforged Shoulder Cape'),
(3130001,340159,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Ebon Crusader''s Stave of the Last Watch'),
(3130001,340394,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Kilt of Wildhammer Clan'),
(3130001,340678,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Skirt of Ice Forge'),
(3130001,360042,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | First King''s Walkers of the Moon Guard'),
(3130001,360665,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Wyrm Queen''s Grips of the Second Dawn'),
(3130001,380229,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Frostfire Hunter Mage Staff'),
(3130001,380327,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Shadow Voice Legguards'),
(3130001,380538,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Relentless Handguards of Grim March'),
(3130001,380730,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Handguards, Broken Death'),
(3130001,380918,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 trash | Frostveined Shawl');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130002,240613,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Bloodguard''s Wristguards'),
(3130002,240637,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Gray Lord Windlass'),
(3130002,240705,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Shadow King''s Valiant Wrap'),
(3130002,260191,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Dragon Queen''s Infused Treads'),
(3130002,260195,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Frostcaller''s Band'),
(3130002,320022,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Thunderwarden''s Mask of the Dark Ritual'),
(3130002,320118,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Belt, Prime Winter'),
(3130002,320841,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | The Bloodsoaked Clublike Mace'),
(3130002,340106,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Draconic Trousers of First King'),
(3130002,340711,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | The Austere Grips'),
(3130002,340853,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Cowl of Frostguard'),
(3130002,360197,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | The Gilded Trousers'),
(3130002,360421,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000586 | Deathcaller''s Living Chestwrap');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130003,260021,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000587 | Walkers of the Rune Forge'),
(3130003,280341,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000587 | Charmstone of the Frozen Pact');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130004,200280,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Raider Clasp of the Iron March'),
(3130004,200757,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Neckguard of the Drowned Hall'),
(3130004,200814,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Coldfire Pact Runed Crossbow'),
(3130004,220208,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Fel Gloves'),
(3130004,220453,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Warbelt of the Hidden Forge'),
(3130004,280807,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Emberwrought Cinch of Sacred Flame'),
(3130004,320090,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Battlemage''s Helm of the Fel Ritual'),
(3130004,320836,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Sun Whisper Warder Cloak'),
(3130004,360279,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000588 | Leggings of Ancient Grove');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130005,240080,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000589 | Chestpiece of the Wildhammer Clan'),
(3130005,340401,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000589 | Ringlet of the Westguard Keep'),
(3130005,380128,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000589 | Stonehammer of Light Breach');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130006,200419,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000590 | Titanblade, Light String'),
(3130006,200940,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000590 | Steelforged Headguard'),
(3130006,260799,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000590 | The Eternal Gloves'),
(3130006,320462,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000590 | Sunblessed Shoulderpads of Dawn Star');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3130007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3130007,200668,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | The Vigilant Surcoat'),
(3130007,220851,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Abyss Ember Chausses'),
(3130007,240800,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Starkeeper''s Warcloak of the Wyrmskull'),
(3130007,240871,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Plaguewarden''s Shoulderguards'),
(3130007,240893,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Windwarden''s Tablet of the Bone Throne'),
(3130007,260869,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Voidbound Handguards of the Holy Oath'),
(3130007,280722,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Stonelord''s Cinch of the Silver Moon'),
(3130007,280785,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | East Walker Archmage Staff'),
(3130007,320262,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Magebound Chestpiece'),
(3130007,320288,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Grips of the Wyrm Queen'),
(3130007,320438,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Stonebound Choker of the Corpse Scar'),
(3130007,340246,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Dread Ash Signet Ring'),
(3130007,340797,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Silent Warden''s Runeforged Headdress'),
(3130007,360033,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Stargazer''s Rune Dagger'),
(3130007,380010,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Grim Deathmask of the Eye of Eternity'),
(3130007,380269,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Shadowwarden''s Chestguard'),
(3130007,380682,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Seal Ring of Deep Mountain'),
(3130007,380805,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Colossal Leggings of Frozen Pact'),
(3130007,380825,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | Skullkeeper''s Ghostly Headdress'),
(3130007,380843,0,0,0,1,1,1,1,'Generated map_43_difficulty_0 boss_000591 | The Dreadforged Claws');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3671 AND `Item` = 2010000056 AND `Reference` = 3130000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3671,2010000056,3130000,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | boss_000585');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3840 AND `Item` = 2010000057 AND `Reference` = 3130001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3840,2010000057,3130001,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5912 AND `Item` = 2010000058 AND `Reference` = 3130001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5912,2010000058,3130001,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3669 AND `Item` = 2010000059 AND `Reference` = 3130002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3669,2010000059,3130002,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | boss_000586');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3653 AND `Item` = 2010000060 AND `Reference` = 3130003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3653,2010000060,3130003,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | boss_000587');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3670 AND `Item` = 2010000061 AND `Reference` = 3130004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3670,2010000061,3130004,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | boss_000588');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3674 AND `Item` = 2010000062 AND `Reference` = 3130005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3674,2010000062,3130005,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | boss_000589');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3673 AND `Item` = 2010000063 AND `Reference` = 3130006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3673,2010000063,3130006,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | boss_000590');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5775 AND `Item` = 2010000064 AND `Reference` = 3130007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5775,2010000064,3130007,2,0,1,0,1,1,'Generated encounter attachment | map_43_difficulty_0 | boss_000591');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3140000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3140000,200068,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Boots, Ember Dusk'),
(3140000,200145,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Chestguard of Bone Lord'),
(3140000,200256,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Great Chopper of the Frozen Dead'),
(3140000,200268,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Ashwarden''s Winterworn Gauntlets'),
(3140000,200278,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Lightwarden''s Savage Helm'),
(3140000,200405,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Deathbound Brooch of Broken Promise'),
(3140000,200505,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Beastmarked Ringlet of the Dawn Star'),
(3140000,200590,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Winterforged Medallion of the Ancient Pact'),
(3140000,200634,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Corrupted Handguards of Northern Crown'),
(3140000,200646,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Firecaller''s Darksteel Great Hauberk'),
(3140000,200720,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Rangemaster''s Chausses of the Dragon Flame'),
(3140000,200819,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Treads of the Scourge March'),
(3140000,220078,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Witchkeeper''s Chestguard'),
(3140000,220243,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Legmail of the Astral Watch'),
(3140000,220435,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Ring, Dark Sun'),
(3140000,220444,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Runeguard''s Hoop'),
(3140000,220521,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Scale-bound War Leggings'),
(3140000,220578,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Heavenforged Leggings, Farseer''s Oath'),
(3140000,220633,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Nightsteel Cape'),
(3140000,220718,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Winterlord''s Shoulder Guards'),
(3140000,220875,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Ancient Keeper''s Thunderous Casque'),
(3140000,240003,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Legguards of Shadowmoon Valley'),
(3140000,240034,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Chestguard of the Bloodguard'),
(3140000,240056,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Spaulders, Silver Claw'),
(3140000,240276,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Firewarden''s Legwraps'),
(3140000,240416,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Light Wind Legwraps'),
(3140000,240489,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Mask, Dream Scream'),
(3140000,240583,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Rangemaster''s Wristguards'),
(3140000,240702,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Pale Lady''s Walkers'),
(3140000,240743,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Legguards of Gilded Crown'),
(3140000,240769,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Shoulderpads of Sons of Hodir'),
(3140000,240849,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Blackened Shoulderwraps of Titan Crown'),
(3140000,260014,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Walkers of Fallen Watch'),
(3140000,260162,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Bloodforged Torc'),
(3140000,260266,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Voidkeeper''s Ringlet of the Mana Wyrm'),
(3140000,260523,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Backcloth of Mage Tower'),
(3140000,260745,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Stonefather''s Wristguards'),
(3140000,260777,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Rimekeeper''s Kingsguard Waistguard'),
(3140000,260782,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Tunic, Nether Flare'),
(3140000,260803,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Rootbound Charm, Voidlord''s Oath'),
(3140000,260881,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Shoulderwraps of the Unquiet King'),
(3140000,280085,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Devout Band of the Silver Crown'),
(3140000,280135,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Spellscarred Locket of the War Forge'),
(3140000,280455,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Robe, Frost Guard'),
(3140000,280503,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Crimson Singer Cloak'),
(3140000,280597,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Dragoncaller''s Wolfhide Trousers'),
(3140000,280715,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Mournful Headdress of the Dusk Watch'),
(3140000,280775,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Wildwarden''s Longstaff'),
(3140000,280961,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Rime-coated Kilt'),
(3140000,280968,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Drakescale Walkers, Spiritwarden''s Oath'),
(3140000,280975,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Wolfbound Royal Cloak'),
(3140000,320094,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Thunderforged Promise'),
(3140000,320141,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Soulwarden''s Starsteel Charm'),
(3140000,320167,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Windcaller''s Coil of the Dragon Aspect'),
(3140000,320178,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Great Cape of the Wintergrasp'),
(3140000,320235,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | North Sorrow Belt'),
(3140000,320249,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Grim Warden''s Tunic of the Storm Queen'),
(3140000,320368,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Deathless Cap'),
(3140000,320470,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Briarbound Cowl'),
(3140000,320478,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Fearsome Handguards'),
(3140000,320619,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Cinch, Ash Spell'),
(3140000,320641,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Grimlord''s Gravebound Wrap'),
(3140000,320760,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Scarlet Requiem Effigy'),
(3140000,320782,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Gravecaller''s Wildbound Legguards'),
(3140000,320819,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Bitter Compass of Forgotten Dead'),
(3140000,320851,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Frostcaller''s Wristbands of the Blood Tide'),
(3140000,320883,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Locket of the Dawnwatch'),
(3140000,320963,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Stonelord''s Drakescale Cinch'),
(3140000,340131,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Woe-bound Waistband'),
(3140000,340234,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Silent Shoes'),
(3140000,340260,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Forsworn Warcloak'),
(3140000,340322,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Arctic Gemmed Band'),
(3140000,340340,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Plagueborn Hoop, Voidwarden''s Oath'),
(3140000,340444,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Sky Bolt Armbands'),
(3140000,340580,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Steel Ruin Treads'),
(3140000,340666,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Shoes, Demon Banner'),
(3140000,340783,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Duskbound Gloves'),
(3140000,340969,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Battleworn Cloak of K3'),
(3140000,360060,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Holy Falchion of the Gjalerbron'),
(3140000,360109,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Trousers, Boar Shade'),
(3140000,360295,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Warcaller''s Arcane Cowl'),
(3140000,360307,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Wyrmwarden''s Cloak'),
(3140000,360341,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Deathcaller''s Mantle of the Frozen Crown'),
(3140000,360344,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Bitter Song Skull'),
(3140000,360357,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Arcanist''s Twilight-forged Armbands'),
(3140000,360452,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Legwraps of Undercity Depths'),
(3140000,360487,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Plaguewarden''s Skirt'),
(3140000,360655,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Stoneguard''s Dawnlit Grips'),
(3140000,360756,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Rimecaller''s Raiment'),
(3140000,360775,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Sandals of Frost Watch'),
(3140000,360900,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Sun Queen''s Kilt'),
(3140000,360921,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Ancient Queen''s Lightblessed Mantle'),
(3140000,360954,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Azure Waistband of the Blood Pact'),
(3140000,380042,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Warsage''s Legwraps of the Broken Gate'),
(3140000,380179,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Ornate Strap'),
(3140000,380181,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Nerubian Medallion'),
(3140000,380329,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Blood Queen''s Deathmask of the Grim Watch'),
(3140000,380398,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Low Cold Grand Mace'),
(3140000,380595,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Stormcaller''s Pricker of the Ebon Hold'),
(3140000,380619,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Grim Warden''s Spell Stave'),
(3140000,380728,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Primal Medallion'),
(3140000,380747,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Ashwarden''s Footguards'),
(3140000,380795,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Savage Chestpiece'),
(3140000,380811,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | The Icetouched Legguards'),
(3140000,380838,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Warhammer of the Sindragosa Fall'),
(3140000,380928,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000438 | Wyrmkeeper''s Warlord Armguards');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3140001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3140001,200110,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Steelblade of the Wildheart'),
(3140001,200218,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Shadowmarked Shoulder Drape of War Crown'),
(3140001,200327,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Griefbound Armguards of the Stone Fathers'),
(3140001,200402,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Thorn Ruin Relic'),
(3140001,200526,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | War Leggings, Bloodfire Pledge'),
(3140001,200968,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Old King''s Mail of the Violet Hold'),
(3140001,220002,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Legmail of the Last Dawn'),
(3140001,220203,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Ebon Casque'),
(3140001,220359,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Chestguard, Demon Judgment'),
(3140001,220552,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Bleak Gloves of the Terokkar'),
(3140001,220629,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Bronzed Hauberk, Dreamkeeper''s Oath'),
(3140001,220657,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Valiant Chausses of the Makers Forge'),
(3140001,220766,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Silverforged War Mantle of Ancient Oak'),
(3140001,220814,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Rimecaller''s Gray War Leggings'),
(3140001,220905,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Hoary Spaulders of Red Dawn'),
(3140001,220989,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Firewarden''s Loop'),
(3140001,240201,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | The Sorrowful Belt'),
(3140001,240302,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Shoulderguards of the Valgarde'),
(3140001,240642,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Royal Band, Scourge Torment'),
(3140001,240712,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Bonecaller''s Battle Bow of the Red Moon'),
(3140001,240797,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Graveborn Deathmask'),
(3140001,240842,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Magekeeper''s Carapace'),
(3140001,240843,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Scarlet Templar''s Deepforged Strap'),
(3140001,240990,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | The Runemarked Claws'),
(3140001,260063,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Headdress, Green Blood'),
(3140001,260194,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Tombforged Spaulders'),
(3140001,260401,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | First Warden''s Legwraps'),
(3140001,260541,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Bracers of Dark Star'),
(3140001,260547,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Shawl of the Wildheart'),
(3140001,260557,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Soullord''s Tunic'),
(3140001,260575,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Old Keeper''s Tunic of the Moon Spirit'),
(3140001,260576,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Cowl, Red Anchor'),
(3140001,260597,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Frozen Warden''s Nightshrouded Walkers'),
(3140001,260721,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Dragon Queen''s Brightmoon Tunic'),
(3140001,260764,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Seal of Cold Memory'),
(3140001,280071,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Wolfkeeper''s Royal Cloak'),
(3140001,280089,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Northkeeper''s Bracelets'),
(3140001,280165,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Handwraps, East Whisper'),
(3140001,280211,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | The Wyrmforged Circle'),
(3140001,280460,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | First King''s Headdress'),
(3140001,280569,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Mitts of the Void Ritual'),
(3140001,280601,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Sun King''s Corpsebound Pillar'),
(3140001,280907,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Hellforged Handwraps of the Blood Price'),
(3140001,280962,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Ornate Runebands'),
(3140001,320041,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Treads, Gray Dirge'),
(3140001,320253,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Bracers of the Frost Queen'),
(3140001,320442,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Shroud of Red Flight'),
(3140001,320515,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | The Battleworn Hatchet'),
(3140001,320516,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Titan Ash Boots'),
(3140001,320521,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Draconic Chestguard of the Bloodguard'),
(3140001,320592,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Armguards, Soulshard Beacon'),
(3140001,320618,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Ironclad Cinch of the Frost Crown'),
(3140001,320671,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Cinch of Grave Lord'),
(3140001,340153,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Armorsmith''s Graspers of the Mimiron Forge'),
(3140001,340191,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Last Knight''s Greatcloak'),
(3140001,340215,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Magekeeper''s Twilight-forged Wristwraps'),
(3140001,340233,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Old Queen''s Ritual Wand'),
(3140001,340257,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Warlord''s Ancestral Mantle'),
(3140001,340277,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Kilt of Void King'),
(3140001,340457,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Plaguewarden''s Bonebound Cap'),
(3140001,340502,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Dusklit Gloves of the Ebon Crown'),
(3140001,340689,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Legwraps, Gold Steel'),
(3140001,340939,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Flamekeeper''s Grips'),
(3140001,340991,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Battlesage''s Runering'),
(3140001,360004,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Scourge Hymn Raiment'),
(3140001,360200,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Northkeeper''s Bleak Cap'),
(3140001,360280,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Vestments of the Gundrak Temple'),
(3140001,360394,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Hoarfrost Regalia of the Dawnwatch'),
(3140001,360442,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Wyrmguard''s Skullbound Waistband'),
(3140001,360512,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Hood of the Gundrak Temple'),
(3140001,360527,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Waistwrap of the Abyssal Flame'),
(3140001,360959,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Ancestor''s Handwraps'),
(3140001,380044,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | The Flameforged Hoop'),
(3140001,380345,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Stonehewn Cap'),
(3140001,380355,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Rimewarden''s Forgehammer'),
(3140001,380587,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Seal Ring, Blood Legacy'),
(3140001,380656,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Titanic Claws of Death Gate'),
(3140001,380674,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Crimson Hex Deathmask'),
(3140001,380824,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Earthkeeper''s Runemarked Flask'),
(3140001,380831,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Belt of Light Eternal'),
(3140001,380885,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Soullord''s Ironthane Ring'),
(3140001,380920,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 trash | Duskwarden''s Devout Stalkers');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3140002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3140002,220972,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000439 | Ironthane''s Witchbound Shoulderguards'),
(3140002,280088,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000439 | Frostguard''s Dustbound Epaulets'),
(3140002,320332,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000439 | Spaulders, Bloodfang Promise'),
(3140002,380340,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000439 | Nightcaller''s Gorget');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3140003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3140003,200102,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Torque, Iron Thirst'),
(3140003,200403,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Twilightwarden''s Chainmail'),
(3140003,200473,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Earthen-forged Footguards'),
(3140003,200484,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Embersteel Mail of the Dead March'),
(3140003,200525,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Legguards, Unholy Fang'),
(3140003,200564,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Lost Warden''s Unhallowed Royal Band'),
(3140003,200569,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Drakebound Footguards'),
(3140003,200658,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Great Warhammer, Void Mail'),
(3140003,200683,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Grim Vengeance Mail'),
(3140003,200686,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Chainmail of Old Memory'),
(3140003,200784,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Polished Loop, Dragoncaller''s Oath'),
(3140003,200788,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Runelord''s Leggings of the Titan Crown'),
(3140003,200847,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Unhallowed Girdle of Altar of Sseratus'),
(3140003,200864,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Emberkeeper''s Spiritforged Scale'),
(3140003,200931,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Warborn Mail of Rime Forge'),
(3140003,220008,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | War Reaver of the Violet Star'),
(3140003,220012,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Hand Hammer of the Blood Crown'),
(3140003,220079,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Warboots, Astral Song'),
(3140003,220125,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Adamant War Leggings of Shadow King'),
(3140003,220287,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Wolfcaller''s Helm'),
(3140003,220329,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Watchkeeper''s Casque'),
(3140003,220384,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Feather of Frost Moon'),
(3140003,220489,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Corpsebound Boots of the War Banner'),
(3140003,220498,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Footguards, Unholy Glyph'),
(3140003,220583,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Pendant of the Broken Hall'),
(3140003,220588,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Rimebound Shroud'),
(3140003,220656,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Rune-etched Spaulders of Endless Night'),
(3140003,220671,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Plagueforged Handguards'),
(3140003,220813,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Icy Harness'),
(3140003,220974,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Last Warden''s War Hatchet'),
(3140003,220985,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Winter Fall Armguards'),
(3140003,240067,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Footguards of the Thunder Bluff'),
(3140003,240355,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Nightshrouded Waistguard of Silent Watch'),
(3140003,240401,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Bonewarden''s Resolute Torque'),
(3140003,240537,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Dragonwarden''s Tunic of the First King'),
(3140003,240578,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Brightsteel Jerkin of the Shadowbinder'),
(3140003,240680,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Carapace of Great Wolf'),
(3140003,240728,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Frost-rimed Cinch of the Wyrm King'),
(3140003,240867,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Blood Prince''s Claws'),
(3140003,240964,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Clasp of Wild Grove'),
(3140003,260007,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Age-darkened Mace of Arcane Star'),
(3140003,260017,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Leggings of the Demon Lord'),
(3140003,260038,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Idol of the Wind King'),
(3140003,260099,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Gloves, Nightfang Thorn'),
(3140003,260120,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Plaguekeeper''s Worldworn Leggings'),
(3140003,260176,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Winterlord''s Faded Grips'),
(3140003,260237,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Ironthane''s Clutches'),
(3140003,260308,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Starbound Wargrips of the Silver Covenant'),
(3140003,260356,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Claws of Iron Council'),
(3140003,260400,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Chestguard, Drake Starfall'),
(3140003,260560,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Wyrmscale Spaulders of Grave Lord'),
(3140003,260580,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Moonlit Shoulderpads of the Great Bear'),
(3140003,260629,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Weathered Clutches of Oculus'),
(3140003,260707,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Enduring Grips'),
(3140003,260737,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Footguards of Avalanche'),
(3140003,260740,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Cowl, Hollow Ember'),
(3140003,260763,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Ironlord''s Sacred Pricker'),
(3140003,260773,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Rootwoven Waistband of Forgotten King'),
(3140003,260891,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Forgotten Relic of the Storm Crown'),
(3140003,260942,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Spaulders of the Stormcaller'),
(3140003,260997,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Living Torc of the Frost Crown'),
(3140003,280119,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Infused Necklace'),
(3140003,280130,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Nameless Warden''s Unbroken Treads'),
(3140003,280160,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Darkwarden''s Battlecloak'),
(3140003,280237,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Coldfire Brand Raiment'),
(3140003,280260,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Titan-carved Regalia'),
(3140003,280346,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Spellwand of the Makers Forge'),
(3140003,280408,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Whitegold Armbands of the Bone Lord'),
(3140003,280500,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Leggings, Frostfire Requiem'),
(3140003,280696,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Kilt of the Black Anvil'),
(3140003,280772,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Leggings, Earth Singer'),
(3140003,280886,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Shadow Queen''s Binding'),
(3140003,280966,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Embercaller''s Legwraps'),
(3140003,280988,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Harsh Tunic'),
(3140003,320038,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Voidkeeper''s Girdle'),
(3140003,320043,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Mark, Emerald Moon'),
(3140003,320060,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Frostworn Mantle'),
(3140003,320073,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Glasslike Shoulderpads'),
(3140003,320338,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Frozen Wake Gloves'),
(3140003,320363,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Lightblessed Idol of Dragon Flame'),
(3140003,320510,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Shoulderwraps of the Violet Gate'),
(3140003,320665,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Headdress of Frozen Sea'),
(3140003,320682,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Stalkers of Frozen Pact'),
(3140003,320808,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Deathwarden''s Unwavering Trousers'),
(3140003,320893,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Wolfcaller''s Shoulderpads'),
(3140003,320926,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Coal-black Jerkin'),
(3140003,340023,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Graveborn Boots'),
(3140003,340136,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Pale Lady''s Binding'),
(3140003,340326,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Sunblessed Footwraps of Freya Garden'),
(3140003,340343,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Bloodstained Leggings'),
(3140003,340558,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Rune King''s Robe of the Burning Sky'),
(3140003,340757,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Ashen King''s Pants'),
(3140003,340762,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Soulmarked Binding of Sacred Dawn'),
(3140003,340814,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Bloodmage''s Gloves of the Drak Tharon Keep'),
(3140003,360051,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Merciless Cuffs of the Exodar Crystal'),
(3140003,360273,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | South Quarrel Diadem'),
(3140003,360432,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Obsidian Pants of Fire Spirit'),
(3140003,360476,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Vest of Storm Spirit'),
(3140003,360496,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Winterborn Cowl of the Great Wolf'),
(3140003,360886,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Voidsteel Cuffs'),
(3140003,360910,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Graspers of Titan Pact'),
(3140003,360961,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Sandals of Bone Crown'),
(3140003,360993,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | The Rime-coated Headdress'),
(3140003,380081,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Lightwoven Belt of the Final Dawn'),
(3140003,380121,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Warden''s Sorcerous Scarab'),
(3140003,380343,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Armguards of the Ebon Watch'),
(3140003,380467,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Highborn''s Waistguard'),
(3140003,380685,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Darksteel Carapace of the Frozen Moon'),
(3140003,380751,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Cowl, Dream Wyrm'),
(3140003,380879,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Torque of Scourge March'),
(3140003,380913,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Dread Shoulderpads of Red Dragonflight'),
(3140003,380944,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Blazing Legwraps of the Sons of Hodir'),
(3140003,380974,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000440 | Traveling Cloak, Starfire Edge');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3140004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3140004,200133,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | North Memory Gorget'),
(3140004,200321,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | The Fearsome Surcoat'),
(3140004,200567,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Shadowlord''s Surcoat of the Black Forge'),
(3140004,220064,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | The Colossal Great Hauberk'),
(3140004,220172,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Blighted Headguard'),
(3140004,220682,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Earth Woe Warbelt'),
(3140004,240052,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Necro Pact Bracers'),
(3140004,240882,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Skull Steel Headguard'),
(3140004,240935,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Violet Warband'),
(3140004,260110,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Dwarven Shiv'),
(3140004,260277,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Old King''s Ghostly Treads'),
(3140004,260788,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Spiritforged Breeches of Storm Queen'),
(3140004,260938,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Wildbound Tunic of Bone Crown'),
(3140004,260978,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Soulshard Shot Armguards'),
(3140004,280419,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Spellbinder''s Runehammer of the Moon Grove'),
(3140004,280459,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Northman''s Circlet of the Ghost Moon'),
(3140004,280548,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Silent Keeper''s Shawl'),
(3140004,280674,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Clouded Tablet'),
(3140004,320522,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Belt of Black Moon'),
(3140004,320668,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Winterlord''s Footguards'),
(3140004,340033,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Old Keeper''s Cap of the White Flame'),
(3140004,340193,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Mooncaller''s Cuffs'),
(3140004,340766,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | The Furious Loop'),
(3140004,360190,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Moonkeeper''s Mitts of the Warsong Clan'),
(3140004,380301,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Tombbound Chestpiece of Scourge Watch'),
(3140004,380427,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Brooch, Nether Wolf'),
(3140004,380736,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Strap, Shadow Ripper'),
(3140004,380964,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000441 | Violet Mage''s Legguards');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3140005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3140005,200739,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Shoulder Guards, Silver Glaive'),
(3140005,240362,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Obsidian Wargrips'),
(3140005,240540,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Claws, Obsidian Hammer'),
(3140005,240896,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Sacred Dragon Spear'),
(3140005,280020,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | The Bonebound Rod'),
(3140005,280493,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Footwraps of Ebon Flame'),
(3140005,320817,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Cerulean Cleaver'),
(3140005,340734,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Witchlord''s Skirt of the Sky Watch'),
(3140005,380049,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000443 | Night Sun Tooth');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3140006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3140006,200703,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Hateful Wargrips of the Sacred Oath'),
(3140006,220533,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Winterwarden''s Belt'),
(3140006,240182,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Deathless Wargrips of Rune Watch'),
(3140006,240203,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | The Unquiet Wristbands'),
(3140006,240488,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Legwraps, Grey Storm'),
(3140006,240502,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Starfire Reaver Treads'),
(3140006,240655,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Vengeful Shoulderpads of the Rune Watch'),
(3140006,260769,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Lost King''s Skullforged Headguard'),
(3140006,260887,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | The Sanctified Legwraps'),
(3140006,280656,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Shieldguard''s Boots'),
(3140006,280816,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | The Skullforged Chestwrap'),
(3140006,280844,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Ashen Circlet of the Stone Watch'),
(3140006,320211,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Warden Collar of the Silver Covenant'),
(3140006,320690,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Sinister Trousers'),
(3140006,340069,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Astral Medallion of the Red Dragon'),
(3140006,340177,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Cuffs of Crimson Moon'),
(3140006,340628,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Windcaller''s Ancestral Waistwrap'),
(3140006,340753,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Lost Keeper''s Feather'),
(3140006,360337,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Virtuous Shroud of the Plague Watch'),
(3140006,360377,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Walkers of the Searing Gorge'),
(3140006,360518,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Shoulder Cape of Fallen Watch'),
(3140006,360790,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Grimkeeper''s Robes'),
(3140006,360940,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Witchforged Bindings'),
(3140006,380140,0,0,0,1,1,1,1,'Generated map_47_difficulty_0 boss_000883 | Spaulders of Argent Crusade');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6168 AND `Item` = 2010000065 AND `Reference` = 3140000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6168,2010000065,3140000,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | boss_000438');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4425 AND `Item` = 2010000066 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4425,2010000066,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4427 AND `Item` = 2010000067 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4427,2010000067,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4435 AND `Item` = 2010000068 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4435,2010000068,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4436 AND `Item` = 2010000069 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4436,2010000069,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4437 AND `Item` = 2010000070 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4437,2010000070,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4438 AND `Item` = 2010000071 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4438,2010000071,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4440 AND `Item` = 2010000072 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4440,2010000072,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4442 AND `Item` = 2010000073 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4442,2010000073,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4511 AND `Item` = 2010000074 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4511,2010000074,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4512 AND `Item` = 2010000075 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4512,2010000075,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4514 AND `Item` = 2010000076 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4514,2010000076,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4515 AND `Item` = 2010000077 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4515,2010000077,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4516 AND `Item` = 2010000078 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4516,2010000078,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4517 AND `Item` = 2010000079 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4517,2010000079,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4518 AND `Item` = 2010000080 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4518,2010000080,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4519 AND `Item` = 2010000081 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4519,2010000081,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4520 AND `Item` = 2010000082 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4520,2010000082,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4522 AND `Item` = 2010000083 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4522,2010000083,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4523 AND `Item` = 2010000084 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4523,2010000084,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4525 AND `Item` = 2010000085 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4525,2010000085,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4530 AND `Item` = 2010000086 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4530,2010000086,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4531 AND `Item` = 2010000087 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4531,2010000087,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4532 AND `Item` = 2010000088 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4532,2010000088,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4538 AND `Item` = 2010000089 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4538,2010000089,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4541 AND `Item` = 2010000090 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4541,2010000090,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4623 AND `Item` = 2010000091 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4623,2010000091,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4842 AND `Item` = 2010000092 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4842,2010000092,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6035 AND `Item` = 2010000093 AND `Reference` = 3140001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6035,2010000093,3140001,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4424 AND `Item` = 2010000094 AND `Reference` = 3140002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4424,2010000094,3140002,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | boss_000439');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4428 AND `Item` = 2010000095 AND `Reference` = 3140003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4428,2010000095,3140003,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | boss_000440');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4420 AND `Item` = 2010000096 AND `Reference` = 3140004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4420,2010000096,3140004,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | boss_000441');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4421 AND `Item` = 2010000097 AND `Reference` = 3140005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4421,2010000097,3140005,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | boss_000443');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4422 AND `Item` = 2010000098 AND `Reference` = 3140006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4422,2010000098,3140006,2,0,1,0,1,1,'Generated encounter attachment | map_47_difficulty_0 | boss_000883');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150000,320615,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000219 | Iron Mace of the Fallen Crown'),
(3150000,340195,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000219 | Sandals of Lost Watch'),
(3150000,340962,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000219 | Shoulderwraps of Sunreaver Host');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150001,200095,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Dreadbound Waistguard of Frozen Sea'),
(3150001,200121,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wolfwarden''s Dawnlit Shoulder Drape'),
(3150001,200144,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Faded Mantle'),
(3150001,200326,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Great Runeblade, Flame Anchor'),
(3150001,200346,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Winterlord''s Gloves'),
(3150001,200469,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Jeweled Coil of the Ancient Watch'),
(3150001,200477,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Warcloak, Argent Brand'),
(3150001,200482,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Keepsake of Drowned Hall'),
(3150001,200659,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Footguards of the Broken Oath'),
(3150001,200698,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Deepdelver Great Cleaver'),
(3150001,200707,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Shadow King''s Serrated Waistchain'),
(3150001,200887,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Deathguard''s Belt'),
(3150001,220043,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Boots of Abyssal Gate'),
(3150001,220299,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Enchanted Band, Argent Templar''s Oath'),
(3150001,220302,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Stormlord''s Footguards'),
(3150001,220335,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Chestguard, Wyrm Hammer'),
(3150001,220458,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Edge, Moonfire Thunder'),
(3150001,220485,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Headguard of the Amberpine Lodge'),
(3150001,220507,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Violet Warden''s Greaves of the Titan Watch'),
(3150001,220515,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Kingsguard''s Warscarred Seal Ring'),
(3150001,220528,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Flamebound Coif of Restless Dead'),
(3150001,220574,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Vambraces of Hearthguard'),
(3150001,220720,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Barbed Wargrips of the Great Eagle'),
(3150001,220731,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Bronze Watch Pendant Chain'),
(3150001,220746,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Warhammer of Moonwarden'),
(3150001,220833,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Gauntlets of Great Forge'),
(3150001,220858,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Effigy, Shield Horn'),
(3150001,220888,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wyrm Queen''s Unyielding Great Hauberk'),
(3150001,220944,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Grimlord''s Headguard of the Spellweaver'),
(3150001,220959,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Stonewarden''s Chausses'),
(3150001,240152,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Darkfire Reaver Torque'),
(3150001,240176,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Windkeeper''s Chestguard of the Netherstorm'),
(3150001,240260,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Savage Longcloak of Titan Vault'),
(3150001,240378,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Fire Vow Carapace'),
(3150001,240477,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Worldwarden''s Fearsome Claws'),
(3150001,240495,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Nightlord''s Snowy Mantle'),
(3150001,240554,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Cloak of the First King'),
(3150001,240673,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Witchbound Handguards of the Great Bear'),
(3150001,240678,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Clutches of Makers Hand'),
(3150001,240809,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Hornbow, Moonfire Sigil'),
(3150001,240822,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Dawnforged Breeches'),
(3150001,260083,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Runeforged Iron Mace of the Dread Crown'),
(3150001,260123,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | The Ashen Legguards'),
(3150001,260337,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Icebound Royal Band'),
(3150001,260565,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Ancestor''s Armguards'),
(3150001,260606,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Ancient Warden''s Waistband'),
(3150001,260633,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Clutches of Venture Bay'),
(3150001,260691,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Vest, Bright Cry'),
(3150001,260696,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Terrible Legwraps'),
(3150001,260880,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Cap, South Edge'),
(3150001,260930,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Thornbound Striders'),
(3150001,280021,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Boots of the Dalaran'),
(3150001,280134,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Spider Torment Cuffs'),
(3150001,280289,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | The Fel Cinch'),
(3150001,280316,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Obsidian Verse Emblem'),
(3150001,280413,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Kilt of the Warsong Hold'),
(3150001,280484,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Grimdark Shoes'),
(3150001,280555,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Mystic Wand of Last Promise'),
(3150001,280629,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Robes, Shadow Arrow'),
(3150001,280784,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Sandals of the Sun Crown'),
(3150001,280804,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wolfsworn Cinch'),
(3150001,280880,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Weathered Cuffs'),
(3150001,280969,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Shattered Fire Seal'),
(3150001,320092,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Runeguard''s Jerkin'),
(3150001,320096,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Watchkeeper''s Clouded Striders'),
(3150001,320120,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wolfguard''s Watchful Boots'),
(3150001,320135,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | The Wild Neckchain'),
(3150001,320190,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wristguards of Utgarde'),
(3150001,320224,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Witchforged Pants of Sky Watch'),
(3150001,320263,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Corroded Charmstone'),
(3150001,320276,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Shieldmaster''s Colossal Signet'),
(3150001,320308,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wristbands of Amberpine Lodge'),
(3150001,320311,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Bloodsoaked Headdress of Lost Crown'),
(3150001,320336,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Mage Staff of Wintergarde'),
(3150001,320496,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Collar of Lost Road'),
(3150001,320498,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Moonlit Clutches'),
(3150001,320597,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Kingsguard''s Plaguetouched Spaulders'),
(3150001,320676,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Tombwarden''s Grips of the Bloodguard'),
(3150001,320679,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Emblem of the White Banner'),
(3150001,320853,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Shoulderguards, Fire Reckoning'),
(3150001,320985,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Chestguard of Ebon Crown'),
(3150001,340048,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Nightlord''s Rondel of the Endless March'),
(3150001,340197,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Northman''s Raiment of the Dark Portal'),
(3150001,340254,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Frost Queen''s Heavenforged Regalia'),
(3150001,340271,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Fire Ray Medallion'),
(3150001,340338,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Ancient Queen''s Plaguebound Headdress'),
(3150001,340461,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Emberforged Poniard of Wyrmskull'),
(3150001,340473,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Grave Dancer Coil'),
(3150001,340585,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Druid Staff of the Shadow Forge'),
(3150001,340667,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Skullcap of the Makers Terrace'),
(3150001,340759,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Boneguard''s Charred Shawl'),
(3150001,340796,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Winterguard''s Brooch'),
(3150001,360005,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Kilt of Frozen Memory'),
(3150001,360017,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Deathcaller''s Aged Rune Band'),
(3150001,360112,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Starkeeper''s Brooch'),
(3150001,360215,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Pitiless Graspers of the Wild Path'),
(3150001,360380,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Embersteel Mantle of Azjol Nerub'),
(3150001,360471,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Epaulets of the Hollow King'),
(3150001,360619,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Skirt, Deep Roar'),
(3150001,360692,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Star Wand, Grey Fate'),
(3150001,360718,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Ancient Crook, Warguard''s Oath'),
(3150001,360753,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wildlord''s Dreaming Grips'),
(3150001,360764,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Iron Queen''s Pants of the Dark Moon'),
(3150001,360792,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | The Feathered Talisman'),
(3150001,360808,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | First Warden''s Grips'),
(3150001,360828,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Sunforged Walkers'),
(3150001,360984,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Band of Frozen North'),
(3150001,380156,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Ancestral Shoulderwraps'),
(3150001,380352,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Whitegold Handguards of Ice Crown'),
(3150001,380430,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Crimson Walking Staff'),
(3150001,380514,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Blackguard''s Handguards'),
(3150001,380581,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Waistband of Scholomance'),
(3150001,380626,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Shawl of the Ice Queen'),
(3150001,380629,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Wyrmcaller''s Dire Spell Stave'),
(3150001,380632,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Tunic, Sable Anvil'),
(3150001,380739,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Waistguard, Long Decree'),
(3150001,380853,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Ember Shield Strap'),
(3150001,380864,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | The Mournful Circle'),
(3150001,380909,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Warrior-forged Trousers'),
(3150001,380988,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 trash | Leggings of Moonwarden');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150002,200241,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Shadowsteel Hauberk of the Holy Flame'),
(3150002,200379,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Heavy War Mantle'),
(3150002,220178,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Stalwart Grips'),
(3150002,220327,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Bloodmarked Battlecloak of the Iron Pact'),
(3150002,220700,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | The Infused Greaves'),
(3150002,220877,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Serpent Spear Vial'),
(3150002,240393,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Permafrost Chestguard of the Broken Crown'),
(3150002,240476,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | The Grim Vest'),
(3150002,240544,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Striders of the Amberpine Lodge'),
(3150002,280034,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Heavy Runebands of Western Plaguelands'),
(3150002,320298,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Forgeblessed Legguards of the War Crown'),
(3150002,320431,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Spaulders of the Water Spirit'),
(3150002,360967,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | East Steel Breeches'),
(3150002,380127,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Circle of the Twilight Reach'),
(3150002,380253,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Wind Freeze Wargrips'),
(3150002,380421,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Charred Mallet'),
(3150002,380516,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Lionheart Fall Gloves'),
(3150002,380816,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Manaforged Mask of Midnight Moon'),
(3150002,380902,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000220 | Cracked Tooth of the Unending Watch');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150003,200006,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Glacial Casque, Highguard''s Oath'),
(3150003,200385,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Rune-etched Warhelm of the Bleak Shore'),
(3150003,200776,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Hollow Great Hauberk of the Northern Watch'),
(3150003,220697,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Oath Pact Great Hauberk'),
(3150003,220756,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Dark Memory Chausses'),
(3150003,220761,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Thunderwarden''s Plaguebound Armguards'),
(3150003,240253,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Darkcaller''s Stalkers'),
(3150003,240293,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Seer''s Shoulderpads of the Valgarde'),
(3150003,260122,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Carver of the Cold Watch'),
(3150003,260283,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Cinch, Bright Dusk'),
(3150003,260519,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Cryptborn Vest of Broken Hall'),
(3150003,260636,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Dreamcaller''s Ring'),
(3150003,260656,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Stone, Rime Spirit'),
(3150003,260672,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Pendant Chain of the Valgarde'),
(3150003,260789,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Great Cape of Wyrm Lord'),
(3150003,280295,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Binding, Wildfire Blood'),
(3150003,280598,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Shoulder Drape, Silver Rebuke'),
(3150003,320101,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Orb of Last Dawn'),
(3150003,320908,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Warforged Cap of Frost Queen'),
(3150003,340361,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Divine Gloves of Westguard Keep'),
(3150003,340497,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Warped Vestments'),
(3150003,340871,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Waistwrap, South Fang'),
(3150003,340918,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Battleworn Spirit Wand of the Gilded Crown'),
(3150003,360253,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Moonwarden''s Sandals'),
(3150003,360360,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Shadowsteel Neckguard'),
(3150003,360440,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Pendant of Shadow King'),
(3150003,360704,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Royal Band, Coldfire Brand'),
(3150003,360884,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Briarwoven Mark'),
(3150003,380695,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000221 | Key of Void Flame');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150004,260708,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000222 | Shoulderwraps of the Arcane Eye'),
(3150004,280137,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000222 | Cryptlord''s Breeches of the Dark Forge'),
(3150004,360151,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000222 | Snowy Kilt'),
(3150004,360268,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000222 | Dustbound Mark of Argent Crusade'),
(3150004,360336,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000222 | Frozen Warden''s Ivory Skirt');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150005,200521,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Twilight Epaulets of Dread March'),
(3150005,200725,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Battleworn Warbelt'),
(3150005,220780,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Unyielding Wargrips of the Dragon Flame'),
(3150005,240824,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Manaforged Loop of the Storm Spirit'),
(3150005,240945,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Wildbound Charmstone of the Deep Hall'),
(3150005,260662,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Starsteel Wristguards of the Drak Tharon'),
(3150005,280612,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Desecrated Shoes of the Frozen Heart'),
(3150005,320669,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Cowl of Gjalerbron'),
(3150005,320837,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Bloodcaller''s Woeful Wristguards'),
(3150005,340238,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Baneful Breeches'),
(3150005,360243,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Epaulets of the Ebon Vanguard'),
(3150005,380036,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Corroded Rune Dagger'),
(3150005,380393,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000224 | Tunic of Thor Modan');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150006,200119,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Wristguards of Khaz Modan'),
(3150006,200291,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Stormmarked Surcoat'),
(3150006,200675,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Coal-black Harness of Frost King'),
(3150006,200785,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Ritual Chestguard, Argent Templar''s Oath'),
(3150006,240299,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Ravenlord''s Pants'),
(3150006,260402,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Wyrmwarden''s Icebound Great Cape'),
(3150006,260589,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Bracers of the Kings Promise'),
(3150006,320187,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Purified Pants of the Ebon Flame'),
(3150006,320781,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Soulfire Pact Breeches'),
(3150006,320812,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Bloodforged Trousers of the Black Anvil'),
(3150006,360557,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Pants of the Northern Forge'),
(3150006,380413,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Moonkeeper''s Legguards of the Bone Ritual'),
(3150006,380812,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Azure Cloak of the Dragon Wastes'),
(3150006,380889,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000225 | Wargrips, Hammer Cleaver');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3150007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3150007,240410,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000226 | Magebound Runeblade'),
(3150007,360170,0,0,0,1,1,1,1,'Generated map_48_difficulty_0 boss_000226 | Boneguard''s Unquiet Mitts');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4887 AND `Item` = 2010000099 AND `Reference` = 3150000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4887,2010000099,3150000,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | boss_000219');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4798 AND `Item` = 2010000100 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4798,2010000100,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4799 AND `Item` = 2010000101 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4799,2010000101,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4805 AND `Item` = 2010000102 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4805,2010000102,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4807 AND `Item` = 2010000103 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4807,2010000103,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4809 AND `Item` = 2010000104 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4809,2010000104,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4810 AND `Item` = 2010000105 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4810,2010000105,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4811 AND `Item` = 2010000106 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4811,2010000106,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4812 AND `Item` = 2010000107 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4812,2010000107,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4813 AND `Item` = 2010000108 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4813,2010000108,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4814 AND `Item` = 2010000109 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4814,2010000109,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4815 AND `Item` = 2010000110 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4815,2010000110,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4818 AND `Item` = 2010000111 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4818,2010000111,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4819 AND `Item` = 2010000112 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4819,2010000112,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4820 AND `Item` = 2010000113 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4820,2010000113,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4821 AND `Item` = 2010000114 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4821,2010000114,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4822 AND `Item` = 2010000115 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4822,2010000115,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4823 AND `Item` = 2010000116 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4823,2010000116,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4824 AND `Item` = 2010000117 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4824,2010000117,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4825 AND `Item` = 2010000118 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4825,2010000118,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4827 AND `Item` = 2010000119 AND `Reference` = 3150001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4827,2010000119,3150001,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4831 AND `Item` = 2010000120 AND `Reference` = 3150002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4831,2010000120,3150002,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | boss_000220');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6243 AND `Item` = 2010000121 AND `Reference` = 3150003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6243,2010000121,3150003,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | boss_000221');

DELETE FROM `creature_loot_template` WHERE `Entry` = 12902 AND `Item` = 2010000122 AND `Reference` = 3150004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(12902,2010000122,3150004,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | boss_000222');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4830 AND `Item` = 2010000123 AND `Reference` = 3150005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4830,2010000123,3150005,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | boss_000224');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4832 AND `Item` = 2010000124 AND `Reference` = 3150006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4832,2010000124,3150006,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | boss_000225');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4829 AND `Item` = 2010000125 AND `Reference` = 3150007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4829,2010000125,3150007,2,0,1,0,1,1,'Generated encounter attachment | map_48_difficulty_0 | boss_000226');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3160000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3160000,200169,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Clawmarked Beads'),
(3160000,200213,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Runeblade of Long Night'),
(3160000,200807,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Winterguard''s Capelet of the Eternal Flame'),
(3160000,220006,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Firekeeper''s Infused Belt'),
(3160000,220041,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | The Sunforged Skull'),
(3160000,220293,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Sorrowful Legmail, Northman''s Oath'),
(3160000,220312,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Earthen-forged Brooch of Engine of Makers'),
(3160000,220332,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Stormguard''s Chestguard'),
(3160000,220597,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Bladeguard''s Grand Axe'),
(3160000,240653,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Fire Bloom Signet'),
(3160000,240776,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Waistband of the Blighted Land'),
(3160000,260754,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Tunic of the Forgotten Depths'),
(3160000,260865,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Clutches, Wolfheart Blood'),
(3160000,260974,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Star Howl Spellknife'),
(3160000,280224,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Shoulderwraps of Runekeeper'),
(3160000,280317,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | The Weathered Armbands'),
(3160000,280766,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Shadowlord''s Stonecarved Royal Band'),
(3160000,320066,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Starlit Traveling Cloak of Wind King'),
(3160000,320216,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Shoulderwraps, Blood Shade'),
(3160000,320583,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | The Stoneforged Pendant Chain'),
(3160000,320698,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | The Coldforged Deathmask'),
(3160000,340223,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Deathguard''s Wristwraps'),
(3160000,340750,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Coal-black Binding of Raven Spirit'),
(3160000,360194,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Cinch of the Broken Promise'),
(3160000,360237,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Plagueforged Tunic, Ancient Queen''s Oath'),
(3160000,360540,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Winterworn Tunic of Violet Crown'),
(3160000,360730,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Silent Warden''s Pants'),
(3160000,360755,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | The Drakeforged Graspers'),
(3160000,380758,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000547 | Adamant Chestguard');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3160001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3160001,200009,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Waistguard, Ember Singer'),
(3160001,200018,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dreadbound Lens'),
(3160001,200029,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runeaxe, Ghost Punch'),
(3160001,200040,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Dawnlit Surcoat'),
(3160001,200058,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Howling Faceguard of the Damned Host'),
(3160001,200065,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hauberk, Argent Fate'),
(3160001,200066,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Warbelt of Dark Crown'),
(3160001,200070,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ethereal Nightcloak of Storm King'),
(3160001,200140,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Voidforged Surcoat'),
(3160001,200142,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hammerlord''s Ancestral Backcloth'),
(3160001,200177,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Infused Shawl'),
(3160001,200208,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Darkmoon Spaulders of Ancient Earth'),
(3160001,200217,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Plaguecaller''s Loop of the Frozen Heart'),
(3160001,200236,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Footguards of the Last Promise'),
(3160001,200274,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Northguard''s Coldforged Legguards'),
(3160001,200283,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Twilight Grips of the Nexus'),
(3160001,200293,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Thornbound Siege Hammer of Lost Vanguard'),
(3160001,200310,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Epaulets of the Grim Dawn'),
(3160001,200319,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Rotting Wargrips of Broken Banner'),
(3160001,200323,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Coldbound Legmail of the Blood Ritual'),
(3160001,200356,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Blazing Shawl of the Ebon Blade'),
(3160001,200367,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Spaulders of the Wyrm King'),
(3160001,200444,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ashwarden''s Vrykul Charm'),
(3160001,200512,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Umbral War Leggings of Moon Guard'),
(3160001,200516,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hollow Boots of Moonwell'),
(3160001,200534,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runesmith''s Greataxe'),
(3160001,200639,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Crusader''s Reinforced Traveling Cloak'),
(3160001,200642,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Orb, Soulfire Fist'),
(3160001,200676,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Harness of Death Gate'),
(3160001,200716,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Legmail of the Shadow Vault'),
(3160001,200733,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Leggings of the Titan King'),
(3160001,200744,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Highlord''s Vambraces of the Emerald Moon'),
(3160001,200800,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Windlord''s Spiritforged Treads'),
(3160001,200881,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Rune-etched Chainmail, Bonekeeper''s Oath'),
(3160001,200917,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Frozen Grave Mail'),
(3160001,200957,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Deathlord''s Great Hauberk'),
(3160001,220031,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Coldfire Vine Spaulders'),
(3160001,220042,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Purified Treads of the Borean Tundra'),
(3160001,220061,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Wildforged Spaulders'),
(3160001,220168,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Green Glacier Warboots'),
(3160001,220199,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Handguards of Frozen Throne'),
(3160001,220301,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Veil of Frostborn'),
(3160001,220304,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Vambraces of the Ancient Banner'),
(3160001,220366,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Surcoat of the Amberpine Lodge'),
(3160001,220387,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Ironclad Backcloth'),
(3160001,220408,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Old Queen''s Great Cape'),
(3160001,220511,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dragonforged Mace of Ancient Storm'),
(3160001,220524,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Nightsteel Wrist Chains of Last Vigil'),
(3160001,220529,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Deathwarden''s Blackened Legmail'),
(3160001,220536,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Coldfire Maul'),
(3160001,220615,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Belt of Makers Vault'),
(3160001,220623,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hauberk of Pale Winter'),
(3160001,220647,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Titanbound Chestguard'),
(3160001,220695,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Soulbound Hauberk'),
(3160001,220724,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Treads, Doom Storm'),
(3160001,220816,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Starlit Handguards of Conquest Hold'),
(3160001,220822,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Bloodguard''s Casque'),
(3160001,220841,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Handguards, Scarlet Grasp'),
(3160001,220863,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Pale-blue Leggings'),
(3160001,220958,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Permafrost Warboots'),
(3160001,220981,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Moonlit Chausses of the Tirisfal Glades'),
(3160001,240001,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Mask of the Blackened Sky'),
(3160001,240006,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ravenkeeper''s Waistband'),
(3160001,240023,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shadowwoven Capelet'),
(3160001,240084,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dawnkeeper''s Waistguard'),
(3160001,240103,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runed Shoulderpads of Frozen Heart'),
(3160001,240104,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Footguards, Wind Keeper'),
(3160001,240124,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Pale Cold Cowl'),
(3160001,240137,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Greatsword, Flame Wolf'),
(3160001,240142,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Grips of Dragon Crown'),
(3160001,240165,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Polished Walkers'),
(3160001,240167,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Headguard, Thorn Spark'),
(3160001,240192,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dawnforged Claws'),
(3160001,240207,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Nightcaller''s Briarwoven Ranger Bow'),
(3160001,240219,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Cryptkeeper''s Steel Crossbow'),
(3160001,240235,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Vambraces, Void Scream'),
(3160001,240247,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Aged Strap'),
(3160001,240257,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Clutches, Scourge Promise'),
(3160001,240278,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Plagueforged Waistguard'),
(3160001,240288,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Spear Hand Shawl'),
(3160001,240377,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Duskbound Band'),
(3160001,240379,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Silent Figurine'),
(3160001,240386,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Rootwoven Clutches of the Violet Citadel'),
(3160001,240412,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ironthane''s Trousers'),
(3160001,240422,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Vigilant Mantle'),
(3160001,240462,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wyrmhide Carapace'),
(3160001,240605,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Spiritbound Spaulders of the Bitter Memory'),
(3160001,240635,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Fel Runegun of Crimson Dawn'),
(3160001,240664,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wyrmforged Greatcloak'),
(3160001,240710,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shadowmarked Boots'),
(3160001,240737,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Waistband of the Hodir Hall'),
(3160001,240764,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Watchful Harness'),
(3160001,240789,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Moonlord''s Forsaken Boots'),
(3160001,240793,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ebon Marshal''s Belt'),
(3160001,240833,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Grimkeeper''s Cowl of the Dragon Spirit'),
(3160001,240852,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Nightfang Brand Wargrips'),
(3160001,240883,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Whispering Mask'),
(3160001,240900,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Leafbound Armguards'),
(3160001,260001,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Bodkin, Scourge Whisper'),
(3160001,260011,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Skullkeeper''s Serrated Legguards'),
(3160001,260074,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Bitter Wake Loop'),
(3160001,260080,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Lightwoven Legguards'),
(3160001,260082,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Battlecloak of the Burning Steppes'),
(3160001,260100,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Frostguard''s Pants'),
(3160001,260103,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Royal Band of Ebon Banner'),
(3160001,260117,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Vest, Azure Breaker'),
(3160001,260145,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Pants, Savage Feather'),
(3160001,260155,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Skyforged War Mace of Sons of Hodir'),
(3160001,260185,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shoulderpads, North Star'),
(3160001,260193,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Moonlit Jerkin of the Grave Watch'),
(3160001,260249,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Flawless Headguard, Iron Queen''s Oath'),
(3160001,260409,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Frostforged Leggings'),
(3160001,260421,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Harness of the Grim Dawn'),
(3160001,260439,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Nightlord''s Ancestral Eye'),
(3160001,260477,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Medallion, Void Star'),
(3160001,260562,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Gravewarden''s Lightbound Fingerband'),
(3160001,260577,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Mantle of the Storm Spirit'),
(3160001,260586,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Chain, Dream Horn'),
(3160001,260655,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runemaster''s Grimdark Legguards'),
(3160001,260667,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dreamwoven Shoulderpads of the Frostborn'),
(3160001,260692,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Trousers of the Grizzlemaw'),
(3160001,260711,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Royal Tablet of Broken Spear'),
(3160001,260720,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Moonforged Token of Deep Mountain'),
(3160001,260722,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Blazing Battlecloak of the Scourge Host'),
(3160001,260758,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ethereal Chestpiece of Broken Crown'),
(3160001,260807,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Silverforged Fang'),
(3160001,260816,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shoulderpads of Dead March'),
(3160001,260831,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Merciless Stalkers of Wildheart'),
(3160001,260844,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Argent Champion''s Unholy Girdle'),
(3160001,260875,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Obsidian Doom Jerkin'),
(3160001,260888,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Old Knight''s Royal Band'),
(3160001,260901,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Assassin Blade of Ebon Hold'),
(3160001,260913,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Boneforged Seal'),
(3160001,260922,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Celestial Blood Broadsword'),
(3160001,260953,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Footguards of Drowned King'),
(3160001,260963,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Scale-bound Footguards of the Ebon Hold'),
(3160001,260969,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Dragonsteel Claws'),
(3160001,280078,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Sandals of the Silver Light'),
(3160001,280086,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Skirt of Dying Light'),
(3160001,280196,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Ravenous Epaulets'),
(3160001,280235,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dread Clutch Shoulder Drape'),
(3160001,280246,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Berserker Sandals of Grizzlemaw'),
(3160001,280253,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Nerubian Legwraps of Frost Moon'),
(3160001,280254,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Frostworn Focus'),
(3160001,280257,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Promise of Green Flight'),
(3160001,280271,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Northkeeper''s Snowy Circlet'),
(3160001,280280,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Sash of the Frozen Banner'),
(3160001,280349,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Binding, Winter Howl'),
(3160001,280360,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Skullbound Armbands of Crimson Crown'),
(3160001,280371,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | First Knight''s Wristwraps'),
(3160001,280382,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wyrmwarden''s Tunic of the White Flame'),
(3160001,280446,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Vestments of the Frozen Forge'),
(3160001,280452,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Soulfire Glow Gloves'),
(3160001,280463,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Silent King''s Rod of the Emerald Star'),
(3160001,280473,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Winter King''s Mossbound Headdress'),
(3160001,280709,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Siegebound Tiara'),
(3160001,280792,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Lightcaller''s Unhallowed Cuffs'),
(3160001,280825,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Glasslike Vestments of Plague Lord'),
(3160001,280842,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wolfguard''s Kilt'),
(3160001,280858,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Titanforged Robes of Autumn Wind'),
(3160001,280862,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Faded Flask'),
(3160001,280865,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Stormkeeper''s Wand'),
(3160001,280879,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Breeches of Scourge Lord'),
(3160001,280896,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Clasp of Gjalerbron'),
(3160001,280901,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Lightforged Gloves of Abyssal Gate'),
(3160001,320024,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Scourgebound Striders'),
(3160001,320074,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wyrmbound Boots'),
(3160001,320075,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Deathlord''s Shoulderpads'),
(3160001,320110,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Mountainborn Carapace of the Violet Gate'),
(3160001,320146,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shoulderwraps, Silver Rune'),
(3160001,320157,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ghostkeeper''s Amulet'),
(3160001,320166,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Earthcaller''s Legwraps'),
(3160001,320234,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Earthwoven Wargrips of Final Stand'),
(3160001,320239,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wristbands of the Astral Gate'),
(3160001,320260,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Witchcaller''s Belt'),
(3160001,320297,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Stoneward Shoulderpads'),
(3160001,320315,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wildguard''s Shadowforged Waistband'),
(3160001,320320,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Headdress of Demon Watch'),
(3160001,320350,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hallowed Strike Vest'),
(3160001,320367,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Zealous Gloves'),
(3160001,320388,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Titan Decree Circle'),
(3160001,320396,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Legwraps of the Scourge March'),
(3160001,320398,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ironkeeper''s Bracers'),
(3160001,320402,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Gravewarden''s Spaulders of the War Banner'),
(3160001,320413,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Clutches, Voidshard Caller'),
(3160001,320428,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Nightcloak, Rime String'),
(3160001,320436,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ancient King''s Hoop of the White Flame'),
(3160001,320440,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Earthen-forged Waistband'),
(3160001,320444,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Strap of the Frozen Gate'),
(3160001,320471,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Duskbound Carapace'),
(3160001,320502,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Pitiless Mask'),
(3160001,320543,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Carapace, Storm Dancer'),
(3160001,320548,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Crimson Runestaff of Crusaders Coliseum'),
(3160001,320582,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | First Queen''s Chestguard'),
(3160001,320660,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Jerkin of the Grave Lord'),
(3160001,320740,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Vanguard''s Girdle of the Wind King'),
(3160001,320745,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Fireforged Treads of Dragon Throne'),
(3160001,320786,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runelord''s Vest'),
(3160001,320842,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Pale-blue Longstaff of Cold Memory'),
(3160001,320866,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Walkers of the Altar of Sseratus'),
(3160001,320955,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Virtuous Stalkers'),
(3160001,320980,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Violet Cinch of the Drak Tharon Keep'),
(3160001,320988,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Highborne Choker'),
(3160001,340035,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Skyforged Legwraps of Ancient Night'),
(3160001,340047,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Warrior-forged Robe of the Wintergrasp'),
(3160001,340052,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Twilightcaller''s Regalia'),
(3160001,340101,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Binding, Gold Scar'),
(3160001,340120,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Nightforged Archmage Staff'),
(3160001,340157,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Spire, Fire Sorrow'),
(3160001,340174,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shadow King''s Mirror'),
(3160001,340180,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Greatcloak, Bitter Howl'),
(3160001,340265,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Bindings of Frost Moon'),
(3160001,340272,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Soulbound Scale of the Iron Crown'),
(3160001,340346,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Graveforged Cord'),
(3160001,340380,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wyrmwarden''s Drape'),
(3160001,340395,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dragonstalker''s Compass of the Rune Crown'),
(3160001,340418,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runewarden''s Wristwraps'),
(3160001,340467,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Frostmarked Cape'),
(3160001,340485,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ghostkeeper''s Briarwoven Eye'),
(3160001,340487,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dragon Branch Binding'),
(3160001,340540,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dragonhide Pants of the Silent Moon'),
(3160001,340548,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ironkeeper''s Warped Longcloak'),
(3160001,340549,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Flamecaller''s Charmstone of the First King'),
(3160001,340590,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Plaguekeeper''s Graspers of the Mana Forge'),
(3160001,340591,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Worldworn Footwraps of the Golden Dawn'),
(3160001,340631,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Highborn''s Waistwrap'),
(3160001,340682,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Dreadbound Shoes of Green Flight'),
(3160001,340705,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Broken Greatstaff'),
(3160001,340733,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Silverkeeper''s Armbands of the Mount Hyjal'),
(3160001,340742,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Clasp of the Iron Council'),
(3160001,340761,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Legwraps, South Breath'),
(3160001,340780,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Stonecaller''s Gloves'),
(3160001,340787,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Divine Sandals of Frostborn'),
(3160001,340790,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hearthkeeper''s Armbands of the Valgarde'),
(3160001,340808,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Stonelord''s Tiara'),
(3160001,340810,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Warlord Handwraps of Ice King'),
(3160001,340847,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Spirit Chill Cinch'),
(3160001,340864,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Gravewarden''s Shoes'),
(3160001,340909,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Cruel Robes'),
(3160001,340949,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Austere Bindings of the Hidden Forge'),
(3160001,340953,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runebands of the Blue Dragon'),
(3160001,340964,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Tombwarden''s Violet Mitts'),
(3160001,340974,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hardened Key of Water Spirit'),
(3160001,340979,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shoulder Cape of Golden Moon'),
(3160001,340980,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Idol, Lionheart Feather'),
(3160001,340988,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Walkers of Borean Expanse'),
(3160001,360023,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Ironforged Cowl'),
(3160001,360028,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Plaguekeeper''s Beastmarked Waistband'),
(3160001,360047,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hateful Bracelets of Makers Hand'),
(3160001,360084,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Beastmarked Heart'),
(3160001,360096,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Glasslike Vestments'),
(3160001,360098,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Iron Hammer Ringlet'),
(3160001,360166,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shoulderpads, Ghostfire Ripper'),
(3160001,360169,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Far Pact Seer Staff'),
(3160001,360192,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Undying Boots of the Ashen March'),
(3160001,360246,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Gladiatorial Graspers'),
(3160001,360278,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ironwarden''s Mantle of the Earthshaper'),
(3160001,360318,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wolfguard''s Shoulderwraps'),
(3160001,360343,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Veil of Arcane Gate'),
(3160001,360348,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Binding, Hammer Pledge'),
(3160001,360355,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Firewarden''s Vestments'),
(3160001,360370,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Whispering Rune Band of the Moon Flame'),
(3160001,360385,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runemaster''s Cuffs of the Grim March'),
(3160001,360399,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Whispering Epaulets'),
(3160001,360422,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Pendant of the Nesingwary Camp'),
(3160001,360423,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Froststeel Cord'),
(3160001,360433,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Arcane Scepter of Scourge March'),
(3160001,360505,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Deathknight''s Legwraps'),
(3160001,360506,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Heavy Vestments, Highborn''s Oath'),
(3160001,360541,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Gloves of the Dragon Pact'),
(3160001,360545,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Broken Warden''s Radiant Breeches'),
(3160001,360577,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Chestwrap, Mana Hammer'),
(3160001,360610,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Thornbound Fang of the Temple of Storms'),
(3160001,360616,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Moonforged Idol of the Endless Road'),
(3160001,360623,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Earthcaller''s Royal Band'),
(3160001,360630,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hood of the Final Promise'),
(3160001,360640,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Argent Drape'),
(3160001,360697,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Moonwoven Cuffs of Endless March'),
(3160001,360698,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Battleworn Longcloak'),
(3160001,360768,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Razor-edged Coil'),
(3160001,360771,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Breeches, Red Watch'),
(3160001,360778,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wildbound Runed Staff of Astral Watch'),
(3160001,360803,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Moon King''s Gloves'),
(3160001,360809,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Runesteel Footwraps'),
(3160001,360814,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Virtuous Sandals of the Makers Hand'),
(3160001,360815,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Cap of Northern King'),
(3160001,360823,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Sash, Grave Thunder'),
(3160001,360844,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Warstaff of Titan Watch'),
(3160001,360883,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Spirit Watch Skirt'),
(3160001,360890,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Boar Watch Royal Cloak'),
(3160001,360913,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | North Singer Cuffs'),
(3160001,360915,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Shoulderwraps of Silver Promise'),
(3160001,360928,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Magebound Backcloth of the Ancient Frost'),
(3160001,360935,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Argent Ember Walkers'),
(3160001,360979,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Plagueforged Coil of New Agamand'),
(3160001,360982,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Waistband, Bloodfire Dream'),
(3160001,380011,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wargrips of Bone Gate'),
(3160001,380025,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Pants of Broken Road'),
(3160001,380027,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ironthane''s Claws of the Raven Queen'),
(3160001,380037,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Hammered Pike of Shadow Crown'),
(3160001,380088,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Earthkeeper''s Horn'),
(3160001,380118,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Silent Knight''s Treads of the Winter Forge'),
(3160001,380153,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Coil of Dark Portal'),
(3160001,380164,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Jerkin of the Ancient Watcher'),
(3160001,380216,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Seal of Bone Lord'),
(3160001,380278,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Astral Freeze Armguards'),
(3160001,380289,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Arcanized Grips'),
(3160001,380303,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Saronite Crook'),
(3160001,380320,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Fallen Freeze Shoulderpads'),
(3160001,380333,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Witchbound Carapace of the Wyrm Queen'),
(3160001,380428,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Virtuous Flanged Mace of the Last Watch'),
(3160001,380447,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Warsage''s Thornwoven Vest'),
(3160001,380449,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Rune King''s Shadowwoven Choker'),
(3160001,380451,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Sunhallowed Walking Staff of Arcane Moon'),
(3160001,380464,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wristguards of Silver Covenant'),
(3160001,380469,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Rootbound Pants'),
(3160001,380504,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Necklace of Mimiron Forge'),
(3160001,380533,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Stormbound Leggings of the Ebon Hold'),
(3160001,380571,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Ironclad Striders of the Serpent Spirit'),
(3160001,380590,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Wildguard''s Argent Stalkers'),
(3160001,380597,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Saronite Jerkin'),
(3160001,380603,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Waistguard, Ash Glaive'),
(3160001,380606,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | The Sunhallowed Royal Cloak'),
(3160001,380649,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Bearwarden''s Rod of the Ebon Vanguard'),
(3160001,380651,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Sacred Tongue Quarterstaff'),
(3160001,380659,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Tombwarden''s Runewoven Legwraps'),
(3160001,380666,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Graven Mantle of Makers Hand'),
(3160001,380680,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Deathkeeper''s Pale Coin'),
(3160001,380691,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Bright Promise Staff'),
(3160001,380726,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Stalkers, Crypt Warden'),
(3160001,380734,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Scarlet Mask of the River Heart'),
(3160001,380761,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Gemmed Band, Star Frost'),
(3160001,380870,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Titan King''s Clawmarked Wristbands'),
(3160001,380872,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Sacred Beacon Poniard'),
(3160001,380882,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Snowbound Jerkin of the Wyrm Crown'),
(3160001,380980,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 trash | Gleaming Mantle of Ironforge Mountain');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3160002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3160002,200045,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Mournbound Talisman'),
(3160002,200210,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Battlecloak of the Naxxramas'),
(3160002,200507,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Rimeforged Ring of Makers Vault'),
(3160002,200531,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Dawnsteel Chain of the Soul Forge'),
(3160002,200690,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Grips, Grave Watch'),
(3160002,200717,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Draconic Legmail of Moonwell'),
(3160002,200966,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Footguards of the Grim Host'),
(3160002,200985,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Runic Axe of Frozen Dead'),
(3160002,220380,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | The Silverforged Legguards'),
(3160002,220514,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Plague Breath Shoulder Guards'),
(3160002,220812,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Sunforged Legmail of the Bitter Memory'),
(3160002,220865,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Crimson Epaulets of the Iron Crown'),
(3160002,240032,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Warder Cloak, Falcon Forge'),
(3160002,240044,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Scythe of Thunder King'),
(3160002,240077,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Handguards, Astral Wolf'),
(3160002,240454,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Ghostly Stalkers of the Frost Watch'),
(3160002,240614,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Worldwarden''s Stalkers'),
(3160002,240649,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | The Corroded Neckguard'),
(3160002,240782,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Stormlord''s Treads of the Hallowed Flame'),
(3160002,240829,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Leafbound Striders of the Broken Blade'),
(3160002,240869,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Lightcaller''s Bone Bow of the Thunder King'),
(3160002,260034,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Flame Dancer Handguards'),
(3160002,260235,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Crimson Treads'),
(3160002,260442,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Darkkeeper''s Grips of the Sable Crown'),
(3160002,260504,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Enchanted Deathmask of the Blood Ritual'),
(3160002,260537,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Vanguard''s Cap'),
(3160002,260686,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Whitegold Wargrips of Scale Queen'),
(3160002,260733,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Unquiet Bindings, Last Queen''s Oath'),
(3160002,260846,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | The Shadowsteel Shoulderpads'),
(3160002,280312,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Promise, Argent Fist'),
(3160002,280585,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Rime Judgment Grips'),
(3160002,280592,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | The Scarlet Mitts'),
(3160002,280727,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Boots of the Long Night'),
(3160002,280949,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Kingsguard Headdress'),
(3160002,320102,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Belt of the Great Bear'),
(3160002,320192,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Blacksmith''s Fang'),
(3160002,320236,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Devout Wristbands of the Dread Crown'),
(3160002,320372,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Walkers of the Ancient Earth'),
(3160002,320651,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Bloodstained Bracers'),
(3160002,320672,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Brutish Striders'),
(3160002,320744,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Bronzed Greatcloak of the Demon Watch'),
(3160002,320873,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Cap, High Reach'),
(3160002,320913,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Borean Walkers of Stormwind Keep'),
(3160002,340269,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Bracelets of the Sindragosa Fall'),
(3160002,340415,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | The Glasslike Cinch'),
(3160002,340571,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Highkeeper''s Robes'),
(3160002,340743,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Winterkeeper''s Heavenforged Sorcerer Rod'),
(3160002,360216,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Earthshard Shine Shawl'),
(3160002,360254,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Last Knight''s Shoes'),
(3160002,360451,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Duskkeeper''s Lightforged Staff'),
(3160002,360454,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Tunic of the Light Eternal'),
(3160002,360708,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Ancient Cinch'),
(3160002,360896,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Saber of First Watch'),
(3160002,380101,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Forgotten String Stave'),
(3160002,380304,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Ghostfire Knuckle Pants'),
(3160002,380392,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Dawnkeeper''s Shoulderpads'),
(3160002,380453,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Argent Templar''s Dreaming Royal Band'),
(3160002,380614,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Bonewarden''s Runed Staff'),
(3160002,380621,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Stalkers of Hallowed Flame'),
(3160002,380653,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Carapace of the Hallowed Ground'),
(3160002,380897,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | Embersteel Waistband'),
(3160002,380949,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | The Manawoven Trousers'),
(3160002,380951,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000548 | The Scourgebound Great Lance');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3160003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3160003,200216,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | The Aged Legguards'),
(3160003,200490,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Warbelt, Scourge Veil'),
(3160003,200875,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Battlemaiden''s Drape'),
(3160003,220023,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | The Rimebound Chainmail'),
(3160003,220488,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Watchful Warbelt of Storm King'),
(3160003,220811,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Dreamkeeper''s Waistchain'),
(3160003,240314,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Dragonmarked Boots'),
(3160003,240715,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Heavy Loop of the Ice Forge'),
(3160003,240966,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Soulmarked Helm'),
(3160003,260036,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Icetouched Claws of Nesingwary Camp'),
(3160003,260573,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Murderous War Sword of Frozen Gate'),
(3160003,260759,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Hoop of the Hallowed Ground'),
(3160003,260931,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Moonwarden''s Trousers of the Blue Dragon'),
(3160003,320352,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Shadow Freeze Mark'),
(3160003,320415,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Steel Vengeance Chestpiece'),
(3160003,340267,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Runebands of Broken Road'),
(3160003,340377,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Stoneforged Trousers of Silver Light'),
(3160003,340535,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Trousers, Mystic Snowfall'),
(3160003,340563,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Capelet of Nameless Dead'),
(3160003,340623,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Shaman Staff of the Drake Rider'),
(3160003,360786,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Bone Wand, Ember Lord'),
(3160003,360941,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | The Ethereal Robe'),
(3160003,380272,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000549 | Sorrowful Footguards of Broken Promise');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3160004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3160004,240218,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000551 | Wildwoven Ringlet, Violet Warden''s Oath'),
(3160004,260797,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000551 | Lightblessed Trousers of the Gjalerbron'),
(3160004,260980,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000551 | Dream Carver Shoulder Drape'),
(3160004,280744,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000551 | Hellforged Waistwrap'),
(3160004,320007,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000551 | Locket of the Makers Hand'),
(3160004,360955,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000551 | Scarlet Champion''s Dragonsteel Armbands');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3160005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3160005,200163,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000552 | Undying Greathelm of Death Knight'),
(3160005,200461,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000552 | Effigy of the Hidden Forge'),
(3160005,200478,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000552 | Visor of the Old Kingdom'),
(3160005,200612,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000552 | Battle Girdle, Wolfheart Plate'),
(3160005,240459,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000552 | Wyrmcarved Waistguard of Wild Crown'),
(3160005,380099,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000552 | Warforged Chain');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3160006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3160006,200312,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000553 | Dragonstalker''s Vambraces'),
(3160006,280866,0,0,0,1,1,1,1,'Generated map_70_difficulty_0 boss_000553 | Warchief''s Skullforged Mystic Wand');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6910 AND `Item` = 2010000126 AND `Reference` = 3160000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6910,2010000126,3160000,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | boss_000547');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4847 AND `Item` = 2010000127 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4847,2010000127,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4848 AND `Item` = 2010000128 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4848,2010000128,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4849 AND `Item` = 2010000129 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4849,2010000129,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4850 AND `Item` = 2010000130 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4850,2010000130,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4851 AND `Item` = 2010000131 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4851,2010000131,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4852 AND `Item` = 2010000132 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4852,2010000132,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4853 AND `Item` = 2010000133 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4853,2010000133,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4855 AND `Item` = 2010000134 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4855,2010000134,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4860 AND `Item` = 2010000135 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4860,2010000135,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4861 AND `Item` = 2010000136 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4861,2010000136,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4863 AND `Item` = 2010000137 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4863,2010000137,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6907 AND `Item` = 2010000138 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6907,2010000138,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6908 AND `Item` = 2010000139 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6908,2010000139,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7012 AND `Item` = 2010000140 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7012,2010000140,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7022 AND `Item` = 2010000141 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7022,2010000141,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7023 AND `Item` = 2010000142 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7023,2010000142,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7030 AND `Item` = 2010000143 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7030,2010000143,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7175 AND `Item` = 2010000144 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7175,2010000144,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7290 AND `Item` = 2010000145 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7290,2010000145,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7320 AND `Item` = 2010000146 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7320,2010000146,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7321 AND `Item` = 2010000147 AND `Reference` = 3160001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7321,2010000147,3160001,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6906 AND `Item` = 2010000148 AND `Reference` = 3160002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6906,2010000148,3160002,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | boss_000548');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7228 AND `Item` = 2010000149 AND `Reference` = 3160003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7228,2010000149,3160003,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | boss_000549');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7206 AND `Item` = 2010000150 AND `Reference` = 3160004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7206,2010000150,3160004,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | boss_000551');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7291 AND `Item` = 2010000151 AND `Reference` = 3160005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7291,2010000151,3160005,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | boss_000552');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4854 AND `Item` = 2010000152 AND `Reference` = 3160006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4854,2010000152,3160006,2,0,1,0,1,1,'Generated encounter attachment | map_70_difficulty_0 | boss_000553');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3170000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3170000,200580,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | Ethereal Surcoat of the Wyrmskull'),
(3170000,220052,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | War Leggings of the Blood Promise'),
(3170000,260423,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | Lightwoven Girdle of Burning Steppes'),
(3170000,260551,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | Armored Headguard'),
(3170000,280863,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | Moon Queen''s Great Stave'),
(3170000,320284,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | Crypt Stone Headguard'),
(3170000,320747,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | Armguards of Drowned Hall'),
(3170000,320973,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000378 | Runeforged Charmstone of Lost Watch');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3170001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3170001,200007,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Necrotic Necklace of the Blood Tide'),
(3170001,200084,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Feathered Belt of the Ancestor Spirit'),
(3170001,200258,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Brutal Wrap'),
(3170001,200304,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Girdle of Golden Moon'),
(3170001,200458,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Celestial Mantle'),
(3170001,200563,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Falcon Maw Waistguard'),
(3170001,200632,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Warband of the Bone Wastes'),
(3170001,200701,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Warbelt, Iron Slayer'),
(3170001,200719,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Earthforged Titan Axe'),
(3170001,200751,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Lost Knight''s Charmstone'),
(3170001,200793,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Sable Ringlet'),
(3170001,200802,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Steelforged Shoulder Guards'),
(3170001,200840,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ancient Queen''s Bracers'),
(3170001,200882,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Starlit Warboots of Pale Watch'),
(3170001,200889,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Cabalistic War Leggings of Ebon Watch'),
(3170001,200938,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Winterlord''s Mark'),
(3170001,200963,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Wyrmlord''s Forgeblessed Ward'),
(3170001,200983,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Gloomed Feather of the Cold Moon'),
(3170001,220110,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ghostcaller''s Watchful Boots'),
(3170001,220170,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Manawoven Traveling Cloak of Ancient Thorn'),
(3170001,220226,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Rangemaster''s Prayerbound Wargrips'),
(3170001,220238,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Treads of Valiance Keep'),
(3170001,220263,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Raven Ward Saber'),
(3170001,220372,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Eternal Loop'),
(3170001,220484,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Warlord Wargrips of the Fallen Watch'),
(3170001,220532,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Shoulder Guards of Sacred Flame'),
(3170001,220590,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Runelord''s Backcloth'),
(3170001,220610,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Moon King''s Dragonhide Fingerband'),
(3170001,220637,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Brightwarden''s Drakescale Gorget'),
(3170001,220639,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Wintertouched Surcoat, Blacksmith''s Oath'),
(3170001,220644,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Prime Wolf Faceguard'),
(3170001,220651,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Sainted Waistguard of the Mana Wyrm'),
(3170001,220655,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Witchlord''s Treads of the Winter Memory'),
(3170001,220891,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Hexed Harness'),
(3170001,220894,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Terrible Raider Axe of Silver Hand'),
(3170001,220915,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Icewarden''s Amulet of the Final Promise'),
(3170001,220995,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Forgekeeper''s Wintersteel Greaves'),
(3170001,240021,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Grim Hex Boots'),
(3170001,240088,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Hallowed Headdress of the Frozen Memory'),
(3170001,240113,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Dreamwarden''s Loop'),
(3170001,240215,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Greenwood Chestguard'),
(3170001,240224,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ravenwarden''s Warcloak'),
(3170001,240267,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Jagged Chestpiece'),
(3170001,240300,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Blacksteel Chestpiece'),
(3170001,240311,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Umbral Shoulderpads'),
(3170001,240409,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Battleblade of the Ashen March'),
(3170001,240461,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Witchlord''s Mantle of the Broken Road'),
(3170001,240526,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Shadowguard''s Strap'),
(3170001,240619,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Glittering Waistband'),
(3170001,240643,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Blunderbuss of Moonwarden'),
(3170001,240682,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Worldwarden''s Pants of the Khaz Modan'),
(3170001,240706,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Iceforged Clutches of the Frost Giant'),
(3170001,240953,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Grips of Military Wing'),
(3170001,260040,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Bloodstained Gloves'),
(3170001,260094,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Tombforged Wristguards of the Great Hunt'),
(3170001,260263,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Titanforged Breeches of the Storm Banner'),
(3170001,260284,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Poniard of the Red Dragon'),
(3170001,260296,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Gleaming Shoulderwraps'),
(3170001,260339,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Bloodkeeper''s Locket'),
(3170001,260395,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Duskwoven Breeches'),
(3170001,260429,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Shattered Song Signet Ring'),
(3170001,260469,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Voidbound Shoulderpads'),
(3170001,260486,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Haunted Chestguard of Ebon March'),
(3170001,260587,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Band, Astral Wall'),
(3170001,260595,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Girdle, Doom Torment'),
(3170001,260613,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Striders of Scarlet Flame'),
(3170001,260659,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Starcaller''s Deathmask of the Far North'),
(3170001,260710,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Briarbound Spaulders of the Pale Watch'),
(3170001,260870,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Glacial Great Cape of the Kings Promise'),
(3170001,260909,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Fierce Shoulderpads of the Dragon Pact'),
(3170001,260926,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Stormkeeper''s Warped Mask'),
(3170001,260940,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Spellbound Mark of Iron March'),
(3170001,260959,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Signet Ring of the Hallowed Ground'),
(3170001,280060,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Everfrost Skullcrusher'),
(3170001,280114,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Hardened Emblem of Makers Terrace'),
(3170001,280162,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Rune King''s Footwraps'),
(3170001,280222,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Silent Keeper''s Cloak'),
(3170001,280277,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Duskwoven Fingerband of Deadwind Pass'),
(3170001,280487,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Briarwoven Traveling Cloak'),
(3170001,280554,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Frostbitten Pants'),
(3170001,280624,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Shoulder Cape of the Frozen Watch'),
(3170001,280675,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Trousers, Drake Hunter'),
(3170001,280714,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Obsidian Raiment of Wind King'),
(3170001,280768,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Skirt, Ebon Bringerless'),
(3170001,280796,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Old Knight''s Raiment'),
(3170001,280812,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Violet Helm Vestments'),
(3170001,280894,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Dragon King''s Moonlit Keepsake'),
(3170001,280906,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Boots of the Golden Light'),
(3170001,320047,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Silver King''s Mask'),
(3170001,320080,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Watchkeeper''s Starforged Shroud'),
(3170001,320181,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Last Warden''s Treads of the Bloodguard'),
(3170001,320213,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Razor-edged Leggings of the Black Ice'),
(3170001,320220,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Headdress of Forgotten Watch'),
(3170001,320225,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Earthwarden''s Obsidian Skull'),
(3170001,320251,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Pants of the Holy Flame'),
(3170001,320264,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Sunbound Armguards'),
(3170001,320290,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Voidlord''s Runeaxe'),
(3170001,320341,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Murderous Walkers'),
(3170001,320343,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Blackguard''s Clutches of the Star Forge'),
(3170001,320466,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Fernwoven Shoulderpads'),
(3170001,320542,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Headdress, Night Claw'),
(3170001,320630,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Goldbound Pendant Chain of the Black Forge'),
(3170001,320643,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Spellbinder''s Seal'),
(3170001,320652,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Runestaff, Eagle Bolt'),
(3170001,320705,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Defiant Clublike Mace of Death Gate'),
(3170001,320724,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Battlelord''s Shoulderwraps'),
(3170001,320756,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Enduring Shoulderpads'),
(3170001,320805,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Bloodforged Strap'),
(3170001,320806,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Haunted Mantle of Broken Spear'),
(3170001,320813,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Hoop of Hidden Path'),
(3170001,320901,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Unbroken Warband'),
(3170001,320904,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Frostguard''s Handguards'),
(3170001,320919,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Handguards of the Great Hunt'),
(3170001,320948,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ringlet of Silent Crypt'),
(3170001,320968,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Farseer''s Iron Mace'),
(3170001,320994,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Illusory Wristbands of the Earthshaper'),
(3170001,340028,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ancient March Raiment'),
(3170001,340110,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Waistwrap, Savage Grasp'),
(3170001,340253,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Terrible Regalia'),
(3170001,340256,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Sepulchral Chain of Ancestor Spirit'),
(3170001,340447,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | First King''s Voidforged Vestments'),
(3170001,340501,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Bracelets of the Makers Terrace'),
(3170001,340541,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ghostfire Ash Keepsake'),
(3170001,340654,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Handwraps of Silver Crown'),
(3170001,340738,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Icon, Unholy Shine'),
(3170001,340764,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Signet, Bitter Seal'),
(3170001,340818,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Broken Torment Binding'),
(3170001,340841,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Headdress of Void Watch'),
(3170001,340940,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Scourgebound Heart'),
(3170001,340997,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Bracelets of Demon Watch'),
(3170001,360063,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Silent Keeper''s Promise'),
(3170001,360099,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Earthwarden''s Treads of the White Crown'),
(3170001,360180,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Runeblade of the War Forge'),
(3170001,360191,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Wyrmkeeper''s Graspers of the Crypt Watch'),
(3170001,360202,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Stonehewn Headdress of the Violet Star'),
(3170001,360288,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Shadowlord''s Bindings'),
(3170001,360299,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Tunic of the Crusader Watch'),
(3170001,360314,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Moonkeeper''s Mitts'),
(3170001,360340,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Trousers, Mystic Hide'),
(3170001,360362,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Wildguard''s Epaulets'),
(3170001,360416,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Locket, Crimson Sigil'),
(3170001,360460,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Drape of Forgotten Oath'),
(3170001,360466,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Blood Freeze Kris'),
(3170001,360468,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Nightbound Robe of the Arcane Moon'),
(3170001,360567,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Silver Queen''s Sash'),
(3170001,360695,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Longstaff, Sky Cleaver'),
(3170001,360757,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Promise, Raven Light'),
(3170001,360826,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Regalia, Hallowed Talon'),
(3170001,360851,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Hoop of Shadow Pact'),
(3170001,360870,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ravenlord''s Mitts'),
(3170001,360878,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Stonecaller''s Arcanized Archmage Staff'),
(3170001,380015,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Plaguebound Shoulderpads'),
(3170001,380060,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Warwarden''s Mirror'),
(3170001,380064,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Sable Rune Band'),
(3170001,380254,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Astral Watch Trousers'),
(3170001,380267,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Brightwarden''s Runestaff'),
(3170001,380351,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Wargrips of Ice Moon'),
(3170001,380374,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Blood King''s Shoulderguards'),
(3170001,380402,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Stormwrought Armguards of Red Dawn'),
(3170001,380461,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Unbroken Clasp of Celestial Gate'),
(3170001,380541,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Rotting Wristbands'),
(3170001,380544,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Argent Templar''s Circle'),
(3170001,380553,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Saronite Stalkers of Nightwatch'),
(3170001,380568,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Treads of the Twilight Reach'),
(3170001,380592,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Royal Cloak of the Forgotten Memory'),
(3170001,380598,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | The Ritual Cap'),
(3170001,380623,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Ebon Marshal''s Girdle'),
(3170001,380646,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Coldforged Carapace, Wayfarer''s Oath'),
(3170001,380650,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Icetouched Runestone'),
(3170001,380678,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Thunderwarden''s Dawnlit Longcloak'),
(3170001,380697,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Cursed Chestpiece of Frost Giant'),
(3170001,380721,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Claws, Gray Vault'),
(3170001,380749,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Grips of Frozen Memory'),
(3170001,380813,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Windforged Band of the Emerald Watch'),
(3170001,380846,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Dawnwarden''s Pitiless Cowl'),
(3170001,380849,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Saronite Pants of Searing Gorge'),
(3170001,380883,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Argent Knight''s Girdle of the Hidden Road'),
(3170001,380907,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Spaulders, Astral Bite'),
(3170001,380917,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Leggings of the Twilight Reach'),
(3170001,380947,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Quarterstaff of the Bone Gate'),
(3170001,380955,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Harness, Doom Judgment'),
(3170001,380956,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 trash | Firewarden''s Hourglass');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3170002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3170002,200362,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Moonbound Wristguards'),
(3170002,200374,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Surcoat of Hearthguard'),
(3170002,240570,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Forgotten Rend Cowl'),
(3170002,260640,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Argent Knight''s Breeches'),
(3170002,260735,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Violet Mage''s Trousers'),
(3170002,280538,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Mooncaller''s Raiment of the Bronze Dragon'),
(3170002,280647,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Wintertouched Headdress of Makers Vault'),
(3170002,320608,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Plagueforged Choker of Fallen Lord'),
(3170002,340927,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Wolfsworn Stone'),
(3170002,360234,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Lost Gloom Mitts'),
(3170002,360438,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Coldforged Skirt of the Gundrak'),
(3170002,360779,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Rimewarden''s Epaulets'),
(3170002,380605,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000380 | Rune King''s Vengeful Vest');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3170003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3170003,200400,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | The Nightshrouded Band'),
(3170003,200902,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Manaforged Locket'),
(3170003,220309,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Gloves, Violet Pledge'),
(3170003,220713,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Boots of Ebon Blade'),
(3170003,280051,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Defiant Longstaff, Shieldmaster''s Oath'),
(3170003,340127,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Brittle Shoulderwraps of the Valgarde'),
(3170003,340176,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Ashcaller''s Diadem of the War Crown'),
(3170003,340490,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | The Forgeblessed Choker'),
(3170003,360187,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Neckchain of the Obsidian Sanctum'),
(3170003,360582,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Ominous Talisman of the Ivory Crown'),
(3170003,360885,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | The Mistbound Walkers'),
(3170003,380102,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Dragonlord''s Clutches of the Sun Watch'),
(3170003,380332,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Warwarden''s Titan Hammer'),
(3170003,380367,0,0,0,1,1,1,1,'Generated map_90_difficulty_0 boss_000381 | Soulforged Shroud of Damned Host');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7079 AND `Item` = 2010000153 AND `Reference` = 3170000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7079,2010000153,3170000,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | boss_000378');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6206 AND `Item` = 2010000154 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6206,2010000154,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6207 AND `Item` = 2010000155 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6207,2010000155,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6211 AND `Item` = 2010000156 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6211,2010000156,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6212 AND `Item` = 2010000157 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6212,2010000157,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6218 AND `Item` = 2010000158 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6218,2010000158,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6219 AND `Item` = 2010000159 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6219,2010000159,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6220 AND `Item` = 2010000160 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6220,2010000160,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6223 AND `Item` = 2010000161 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6223,2010000161,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6224 AND `Item` = 2010000162 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6224,2010000162,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6225 AND `Item` = 2010000163 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6225,2010000163,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6226 AND `Item` = 2010000164 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6226,2010000164,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6227 AND `Item` = 2010000165 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6227,2010000165,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6228 AND `Item` = 2010000166 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6228,2010000166,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6230 AND `Item` = 2010000167 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6230,2010000167,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6232 AND `Item` = 2010000168 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6232,2010000168,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6233 AND `Item` = 2010000169 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6233,2010000169,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6234 AND `Item` = 2010000170 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6234,2010000170,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6329 AND `Item` = 2010000171 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6329,2010000171,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6391 AND `Item` = 2010000172 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6391,2010000172,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6392 AND `Item` = 2010000173 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6392,2010000173,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6407 AND `Item` = 2010000174 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6407,2010000174,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7603 AND `Item` = 2010000175 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7603,2010000175,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7849 AND `Item` = 2010000176 AND `Reference` = 3170001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7849,2010000176,3170001,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6235 AND `Item` = 2010000177 AND `Reference` = 3170002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6235,2010000177,3170002,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | boss_000380');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6229 AND `Item` = 2010000178 AND `Reference` = 3170003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6229,2010000178,3170003,2,0,1,0,1,1,'Generated encounter attachment | map_90_difficulty_0 | boss_000381');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3180000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3180000,200109,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Pauldrons of Bronzebeard Clan'),
(3180000,200548,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Footplates of Thunder King'),
(3180000,200964,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Spiritcaller''s Eye of the Red Flight'),
(3180000,200974,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Runeforged Charm of the Moon Watch'),
(3180000,220412,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | The Carved Shoulderplates'),
(3180000,220543,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Talisman, Wild Feather'),
(3180000,220864,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Titanbound Grand Warhammer of Long Road'),
(3180000,240735,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Ringlet of the Silver Banner'),
(3180000,260062,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Grim Treads'),
(3180000,260323,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Warmaster Saber'),
(3180000,260527,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Coal-black Waistband'),
(3180000,260898,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Leggings of the Emerald Star'),
(3180000,280874,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Valiant Shoes, Forgotten Knight''s Oath'),
(3180000,320132,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Vambraces of Arcane Star'),
(3180000,320312,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Warboots of the Scarlet Bastion'),
(3180000,320501,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Spiritwarden''s Wintersteel War Mantle'),
(3180000,320824,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Bloodied Harness'),
(3180000,320959,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Forgotten Knight''s War Leggings'),
(3180000,320966,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Frostscarred Chausses'),
(3180000,340333,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Drakelord''s Runestaff of the Fallen King'),
(3180000,340428,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Moonforged Backcloth of Argent Dawn'),
(3180000,340532,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Wyrmcaller''s Robes of the Scholomance'),
(3180000,340719,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Waistwrap of White Crown'),
(3180000,360123,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Bonewarden''s Nerubian Cord'),
(3180000,360142,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Hearthkeeper''s Sinister Raiment'),
(3180000,360158,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Clouded Skirt of the Wild Heart'),
(3180000,360494,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Twilight-forged Cape of Makers Hand'),
(3180000,360588,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Tiara of Moon Spirit'),
(3180000,360875,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Stormcaller''s Shoulderpads'),
(3180000,380521,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Windforged Gloves of the Wintergrasp'),
(3180000,380704,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | Battlemage''s Coil of the Bone Gate'),
(3180000,380950,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000485 | The Sunhallowed Seer Staff');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3180001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3180001,200005,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Handplates of Borean Tundra'),
(3180001,200010,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Signet of the Black Temple'),
(3180001,200012,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warlord Signet, Deathkeeper''s Oath'),
(3180001,200057,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Great Chopper of the Cold Flame'),
(3180001,200060,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Blood King''s Primeval Bracers'),
(3180001,200067,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Earthkeeper''s Stormmarked Pauldrons'),
(3180001,200085,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Murderous Battlehelm of the Stratholme'),
(3180001,200087,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sacred Girdle'),
(3180001,200088,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Tarnished Harpoon of the Frozen Road'),
(3180001,200101,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Azure War Pauldrons of Light Watch'),
(3180001,200178,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Faceguard of Crimson Flame'),
(3180001,200183,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warbelt of the Pale Flame'),
(3180001,200190,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ancestor''s Bracers of the Tempest Keep'),
(3180001,200259,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warchief''s Helm'),
(3180001,200264,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ornate Orb'),
(3180001,200276,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Voidlord''s War Greaves of the Dread Wyrm'),
(3180001,200284,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Sunhallowed Gauntlets'),
(3180001,200317,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Great Pauldrons of the Final Promise'),
(3180001,200329,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Footplates of the Arcane Eye'),
(3180001,200345,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Titan King''s Gray Wargrips'),
(3180001,200347,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Forgotten Knight''s Soldierly Waistguard'),
(3180001,200364,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Traveling Cloak of the Death March'),
(3180001,200376,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Handplates of the Zim Torga'),
(3180001,200382,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Maul of the Ancient Watch'),
(3180001,200418,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Battlemage''s Argent Torc'),
(3180001,200475,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Vigilant Visor'),
(3180001,200536,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shadowmage''s Starwoven Waistplate'),
(3180001,200543,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Lost Queen''s Traveling Cloak'),
(3180001,200600,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Red Watch Legguards'),
(3180001,200606,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Lightforged Legplates of the Ancient Watch'),
(3180001,200607,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Vambraces of the Stormwind Guard'),
(3180001,200623,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Slasher, Lion Wake'),
(3180001,200652,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sollerets, Last Ice'),
(3180001,200653,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Gravekeeper''s Warplate'),
(3180001,200657,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Axe, Ice Edge'),
(3180001,200673,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Old Knight''s War Leggings'),
(3180001,200721,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Silvered Legplates'),
(3180001,200726,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wildcaller''s Great Pauldrons'),
(3180001,200729,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Thunderlord''s Iron Boots'),
(3180001,200731,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Vambraces, Red Horn'),
(3180001,200790,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Lost Sabatons'),
(3180001,200794,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Warden Sollerets'),
(3180001,200828,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Gold Crush Vambraces'),
(3180001,200832,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hateful Warcloak of the Violet Hold'),
(3180001,200838,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cursed Sollerets'),
(3180001,200841,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warchief''s Starsteel Greathelm'),
(3180001,200846,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cuirass of the Dalaran Watch'),
(3180001,200906,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ebon Champion''s Forgeblessed Girdle'),
(3180001,200910,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Arcanist''s Cuirass'),
(3180001,200949,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Legguards of the Midnight Moon'),
(3180001,200987,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Scale, Serpent Crush'),
(3180001,220017,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Vengeful Medallion of Makers Overlook'),
(3180001,220020,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cape of Deep Anvil'),
(3180001,220024,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Kingsguard Loop'),
(3180001,220034,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Ironclad Cape'),
(3180001,220057,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Rune Band of Thunder King'),
(3180001,220060,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hexed Cloak'),
(3180001,220062,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Enduring Longcloak'),
(3180001,220122,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Rune Blade Warhelm'),
(3180001,220126,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Thunder Echo Greaves'),
(3180001,220184,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Starwarden''s Vambraces'),
(3180001,220185,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ironlord''s Windbound Great Pauldrons'),
(3180001,220207,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Great Hammer, Starfire Wound'),
(3180001,220236,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Battlehelm, Far Bite'),
(3180001,220253,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wrathful Iron Boots of the Makers Terrace'),
(3180001,220278,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warband of Dawn Star'),
(3180001,220290,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Leafwoven Armguards'),
(3180001,220315,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ashkeeper''s Warhelm of the Emerald Wilds'),
(3180001,220324,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Helm of Lost Memory'),
(3180001,220345,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dreambound Carapace'),
(3180001,220354,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Rimewalker''s Fingerband of the Death March'),
(3180001,220360,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Scarlet Marshal''s Darkened Battle Girdle'),
(3180001,220374,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grim Iron Boots'),
(3180001,220381,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warbelt, Wind Dawn'),
(3180001,220402,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Spiritforged Legguards'),
(3180001,220427,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Leafbound Lens of Titan Watch'),
(3180001,220428,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Boar Creed Hoop'),
(3180001,220431,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cutlass of the Sable Watch'),
(3180001,220432,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Greathelm of Last Promise'),
(3180001,220456,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Whitegold Legguards'),
(3180001,220483,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Nightshrouded Legguards'),
(3180001,220491,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Firewarden''s Shoulderplates'),
(3180001,220517,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Handguards of Westguard Keep'),
(3180001,220520,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Royal Band of Shadow Ritual'),
(3180001,220553,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Carved Armguards'),
(3180001,220595,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Lightbound Shoulderplates of Dawn Vanguard'),
(3180001,220699,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Footplates, Nightfang Keeper'),
(3180001,220747,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Relicbound Signet Ring'),
(3180001,220776,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Fernwoven Great Pauldrons of Pale Crown'),
(3180001,220804,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Voidcaller''s War Leggings'),
(3180001,220868,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Forgeblessed Cuirass'),
(3180001,220911,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Greaves, Shattered Forge'),
(3180001,220937,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Gold Grasp Greatsword'),
(3180001,220943,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ashen King''s Mountainborn Seal Ring'),
(3180001,220951,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Steelbound Warplate of Ice Moon'),
(3180001,220992,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Snowforged Handplates'),
(3180001,240011,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Iceforged Legmail of the Altar of Sseratus'),
(3180001,240020,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Boneguard''s Silent Shoulderguards'),
(3180001,240026,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Savage Fate Loop'),
(3180001,240046,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Embercaller''s Boots of the Broken Shield'),
(3180001,240063,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Starbound Shoulder Guards'),
(3180001,240065,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warden Battlecloak'),
(3180001,240078,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hauberk of the Ancient Pact'),
(3180001,240094,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Runeguard''s Boots'),
(3180001,240097,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Veil, Low Doom'),
(3180001,240107,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Arcanist''s Stormwrought Warbelt'),
(3180001,240121,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grips of the Crimson Crown'),
(3180001,240194,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Silverwarden''s Wyrmhide Great Chopper'),
(3180001,240255,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Necklace, Unholy Sun'),
(3180001,240307,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Furious Runesword'),
(3180001,240354,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Handguards of the Winter Moon'),
(3180001,240373,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Argent Defender''s Neckchain'),
(3180001,240389,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Enduring Chainmail of Ancient Promise'),
(3180001,240403,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Jagged Mail of the Last Light'),
(3180001,240435,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Mail, Starfang Watch'),
(3180001,240470,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Sunblessed Stone'),
(3180001,240508,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Weathered Leggings'),
(3180001,240546,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Mail of the Kings Road'),
(3180001,240555,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Witchbound Warbelt'),
(3180001,240592,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grey Punch Boots'),
(3180001,240660,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Legmail of Bone Crown'),
(3180001,240675,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Execution Blade, Death Glyph'),
(3180001,240685,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | First Warden''s Pale-blue Pendant Chain'),
(3180001,240713,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Baleful Chainmail'),
(3180001,240739,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Rimekeeper''s Dire War Mantle'),
(3180001,240749,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Snowy Boots'),
(3180001,240756,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hauberk of the Fire Spirit'),
(3180001,240808,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bracers of the Crypt Lord'),
(3180001,240826,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Twilightwarden''s Scourgeforged Crankbow'),
(3180001,240835,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Nightshrouded Hunter Crossbow'),
(3180001,240850,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Key of the Ebon Pact'),
(3180001,240859,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Earthen Armguards of the Ebon Crown'),
(3180001,240886,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Promise, Soul Arrow'),
(3180001,240909,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Armguards of the Emerald Grove'),
(3180001,240929,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Runic Great Hauberk of the Blackened Sky'),
(3180001,240948,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Fel Leggings'),
(3180001,240957,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hollow Chainmail'),
(3180001,240969,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Frost King''s War Leggings'),
(3180001,240981,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Graveborn Wristguards of Shadow Moon'),
(3180001,240997,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Mark of Kirin Tor'),
(3180001,260008,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shoulderpads, Far Decree'),
(3180001,260071,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ancestor''s Frostmarked Stalkers'),
(3180001,260085,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Corrupted Footguards of the Star Watch'),
(3180001,260138,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Rimelord''s Harsh Headguard'),
(3180001,260143,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ancient Knight''s Scimitar'),
(3180001,260149,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Loop, Ebon Legacy'),
(3180001,260163,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Boots of the Deep Earth'),
(3180001,260179,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Chestpiece, Skull Hex'),
(3180001,260184,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Titanbound Spaulders of the Great North'),
(3180001,260210,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cinch, Mystic Spirit'),
(3180001,260218,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Legguards of the Utgarde Pinnacle'),
(3180001,260258,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Headguard of Death Lord'),
(3180001,260259,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Skyforged Strap'),
(3180001,260261,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Darkforged Armguards'),
(3180001,260298,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Thundersteel Cap'),
(3180001,260313,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ravenkeeper''s Blessed Pendant Chain'),
(3180001,260347,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bloodforged Stalkers'),
(3180001,260373,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Trousers of Ebon Blade'),
(3180001,260407,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Nightbound Legwraps of the Final Watch'),
(3180001,260419,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Gloves, Stone Hail'),
(3180001,260457,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Silver Queen''s Woeful Legguards'),
(3180001,260463,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Promise, Fallen Verse'),
(3180001,260480,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Scourged Cap'),
(3180001,260485,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bitter Headguard'),
(3180001,260549,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Breeches, Void Beacon'),
(3180001,260550,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Sainted Legguards'),
(3180001,260598,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Illusory Cap'),
(3180001,260618,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Beads of the Grim March'),
(3180001,260620,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Greenwood Cowl'),
(3180001,260626,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shoulderwraps, Spider Star'),
(3180001,260630,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grips of the Arcane Watch'),
(3180001,260652,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warder Cloak of Iron Watch'),
(3180001,260653,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Silent Keeper''s Sword'),
(3180001,260671,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Forge Bloom Totem'),
(3180001,260715,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Frostveined Pendant Chain'),
(3180001,260723,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grips, Nightfang Starfall'),
(3180001,260743,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Watchful Walkers'),
(3180001,260748,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Unquiet Hymn Stiletto'),
(3180001,260766,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ironforged Blade of the Wyrm King'),
(3180001,260767,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bronzed Fingerband of the Nesingwary Camp'),
(3180001,260776,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Chestpiece of Blue Dragon'),
(3180001,260811,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Spellbinder''s Skinner'),
(3180001,260823,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Forsworn Harness'),
(3180001,260827,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | War Dagger of Tempest Keep'),
(3180001,260851,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bright Pendant Chain of the Raven Queen'),
(3180001,260929,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shoulderpads of Silent Road'),
(3180001,260936,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Treads of Iron March'),
(3180001,260941,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Tunic of the Borean Tundra'),
(3180001,260954,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Broken Grips of the Stratholme'),
(3180001,260957,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Starforged Shoulderguards of Wyrm King'),
(3180001,260958,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Leafwoven Treads'),
(3180001,260987,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Faithful Treads, Frozen Queen''s Oath'),
(3180001,280008,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Royal Band of the Abyssal Flame'),
(3180001,280011,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hood of Moon Crown'),
(3180001,280050,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Blighted Gloves of Red Dawn'),
(3180001,280064,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bloodguard''s Runic Cap'),
(3180001,280075,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Legwraps of Last Oath'),
(3180001,280091,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Lightwarden''s Warcloak'),
(3180001,280126,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Moonkeeper''s Graspers'),
(3180001,280127,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Blade Dirge Royal Band'),
(3180001,280180,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cowl, Iron Rime'),
(3180001,280193,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Berserker Headdress of the Blood Watch'),
(3180001,280233,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Waistwrap of the Northern Light'),
(3180001,280236,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bracelets, Unbroken Pledge'),
(3180001,280247,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Trousers of the Construct Wing'),
(3180001,280255,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dragonlord''s Kilt of the Wind Watch'),
(3180001,280265,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Mystic Plate Rod'),
(3180001,280282,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Steelbound Skullcap'),
(3180001,280294,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Graspers, Mana Reaver'),
(3180001,280300,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Earthforged Wristwraps of Crimson Flame'),
(3180001,280320,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Savage Pants'),
(3180001,280333,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Effigy of Sunwell'),
(3180001,280353,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Warped Headdress'),
(3180001,280372,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Deep Hand Neckchain'),
(3180001,280392,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cuffs of the Howling Wind'),
(3180001,280395,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Vest of the Distant Memory'),
(3180001,280396,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Stonewarden''s Runering of the Blue Flight'),
(3180001,280412,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Illusory Cudgel'),
(3180001,280415,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Voidforged Shoes of the Burning Crown'),
(3180001,280449,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Silver Doom Beads'),
(3180001,280454,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Flamecaller''s Zealous Armbands'),
(3180001,280467,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Drakeforged Raiment'),
(3180001,280510,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Worldworn Cuffs'),
(3180001,280524,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Holy Memory Vest'),
(3180001,280544,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Storm King''s Stone'),
(3180001,280575,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wildcaller''s Mage Staff'),
(3180001,280589,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Signet Ring, Primal Vine'),
(3180001,280591,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Boots of the Crimson Banner'),
(3180001,280596,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sandals of the Pale Flame'),
(3180001,280600,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Northkeeper''s Vest of the Scarlet Watch'),
(3180001,280611,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Falcon Storm Ring'),
(3180001,280654,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Vicious Lens'),
(3180001,280662,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wolfguard''s Trousers'),
(3180001,280673,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dread Warden Insignia'),
(3180001,280679,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Soulwarden''s Sash of the North Wind'),
(3180001,280682,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Runebands, Wildfire Edge'),
(3180001,280701,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ebon Crusader''s Darkforged Pants'),
(3180001,280740,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wrathful Diadem'),
(3180001,280749,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sainted Hoop of the Dawn Oath'),
(3180001,280754,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Warscarred Veil'),
(3180001,280776,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Deep Shine Vest'),
(3180001,280811,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Binding of Holy Flame'),
(3180001,280813,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Effigy of the Final Stand'),
(3180001,280837,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Violet Mage''s Boots of the Red Dawn'),
(3180001,280872,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Windkeeper''s Skirt of the Dread Crown'),
(3180001,280882,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | West Decree Clasp'),
(3180001,280893,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Soulkeeper''s Runebands'),
(3180001,280919,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hammer Bite Skirt'),
(3180001,280926,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Merciless Shoulderwraps'),
(3180001,280933,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Conqueror Handwraps'),
(3180001,280941,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Scarlet Inquisitor''s Rotting Longstaff'),
(3180001,280954,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Skyforged Greatstaff'),
(3180001,280965,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Stormsteel Fingerband of the Ivory Crown'),
(3180001,320002,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Purified Leggings'),
(3180001,320072,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bloodforged Footguards of the Wyrm King'),
(3180001,320107,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Tarnished Shoulder Guards'),
(3180001,320145,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Darkforged Spaulders of Silver Flame'),
(3180001,320154,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sunwarden''s Consecrated Girdle'),
(3180001,320164,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shield Snow War Leggings'),
(3180001,320203,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dragonlord''s Vambraces'),
(3180001,320204,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bloodkeeper''s Starforged Nightcloak'),
(3180001,320214,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Furious Armguards of Wild King'),
(3180001,320215,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Stormmarked Grips, Nightcaller''s Oath'),
(3180001,320222,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hallowed Shade Runering'),
(3180001,320233,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Rimekeeper''s Warboots'),
(3180001,320296,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shoulder Guards, Dire Bloom'),
(3180001,320375,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Old Keeper''s Girdle of the Great Hunt'),
(3180001,320400,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Mark of Freya Garden'),
(3180001,320536,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warpriest''s Chain of the Wind King'),
(3180001,320549,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bonebound Headguard'),
(3180001,320550,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Medallion, Storm Plate'),
(3180001,320552,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Staff of the White Crown'),
(3180001,320579,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Chestguard of Void Crown'),
(3180001,320587,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dawnkeeper''s Spire'),
(3180001,320590,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Runemarked Vambraces of Dragon Guard'),
(3180001,320593,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Resolute Headguard'),
(3180001,320604,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Battlecloak of Storm Forge'),
(3180001,320605,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ebon Champion''s Warlord Mail'),
(3180001,320614,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Deepdelver Wargrips'),
(3180001,320633,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Seer''s Cape of the Red Moon'),
(3180001,320637,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Battle Staff of Grizzly Hills'),
(3180001,320644,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Talisman, Winter Branch'),
(3180001,320645,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Haunted Waistguard of Crimson Watch'),
(3180001,320670,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wallshield, Dusk Keeper'),
(3180001,320709,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ravenkeeper''s War Mantle'),
(3180001,320739,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Gloves of the Tempest Keep'),
(3180001,320788,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Armguards, Violet Decree'),
(3180001,320821,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Runecaller''s Idol of the Ancient Storm'),
(3180001,320868,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Necro Rune Headguard'),
(3180001,320871,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Titan Keeper''s Chain of the Silver Hand'),
(3180001,320874,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Winterwarden''s Dawnsteel Traveling Cloak'),
(3180001,320877,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shard of Grim Watch'),
(3180001,320882,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Nightbound Warder Cloak of the Star Crown'),
(3180001,320890,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Eye of the Wyrm King'),
(3180001,320917,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Doomed Backcloth, Ashkeeper''s Oath'),
(3180001,320933,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Rune Queen''s Brooch'),
(3180001,320935,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Waistchain, Emerald Crush'),
(3180001,320936,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Gemmed Band, Far Requiem'),
(3180001,320950,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Titan Queen''s Hardened Mail'),
(3180001,320953,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Gauntlets of the Plague Lord'),
(3180001,320997,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Surcoat, Silver Creed'),
(3180001,320998,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Tombwarden''s Insignia'),
(3180001,340001,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grave Ruin Waistwrap'),
(3180001,340006,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grips, Low Shadow'),
(3180001,340015,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Darksteel Neckguard'),
(3180001,340016,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cuffs of Argent Watch'),
(3180001,340061,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Spirit Staff, Unbroken Keeper'),
(3180001,340063,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Winterborn Shroud, Violet Mage''s Oath'),
(3180001,340093,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sash, Bloodfire Oath'),
(3180001,340125,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Silverguard''s Bracelets'),
(3180001,340230,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Battleworn Sandals of the Scarlet Flame'),
(3180001,340263,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Harsh Pants, Ancestor''s Oath'),
(3180001,340268,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Lost Knight''s Ghostly Gloves'),
(3180001,340282,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Hoary Amulet of Sky Forge'),
(3180001,340307,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Winterlord''s Bitter Walkers'),
(3180001,340324,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bindings of North Road'),
(3180001,340334,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Stormscarred Seal'),
(3180001,340359,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Voidcaller''s Breeches of the Star Grove'),
(3180001,340391,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Skullwarden''s Runebands'),
(3180001,340405,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Earthcaller''s Nightcloak'),
(3180001,340441,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Runic Torque of the Unquiet King'),
(3180001,340445,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Stonefather''s Binding of the Black Forge'),
(3180001,340450,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shoulderwraps of Dark Moon'),
(3180001,340454,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Dawnsteel Charmstone'),
(3180001,340496,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Trousers of the Old Road'),
(3180001,340512,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Grim Warden''s Kilt'),
(3180001,340560,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Argent Marshal''s Ghoststeel Talisman'),
(3180001,340565,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Lost Warden''s Choker'),
(3180001,340578,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Veil, Bloodfang Hammer'),
(3180001,340587,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Waistwrap of the Iron Oath'),
(3180001,340614,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Moon King''s Shoes of the Rimefang'),
(3180001,340620,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warforged Shoulderwraps'),
(3180001,340652,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Headdress of the Cold Flame'),
(3180001,340675,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Greatstaff of the Ebon March'),
(3180001,340680,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Armorsmith''s Merciless Cape'),
(3180001,340686,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wrathful Hood'),
(3180001,340712,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bearwarden''s Chain of the Sons of Hodir'),
(3180001,340730,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Unyielding Grips'),
(3180001,340777,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Lost Keeper''s Gray Footwraps'),
(3180001,340785,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | North Vine Signet'),
(3180001,340803,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Traveling Cloak of the Warsong Hold'),
(3180001,340805,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Footwraps of the Argent Vanguard'),
(3180001,340812,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Argent Champion''s Aged Footwraps'),
(3180001,340822,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Celestial Binding'),
(3180001,340833,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Winterguard''s Wyrmcarved Rod'),
(3180001,340846,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Crypt Mark Graspers'),
(3180001,340866,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Graveborn Falchion'),
(3180001,340870,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Shoulderwraps of Grave King'),
(3180001,340872,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Unhallowed Robes'),
(3180001,340885,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Enduring Graspers of Dragon Throne'),
(3180001,340897,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Deepwarden''s Epaulets of the Frozen Banner'),
(3180001,340906,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Mournful Bindings'),
(3180001,340916,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Fierce March Mitts'),
(3180001,340920,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Jeweled Crystal'),
(3180001,340942,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Winter King''s Shoulderpads'),
(3180001,340965,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Deathlord''s Branch of the Burning Crown'),
(3180001,340982,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Legwraps of Black Harvest'),
(3180001,340996,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warband of the Titan Vault'),
(3180001,360040,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Deathwarden''s Shroud'),
(3180001,360048,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cord of the Long Night'),
(3180001,360108,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Briarbound Runebands'),
(3180001,360150,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Argent Marshal''s Nightwoven Breeches'),
(3180001,360163,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bracelets of Fallen Crown'),
(3180001,360207,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Last Queen''s Gloves'),
(3180001,360208,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Chestwrap of the Raven Queen'),
(3180001,360224,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ghost Creed Skirt'),
(3180001,360233,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Brassbound Robes'),
(3180001,360274,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Void Plate Waistwrap'),
(3180001,360356,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warblade, Nether Mail'),
(3180001,360372,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ominous Scepter'),
(3180001,360374,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Starfire Glow Diadem'),
(3180001,360443,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Clasp of the Lost Crown'),
(3180001,360450,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Diadem, Iron Vault'),
(3180001,360480,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cord of Sholazar'),
(3180001,360486,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Winterworn Handwraps'),
(3180001,360497,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wyrmbound Circlet of Shadowbinder'),
(3180001,360502,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cap, Rune Fall'),
(3180001,360550,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Soulforged Binding'),
(3180001,360552,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Aged Sandals of the Ancient Pact'),
(3180001,360576,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Whitegold Pants'),
(3180001,360603,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Coal-black Pendant Chain'),
(3180001,360688,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Skullbound Epaulets of the Emerald Grove'),
(3180001,360703,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Firekeeper''s Sandals'),
(3180001,360717,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Titanwarden''s Defiant Crystal'),
(3180001,360729,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ancient Keeper''s Cursed Mitts'),
(3180001,360739,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Colossal Binding of the Frozen Banner'),
(3180001,360741,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ancestral Raiment of the Sky Forge'),
(3180001,360746,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Robes, Darkfire Memory'),
(3180001,360816,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sainted Bone Wand of Green Flame'),
(3180001,360820,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Warwarden''s Boots of the Sky Forge'),
(3180001,360839,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Voidkeeper''s Skirt of the Blade Edge'),
(3180001,360894,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Scalebound Bracelets of Frozen King'),
(3180001,360901,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Witchcaller''s Sandals of the Wyrm Forge'),
(3180001,360908,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Thorned Shoulder Cape'),
(3180001,360918,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Stormwarden''s Crimson Longcloak'),
(3180001,360945,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Violet Handwraps'),
(3180001,360958,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Sable Dusk Cowl'),
(3180001,360989,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Voidlord''s Spirit Staff of the Icecrown'),
(3180001,380022,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Faithful Circle of Zul Drak'),
(3180001,380038,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Forgemaster''s Collar'),
(3180001,380039,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wyrm Queen''s Pants'),
(3180001,380075,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wildguard''s Mage Staff'),
(3180001,380087,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dreambound Bodkin of the Shadow Pact'),
(3180001,380098,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Falcon Plate Grips'),
(3180001,380124,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Coil, Ash Flame'),
(3180001,380131,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Royal Cloak of Titan Keeper'),
(3180001,380228,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Heavy Loop of Argent Vanguard'),
(3180001,380232,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Hammered Shoulderpads'),
(3180001,380237,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ironthane''s Solemn Gloves'),
(3180001,380242,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Moon King''s Forsaken Drape'),
(3180001,380274,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Waistguard of the Wild King'),
(3180001,380322,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Carapace of the Rainspeaker Canopy'),
(3180001,380341,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Snowy Belt of Dragon Pact'),
(3180001,380460,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Faded Leggings'),
(3180001,380462,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Girdle of Dark Star'),
(3180001,380493,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ironthane Waistband'),
(3180001,380502,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Red Anvil Locket'),
(3180001,380503,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Demon Mist Spaulders'),
(3180001,380505,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Worldworn Gorget of the Lich King'),
(3180001,380512,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Argent Neckchain'),
(3180001,380520,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dreamwarden''s Legwraps of the Lich King'),
(3180001,380542,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Armguards of Burning Sky'),
(3180001,380555,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ghostfire Memory Vest'),
(3180001,380557,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Veil, Scourge Bane'),
(3180001,380567,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Argent Marshal''s Raider Mirror'),
(3180001,380593,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Moonlord''s Merciless Shoulderpads'),
(3180001,380610,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bloodbound Strap of the Hollow King'),
(3180001,380627,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Carapace of Titan King'),
(3180001,380686,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | The Bearhide Helm'),
(3180001,380687,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Belt, Crypt Glaive'),
(3180001,380705,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Dawncaller''s Dalaran Legwraps'),
(3180001,380714,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Ice Witch''s Grand Warhammer'),
(3180001,380729,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cap of Shattered Gate'),
(3180001,380732,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Raider Waistguard of War Crown'),
(3180001,380750,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Desecrated Greatcloak of the Death Lord'),
(3180001,380752,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Leafwoven Backcloth of Burning Star'),
(3180001,380771,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Old King''s Wintersteel Belt'),
(3180001,380776,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cinch of the Wild Moon'),
(3180001,380800,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Siegebound Battlehammer'),
(3180001,380801,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Last Warden''s Woe-bound Chestpiece'),
(3180001,380806,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Tunic of Dragon Oath'),
(3180001,380871,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Anvilkeeper''s Gilded Headguard'),
(3180001,380886,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Bloodied Chestguard of North Road'),
(3180001,380960,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Cabalistic Legwraps of the Grave King'),
(3180001,380997,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 trash | Wyrmcaller''s Tunic of the Lordaeron Guard');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3180002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3180002,200628,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Wolfcaller''s Ancient Greaves'),
(3180002,200745,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Soldierly Greaves of the Blood Crown'),
(3180002,220088,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Runemaster''s Nightcloak'),
(3180002,220163,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Ghostfire Blade Signet Ring'),
(3180002,220240,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | The Starlit Battlewall'),
(3180002,220267,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Ancient Queen''s Twilight-forged Lens'),
(3180002,220661,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Cryptlord''s Armplates of the Earthshaper'),
(3180002,240009,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Soulwarden''s Ashen Handguards'),
(3180002,240274,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Titanbound Longcloak of Ebon Pact'),
(3180002,240864,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Cursed Cloak'),
(3180002,240954,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Ironthane''s Girdle of the Moon Watch'),
(3180002,260037,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | The Grim Clutches'),
(3180002,260367,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Hollow Shoulderguards of Crusader Oath'),
(3180002,280827,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Lightwoven Shoulderpads'),
(3180002,320182,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Valiant Flanged Mace of the Hearthguard'),
(3180002,320265,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Twilight Warhelm'),
(3180002,340166,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Wrathful Signet of the Dragon Aspect'),
(3180002,340366,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Ruthless Druid Staff of Frozen Heart'),
(3180002,340636,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Forgeblessed Battle Staff'),
(3180002,360055,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Rime Whisper Coin'),
(3180002,360683,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Sun King''s Twilight-forged Treads'),
(3180002,360981,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000486 | Mist Fang Bindings');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3180004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3180004,200223,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Battlemage''s Vengeful Breastplate'),
(3180004,220197,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Warmaster Greatcloak of Runekeeper'),
(3180004,240071,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Wristguards of the Coldarra'),
(3180004,260702,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Frostveined Choker'),
(3180004,280617,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Stonecarved Hammer of Howling Fjord'),
(3180004,280868,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Boar Quarrel Circlet'),
(3180004,320127,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Legguards of the Netherstorm'),
(3180004,320266,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Frostscarred Maul of Storm Queen'),
(3180004,340118,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Sanctified Cuffs of Wild Hunt'),
(3180004,340717,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000488 | Rune-etched Orb of Iron March');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3180007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3180007,200203,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Collar of Sun Crown'),
(3180007,200445,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Deathknight''s Visor'),
(3180007,200553,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Amulet, Dawn Shadow'),
(3180007,220029,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Breastplate of the Forgotten Memory'),
(3180007,220275,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Emerald Wind Neckguard'),
(3180007,220363,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | The Dire Grand Warhammer'),
(3180007,220535,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Soulcaller''s Warhelm of the Astral Crown'),
(3180007,240058,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | The Draconic Legguards'),
(3180007,240072,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Ironclad Hoop of Drowned Hall'),
(3180007,240721,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Rune-etched Mail'),
(3180007,260047,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Aged Clutches'),
(3180007,260076,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Soulcaller''s Titanic Wristguards'),
(3180007,260177,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Arcane Brand Shoulderpads'),
(3180007,260481,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Mantle of the Frost Giant'),
(3180007,280148,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Epaulets of the Ebon Watch'),
(3180007,280272,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Arcane Gloves of the Gilded Crown'),
(3180007,280735,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Gloves of the Great Forge'),
(3180007,320246,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Bleak String Chestguard'),
(3180007,320625,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Darkwarden''s Wyrmcarved Spellstaff'),
(3180007,320751,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Doomed Harness of Hallowed Watch'),
(3180007,320911,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Ravenwarden''s Legmail of the Grim Crown'),
(3180007,340207,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Walking Staff of Fallen Watch'),
(3180007,340367,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Cuffs, Dire Cleaver'),
(3180007,340533,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Blackened Channeling Rod of Bone Crown'),
(3180007,360081,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Kilt of the Winter Watch'),
(3180007,380136,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Lost Knight''s Bracers'),
(3180007,380414,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Dirk of Wildheart'),
(3180007,380586,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Everfrost Shoulderguards of Shadow Forge'),
(3180007,380915,0,0,0,1,1,1,1,'Generated map_109_difficulty_0 boss_000493 | Flame Quarrel Gloves');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8580 AND `Item` = 2010000179 AND `Reference` = 3180000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8580,2010000179,3180000,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | boss_000485');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5226 AND `Item` = 2010000180 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5226,2010000180,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5228 AND `Item` = 2010000181 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5228,2010000181,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5256 AND `Item` = 2010000182 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5256,2010000182,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5259 AND `Item` = 2010000183 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5259,2010000183,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5263 AND `Item` = 2010000184 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5263,2010000184,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5267 AND `Item` = 2010000185 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5267,2010000185,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5269 AND `Item` = 2010000186 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5269,2010000186,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5270 AND `Item` = 2010000187 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5270,2010000187,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5271 AND `Item` = 2010000188 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5271,2010000188,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5273 AND `Item` = 2010000189 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5273,2010000189,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5277 AND `Item` = 2010000190 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5277,2010000190,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5280 AND `Item` = 2010000191 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5280,2010000191,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5283 AND `Item` = 2010000192 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5283,2010000192,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5291 AND `Item` = 2010000193 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5291,2010000193,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5708 AND `Item` = 2010000194 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5708,2010000194,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5711 AND `Item` = 2010000195 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5711,2010000195,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5712 AND `Item` = 2010000196 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5712,2010000196,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5713 AND `Item` = 2010000197 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5713,2010000197,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5714 AND `Item` = 2010000198 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5714,2010000198,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5715 AND `Item` = 2010000199 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5715,2010000199,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5716 AND `Item` = 2010000200 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5716,2010000200,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5717 AND `Item` = 2010000201 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5717,2010000201,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8319 AND `Item` = 2010000202 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8319,2010000202,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8384 AND `Item` = 2010000203 AND `Reference` = 3180001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8384,2010000203,3180001,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5721 AND `Item` = 2010000204 AND `Reference` = 3180002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5721,2010000204,3180002,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | boss_000486');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5710 AND `Item` = 2010000205 AND `Reference` = 3180004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5710,2010000205,3180004,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | boss_000488');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5709 AND `Item` = 2010000206 AND `Reference` = 3180007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5709,2010000206,3180007,2,0,1,0,1,1,'Generated encounter attachment | map_109_difficulty_0 | boss_000493');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3190000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3190000,260060,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000435 | The Thornbound Coil'),
(3190000,320032,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000435 | Stonehewn Boots');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3190001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3190001,200013,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Bloodstained Titanblade'),
(3190001,200048,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Runic Greataxe, Starfang Stone'),
(3190001,200153,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bloodcaller''s Casque of the Netherstorm'),
(3190001,200174,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Mountainborn Hauberk of Shadow Vault'),
(3190001,200201,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Pavise of the Wyrm Forge'),
(3190001,200316,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Tombkeeper''s Cryptborn Wargrips'),
(3190001,200325,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Astral Mist Warhelm'),
(3190001,200411,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Lost Keeper''s Snowy Headguard'),
(3190001,200440,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | South Rider Faceguard'),
(3190001,200487,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Barbed Chainmail of the Last King'),
(3190001,200582,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Warhelm of the Midnight Watch'),
(3190001,200592,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Belt, Mana Rime'),
(3190001,200596,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Earthen Hauberk'),
(3190001,200660,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Handguards, Starfang Reach'),
(3190001,200748,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Worldwarden''s Radiant Gorget'),
(3190001,200803,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Argent Morningstar'),
(3190001,200854,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Serrated Armguards of Conquest Hold'),
(3190001,200903,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Shadow Freeze Grips'),
(3190001,200912,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Pendant, Sacred Ash'),
(3190001,200930,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Burial Shawl'),
(3190001,200943,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Steelbound Wargrips, Duskcaller''s Oath'),
(3190001,200976,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Stormwrought Promise of the Sky Watch'),
(3190001,200981,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Siegebound Legguards'),
(3190001,220016,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Aged War Leggings of the Dread Wyrm'),
(3190001,220025,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Hauberk of Violet Star'),
(3190001,220171,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Raider Greataxe of the Warsong Clan'),
(3190001,220200,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Starbound Horn of the Thunder King'),
(3190001,220213,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Dwarven Casque'),
(3190001,220264,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Hollow Blood Oathring'),
(3190001,220298,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Hollow Greatsword'),
(3190001,220320,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Jagged Wristguards'),
(3190001,220353,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Relicbound Charm of the Lost Promise'),
(3190001,220602,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Gauntlets of the Damned Host'),
(3190001,220741,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Whispering Gauntlets of Fallen King'),
(3190001,220798,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Footguards of the Broken Promise'),
(3190001,220838,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Moonsteel Signet Ring of the Endless Path'),
(3190001,220991,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Scalebound Warboots'),
(3190001,240004,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bone Veil Footguards'),
(3190001,240037,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Deepforged Trousers of Paladin Oath'),
(3190001,240053,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Claws, Silver Carver'),
(3190001,240087,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Darksteel Wargrips'),
(3190001,240108,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Earth Plate Signet'),
(3190001,240206,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Scourge Pact Shoulderguards'),
(3190001,240209,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Girdle, Demon Rebuke'),
(3190001,240236,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Silent Warden''s Clutches'),
(3190001,240241,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Falchion of the Soul Crown'),
(3190001,240431,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Last Warden''s Vial of the Frozen Pact'),
(3190001,240446,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Tempered Treads of Broken Promise'),
(3190001,240483,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Chilled Insignia'),
(3190001,240504,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Lens of the Cold Flame'),
(3190001,240547,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Spellbinder''s Strap of the Violet Star'),
(3190001,240553,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Furious Shoulderguards'),
(3190001,240559,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Seal of Shadow Crown'),
(3190001,240751,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Spiritkeeper''s Harness of the High Citadel'),
(3190001,240762,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Helm of Nagrand'),
(3190001,240817,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Cerulean Grips of Sacred Watch'),
(3190001,240865,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Tunic of Dead Watch'),
(3190001,260031,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Shield Lord Charmstone'),
(3190001,260142,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Grim Warden''s Brooch'),
(3190001,260150,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Ironkeeper''s Eye of the Twilight Crown'),
(3190001,260172,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Sun Queen''s Titan-carved Trousers'),
(3190001,260173,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bloodmarked Assassin Blade of Dark Ritual'),
(3190001,260181,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Coldforged Waistguard'),
(3190001,260198,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Stonekeeper''s Vest of the Twilight Reach'),
(3190001,260204,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Kingskeeper''s Dread Royal Band'),
(3190001,260273,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Violet Capelet, Wildkeeper''s Oath'),
(3190001,260328,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Duskcaller''s Chestguard of the Raven Queen'),
(3190001,260345,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Veil, Fel Torment'),
(3190001,260369,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Cinch of Warsong Hold'),
(3190001,260435,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Stormmarked Deathmask'),
(3190001,260470,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bearhide Deathmask, Stonekeeper''s Oath'),
(3190001,260482,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Sun Queen''s Charmstone'),
(3190001,260513,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Beastmarked Mask of the Stone Giant'),
(3190001,260540,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Darkcaller''s Headdress of the Silver Hand'),
(3190001,260650,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bloodstained Mantle of the Frozen Crown'),
(3190001,260666,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Northborn Shoulderguards of Gundrak Temple'),
(3190001,260774,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Claws, Gold Helm'),
(3190001,260904,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Hoarfrost Headdress of Deep Vault'),
(3190001,280031,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Skirt, Nightfang Ash'),
(3190001,280068,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Boots, Thorn Rend'),
(3190001,280102,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Chestwrap, Hidden Wind'),
(3190001,280116,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Deathforged Cape'),
(3190001,280166,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Grimkeeper''s Grips'),
(3190001,280185,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Mystic Reaver Crusher'),
(3190001,280205,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Regalia of the Red Flight'),
(3190001,280212,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Mist Night Headdress'),
(3190001,280239,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Ravenlord''s Soulbound Mantle'),
(3190001,280248,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Runebands, Unholy Winter'),
(3190001,280267,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Furious Vest of the Azjol Nerub'),
(3190001,280274,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Talisman, High Twilight'),
(3190001,280305,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bloodmarked Cap'),
(3190001,280335,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Silversteel Walkers'),
(3190001,280364,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Mantle, Lionheart Wyrm'),
(3190001,280369,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Witchforged Torque, Drakekeeper''s Oath'),
(3190001,280404,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Totem of Burning Steppes'),
(3190001,280505,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bone Wand of the Shadow Forge'),
(3190001,280579,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Silver King''s Fierce Kilt'),
(3190001,280626,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Branch of the Ashen Pact'),
(3190001,280640,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Torc of Dead Watch'),
(3190001,280703,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Silver King''s Boots'),
(3190001,280708,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Legwraps of the Titan Forge'),
(3190001,280717,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Forgotten Keeper''s Breeches'),
(3190001,280786,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Frozen Skullcap'),
(3190001,280869,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Prayerbound Cap'),
(3190001,280923,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Cuffs of the Ice Queen'),
(3190001,280955,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Waistwrap, Stone Spark'),
(3190001,280984,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Blighted Talisman'),
(3190001,280995,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Diadem of the Nightwatch'),
(3190001,320034,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Scalebound Mask of Dragonblight'),
(3190001,320050,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Charm, Sky Hail'),
(3190001,320116,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Spaulders of the Forgotten Memory'),
(3190001,320131,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Mask of the Iron Banner'),
(3190001,320148,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bloodfire Shine Spirit Staff'),
(3190001,320171,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Runering of Wind Spirit'),
(3190001,320180,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Cinch of Sun Crown'),
(3190001,320231,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Plaguekeeper''s Cap'),
(3190001,320272,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Shadowmarked Treads of Ancient Memory'),
(3190001,320319,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Ashkeeper''s Neckguard of the Blood Pact'),
(3190001,320330,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Night Ruin Legguards'),
(3190001,320365,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Ancient King''s Breeches'),
(3190001,320384,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Witchforged Warband'),
(3190001,320487,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Twilight Glyph Claws'),
(3190001,320570,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Thorn Verse Waistband'),
(3190001,320584,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Shoulderguards of the Soul Watch'),
(3190001,320649,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Briarwoven Treads of the Dragon Oath'),
(3190001,320678,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Ancestral Wristbands'),
(3190001,320692,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Sinister Headguard of Bronze Dragon'),
(3190001,320697,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Iron Mace of Scale Queen'),
(3190001,320706,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Titanforged Cinch of Violet Crown'),
(3190001,320719,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Crusader Seal of the Silent Crown'),
(3190001,320898,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Earthcaller''s Fearsome Legwraps'),
(3190001,340046,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Warmaster Leggings'),
(3190001,340053,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Hateful Neckguard of the Endless Night'),
(3190001,340128,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Circle of Drak Tharon Keep'),
(3190001,340144,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Doom Rebuke Headdress'),
(3190001,340164,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Warwarden''s Armbands of the Star Crown'),
(3190001,340232,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Thorned Skirt of the Shattered Gate'),
(3190001,340276,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Spell Wolf Skull'),
(3190001,340281,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Warden''s Dread Vest'),
(3190001,340308,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Rangemaster''s Trousers of the Fire Spirit'),
(3190001,340311,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Sacred Breeches'),
(3190001,340335,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Vest, Death Storm'),
(3190001,340390,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Battlemage''s Epaulets of the Hearthguard'),
(3190001,340479,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Forgekeeper''s Earthen-forged Slasher'),
(3190001,340492,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Mystic Chestwrap of Warsong Hold'),
(3190001,340619,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Spiritbound Leggings'),
(3190001,340687,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Ghost Brand Waistwrap'),
(3190001,340706,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Crusader''s Warcloak'),
(3190001,340868,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Greatstaff of the Ancient Watcher'),
(3190001,340902,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Kilt of Ebon Watch'),
(3190001,340937,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Dragoncaller''s Skirt'),
(3190001,340971,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Windlord''s Wrap of the Crimson Banner'),
(3190001,340981,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Razor-edged Band of the Blighted Land'),
(3190001,340987,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Cinch, Wildfire Fate'),
(3190001,360049,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Stargazer''s Pale Skirt'),
(3190001,360085,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Kingsguard''s Leggings'),
(3190001,360139,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Cabalistic Waistband of the Stone Forge'),
(3190001,360176,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Neckchain, Arcane Echo'),
(3190001,360206,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Eternal Binding'),
(3190001,360241,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Spiritforged Walkers of Void Flame'),
(3190001,360252,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Forgotten Vine Footwraps'),
(3190001,360277,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Hateful Runering'),
(3190001,360338,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Corrupted Tiara'),
(3190001,360386,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | North Grasp Seal Ring'),
(3190001,360434,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bloodwarden''s Moonlit Cap'),
(3190001,360461,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Bitter Sandals of Broken Gate'),
(3190001,360474,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Dreaming Graspers'),
(3190001,360535,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Stormcaller''s Collar'),
(3190001,360606,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Arcanist''s Deathforged Breeches'),
(3190001,360664,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Spell Stave of K3'),
(3190001,360670,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Pale-blue Trousers'),
(3190001,360689,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Sunhallowed Robes of the Soul Watch'),
(3190001,360693,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Handwraps of the Ironforge Mountain'),
(3190001,360715,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Ashen Shoulderwraps'),
(3190001,360742,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Grips of the Star Watch'),
(3190001,360802,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Treads of Winter King'),
(3190001,360866,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Blessed Torque'),
(3190001,360895,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Shoulder Cape of the Searing Gorge'),
(3190001,360942,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Sun King''s Charm'),
(3190001,360943,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Nightwatcher''s Royal Cloak'),
(3190001,360948,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Cap, Rune Strike'),
(3190001,360975,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Storm Queen''s Tunic'),
(3190001,380056,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Ashcaller''s Striders'),
(3190001,380082,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Embercaller''s Helm of the Frenzyheart Hill'),
(3190001,380126,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Blessed Wristguards of Final March'),
(3190001,380138,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Dreamwoven Gloves of the Unquiet Dead'),
(3190001,380147,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Nightkeeper''s Spaulders of the Fire Spirit'),
(3190001,380169,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Shoulder Drape of the Dead King'),
(3190001,380175,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Claws of the North Road'),
(3190001,380323,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | The Stonehewn Tunic'),
(3190001,380337,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Lost Queen''s Blackened Boots'),
(3190001,380361,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Dawnkeeper''s Gravebound Helm'),
(3190001,380377,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Tablet of the Moon Grove'),
(3190001,380446,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Chestpiece of Broken Blade'),
(3190001,380507,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Death Arrow Waistband'),
(3190001,380631,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Colossal Gloves of the Altar of Sseratus'),
(3190001,380681,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Band of the Azure Flame'),
(3190001,380841,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Merciless Jerkin of the Moon Pact'),
(3190001,380862,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 trash | Wintertouched Mantle of the Wyrm Queen');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3190002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3190002,200162,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Warboots, Long Ripper'),
(3190002,200181,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Ghostcaller''s Warcloak of the Dread March'),
(3190002,220837,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Runering, Death Freeze'),
(3190002,240059,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Winter King''s Walkers'),
(3190002,240429,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Forgekeeper''s Hallowed Mask'),
(3190002,240587,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Warborn Legwraps of the Ancient Earth'),
(3190002,260221,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Ravenkeeper''s Sorcerous Wargrips'),
(3190002,320077,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Rimelord''s Blazing Cinch'),
(3190002,320201,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | The Silverforged Legwraps'),
(3190002,320430,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Signet Ring of Sacred Dawn'),
(3190002,340561,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Shortsword, Bright Ray'),
(3190002,340574,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Blacksmith''s Fireforged Waistwrap'),
(3190002,340664,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | The Dreamwoven Fingerband'),
(3190002,360383,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | The Jeweled Shoulder Cape'),
(3190002,360813,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Thunderwarden''s Cord'),
(3190002,380582,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Quarterstaff of Crimson Banner'),
(3190002,380639,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000436 | Prayerbound Boots of Ancient Grove');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3190003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3190003,200134,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Silverforged Harness'),
(3190003,200285,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Razor-edged Footplates'),
(3190003,200471,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Ironwarden''s Handguards'),
(3190003,200481,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Gleaming Warboots of Death Gate'),
(3190003,200486,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Dreaming Locket'),
(3190003,200547,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Astral Belt of Gundrak'),
(3190003,200603,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Prayerbound Belt'),
(3190003,200621,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Worldforged Hauberk of Frozen Road'),
(3190003,200872,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Illusory Hauberk'),
(3190003,200892,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Titanforger''s Earthen-forged Pendant Chain'),
(3190003,220141,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Dawn Grave Greaves'),
(3190003,220204,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Casque of Moonwell'),
(3190003,220318,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Wargrips, Bear Whisper'),
(3190003,220326,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Steelbound Warboots of the Frozen Gate'),
(3190003,220425,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Mournbound Ward'),
(3190003,220490,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Wildbound Greatcloak'),
(3190003,220663,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Iron Creed Chainmail'),
(3190003,220755,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Wargrips of the Earthen Watch'),
(3190003,220824,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Saronite Legmail of the Wyrm Crown'),
(3190003,220870,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Bloodfire Ice Battleaxe'),
(3190003,220873,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Dragon King''s Charm'),
(3190003,220874,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Handguards of the Storm Watch'),
(3190003,220941,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Hallowed Winter Runesword'),
(3190003,240005,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Earthforged Skull'),
(3190003,240115,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Mantle of Argent Vanguard'),
(3190003,240199,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Doomed Mantle of the Drowned King'),
(3190003,240281,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Deathknight''s Shoulderwraps'),
(3190003,240398,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | War Cleaver of the Stormcaller'),
(3190003,240528,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Unhallowed Shoulderpads'),
(3190003,240564,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Warboots of Frozen Road'),
(3190003,240565,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Hammer Freeze Warboots'),
(3190003,240761,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Ebon Fingerband'),
(3190003,260118,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Shoulder Drape of the Eagle Spirit'),
(3190003,260292,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Warband of the North Road'),
(3190003,260319,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Deepwarden''s Silverforged Clutches'),
(3190003,260581,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Thunderkeeper''s Hammer of the Bone Ritual'),
(3190003,260679,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Eagle Forge Seal'),
(3190003,260755,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Skull Vigil Armguards'),
(3190003,260812,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Chestguard of the Burning Star'),
(3190003,260882,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Vengeful Claws of Crimson Flame'),
(3190003,260934,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Nightwoven Chestguard'),
(3190003,280041,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Bleak Cord'),
(3190003,280070,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Firewarden''s Soldierly Cuffs'),
(3190003,280249,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Icetouched Sandals of Silver Flame'),
(3190003,280259,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Primeval Leggings'),
(3190003,280368,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Mantle, North Mark'),
(3190003,280405,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Heavy Cloak'),
(3190003,280426,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Nightshrouded Cinch of the Freya Garden'),
(3190003,280443,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Forgotten King''s Gloves'),
(3190003,280488,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Bonekeeper''s Ancestral Graspers'),
(3190003,280566,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Clawmarked Warder Cloak'),
(3190003,280826,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Iceforged Headdress'),
(3190003,320245,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Chestguard of the Icecrown'),
(3190003,320279,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Twilightwarden''s Northforged Treads'),
(3190003,320331,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Spellscarred Footguards'),
(3190003,320345,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Mantle of the Ebon Crown'),
(3190003,320404,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Soulmarked Pants of Mystic Eye'),
(3190003,320554,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Legguards, Icefang Piercer'),
(3190003,320623,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Gloves of the Searing Gorge'),
(3190003,320707,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Claws of the Halls of Reflection'),
(3190003,320712,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Griefbound Icon'),
(3190003,340065,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Timeworn Promise'),
(3190003,340208,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Treads of Last Vigil'),
(3190003,340291,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Stoic Skirt of Stratholme'),
(3190003,340350,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Thunderforged Shoulderpads'),
(3190003,340452,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Grimlord''s Baleful Traveling Cloak'),
(3190003,340494,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Blood Fate Longcloak'),
(3190003,340624,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Nightwoven Armbands of Void Watch'),
(3190003,340845,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Binding of the Kings Road'),
(3190003,340857,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Binding, Moon Scar'),
(3190003,340861,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Hollow Legwraps'),
(3190003,340886,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Ironclad Mantle of Violet Citadel'),
(3190003,360024,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Quarterstaff, Moonfire Maw'),
(3190003,360077,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | The Runesteel Shoulderpads'),
(3190003,360161,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Coldhearted Gloves of the Utgarde Pinnacle'),
(3190003,360248,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Nightkeeper''s Greenwood Waistwrap'),
(3190003,360260,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Pendant Chain, High Seed'),
(3190003,360263,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Deathkeeper''s Runebands of the Drake Rider'),
(3190003,360500,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Forgekeeper''s Loop of the Ice Crown'),
(3190003,360534,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Blacksteel Epaulets'),
(3190003,360743,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Eternal Grips of Ebon Vanguard'),
(3190003,360843,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Gleaming Loop'),
(3190003,360950,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Ashwarden''s Seal of the Star Watch'),
(3190003,360956,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Grim Stone Breeches'),
(3190003,380047,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Spear of Frozen King'),
(3190003,380159,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Howling Waistguard of Dead March'),
(3190003,380233,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Strap, Gold Anchor'),
(3190003,380405,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Forgotten Queen''s Armguards'),
(3190003,380530,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Cap of the Moon Watch'),
(3190003,380663,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Clutches, Storm Glacier'),
(3190003,380727,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Drakekeeper''s Steelforged Grips'),
(3190003,380826,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Blood Breath Shroud'),
(3190003,380827,0,0,0,1,1,1,1,'Generated map_129_difficulty_0 boss_000437 | Ironkeeper''s Ivory Necklace');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7357 AND `Item` = 2010000207 AND `Reference` = 3190000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7357,2010000207,3190000,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | boss_000435');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7327 AND `Item` = 2010000208 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7327,2010000208,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7328 AND `Item` = 2010000209 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7328,2010000209,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7329 AND `Item` = 2010000210 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7329,2010000210,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7332 AND `Item` = 2010000211 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7332,2010000211,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7335 AND `Item` = 2010000212 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7335,2010000212,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7337 AND `Item` = 2010000213 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7337,2010000213,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7341 AND `Item` = 2010000214 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7341,2010000214,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7342 AND `Item` = 2010000215 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7342,2010000215,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7345 AND `Item` = 2010000216 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7345,2010000216,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7347 AND `Item` = 2010000217 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7347,2010000217,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7348 AND `Item` = 2010000218 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7348,2010000218,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7352 AND `Item` = 2010000219 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7352,2010000219,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7353 AND `Item` = 2010000220 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7353,2010000220,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7354 AND `Item` = 2010000221 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7354,2010000221,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14686 AND `Item` = 2010000222 AND `Reference` = 3190001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14686,2010000222,3190001,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8567 AND `Item` = 2010000223 AND `Reference` = 3190002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8567,2010000223,3190002,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | boss_000436');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7358 AND `Item` = 2010000224 AND `Reference` = 3190003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7358,2010000224,3190003,2,0,1,0,1,1,'Generated encounter attachment | map_129_difficulty_0 | boss_000437');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200000,200230,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000444 | Shoulderguards of Moon Flame'),
(3200000,200617,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000444 | Starlit Hauberk of Eternal Flame'),
(3200000,240433,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000444 | Silvered Vest'),
(3200000,280670,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000444 | Goldbound Seal, Moon King''s Oath'),
(3200000,280932,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000444 | The Dragonhide Skullcap'),
(3200000,340081,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000444 | Kingskeeper''s Vestments');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200001,200019,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Handguards, Sunfire Reach'),
(3200001,200157,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Leafbound Waistchain'),
(3200001,200234,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Snowbound Chain of the Borean Tundra'),
(3200001,200287,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Coif, Mist Wound'),
(3200001,200336,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Deathbound Shoulder Guards'),
(3200001,200344,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Ebon Crusader''s Living Mantle'),
(3200001,200556,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Dragonstalker''s Armguards'),
(3200001,200615,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Fel Lens of the Violet Crown'),
(3200001,200711,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Dustbound Treads of Pale Moon'),
(3200001,200820,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Ice Witch''s Murderous Shoulder Guards'),
(3200001,200823,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Kingskeeper''s Conqueror Waistguard'),
(3200001,220054,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | First Queen''s Colossal Grips'),
(3200001,220151,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Pale Wallshield'),
(3200001,220194,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Frostforged Raider Axe, Soulkeeper''s Oath'),
(3200001,220268,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Wildcaller''s Warboots of the Star Crown'),
(3200001,220308,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Earth Fang Battle Greatsword'),
(3200001,220352,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Stormscarred Torc'),
(3200001,220406,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Gray Whisper Greaves'),
(3200001,220457,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Deathcaller''s Dawnforged Gloves'),
(3200001,220487,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Hammerlord''s Boneforged Belt'),
(3200001,220505,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Tarnished Gloves'),
(3200001,220545,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Shroud, White Spire'),
(3200001,220658,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Ravenous Chestguard'),
(3200001,220704,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Deathcaller''s Kingsworn Leggings'),
(3200001,220706,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Heart, Argent Hex'),
(3200001,220707,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Sunwarden''s Gauntlets of the New Agamand'),
(3200001,220854,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Shadowbound Chestguard of the Runed Path'),
(3200001,220859,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Age-darkened Gloves of Earth Spirit'),
(3200001,220878,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Brooch of Deep Hall'),
(3200001,220886,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Battlecloak of the Storm Crown'),
(3200001,220895,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Footguards of Crimson Banner'),
(3200001,220898,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Gravecaller''s Grips'),
(3200001,220908,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Executioner, Argent Guard'),
(3200001,220917,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Signet, Dark Scream'),
(3200001,240116,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Beads, Serpent Shine'),
(3200001,240193,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Lightbound Jerkin'),
(3200001,240195,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Bloodknight''s Cowl'),
(3200001,240225,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Pitiless Waistband'),
(3200001,240264,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Ravenlord''s Claws of the Argent Vanguard'),
(3200001,240283,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Soldierly Jerkin, Argent Marshal''s Oath'),
(3200001,240319,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Sun Root Leggings'),
(3200001,240337,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Gravewarden''s Chestpiece'),
(3200001,240405,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Starlit Neckchain of the Rune King'),
(3200001,240427,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Aged Warblade'),
(3200001,240469,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Thunderforged Wargrips'),
(3200001,240500,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Chestguard of the Great Hunt'),
(3200001,240517,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Chillborn Bracers'),
(3200001,240520,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Dustbound Leggings of the Frozen Sea'),
(3200001,240668,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Headguard of the Grizzly Hills'),
(3200001,240747,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Adamant Siege Crossbow, Witchkeeper''s Oath'),
(3200001,240870,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Traveling Cloak of the Sky Watch'),
(3200001,240894,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Razor-edged Jerkin of Lost Watch'),
(3200001,240908,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Lost Keeper''s Mask of the Dread March'),
(3200001,240956,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Voidwarden''s Faded Clutches'),
(3200001,240967,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Legwraps, Shield Echo'),
(3200001,240975,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Wayfarer''s Promise'),
(3200001,240989,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Sunfire Bringerless Belt'),
(3200001,260209,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Spiritcaller''s Chain'),
(3200001,260430,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Winter King''s Scalebound Legguards'),
(3200001,260443,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Frostworn Gloves'),
(3200001,260594,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Holy Neckguard of Fallen Crown'),
(3200001,260607,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Icekeeper''s Bindings of the Autumn Wind'),
(3200001,260717,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Kingsworn Shanker'),
(3200001,260739,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Deathwarden''s Vest'),
(3200001,260837,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Signet, Wolf Quarrel'),
(3200001,260876,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Wargrips, Storm Bolt'),
(3200001,260992,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Ghostkeeper''s Fierce Headguard'),
(3200001,280023,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Dragon Queen''s Scale-bound Wristwraps'),
(3200001,280100,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Primal Shroud'),
(3200001,280115,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Seer Staff, Celestial Shade'),
(3200001,280188,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Forgotten King''s Breeches'),
(3200001,280213,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Conduit of the Borean Tundra'),
(3200001,280234,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Rangemaster''s Footwraps of the Violet Hold'),
(3200001,280287,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Wyrmkeeper''s Cord'),
(3200001,280492,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Armbands, Starfang Blood'),
(3200001,280502,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Sunforged Handwraps'),
(3200001,280543,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Runewarden''s Warder Cloak'),
(3200001,280734,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Titanguard''s Ringlet'),
(3200001,280761,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Bloodcaller''s Cloak of the Emerald Dream'),
(3200001,280855,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Bonebound Circlet'),
(3200001,280864,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Forgeblessed Waistband'),
(3200001,280957,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Drakescale Breeches'),
(3200001,280973,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Verdant Epaulets'),
(3200001,280990,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Deep Shine Waistwrap'),
(3200001,320058,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Brittle Carapace'),
(3200001,320205,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Pale Lady''s Dragonhide Boots'),
(3200001,320268,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Vrykul Mark'),
(3200001,320357,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Silverkeeper''s Dawnforged Battle Claw'),
(3200001,320499,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Runewarden''s Tunic'),
(3200001,320551,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Heavenforged Headguard, Highborn''s Oath'),
(3200001,320559,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Bindings of Yogg Prison'),
(3200001,320574,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Dreadbound Bearded Axe, Gravewarden''s Oath'),
(3200001,320727,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Striders of Bear Spirit'),
(3200001,320775,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Steadfast Footguards of the Abyssal Flame'),
(3200001,320840,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Rootwoven Boots'),
(3200001,320903,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Deepwarden''s Cinch of the Ivory Crown'),
(3200001,340024,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Great Stave of the Black Citadel'),
(3200001,340135,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Cryptlord''s Mantle of the Frozen Heart'),
(3200001,340192,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Lightwarden''s Dreamwoven Kilt'),
(3200001,340255,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Warpriest''s Kris'),
(3200001,340285,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Torc of the Endless Vigil'),
(3200001,340297,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Sun Oath Armbands'),
(3200001,340300,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Warrior-forged Hoop, Tombkeeper''s Oath'),
(3200001,340325,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Enchanted Waistband of Black Flight'),
(3200001,340339,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Blade Ripper Shawl'),
(3200001,340354,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Bronze Spear Graspers'),
(3200001,340431,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Deepforged Treads of the Freya Garden'),
(3200001,340526,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Wand, Oath Heart'),
(3200001,340537,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Divine Chestwrap of the Titan Archive'),
(3200001,340553,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Grimdark Chestwrap, Lost Warden''s Oath'),
(3200001,340596,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Battleworn Waistwrap'),
(3200001,340603,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Shadowmage''s Drakeforged Rod'),
(3200001,340618,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Beads of the Ebon Hold'),
(3200001,340629,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Vicious Shoes'),
(3200001,340651,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Dawn Hand Idol'),
(3200001,340691,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Witchlord''s Pants of the Thunder Bluff'),
(3200001,340693,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Ebon Crusader''s Armbands of the Pale Moon'),
(3200001,340704,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Runeguard''s Sash'),
(3200001,340827,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Hellforged Pants'),
(3200001,340838,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Nameless Warden''s Leafwoven Raiment'),
(3200001,340910,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Briarbound Effigy of the Frozen Pact'),
(3200001,360092,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Northborn Diadem of the Scourge March'),
(3200001,360125,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Charm of Howling Wind'),
(3200001,360133,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Locket of the Wild Grove'),
(3200001,360350,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Relicbound Robes, Warcaller''s Oath'),
(3200001,360415,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Regalia of the Ancient Grove'),
(3200001,360426,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Ivory Trousers'),
(3200001,360429,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Bloodwarden''s Gloves of the Light Crown'),
(3200001,360568,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Eternal Shoulder Cape of the Golden Flame'),
(3200001,360649,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Cord of Amberpine Lodge'),
(3200001,360699,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Astral Ruin Epaulets'),
(3200001,360774,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Moonlit Footwraps'),
(3200001,360879,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Old Warden''s Regalia'),
(3200001,360951,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Vest of the Hellfire Citadel'),
(3200001,380021,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Corpsebound Cowl'),
(3200001,380070,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Wristbands, Voidshard Grip'),
(3200001,380129,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Highlord''s Trousers'),
(3200001,380130,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Warcloak of the Star Caller'),
(3200001,380227,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Clutches, Titan Seal'),
(3200001,380243,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Northwarden''s Waistband of the Fallen King'),
(3200001,380271,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Seal Ring of the Holy Guard'),
(3200001,380364,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Waistguard, Rime Shield'),
(3200001,380566,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Faded Cap of Deep Anvil'),
(3200001,380602,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Titanbound Deathmask of the Bone Wastes'),
(3200001,380640,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Bloodkeeper''s Nightbound Chestpiece'),
(3200001,380683,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Shadow King''s Frost-rimed Harness'),
(3200001,380712,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Chestpiece of the Titan Forge'),
(3200001,380722,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Magebound Bracers'),
(3200001,380723,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Boots, Hollow Seed'),
(3200001,380725,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | The Dragonbound Shoulder Drape'),
(3200001,380799,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Cap of the Light Crown'),
(3200001,380910,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 trash | Warborn Ring of the Scourge Watch');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200002,240237,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000445 | Rotting Strap'),
(3200002,280117,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000445 | The Bonebound Tunic'),
(3200002,280817,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000445 | Frostbound Greatstaff of the Ice Moon'),
(3200002,380008,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000445 | The Profane Handguards'),
(3200002,380122,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000445 | Mantle of Makers Will');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200003,200263,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Chausses of Stone Watch'),
(3200003,200300,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Legguards of Star Crown'),
(3200003,200468,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Bear Verse Helm'),
(3200003,200488,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Icetouched Spaulders of the Black Flight'),
(3200003,200551,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Coldfire Seal Helm'),
(3200003,200856,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Bracers of the Ebon Watch'),
(3200003,220035,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Ironclad Torc of Silver Flame'),
(3200003,220153,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Surcoat, Grey Sigil'),
(3200003,220467,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Emberforged Legguards of the Grim Crown'),
(3200003,220525,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Blood Whisper Battlecloak'),
(3200003,220673,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Titanbound Chausses of the Lordaeron Guard'),
(3200003,220686,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Shoulder Guards, Fallen Hammer'),
(3200003,220799,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dread Charm of Moonwarden'),
(3200003,240122,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Stormscarred Legwraps of Dawn Star'),
(3200003,240220,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Jerkin, Prime Lament'),
(3200003,240234,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Collar of the Last Watch'),
(3200003,240315,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Living Neckguard'),
(3200003,240566,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Handguards of Broken Banner'),
(3200003,240609,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Carapace of the Temple of Storms'),
(3200003,240719,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dream Spire Drape'),
(3200003,260152,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Steadfast Legwraps of the Blood Oath'),
(3200003,260473,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Moon King''s Hoop of the Divine Watch'),
(3200003,260642,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Stoneguard''s Carapace'),
(3200003,260734,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Deathmarked Shoulderguards'),
(3200003,260736,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Argent Rune Tunic'),
(3200003,260825,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dragonwarden''s Girdle'),
(3200003,280098,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Shattered Cap of Scarlet Monastery'),
(3200003,280240,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Illusory Kilt of Arcane Watch'),
(3200003,280409,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Seal Ring, Pale Gaze'),
(3200003,280461,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Fernwoven Leggings'),
(3200003,280475,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Bonecaller''s Tunic of the Second Dawn'),
(3200003,280479,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Tempered Mitts of Cold Memory'),
(3200003,280618,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Kilt, Wild Singer'),
(3200003,320014,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Traveling Cloak of the Dread Host'),
(3200003,320188,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Twilightcaller''s Boneclad Charmstone'),
(3200003,320229,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dark Piercer Wargrips'),
(3200003,320369,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | The Moonlit Pants'),
(3200003,320479,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dragonforged Headguard'),
(3200003,320566,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Belt of the Ghost Watch'),
(3200003,320656,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | The Earthen-forged Trousers'),
(3200003,320728,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Loop of Winter King'),
(3200003,320729,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Worldforged Leggings'),
(3200003,320778,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Duskkeeper''s Walkers'),
(3200003,320962,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dragonhide Leggings of Soul Crown'),
(3200003,340155,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Tunic of the Ebon Banner'),
(3200003,340185,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Cinch of North Wind'),
(3200003,340293,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Fingerband of Ghost Moon'),
(3200003,340511,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Wyrmkeeper''s Lightbound Pendant Chain'),
(3200003,340639,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Ash Roar Skirt'),
(3200003,340661,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Nightforged Bracelets of the Wild Crown'),
(3200003,340807,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Runering, Serpent Fate'),
(3200003,340867,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Epaulets, Storm Ash'),
(3200003,360147,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Ancient King''s Raiment of the Sacred Flame'),
(3200003,360149,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Stonefather''s Stormscarred Gemmed Band'),
(3200003,360297,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | The Plagueborn Mantle'),
(3200003,360498,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Briarbound Seal'),
(3200003,360643,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Skirt, Emerald Wolf'),
(3200003,360797,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Mossbound Cuffs'),
(3200003,360997,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Shiv, Bright Strike'),
(3200003,380167,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Witchcaller''s Drape'),
(3200003,380434,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Bloodcaller''s Timeworn Mantle'),
(3200003,380459,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dragon King''s Scarlet Girdle'),
(3200003,380775,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Dreamkeeper''s Walking Staff'),
(3200003,380789,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Necrotic Strap'),
(3200003,380836,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Shoulderwraps of Moon Grove'),
(3200003,380927,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000446 | Soulcaller''s Zealous Neckchain');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200004,200921,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Winterkeeper''s Boots'),
(3200004,220367,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | West March Wargrips'),
(3200004,220378,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Traveling Cloak of Fel Watch'),
(3200004,280018,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Gloves of the Divine Watch'),
(3200004,280303,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Mage Wand of the Moon Spirit'),
(3200004,280377,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Baneful Robes'),
(3200004,280899,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Hood of the Lordaeron Guard'),
(3200004,320317,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Titanforged Harness'),
(3200004,320342,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Wyrmscale Trousers'),
(3200004,320555,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Clutches, Nightfang Slayer'),
(3200004,320588,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Fingerband of the Sunwell'),
(3200004,340992,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Frozen Cowl of the Sun Flame'),
(3200004,360054,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Hollow Breeches of the Star King'),
(3200004,360309,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Ironthane''s Footwraps'),
(3200004,360831,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Frost-rimed Shoulderpads of Storm Forge'),
(3200004,360858,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Storm Queen''s Gemmed Band'),
(3200004,380006,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Stormscarred Striders of Iron Dwarf'),
(3200004,380062,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Harness of the Altar of Sseratus'),
(3200004,380318,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Rugged Headguard'),
(3200004,380445,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Astral Spaulders of the Star Caller'),
(3200004,380954,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000447 | Stalkers of Silent King');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200005,200030,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Totem, Savage Guard'),
(3200005,200380,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Whispering Boots of Thunder Watch'),
(3200005,220630,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Ironthane Loop of the Scarlet Monastery'),
(3200005,220733,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Nightkeeper''s Greaves'),
(3200005,240160,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Drakeforged Wristbands of the Void Ritual'),
(3200005,240468,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Royal Cloak of the Iron Giant'),
(3200005,240615,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Frostlord''s Helm'),
(3200005,260674,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Hollow Mist Deathmask'),
(3200005,280006,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Brutish Shoulderwraps'),
(3200005,280383,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Skirt of Wyrm Forge'),
(3200005,280666,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Northborn Robe of the Drak Tharon Keep'),
(3200005,320160,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | The Scourgeforged Band'),
(3200005,320244,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Wolfhide Girdle'),
(3200005,320482,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Frozen Boots of the Arcane Eye'),
(3200005,320628,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Bronze Wind Coil'),
(3200005,340088,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Darkrider''s Vest of the Icecrown Citadel'),
(3200005,340881,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Battlecloak of the Deep Anvil'),
(3200005,360050,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Mantle of the Golden Dawn'),
(3200005,360069,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Binding of the Soul Crown'),
(3200005,360114,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Death Hide Hood'),
(3200005,380471,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | The Warrior-forged Treads'),
(3200005,380822,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Brightwarden''s Argent Walkers'),
(3200005,380863,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000448 | Handguards, Fire Talon');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200006,200170,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000449 | Hammerlord''s Old Legguards'),
(3200006,200509,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000449 | Warbelt of Light Watch'),
(3200006,280062,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000449 | Coldforged Royal Cloak of the Dragon Forge'),
(3200006,380109,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000449 | Mask, Skull Lament'),
(3200006,380536,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000449 | Carapace of War Watch');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3200007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3200007,200096,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Helm, Starfire Hex'),
(3200007,200470,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Legplates of the Ancient North'),
(3200007,200498,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Red Horn Greaves'),
(3200007,200540,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Violet Mage''s Bleak Wrist Chains'),
(3200007,200576,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Helm of the Ancient North'),
(3200007,200815,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Breastplate of the Ancient North'),
(3200007,200837,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Gauntlets of the Ancient North'),
(3200007,200878,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Shoulderguards of the Ancient North'),
(3200007,280123,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Treads, Soulfire Ripper'),
(3200007,320318,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Girdle of the Broken Banner'),
(3200007,320606,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Quarterstaff of Wind Watch'),
(3200007,340201,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Shoulderwraps of Iron Crown'),
(3200007,360301,0,0,0,1,1,1,1,'Generated map_189_difficulty_0 boss_000450 | Stoneforged Veil of Twilight Watch');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3983 AND `Item` = 2010000225 AND `Reference` = 3200000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3983,2010000225,3200000,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | boss_000444');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3976 AND `Item` = 2010000226 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3976,2010000226,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4283 AND `Item` = 2010000227 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4283,2010000227,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4286 AND `Item` = 2010000228 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4286,2010000228,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4287 AND `Item` = 2010000229 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4287,2010000229,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4288 AND `Item` = 2010000230 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4288,2010000230,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4289 AND `Item` = 2010000231 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4289,2010000231,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4290 AND `Item` = 2010000232 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4290,2010000232,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4291 AND `Item` = 2010000233 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4291,2010000233,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4292 AND `Item` = 2010000234 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4292,2010000234,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4293 AND `Item` = 2010000235 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4293,2010000235,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4294 AND `Item` = 2010000236 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4294,2010000236,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4295 AND `Item` = 2010000237 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4295,2010000237,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4296 AND `Item` = 2010000238 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4296,2010000238,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4297 AND `Item` = 2010000239 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4297,2010000239,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4298 AND `Item` = 2010000240 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4298,2010000240,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4299 AND `Item` = 2010000241 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4299,2010000241,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4300 AND `Item` = 2010000242 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4300,2010000242,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4301 AND `Item` = 2010000243 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4301,2010000243,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4302 AND `Item` = 2010000244 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4302,2010000244,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4303 AND `Item` = 2010000245 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4303,2010000245,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4304 AND `Item` = 2010000246 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4304,2010000246,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4306 AND `Item` = 2010000247 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4306,2010000247,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4308 AND `Item` = 2010000248 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4308,2010000248,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4540 AND `Item` = 2010000249 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4540,2010000249,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6426 AND `Item` = 2010000250 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6426,2010000250,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6427 AND `Item` = 2010000251 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6427,2010000251,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6488 AND `Item` = 2010000252 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6488,2010000252,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6489 AND `Item` = 2010000253 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6489,2010000253,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6490 AND `Item` = 2010000254 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6490,2010000254,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14693 AND `Item` = 2010000255 AND `Reference` = 3200001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14693,2010000255,3200001,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4543 AND `Item` = 2010000256 AND `Reference` = 3200002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4543,2010000256,3200002,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | boss_000445');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3974 AND `Item` = 2010000257 AND `Reference` = 3200003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3974,2010000257,3200003,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | boss_000446');

DELETE FROM `creature_loot_template` WHERE `Entry` = 6487 AND `Item` = 2010000258 AND `Reference` = 3200004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(6487,2010000258,3200004,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | boss_000447');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3975 AND `Item` = 2010000259 AND `Reference` = 3200005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3975,2010000259,3200005,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | boss_000448');

DELETE FROM `creature_loot_template` WHERE `Entry` = 4542 AND `Item` = 2010000260 AND `Reference` = 3200006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4542,2010000260,3200006,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | boss_000449');

DELETE FROM `creature_loot_template` WHERE `Entry` = 3977 AND `Item` = 2010000261 AND `Reference` = 3200007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3977,2010000261,3200007,2,0,1,0,1,1,'Generated encounter attachment | map_189_difficulty_0 | boss_000450');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3210000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3210000,200591,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Ghostwarden''s Sabatons of the Sun Crown'),
(3210000,200762,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Northguard''s Armplates'),
(3210000,200822,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Zweihander of the Forgotten Road'),
(3210000,200835,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Forge Keeper Battleplate Legguards'),
(3210000,200955,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Great Warblade of the Last Promise'),
(3210000,220164,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Forgotten War Cleaver'),
(3210000,220284,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Ebon Chain of Dawnwatch'),
(3210000,220397,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Jeweled Backcloth of the Frozen Gate'),
(3210000,220413,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Greathelm of Dark Star'),
(3210000,220449,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | The Bright Armplates'),
(3210000,220460,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | The Soulforged Battleplate Legguards'),
(3210000,220478,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Mountainborn Loop of the Blue Flight'),
(3210000,220624,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Sunsteel Carapace of the Runed Path'),
(3210000,220735,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Ebon Knight''s Shadowwoven Vambraces'),
(3210000,220738,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | The Icy Greatcloak'),
(3210000,220968,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Rimeforged Medallion of Bronze Flight'),
(3210000,220969,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Stoic Great Pauldrons of the Gundrak'),
(3210000,240045,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Chainmail of Dalaran'),
(3210000,240161,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Cape, Storm Grip'),
(3210000,240297,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Execution Axe of Iron Banner'),
(3210000,240338,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Bloodguard''s War Crossbow'),
(3210000,240376,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Frostmage''s Gauntlets of the Golden Moon'),
(3210000,240443,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Grimdark Gloves of Moon Spirit'),
(3210000,240533,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Tombkeeper''s Gladiatorial Longcloak'),
(3210000,240611,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Wind Leaf Kingsblade'),
(3210000,240787,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Voidlord''s Leggings'),
(3210000,240827,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | The Briarwoven Coif'),
(3210000,240919,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Skullkeeper''s Headguard'),
(3210000,240950,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Tempered Capelet of the Endless March'),
(3210000,260009,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | The Corrupted Walkers'),
(3210000,260251,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Vrykul Stalkers, Forgotten Warden''s Oath'),
(3210000,260275,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Beads of the Silver Pact'),
(3210000,260404,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Lightlord''s Cinch'),
(3210000,260449,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Starwoven Spellknife of Ghost King'),
(3210000,260860,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Celestial Steel Crossbow'),
(3210000,260939,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Shard of Bronze Dragon'),
(3210000,280074,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Dreamwarden''s Shoulder Drape'),
(3210000,280105,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Savage Reach Warstaff'),
(3210000,280107,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Sash, Star Ritual'),
(3210000,280145,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | The Thorned Waistband'),
(3210000,280169,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Ferocious Graspers of Winter Court'),
(3210000,280170,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Skull of the Star Grove'),
(3210000,280430,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Blood King''s Golden Robes'),
(3210000,280477,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Raiment, Blade Lament'),
(3210000,280486,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Waistband of the Gundrak Temple'),
(3210000,280532,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Wolfhide Trousers of the Iron Banner'),
(3210000,280537,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Old Warden''s Tunic of the Onslaught Harbor'),
(3210000,280541,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Mace, Stormshard Ash'),
(3210000,280702,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | The Ravenous Graspers'),
(3210000,280841,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Sandals, Wolfheart Thorn'),
(3210000,320258,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Voidkeeper''s Mournful War Leggings'),
(3210000,320766,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | First Warden''s Girdle'),
(3210000,320888,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Boneforged Mallet'),
(3210000,320957,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Hearthkeeper''s Spellscarred Choker'),
(3210000,340211,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Blood Queen''s Skull of the Mystic Eye'),
(3210000,340228,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Gemmed Band, Wolfheart Hunter'),
(3210000,340319,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Froststeel Walkers'),
(3210000,340345,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Grimdark Cord of Scourge Host'),
(3210000,340451,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Mournful Shoes of the Dragon Flame'),
(3210000,340595,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Sandals, West Spear'),
(3210000,340644,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Nightlord''s Fetish of the Iron Dwarf'),
(3210000,340817,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Wyrmcaller''s Runebands'),
(3210000,360013,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | North Quarrel Shoulderwraps'),
(3210000,360102,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Nameless Spellwand'),
(3210000,360104,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Mountainborn Leggings, First Warden''s Oath'),
(3210000,360315,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Warforged Star Wand'),
(3210000,360584,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Handwraps, Dusk Scream'),
(3210000,360612,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Rootbound Cord'),
(3210000,360618,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Obsidian Backcloth'),
(3210000,360657,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Firecaller''s Warstaff of the Blood Tide'),
(3210000,360761,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Spiritbound Kilt of the Dead King'),
(3210000,380178,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Adamant Stalkers of the Soul Watch'),
(3210000,380382,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Forgotten Footguards'),
(3210000,380387,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Lightforged Cowl'),
(3210000,380540,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Plagueforged Harness of the Burning Star'),
(3210000,380748,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Ironclad Longstaff'),
(3210000,380923,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000593 | Hammer Mist Maul');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3210001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3210001,200130,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Ironkeeper''s War Sword'),
(3210001,200859,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | The Skyforged Battleplate Legguards'),
(3210001,220826,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Titanguard''s Legguards of the Ivory Crown'),
(3210001,240318,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | The Thornbound Epaulets'),
(3210001,240663,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | The Necrotic Rune Band'),
(3210001,240813,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Leggings, Dream Shade'),
(3210001,280777,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Kilt, Grey Winter'),
(3210001,280840,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Faded Coil, Ashwarden''s Oath'),
(3210001,320796,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Helm of the Dragon Queen'),
(3210001,320990,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Ironlord''s Fearsome Footguards'),
(3210001,340417,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Veil of the Broken Banner'),
(3210001,340455,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Treads, Dragon Stone'),
(3210001,360062,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | The Scarlet Waistband'),
(3210001,360181,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Scepter, Wyrm Glow'),
(3210001,360302,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Lightwoven Cord, Titanwarden''s Oath'),
(3210001,360628,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Amulet, Far Banner'),
(3210001,360793,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | The Nightforged Battle Staff'),
(3210001,360827,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Stonecarved Handwraps of Ancient Promise'),
(3210001,380708,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Handguards of the First King'),
(3210001,380764,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 trash | Blood Prince''s Timeworn Seal');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3210002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3210002,200094,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Doomforged Backcloth of the Serpent Spirit'),
(3210002,200168,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Pathfinder''s Handplates'),
(3210002,200176,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Embercaller''s Edge'),
(3210002,200252,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Graveborn Bracers'),
(3210002,200262,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Thornwoven Charm of the Winter Moon'),
(3210002,200288,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Charm of the Blue Flight'),
(3210002,200342,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Last Keeper''s Cuirass of the Ruby Sanctum'),
(3210002,200497,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Visor, Long Wound'),
(3210002,200665,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Flamecaller''s Lens'),
(3210002,200827,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Wolfcaller''s Earthwoven Handplates'),
(3210002,200928,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | The Whitefrost Waistguard'),
(3210002,200952,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Dragonhide War Hatchet'),
(3210002,220039,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Runesmith''s Warhelm of the Scarlet Bastion'),
(3210002,220137,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Starfang Cleaver Warplate'),
(3210002,220277,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Cleaver of Rune Crown'),
(3210002,220451,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Moonkeeper''s Visor of the Hodir Hall'),
(3210002,220603,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Thornbound Badge of Avalanche'),
(3210002,220734,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Grey Maw Wristplates'),
(3210002,220897,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Wintersteel Armplates of Astral Crown'),
(3210002,240258,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Stonehewn Chausses'),
(3210002,240295,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Clouded Bracers, Scarlet Inquisitor''s Oath'),
(3210002,240700,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Silversteel Warbelt'),
(3210002,260079,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | The Conqueror Tunic'),
(3210002,260244,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Legwraps, Raven Guard'),
(3210002,260363,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | High Shield Waistguard'),
(3210002,260425,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Headdress of Dragon Throne'),
(3210002,260436,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Crusader Battle Fist of Altar of Sseratus'),
(3210002,260454,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Argent Defender''s Thunderforged Wargrips'),
(3210002,260494,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Moonkeeper''s Dreamwoven Clasp'),
(3210002,260625,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Clutches, Ivory Watch'),
(3210002,260742,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Spellbinder''s Shortbow'),
(3210002,260791,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Wildlord''s Effigy'),
(3210002,260877,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Wyrmhide Fang of Argent Tournament'),
(3210002,260928,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Icewarden''s Stoneward Badge'),
(3210002,280002,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Vestments, Spell Punch'),
(3210002,280229,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Signet of the Ice King'),
(3210002,280245,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | The Thunderous Bindings'),
(3210002,280363,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Warlord''s Fingerband of the Fallen Star'),
(3210002,280628,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Dread Walker Archmage Staff'),
(3210002,280888,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Radiant Cuffs of Twilight Reach'),
(3210002,280976,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Wild Bone Wand of Onslaught Harbor'),
(3210002,320257,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | The Bearhide Belt'),
(3210002,320291,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Wolfhide Legguards of Grizzlemaw'),
(3210002,320327,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | The Illusory Gauntlets'),
(3210002,320486,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Northguard''s Greatstaff'),
(3210002,320538,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Soulforged Helm, Thunderwarden''s Oath'),
(3210002,320984,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Ironthane''s War Leggings of the Cold Watch'),
(3210002,340026,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Shoulderwraps, Bleak Dirge'),
(3210002,340038,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Ringlet of the Ancient Frost'),
(3210002,340140,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Warmaster''s Vest'),
(3210002,340244,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Bloodkeeper''s Robe of the Black Ritual'),
(3210002,340278,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Iron Queen''s Graveborn Cinch'),
(3210002,340331,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Runeguard''s Pants of the Tirisfal Glades'),
(3210002,340493,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Merciless Epaulets of the Exodar Crystal'),
(3210002,340896,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Chestwrap of the Warsong Clan'),
(3210002,360011,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Griefbound Hexing Rod of the Sable Crown'),
(3210002,360244,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Wrap of Ice Crown'),
(3210002,360264,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Gemmed Band, Earth Light'),
(3210002,360371,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Gilded Coil'),
(3210002,360439,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Stormbound Bindings'),
(3210002,360510,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Rune Queen''s Shroud'),
(3210002,360734,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Soulcaller''s Veil of the Wild Pact'),
(3210002,360800,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Skullcap, Dusk Mark'),
(3210002,360983,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Graspers, Scarlet Claw'),
(3210002,380046,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Lightlord''s Sinister Coil'),
(3210002,380072,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Ringlet of Golden King'),
(3210002,380248,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Silver King''s Wargrips'),
(3210002,380266,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Scourged Longstaff'),
(3210002,380347,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Earthwarden''s Claws'),
(3210002,380596,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Bonewarden''s Age-darkened Ringlet'),
(3210002,380973,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Treads of Shadow Forge'),
(3210002,380983,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000595 | Icetouched Medallion');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3210003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3210003,200104,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Stonefather''s Pauldrons of the Violet Gate'),
(3210003,200358,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Greathelm, Prime Vengeance'),
(3210003,200426,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Brutal Pauldrons'),
(3210003,200679,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Starsteel Cuirass of Silent Crown'),
(3210003,200714,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Cabalistic Footplates of Ancient Frost'),
(3210003,200775,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Graven Gauntlets'),
(3210003,200830,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Warbelt of the Last Watch'),
(3210003,220082,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Legplates of the Dusk Watch'),
(3210003,220116,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Runesteel Legguards'),
(3210003,220248,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Stonewarden''s Breastplate'),
(3210003,220305,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Ancient Wargrips of the Dalaran'),
(3210003,220323,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Manaforged War Axe'),
(3210003,220389,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Starlit Bracers of Searing Gorge'),
(3210003,220495,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Dreambound Wargrips'),
(3210003,220527,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Runekeeper''s Clawmarked War Greaves'),
(3210003,220600,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Ritual Waistguard of the War Oath'),
(3210003,220611,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Horn of the Warsong Hold'),
(3210003,220966,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Broadsword of the Dark Iron Clan'),
(3210003,240147,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Eternal Boots of Frost Forge'),
(3210003,240168,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Boneguard''s Wolfhide Shoulderguards'),
(3210003,240212,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Moon King''s Thornbound Repeating Rifle'),
(3210003,240244,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Earthkeeper''s Spaulders of the Northwatch'),
(3210003,240259,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Sunbound Warboots of Hidden Road'),
(3210003,240327,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Shadowguard''s Greatcloak'),
(3210003,240328,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Hauberk of the War Forge'),
(3210003,240388,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | War Mantle, Primal Cleaver'),
(3210003,240580,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Wolfwarden''s Wristguards'),
(3210003,240693,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Farseer''s Warhelm'),
(3210003,260003,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Violet Keeper''s Medallion'),
(3210003,260139,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Battlesage''s Living Shoulderpads'),
(3210003,260306,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Runesword of Sun Spirit'),
(3210003,260311,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Stormsteel Legguards of North Road'),
(3210003,260503,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Feathered Key of Khaz Modan'),
(3210003,260526,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Carapace, Shattered Chill'),
(3210003,260829,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Darkfire Clutch Boots'),
(3210003,260899,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Worldforged Signet'),
(3210003,260973,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Bindings of the Violet Crown'),
(3210003,280047,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Ravenwarden''s Runebands'),
(3210003,280183,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Falcon Knuckle Graspers'),
(3210003,280186,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Cord of the Shattered Gate'),
(3210003,280361,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Adamant Gemmed Band of Broken Spear'),
(3210003,280398,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Pants of Holy Flame'),
(3210003,280448,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Raider Sash'),
(3210003,280619,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Saronite Gloves, Mooncaller''s Oath'),
(3210003,280691,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Dragonstalker''s Walkers of the Iron Pact'),
(3210003,280820,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Icecaller''s Unbroken Loop'),
(3210003,280952,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Boneguard''s Gleaming Robes'),
(3210003,320001,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Ravenwarden''s Runering'),
(3210003,320028,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Deepfrost Rampart'),
(3210003,320051,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Cape of Deep Hall'),
(3210003,320087,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Seer''s Thunderous Great Hauberk'),
(3210003,320137,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Darkmoon Great Hauberk'),
(3210003,320196,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Jagged Greaves'),
(3210003,320256,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Talisman of the Blade Edge'),
(3210003,320537,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Waistguard of Pale Crown'),
(3210003,320540,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | The Stormforged Stone'),
(3210003,320546,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Gloves of the Silent King'),
(3210003,320757,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Jagged Shard of the Emerald Wilds'),
(3210003,320784,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Thunderous Waistguard of Storm Peaks'),
(3210003,320859,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Battlesage''s Boots'),
(3210003,320942,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Waistguard of the Restless Dead'),
(3210003,320972,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Ornate Chausses'),
(3210003,340141,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Wildforged Hood'),
(3210003,340178,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Longcloak of the Silver Dawn'),
(3210003,340212,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Stave, Void Breaker'),
(3210003,340499,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Blademaster''s Hoop'),
(3210003,340784,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Amulet, Icefang Thirst'),
(3210003,340862,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Blade Decree Runic Rod'),
(3210003,340975,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Greenwood Kilt of Final Watch'),
(3210003,360019,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Shadow Gloom Robe'),
(3210003,360093,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Broadsword, Wyrm Sorrow'),
(3210003,360162,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Cryptlord''s Corrupted Bracelets'),
(3210003,360285,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Frostmage''s Unholy Medallion'),
(3210003,360408,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Zealous Sash'),
(3210003,360457,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Rotting Band, Hearthwarden''s Oath'),
(3210003,360515,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Twilight Mail Cuffs'),
(3210003,360564,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Jeweled Graspers'),
(3210003,360631,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Last Queen''s Earthbound Chain'),
(3210003,360646,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Brutish Binding of the Frostguard'),
(3210003,360660,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Wintercaller''s Blackened Regalia'),
(3210003,360893,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Dream Ruin Gloves'),
(3210003,360922,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Spirit Wand, Titan Vine'),
(3210003,360960,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Skullcap, Bleak Light'),
(3210003,380165,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Carrion Clutches of Rime Watch'),
(3210003,380180,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Tunic of the Undercity Depths'),
(3210003,380263,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Hollow Necklace of Zim Torga'),
(3210003,380285,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Faded Jerkin of Rimefang'),
(3210003,380418,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Firekeeper''s Helm of the Nightwatch'),
(3210003,380645,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Girdle, Lion Sorrow'),
(3210003,380657,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Headguard of Blood Memory'),
(3210003,380741,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Scarlet Bracers of the Fel Flame'),
(3210003,380765,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Pathfinder''s Claws of the Bronze Flight'),
(3210003,380916,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000596 | Grimlord''s Brassbound Shoulderguards');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3210004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3210004,200518,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000597 | Frostworn Handplates of the Titan King'),
(3210004,200537,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000597 | Winter Storm Footplates'),
(3210004,200768,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000597 | Highborne Great Pauldrons'),
(3210004,220351,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000597 | Firewarden''s Warsword'),
(3210004,220767,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000597 | Wildguard''s War Leggings'),
(3210004,380989,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000597 | Duskwarden''s Bindings of the Runekeeper');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3210005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3210005,200638,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000600 | The Voidsteel Shoulderplates'),
(3210005,220744,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000600 | Battleplate, Mist Judgment'),
(3210005,260434,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000600 | Colossal Chestguard'),
(3210005,340506,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000600 | Shoes of Iron Banner'),
(3210005,360663,0,0,0,1,1,1,1,'Generated map_209_difficulty_0 boss_000600 | Jeweled Warder Cloak of Blood Pact');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7795 AND `Item` = 2010000262 AND `Reference` = 3210000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7795,2010000262,3210000,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | boss_000593');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5648 AND `Item` = 2010000263 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5648,2010000263,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5649 AND `Item` = 2010000264 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5649,2010000264,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 5650 AND `Item` = 2010000265 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(5650,2010000265,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7246 AND `Item` = 2010000266 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7246,2010000266,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7247 AND `Item` = 2010000267 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7247,2010000267,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7268 AND `Item` = 2010000268 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7268,2010000268,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7274 AND `Item` = 2010000269 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7274,2010000269,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7604 AND `Item` = 2010000270 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7604,2010000270,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7605 AND `Item` = 2010000271 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7605,2010000271,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7606 AND `Item` = 2010000272 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7606,2010000272,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7608 AND `Item` = 2010000273 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7608,2010000273,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7797 AND `Item` = 2010000274 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7797,2010000274,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8095 AND `Item` = 2010000275 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8095,2010000275,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8120 AND `Item` = 2010000276 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8120,2010000276,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10080 AND `Item` = 2010000277 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10080,2010000277,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10081 AND `Item` = 2010000278 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10081,2010000278,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10082 AND `Item` = 2010000279 AND `Reference` = 3210001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10082,2010000279,3210001,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8127 AND `Item` = 2010000280 AND `Reference` = 3210002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8127,2010000280,3210002,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | boss_000595');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7272 AND `Item` = 2010000281 AND `Reference` = 3210003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7272,2010000281,3210003,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | boss_000596');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7271 AND `Item` = 2010000282 AND `Reference` = 3210004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7271,2010000282,3210004,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | boss_000597');

DELETE FROM `creature_loot_template` WHERE `Entry` = 7267 AND `Item` = 2010000283 AND `Reference` = 3210005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(7267,2010000283,3210005,2,0,1,0,1,1,'Generated encounter attachment | map_209_difficulty_0 | boss_000600');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220000,200192,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000267 | Old Knight''s Great Pauldrons'),
(3220000,240942,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000267 | Ironclad Handguards'),
(3220000,280435,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000267 | Moonlord''s Robes'),
(3220000,320581,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000267 | Silversteel Vambraces'),
(3220000,340952,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000267 | Titanwarden''s Mantle'),
(3220000,360458,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000267 | The Manawoven Cuffs'),
(3220000,360891,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000267 | Armbands of Scarlet Flame');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220001,200248,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Silversteel Orb of the Crypt Lord'),
(3220001,200286,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Last Queen''s Rune-etched Locket'),
(3220001,200413,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Royal Visor'),
(3220001,200656,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Runewoven Ranseur of Zangarmarsh'),
(3220001,200766,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Battleaxe, Necro Blade'),
(3220001,220059,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Girdle, Primal Breath'),
(3220001,220195,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Hoop of the Taunka Village'),
(3220001,220404,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Legguards, Gold Ice'),
(3220001,220506,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Promise of Arcane Moon'),
(3220001,220508,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Beastmarked Rampart of Great Bear'),
(3220001,220664,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Waistguard, Soul Spirit'),
(3220001,220693,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Moon Queen''s Ring'),
(3220001,220728,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Spear Grasp War Relic'),
(3220001,220817,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Obsidian Roar Footplates'),
(3220001,220881,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Bear Briar Armguards'),
(3220001,220900,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Feathered Armguards of Wyrm Queen'),
(3220001,240162,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Violet Mage''s Runeforged War Mantle'),
(3220001,240175,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Collar of the Silent King'),
(3220001,240620,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Ivory Wrist Chains of the Earth Spirit'),
(3220001,240944,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Legmail of Halls of Lightning'),
(3220001,260025,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Titan Crown Tunic'),
(3220001,260248,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Pale-blue Treads, Twilightcaller''s Oath'),
(3220001,260374,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Burnished Mantle'),
(3220001,260388,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Pale-blue Spellknife of the Restless Dead'),
(3220001,260461,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Pants of Shadow King'),
(3220001,260511,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Titanbound Chestguard of Ebon Watch'),
(3220001,260704,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Rimeforged Tunic of Makers Forge'),
(3220001,260770,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Watchful Leggings of Mana Forge'),
(3220001,260792,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Ravenbound Legguards'),
(3220001,280095,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Pendant of Crimson Dawn'),
(3220001,280140,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Zealous Gemmed Band'),
(3220001,280163,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Watchkeeper''s Mark'),
(3220001,280270,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Shattered Promise Armbands'),
(3220001,280400,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Witchlord''s Sepulchral Tiara'),
(3220001,280401,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Graspers of the Crimson Dawn'),
(3220001,280417,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Loop of the Military Wing'),
(3220001,280464,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | The Draconic Robe'),
(3220001,280530,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | The Dreadbound Waistwrap'),
(3220001,280552,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | The Dawnforged Leggings'),
(3220001,280830,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Ironkeeper''s Mistbound Shoulder Cape'),
(3220001,300013,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Stormwarden''s Iron Boots'),
(3220001,300242,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Cryptlord''s Warbelt of the Deep Mountain'),
(3220001,300300,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | First Knight''s Breastplate'),
(3220001,300631,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Unbroken Horn Maul'),
(3220001,300660,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Wolfwarden''s Battle Girdle'),
(3220001,300800,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Pauldrons of Pale Winter'),
(3220001,300827,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Frost King''s Stormwrought Talisman'),
(3220001,300882,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Waistplate of the North Wind'),
(3220001,320165,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Ironclad Greaves of Unquiet King'),
(3220001,320226,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | The Hoarfrost Casque'),
(3220001,320427,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Shadow King''s Spaulders'),
(3220001,320662,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Gloves, Violet Shield'),
(3220001,320677,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Runemaster''s Shiv'),
(3220001,320696,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Bracers of the Soul Reaper'),
(3220001,320914,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Goldbound Leggings'),
(3220001,320949,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Darkfire Anvil Chainmail'),
(3220001,320961,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Starfire Vow Compass'),
(3220001,320969,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Legmail of the Endless March'),
(3220001,340358,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Spell Lament Chestwrap'),
(3220001,340369,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Thorned Dagger'),
(3220001,340472,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | The Stormwrought Handwraps'),
(3220001,340516,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Mist Steel Scarab'),
(3220001,340815,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Duskbound Medallion'),
(3220001,360227,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Pendant Chain, Death Hand'),
(3220001,360607,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Warwarden''s Shoulderwraps'),
(3220001,360706,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Stonehewn Shoulder Cape of Wild King'),
(3220001,360744,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Starwoven Warstaff'),
(3220001,360848,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Shoes, Soulshard Guard'),
(3220001,380281,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Shoulderpads of Moonwarden'),
(3220001,380294,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Shadowguard''s Leggings of the Great Hunt'),
(3220001,380312,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Boots of the Midnight Flame'),
(3220001,380349,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Pendant Chain, Thunder Banner'),
(3220001,380706,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Zealous Tablet of Winter Forge'),
(3220001,380794,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Seal Ring of the Eastern Plaguelands'),
(3220001,380832,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Ritual Knife of Silver Pact'),
(3220001,380946,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 trash | Shadowbound Headguard of the Lost Vanguard');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220002,240946,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000268 | The Froststeel Armguards'),
(3220002,260967,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000268 | Voidforged Boots of Undercity Depths'),
(3220002,340421,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000268 | Gravecaller''s Shadowforged Scarab'),
(3220002,360392,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000268 | Wind Feather Wristwraps');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220003,200020,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | The Coldhearted Cuirass'),
(3220003,220691,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | Headplate of Frozen Road'),
(3220003,220743,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | Crypt Decree Scarab'),
(3220003,280144,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | Gold Pact Armbands'),
(3220003,300076,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | The Dwarven Greaves'),
(3220003,320360,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | Kingsguard Vial of Frostguard'),
(3220003,320683,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | Ash Hide Helm'),
(3220003,340665,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000269 | Runeforged Kilt of Ancient Night');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220004,200655,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000270 | Last Warden''s Blacksteel Helm'),
(3220004,200873,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000270 | Backcloth of Ebon Flame'),
(3220004,220115,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000270 | Arctic Runeblade of the Construct Wing'),
(3220004,220821,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000270 | Lost Keeper''s Greaves of the Frozen North');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220005,280225,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000272 | Spectral Pendant'),
(3220005,280718,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000272 | Forgotten Forge Skirt'),
(3220005,380302,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000272 | Warsage''s Broken Drape');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220006,200156,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Legguards, Wind Glaive'),
(3220006,200452,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | The Forsaken Warbracers'),
(3220006,240016,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Gravewarden''s Brutal Vambraces'),
(3220006,240140,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Wyrm Queen''s Heavy Crossbow'),
(3220006,240917,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Argent Champion''s Gauntlets'),
(3220006,280992,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Devout Warband of the Lost Oath'),
(3220006,300845,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Moonlord''s Mystwoven Helm'),
(3220006,340209,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Frostmarked Sash of Pale Crown'),
(3220006,340435,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | The Lightblessed Cinch'),
(3220006,340744,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Mountainborn Hood of the Twilight Crown'),
(3220006,360120,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Soulfire Memory Epaulets'),
(3220006,360168,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Profane Beads'),
(3220006,380324,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Deathly Jerkin'),
(3220006,380561,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000274 | Lost Keeper''s Waistband');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220007,200114,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | The Whitefrost Sabatons'),
(3220007,200386,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Ghostfire Bolt Promise'),
(3220007,220214,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | The Lightblessed Brooch'),
(3220007,220291,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Winterwarden''s Shoulder Drape'),
(3220007,220946,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Hoop of the Long Road'),
(3220007,220948,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Wyrmforged Waistplate, Bloodguard''s Oath'),
(3220007,240494,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Coif of the Fel Flame'),
(3220007,240970,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Stonecaller''s Great Cleaver'),
(3220007,280403,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Sunsteel Crystal'),
(3220007,280681,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Stoneforged Staff of the Scourge Watch'),
(3220007,300039,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Stone Relic of Moon Grove'),
(3220007,300239,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Bloodkeeper''s Broadsword'),
(3220007,300387,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Footplates, Astral Lord'),
(3220007,300401,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Shadow King''s Torc of the Titan Vault'),
(3220007,300454,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Stormkeeper''s Coldfire Thunder Hammer'),
(3220007,300518,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | The Rune-etched Wargrips'),
(3220007,300546,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Bonewarden''s Pendant Chain'),
(3220007,300957,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Bright Crown Iron Boots'),
(3220007,300966,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Highblade of the Amphitheater'),
(3220007,300998,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Rune Queen''s Patient Warbelt'),
(3220007,320189,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Illusory War Leggings of Wind King'),
(3220007,320746,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | The Fierce Spaulders'),
(3220007,340113,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Wildlord''s Keepsake of the Dragon Guard'),
(3220007,340181,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Plaguekeeper''s Moonforged Bindings'),
(3220007,340374,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Austere Cowl of the Shadow Pact'),
(3220007,360113,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | The Bitter Wristwraps'),
(3220007,360289,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Warmaster''s Steadfast Circlet'),
(3220007,380675,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000275 | Battlemage''s Leggings');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3220008;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3220008,280620,0,0,0,1,1,1,1,'Generated map_229_difficulty_0 boss_000276 | Duskwarden''s Heavenforged Binding');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9196 AND `Item` = 2010000284 AND `Reference` = 3220000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9196,2010000284,3220000,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000267');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9096 AND `Item` = 2010000285 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9096,2010000285,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9097 AND `Item` = 2010000286 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9097,2010000286,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9098 AND `Item` = 2010000287 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9098,2010000287,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9197 AND `Item` = 2010000288 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9197,2010000288,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9216 AND `Item` = 2010000289 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9216,2010000289,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9217 AND `Item` = 2010000290 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9217,2010000290,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9218 AND `Item` = 2010000291 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9218,2010000291,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9219 AND `Item` = 2010000292 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9219,2010000292,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9239 AND `Item` = 2010000293 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9239,2010000293,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9240 AND `Item` = 2010000294 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9240,2010000294,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9241 AND `Item` = 2010000295 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9241,2010000295,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9257 AND `Item` = 2010000296 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9257,2010000296,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9258 AND `Item` = 2010000297 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9258,2010000297,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9259 AND `Item` = 2010000298 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9259,2010000298,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9260 AND `Item` = 2010000299 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9260,2010000299,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9261 AND `Item` = 2010000300 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9261,2010000300,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9262 AND `Item` = 2010000301 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9262,2010000301,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9263 AND `Item` = 2010000302 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9263,2010000302,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9264 AND `Item` = 2010000303 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9264,2010000303,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9265 AND `Item` = 2010000304 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9265,2010000304,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9266 AND `Item` = 2010000305 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9266,2010000305,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9267 AND `Item` = 2010000306 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9267,2010000306,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9268 AND `Item` = 2010000307 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9268,2010000307,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9269 AND `Item` = 2010000308 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9269,2010000308,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9583 AND `Item` = 2010000309 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9583,2010000309,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9596 AND `Item` = 2010000310 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9596,2010000310,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9692 AND `Item` = 2010000311 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9692,2010000311,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9693 AND `Item` = 2010000312 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9693,2010000312,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9716 AND `Item` = 2010000313 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9716,2010000313,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9717 AND `Item` = 2010000314 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9717,2010000314,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9718 AND `Item` = 2010000315 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9718,2010000315,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9817 AND `Item` = 2010000316 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9817,2010000316,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9818 AND `Item` = 2010000317 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9818,2010000317,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9819 AND `Item` = 2010000318 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9819,2010000318,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10083 AND `Item` = 2010000319 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10083,2010000319,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10263 AND `Item` = 2010000320 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10263,2010000320,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10317 AND `Item` = 2010000321 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10317,2010000321,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10318 AND `Item` = 2010000322 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10318,2010000322,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10319 AND `Item` = 2010000323 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10319,2010000323,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10366 AND `Item` = 2010000324 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10366,2010000324,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10372 AND `Item` = 2010000325 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10372,2010000325,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10374 AND `Item` = 2010000326 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10374,2010000326,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10376 AND `Item` = 2010000327 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10376,2010000327,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10447 AND `Item` = 2010000328 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10447,2010000328,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10509 AND `Item` = 2010000329 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10509,2010000329,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10762 AND `Item` = 2010000330 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10762,2010000330,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10814 AND `Item` = 2010000331 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10814,2010000331,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10899 AND `Item` = 2010000332 AND `Reference` = 3220001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10899,2010000332,3220001,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9236 AND `Item` = 2010000333 AND `Reference` = 3220002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9236,2010000333,3220002,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000268');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9237 AND `Item` = 2010000334 AND `Reference` = 3220003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9237,2010000334,3220003,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000269');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10596 AND `Item` = 2010000335 AND `Reference` = 3220004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10596,2010000335,3220004,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000270');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9736 AND `Item` = 2010000336 AND `Reference` = 3220005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9736,2010000336,3220005,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000272');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10220 AND `Item` = 2010000337 AND `Reference` = 3220006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10220,2010000337,3220006,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000274');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9568 AND `Item` = 2010000338 AND `Reference` = 3220007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9568,2010000338,3220007,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000275');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9816 AND `Item` = 2010000339 AND `Reference` = 3220008;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9816,2010000339,3220008,2,0,1,0,1,1,'Generated encounter attachment | map_229_difficulty_0 | boss_000276');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230000,200496,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Carapace, Grim Doom'),
(3230000,220421,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Shadowsteel Bracers'),
(3230000,220737,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Ancient Keeper''s Flawless Battle Girdle'),
(3230000,240977,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | The Voidforged Runebow'),
(3230000,260297,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Gravelord''s Gladiatorial Shoulderwraps'),
(3230000,280241,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | The Dragonsteel Cowl'),
(3230000,280407,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Ravenkeeper''s Runebands of the Mana Wyrm'),
(3230000,280801,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Cabalistic Shoulderwraps of Dying Promise'),
(3230000,280998,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Spellscarred Legwraps'),
(3230000,340616,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Ironclad Trousers of the Titan Crown'),
(3230000,360738,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Firekeeper''s Runed Wand'),
(3230000,380432,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000227 | Titan King''s Talisman');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230001,200077,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Stonefather''s Sabatons of the Rune Forge'),
(3230001,200122,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Tempered Greaves'),
(3230001,200128,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Hoary Iron Boots of the Stone Giant'),
(3230001,200172,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Nightkeeper''s Everfrost Fetish'),
(3230001,200292,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Great Pauldrons of Lost Road'),
(3230001,200333,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Spellblade, Ebon Ice'),
(3230001,200396,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Warplate of Frost Watch'),
(3230001,200474,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Moonforged Vambraces'),
(3230001,200483,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Royal Cloak of the Blood Price'),
(3230001,200523,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Sabatons of the Grizzlemaw'),
(3230001,200527,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Voidlord''s Handplates'),
(3230001,200579,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Deathly Iron Boots'),
(3230001,200627,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Nightlord''s Keepsake of the Final March'),
(3230001,200631,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Greaves of the Silvermoon Spires'),
(3230001,200684,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Rimebound Vambraces'),
(3230001,200693,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Legguards, Frozen Horn'),
(3230001,200742,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Hornbow of the Red Moon'),
(3230001,200755,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Greathelm of the Deep Forge'),
(3230001,200758,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Sunbound Handguards, Dragonlord''s Oath'),
(3230001,200871,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Deep Steel War Pauldrons'),
(3230001,200884,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Dread Warhelm'),
(3230001,200909,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bonekeeper''s Stonebound Royal Band'),
(3230001,200927,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Beastmarked Great Runeaxe of Titan King'),
(3230001,200980,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Warbelt, Frost Dusk'),
(3230001,220011,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Stoneguard''s Armguards of the Storm Queen'),
(3230001,220027,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bonewarden''s Mystic Handplates'),
(3230001,220087,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Primeval War Greaves of Iron Forge'),
(3230001,220103,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Neckchain of the Dark Forge'),
(3230001,220104,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dark Vow Royal Band'),
(3230001,220136,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | First Warden''s Clouded Feather'),
(3230001,220182,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Icewarden''s Legplates'),
(3230001,220219,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Silent King''s Battleplate of the Kaskala'),
(3230001,220230,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Blessed Legplates of Dread Host'),
(3230001,220235,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Scarlet Templar''s Wargrips'),
(3230001,220246,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Warped Great Gauntlets'),
(3230001,220262,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Terrible Legguards of Scarlet Keep'),
(3230001,220274,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Titanforged Greaves, Dragonkeeper''s Oath'),
(3230001,220349,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Serrated Gemmed Band of War Forge'),
(3230001,220365,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Brutal Icon, Starcaller''s Oath'),
(3230001,220382,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Carapace of Lost Memory'),
(3230001,220392,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Steelforged Wargrips'),
(3230001,220422,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Scourgeforged Headplate'),
(3230001,220482,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dawnsteel Buckler of the Deep Mountain'),
(3230001,220499,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Battle Girdle of Hallowed Ground'),
(3230001,220531,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Great Pauldrons, Dire Rime'),
(3230001,220567,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Great Pauldrons of Soul Reaper'),
(3230001,220689,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ritual War Mace of the Iron Oath'),
(3230001,220708,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wildbound Waistplate of the Sunwell'),
(3230001,220712,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Chestplate of Ancient Thorn'),
(3230001,220758,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Torque, Wildfire Shot'),
(3230001,220763,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Sanctified War Leggings of Silver Flame'),
(3230001,220772,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Helm, Thorn Reach'),
(3230001,220774,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ironcaller''s Chestplate'),
(3230001,220802,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Runering of Western Plaguelands'),
(3230001,220806,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Nightfang Arrow Helm'),
(3230001,220829,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Sun Queen''s Idol of the Fel Watch'),
(3230001,220869,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Purified Warcloak'),
(3230001,220977,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Titanic Vambraces'),
(3230001,240002,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Emberforged Warband of Distant Memory'),
(3230001,240014,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Forgotten Knight''s Backcloth'),
(3230001,240043,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Gold Flame Band'),
(3230001,240098,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Hellforged Treads'),
(3230001,240126,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Fel Helm of the Great Hunt'),
(3230001,240170,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Argent Knight''s Emberforged Wargrips'),
(3230001,240198,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Winterworn Wrap of the Ancient Frost'),
(3230001,240231,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wildkeeper''s Surcoat of the Northern Forge'),
(3230001,240250,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Drape of Black Ritual'),
(3230001,240256,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dwarven Waistchain'),
(3230001,240286,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dawnwarden''s Wrist Chains'),
(3230001,240304,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shadowmarked Handguards of Lost Road'),
(3230001,240383,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dire War Leggings'),
(3230001,240522,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Darkforged Ring'),
(3230001,240530,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Seer''s Warboots'),
(3230001,240582,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Broken Warden''s Lightforged Waistchain'),
(3230001,240594,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shieldbearer''s Bracers'),
(3230001,240750,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wyrm King''s Harness'),
(3230001,240790,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dragonsteel Coif of Far North'),
(3230001,240792,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Harness of Borean Expanse'),
(3230001,240851,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Barbed Necklace'),
(3230001,240885,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dalaran War Mantle, Ancestor''s Oath'),
(3230001,240913,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dawnforged Faceguard of Red Dragonflight'),
(3230001,240918,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ice Song Shroud'),
(3230001,240963,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Greaves of Wild Grove'),
(3230001,240976,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bloodfang Vine Wargrips'),
(3230001,240995,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Warlord Hauberk of Violet Flame'),
(3230001,260026,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Highborn''s Ironthane Kris'),
(3230001,260077,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Savage Tunic'),
(3230001,260114,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bindings of the Grave Watch'),
(3230001,260127,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Forgotten Keeper''s Stoic War Mace'),
(3230001,260128,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Waistguard, West Punch'),
(3230001,260132,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ebon Crusader''s Mark'),
(3230001,260187,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Stonefather''s Fingerband of the Rime Forge'),
(3230001,260236,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Crimson Walkers'),
(3230001,260250,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Sunlit Leggings'),
(3230001,260330,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Winterwarden''s Mantle'),
(3230001,260355,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Soldierly Choker of the Burning Sky'),
(3230001,260393,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ancient Queen''s Leggings'),
(3230001,260406,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Gravewarden''s Helm of the Wrathgate'),
(3230001,260431,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Breeches of Emerald Grove'),
(3230001,260489,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wild Bindings of Shadow Moon'),
(3230001,260501,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Sunlit Seal Ring of the Dark Portal'),
(3230001,260506,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Primal Promise'),
(3230001,260536,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Rune King''s Spaulders of the Shadow Ritual'),
(3230001,260584,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Unquiet Belt'),
(3230001,260623,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Breeches of the Violet Citadel'),
(3230001,260709,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Moonlit Warband'),
(3230001,260802,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Nameless Ringlet'),
(3230001,260805,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Silverkeeper''s Cloak'),
(3230001,260835,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ebon Veil of the Wild Watch'),
(3230001,260856,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dragonforged Leggings'),
(3230001,260902,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Starfire Plate Eye'),
(3230001,260921,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Weathered Waistguard'),
(3230001,260968,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Veiled Treads'),
(3230001,280009,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Heavy Pillar of the Ancient Night'),
(3230001,280061,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Winterguard''s Brittle Footwraps'),
(3230001,280067,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bone Starfall Boots'),
(3230001,280092,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Earthwoven Waistwrap'),
(3230001,280131,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Last Warden''s Bracelets of the Silver Moon'),
(3230001,280175,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Thunderwarden''s Sandals of the Pale Crown'),
(3230001,280194,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bindings, Frozen Sorrow'),
(3230001,280202,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Legwraps of Frozen Star'),
(3230001,280243,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Handwraps, Deep Mark'),
(3230001,280306,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shaman Staff of the Wyrm King'),
(3230001,280358,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shoulderwraps, Bright Fang'),
(3230001,280376,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Skull Blade Tunic'),
(3230001,280465,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Armorsmith''s Boneforged Treads'),
(3230001,280476,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | North Storm Pendant'),
(3230001,280480,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dalaran Binding of the Frost Giant'),
(3230001,280588,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Blazing Seal Ring of the Death March'),
(3230001,280646,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | White Judgment Ringlet'),
(3230001,280661,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Circle of the Water Spirit'),
(3230001,280669,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dawnwarden''s Runed Circlet'),
(3230001,280737,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wyrmcaller''s Primeval Battlecloak'),
(3230001,280757,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Robes of Red Dragon'),
(3230001,280759,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Heavenforged Walking Staff'),
(3230001,280773,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Mitts, Earth Rime'),
(3230001,280790,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Epaulets of the Orgrimmar Guard'),
(3230001,280808,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Gladiatorial Leggings'),
(3230001,280908,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Skyforged Kilt of the Ebon Blade'),
(3230001,280912,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Burnished Treads'),
(3230001,280946,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shadowsteel Breeches of Stone Crown'),
(3230001,280972,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Skullkeeper''s Robes of the Violet Flame'),
(3230001,320029,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Sacred Whisper Idol'),
(3230001,320173,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Timeworn Gauntlets of Mount Hyjal'),
(3230001,320194,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Girdle of First King'),
(3230001,320198,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Rime Dusk Chausses'),
(3230001,320247,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Circle of Green Flame'),
(3230001,320255,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Legguards of the Argent Crusade'),
(3230001,320294,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Runekeeper''s Beads'),
(3230001,320333,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ebon Marshal''s Enduring Scepter'),
(3230001,320385,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | War Axe of Stone King'),
(3230001,320399,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Moon Edge Greaves'),
(3230001,320416,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | War Leggings, Sky Steel'),
(3230001,320417,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bone Curse Crystal'),
(3230001,320421,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ancestor''s Talisman of the Violet Flame'),
(3230001,320449,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Starwoven Staff of the Azure Moon'),
(3230001,320459,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Sun Queen''s Boots of the Black Flight'),
(3230001,320483,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Casque of Ancient Spirit'),
(3230001,320576,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bloodbound Druid Staff'),
(3230001,320598,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Grips, Blood Moon'),
(3230001,320621,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Storm King''s Sunhallowed Gemmed Band'),
(3230001,320675,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Stonelord''s Warscarred Chausses'),
(3230001,320716,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Warlord Great Hauberk, Arcanist''s Oath'),
(3230001,320735,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Old Knight''s Mail of the Deep Roads'),
(3230001,320774,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Gleaming Gemmed Band of the Iron Pact'),
(3230001,320792,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dusk Song Waistchain'),
(3230001,320822,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Veil of Frozen North'),
(3230001,320881,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Clouded Headguard'),
(3230001,320918,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Worldwarden''s Wristguards'),
(3230001,320928,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Silverkeeper''s Voidforged Battlecloak'),
(3230001,320943,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Warshield of the Ivory Crown'),
(3230001,340031,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dire Cinch'),
(3230001,340056,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Frostcaller''s Draconic Trousers'),
(3230001,340073,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Draconic Cuffs of Golden Moon'),
(3230001,340074,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Hearthkeeper''s Armored Idol'),
(3230001,340092,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Lightlord''s Sepulchral Shoes'),
(3230001,340111,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Gloves of the Black Ritual'),
(3230001,340175,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shadowmarked Regalia of the Bone Lord'),
(3230001,340288,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Gold Light Tiara'),
(3230001,340344,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Worldkeeper''s Clasp of the Shadow Pact'),
(3230001,340360,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Grim Banner Shoulder Cape'),
(3230001,340456,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Warscarred Diadem of Iron Gate'),
(3230001,340459,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Manaforged Leggings of First Flame'),
(3230001,340469,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Darkfire Frost Signet Ring'),
(3230001,340514,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wolfcaller''s Skirt'),
(3230001,340547,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Plaguekeeper''s Tiara'),
(3230001,340579,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Dread Treads'),
(3230001,340677,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Earthbound Epaulets of Winter King'),
(3230001,340696,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bloodied Pendant of the Dead Watch'),
(3230001,340763,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Deathmarked Choker of Ironforge Guard'),
(3230001,340769,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Frostmage''s Wristwraps of the Long Road'),
(3230001,340835,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Necro Skull Binding'),
(3230001,340876,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Runic Footwraps of Valiance Keep'),
(3230001,340938,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Backcloth of the Winter King'),
(3230001,360070,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shoulderwraps of Holy Watch'),
(3230001,360100,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Kingsguard Shoes'),
(3230001,360269,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Soulwarden''s Rune Band of the Dawnwatch'),
(3230001,360308,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Grips of the Rune Forge'),
(3230001,360319,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ancient Keeper''s Boots of the Hidden Path'),
(3230001,360321,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Runebands of Storm Banner'),
(3230001,360329,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bloodforged Gorget'),
(3230001,360387,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Dawnsteel Vial'),
(3230001,360397,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Armbands of Great Hunt'),
(3230001,360491,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shoes, Death Clutch'),
(3230001,360492,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shieldbearer''s Waistband of the Frostguard'),
(3230001,360511,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Flawless Loop of River Heart'),
(3230001,360519,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Scourged Pendant Chain'),
(3230001,360532,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Grips of Titan Watcher'),
(3230001,360622,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Chain of the Ebon Flame'),
(3230001,360637,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Scourge Anvil Hood'),
(3230001,360666,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wristwraps, Bloodfire Steel'),
(3230001,360671,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shoulder Drape, Frozen Gaze'),
(3230001,360676,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Graspers of Hidden Path'),
(3230001,360696,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Blighted Battlecloak of Sacred Watch'),
(3230001,360801,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Deathwarden''s Frostmarked Circle'),
(3230001,360821,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Starwoven Rod of the Scarlet Banner'),
(3230001,360822,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Stonewarden''s Duskwoven Cord'),
(3230001,360852,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Battlesage''s Vial'),
(3230001,360887,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shoulder Cape of Ice Crown'),
(3230001,360889,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Northforged Skirt of the Silver Light'),
(3230001,380009,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wildwoven Grips'),
(3230001,380026,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Starlit Wristbands'),
(3230001,380041,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Legguards of Final Watch'),
(3230001,380142,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Ravenkeeper''s Boots of the Shadow King'),
(3230001,380250,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Thornbound Sigil of Red Dragonflight'),
(3230001,380270,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wyrmcarved Strap of Dark Portal'),
(3230001,380290,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Argent Champion''s Coldfire Girdle'),
(3230001,380292,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Shaman Staff, Unbroken Stone'),
(3230001,380331,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Claws of the Sacred Flame'),
(3230001,380378,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Starkeeper''s Graveforged Striders'),
(3230001,380417,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Graveforged Footguards, Archmage''s Oath'),
(3230001,380452,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Breeches of Dead Watch'),
(3230001,380472,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Helm of Grim Crown'),
(3230001,380475,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Waistguard of Ebon Hold'),
(3230001,380485,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Icewarden''s Wrathful Stalkers'),
(3230001,380488,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wolfcaller''s Plagueborn Tunic'),
(3230001,380524,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Deathcaller''s Cowl'),
(3230001,380572,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Profane Chestguard of Last Stand'),
(3230001,380611,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Hardened Leggings of the Divine Watch'),
(3230001,380612,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Froststeel Runering of the Dead Watch'),
(3230001,380644,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Crusader''s Battleworn Shoulderguards'),
(3230001,380652,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | The Arctic Headdress'),
(3230001,380664,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Walkers of Scholomance'),
(3230001,380709,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Wolfhide Cap'),
(3230001,380713,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Argent Shadow Cap'),
(3230001,380754,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Primal Dirge Brooch'),
(3230001,380772,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Dragonwarden''s Nightwoven Shoulderwraps'),
(3230001,380784,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Handguards of Iron Giant'),
(3230001,380796,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Voidwarden''s Sacred Breeches'),
(3230001,380835,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Old Keeper''s Headdress'),
(3230001,380854,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Spaulders of the Second Dawn'),
(3230001,380914,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Deathmask, Unholy Heart'),
(3230001,380932,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Bloodmage''s Mantle of the Hallowed Flame'),
(3230001,380972,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 trash | Drakescale Legguards of Sun Flame');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230002,200441,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Stalwart Sabatons'),
(3230002,200611,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Cursed Greatcloak of Scourge Lord'),
(3230002,200853,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Greaves of the Valgarde'),
(3230002,200886,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Ember Ripper Shard'),
(3230002,220112,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Thunderous Shoulderplates of Shadow Watch'),
(3230002,220162,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Ancestral Fetish'),
(3230002,220232,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Sunfire Spire Battlehammer'),
(3230002,220609,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Great Pauldrons of Dying Promise'),
(3230002,240047,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Blademaster''s Longcloak'),
(3230002,240460,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | The Ashen Gemmed Band'),
(3230002,240498,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | War Mantle, Hollow Dusk'),
(3230002,240568,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Ferocious Belt of the Azure Moon'),
(3230002,240765,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Witchcaller''s Helm of the Winter Watch'),
(3230002,260873,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Stone Reckoning Trousers'),
(3230002,280378,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Forge Twilight Mantle'),
(3230002,280604,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Warmarked Hand Hammer of Violet Flame'),
(3230002,280665,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Earthwoven Shoulder Cape of Fel Ritual'),
(3230002,280958,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Ghostly Brooch of Fallen Crown'),
(3230002,320109,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Girdle, Scourge Shadow'),
(3230002,320722,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Calm Mantle'),
(3230002,340758,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Dire Ember Diadem'),
(3230002,340801,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Voidkeeper''s Breeches of the Ebon Watch'),
(3230002,360044,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Gloves of Spider Wing'),
(3230002,360143,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Armorsmith''s Battle Staff'),
(3230002,360396,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Solemn Tunic of Stone Watch'),
(3230002,360701,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | The Briarbound Epaulets'),
(3230002,380104,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | The Reinforced Warder Cloak'),
(3230002,380483,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Ring of the Final Promise'),
(3230002,380486,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | The Weathered Longcloak'),
(3230002,380668,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | The Forgeblessed Chestpiece'),
(3230002,380880,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000228 | Windbound Charm of Raven Spirit');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230003,220285,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000229 | Lightbound Warbelt of Winter Watch'),
(3230003,240855,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000229 | Argent Casque'),
(3230003,260394,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000229 | Last Knight''s Fang of the Moon Watch'),
(3230003,260990,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000229 | Icekeeper''s Scimitar of the Frozen Dead'),
(3230003,280978,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000229 | West Scream Cap'),
(3230003,320803,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000229 | Soulforged Warboots of Broken Gate'),
(3230003,360780,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000229 | Brightsteel Binding of Makers Overlook');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230004,200330,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | The Necrotic Wristplates'),
(3230004,240358,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | Hateful Casque of Broken Hall'),
(3230004,260199,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | Rotting Spaulders of Bronze Flight'),
(3230004,260207,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | Footguards, Voidshard Crush'),
(3230004,260365,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | Talisman of the Silver Dawn'),
(3230004,320283,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | Footguards of the Shadow King'),
(3230004,320862,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | Sanctified Wristguards of Pale Flame'),
(3230004,340538,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000231 | Corpsebound Dagger of the Red Dragonflight');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230005,220736,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000232 | Seal Ring of the Valiance Keep'),
(3230005,360602,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000232 | Skyforged Charmstone of Makers Vault'),
(3230005,380385,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000232 | Gloves of the Iron Gate');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230007,200164,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000234 | Mirror of the Broken Hall'),
(3230007,200350,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000234 | The Briarbound Royal Cloak'),
(3230007,200609,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000234 | Crusader War Greaves of the Spellweaver'),
(3230007,220174,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000234 | Wargrips, Unquiet Pledge'),
(3230007,260366,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000234 | Unquiet Talisman of Ice Crown'),
(3230007,340956,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000234 | Regalia of Howling North'),
(3230007,360865,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000234 | Deathwarden''s Handwraps of the Stone King');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230008;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230008,200763,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Terrible Battleplate of Avalanche'),
(3230008,200786,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Desecrated Hoop of Broken Banner'),
(3230008,220297,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Legguards, Skull Whisper'),
(3230008,220823,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Sabatons, White Dirge'),
(3230008,240806,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Rime-coated Oathring of Sky King'),
(3230008,260168,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Dragon Queen''s Iceforged Brooch'),
(3230008,260196,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Cruel Cinch of the Forgotten Road'),
(3230008,260227,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Starcaller''s Stormforged Choker'),
(3230008,280138,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Ancestor''s Phylactery'),
(3230008,280268,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Binding of the Emerald Moon'),
(3230008,280276,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Pale Mist Breeches'),
(3230008,280421,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Promise of Northern Watch'),
(3230008,280427,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Jagged Neckchain of the Violet Flame'),
(3230008,320406,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | The Iceforged Ringlet'),
(3230008,320484,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | The Blackened Chopper'),
(3230008,340221,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Leggings of the Wild Hunt'),
(3230008,340286,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Mantle of the Wild Hunt'),
(3230008,340302,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Gloves of the Wild Hunt'),
(3230008,340402,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Robes of the Wild Hunt'),
(3230008,340517,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Purified Gorget of the Onslaught Harbor'),
(3230008,340613,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Cowl of the Wild Hunt'),
(3230008,360587,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Glittering Neckchain'),
(3230008,380013,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Stormmarked Warstaff'),
(3230008,380052,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Enchanted Waistguard, Stormwarden''s Oath'),
(3230008,380173,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Warped Branch'),
(3230008,380238,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Primeval Claws of the Shadow Watch'),
(3230008,380509,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Death Gaze Boots'),
(3230008,380690,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Cap, Titan Reckoning'),
(3230008,380779,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Bloodmage''s Ringlet of the Autumn Wind'),
(3230008,380873,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000235 | Walkers of North Wind');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230009;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230009,220101,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | Terrible Crusher of the Frozen Forge'),
(3230009,240926,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | Fearsome War Leggings'),
(3230009,260220,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | The Titan-carved Tunic'),
(3230009,280112,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | Emblem of Bronze Flight'),
(3230009,280528,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | Stormcaller''s Regalia of the Green Dragon'),
(3230009,300170,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | The Ruthless Handplates'),
(3230009,340068,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | Stormwrought Hoop'),
(3230009,360359,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000236 | Bindings of the Lost Road');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230010;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230010,200510,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000237 | Rangemaster''s Battle Girdle'),
(3230010,240273,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000237 | Broken Vow Spaulders'),
(3230010,240617,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000237 | Hearthwarden''s Casque of the Bone Gate'),
(3230010,260688,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000237 | Sainted Capelet'),
(3230010,320978,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000237 | Forsaken Legguards of Frozen Crown');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230012;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230012,200397,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Carapace of the Ebon Watch'),
(3230012,200528,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Circle of Ice Crown'),
(3230012,220726,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Warhelm of the Hidden Path'),
(3230012,240153,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Unbroken Treads'),
(3230012,240178,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Soldierly Drape'),
(3230012,260035,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Shoulderpads, Crimson Vigil'),
(3230012,260126,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Frozen King''s Cap of the Crimson Banner'),
(3230012,260944,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Leggings, Wyrm Glyph'),
(3230012,280197,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Hateful Tunic of Dying Light'),
(3230012,280930,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Forgemaster''s Leggings of the Black Moon'),
(3230012,320057,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Spiritkeeper''s Cryptborn War Leggings'),
(3230012,320527,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Shadowmage''s Gloves'),
(3230012,340210,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Lost Pledge Conduit'),
(3230012,340474,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Staff of the Wild Grove'),
(3230012,340828,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Darksteel Edge'),
(3230012,340921,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Cloak, Gray Doom'),
(3230012,360086,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Plaguetouched Footwraps'),
(3230012,360296,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Frozen King''s Cap of the Hidden Forge'),
(3230012,360445,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Far Doom Hood'),
(3230012,360661,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Walkers of Dark Forge'),
(3230012,380103,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Wargrips of the Dawn Vanguard'),
(3230012,380150,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Faithful Shoulderpads'),
(3230012,380328,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Ebon Tunic, Ashcaller''s Oath'),
(3230012,380952,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000239 | Windwarden''s Legguards of the Pale Winter');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230014;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230014,220420,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Cruel Emblem of Frozen Heart'),
(3230014,220918,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Warped Pendant Chain of Thunder Watch'),
(3230014,260084,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Heavy Badge'),
(3230014,260392,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Legwraps of the Nesingwary Camp'),
(3230014,280046,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Bladeguard''s Wristwraps'),
(3230014,340060,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Fel Epaulets of the Ebon Blade'),
(3230014,340149,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Bracelets of the Astral Watch'),
(3230014,360459,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000242 | Wolfguard''s Grips of the Scarlet Bastion');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3230016;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3230016,200302,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Mist Crush Locket'),
(3230016,200740,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Veil, Soulfire Shade'),
(3230016,200911,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Thundersteel Waistguard'),
(3230016,220716,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | The Cabalistic Greaves'),
(3230016,240200,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Battlemaiden''s Chopper of the Ancient Pact'),
(3230016,240287,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Hammered Warcloak of the Sindragosa Fall'),
(3230016,240832,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Moonkeeper''s Helm of the Light Breach'),
(3230016,260806,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Royal Band of the Blood Crown'),
(3230016,300340,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Bloodguard''s Crusher of the Cold Watch'),
(3230016,320238,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Hammered Treads of the Naxxramas'),
(3230016,320720,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Warsage''s Legmail'),
(3230016,340107,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Robes of the Crimson Dawn'),
(3230016,340150,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Cowl of the Crimson Dawn'),
(3230016,340187,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Leggings of the Crimson Dawn'),
(3230016,340224,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Gloves of the Crimson Dawn'),
(3230016,340723,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Mantle of the Crimson Dawn'),
(3230016,360748,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Graspers of Wrathgate'),
(3230016,380416,0,0,0,1,1,1,1,'Generated map_230_difficulty_0 boss_000245 | Vest of Scarlet Monastery');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9018 AND `Item` = 2010000340 AND `Reference` = 3230000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9018,2010000340,3230000,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000227');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8889 AND `Item` = 2010000341 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8889,2010000341,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8890 AND `Item` = 2010000342 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8890,2010000342,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8891 AND `Item` = 2010000343 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8891,2010000343,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8892 AND `Item` = 2010000344 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8892,2010000344,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8893 AND `Item` = 2010000345 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8893,2010000345,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8894 AND `Item` = 2010000346 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8894,2010000346,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8895 AND `Item` = 2010000347 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8895,2010000347,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8897 AND `Item` = 2010000348 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8897,2010000348,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8898 AND `Item` = 2010000349 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8898,2010000349,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8899 AND `Item` = 2010000350 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8899,2010000350,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8903 AND `Item` = 2010000351 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8903,2010000351,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8905 AND `Item` = 2010000352 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8905,2010000352,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8906 AND `Item` = 2010000353 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8906,2010000353,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8907 AND `Item` = 2010000354 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8907,2010000354,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8908 AND `Item` = 2010000355 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8908,2010000355,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8909 AND `Item` = 2010000356 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8909,2010000356,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8910 AND `Item` = 2010000357 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8910,2010000357,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8911 AND `Item` = 2010000358 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8911,2010000358,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8912 AND `Item` = 2010000359 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8912,2010000359,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8913 AND `Item` = 2010000360 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8913,2010000360,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8914 AND `Item` = 2010000361 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8914,2010000361,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8923 AND `Item` = 2010000362 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8923,2010000362,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8929 AND `Item` = 2010000363 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8929,2010000363,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9042 AND `Item` = 2010000364 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9042,2010000364,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9541 AND `Item` = 2010000365 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9541,2010000365,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9545 AND `Item` = 2010000366 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9545,2010000366,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9554 AND `Item` = 2010000367 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9554,2010000367,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9677 AND `Item` = 2010000368 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9677,2010000368,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9678 AND `Item` = 2010000369 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9678,2010000369,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9680 AND `Item` = 2010000370 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9680,2010000370,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9681 AND `Item` = 2010000371 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9681,2010000371,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9956 AND `Item` = 2010000372 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9956,2010000372,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10043 AND `Item` = 2010000373 AND `Reference` = 3230001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10043,2010000373,3230001,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9025 AND `Item` = 2010000374 AND `Reference` = 3230002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9025,2010000374,3230002,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000228');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9319 AND `Item` = 2010000375 AND `Reference` = 3230003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9319,2010000375,3230003,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000229');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9024 AND `Item` = 2010000376 AND `Reference` = 3230004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9024,2010000376,3230004,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000231');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9017 AND `Item` = 2010000377 AND `Reference` = 3230005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9017,2010000377,3230005,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000232');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9056 AND `Item` = 2010000378 AND `Reference` = 3230007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9056,2010000378,3230007,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000234');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9016 AND `Item` = 2010000379 AND `Reference` = 3230008;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9016,2010000379,3230008,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000235');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9033 AND `Item` = 2010000380 AND `Reference` = 3230009;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9033,2010000380,3230009,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000236');

DELETE FROM `creature_loot_template` WHERE `Entry` = 8983 AND `Item` = 2010000381 AND `Reference` = 3230010;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(8983,2010000381,3230010,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000237');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9502 AND `Item` = 2010000382 AND `Reference` = 3230012;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9502,2010000382,3230012,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000239');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9156 AND `Item` = 2010000383 AND `Reference` = 3230014;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9156,2010000383,3230014,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000242');

DELETE FROM `creature_loot_template` WHERE `Entry` = 9019 AND `Item` = 2010000384 AND `Reference` = 3230016;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(9019,2010000384,3230016,2,0,1,0,1,1,'Generated encounter attachment | map_230_difficulty_0 | boss_000245');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3240000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3240000,200694,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Girdle of Storm Forge'),
(3240000,220322,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Shadowcaller''s Greaves'),
(3240000,220394,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Titan-carved Gauntlets of the Ancient Pact'),
(3240000,220470,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | The Profane Legguards'),
(3240000,220789,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Medallion of the Stratholme'),
(3240000,220892,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Cuirass, Thunder Claw'),
(3240000,220952,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Pathfinder''s Wildbound Sabatons'),
(3240000,240015,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Rune Band, Spell Wyrm'),
(3240000,240029,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Aged Bone Crossbow of Iron Pact'),
(3240000,240130,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Gauntlets, Cold Gloom'),
(3240000,240359,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Shoulderguards, Mystic Void'),
(3240000,240600,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Dragonkeeper''s Bracers'),
(3240000,240654,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Soullord''s Battle Bow of the Grim King'),
(3240000,260427,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Wyrmforged Jerkin'),
(3240000,260849,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Hidden Vine Mask'),
(3240000,260919,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Bitter Steel Carapace'),
(3240000,260924,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Chilled Striders of the Void King'),
(3240000,260979,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Runestone of Ancestor Spirit'),
(3240000,280362,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Treads of Thor Modan'),
(3240000,280742,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Thundersteel Mantle of Second Dawn'),
(3240000,300102,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Legguards of the Dark Iron Clan'),
(3240000,300291,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Forsworn Helm of the Blighted Land'),
(3240000,300321,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Battle Girdle of the Ebon Crown'),
(3240000,300380,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Helm, Void Rime'),
(3240000,300500,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Blessed Greaves of Mage Lord'),
(3240000,300547,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Worldwarden''s Warhelm of the Silver Banner'),
(3240000,300550,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Deathforged Legplates'),
(3240000,300606,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Warhelm of the Runekeeper'),
(3240000,300628,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Plaguelord''s Scarab'),
(3240000,300646,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Boar Dawn Cloak'),
(3240000,300782,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Warplate of Titan Watcher'),
(3240000,300933,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | The Runic Girdle'),
(3240000,300949,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | The Stormscarred Coin'),
(3240000,320008,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | The Gravebound Walking Staff'),
(3240000,320163,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Silvered Idol, Wildkeeper''s Oath'),
(3240000,320807,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Heart, Spider Hex'),
(3240000,360204,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Legwraps of Wild King'),
(3240000,380261,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Witchbound Bindings'),
(3240000,380371,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Pathfinder''s Charm'),
(3240000,380570,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Jagged Pants'),
(3240000,380720,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Magekeeper''s Leggings'),
(3240000,380782,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Consecrated Walkers of Ebon Vanguard'),
(3240000,380792,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Warmaster''s Spellbound Chestguard'),
(3240000,380855,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Old Cinch of Tempest Keep'),
(3240000,380888,0,0,0,2,1,1,1,'Generated map_249_difficulty_1 boss_000707 | Windkeeper''s Silverblessed Hoop');

DELETE FROM `creature_loot_template` WHERE `Entry` = 36538 AND `Item` = 2010000385 AND `Reference` = 3240000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(36538,2010000385,3240000,2,0,2,0,1,1,'Generated encounter attachment | map_249_difficulty_1 | boss_000707');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3250000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3250000,220912,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | Plaguelord''s Gorget of the Wolf Spirit'),
(3250000,240648,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | Blood King''s Prayerbound Legmail'),
(3250000,260605,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | Shoulderpads of the Scarlet Dawn'),
(3250000,260988,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | The Crimson Waistband'),
(3250000,300075,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | Profane Longblade of Amberpine Lodge'),
(3250000,340158,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | Northkeeper''s Hood of the Mystic Gate'),
(3250000,360437,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | Stormcaller''s Mantle'),
(3250000,360765,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000452 | Thunderous Epaulets of Frozen Gate');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3250001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3250001,200186,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Cryptlord''s Great Cape'),
(3250001,200378,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Highblade, Azure Doom'),
(3250001,200407,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Firewarden''s War Leggings'),
(3250001,200806,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Witchlord''s Ivory Gauntlets'),
(3250001,220047,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Brittle Fingerband of Shadow Crown'),
(3250001,220099,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Nightwatcher''s Magebound Cleaver'),
(3250001,220344,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Vrykul Cuirass of Nesingwary Camp'),
(3250001,220400,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Wargrips of Ice Forge'),
(3250001,220616,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Earth Vault Medallion'),
(3250001,220678,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Rimelord''s Embersteel Greaves'),
(3250001,220976,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Runed Relic of Dawn Guard'),
(3250001,240036,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | The Snowbound Helm'),
(3250001,240309,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | The Thunderforged War Leggings'),
(3250001,240447,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | First Warden''s Siege Gun'),
(3250001,240464,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Dire Maw Shoulderguards'),
(3250001,240478,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | The Gilded Chainmail'),
(3250001,240510,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Dragonkeeper''s Legguards'),
(3250001,240672,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Charm of Final March'),
(3250001,240725,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Epaulets of the Frozen Pact'),
(3250001,240825,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Royal Band of the Ebon Banner'),
(3250001,240941,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Wind Reaver War Mantle'),
(3250001,240947,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Vambraces of Iron Council'),
(3250001,260032,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Iron Queen''s Circle'),
(3250001,260136,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Legguards of the Scarlet Watch'),
(3250001,260238,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Shadowwarden''s Carapace'),
(3250001,260552,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Shadowguard''s Burnished Stalkers'),
(3250001,260651,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Manaforged Falchion'),
(3250001,260790,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Warder Cloak of Star Grove'),
(3250001,260867,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Jerkin of the Ice Moon'),
(3250001,280087,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Firekeeper''s Robes'),
(3250001,280094,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Hood of the Scarlet Flame'),
(3250001,280143,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Grimlord''s Runehammer'),
(3250001,280210,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Headdress of the Star Grove'),
(3250001,280252,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Shadowwarden''s Patient Cuffs'),
(3250001,280374,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Steadfast Collar of Unending Watch'),
(3250001,280420,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Circlet of the Dragon Aspect'),
(3250001,280517,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Pale Lady''s Frostbitten Druid Staff'),
(3250001,280643,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Regalia of Lost Promise'),
(3250001,280683,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Dragoncaller''s Talisman'),
(3250001,300018,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Everfrost Handguards of the Silent King'),
(3250001,300058,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Warchief''s Tombbound Vambraces'),
(3250001,300171,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Waistplate, Gold Anchor'),
(3250001,300341,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Windcaller''s Deathmarked Sollerets'),
(3250001,300390,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | West Covenant Battlecloak'),
(3250001,300543,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | The Ironbound Signet'),
(3250001,300664,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Boneforged Effigy'),
(3250001,300711,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Stormbound Inscription'),
(3250001,300724,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Nightshrouded Signet Ring'),
(3250001,300745,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Magekeeper''s Handguards'),
(3250001,300761,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Grimkeeper''s Earthforged Badge'),
(3250001,320013,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Shadowcaller''s Warped Warbelt'),
(3250001,320089,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Sacred Gauntlets of the Titan Forge'),
(3250001,320500,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Waistguard of the Dragon Wastes'),
(3250001,320602,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Frostkeeper''s Coldhearted Runering'),
(3250001,320626,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Dreamkeeper''s Mail'),
(3250001,320798,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Northkeeper''s Figurine'),
(3250001,340142,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | The Wolfhide Vest'),
(3250001,340373,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Earthkeeper''s Shoulderpads'),
(3250001,340419,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Ravenbound Tiara of Wild Grove'),
(3250001,340463,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Skirt, Necro Bringerless'),
(3250001,340559,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Bloodmage''s Stave'),
(3250001,340621,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Frostguard''s Carved Graspers'),
(3250001,340771,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Plagueborn Cinch of Mount Hyjal'),
(3250001,340854,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Blood King''s Deathly Robe'),
(3250001,340893,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Brazen Sandals of Rainspeaker Canopy'),
(3250001,340967,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Trousers of Argent Tournament'),
(3250001,360067,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Stoneguard''s Handwraps'),
(3250001,360361,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Unwavering Gorget'),
(3250001,360403,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Northforged Shoulderpads'),
(3250001,360477,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Highguard''s Hoarfrost Boots'),
(3250001,360572,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Grey Shield Walkers'),
(3250001,360806,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Broken Warden''s Prayerbound Talisman'),
(3250001,360850,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Nightfang Whisper Runebands'),
(3250001,360994,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Voidlord''s Feathered Royal Cloak'),
(3250001,360996,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | The Dawnlit Boots'),
(3250001,380012,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Starbound Grips of Blood Crown'),
(3250001,380205,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Breeches, Twilight Root'),
(3250001,380208,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Harness, Soulfire Beacon'),
(3250001,380241,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Brassbound Jerkin'),
(3250001,380357,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Band of the Halls of Reflection'),
(3250001,380476,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Thunderforged Mark'),
(3250001,380560,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Cinch of the Bloodguard'),
(3250001,380580,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Goldsteel Helm'),
(3250001,380762,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Rootbound Seer Staff'),
(3250001,380823,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 trash | Ruthless Clutches of the Ulduar');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3250002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3250002,200341,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000453 | Sepulchral Longcloak'),
(3250002,280010,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000453 | War Mace of Silver Promise'),
(3250002,280497,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000453 | Northwind Graspers'),
(3250002,380411,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000453 | Warguard''s Wrap'),
(3250002,380607,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000453 | Burnished Cowl of the Dawn Light');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3250003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3250003,320425,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000454 | Sanctified War Mantle of the Wyrm Forge');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3250004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3250004,220474,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000455 | Frostveined Armplates of the New Agamand'),
(3250004,300015,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000455 | Footplates, South Rime'),
(3250004,320654,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000455 | Waistchain of Black Harvest');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3250006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3250006,240543,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000457 | Dragon Queen''s Mark'),
(3250006,360464,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000457 | Waistband of the Netherstorm'),
(3250006,380431,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000457 | Shoulderguards of the Rime Crown'),
(3250006,380969,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000457 | Stormscarred Trousers');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3250012;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3250012,220201,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000463 | The Silent Helm'),
(3250012,240423,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000463 | Fetish of the Ebon March'),
(3250012,260498,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000463 | Ashcaller''s Woe-bound Mask'),
(3250012,260907,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000463 | Lion Lament Footguards'),
(3250012,300746,0,0,0,1,1,1,1,'Generated map_289_difficulty_0 boss_000463 | Carved Relic, Bronze Vengeance');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10503 AND `Item` = 2010000386 AND `Reference` = 3250000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10503,2010000386,3250000,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | boss_000452');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10469 AND `Item` = 2010000387 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10469,2010000387,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10470 AND `Item` = 2010000388 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10470,2010000388,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10471 AND `Item` = 2010000389 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10471,2010000389,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10476 AND `Item` = 2010000390 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10476,2010000390,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10477 AND `Item` = 2010000391 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10477,2010000391,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10478 AND `Item` = 2010000392 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10478,2010000392,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10481 AND `Item` = 2010000393 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10481,2010000393,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10486 AND `Item` = 2010000394 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10486,2010000394,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10487 AND `Item` = 2010000395 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10487,2010000395,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10488 AND `Item` = 2010000396 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10488,2010000396,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10489 AND `Item` = 2010000397 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10489,2010000397,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10491 AND `Item` = 2010000398 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10491,2010000398,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10495 AND `Item` = 2010000399 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10495,2010000399,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10498 AND `Item` = 2010000400 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10498,2010000400,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10499 AND `Item` = 2010000401 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10499,2010000401,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10500 AND `Item` = 2010000402 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10500,2010000402,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11257 AND `Item` = 2010000403 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11257,2010000403,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11551 AND `Item` = 2010000404 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11551,2010000404,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11582 AND `Item` = 2010000405 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11582,2010000405,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14695 AND `Item` = 2010000406 AND `Reference` = 3250001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14695,2010000406,3250001,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11622 AND `Item` = 2010000407 AND `Reference` = 3250002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11622,2010000407,3250002,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | boss_000453');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10433 AND `Item` = 2010000408 AND `Reference` = 3250003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10433,2010000408,3250003,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | boss_000454');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10432 AND `Item` = 2010000409 AND `Reference` = 3250004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10432,2010000409,3250004,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | boss_000455');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10505 AND `Item` = 2010000410 AND `Reference` = 3250006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10505,2010000410,3250006,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | boss_000457');

DELETE FROM `creature_loot_template` WHERE `Entry` = 1853 AND `Item` = 2010000411 AND `Reference` = 3250012;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(1853,2010000411,3250012,2,0,1,0,1,1,'Generated encounter attachment | map_289_difficulty_0 | boss_000463');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270000,220001,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | The Conqueror Necklace'),
(3270000,220092,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Eternal Orb of the Storm Watch'),
(3270000,260029,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Lightlord''s Stalkers of the Broken Banner'),
(3270000,260067,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Northkeeper''s Whitegold Leggings'),
(3270000,280207,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Icewarden''s Vengeful Tablet'),
(3270000,280478,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Robes of Second Dawn'),
(3270000,280572,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Ghostkeeper''s Sunforged Mitts'),
(3270000,280751,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Starwarden''s Dragonforged Gemmed Band'),
(3270000,320042,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Mist Heart Rune'),
(3270000,320473,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | The Warborn Faceguard'),
(3270000,320488,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Drakebound Casque of the Holy Crown'),
(3270000,320795,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Neckchain of the Howling Wind'),
(3270000,380677,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000472 | Worldworn Bindings');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270001,200108,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Starkeeper''s Dusty Wargrips'),
(3270001,200111,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Warbelt of the Sable Crown'),
(3270001,200131,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Cabalistic Armplates, Darkrider''s Oath'),
(3270001,200408,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Permafrost Backcloth of Dread Host'),
(3270001,220114,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | The Forgotten Royal Band'),
(3270001,220548,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | The Defiant Waistplate'),
(3270001,220949,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Wyrmcaller''s Battle Girdle'),
(3270001,240155,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Serrated Dragon Spear of the Ancient Oak'),
(3270001,240181,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Dark Dream Coil'),
(3270001,240222,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Azure Waistchain of the Great Hunt'),
(3270001,260013,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Dawnkeeper''s Spaulders of the Bone Throne'),
(3270001,260332,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Grim Seal of the Halls of Stone'),
(3270001,280275,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Night Ice Boots'),
(3270001,280410,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Wintercaller''s Tombbound Ring'),
(3270001,280562,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Handwraps of Golden King'),
(3270001,300181,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Nightlord''s Battleplate of the Titan Forge'),
(3270001,300398,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Burnished Greatcloak of Iron Dwarf'),
(3270001,300466,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Wolfheart Sorrow Ritual Relic'),
(3270001,300478,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Runelord''s Vigilant Greatblade'),
(3270001,300687,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Magekeeper''s Locket'),
(3270001,300695,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Frost Queen''s Ironclad Gauntlets'),
(3270001,300948,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Celestial Drape of Wolf Spirit'),
(3270001,320281,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Warlord Vambraces, Mooncaller''s Oath'),
(3270001,320599,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Deathknight''s Leggings'),
(3270001,320869,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Harness of Silver Light'),
(3270001,320979,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Ghostcaller''s Girdle of the Rune Forge'),
(3270001,340289,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Talisman of the Wyrmskull'),
(3270001,340309,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Unquiet Great Stave, Windkeeper''s Oath'),
(3270001,340392,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Battleworn Waistwrap of the Broken Promise'),
(3270001,340513,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Serrated Shoulderwraps'),
(3270001,340657,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Runemaster''s Effigy'),
(3270001,340800,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Corroded Treads'),
(3270001,360036,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Windbound Trousers of Holy Flame'),
(3270001,360121,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Epaulets of Ancient Grove'),
(3270001,360463,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Moonwarden''s Cuffs'),
(3270001,360509,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | War Sword of Ice King'),
(3270001,360677,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Frostlord''s Crimson Cinch'),
(3270001,360787,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Gray Cold Epaulets'),
(3270001,360902,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Ashen Lord''s Regalia'),
(3270001,380258,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Neckguard of the Emerald Grove'),
(3270001,380585,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Headguard of Burning Shadow'),
(3270001,380718,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | Carapace of Silent Crypt'),
(3270001,380926,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 trash | The Thunderforged Harness');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270002,220571,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000473 | Skullcrusher, Soulshard Shot'),
(3270002,220665,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000473 | Nightsteel Shoulderplates of Pale King'),
(3270002,260583,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000473 | The Coal-black Strap'),
(3270002,340165,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000473 | Wristwraps of Dragon Rider'),
(3270002,340901,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000473 | Skirt of the Last Watch'),
(3270002,380391,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000473 | Helm of Ancient Storm'),
(3270002,380534,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000473 | Earthbound Wrap of Silent King');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270003,200883,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Witchkeeper''s Pauldrons'),
(3270003,220714,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Gemmed Band, Rime Glacier'),
(3270003,260858,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Deepfrost Legguards'),
(3270003,260956,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Grips of Water Spirit'),
(3270003,280849,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Valiant Spellwand'),
(3270003,300220,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Breastplate, Obsidian Cry'),
(3270003,320084,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Great Hauberk of Rime Watch'),
(3270003,320847,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Lost Warden''s Hammer'),
(3270003,360723,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Dreadforged Trousers of the Shattered Gate'),
(3270003,380210,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000474 | Kingsworn Legguards of Fire Spirit');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270004,200387,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | The Titan-carved War Pauldrons'),
(3270004,240324,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Starcaller''s Figurine of the Mount Hyjal'),
(3270004,240426,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Ironcaller''s Leggings of the Storm Peaks'),
(3270004,240928,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Blood Queen''s Surcoat'),
(3270004,260570,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Bear Verse Belt'),
(3270004,300388,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Dragonsteel Greaves of Thorim Arena'),
(3270004,300573,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Forsworn Waistguard of the Silver Watch'),
(3270004,320282,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | The Conqueror Mail'),
(3270004,340245,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Stormbound Vest of the Frenzyheart Hill'),
(3270004,340782,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Dreaming Neckchain'),
(3270004,340842,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000475 | Bloodstained Bone');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270005,260446,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000476 | The Thornwoven Strap'),
(3270005,280310,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000476 | Plaguekeeper''s Coil'),
(3270005,300659,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000476 | Cryptborn Faceguard of the Black Harvest'),
(3270005,320049,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000476 | Wildfire Scar Waistchain'),
(3270005,340070,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000476 | Rune Queen''s Solemn Bindings'),
(3270005,380647,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000476 | Wayfarer''s Oathforged Jerkin');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270006,200879,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000477 | War Leggings of the Deep Mountain'),
(3270006,360009,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000477 | First Queen''s Desecrated Cord');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270007,220096,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | High Rebuke Wrap'),
(3270007,240202,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | Surcoat of Dread Host'),
(3270007,240742,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | Traveling Cloak, Wind Hex'),
(3270007,260466,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | Capelet of the Blue Flame'),
(3270007,260531,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | The Devout Loop'),
(3270007,260753,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | Drakekeeper''s Choker of the Silent Road'),
(3270007,280557,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | The Lightbound Necklace'),
(3270007,320389,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | Grips of Shadow Vault'),
(3270007,360342,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | Breeches of the Terokkar'),
(3270007,360579,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000479 | Nightlord''s Sacred Robe');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270009;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270009,200898,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000481 | Ward of the Emerald Moon'),
(3270009,240444,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000481 | Warbelt of the Azure Moon'),
(3270009,260808,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000481 | Far Caller Mantle'),
(3270009,340082,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000481 | The Skullbound Sash'),
(3270009,340305,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000481 | Shieldbearer''s Sandals of the Shadow Moon'),
(3270009,340442,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000481 | Chestwrap of the Black Harvest'),
(3270009,360482,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000481 | Graven Treads, Frozen Keeper''s Oath');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270010;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270010,200017,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Blacksmith''s Ringlet'),
(3270010,200078,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | The Runewoven Scale'),
(3270010,220684,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | The Starforged Battleplate'),
(3270010,240513,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Graveborn Fingerband'),
(3270010,260361,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Mistbound Striders of Dalaran Watch'),
(3270010,260682,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Cowl of the Dark Moon'),
(3270010,280157,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Deathforged Vestments of the Void Flame'),
(3270010,280951,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Regalia of Crypt Lord'),
(3270010,300521,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Azure March Greathelm'),
(3270010,300773,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Bloodstained Battlehelm'),
(3270010,320725,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Last Knight''s Seal of the Coldarra'),
(3270010,340914,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Azure Wrath Handwraps'),
(3270010,340985,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | The Rimebound Wristwraps'),
(3270010,360101,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Diadem of the Ebon Pact'),
(3270010,360251,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Thorned Shiv'),
(3270010,380342,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 boss_000482 | Maul of the Deep Roads');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3270013;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3270013,200354,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 script_HandleBothDead | Pale Lady''s Wrap'),
(3270013,280321,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 script_HandleBothDead | Silent Keeper''s Manawoven Waistband'),
(3270013,280697,0,0,0,1,1,1,1,'Generated map_329_difficulty_0 script_HandleBothDead | Druid Staff of Howling Wind');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10516 AND `Item` = 2010000412 AND `Reference` = 3270000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10516,2010000412,3270000,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000472');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10381 AND `Item` = 2010000413 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10381,2010000413,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10382 AND `Item` = 2010000414 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10382,2010000414,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10384 AND `Item` = 2010000415 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10384,2010000415,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10385 AND `Item` = 2010000416 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10385,2010000416,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10390 AND `Item` = 2010000417 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10390,2010000417,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10391 AND `Item` = 2010000418 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10391,2010000418,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10393 AND `Item` = 2010000419 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10393,2010000419,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10398 AND `Item` = 2010000420 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10398,2010000420,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10399 AND `Item` = 2010000421 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10399,2010000421,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10400 AND `Item` = 2010000422 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10400,2010000422,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10405 AND `Item` = 2010000423 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10405,2010000423,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10406 AND `Item` = 2010000424 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10406,2010000424,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10407 AND `Item` = 2010000425 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10407,2010000425,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10408 AND `Item` = 2010000426 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10408,2010000426,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10409 AND `Item` = 2010000427 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10409,2010000427,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10412 AND `Item` = 2010000428 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10412,2010000428,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10413 AND `Item` = 2010000429 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10413,2010000429,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10414 AND `Item` = 2010000430 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10414,2010000430,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10416 AND `Item` = 2010000431 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10416,2010000431,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10417 AND `Item` = 2010000432 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10417,2010000432,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10418 AND `Item` = 2010000433 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10418,2010000433,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10419 AND `Item` = 2010000434 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10419,2010000434,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10420 AND `Item` = 2010000435 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10420,2010000435,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10421 AND `Item` = 2010000436 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10421,2010000436,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10422 AND `Item` = 2010000437 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10422,2010000437,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10423 AND `Item` = 2010000438 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10423,2010000438,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10424 AND `Item` = 2010000439 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10424,2010000439,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10425 AND `Item` = 2010000440 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10425,2010000440,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10426 AND `Item` = 2010000441 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10426,2010000441,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10463 AND `Item` = 2010000442 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10463,2010000442,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10464 AND `Item` = 2010000443 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10464,2010000443,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10809 AND `Item` = 2010000444 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10809,2010000444,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11043 AND `Item` = 2010000445 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11043,2010000445,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14684 AND `Item` = 2010000446 AND `Reference` = 3270001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14684,2010000446,3270001,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10558 AND `Item` = 2010000447 AND `Reference` = 3270002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10558,2010000447,3270002,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000473');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10808 AND `Item` = 2010000448 AND `Reference` = 3270003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10808,2010000448,3270003,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000474');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10997 AND `Item` = 2010000449 AND `Reference` = 3270004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10997,2010000449,3270004,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000475');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11032 AND `Item` = 2010000450 AND `Reference` = 3270005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11032,2010000450,3270005,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000476');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10811 AND `Item` = 2010000451 AND `Reference` = 3270006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10811,2010000451,3270006,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000477');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10436 AND `Item` = 2010000452 AND `Reference` = 3270007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10436,2010000452,3270007,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000479');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10438 AND `Item` = 2010000453 AND `Reference` = 3270009;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10438,2010000453,3270009,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000481');

DELETE FROM `creature_loot_template` WHERE `Entry` = 10435 AND `Item` = 2010000454 AND `Reference` = 3270010;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(10435,2010000454,3270010,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | boss_000482');

DELETE FROM `gameobject_loot_template` WHERE `Entry` = 17919 AND `Item` = 2010000455 AND `Reference` = 3270013;

INSERT INTO `gameobject_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(17919,2010000455,3270013,2,0,1,0,1,1,'Generated encounter attachment | map_329_difficulty_0 | script_HandleBothDead');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3280000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3280000,220562,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | The Titanbound Sabatons'),
(3280000,240550,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | Bone Bow, Fierce Keeper'),
(3280000,240607,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | Ebon Knight''s Bracers of the Frost Watch'),
(3280000,260158,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | Winter King''s Timeworn Wristbands'),
(3280000,280204,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | Star Wand, Dire Whisper'),
(3280000,280386,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | Warmaster''s Hood'),
(3280000,320151,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | Shoulderguards of Scourge Lord'),
(3280000,360521,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000422 | Baleful Footwraps of Wild Watch');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3280003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3280003,220844,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000424 | Dragonkeeper''s Cryptborn Gauntlets'),
(3280003,280512,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000424 | Star Wand of Broken Hall'),
(3280003,280527,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000424 | Stonefather''s Stoic Shoulderpads'),
(3280003,320481,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000424 | Dreamkeeper''s Cursed Wrist Chains'),
(3280003,320897,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000424 | Boots of the Moon Pact'),
(3280003,360531,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000424 | Dreadbound Capelet of Midnight Watch'),
(3280003,380523,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000424 | Warlord''s Brutal Headguard');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3280004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3280004,220007,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Gravebound Shoulderplates'),
(3280004,220945,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | The Frostforged Armplates'),
(3280004,260065,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Shadowsteel Strap, Stonefather''s Oath'),
(3280004,320017,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Iron King''s Belt'),
(3280004,320055,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Longstaff, Forge Watch'),
(3280004,340531,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Old Warden''s Runeforged Beads'),
(3280004,340874,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Obsidian Lord Runewand'),
(3280004,360523,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Crimson Shoulder Cape of the Rune Forge'),
(3280004,380177,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000425 | Scepter of the Wind Crown');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3280005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3280005,200520,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000426 | Relentless Legplates'),
(3280005,240238,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000426 | The Thundersteel Chestguard'),
(3280005,260970,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000426 | The Carrion Bindings'),
(3280005,340328,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000426 | Voidlord''s Thundersteel Footwraps'),
(3280005,340883,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000426 | Pale Cuffs of the Nagrand'),
(3280005,340958,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000426 | Amulet of Hellfire Citadel');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3280008;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3280008,200637,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Dreadforged Royal Band'),
(3280008,220140,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Hateful Rampart'),
(3280008,220537,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Warbelt of North Road'),
(3280008,220561,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Frostkeeper''s Kingsworn Vambraces'),
(3280008,240773,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Stormguard''s Shoulderguards'),
(3280008,340786,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Handwraps of the Argent Crusade'),
(3280008,360188,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Bearhide Emblem of the Lich King'),
(3280008,380209,0,0,0,1,1,1,1,'Generated map_349_difficulty_0 boss_000429 | Waistguard, Storm Shade');

DELETE FROM `creature_loot_template` WHERE `Entry` = 13282 AND `Item` = 2010000456 AND `Reference` = 3280000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(13282,2010000456,3280000,2,0,1,0,1,1,'Generated encounter attachment | map_349_difficulty_0 | boss_000422');

DELETE FROM `creature_loot_template` WHERE `Entry` = 12236 AND `Item` = 2010000457 AND `Reference` = 3280003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(12236,2010000457,3280003,2,0,1,0,1,1,'Generated encounter attachment | map_349_difficulty_0 | boss_000424');

DELETE FROM `creature_loot_template` WHERE `Entry` = 12225 AND `Item` = 2010000458 AND `Reference` = 3280004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(12225,2010000458,3280004,2,0,1,0,1,1,'Generated encounter attachment | map_349_difficulty_0 | boss_000425');

DELETE FROM `creature_loot_template` WHERE `Entry` = 12203 AND `Item` = 2010000459 AND `Reference` = 3280005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(12203,2010000459,3280005,2,0,1,0,1,1,'Generated encounter attachment | map_349_difficulty_0 | boss_000426');

DELETE FROM `creature_loot_template` WHERE `Entry` = 12201 AND `Item` = 2010000460 AND `Reference` = 3280008;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(12201,2010000460,3280008,2,0,1,0,1,1,'Generated encounter attachment | map_349_difficulty_0 | boss_000429');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3290000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3290000,240312,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Ebon Nightcloak of the Bronze Dragon'),
(3290000,240802,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Warden Bow of Arcane Moon'),
(3290000,260741,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Brittle Cinch of the Deep Forge'),
(3290000,260781,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Warband of the Thunder Watch'),
(3290000,280986,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Bloodied Cap of the Burning Sky'),
(3290000,360061,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Dreadforged Binding'),
(3290000,360167,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Ethereal Chestwrap'),
(3290000,360916,0,0,0,1,1,1,1,'Generated map_389_difficulty_0 boss_000431 | Bloodmarked Vestments of the Dark Forge');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11520 AND `Item` = 2010000461 AND `Reference` = 3290000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11520,2010000461,3290000,2,0,1,0,1,1,'Generated encounter attachment | map_389_difficulty_0 | boss_000431');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310000,220906,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000343 | Conqueror Helm of the Hidden Path'),
(3310000,380190,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000343 | Trousers, Fallen Sorrow');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310001,200015,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Soullord''s Torc of the Wild Pact'),
(3310001,200047,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Shoulderplates of Warsong Clan'),
(3310001,200191,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Clouded Warplate of Scarlet Banner'),
(3310001,200239,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Visor of Last Dawn'),
(3310001,200246,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Windcaller''s Pauldrons'),
(3310001,200299,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Handplates of Wild Heart'),
(3310001,200414,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Fierce Handplates'),
(3310001,200449,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Gold Chain Footplates'),
(3310001,200479,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Bracers of Tempest Keep'),
(3310001,200522,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Graveforged Warplate'),
(3310001,200538,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Dragonsteel Warbelt of the Broken Banner'),
(3310001,200561,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Mana Anchor Great Gauntlets'),
(3310001,200575,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Nameless Chestplate of Winter Memory'),
(3310001,200589,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Battleplate of Arcane Eye'),
(3310001,200597,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Violet Legguards'),
(3310001,200616,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Shattered Legguards'),
(3310001,200680,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Forgekeeper''s Steelforged Fingerband'),
(3310001,200799,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ironwarden''s Barbed Greathelm'),
(3310001,200975,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Feathered War Leggings of Winter Forge'),
(3310001,220117,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Charm, Prime Tongue'),
(3310001,220224,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Furious Nightcloak of the Void Crown'),
(3310001,220249,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Engraved Brooch of the Void King'),
(3310001,220266,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Warbelt of the Grim Host'),
(3310001,220279,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Breastplate, Dawn Claw'),
(3310001,220282,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Dragonbound Headplate of the Fel Flame'),
(3310001,220342,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Arctic Grand Mace'),
(3310001,220461,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Kingsworn Shoulderplates of Earth Spirit'),
(3310001,220773,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Sunkeeper''s War Pauldrons'),
(3310001,220779,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Spellforged Rider Blade'),
(3310001,220975,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Winterborn Handplates'),
(3310001,240051,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Great Hauberk, Eagle Briar'),
(3310001,240079,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Lion Wing Horn'),
(3310001,240105,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Thornwoven Seal of the Silver Covenant'),
(3310001,240114,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Rimeforged Greaves, Dawnkeeper''s Oath'),
(3310001,240135,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Dragonstalker''s Dragonbound Legmail'),
(3310001,240174,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Fire Wrath Shoulder Guards'),
(3310001,240275,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Warped War Leggings'),
(3310001,240364,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Burnished Warbelt, Spellbinder''s Oath'),
(3310001,240440,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Defiant Chausses of the Forge of Souls'),
(3310001,240534,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Deathcaller''s Shoulder Guards'),
(3310001,240815,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Argent Champion''s Rifle of the Grim King'),
(3310001,240868,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Treads, Bone Shard'),
(3310001,260000,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Pants of the Wild Grove'),
(3310001,260105,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Handguards of the Silver Dawn'),
(3310001,260107,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ivory Grips of Great Hunt'),
(3310001,260133,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Rimeforged Amulet'),
(3310001,260351,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Frozen Shoulderpads of the Hidden Path'),
(3310001,260408,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Adamant Rune Dagger'),
(3310001,260813,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Wildfire Veil Mask'),
(3310001,260820,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Embersteel Oathring'),
(3310001,260975,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Spellforged Armguards of the Storm Peaks'),
(3310001,260981,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Wolfsworn Mark'),
(3310001,280022,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Royal Cloak of the Pale Crown'),
(3310001,280063,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Mitts of Zim Torga'),
(3310001,280099,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Black Wolf Vest'),
(3310001,280111,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ancient King''s Wyrmhide Robe'),
(3310001,280125,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Footwraps, High Ice'),
(3310001,280149,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Solemn Legwraps of the Black Ice'),
(3310001,280151,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Twilight-forged Mark of Shadow Crown'),
(3310001,280291,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Bracelets, Shadow Winter'),
(3310001,280322,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Plaguetouched Pendant Chain of Storm Forge'),
(3310001,280336,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Mitts of Void Flame'),
(3310001,280468,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Emberkeeper''s Sunforged Collar'),
(3310001,280499,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Cinch, Serpent Wall'),
(3310001,280561,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Bonebound Footwraps of the Stone Watch'),
(3310001,280605,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Robes, Earthshard Cold'),
(3310001,300026,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Backcloth of the Dalaran Watch'),
(3310001,300062,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | First King''s Mirror of the Frozen Promise'),
(3310001,300079,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Stormforged Charmstone of the Corpse Scar'),
(3310001,300142,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ancient Relic of the Moon Flame'),
(3310001,300146,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Emerald Star Neckchain'),
(3310001,300185,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Last Keeper''s Stormforged Battlecloak'),
(3310001,300269,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Great Pauldrons of the Storm Crown'),
(3310001,300459,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Warplate of the Khaz Modan'),
(3310001,300563,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Iron Boots of Conquest Hold'),
(3310001,300604,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Sunfire Decree Breastplate'),
(3310001,300625,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Bonekeeper''s Girdle of the Crimson Watch'),
(3310001,300679,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Sunsteel Breastplate of Rune King'),
(3310001,300680,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Grim Waistguard'),
(3310001,300772,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Primeval Greaves'),
(3310001,300874,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Wolfsworn Armguards'),
(3310001,300915,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Great Claymore of the Winter Forge'),
(3310001,320105,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Hoarfrost Epaulets of Dark Forge'),
(3310001,320304,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Furious Warboots'),
(3310001,320339,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Leafwoven Symbol'),
(3310001,320391,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Mournful Legguards'),
(3310001,320409,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Hauberk of the Northwatch'),
(3310001,320531,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Violet Keeper''s Lightblessed Wargrips'),
(3310001,320823,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Magekeeper''s War Mantle'),
(3310001,320945,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Shadowguard''s Battlecloak'),
(3310001,340017,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Heroic Breeches'),
(3310001,340039,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Wolfwarden''s Pants'),
(3310001,340182,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Dawnwarden''s Breeches'),
(3310001,340219,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Runesmith''s Flask'),
(3310001,340283,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Dreamwoven Runed Staff of Hallowed Oath'),
(3310001,340356,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Legwraps, Mana Roar'),
(3310001,340364,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Lost Queen''s Treads of the Ice King'),
(3310001,340399,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Blood Prince''s Necklace'),
(3310001,340471,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Enchanted Breeches'),
(3310001,340653,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ring of Broken Crown'),
(3310001,340768,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Choker of the Plague Watch'),
(3310001,340789,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Amulet of the Kamagua'),
(3310001,340816,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Diadem of Death Lord'),
(3310001,340840,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Pendant Chain of the Frozen Forge'),
(3310001,340973,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Baleful Cord'),
(3310001,340984,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Fearsome Torque of the Wyrmrest'),
(3310001,360026,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Scourgeforged Seal of the Fel Ritual'),
(3310001,360105,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Frozen Queen''s Manaforged Rune Band'),
(3310001,360136,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Golden Grips of Dragon Forge'),
(3310001,360193,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Deathwarden''s Kilt of the Winter Crown'),
(3310001,360220,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Shroud, Dread Anvil'),
(3310001,360283,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Violet Guardian''s Loop of the Endless Road'),
(3310001,360334,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Cloak of Distant Memory'),
(3310001,360484,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Trousers, Cold Brand'),
(3310001,360520,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Mystwoven Treads of Shadowbinder'),
(3310001,360529,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Snowbound Shroud, Deathwarden''s Oath'),
(3310001,360537,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Icecaller''s Veil'),
(3310001,360615,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Runestone, Skull Caller'),
(3310001,360733,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Northman''s Frostbound Cord'),
(3310001,360990,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ancient King''s Mantle'),
(3310001,380017,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Ironbound Spaulders'),
(3310001,380096,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Nightsteel Totem of Mount Hyjal'),
(3310001,380198,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Argent Templar''s Primeval Treads'),
(3310001,380298,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Lion Verse Headdress'),
(3310001,380307,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Carrion Armguards of Golden Dawn'),
(3310001,380308,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Tombbound Headguard of the Star Crown'),
(3310001,380368,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ancient King''s Carrion Pendant'),
(3310001,380642,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Shoulderguards, Obsidian Torment'),
(3310001,380658,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Tunic, Spell Decree'),
(3310001,380707,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Holy Headguard'),
(3310001,380715,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Ebon Waistband'),
(3310001,380858,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | The Pale Helm'),
(3310001,380943,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Gilded Rune Band'),
(3310001,380994,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 trash | Darksteel Inscription of Wyrm Queen');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310004,220281,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000346 | Vanguard''s Handguards of the Crypt Watch'),
(3310004,240081,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000346 | Belt, Night Ray'),
(3310004,360152,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000346 | Mournbound Breeches of Fel Ritual');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310005,220807,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000347 | Iron Boots, Ancient Glyph'),
(3310005,240703,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000347 | Argent Champion''s War Mantle');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310006,200876,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000348 | Brittle Great Pauldrons, Soullord''s Oath'),
(3310006,220192,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000348 | Battleplate, Shield Fang'),
(3310006,240791,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000348 | Loop, Ghost Warden'),
(3310006,300541,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000348 | The Nightshrouded Handguards'),
(3310006,340086,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000348 | The Moonbound Footwraps'),
(3310006,360053,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000348 | Thunderlord''s Cinch of the Dawn Star');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310008;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310008,220692,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000350 | Sun Queen''s Cabalistic Gorget'),
(3310008,300274,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000350 | Warplate of the Broken Blade');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310010;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310010,240634,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000362 | Boots, Sun Voice'),
(3310010,360064,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000362 | Last Scream Leggings');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310011;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310011,200395,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000364 | Wristplates of the Searing Gorge'),
(3310011,200424,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000364 | Frostforged Oathring'),
(3310011,340649,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000364 | The Wintertouched Circlet');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3310013;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3310013,280411,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000366 | Battlemaiden''s Sandals'),
(3310013,380235,0,0,0,1,1,1,1,'Generated map_429_difficulty_0 boss_000366 | Austere Coil of the Bloodguard');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11490 AND `Item` = 2010000462 AND `Reference` = 3310000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11490,2010000462,3310000,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000343');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11451 AND `Item` = 2010000463 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11451,2010000463,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11452 AND `Item` = 2010000464 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11452,2010000464,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11453 AND `Item` = 2010000465 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11453,2010000465,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11454 AND `Item` = 2010000466 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11454,2010000466,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11455 AND `Item` = 2010000467 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11455,2010000467,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11456 AND `Item` = 2010000468 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11456,2010000468,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11457 AND `Item` = 2010000469 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11457,2010000469,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11458 AND `Item` = 2010000470 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11458,2010000470,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11459 AND `Item` = 2010000471 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11459,2010000471,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11462 AND `Item` = 2010000472 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11462,2010000472,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11464 AND `Item` = 2010000473 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11464,2010000473,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11467 AND `Item` = 2010000474 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11467,2010000474,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11469 AND `Item` = 2010000475 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11469,2010000475,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11470 AND `Item` = 2010000476 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11470,2010000476,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11471 AND `Item` = 2010000477 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11471,2010000477,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11472 AND `Item` = 2010000478 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11472,2010000478,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11473 AND `Item` = 2010000479 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11473,2010000479,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11475 AND `Item` = 2010000480 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11475,2010000480,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11480 AND `Item` = 2010000481 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11480,2010000481,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11483 AND `Item` = 2010000482 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11483,2010000482,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11484 AND `Item` = 2010000483 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11484,2010000483,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 13021 AND `Item` = 2010000484 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(13021,2010000484,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 13036 AND `Item` = 2010000485 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(13036,2010000485,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 13196 AND `Item` = 2010000486 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(13196,2010000486,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14303 AND `Item` = 2010000487 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14303,2010000487,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14349 AND `Item` = 2010000488 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14349,2010000488,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14398 AND `Item` = 2010000489 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14398,2010000489,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14399 AND `Item` = 2010000490 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14399,2010000490,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14690 AND `Item` = 2010000491 AND `Reference` = 3310001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14690,2010000491,3310001,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11492 AND `Item` = 2010000492 AND `Reference` = 3310004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11492,2010000492,3310004,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000346');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11488 AND `Item` = 2010000493 AND `Reference` = 3310005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11488,2010000493,3310005,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000347');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11487 AND `Item` = 2010000494 AND `Reference` = 3310006;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11487,2010000494,3310006,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000348');

DELETE FROM `creature_loot_template` WHERE `Entry` = 11489 AND `Item` = 2010000495 AND `Reference` = 3310008;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(11489,2010000495,3310008,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000350');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14326 AND `Item` = 2010000496 AND `Reference` = 3310010;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14326,2010000496,3310010,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000362');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14321 AND `Item` = 2010000497 AND `Reference` = 3310011;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14321,2010000497,3310011,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000364');

DELETE FROM `creature_loot_template` WHERE `Entry` = 14325 AND `Item` = 2010000498 AND `Reference` = 3310013;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(14325,2010000498,3310013,2,0,1,0,1,1,'Generated encounter attachment | map_429_difficulty_0 | boss_000366');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3340007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3340007,200562,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Titanic Great Gauntlets of the Gjalerbron'),
(3340007,220150,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Leafwoven Sabatons of the Northern Forge'),
(3340007,220260,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Gauntlets of the Endless Path'),
(3340007,220280,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Traveling Cloak, Moonfire Helm'),
(3340007,220339,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Unquiet War Pauldrons of Ancient Banner'),
(3340007,220395,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Great Pauldrons, Frozen Song'),
(3340007,220626,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Duskcaller''s Sollerets of the Black Anvil'),
(3340007,220791,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | The Wintertouched Carapace'),
(3340007,220960,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Footplates of the Holy Guard'),
(3340007,240102,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Boots, Rune Branch'),
(3340007,240296,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Warbelt of Scarlet Banner'),
(3340007,240360,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Waistguard of the Black Flight'),
(3340007,240821,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Drape of Ebon Blade'),
(3340007,280133,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Runelord''s Beads of the Hearthguard'),
(3340007,280366,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Cinch, Astral Doom'),
(3340007,280542,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Stoic Shroud'),
(3340007,300092,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Embersteel Gauntlets'),
(3340007,300324,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Greathelm, Coldfire Snow'),
(3340007,300584,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Pendant of the Emerald Path'),
(3340007,300770,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Inscription, Dream Spire'),
(3340007,340241,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Clasp of the Grim Host'),
(3340007,340572,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Faithful Bodkin of the Void Crown'),
(3340007,340703,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Adamant Trousers'),
(3340007,340995,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Thunderkeeper''s Cord'),
(3340007,360110,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Mantle of Silver Hand'),
(3340007,360490,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Shadowkeeper''s Beads'),
(3340007,360504,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Scale of the Stormcaller'),
(3340007,360525,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Amulet of the Scarlet Keep'),
(3340007,380034,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Legwraps, Night Thorn'),
(3340007,380244,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Arcanized Leggings of Lich King'),
(3340007,380426,0,0,0,1,1,1,1,'Generated map_531_difficulty_0 boss_000717 | Silent King''s Torque of the Silver Crown');

DELETE FROM `creature_loot_template` WHERE `Entry` = 15727 AND `Item` = 2010000499 AND `Reference` = 3340007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(15727,2010000499,3340007,2,0,1,0,1,1,'Generated encounter attachment | map_531_difficulty_0 | boss_000717');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3360005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3360005,200995,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000685 | The Twilight Scale'),
(3360005,300615,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000685 | Permafrost Armguards of Silver Dawn'),
(3360005,340781,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000685 | Starfire Grip Armbands'),
(3360005,380225,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000685 | Mirror of Bone Ritual');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3360013;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3360013,220217,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Greaves of the Wyrm Crown'),
(3360013,240232,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Wyrmguard''s Sunsteel Chausses'),
(3360013,240481,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Wristguards, Silver Storm'),
(3360013,240840,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | The Stormsteel Torque'),
(3360013,260234,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | First Queen''s Wristguards'),
(3360013,260518,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Carrion Belt of the Frozen Moon'),
(3360013,300086,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Tombkeeper''s Warplate of the River Heart'),
(3360013,300087,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Winterwarden''s Siegebound Vambraces'),
(3360013,300219,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Stonefather''s Dawnlit Thunder Hammer'),
(3360013,300314,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Frostguard''s Waistplate of the Stone King'),
(3360013,300337,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Northwarden''s Blackened Charmstone'),
(3360013,300530,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Ebon Marshal''s Fernwoven Armplates'),
(3360013,300652,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Tomahawk of the Death Knight'),
(3360013,300801,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | The Arcane Wristplates'),
(3360013,300825,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Chestplate of Rime Crown'),
(3360013,320091,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Steelbound Circle of Winter Crown'),
(3360013,320136,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Runeforged Wargrips'),
(3360013,320787,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Baleful Boots of First King'),
(3360013,340250,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Ravenlord''s Runewand of the Iron Banner'),
(3360013,340273,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Spellstaff, Forge Vengeance'),
(3360013,340292,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Void Talon Band'),
(3360013,380163,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Shattered Piercer Warband'),
(3360013,380215,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Windcaller''s Pants'),
(3360013,380821,0,0,0,1,1,1,1,'Generated map_533_difficulty_0 boss_000704 | Armguards of the Silver Promise');

DELETE FROM `creature_loot_template` WHERE `Entry` = 16011 AND `Item` = 2010000500 AND `Reference` = 3360005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(16011,2010000500,3360005,2,0,1,0,1,1,'Generated encounter attachment | map_533_difficulty_0 | boss_000685');

DELETE FROM `creature_loot_template` WHERE `Entry` = 15990 AND `Item` = 2010000501 AND `Reference` = 3360013;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(15990,2010000501,3360013,2,0,1,0,1,1,'Generated encounter attachment | map_533_difficulty_0 | boss_000704');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3370000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3370000,200147,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Silver Freeze Wristplates'),
(3370000,200199,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | The Stormsteel Pauldrons'),
(3370000,200282,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Gauntlets of the Last Vigil'),
(3370000,220805,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Wintertouched Charmstone'),
(3370000,240507,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Wintercaller''s Great Cape'),
(3370000,240671,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Moonwarden''s Starlit Leggings'),
(3370000,240726,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | The Tarnished Chausses'),
(3370000,240745,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | South Wake Dwarven Rifle'),
(3370000,260111,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Violet Guardian''s Hallowed Cap'),
(3370000,260321,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Duskwarden''s Dragonbound Brooch'),
(3370000,260468,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Soulfire Flame Cinch'),
(3370000,260751,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Breeches, Crypt Feather'),
(3370000,260866,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Rune Band of Ebon Blade'),
(3370000,280266,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Warcaller''s Northforged Mantle'),
(3370000,280498,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Grips of the Frozen Forge'),
(3370000,280519,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Bindings of the Ebon Watch'),
(3370000,280685,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Binding of Sons of Hodir'),
(3370000,280852,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Battlesage''s Leggings of the Rune Forge'),
(3370000,300140,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Moon Queen''s Manaforged Keepsake'),
(3370000,300155,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Forge Spire Choker'),
(3370000,300176,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Pitiless Carapace'),
(3370000,300197,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Spirit Anchor Chestplate'),
(3370000,300240,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Iron Boots of Final March'),
(3370000,300299,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Greaves of the Forgotten Oath'),
(3370000,300363,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Ashen King''s Greaves of the Titan Archive'),
(3370000,300386,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Armplates of the Arathi Highlands'),
(3370000,300391,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | War Pauldrons of Blood Moon'),
(3370000,300485,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Stonelord''s Cuirass'),
(3370000,300712,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | War Sword, Stormshard Dream'),
(3370000,300869,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Emerald Rage Torc'),
(3370000,340859,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Haunted Footwraps'),
(3370000,360551,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Headdress of the Wyrm Watch'),
(3370000,360659,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | Baleful Shoulder Cape of Mana Tide'),
(3370000,380965,0,0,0,2,1,1,1,'Generated map_533_difficulty_1 boss_000673 | The Twilight-forged Headguard');

DELETE FROM `creature_loot_template` WHERE `Entry` = 29249 AND `Item` = 2010000502 AND `Reference` = 3370000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(29249,2010000502,3370000,2,0,2,0,1,1,'Generated encounter attachment | map_533_difficulty_1 | boss_000673');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3390000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3390000,220085,0,0,0,1,1,1,1,'Generated map_540_difficulty_0 boss_000407 | Death Brand Gemmed Band'),
(3390000,300303,0,0,0,1,1,1,1,'Generated map_540_difficulty_0 boss_000407 | Neckguard, Drake Howl'),
(3390000,300862,0,0,0,1,1,1,1,'Generated map_540_difficulty_0 boss_000407 | Battleplate Legguards, Necro Claw'),
(3390000,320179,0,0,0,1,1,1,1,'Generated map_540_difficulty_0 boss_000407 | Boots, Green Vigil');

DELETE FROM `creature_loot_template` WHERE `Entry` = 16807 AND `Item` = 2010000503 AND `Reference` = 3390000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(16807,2010000503,3390000,2,0,1,0,1,1,'Generated encounter attachment | map_540_difficulty_0 | boss_000407');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3400000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3400000,220337,0,0,0,2,1,1,1,'Generated map_540_difficulty_1 boss_000407 | Thornbound Helm of the Golden Dawn'),
(3400000,240684,0,0,0,2,1,1,1,'Generated map_540_difficulty_1 boss_000407 | Solemn Shoulder Guards'),
(3400000,260109,0,0,0,2,1,1,1,'Generated map_540_difficulty_1 boss_000407 | Frozen Heart Wristbands'),
(3400000,320761,0,0,0,2,1,1,1,'Generated map_540_difficulty_1 boss_000407 | Celestial Glaive War Leggings'),
(3400000,340894,0,0,0,2,1,1,1,'Generated map_540_difficulty_1 boss_000407 | The Jagged Spellstaff'),
(3400000,380443,0,0,0,2,1,1,1,'Generated map_540_difficulty_1 boss_000407 | Amulet of the Green Dragon');

DELETE FROM `creature_loot_template` WHERE `Entry` = 20568 AND `Item` = 2010000504 AND `Reference` = 3400000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(20568,2010000504,3400000,2,0,2,0,1,1,'Generated encounter attachment | map_540_difficulty_1 | boss_000407');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3420002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3420002,220169,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Greathelm of Khaz Modan'),
(3420002,240903,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Boots, Star Branch'),
(3420002,300710,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Waistplate of Ironforge Mountain'),
(3420002,340321,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Deathguard''s Brutish Sandals'),
(3420002,340752,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Bloodfire Crown Gloves'),
(3420002,360911,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Twilightkeeper''s Waistband'),
(3420002,380818,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Hardened Footguards'),
(3420002,380971,0,0,0,2,1,1,1,'Generated map_542_difficulty_1 boss_000405 | Walkers of Crimson Crown');

DELETE FROM `creature_loot_template` WHERE `Entry` = 18607 AND `Item` = 2010000505 AND `Reference` = 3420002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(18607,2010000505,3420002,2,0,2,0,1,1,'Generated encounter attachment | map_542_difficulty_1 | boss_000405');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3440001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3440001,200626,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Blackguard''s Vial of the Mount Hyjal'),
(3440001,200996,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Iron Boots of Ancient Storm'),
(3440001,220234,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Battleplate Legguards of Frozen Forge'),
(3440001,220530,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Shattered Decree Mirror'),
(3440001,220703,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Boneforged Armplates, Old Keeper''s Oath'),
(3440001,240588,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Blademaster''s Polished Gemmed Band'),
(3440001,280721,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Pendant of the Ancient Watch'),
(3440001,300302,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Lost Warden''s Blackened Great Pauldrons'),
(3440001,340698,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Icecaller''s Mitts'),
(3440001,360398,0,0,0,2,1,1,1,'Generated map_543_difficulty_1 boss_000394 | Splintered Kilt');

DELETE FROM `creature_loot_template` WHERE `Entry` = 18433 AND `Item` = 2010000506 AND `Reference` = 3440001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(18433,2010000506,3440001,2,0,2,0,1,1,'Generated encounter attachment | map_543_difficulty_1 | boss_000394');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3460000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3460000,240110,0,0,0,1,1,1,1,'Generated map_545_difficulty_0 boss_000314 | Dusty Promise of the Golden Dawn'),
(3460000,260512,0,0,0,1,1,1,1,'Generated map_545_difficulty_0 boss_000314 | Bloodkeeper''s Deepdelver Legguards'),
(3460000,280657,0,0,0,1,1,1,1,'Generated map_545_difficulty_0 boss_000314 | Shield Blade Neckchain'),
(3460000,360829,0,0,0,1,1,1,1,'Generated map_545_difficulty_0 boss_000314 | Robe, North Clutch');

DELETE FROM `creature_loot_template` WHERE `Entry` = 17797 AND `Item` = 2010000507 AND `Reference` = 3460000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(17797,2010000507,3460000,2,0,1,0,1,1,'Generated encounter attachment | map_545_difficulty_0 | boss_000314');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3470000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3470000,240173,0,0,0,2,1,1,1,'Generated map_545_difficulty_1 boss_000314 | Coif of Stormwind Keep'),
(3470000,240677,0,0,0,2,1,1,1,'Generated map_545_difficulty_1 boss_000314 | Icy Epaulets of Storm King'),
(3470000,260521,0,0,0,2,1,1,1,'Generated map_545_difficulty_1 boss_000314 | Arcanist''s Duskbound Legwraps');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3470001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3470001,280851,0,0,0,2,1,1,1,'Generated map_545_difficulty_1 boss_000316 | The Primeval Shoulderpads'),
(3470001,320380,0,0,0,2,1,1,1,'Generated map_545_difficulty_1 boss_000316 | Neckchain, Frozen Rend');

DELETE FROM `creature_loot_template` WHERE `Entry` = 20629 AND `Item` = 2010000508 AND `Reference` = 3470000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(20629,2010000508,3470000,2,0,2,0,1,1,'Generated encounter attachment | map_545_difficulty_1 | boss_000314');

DELETE FROM `creature_loot_template` WHERE `Entry` = 20630 AND `Item` = 2010000509 AND `Reference` = 3470001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(20630,2010000509,3470001,2,0,2,0,1,1,'Generated encounter attachment | map_545_difficulty_1 | boss_000316');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3520000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3520000,240985,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000623 | Dawn Cleaver Warden Bow'),
(3520000,320004,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000623 | Treads of the Pale Winter'),
(3520000,320714,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000623 | Blood Anchor Hauberk');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3520001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3520001,200091,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Legguards of the Argent Watch'),
(3520001,200257,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Thunderous Footplates of High Citadel'),
(3520001,200662,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Argent Marshal''s Hellforged Faceguard'),
(3520001,220106,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Iron Boots, Mystic Horn'),
(3520001,220139,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Star Keeper Beads'),
(3520001,240013,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Falcon Scream Longshot'),
(3520001,240144,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Bright Wyrm Bracers'),
(3520001,240724,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | North Ruin Shoulder Guards'),
(3520001,260643,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | The Dalaran Waistguard'),
(3520001,280016,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Enchanted Runering of the Deep Earth'),
(3520001,280057,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Leggings of the Star Watch'),
(3520001,280187,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Grave Warden Bracelets'),
(3520001,280284,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Cord of Amphitheater'),
(3520001,280556,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Argent Crusader''s Phylactery'),
(3520001,280876,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Ringlet, Falcon Hide'),
(3520001,280903,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Mark, West Heart'),
(3520001,300129,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Shoulderplates of Broken Shield'),
(3520001,300552,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Adamant Legguards'),
(3520001,300856,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Berserker Battleplate'),
(3520001,300894,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Red Crush Warplate'),
(3520001,300925,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Astral Reckoning Inscription'),
(3520001,320964,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Soulshard Rime Vambraces'),
(3520001,340220,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Marauding Shoulderpads'),
(3520001,340393,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Ancient Robes of the Astral Gate'),
(3520001,340731,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Starcaller''s Cord'),
(3520001,360256,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 trash | Shadowmage''s Baleful Wristwraps');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3520002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3520002,240333,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000625 | Frostworn Warcloak of Hidden King'),
(3520002,300342,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000625 | Serrated Signet Ring'),
(3520002,300666,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000625 | Soulshard Scar Wargrips'),
(3520002,320366,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000625 | Darkwarden''s Weathered Helm'),
(3520002,340674,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000625 | Shoes, Astral Punch'),
(3520002,360617,0,0,0,1,1,1,1,'Generated map_548_difficulty_0 boss_000625 | Forgemaster''s Kilt');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21216 AND `Item` = 2010000510 AND `Reference` = 3520000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21216,2010000510,3520000,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | boss_000623');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21218 AND `Item` = 2010000511 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21218,2010000511,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21220 AND `Item` = 2010000512 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21220,2010000512,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21221 AND `Item` = 2010000513 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21221,2010000513,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21224 AND `Item` = 2010000514 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21224,2010000514,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21225 AND `Item` = 2010000515 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21225,2010000515,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21226 AND `Item` = 2010000516 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21226,2010000516,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21227 AND `Item` = 2010000517 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21227,2010000517,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21228 AND `Item` = 2010000518 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21228,2010000518,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21229 AND `Item` = 2010000519 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21229,2010000519,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21230 AND `Item` = 2010000520 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21230,2010000520,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21231 AND `Item` = 2010000521 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21231,2010000521,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21232 AND `Item` = 2010000522 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21232,2010000522,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21246 AND `Item` = 2010000523 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21246,2010000523,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21251 AND `Item` = 2010000524 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21251,2010000524,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21263 AND `Item` = 2010000525 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21263,2010000525,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21298 AND `Item` = 2010000526 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21298,2010000526,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21299 AND `Item` = 2010000527 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21299,2010000527,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21301 AND `Item` = 2010000528 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21301,2010000528,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21339 AND `Item` = 2010000529 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21339,2010000529,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21863 AND `Item` = 2010000530 AND `Reference` = 3520001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21863,2010000530,3520001,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 21215 AND `Item` = 2010000531 AND `Reference` = 3520002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(21215,2010000531,3520002,2,0,1,0,1,1,'Generated encounter attachment | map_548_difficulty_0 | boss_000625');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3530000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3530000,200036,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Magekeeper''s Headplate of the Winter Crown'),
(3530000,200377,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | The Nightbound Great Pauldrons'),
(3530000,200391,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Splintered War Greaves of Bloodguard'),
(3530000,220347,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Silverforged Warhelm of Final Watch'),
(3530000,220468,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Armguards, Grey Seal'),
(3530000,220830,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | The Lightblessed Shoulderplates'),
(3530000,220922,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Battle Girdle of the High Citadel'),
(3530000,240064,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | The Silversteel Blunderbuss'),
(3530000,240480,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Highlord''s Ghostly Vambraces'),
(3530000,240593,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Doomed Warhelm of the Runekeeper'),
(3530000,240741,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Dream Sorrow Token'),
(3530000,240914,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Last Keeper''s Chausses of the Hearthguard'),
(3530000,260147,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Deathless Scimitar of Frozen Watch'),
(3530000,260591,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Grim Requiem Waistband'),
(3530000,260683,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | The Dread Seal Ring'),
(3530000,280164,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Raven Brand Treads'),
(3530000,280296,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | The Winterborn Walkers'),
(3530000,280518,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Pale Hail Trousers'),
(3530000,280586,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Cinch of the Silent Moon'),
(3530000,280731,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Pendant Chain of the Rime King'),
(3530000,300033,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Handaxe of Bronze Dragon'),
(3530000,300186,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Stoneguard''s Warbelt'),
(3530000,300226,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Soldierly Vambraces of the Kings Road'),
(3530000,300307,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Cracked Battleplate of the Dragon Wastes'),
(3530000,300901,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Battle Hammer of the Midnight Flame'),
(3530000,300963,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Earthkeeper''s Libram of the Frozen Sea'),
(3530000,320174,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Iron King''s Chausses'),
(3530000,340025,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Trousers, Hammer Ritual'),
(3530000,340384,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Talisman, Blade Quarrel'),
(3530000,340638,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Trousers, Icefang Sigil'),
(3530000,340798,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Pitiless Walkers'),
(3530000,360580,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Last Warden''s Sandals'),
(3530000,360937,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Shieldguard''s Patient Mitts'),
(3530000,380519,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Spaulders of the Deep Mountain'),
(3530000,380933,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000730 | Brittle Footguards of Azure Flame');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3530002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3530002,300706,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000731 | Waistplate, Dusk Doom'),
(3530002,320410,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000731 | Helm of the Last Oath'),
(3530002,320493,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000731 | Silent Keeper''s Spire');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3530003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3530003,200318,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000732 | Bleak Girdle, Argent Champion''s Oath'),
(3530003,220019,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000732 | Badge of the Thorim Arena'),
(3530003,240845,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000732 | Griefbound Mail of the Ice King'),
(3530003,280704,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000732 | Merciless Greatcloak of Kirin Tor'),
(3530003,360966,0,0,0,1,1,1,1,'Generated map_550_difficulty_0 boss_000732 | The Bitter Brooch');

DELETE FROM `creature_loot_template` WHERE `Entry` = 19514 AND `Item` = 2010000532 AND `Reference` = 3530000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(19514,2010000532,3530000,2,0,1,0,1,1,'Generated encounter attachment | map_550_difficulty_0 | boss_000730');

DELETE FROM `creature_loot_template` WHERE `Entry` = 19516 AND `Item` = 2010000533 AND `Reference` = 3530002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(19516,2010000533,3530002,2,0,1,0,1,1,'Generated encounter attachment | map_550_difficulty_0 | boss_000731');

DELETE FROM `creature_loot_template` WHERE `Entry` = 18805 AND `Item` = 2010000534 AND `Reference` = 3530003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(18805,2010000534,3530003,2,0,1,0,1,1,'Generated encounter attachment | map_550_difficulty_0 | boss_000732');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3600002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3600002,220097,0,0,0,1,1,1,1,'Generated map_555_difficulty_0 boss_000210 | Emerald Keeper Reaver'),
(3600002,220259,0,0,0,1,1,1,1,'Generated map_555_difficulty_0 boss_000210 | Girdle of Arathi Highlands'),
(3600002,220269,0,0,0,1,1,1,1,'Generated map_555_difficulty_0 boss_000210 | Thunderkeeper''s Greaves'),
(3600002,240740,0,0,0,1,1,1,1,'Generated map_555_difficulty_0 boss_000210 | Howling Harness of the Dragon Throne'),
(3600002,300834,0,0,0,1,1,1,1,'Generated map_555_difficulty_0 boss_000210 | The Wyrmbound Battleplate Legguards'),
(3600002,360000,0,0,0,1,1,1,1,'Generated map_555_difficulty_0 boss_000210 | The Leafwoven Battleblade');

DELETE FROM `creature_loot_template` WHERE `Entry` = 18732 AND `Item` = 2010000535 AND `Reference` = 3600002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(18732,2010000535,3600002,2,0,1,0,1,1,'Generated encounter attachment | map_555_difficulty_0 | boss_000210');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3610000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3610000,300148,0,0,0,2,1,1,1,'Generated map_555_difficulty_1 boss_000208 | Ebon Crusader''s Corroded Veil');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3610002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3610002,280109,0,0,0,2,1,1,1,'Generated map_555_difficulty_1 boss_000210 | Frozen King''s Ghostly Wristwraps'),
(3610002,340760,0,0,0,2,1,1,1,'Generated map_555_difficulty_1 boss_000210 | Shoulderpads of Scarlet Banner');

DELETE FROM `creature_loot_template` WHERE `Entry` = 20636 AND `Item` = 2010000536 AND `Reference` = 3610000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(20636,2010000536,3610000,2,0,2,0,1,1,'Generated encounter attachment | map_555_difficulty_1 | boss_000208');

DELETE FROM `creature_loot_template` WHERE `Entry` = 20653 AND `Item` = 2010000537 AND `Reference` = 3610002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(20653,2010000537,3610002,2,0,2,0,1,1,'Generated encounter attachment | map_555_difficulty_1 | boss_000210');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3620000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3620000,200753,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000206 | Fallen Hand Rune Band'),
(3620000,240325,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000206 | Wrist Chains, Dragon Banner'),
(3620000,280299,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000206 | The Bloodforged Charm'),
(3620000,300598,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000206 | Wyrmforged War Leggings'),
(3620000,320845,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000206 | Wargrips of the Titan Archive'),
(3620000,380030,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000206 | Royal Band, Savage Verse'),
(3620000,380780,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000206 | Rod of the Final Dawn');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3620001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3620001,300432,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000207 | Ashen Lord''s Coil of the Cold Memory'),
(3620001,320267,0,0,0,1,1,1,1,'Generated map_556_difficulty_0 boss_000207 | Primeval Spire');

DELETE FROM `creature_loot_template` WHERE `Entry` = 18472 AND `Item` = 2010000538 AND `Reference` = 3620000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(18472,2010000538,3620000,2,0,1,0,1,1,'Generated encounter attachment | map_556_difficulty_0 | boss_000206');

DELETE FROM `creature_loot_template` WHERE `Entry` = 18473 AND `Item` = 2010000539 AND `Reference` = 3620001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(18473,2010000539,3620001,2,0,1,0,1,1,'Generated encounter attachment | map_556_difficulty_0 | boss_000207');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3630000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3630000,260447,0,0,0,2,1,1,1,'Generated map_556_difficulty_1 boss_000206 | Grim Armguards of the Sun Watch');

DELETE FROM `creature_loot_template` WHERE `Entry` = 20690 AND `Item` = 2010000540 AND `Reference` = 3630000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(20690,2010000540,3630000,2,0,2,0,1,1,'Generated encounter attachment | map_556_difficulty_1 | boss_000206');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3640001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3640001,200000,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Plaguebound Vambraces'),
(3640001,200001,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stormsteel Wargrips of the Valiance Keep'),
(3640001,200008,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rune-carved Wargrips'),
(3640001,200069,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Glacial Drape'),
(3640001,200215,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Greatsword of Nameless Dead'),
(3640001,200238,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Deathmarked Warbelt'),
(3640001,200272,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Earth Strike Armplates'),
(3640001,200365,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Soulfire Song Handplates'),
(3640001,200436,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Glacial Gauntlets'),
(3640001,200464,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Great Battleaxe, Wolf Dream'),
(3640001,200466,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Twilight-forged Armplates of Cold Hearth'),
(3640001,200494,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Carapace, Stone Horn'),
(3640001,200581,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Gray Legguards'),
(3640001,200583,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dragonhide Shroud of the First Flame'),
(3640001,200593,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dreamwarden''s Sword'),
(3640001,200672,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Legplates, Eagle Chill'),
(3640001,200688,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Breastplate of the Ancestor Spirit'),
(3640001,200695,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shadow Helm Chestplate'),
(3640001,200708,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Stormwrought Footplates'),
(3640001,200765,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Feathered Faceguard'),
(3640001,200831,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wolfguard''s Torque'),
(3640001,200839,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Silverkeeper''s Arcane Torc'),
(3640001,200845,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bonecrusher of the Dead King'),
(3640001,200857,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dark Crush Bone'),
(3640001,200858,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Corpsebound Waistguard of Wildhammer Clan'),
(3640001,200890,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | War Leggings of the Shattered Crown'),
(3640001,200905,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Coal-black Legplates'),
(3640001,200907,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ice Witch''s Battle Girdle of the Sunwell'),
(3640001,200913,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stonecaller''s Medallion'),
(3640001,200926,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Starfire Anvil Waistplate'),
(3640001,200947,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Astral Ring of Fel Ritual'),
(3640001,200965,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ornate Vambraces of the Ebon Blade'),
(3640001,200982,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Highborne Runeblade'),
(3640001,220013,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Hexed Breastplate of the Silver Watch'),
(3640001,220028,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | War Greaves of K3'),
(3640001,220069,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battleplate of Runekeeper'),
(3640001,220102,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Pauldrons of War Watch'),
(3640001,220111,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Choker, Spell Oath'),
(3640001,220127,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Legguards, Forgotten Edge'),
(3640001,220160,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Steadfast Battleplate of Valgarde'),
(3640001,220176,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Charmstone, Lion Rage'),
(3640001,220191,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bonekeeper''s Embersteel Breastplate'),
(3640001,220193,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warmaster''s Veil'),
(3640001,220227,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Legguards, Winter Cleaver'),
(3640001,220254,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | War Pauldrons of the Great Bear'),
(3640001,220256,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dragonforged Warband of the Rime Watch'),
(3640001,220325,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Blackened Stonehammer'),
(3640001,220386,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rune Blood Shieldwall'),
(3640001,220403,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ornate Warbracers'),
(3640001,220430,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Storm Queen''s Crimson Great Cape'),
(3640001,220437,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Legguards of the Dragon Aspect'),
(3640001,220459,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Iron King''s Runeblade'),
(3640001,220469,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Briarwoven War Pauldrons'),
(3640001,220475,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wyrm King''s Beads of the Ancient Night'),
(3640001,220496,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Runeforged Warplate'),
(3640001,220497,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Frozen Curse Greaves'),
(3640001,220504,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Windlord''s Libram'),
(3640001,220513,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Neckguard of the Amber Ledge'),
(3640001,220516,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Lightbound Breastplate of the Water Spirit'),
(3640001,220551,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Brazen Shoulderplates of the Blood Tide'),
(3640001,220730,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stargazer''s Stormwrought Visor'),
(3640001,220732,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Visor of Long Road'),
(3640001,220748,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Leafbound Bracers of the Construct Wing'),
(3640001,220777,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ancient Knight''s Seal'),
(3640001,220783,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battleplate of Bone Wastes'),
(3640001,220800,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Woeful Gemmed Band of Wyrm King'),
(3640001,220815,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Grey Dusk Headplate'),
(3640001,220825,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ravenous Shawl'),
(3640001,220957,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Cape, Violet Song'),
(3640001,240010,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Titan King''s Warboots'),
(3640001,240024,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Lightwoven Shoulder Guards of Azjol Nerub'),
(3640001,240120,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wrathful War Leggings'),
(3640001,240164,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stormscarred Epaulets'),
(3640001,240262,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Mail of the Void King'),
(3640001,240291,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Faded Treads of Grim Dawn'),
(3640001,240326,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bearwarden''s Legguards'),
(3640001,240330,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Titanwarden''s Sunforged Girdle'),
(3640001,240340,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Gauntlets, Scarlet Hand'),
(3640001,240353,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Spiritkeeper''s Grips'),
(3640001,240413,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Treads, Light Clutch'),
(3640001,240430,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wildbound Fingerband of the Ebon Banner'),
(3640001,240434,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Astral Greaves of the Forgotten Dead'),
(3640001,240436,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Runewarden''s Everfrost Shoulder Guards'),
(3640001,240465,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shoulder Drape of the Argent Tournament'),
(3640001,240487,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Spaulders, Frozen Glyph'),
(3640001,240497,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Bronzed Shawl'),
(3640001,240505,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Grand Axe of the Frozen Crown'),
(3640001,240512,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Leggings of the Earthen Watch'),
(3640001,240538,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Nether Roar Treads'),
(3640001,240556,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Sunbound Handguards'),
(3640001,240575,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warforged Faceguard of the Old Kingdom'),
(3640001,240603,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Engraved Orb'),
(3640001,240632,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shoulder Drape of the Silent Watch'),
(3640001,240658,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Hardened Figurine of the Blood Moon'),
(3640001,240681,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Waistchain of the Titan Watcher'),
(3640001,240688,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Iron King''s Boots'),
(3640001,240717,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | First Queen''s Grips of the Endless Path'),
(3640001,240727,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Everfrost Torque'),
(3640001,240803,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Titanforger''s Belt'),
(3640001,240862,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Vanguard''s Plaguebound Wrist Chains'),
(3640001,240863,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Mail of the Sky Watch'),
(3640001,240962,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Violet Spear of Iron Council'),
(3640001,240968,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Hoarfrost Capelet of Frozen Star'),
(3640001,260046,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warcloak of Blighted Land'),
(3640001,260051,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shortsword of Halls of Reflection'),
(3640001,260055,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Cap of Grave Lord'),
(3640001,260087,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Carrion Vest of the Scarlet Bastion'),
(3640001,260095,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ashkeeper''s Waistguard'),
(3640001,260129,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Starfire Sun Heart'),
(3640001,260135,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Blessed Traveling Cloak'),
(3640001,260157,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wyrmscale Mantle of Dalaran'),
(3640001,260188,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Cryptborn Bindings'),
(3640001,260189,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rondel, Wild Brand'),
(3640001,260239,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Darkrider''s Seal Ring of the Titan Vault'),
(3640001,260260,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Manaforged Treads, Warcaller''s Oath'),
(3640001,260264,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dreambound Shoulder Drape'),
(3640001,260288,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rimebound Band'),
(3640001,260294,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Legwraps, Iron Will'),
(3640001,260300,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Lightwoven Waistguard'),
(3640001,260310,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Spirit Guard Idol'),
(3640001,260327,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Graven Torque of the Deep Forge'),
(3640001,260358,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rime-coated Headguard of the Great Hunt'),
(3640001,260426,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Dreadbound Wristbands'),
(3640001,260479,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Eagle Shot Footguards'),
(3640001,260491,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Primal Beacon Carapace'),
(3640001,260496,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Grim Collar of Moonwell'),
(3640001,260539,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battle Fist, Sacred Ray'),
(3640001,260542,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Magebound Trousers'),
(3640001,260599,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dawnwarden''s Cowl of the Stone Watch'),
(3640001,260615,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Silver King''s Coldbound Band'),
(3640001,260617,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dragon Warden Leggings'),
(3640001,260624,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Defiant Reaver'),
(3640001,260690,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Luminous Handguards'),
(3640001,260726,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wyrmkeeper''s Legguards'),
(3640001,260780,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Icy Battlecloak of Iron Dwarf'),
(3640001,260787,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Flawless Promise of the Ice Queen'),
(3640001,260793,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shoulderwraps of the Thunder King'),
(3640001,260818,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rimewarden''s Ritual Knife'),
(3640001,260842,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dwarven Clutches of Wind King'),
(3640001,260859,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stalkers of the Argent Tournament'),
(3640001,260868,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Cursed Great Cape'),
(3640001,260916,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Clutches of the Void Flame'),
(3640001,260949,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Voidwarden''s Chestguard'),
(3640001,260955,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warguard''s Warcloak'),
(3640001,280012,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Solemn Hammer of the Violet Citadel'),
(3640001,280037,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Colossal Emblem'),
(3640001,280055,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Frostkeeper''s Scale-bound Headdress'),
(3640001,280072,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Gravekeeper''s Shoulderpads'),
(3640001,280090,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shoulderpads, Starfang Veil'),
(3640001,280096,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Stoneforged Leggings'),
(3640001,280146,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wintercaller''s Binding'),
(3640001,280147,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Epaulets of the Shadow Vault'),
(3640001,280150,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Skullforged Spell Scepter of the Ice Moon'),
(3640001,280172,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Boots, Scarlet Brand'),
(3640001,280177,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Silver Queen''s Voidbound Archmage Staff'),
(3640001,280178,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Runed Choker'),
(3640001,280279,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Silverblessed Shoulderwraps'),
(3640001,280308,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Voidlord''s Totem'),
(3640001,280337,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Brassbound Star Wand'),
(3640001,280338,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Soulcaller''s Briarwoven Royal Cloak'),
(3640001,280344,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Arctic Diadem'),
(3640001,280379,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Skullkeeper''s Armbands'),
(3640001,280418,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Footwraps of the Frost Crown'),
(3640001,280471,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Waistband, High Carver'),
(3640001,280521,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Silent Keeper''s Raiment'),
(3640001,280577,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Raven Hex Signet Ring'),
(3640001,280578,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Cowl of Moon Guard'),
(3640001,280614,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Unbroken Spirit Staff'),
(3640001,280651,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Soullord''s Raiment of the Pale King'),
(3640001,280713,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Signet Ring, Blood Grave'),
(3640001,280725,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Moon Queen''s Waistband'),
(3640001,280758,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Chestwrap of Dark Iron Clan'),
(3640001,280781,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shadowwarden''s Mirror'),
(3640001,280787,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rune Band of Wild Moon'),
(3640001,280793,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dragonbound Knobbed Mace of Dawn Vanguard'),
(3640001,280814,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stonekeeper''s Voidsteel Runestaff'),
(3640001,280856,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Nightcaller''s Necrotic Treads'),
(3640001,280860,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Moonforged Vest of Oculus'),
(3640001,280890,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Vestments of the Fel Ritual'),
(3640001,280904,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Boots of the Kings Promise'),
(3640001,280948,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dreamwoven Medallion of the Dalaran Watch'),
(3640001,280971,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bloodforged Keepsake'),
(3640001,280996,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Deathly Epaulets of Emerald Grove'),
(3640001,300008,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rune-etched Forgehammer'),
(3640001,300010,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Duskcaller''s Merciless Vambraces'),
(3640001,300011,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Arcane Ash War Pauldrons'),
(3640001,300054,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Waistplate, Forge Wall'),
(3640001,300100,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Unwavering Longcloak of the Great Bear'),
(3640001,300113,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Watchful Battleaxe of Red Dragon'),
(3640001,300119,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Carapace, Sun Cry'),
(3640001,300124,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Greataxe, Frostfire Ash'),
(3640001,300126,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warbracers of Azure Moon'),
(3640001,300154,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Coil, Serpent Flame'),
(3640001,300175,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Vanguard''s Lightbound Bearded Axe'),
(3640001,300182,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Brooch, Twilight Caller'),
(3640001,300203,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wintercaller''s Battleblade'),
(3640001,300210,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warbelt of the Shadow Moon'),
(3640001,300225,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ravenwarden''s Skullsplitter'),
(3640001,300234,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bitter Seal Beads'),
(3640001,300244,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Northman''s Sabatons'),
(3640001,300255,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Crimson Faceguard of Dawn Oath'),
(3640001,300258,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | East Watch Armguards'),
(3640001,300263,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Graven Warsword of Grim King'),
(3640001,300264,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Handplates of Forgotten Depths'),
(3640001,300282,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Illusory Stonehammer of Frozen North'),
(3640001,300330,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Clawmarked Faceguard of Titan King'),
(3640001,300332,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Plaguebound Runeblade of Light Breach'),
(3640001,300349,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rune King''s Fireforged Warplate'),
(3640001,300364,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ravenwarden''s Scourged Carapace'),
(3640001,300378,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Handplates, Dawn Creed'),
(3640001,300396,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Baleful Rune Band, Battlemage''s Oath'),
(3640001,300406,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Titan Axe of Ebon Hold'),
(3640001,300422,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Blazing Warband of the War Crown'),
(3640001,300429,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battleplate Legguards, Steel Chain'),
(3640001,300463,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Last King''s Effigy'),
(3640001,300477,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Headplate of Winter Watch'),
(3640001,300496,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wildbound Torque'),
(3640001,300508,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Faceguard, Wildfire Rend'),
(3640001,300520,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Hoarfrost Neckguard of Wyrm Crown'),
(3640001,300525,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Flask of the Red Moon'),
(3640001,300528,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Nightforged Faceguard of Dalaran Watch'),
(3640001,300536,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Carved Relic, Wolf Starfall'),
(3640001,300539,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Enchanted Waistguard of Mount Hyjal'),
(3640001,300551,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Darkmoon War Pauldrons'),
(3640001,300561,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Steadfast Iron Boots'),
(3640001,300569,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ashen Queen''s Gauntlets'),
(3640001,300602,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Cryptborn Stone Relic of Arcane Star'),
(3640001,300614,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stormwrought Decapitator of the Sun Watch'),
(3640001,300630,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | First Queen''s Armplates'),
(3640001,300640,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Greaves of Utgarde Keep'),
(3640001,300650,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Flanged Mace, Argent Song'),
(3640001,300662,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Deepforged Battle Girdle'),
(3640001,300669,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warwarden''s Spellscarred Eye'),
(3640001,300673,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Necrotic Warplate of the Final Dawn'),
(3640001,300693,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Skull Clutch Eye'),
(3640001,300696,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Thornbound Visor'),
(3640001,300700,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Faceguard, Dread Memory'),
(3640001,300701,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Legguards of Warriors Promise'),
(3640001,300702,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Crimson Thorn Warband'),
(3640001,300739,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ravenkeeper''s Handplates'),
(3640001,300754,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battleplate Legguards of the Iron Gate'),
(3640001,300776,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Cryptlord''s Lightbound Great Pauldrons'),
(3640001,300840,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battleplate, Unbroken Seal'),
(3640001,300880,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Key, Violet Wind'),
(3640001,300900,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Footplates, Soulshard Rider'),
(3640001,300903,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | War Greaves, Green Rebuke'),
(3640001,300905,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Infused Crystal'),
(3640001,300941,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Highlord''s Stonehammer of the Wildheart'),
(3640001,300945,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Vambraces of the Blood Watch'),
(3640001,300955,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Colossal Veil of the Rime King'),
(3640001,300959,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Silvered Carapace'),
(3640001,300986,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Emerald Wing Legplates'),
(3640001,300997,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ancestral Armguards of the Forgotten Road'),
(3640001,320011,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Terrible Legguards of Scourge Lord'),
(3640001,320019,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Windforged Girdle of the Blood Crown'),
(3640001,320020,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bear Clutch Hoop'),
(3640001,320026,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bloodknight''s Footguards'),
(3640001,320086,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stonecarved Footguards'),
(3640001,320129,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Drakebound Casque'),
(3640001,320191,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | First Knight''s Amulet of the Earthen Watch'),
(3640001,320261,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bloodkeeper''s Spaulders'),
(3640001,320273,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Wintersteel Warboots'),
(3640001,320292,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Spider Beacon Epaulets'),
(3640001,320293,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Drakecaller''s Warboots'),
(3640001,320329,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Legmail of the Great Forge'),
(3640001,320435,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bearhide Great Hauberk'),
(3640001,320446,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Unyielding Spaulders'),
(3640001,320465,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Assassin Blade of the Broken Spear'),
(3640001,320472,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Worldforged Ritual Relic'),
(3640001,320547,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Sable Cape of the Void King'),
(3640001,320575,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Broken Wargrips of the Iron March'),
(3640001,320586,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Warboots of the Violet Eye'),
(3640001,320609,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ivory Bolt Cloak'),
(3640001,320664,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Figurine of Fallen Lord'),
(3640001,320721,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Violet Warden''s Hoarfrost Great Cape'),
(3640001,320750,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Starbound Cudgel'),
(3640001,320770,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Soulforged Casque'),
(3640001,320779,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Winter Hymn Headguard'),
(3640001,320794,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Goldsteel Casque'),
(3640001,320827,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Runestaff, Dark Bane'),
(3640001,320879,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shoulder Guards, Sable Heart'),
(3640001,320938,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Headguard of Ancient Memory'),
(3640001,320951,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Soulwarden''s Twilight-forged War Mantle'),
(3640001,320958,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Duskwarden''s Legguards of the Fallen King'),
(3640001,320971,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Forgotten King''s Hallowed Runestaff'),
(3640001,320992,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Fanged Nightcloak of the Dark Crown'),
(3640001,320999,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Brutish Bracers of Winter Forge'),
(3640001,340030,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Primal Cowl'),
(3640001,340032,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Mystic Wand, Ivory Fang'),
(3640001,340036,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Shoulderwraps of Blood Ritual'),
(3640001,340103,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ironthane''s Forgeblessed Seal Ring'),
(3640001,340105,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Merciless Blade of the Iron Banner'),
(3640001,340114,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wildbound Skullcap'),
(3640001,340170,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battlelord''s Greatstaff'),
(3640001,340186,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wolfhide Wand'),
(3640001,340190,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Relentless Keepsake'),
(3640001,340199,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Runemaster''s Thorned Bracelets'),
(3640001,340202,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Mitts of the Thunder Bluff'),
(3640001,340353,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bloodforged Robe'),
(3640001,340383,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bronzed Treads of the Winter Crown'),
(3640001,340386,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Conqueror Handwraps of Dragon Pact'),
(3640001,340404,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Dustbound Phylactery of Pit of Saron'),
(3640001,340407,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Waistband of the Silent Crypt'),
(3640001,340425,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Plague Hail Crook'),
(3640001,340432,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Darkkeeper''s Trousers'),
(3640001,340491,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Amulet of the Moon Crown'),
(3640001,340581,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Haunted Shawl'),
(3640001,340655,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Frostkeeper''s Breeches'),
(3640001,340673,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Broken Warden''s Neckchain'),
(3640001,340740,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Battlelord''s Pale Diadem'),
(3640001,340848,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Deathcaller''s Hammered Spire'),
(3640001,340858,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Merciless Clasp of the Sacred Flame'),
(3640001,340948,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Sash of the Broken Road'),
(3640001,340957,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ashen Queen''s Runebands'),
(3640001,340963,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Glittering Vest'),
(3640001,360030,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Coil of Kirin Tor'),
(3640001,360090,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stonecaller''s Conduit of the Arcane Watch'),
(3640001,360094,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Embersteel Staff of the Broken Spear'),
(3640001,360145,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Brooch, Moon Grasp'),
(3640001,360159,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Clouded Dirk of the Stormcaller'),
(3640001,360229,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Frozen Keeper''s Draconic Leggings'),
(3640001,360261,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Pants, Earthshard Reaver'),
(3640001,360262,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Brand of the Silent Crypt'),
(3640001,360327,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Umbral Regalia'),
(3640001,360331,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Silent King''s Beads of the Burning Blood'),
(3640001,360413,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Unbroken Root Vestments'),
(3640001,360420,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Boots, West Roar'),
(3640001,360449,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Virtuous Arcane Rod of the Utgarde'),
(3640001,360462,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bronzed Seer Staff'),
(3640001,360517,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Bloodforged Medallion'),
(3640001,360543,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Living Handwraps of the Warsong Clan'),
(3640001,360559,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Ancient Robes'),
(3640001,360562,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Flameforged Diadem'),
(3640001,360575,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Northman''s Austere Shortsword'),
(3640001,360639,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Twilight Ringlet of the Temple of Storms'),
(3640001,360662,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Pendant, Soul Ice'),
(3640001,360687,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Silver Seed Skullcap'),
(3640001,360762,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Greenwood Scale'),
(3640001,360805,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Footwraps of Frozen Pact'),
(3640001,360807,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Mitts of Black Ice'),
(3640001,360810,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ironforged Wristwraps of the Kings Road'),
(3640001,360830,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Mistbound Gemmed Band'),
(3640001,360904,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stormwrought Crystal Wand of the Dead King'),
(3640001,360906,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Sandals, Bleak Rune'),
(3640001,360933,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Runecaller''s Heavenforged Armbands'),
(3640001,360947,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Royal Vestments'),
(3640001,360976,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Argent Marshal''s Dreamwoven Boots'),
(3640001,380003,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Runekeeper''s Gorget of the Twilight Flame'),
(3640001,380023,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ancestor''s Stalkers of the High Citadel'),
(3640001,380083,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Frostbitten Choker'),
(3640001,380085,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Headdress of Stone King'),
(3640001,380100,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | First King''s Assassin Blade'),
(3640001,380116,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Stoneguard''s Bloodsoaked Shawl'),
(3640001,380125,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Wolf Cold Greatstaff'),
(3640001,380134,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Witchbound Strap'),
(3640001,380187,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Icebound Grand Mace of Wind Crown'),
(3640001,380221,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Girdle of the Dragon Aspect'),
(3640001,380276,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Darkkeeper''s Waistguard of the Cold Memory'),
(3640001,380277,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Carapace of First King'),
(3640001,380295,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Forsaken Greatstaff of Infinite Flight'),
(3640001,380313,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bright Mantle of the Terokkar'),
(3640001,380314,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Runed Stalkers of Wyrmrest'),
(3640001,380321,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Whispering Helm'),
(3640001,380325,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Argent Knight''s Brightsteel Bone'),
(3640001,380339,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Drakekeeper''s Pricker'),
(3640001,380344,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Amulet of the Fel Ritual'),
(3640001,380353,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Unyielding Capelet of the Ancient Banner'),
(3640001,380375,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Icy Wargrips of the Divine Watch'),
(3640001,380383,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Tombkeeper''s Charmstone'),
(3640001,380406,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Moonsteel Shoulderwraps of Cold Watch'),
(3640001,380419,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Mist Wolf Tunic'),
(3640001,380420,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | The Rimeforged Headguard'),
(3640001,380501,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Vest of Violet Eye'),
(3640001,380584,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Ashwarden''s Spellscarred Shoulderwraps'),
(3640001,380630,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Neckguard of the Kings Promise'),
(3640001,380654,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Arctic Shoulderwraps'),
(3640001,380702,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Flamebound Cinch'),
(3640001,380742,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Thunderwarden''s Ironbound Wristguards'),
(3640001,380769,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Deathmask of the Azure Moon'),
(3640001,380785,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Voidcaller''s Pants'),
(3640001,380786,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Rimecaller''s Girdle'),
(3640001,380798,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Silent Wargrips of the Deep Vault'),
(3640001,380803,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bracers of the Rune Watch'),
(3640001,380839,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Timeworn Pants of the Frozen Heart'),
(3640001,380894,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Blood Wake Gloves'),
(3640001,380929,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Bloodmage''s Spaulders of the Golden Banner'),
(3640001,380992,0,0,0,1,1,1,1,'Generated map_557_difficulty_0 trash | Spaulders of Frost Queen');

DELETE FROM `creature_loot_template` WHERE `Entry` = 18314 AND `Item` = 2010000541 AND `Reference` = 3640001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(18314,2010000541,3640001,2,0,1,0,1,1,'Generated encounter attachment | map_557_difficulty_0 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 19306 AND `Item` = 2010000542 AND `Reference` = 3640001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(19306,2010000542,3640001,2,0,1,0,1,1,'Generated encounter attachment | map_557_difficulty_0 | trash');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3650001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3650001,220586,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Battleplate, Bronze Fire'),
(3650001,280065,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Vest of the Kings Promise'),
(3650001,300221,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Wildforged Medallion'),
(3650001,300713,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Cryptkeeper''s Soulforged Legguards'),
(3650001,320432,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Ashen Lord''s Belt of the Argent Crusade'),
(3650001,320850,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Unholy Lens'),
(3650001,340414,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Breeches of the Ironforge Mountain'),
(3650001,380788,0,0,0,2,1,1,1,'Generated map_557_difficulty_1 trash | Northman''s Handguards');

DELETE FROM `creature_loot_template` WHERE `Entry` = 19306 AND `Item` = 2010000543 AND `Reference` = 3650001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(19306,2010000543,3650001,2,0,2,0,1,1,'Generated encounter attachment | map_557_difficulty_1 | trash');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3720000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3720000,200261,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Twilight Sabatons'),
(3720000,200383,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Great Hammer, Rune Doom'),
(3720000,200922,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Ravenous Headsman of the Silent Crypt'),
(3720000,200929,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | The Mournful Greaves'),
(3720000,220334,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Brutish Breastplate of Bone Lord'),
(3720000,220418,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | The Wildbound Armplates'),
(3720000,220631,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Shoulderplates of Dragon Queen'),
(3720000,240290,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Leggings of the Long Road'),
(3720000,260459,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Austere Boots, Silverwarden''s Oath'),
(3720000,260951,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Bindings of the Mount Hyjal'),
(3720000,280189,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Stormwrought Diadem of Demon Watch'),
(3720000,280974,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Razor-edged Kilt of the Ancient Thorn'),
(3720000,300116,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Dawnwarden''s Chestplate of the Sable Crown'),
(3720000,300261,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Nerubian Sollerets of the Stone King'),
(3720000,300722,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Storm King''s Handplates of the Light Oath'),
(3720000,300821,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Footplates, Last Requiem'),
(3720000,320356,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Hoop of the Silver Dawn'),
(3720000,320451,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Helm of the Iron Council'),
(3720000,340509,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Headdress, Bitter Lament'),
(3720000,360406,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Handwraps, Moon Flame'),
(3720000,360561,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Dragonsteel Sandals of the War King'),
(3720000,360754,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Grimdark Ringlet'),
(3720000,380802,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000778 | Silverforged Headguard of Broken Pact');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3720004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3720004,200824,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000782 | Scarlet Chain of the Dragon Queen'),
(3720004,240590,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000782 | Bone Vengeance Casque'),
(3720004,280082,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000782 | Headdress of Dawn Light'),
(3720004,320463,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000782 | Worldwarden''s Greaves of the Endless Vigil'),
(3720004,380535,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000782 | Gray Clutches');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3720005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3720005,220021,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Void Ripper Great Lance'),
(3720005,220834,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Frost Queen''s Ornate Greathelm'),
(3720005,260700,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Deep Singer Girdle'),
(3720005,280485,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Ironthane Royal Band'),
(3720005,300641,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Wargrips of the Burning Steppes'),
(3720005,360368,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Soullord''s Runering of the Great Hunt'),
(3720005,360772,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Stormwarden''s Circlet'),
(3720005,380366,0,0,0,1,1,1,1,'Generated map_568_difficulty_0 boss_000783 | Thunderlord''s Leggings of the High Watch');

DELETE FROM `creature_loot_template` WHERE `Entry` = 23574 AND `Item` = 2010000544 AND `Reference` = 3720000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(23574,2010000544,3720000,2,0,1,0,1,1,'Generated encounter attachment | map_568_difficulty_0 | boss_000778');

DELETE FROM `creature_loot_template` WHERE `Entry` = 24239 AND `Item` = 2010000545 AND `Reference` = 3720004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(24239,2010000545,3720004,2,0,1,0,1,1,'Generated encounter attachment | map_568_difficulty_0 | boss_000782');

DELETE FROM `creature_loot_template` WHERE `Entry` = 23863 AND `Item` = 2010000546 AND `Reference` = 3720005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(23863,2010000546,3720005,2,0,1,0,1,1,'Generated encounter attachment | map_568_difficulty_0 | boss_000783');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3740000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3740000,240086,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000571 | The Runeforged Siegebow'),
(3740000,300345,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000571 | The Ancestral Breastplate'),
(3740000,300382,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000571 | Sigil of Dark Ritual'),
(3740000,300699,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000571 | Aged Footplates of Arathi Highlands'),
(3740000,300934,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000571 | Radiant Legguards of the Midnight Moon'),
(3740000,380699,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000571 | The Stoneward Boots');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3740003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3740003,200571,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000575 | Light Hex War Pauldrons'),
(3740003,300143,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000575 | Brittle Armguards'),
(3740003,380389,0,0,0,2,1,1,1,'Generated map_574_difficulty_1 boss_000575 | Frozen King''s Arcane Bracers');

DELETE FROM `creature_loot_template` WHERE `Entry` = 30748 AND `Item` = 2010000547 AND `Reference` = 3740000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(30748,2010000547,3740000,2,0,2,0,1,1,'Generated encounter attachment | map_574_difficulty_1 | boss_000571');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31673 AND `Item` = 2010000548 AND `Reference` = 3740003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31673,2010000548,3740003,2,0,2,0,1,1,'Generated encounter attachment | map_574_difficulty_1 | boss_000575');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3750000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3750000,220292,0,0,0,1,1,1,1,'Generated map_575_difficulty_0 boss_000579 | War Leggings, Holy Wound'),
(3750000,240490,0,0,0,1,1,1,1,'Generated map_575_difficulty_0 boss_000579 | Helm, Red Plate'),
(3750000,300029,0,0,0,1,1,1,1,'Generated map_575_difficulty_0 boss_000579 | Icebound Rune Band of the Ashen Pact'),
(3750000,360365,0,0,0,1,1,1,1,'Generated map_575_difficulty_0 boss_000579 | Icekeeper''s Branch'),
(3750000,360556,0,0,0,1,1,1,1,'Generated map_575_difficulty_0 boss_000579 | Bindings of the Star Forge'),
(3750000,380032,0,0,0,1,1,1,1,'Generated map_575_difficulty_0 boss_000579 | Ominous Longcloak of Dragonblight');

DELETE FROM `creature_loot_template` WHERE `Entry` = 26687 AND `Item` = 2010000549 AND `Reference` = 3750000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(26687,2010000549,3750000,2,0,1,0,1,1,'Generated encounter attachment | map_575_difficulty_0 | boss_000579');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3760000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3760000,200650,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000579 | Chain, Dire Dirge'),
(3760000,220080,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000579 | Fanged Key of Sun Flame'),
(3760000,220261,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000579 | Icetouched Cloak, Dreamkeeper''s Oath'),
(3760000,240666,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000579 | Illusory Chain of Wyrm Lord'),
(3760000,300964,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000579 | Earthwarden''s Warplate');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3760003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3760003,280823,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000583 | Grips of the Golden Moon'),
(3760003,300328,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000583 | Fernwoven War Pauldrons of Broken Banner'),
(3760003,380439,0,0,0,2,1,1,1,'Generated map_575_difficulty_1 boss_000583 | Shroud, Astral Spire');

DELETE FROM `creature_loot_template` WHERE `Entry` = 30774 AND `Item` = 2010000550 AND `Reference` = 3760000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(30774,2010000550,3760000,2,0,2,0,1,1,'Generated encounter attachment | map_575_difficulty_1 | boss_000579');

DELETE FROM `creature_loot_template` WHERE `Entry` = 30788 AND `Item` = 2010000551 AND `Reference` = 3760003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(30788,2010000551,3760003,2,0,2,0,1,1,'Generated encounter attachment | map_575_difficulty_1 | boss_000583');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3780001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3780001,240778,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000520 | Dreambound Wargrips of the Silent Crypt'),
(3780001,280707,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000520 | Forgotten Knight''s Robe'),
(3780001,300213,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000520 | Drakebound Greaves'),
(3780001,300727,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000520 | Frozen King''s Talisman'),
(3780001,340304,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000520 | Shadowforged Shoulderpads'),
(3780001,340349,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000520 | Ironkeeper''s Epaulets'),
(3780001,340684,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000520 | Silverguard''s Shadowmarked Neckchain');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3780004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3780004,260267,0,0,0,2,1,1,1,'Generated map_576_difficulty_1 boss_000526 | Stalkers of the Star Crown');

DELETE FROM `creature_loot_template` WHERE `Entry` = 30510 AND `Item` = 2010000552 AND `Reference` = 3780001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(30510,2010000552,3780001,2,0,2,0,1,1,'Generated encounter attachment | map_576_difficulty_1 | boss_000520');

DELETE FROM `creature_loot_template` WHERE `Entry` = 30540 AND `Item` = 2010000553 AND `Reference` = 3780004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(30540,2010000553,3780004,2,0,2,0,1,1,'Generated encounter attachment | map_576_difficulty_1 | boss_000526');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3790000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3790000,220091,0,0,0,1,1,1,1,'Generated map_578_difficulty_0 boss_000528 | Frost Queen''s Locket'),
(3790000,280726,0,0,0,1,1,1,1,'Generated map_578_difficulty_0 boss_000528 | Deep Bane Neckguard');

DELETE FROM `creature_loot_template` WHERE `Entry` = 27654 AND `Item` = 2010000554 AND `Reference` = 3790000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(27654,2010000554,3790000,2,0,1,0,1,1,'Generated encounter attachment | map_578_difficulty_0 | boss_000528');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3800000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3800000,200779,0,0,0,2,1,1,1,'Generated map_578_difficulty_1 boss_000528 | Footplates of Dread Wyrm'),
(3800000,220503,0,0,0,2,1,1,1,'Generated map_578_difficulty_1 boss_000528 | Shield Ice Torc'),
(3800000,260810,0,0,0,2,1,1,1,'Generated map_578_difficulty_1 boss_000528 | Spaulders of Unending Watch'),
(3800000,300166,0,0,0,2,1,1,1,'Generated map_578_difficulty_1 boss_000528 | Blade Horn War Sword'),
(3800000,300704,0,0,0,2,1,1,1,'Generated map_578_difficulty_1 boss_000528 | Gauntlets, Dark Star');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31558 AND `Item` = 2010000555 AND `Reference` = 3800000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31558,2010000555,3800000,2,0,2,0,1,1,'Generated encounter attachment | map_578_difficulty_1 | boss_000528');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3840000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3840000,220135,0,0,0,1,1,1,1,'Generated map_595_difficulty_0 boss_000293 | Chestplate of the First King'),
(3840000,220464,0,0,0,1,1,1,1,'Generated map_595_difficulty_0 boss_000293 | Armguards, West Howl'),
(3840000,220585,0,0,0,1,1,1,1,'Generated map_595_difficulty_0 boss_000293 | Dragonhide Warbelt'),
(3840000,340754,0,0,0,1,1,1,1,'Generated map_595_difficulty_0 boss_000293 | Gravelord''s Pants');

DELETE FROM `creature_loot_template` WHERE `Entry` = 26529 AND `Item` = 2010000556 AND `Reference` = 3840000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(26529,2010000556,3840000,2,0,1,0,1,1,'Generated encounter attachment | map_595_difficulty_0 | boss_000293');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3850000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3850000,220393,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 boss_000293 | Unholy Creed Cloak'),
(3850000,300534,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 boss_000293 | Armplates, Celestial Fury'),
(3850000,340898,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 boss_000293 | Sash of Void Crown');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3850001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3850001,240785,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 trash | Surcoat of Ancient Storm'),
(3850001,300542,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 trash | The Goldbound Legplates'),
(3850001,360925,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 trash | Deathguard''s Runebands'),
(3850001,360934,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 trash | Dreamcaller''s Skullcap');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3850004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3850004,200053,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 script_DamageTaken | The Dawnlit Key'),
(3850004,260245,0,0,0,2,1,1,1,'Generated map_595_difficulty_1 script_DamageTaken | Splintered Bracers of Restless Dead');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31211 AND `Item` = 2010000557 AND `Reference` = 3850000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31211,2010000557,3850000,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | boss_000293');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31178 AND `Item` = 2010000558 AND `Reference` = 3850001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31178,2010000558,3850001,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31179 AND `Item` = 2010000559 AND `Reference` = 3850001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31179,2010000559,3850001,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31187 AND `Item` = 2010000560 AND `Reference` = 3850001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31187,2010000560,3850001,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31199 AND `Item` = 2010000561 AND `Reference` = 3850001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31199,2010000561,3850001,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31200 AND `Item` = 2010000562 AND `Reference` = 3850001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31200,2010000562,3850001,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31201 AND `Item` = 2010000563 AND `Reference` = 3850001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31201,2010000563,3850001,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | trash');

DELETE FROM `gameobject_loot_template` WHERE `Entry` = 24589 AND `Item` = 2010000564 AND `Reference` = 3850004;

INSERT INTO `gameobject_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(24589,2010000564,3850004,2,0,2,0,1,1,'Generated encounter attachment | map_595_difficulty_1 | script_DamageTaken');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3860000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3860000,200485,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Handplates of the Broken Spear'),
(3860000,220148,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Barbed Battlehelm'),
(3860000,240656,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Legmail of Bone Lord'),
(3860000,260278,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Frostbitten Pants of Dread Watch'),
(3860000,260976,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Emberwrought Treads, Sun Queen''s Oath'),
(3860000,280434,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Desecrated Sandals'),
(3860000,300027,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Battleplate Legguards of Silvermoon Spires'),
(3860000,300316,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Kingsworn Wrap of the Sable Crown'),
(3860000,300513,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Sable Freeze Neckchain'),
(3860000,300785,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | The Frostveined Skullsplitter'),
(3860000,320489,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | The Mistbound Greaves'),
(3860000,320996,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | War Leggings, Ebon Shine'),
(3860000,340007,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Spiritforged Spellblade'),
(3860000,340408,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Lost Warden''s Skirt'),
(3860000,340900,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Fetish of Zul Drak'),
(3860000,360973,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Dreaming Shoes of Final Dawn'),
(3860000,380020,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | Blood Prince''s Drakescale Waistguard'),
(3860000,380234,0,0,0,1,1,1,1,'Generated map_599_difficulty_0 boss_000563 | The Scale-bound Shoulderguards');

DELETE FROM `creature_loot_template` WHERE `Entry` = 27977 AND `Item` = 2010000565 AND `Reference` = 3860000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(27977,2010000565,3860000,2,0,1,0,1,1,'Generated encounter attachment | map_599_difficulty_0 | boss_000563');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3870000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3870000,240669,0,0,0,2,1,1,1,'Generated map_599_difficulty_1 boss_000563 | Brightmoon Skullsplitter of the Blood Pact'),
(3870000,260839,0,0,0,2,1,1,1,'Generated map_599_difficulty_1 boss_000563 | Headguard of Bone Ritual'),
(3870000,300217,0,0,0,2,1,1,1,'Generated map_599_difficulty_1 boss_000563 | Silverkeeper''s Dragonforged Footplates'),
(3870000,320439,0,0,0,2,1,1,1,'Generated map_599_difficulty_1 boss_000563 | Murderous Hoop, First Keeper''s Oath');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3870003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3870003,200619,0,0,0,2,1,1,1,'Generated map_599_difficulty_1 boss_000569 | Wyrm King''s Capelet');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31381 AND `Item` = 2010000566 AND `Reference` = 3870000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31381,2010000566,3870000,2,0,2,0,1,1,'Generated encounter attachment | map_599_difficulty_1 | boss_000563');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31386 AND `Item` = 2010000567 AND `Reference` = 3870003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31386,2010000567,3870003,2,0,2,0,1,1,'Generated encounter attachment | map_599_difficulty_1 | boss_000569');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3890000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3890000,220939,0,0,0,2,1,1,1,'Generated map_600_difficulty_1 boss_000369 | Earthshard Hunter Breastplate'),
(3890000,240732,0,0,0,2,1,1,1,'Generated map_600_difficulty_1 boss_000369 | Spear Sun Wargrips'),
(3890000,300421,0,0,0,2,1,1,1,'Generated map_600_difficulty_1 boss_000369 | Mark of Argent Vanguard'),
(3890000,300961,0,0,0,2,1,1,1,'Generated map_600_difficulty_1 boss_000369 | Icon of the Thunder King'),
(3890000,320684,0,0,0,2,1,1,1,'Generated map_600_difficulty_1 boss_000369 | Titanforged Legmail'),
(3890000,380474,0,0,0,2,1,1,1,'Generated map_600_difficulty_1 boss_000369 | Clouded Bracers, Nightkeeper''s Oath');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3890001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3890001,300658,0,0,0,2,1,1,1,'Generated map_600_difficulty_1 trash | Wyrmkeeper''s Vambraces');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31362 AND `Item` = 2010000568 AND `Reference` = 3890000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31362,2010000568,3890000,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | boss_000369');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31336 AND `Item` = 2010000569 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31336,2010000569,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31337 AND `Item` = 2010000570 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31337,2010000570,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31338 AND `Item` = 2010000571 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31338,2010000571,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31339 AND `Item` = 2010000572 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31339,2010000572,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31340 AND `Item` = 2010000573 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31340,2010000573,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31342 AND `Item` = 2010000574 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31342,2010000574,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31343 AND `Item` = 2010000575 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31343,2010000575,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31345 AND `Item` = 2010000576 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31345,2010000576,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31347 AND `Item` = 2010000577 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31347,2010000577,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31351 AND `Item` = 2010000578 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31351,2010000578,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31352 AND `Item` = 2010000579 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31352,2010000579,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31354 AND `Item` = 2010000580 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31354,2010000580,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31355 AND `Item` = 2010000581 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31355,2010000581,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31357 AND `Item` = 2010000582 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31357,2010000582,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31359 AND `Item` = 2010000583 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31359,2010000583,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31360 AND `Item` = 2010000584 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31360,2010000584,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31363 AND `Item` = 2010000585 AND `Reference` = 3890001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31363,2010000585,3890001,2,0,2,0,1,1,'Generated encounter attachment | map_600_difficulty_1 | trash');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3910000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3910000,260413,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Aged Battleblade of the Deep Earth'),
(3910000,280319,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Dragonwarden''s Bindings'),
(3910000,280583,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Nightfang Sigil Binding'),
(3910000,300019,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Silent Warbelt of the Ghost Moon'),
(3910000,300134,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Ashen Lord''s Bitter Footplates'),
(3910000,300257,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Grimdark Cuirass of the Soul Watch'),
(3910000,300619,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Plaguewarden''s Glacial Warhelm'),
(3910000,300846,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Relicbound Band of the Death Lord'),
(3910000,340539,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Pants, Abyss Slayer'),
(3910000,360177,0,0,0,2,1,1,1,'Generated map_601_difficulty_1 boss_000216 | Mitts of the Sindragosa Fall');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31612 AND `Item` = 2010000586 AND `Reference` = 3910000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31612,2010000586,3910000,2,0,2,0,1,1,'Generated encounter attachment | map_601_difficulty_1 | boss_000216');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3920000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3920000,360714,0,0,0,1,1,1,1,'Generated map_602_difficulty_0 boss_000555 | Bracelets, Fierce Fire'),
(3920000,380670,0,0,0,1,1,1,1,'Generated map_602_difficulty_0 boss_000555 | Frozen Keeper''s Headguard of the Ice Forge');

DELETE FROM `creature_loot_template` WHERE `Entry` = 28586 AND `Item` = 2010000587 AND `Reference` = 3920000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(28586,2010000587,3920000,2,0,1,0,1,1,'Generated encounter attachment | map_602_difficulty_0 | boss_000555');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3930000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3930000,200920,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000555 | Battlemage''s Seal Ring'),
(3930000,240972,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000555 | Repeater of Rimefang'),
(3930000,300417,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000555 | Kingsguard Fetish'),
(3930000,320738,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000555 | Carved Relic of Fallen Crown'),
(3930000,360364,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000555 | Magekeeper''s Robes');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3930004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3930004,300357,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000561 | Wargrips, Thorn Dancer'),
(3930004,340013,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000561 | Dream Fist Sword'),
(3930004,380684,0,0,0,2,1,1,1,'Generated map_602_difficulty_1 boss_000561 | Warrior-forged Runestaff');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31533 AND `Item` = 2010000588 AND `Reference` = 3930000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31533,2010000588,3930000,2,0,2,0,1,1,'Generated encounter attachment | map_602_difficulty_1 | boss_000555');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31538 AND `Item` = 2010000589 AND `Reference` = 3930004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31538,2010000589,3930004,2,0,2,0,1,1,'Generated encounter attachment | map_602_difficulty_1 | boss_000561');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3940000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3940000,240455,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Coldbound Runesword'),
(3940000,240905,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Bronze Knuckle Helm'),
(3940000,260378,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Wyrmbound Legwraps of Pale Moon'),
(3940000,280101,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Wildguard''s Tunic'),
(3940000,280797,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | The Primal Mantle'),
(3940000,280847,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Argent Tooth Runewand'),
(3940000,300096,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Glasslike Necklace'),
(3940000,300797,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Sky Mark Armplates'),
(3940000,300909,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Low Starfall Helm'),
(3940000,340010,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Sacred Starfall Hoop'),
(3940000,340776,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Deathcaller''s Primal Skullcap'),
(3940000,380442,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 boss_000744 | Woeful Mirror of the Hidden King');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3940006;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3940006,200643,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Blood King''s Glacial Legguards'),
(3940006,220462,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | The Deathbound Battle Girdle'),
(3940006,240363,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Sunfire Wall Beads'),
(3940006,280168,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Runesmith''s Cowl'),
(3940006,280227,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Coldforged Cord of Wild Pact'),
(3940006,300108,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Silent Sabatons, Old Knight''s Oath'),
(3940006,300202,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Grand Warhammer of the Emerald Watch'),
(3940006,300243,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Veteran Talisman of Black Dragon'),
(3940006,300353,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Compass of Shadow King'),
(3940006,300381,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Warpriest''s Carapace of the Titan King'),
(3940006,300415,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Wind Reach Battleplate Legguards'),
(3940006,300596,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Violet Ruin Backcloth'),
(3940006,300848,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Shadow King''s Runed Great Warblade'),
(3940006,300999,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Rune Queen''s Greathelm'),
(3940006,340044,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Scarlet Champion''s Traveling Cloak'),
(3940006,340470,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Eternal Hunter Shoulder Cape'),
(3940006,360111,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Drakeforged Waistband of Makers Overlook'),
(3940006,380693,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Grey Thirst Seal Ring'),
(3940006,380829,0,0,0,1,1,1,1,'Generated map_603_difficulty_0 script_UpdateAI | Silver King''s Chestpiece');

DELETE FROM `creature_loot_template` WHERE `Entry` = 33113 AND `Item` = 2010000590 AND `Reference` = 3940000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(33113,2010000590,3940000,2,0,1,0,1,1,'Generated encounter attachment | map_603_difficulty_0 | boss_000744');

DELETE FROM `gameobject_loot_template` WHERE `Entry` = 27086 AND `Item` = 2010000591 AND `Reference` = 3940006;

INSERT INTO `gameobject_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(27086,2010000591,3940006,2,0,1,0,1,1,'Generated encounter attachment | map_603_difficulty_0 | script_UpdateAI');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3950000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3950000,200267,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Shoulderplates of Ancient Watcher'),
(3950000,200339,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Forgotten Wristplates of the First Watch'),
(3950000,200425,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Starbound Gauntlets of Lost Crown'),
(3950000,200602,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Flawless Greatcloak'),
(3950000,200730,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Griefbound Greaves, Icewarden''s Oath'),
(3950000,200914,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Amulet of the Scarlet Dawn'),
(3950000,220128,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Northguard''s Warrior-forged Insignia'),
(3950000,220436,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Runic Warplate of the Broken Banner'),
(3950000,240246,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Warbelt of the Raven Spirit'),
(3950000,240271,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Hellforged Horn'),
(3950000,260116,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Iron Mace of Frenzyheart Hill'),
(3950000,260329,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Skullcrusher, Moonfire Piercer'),
(3950000,260590,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Figurine of the Frostwolf Clan'),
(3950000,260637,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Boneclad Shroud of Raven Queen'),
(3950000,260991,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Tooth of the Black Ritual'),
(3950000,280121,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | The Coldforged Cuffs'),
(3950000,280489,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Wild Mantle of the Scourge Watch'),
(3950000,280627,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Lost Keeper''s Plagueforged Robes'),
(3950000,280720,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Hardened Treads of Forgotten King'),
(3950000,300083,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Wolfcaller''s Wristplates of the Zul Drak'),
(3950000,300162,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Unhallowed Gauntlets of Karazhan'),
(3950000,300190,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | The Luminous Greatcloak'),
(3950000,300238,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Grave Guard Mark'),
(3950000,300356,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Savage Warplate of the Last Watch'),
(3950000,300446,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Pauldrons of the Long Night'),
(3950000,300449,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Seal Ring of the Astral Crown'),
(3950000,300458,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Warbracers of Silver Promise'),
(3950000,300472,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Froststeel Carapace of the Dragon Pact'),
(3950000,300473,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Bright Runeblade'),
(3950000,300512,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Band of Moon Flame'),
(3950000,300583,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Baleful Vambraces'),
(3950000,300595,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | The Sunblessed War Pauldrons'),
(3950000,300649,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Warlord''s Frostforged Armplates'),
(3950000,300665,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Witchbound Pauldrons of Shattered Gate'),
(3950000,300668,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Legguards of the Soul Watch'),
(3950000,300683,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Grim Song Titan Hammer'),
(3950000,300716,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Shieldbearer''s Sollerets'),
(3950000,300781,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Bloodwarden''s Shadowforged Warhelm'),
(3950000,300828,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Armplates of the Demon Lord'),
(3950000,300883,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Mountainborn Warbracers, Dawnkeeper''s Oath'),
(3950000,300919,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Medallion, Twilight Ice'),
(3950000,320210,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Shadow Shard Coif'),
(3950000,320685,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Stonekeeper''s Forgotten Warhelm'),
(3950000,320834,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Bracers of Ebon March'),
(3950000,320940,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Bloodforged Helm of the Sky King'),
(3950000,320989,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Necro Reach Pendant'),
(3950000,340145,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Grimlord''s Raiment of the Blood Crown'),
(3950000,340251,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Watchful Amulet of Star Forge'),
(3950000,340488,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Scale-bound Cowl'),
(3950000,340600,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Cord, Demon Plate'),
(3950000,340806,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | The Witchbound Grips'),
(3950000,340809,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | The Nerubian Vest'),
(3950000,360015,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Defiant Vest of Silver Flame'),
(3950000,360218,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Drape of the Runed Path'),
(3950000,360245,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Duskwoven Signet of Ashen Vale'),
(3950000,360293,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Permafrost Waistband of Iron Banner'),
(3950000,360298,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Plagueborn Longsword of the Dying Light'),
(3950000,360441,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Plaguekeeper''s Sash'),
(3950000,360547,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Unbroken Boots of Broken Hall'),
(3950000,360574,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | The Sunsteel Shoulder Drape'),
(3950000,360621,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Lost Warden''s Mountainborn Cord'),
(3950000,360721,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Reinforced Pants of the Zim Torga'),
(3950000,360897,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Primal Punch Shoulder Cape'),
(3950000,360938,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Frostwarden''s Luminous Bracelets'),
(3950000,360978,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Serrated Binding'),
(3950000,380213,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | The Wrathful Necklace'),
(3950000,380628,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Wyrm Queen''s Necklace of the Sun Crown'),
(3950000,380921,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000744 | Baneful Bindings, Ebon Knight''s Oath');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3950001;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3950001,200472,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Furious Breastplate'),
(3950001,240100,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Mail of Mana Forge'),
(3950001,260962,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Mirror, Earth Ray'),
(3950001,280250,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Grips, Bright Rend'),
(3950001,280439,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | The Fel Torc'),
(3950001,300016,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Warplate of Scarlet Bastion'),
(3950001,300199,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Spiritwarden''s Charm of the Oculus'),
(3950001,300205,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Frostbound Torque of Ghost Watch'),
(3950001,300318,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Arctic Carapace of Hearthguard'),
(3950001,300684,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | The Unholy Legplates'),
(3950001,300960,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Shoulderplates of Wind Watch'),
(3950001,340464,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Boots of the Frozen Star'),
(3950001,360132,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Steel Dusk Shawl'),
(3950001,360672,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Nightsteel Headdress of Wyrm Queen'),
(3950001,380865,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000745 | Mantle of the Quel Thalas');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3950003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3950003,200667,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Argent Knight''s Emberforged Girdle'),
(3950003,220666,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | The Holy Slasher'),
(3950003,220836,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Hidden Hunter Warcloak'),
(3950003,220893,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Doomforged Warbelt'),
(3950003,240411,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Casque of the Frost Forge'),
(3950003,240856,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Darkkeeper''s Bracers'),
(3950003,260440,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Battle Claw of the Light Eternal'),
(3950003,260966,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | The Thunderous Great Cape'),
(3950003,280176,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Windcaller''s Runed Footwraps'),
(3950003,300030,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Merciless Breastplate of Winter Moon'),
(3950003,300084,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Bloodkeeper''s Helm of the Arcane Gate'),
(3950003,300139,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Woeful Coil of the Dusk Watch'),
(3950003,300228,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Zweihander of the High Watch'),
(3950003,300275,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Crusader Warbracers'),
(3950003,300312,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Shattered Headplate of Ebon Pact'),
(3950003,300326,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Sorrowful Vambraces of the Avalanche'),
(3950003,300444,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Brooch of the Thunder King'),
(3950003,300503,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Carapace, Starfire Wake'),
(3950003,300616,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Argent Defender''s Pauldrons'),
(3950003,300717,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Dragon King''s Great Cape'),
(3950003,300744,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Shieldbearer''s Waistplate'),
(3950003,300809,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Star Death Grand Mace'),
(3950003,300973,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Shadow King''s Lightblessed War Leggings'),
(3950003,320134,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Forgotten Briar Treads'),
(3950003,320711,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Silent Harness of Sky King'),
(3950003,320878,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Ebon War Mantle'),
(3950003,320970,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Frostmage''s Worldforged Shawl'),
(3950003,340104,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Devout Robe of the Star Caller'),
(3950003,340287,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Broken Warden''s Orb of the Frozen Memory'),
(3950003,340737,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Wyrm Queen''s Trousers'),
(3950003,360016,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | The Windforged Charm'),
(3950003,360710,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Iron Ray Shoes'),
(3950003,380354,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Traveling Cloak, Mana Sorrow'),
(3950003,380424,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Wolfcaller''s Shoulderguards'),
(3950003,380444,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Charm, Crimson Reach'),
(3950003,380620,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Frostmage''s Greenwood Wargrips'),
(3950003,380766,0,0,0,2,1,1,1,'Generated map_603_difficulty_1 boss_000747 | Titanguard''s Cinch');

DELETE FROM `creature_loot_template` WHERE `Entry` = 34003 AND `Item` = 2010000592 AND `Reference` = 3950000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(34003,2010000592,3950000,2,0,2,0,1,1,'Generated encounter attachment | map_603_difficulty_1 | boss_000744');

DELETE FROM `creature_loot_template` WHERE `Entry` = 33190 AND `Item` = 2010000593 AND `Reference` = 3950001;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(33190,2010000593,3950001,2,0,2,0,1,1,'Generated encounter attachment | map_603_difficulty_1 | boss_000745');

DELETE FROM `creature_loot_template` WHERE `Entry` = 33885 AND `Item` = 2010000594 AND `Reference` = 3950003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(33885,2010000594,3950003,2,0,2,0,1,1,'Generated encounter attachment | map_603_difficulty_1 | boss_000747');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3960002;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3960002,200004,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Scourge Keeper Great Gauntlets'),
(3960002,200056,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Tombwarden''s Starlit Warplate'),
(3960002,200061,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Warmarked Sollerets'),
(3960002,200098,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wildforged Pauldrons of Icecrown'),
(3960002,200227,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Legplates, Nether Moon'),
(3960002,200273,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Charm, Doom Hunter'),
(3960002,200381,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Manawoven War Leggings of the Lost Memory'),
(3960002,200451,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Witchlord''s Scourged Legplates'),
(3960002,200500,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Stonewarden''s Shawl'),
(3960002,200506,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Legplates, Starfire Flame'),
(3960002,200545,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Sabatons of Thunder King'),
(3960002,200649,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Cursed Iron Boots of the Hallowed Flame'),
(3960002,200713,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warforged Legplates of Death Knight'),
(3960002,200747,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Wolfmarked Clasp'),
(3960002,200759,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Argent Defender''s Battleplate'),
(3960002,200760,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warforged Gauntlets'),
(3960002,200842,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wolfheart Cry Legplates'),
(3960002,200862,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Graveborn Shieldwall'),
(3960002,200967,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Living Sollerets'),
(3960002,200997,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wildcaller''s Corrupted Great Gauntlets'),
(3960002,220005,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Corroded Gorget of Spellweaver'),
(3960002,220077,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Nightwoven Backcloth of the Northern King'),
(3960002,220083,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Cold Reaver Gauntlets'),
(3960002,220173,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Frost King''s Winterworn Charmstone'),
(3960002,220211,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Battleplate Legguards of Spellweaver'),
(3960002,220303,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Grim Shard Shoulderplates'),
(3960002,220348,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warforged Charmstone, Blademaster''s Oath'),
(3960002,220390,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Chestplate of the Scourge Lord'),
(3960002,220471,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Tempered Warhelm of the Iron March'),
(3960002,220473,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Heavenforged Locket'),
(3960002,220476,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Stoneward Gorget'),
(3960002,220596,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Frozen Warden''s Bleak Brooch'),
(3960002,220608,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Chestplate of the Northern Watch'),
(3960002,220621,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Colossal Scarab of Holy Oath'),
(3960002,220649,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Froststeel Armguards of the Wild King'),
(3960002,220668,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runesmith''s Promise'),
(3960002,220710,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Unholy Hoop of Star Forge'),
(3960002,220722,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Key of Dalaran'),
(3960002,220889,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Sun Crush Neckguard'),
(3960002,220914,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | War Greaves, Hallowed Bloom'),
(3960002,220973,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Radiant Wargrips of the Blood Promise'),
(3960002,240092,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wristguards of Halls of Stone'),
(3960002,240159,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Starforged Mark of the Dread Host'),
(3960002,240284,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Cryptkeeper''s Moonsteel Epaulets'),
(3960002,240292,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Everfrost Legmail'),
(3960002,240336,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Spaulders of Iron King'),
(3960002,240448,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Drakelord''s War Spear of the Emerald Moon'),
(3960002,240484,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Necrotic Partisan'),
(3960002,240514,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Spiritwarden''s Siegebound Shroud'),
(3960002,240516,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warbelt, Eagle Ritual'),
(3960002,240572,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Icecaller''s Belt'),
(3960002,240657,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Storm Queen''s Vambraces'),
(3960002,240766,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | War Leggings of the Ebon Banner'),
(3960002,240801,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Gauntlets, Sacred Light'),
(3960002,240818,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Dragon King''s Soldierly War Mantle'),
(3960002,240846,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Chainmail of the Stormcaller'),
(3960002,240876,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Armorsmith''s Leggings of the Storm Banner'),
(3960002,240974,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Starwarden''s Warhelm'),
(3960002,260005,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Soulmarked Wargrips'),
(3960002,260012,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Moonlit Collar of Frozen Heart'),
(3960002,260072,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Argent Champion''s War Claw of the Karazhan'),
(3960002,260090,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runelord''s Warlord War Mace'),
(3960002,260161,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Primeval Loop of the Demon Lord'),
(3960002,260214,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runelord''s Charmstone'),
(3960002,260253,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Mantle, Winter Vine'),
(3960002,260280,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Fernwoven Bracers of Shadow Crown'),
(3960002,260340,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Obsidian Hammer Coil'),
(3960002,260417,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Armored Totem'),
(3960002,260445,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Bindings, Titan Knuckle'),
(3960002,260493,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Winterborn Vest'),
(3960002,260559,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Rimelord''s Resolute Seal Ring'),
(3960002,260601,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Dragonsteel Carapace'),
(3960002,260611,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Harsh Shoulder Drape'),
(3960002,260645,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Deepfrost Vest'),
(3960002,260658,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Rootwoven War Claw'),
(3960002,260668,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Drake Quarrel Mark'),
(3960002,260685,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Pendant Chain of the Hidden Forge'),
(3960002,260724,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Mantle of the Sindragosa Fall'),
(3960002,260744,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Vicious Carapace'),
(3960002,260879,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Shortsword of the Iron Banner'),
(3960002,260961,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Waistguard, Pale Blade'),
(3960002,260982,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Stoneguard''s Locket of the Storm Peaks'),
(3960002,260983,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Forgemaster''s Locket of the Makers Will'),
(3960002,280025,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Permafrost Tiara'),
(3960002,280059,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Sacred Spirit Wand'),
(3960002,280076,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runebands, Crown Will'),
(3960002,280084,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Iron Queen''s Vestments'),
(3960002,280097,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Rune Queen''s Pants of the Mimiron Forge'),
(3960002,280122,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Raiment of the Storm Queen'),
(3960002,280124,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Cinch of Thorim Arena'),
(3960002,280136,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Trousers of the Iron King'),
(3960002,280232,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Siegebound Handwraps'),
(3960002,280261,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runebands of the Wintergarde'),
(3960002,280263,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wildlord''s Forsaken Skullcap'),
(3960002,280345,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Headdress of Ice Forge'),
(3960002,280399,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Shoulderpads, Dawn Ice'),
(3960002,280440,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Night Cleaver Skullcap'),
(3960002,280450,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Terrible Waistband of the Twilight Watch'),
(3960002,280507,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Icewarden''s Heavenforged Treads'),
(3960002,280539,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Tombwarden''s Headdress'),
(3960002,280558,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Firecaller''s Hoop of the Quel Thalas'),
(3960002,280574,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Dawnlit Gorget, Frostlord''s Oath'),
(3960002,280688,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Skirt of the Green Flame'),
(3960002,280724,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Ancient Queen''s Grimdark Grips'),
(3960002,280815,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Graveforged Kilt'),
(3960002,280838,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Stonebound Cinch, Sun King''s Oath'),
(3960002,280885,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Ebon Crusader''s Eternal Mantle'),
(3960002,280898,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Murderous Pants'),
(3960002,280960,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Lost Keeper''s Waistband of the First King'),
(3960002,300002,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warcloak of Wyrmskull'),
(3960002,300017,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Spellforged Warplate'),
(3960002,300020,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Amulet of the Amberpine Lodge'),
(3960002,300043,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Death Bane Footplates'),
(3960002,300051,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Stonekeeper''s Capelet'),
(3960002,300056,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Wildforged Carapace'),
(3960002,300066,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Ironkeeper''s Titanic Wristplates'),
(3960002,300098,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Shadowmarked Armplates of the Moon Pact'),
(3960002,300104,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Barbed Gauntlets'),
(3960002,300110,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wildfire Flare Warplate'),
(3960002,300137,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Choker of the Violet Citadel'),
(3960002,300168,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warblade of the Green Flight'),
(3960002,300187,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warsage''s Waistplate of the Dark Rider'),
(3960002,300196,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Graveforged Pauldrons'),
(3960002,300206,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Flamewarden''s Rootwoven Breastplate'),
(3960002,300216,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Gray Hammer'),
(3960002,300222,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Merciless Warbracers of the War Banner'),
(3960002,300246,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Icewarden''s Forgehammer'),
(3960002,300248,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Great Pauldrons, South Blood'),
(3960002,300253,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Scarlet Inquisitor''s Whitegold War Mace'),
(3960002,300279,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Battleplate of Ebon Crown'),
(3960002,300288,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Girdle, Grey Maw'),
(3960002,300296,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Battle Girdle of Holy Guard'),
(3960002,300313,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Dragonforged Spellblade of Ivory Crown'),
(3960002,300371,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Infused War Leggings'),
(3960002,300376,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wristplates, Iron Keeper'),
(3960002,300392,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Bracers of Engine of Makers'),
(3960002,300397,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Helm of Iron Pact'),
(3960002,300409,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Northforged Signet Ring of the Coldarra'),
(3960002,300414,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Titanbound Mantle of Ancient Night'),
(3960002,300416,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Warforged Great Pauldrons'),
(3960002,300424,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Bloodstained War Leggings of Voldrune'),
(3960002,300426,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Nightshrouded Battlecloak'),
(3960002,300438,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Bronze Chill Warplate'),
(3960002,300470,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wolfguard''s Capelet'),
(3960002,300535,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Stormbound Bracers'),
(3960002,300562,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Rootwoven Wristplates of the Zangarmarsh'),
(3960002,300571,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Savage Blood Great Pauldrons'),
(3960002,300591,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Torque of Burning Steppes'),
(3960002,300611,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Cryptkeeper''s Band of the Great Hunt'),
(3960002,300647,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runeguard''s Permafrost Greatcloak'),
(3960002,300749,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Fernwoven Battle Girdle'),
(3960002,300750,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | War Greaves, Low Gloom'),
(3960002,300759,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Weathered Pauldrons of the Black Anvil'),
(3960002,300762,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Visor of Shadow Crown'),
(3960002,300774,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warhelm of Thunder Forge'),
(3960002,300780,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Sollerets of the Western Plaguelands'),
(3960002,300808,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Glittering Reaver of the Blood Watch'),
(3960002,300811,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Earthkeeper''s Colossal Sabatons'),
(3960002,300835,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Hallowed Circle'),
(3960002,300851,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Witchkeeper''s Headplate'),
(3960002,300855,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Timeworn Great Gauntlets of the Blood Pact'),
(3960002,300876,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Frost King''s Shoulderplates'),
(3960002,300878,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warbelt of the Bone March'),
(3960002,300890,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Argent Crusader''s Greatsword'),
(3960002,300893,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runekeeper''s Merciless Signet Ring'),
(3960002,300896,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Grim Warden''s Legplates'),
(3960002,300904,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Great Pauldrons, Spear Forge'),
(3960002,300908,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Violet Mage''s Merciless Great Pauldrons'),
(3960002,300912,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Nightlord''s Mark of the Silent Crypt'),
(3960002,300930,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Drakecaller''s Legplates'),
(3960002,300947,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Breastplate of the Zangarmarsh'),
(3960002,300978,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Wrathful Waistplate'),
(3960002,300994,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Great Pauldrons of Sky Watch'),
(3960002,320067,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Helm of Dragon Forge'),
(3960002,320068,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Merciless Runestaff'),
(3960002,320108,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Grips, Black Wound'),
(3960002,320114,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Nameless Warden''s Ancient Relic'),
(3960002,320143,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Moonsteel Cape of Black Ritual'),
(3960002,320242,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Witchcaller''s Veil of the Northwatch'),
(3960002,320310,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Bright Handguards'),
(3960002,320359,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wolfcaller''s Neckchain'),
(3960002,320407,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Gravewarden''s Band'),
(3960002,320420,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Gravewarden''s Signet Ring'),
(3960002,320474,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wildwoven Wargrips'),
(3960002,320512,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Corrupted Signet of Blood Price'),
(3960002,320572,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Boneforged Bracers of the Void King'),
(3960002,320646,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Flameforged Mail'),
(3960002,320753,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Blazing Ring'),
(3960002,320804,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Moonkeeper''s Footguards of the Wyrm Forge'),
(3960002,340000,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Deepdelver Runed Wand of the Blue Flame'),
(3960002,340005,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Binding of Red Dragonflight'),
(3960002,340014,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Steelforged Gloves, Farseer''s Oath'),
(3960002,340154,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Lost Warden''s Leggings'),
(3960002,340213,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Warsage''s Earthen-forged Pants'),
(3960002,340218,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Broken Cleaver Seal'),
(3960002,340313,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Raiment of Frost Forge'),
(3960002,340433,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Anvilkeeper''s Cap'),
(3960002,340495,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Deep Crush Fang'),
(3960002,340544,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Icefang Forge Treads'),
(3960002,340554,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wyrmguard''s Emberwrought Spellblade'),
(3960002,340562,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Corrupted Shard'),
(3960002,340702,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Shoulderpads of the Argent Watch'),
(3960002,340710,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Vest of Spellweaver'),
(3960002,340729,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Bloodmage''s Crimson Charmstone'),
(3960002,340770,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Long Freeze Shoes'),
(3960002,340778,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Frost-rimed Bracelets'),
(3960002,340813,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Star Gaze Runebands'),
(3960002,340865,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Ebon Fang Oathring'),
(3960002,340891,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Hearthkeeper''s Vestments'),
(3960002,340970,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Regalia, High Veil'),
(3960002,340983,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Warmarked Mirror'),
(3960002,340993,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Frozen Queen''s Cloak'),
(3960002,360014,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Sash of Spider Wing'),
(3960002,360052,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Briarwoven Bracelets of the Rune King'),
(3960002,360056,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Drakescale Footwraps'),
(3960002,360097,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Hood of Serpent Spirit'),
(3960002,360115,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Sandals of the Final Stand'),
(3960002,360144,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Ghostcaller''s Dusty Runed Staff'),
(3960002,360156,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Firewarden''s Brassbound Treads'),
(3960002,360258,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Blighted Spell Scepter'),
(3960002,360290,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Seal of the Ebon Flame'),
(3960002,360310,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Runeforged Pants'),
(3960002,360369,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Brazen Figurine'),
(3960002,360373,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Lightblessed Mark of Ancient Watcher'),
(3960002,360389,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Northwarden''s Ghostly Graspers'),
(3960002,360390,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Graveborn Badge of Fallen Crown'),
(3960002,360472,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Graspers of Grim Oath'),
(3960002,360481,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Skirt, Dragon Guard'),
(3960002,360495,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Skyforged Stave of Broken Pact'),
(3960002,360583,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Frostbound Walkers'),
(3960002,360609,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Gloves, Star Scar'),
(3960002,360629,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Starlit Shoulder Cape of the Old Kingdom'),
(3960002,360691,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Boots of Drowned Hall'),
(3960002,360716,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Earthwarden''s Shoulderwraps'),
(3960002,360854,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Bright Hide Clasp'),
(3960002,360905,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Raiment, Silver Glaive'),
(3960002,360991,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Ironthane''s Eye'),
(3960002,360999,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Fanged Tiara'),
(3960002,380004,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Worldwarden''s Runed Shoulderguards'),
(3960002,380029,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Plaguekeeper''s Winterworn Legwraps'),
(3960002,380066,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Stormwarden''s Medallion'),
(3960002,380071,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Darkwarden''s Boots'),
(3960002,380074,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Lightblessed Headguard'),
(3960002,380114,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Dawncaller''s Shadowmarked Wristguards'),
(3960002,380226,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Runering of Grim Host'),
(3960002,380330,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Veil of the Deep Hall'),
(3960002,380448,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Trousers of Pale Crown'),
(3960002,380455,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wristbands of North Wind'),
(3960002,380616,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Scourgebound Tunic'),
(3960002,380665,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Winterguard''s Scale-bound Clutches'),
(3960002,380724,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Engraved Handguards of the Star Watch'),
(3960002,380808,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Wyrm Vow Cap'),
(3960002,380815,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Lightblessed Seer Staff of Lost Promise'),
(3960002,380830,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Rune King''s Watchful Mantle'),
(3960002,380953,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | Ironkeeper''s Violet Gemmed Band'),
(3960002,380961,0,0,0,1,1,1,1,'Generated map_604_difficulty_0 boss_000390 | The Terrible Druid Staff');

DELETE FROM `creature_loot_template` WHERE `Entry` = 29306 AND `Item` = 2010000595 AND `Reference` = 3960002;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(29306,2010000595,3960002,2,0,1,0,1,1,'Generated encounter attachment | map_604_difficulty_0 | boss_000390');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3970000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3970000,200456,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000383 | Ebon Storm Armguards'),
(3970000,300545,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000383 | Starcaller''s Dreambound Amulet'),
(3970000,300575,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000383 | Chestplate of Black Ice'),
(3970000,300681,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000383 | Greathelm of the Skorn'),
(3970000,320855,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000383 | Soulbound Effigy of Endless March'),
(3970000,360447,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000383 | Robes, Ice Rime');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3970003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3970003,300069,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000390 | The Corpsebound Headsman Axe'),
(3970003,300985,0,0,0,2,1,1,1,'Generated map_604_difficulty_1 boss_000390 | Dreaming Battleplate Legguards');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31370 AND `Item` = 2010000596 AND `Reference` = 3970000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31370,2010000596,3970000,2,0,2,0,1,1,'Generated encounter attachment | map_604_difficulty_1 | boss_000383');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31368 AND `Item` = 2010000597 AND `Reference` = 3970003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31368,2010000597,3970003,2,0,2,0,1,1,'Generated encounter attachment | map_604_difficulty_1 | boss_000390');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 3990000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3990000,200115,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000541 | Runekeeper''s Helm'),
(3990000,240349,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000541 | Starwoven Horn of the Argent Watch'),
(3990000,260871,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000541 | Wyrm King''s Bracers'),
(3990000,300498,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000541 | Icy Legplates of Quel Thalas'),
(3990000,340582,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000541 | Skullbound Wristwraps of Frozen Gate');

DELETE FROM `reference_loot_template` WHERE `Entry` = 3990003;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(3990003,220965,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000545 | Fanged Promise of the Sky Watch'),
(3990003,340566,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000545 | Luminous Vest of the Dark Portal'),
(3990003,340824,0,0,0,2,1,1,1,'Generated map_608_difficulty_1 boss_000545 | Great Cape of Emerald Wilds');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31507 AND `Item` = 2010000598 AND `Reference` = 3990000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31507,2010000598,3990000,2,0,2,0,1,1,'Generated encounter attachment | map_608_difficulty_1 | boss_000541');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31506 AND `Item` = 2010000599 AND `Reference` = 3990003;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31506,2010000599,3990003,2,0,2,0,1,1,'Generated encounter attachment | map_608_difficulty_1 | boss_000545');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4000000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4000000,300346,0,0,0,1,1,1,1,'Generated map_615_difficulty_0 boss_000742 | Choker, Nether Void'),
(4000000,380359,0,0,0,1,1,1,1,'Generated map_615_difficulty_0 boss_000742 | Runehammer of the Lost King');

DELETE FROM `creature_loot_template` WHERE `Entry` = 28860 AND `Item` = 2010000600 AND `Reference` = 4000000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(28860,2010000600,4000000,2,0,1,0,1,1,'Generated encounter attachment | map_615_difficulty_0 | boss_000742');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4010000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4010000,200764,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Starwoven Mallet of the Void King'),
(4010000,220231,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Sun King''s Warbelt'),
(4010000,240334,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Warboots of Frozen Halls'),
(4010000,240511,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Sunblessed Girdle of the Wild Watch'),
(4010000,260022,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Ebon Royal Cloak of the Crusader Watch'),
(4010000,260862,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Bright Horn Claws'),
(4010000,280547,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Scarlet Talon Mantle'),
(4010000,300038,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Silverwarden''s Sable Iron Boots'),
(4010000,300101,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Crusader''s Mark'),
(4010000,300285,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Ironwarden''s Howling Titanblade'),
(4010000,300323,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Torc of the Ebon Hold'),
(4010000,300735,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Argent Marshal''s Chestplate'),
(4010000,300849,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Capelet of the Rime Watch'),
(4010000,300858,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Highborne Charm of the Stormwind Keep'),
(4010000,300927,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Titan Fist Locket'),
(4010000,320061,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Argent Crusader''s Leggings'),
(4010000,320571,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Rimebound War Mantle, Lost Keeper''s Oath'),
(4010000,320687,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | The Starforged Footguards'),
(4010000,380291,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Sanctified Trousers of Fallen King'),
(4010000,380604,0,0,0,2,1,1,1,'Generated map_615_difficulty_1 boss_000742 | Mossbound Vest of Plague Watch');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31311 AND `Item` = 2010000601 AND `Reference` = 4010000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31311,2010000601,4010000,2,0,2,0,1,1,'Generated encounter attachment | map_615_difficulty_1 | boss_000742');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4030000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4030000,200093,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000212 | Bloodforged Necklace'),
(4030000,200136,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000212 | Doomed Waistguard'),
(4030000,260223,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000212 | Darkmoon Tunic of the Tempest Keep'),
(4030000,260569,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000212 | Eternal Cold Ring'),
(4030000,300586,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000212 | Wargrips, Falcon Storm'),
(4030000,340274,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000212 | Shoulder Drape of the Pit of Saron'),
(4030000,360178,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000212 | The Scourgebound Robe');

DELETE FROM `reference_loot_template` WHERE `Entry` = 4030004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4030004,300327,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000215 | Adamant Handguards of the Darkened Sun'),
(4030004,360072,0,0,0,2,1,1,1,'Generated map_619_difficulty_1 boss_000215 | Cap, Spider Thunder');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31456 AND `Item` = 2010000602 AND `Reference` = 4030000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31456,2010000602,4030000,2,0,2,0,1,1,'Generated encounter attachment | map_619_difficulty_1 | boss_000212');

DELETE FROM `creature_loot_template` WHERE `Entry` = 31464 AND `Item` = 2010000603 AND `Reference` = 4030004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(31464,2010000603,4030004,2,0,2,0,1,1,'Generated encounter attachment | map_619_difficulty_1 | boss_000215');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4060000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4060000,200270,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Waistguard of the Quel Thalas'),
(4060000,200433,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Drakewarden''s Coil of the Grim Host'),
(4060000,220612,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Runestone of Grim Watch'),
(4060000,240342,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Spaulders of the Black Flight'),
(4060000,240347,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Shadowbound Hauberk'),
(4060000,240357,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Warboots of the Old Road'),
(4060000,240683,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Starbound Helm'),
(4060000,240933,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Legguards of Iron Pact'),
(4060000,260102,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Circle, Blood Torment'),
(4060000,260282,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Boots, Plague Roar'),
(4060000,260730,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Merciless Shawl of Eternal Flame'),
(4060000,280286,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Nightcloak of Stone Crown'),
(4060000,280551,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Windbound Hammer'),
(4060000,280706,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | The Coldfire Shawl'),
(4060000,300128,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Silverguard''s Waistguard'),
(4060000,300297,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Gravelord''s Spellbound Legguards'),
(4060000,300399,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | The Fanged War Leggings'),
(4060000,300468,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Rune King''s Warplate'),
(4060000,300486,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Ironlord''s War Mace of the Freya Garden'),
(4060000,300505,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Earthcaller''s Royal Cloak'),
(4060000,300597,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Forgehammer, Dark Sorrow'),
(4060000,300601,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Battlemage''s Greaves'),
(4060000,300655,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Bloodsoaked Mark of the Frost Queen'),
(4060000,300812,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Starsteel War Leggings of the Rune Crown'),
(4060000,300898,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Medallion of Titan Keeper'),
(4060000,320535,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Winter Strike Waistchain'),
(4060000,320780,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Gauntlets of Golden Banner'),
(4060000,320915,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000845 | Earthshard Flame Rune Band');

DELETE FROM `reference_loot_template` WHERE `Entry` = 4060007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4060007,220604,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | War Leggings of the Frost Watch'),
(4060007,220778,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Deathkeeper''s Legguards'),
(4060007,240039,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Wargrips of the Dark Ritual'),
(4060007,240057,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Surcoat of the Dark Ritual'),
(4060007,260088,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Coldforged Longcloak'),
(4060007,280680,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Grips, Shadow Tooth'),
(4060007,300112,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Sunlit War Leggings of the Wyrm Forge'),
(4060007,300122,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Forgehammer of Silver Crown'),
(4060007,300971,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Frostmarked Charm'),
(4060007,320093,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Unwavering Waistchain of the Silver Crown'),
(4060007,320648,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Shieldguard''s Runebound Leggings'),
(4060007,340098,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Fire Moon Regalia'),
(4060007,360428,0,0,0,1,1,1,1,'Generated map_631_difficulty_0 boss_000856 | Runemarked Headdress');

DELETE FROM `creature_loot_template` WHERE `Entry` = 36612 AND `Item` = 2010000604 AND `Reference` = 4060000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(36612,2010000604,4060000,2,0,1,0,1,1,'Generated encounter attachment | map_631_difficulty_0 | boss_000845');

DELETE FROM `creature_loot_template` WHERE `Entry` = 36597 AND `Item` = 2010000605 AND `Reference` = 4060007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(36597,2010000605,4060007,2,0,1,0,1,1,'Generated encounter attachment | map_631_difficulty_0 | boss_000856');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4070005;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4070005,200771,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Bracers, Drake Talon'),
(4070005,220919,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Fetish of the Hearthguard'),
(4070005,240482,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | The Frozen Ring'),
(4070005,240523,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | The Merciless Kingsblade'),
(4070005,300151,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | War Leggings of Fallen Crown'),
(4070005,300273,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Old Warden''s Armplates of the Bone Gate'),
(4070005,300281,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Warbracers of Fel Watch'),
(4070005,300293,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Blacksmith''s War Hatchet'),
(4070005,300306,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Ironthane''s Handguards'),
(4070005,300484,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Winterguard''s Battleplate Legguards'),
(4070005,300895,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Warmaster Phylactery, Shadow Queen''s Oath'),
(4070005,320045,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Moonfire Cleaver Spirit Staff'),
(4070005,320825,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000851 | Band of Great Hunt');

DELETE FROM `reference_loot_template` WHERE `Entry` = 4070008;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4070008,380637,0,0,0,2,1,1,1,'Generated map_631_difficulty_1 boss_000856 | Harness of the Last Memory');

DELETE FROM `creature_loot_template` WHERE `Entry` = 38431 AND `Item` = 2010000606 AND `Reference` = 4070005;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(38431,2010000606,4070005,2,0,2,0,1,1,'Generated encounter attachment | map_631_difficulty_1 | boss_000851');

DELETE FROM `creature_loot_template` WHERE `Entry` = 39166 AND `Item` = 2010000607 AND `Reference` = 4070008;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(39166,2010000607,4070008,2,0,2,0,1,1,'Generated encounter attachment | map_631_difficulty_1 | boss_000856');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4080000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4080000,220350,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000845 | Chestplate of the Wyrm Queen'),
(4080000,220723,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000845 | Lightwarden''s Steelforged Waistplate'),
(4080000,240346,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000845 | Moonwoven Armguards of the Scale Queen'),
(4080000,280451,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000845 | Boar Glow Armbands'),
(4080000,320469,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000845 | Greaves of the Dead King'),
(4080000,340650,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000845 | Seal of Iron Dwarf'),
(4080000,380466,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000845 | Wintercaller''s Spellstaff');

DELETE FROM `reference_loot_template` WHERE `Entry` = 4080007;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4080007,300152,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000856 | Bitter Vambraces of Soul Crown'),
(4080007,300431,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000856 | Worldforged Helm of the Sun Flame'),
(4080007,360724,0,0,0,4,1,1,1,'Generated map_631_difficulty_2 boss_000856 | Kingsguard''s Bone of the Wild Heart');

DELETE FROM `creature_loot_template` WHERE `Entry` = 37958 AND `Item` = 2010000608 AND `Reference` = 4080000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(37958,2010000608,4080000,2,0,4,0,1,1,'Generated encounter attachment | map_631_difficulty_2 | boss_000845');

DELETE FROM `creature_loot_template` WHERE `Entry` = 39167 AND `Item` = 2010000609 AND `Reference` = 4080007;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(39167,2010000609,4080007,2,0,4,0,1,1,'Generated encounter attachment | map_631_difficulty_2 | boss_000856');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4090004;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4090004,240303,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Deathkeeper''s Circle of the Ebon Hold'),
(4090004,280373,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Ravenous Cudgel of the Makers Forge'),
(4090004,280422,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Ashkeeper''s Chestwrap of the Damned Host'),
(4090004,280942,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Soulshard Wake Bell'),
(4090004,300450,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Deathknight''s Ebon Seal Ring'),
(4090004,300769,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | The Holy Battleplate'),
(4090004,300996,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Wolfwarden''s Girdle'),
(4090004,320475,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Saronite Runering of the Mimiron Forge'),
(4090004,320828,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Vambraces of the Scarlet Flame'),
(4090004,340836,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Black Wound Binding'),
(4090004,360684,0,0,0,8,1,1,1,'Generated map_631_difficulty_3 boss_000851 | Diadem of Silver Covenant');

DELETE FROM `creature_loot_template` WHERE `Entry` = 38586 AND `Item` = 2010000610 AND `Reference` = 4090004;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(38586,2010000610,4090004,2,0,8,0,1,1,'Generated encounter attachment | map_631_difficulty_3 | boss_000851');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4100000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4100000,200904,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Frostmarked Footplates of Scarlet Watch'),
(4100000,240188,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Wolfguard''s Greaves'),
(4100000,240418,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Charmstone, Fierce Wind'),
(4100000,280496,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Gloves, Boar Rebuke'),
(4100000,300022,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Battlehammer of the Dark Crown'),
(4100000,300183,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | The Steadfast Visor'),
(4100000,300758,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Armored Helm'),
(4100000,300982,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Jagged War Sword of Bone Ritual'),
(4100000,320361,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Warhelm, Ancient Glaive'),
(4100000,320382,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Vanguard''s Waistguard of the Eagle Spirit'),
(4100000,320809,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Last Knight''s Corrupted Shoulder Guards'),
(4100000,340194,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Shoulderpads of the Green Flame'),
(4100000,340315,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Icon, Starfire Thirst'),
(4100000,360303,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | The Deathless Phylactery'),
(4100000,360597,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Footwraps, Sunfire Bloom'),
(4100000,360644,0,0,0,1,1,1,1,'Generated map_632_difficulty_0 boss_000829 | Spirit Ember Amulet');

DELETE FROM `creature_loot_template` WHERE `Entry` = 36497 AND `Item` = 2010000611 AND `Reference` = 4100000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(36497,2010000611,4100000,2,0,1,0,1,1,'Generated encounter attachment | map_632_difficulty_0 | boss_000829');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4110000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4110000,200447,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Rune Queen''s Silverblessed Pavise'),
(4110000,200749,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Sunkeeper''s Iron Boots'),
(4110000,220242,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Forgotten Knight''s Frostbitten Gemmed Band'),
(4110000,240150,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Ritual Band'),
(4110000,260291,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Cowl, North Quarrel'),
(4110000,260546,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Burnished Treads, Rimewalker''s Oath'),
(4110000,260965,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Warcloak of the Light Crown'),
(4110000,300169,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | The Gloomed Claymore'),
(4110000,300361,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | The Valiant Battleplate'),
(4110000,300533,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Greaves of Drake Rider'),
(4110000,300837,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Highkeeper''s Winterworn Wargrips'),
(4110000,320348,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Violet Mage''s Divine Wristguards'),
(4110000,340078,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Highguard''s Brutal Charmstone'),
(4110000,340570,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Mantle of Ancient Earth'),
(4110000,360384,0,0,0,2,1,1,1,'Generated map_632_difficulty_1 boss_000829 | Dark Bane Warband');

DELETE FROM `creature_loot_template` WHERE `Entry` = 36498 AND `Item` = 2010000612 AND `Reference` = 4110000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(36498,2010000612,4110000,2,0,2,0,1,1,'Generated encounter attachment | map_632_difficulty_1 | boss_000829');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4120000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4120000,300085,0,0,0,1,1,1,1,'Generated map_650_difficulty_0 script_SetData | Lost Knight''s Cuirass'),
(4120000,340295,0,0,0,1,1,1,1,'Generated map_650_difficulty_0 script_SetData | Runebands, Hidden Seal'),
(4120000,340919,0,0,0,1,1,1,1,'Generated map_650_difficulty_0 script_SetData | Corroded Breeches');

DELETE FROM `gameobject_loot_template` WHERE `Entry` = 27321 AND `Item` = 2010000613 AND `Reference` = 4120000;

INSERT INTO `gameobject_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(27321,2010000613,4120000,2,0,1,0,1,1,'Generated encounter attachment | map_650_difficulty_0 | script_SetData');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4130000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4130000,200039,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Sorrowful Warplate of the Dawn Star'),
(4130000,200998,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Stormkeeper''s Great Runeaxe'),
(4130000,220316,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Warcaller''s Ghostly Armplates'),
(4130000,220454,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Emerald Shot Warband'),
(4130000,260509,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Lightlord''s Cap of the Violet Watch'),
(4130000,300044,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | The Verdant Faceguard'),
(4130000,300082,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Hearthkeeper''s Thunderous Sollerets'),
(4130000,300123,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Greatblade of the Storm Crown'),
(4130000,300131,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Heavenforged Warbracers of the Pale Crown'),
(4130000,300686,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Flamekeeper''s Battlehelm'),
(4130000,340658,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Heavy Band of the Borean Tundra'),
(4130000,380255,0,0,0,2,1,1,1,'Generated map_650_difficulty_1 script_SetData | Heroic Great Stave of the Khaz Modan');

DELETE FROM `gameobject_loot_template` WHERE `Entry` = 27414 AND `Item` = 2010000614 AND `Reference` = 4130000;

INSERT INTO `gameobject_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(27414,2010000614,4130000,2,0,2,0,1,1,'Generated encounter attachment | map_650_difficulty_1 | script_SetData');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4140000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4140000,240499,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Austere Rune Band'),
(4140000,260197,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Spaulders of the Emerald Moon'),
(4140000,300095,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | West Talon Shoulderplates'),
(4140000,300554,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | The Ornate Battleplate Legguards'),
(4140000,300564,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Eagle Carver Battleplate Legguards'),
(4140000,300794,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Pendant Chain of Halls of Stone'),
(4140000,300842,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Shadowcaller''s Handplates'),
(4140000,340139,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Blackguard''s Heart of the Tirisfal Glades'),
(4140000,340237,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Dawnwarden''s Amulet of the Broken Road'),
(4140000,340676,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Mountainborn Walking Staff of Sable Crown'),
(4140000,360020,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | The Corpsebound Token'),
(4140000,360536,0,0,0,1,1,1,1,'Generated map_658_difficulty_0 boss_000833 | Mark, Scourge Spire');

DELETE FROM `creature_loot_template` WHERE `Entry` = 36494 AND `Item` = 2010000615 AND `Reference` = 4140000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(36494,2010000615,4140000,2,0,1,0,1,1,'Generated encounter attachment | map_658_difficulty_0 | boss_000833');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4150000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4150000,200371,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | The Dusty Ranseur'),
(4150000,200677,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Bear Edge Iron Mace'),
(4150000,220634,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Rootbound Handplates of Moon Path'),
(4150000,220860,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | The Coldfire Bracers'),
(4150000,240629,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Magekeeper''s Legmail of the Lost Memory'),
(4150000,260160,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Nightfang Blood Band'),
(4150000,300283,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Soul Glacier Cape'),
(4150000,300688,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Pendant Chain of High Citadel'),
(4150000,300730,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Frostworn Headplate of the New Agamand'),
(4150000,300753,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Thorn Night War Leggings'),
(4150000,300760,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | Witchkeeper''s Battlehelm'),
(4150000,360006,0,0,0,2,1,1,1,'Generated map_658_difficulty_1 boss_000833 | The Plagueforged Kilt');

DELETE FROM `creature_loot_template` WHERE `Entry` = 37613 AND `Item` = 2010000616 AND `Reference` = 4150000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(37613,2010000616,4150000,2,0,2,0,1,1,'Generated encounter attachment | map_658_difficulty_1 | boss_000833');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4160000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4160000,260654,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | Mantle of the Black Flight'),
(4160000,260883,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | Deathmarked Treads of Silver Dawn'),
(4160000,280244,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | Dreaming Mantle of the River Heart'),
(4160000,300106,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | The Ironthane Battleplate Legguards'),
(4160000,300405,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | Stormshard Gaze Greaves'),
(4160000,300538,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | The Scourgebound Signet'),
(4160000,300677,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | Gloomed Legguards of the Grizzlemaw'),
(4160000,380050,0,0,0,1,1,1,1,'Generated map_668_difficulty_0 boss_000839 | Armorsmith''s Warband');

DELETE FROM `creature_loot_template` WHERE `Entry` = 38113 AND `Item` = 2010000617 AND `Reference` = 4160000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(38113,2010000617,4160000,2,0,1,0,1,1,'Generated encounter attachment | map_668_difficulty_0 | boss_000839');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4170000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4170000,200099,0,0,0,2,1,1,1,'Generated map_668_difficulty_1 boss_000839 | Deathguard''s Emblem of the Ancient Thorn'),
(4170000,260064,0,0,0,2,1,1,1,'Generated map_668_difficulty_1 boss_000839 | The Briarbound Striders'),
(4170000,260265,0,0,0,2,1,1,1,'Generated map_668_difficulty_1 boss_000839 | Scarlet Inquisitor''s Shoulderguards'),
(4170000,300344,0,0,0,2,1,1,1,'Generated map_668_difficulty_1 boss_000839 | Armplates, Eagle Vengeance'),
(4170000,300559,0,0,0,2,1,1,1,'Generated map_668_difficulty_1 boss_000839 | Visor, East Spark'),
(4170000,380698,0,0,0,2,1,1,1,'Generated map_668_difficulty_1 boss_000839 | Unbroken Hail Royal Cloak');

DELETE FROM `creature_loot_template` WHERE `Entry` = 38603 AND `Item` = 2010000618 AND `Reference` = 4170000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(38603,2010000618,4170000,2,0,2,0,1,1,'Generated encounter attachment | map_668_difficulty_1 | boss_000839');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4180000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4180000,220143,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Ravenkeeper''s Waistguard of the Wyrmskull'),
(4180000,220705,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Warsage''s Manaforged Warplate'),
(4180000,260070,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Dwarven Vest of Gjalerbron'),
(4180000,260106,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Ancestor''s Mantle of the Dark Forge'),
(4180000,260174,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Iceforged Footguards of North Road'),
(4180000,260451,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Backcloth, Bright Glacier'),
(4180000,280736,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Hood of the Wyrm Lord'),
(4180000,300109,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Dusk Reach Greaves'),
(4180000,300308,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Bone, Forge Vigil'),
(4180000,300720,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Faceguard of Wild Watch'),
(4180000,300916,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Spellbound Fetish'),
(4180000,320006,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Armguards, Dread Brand'),
(4180000,360137,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Heart of Broken Crown'),
(4180000,360305,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Thorn Vine Token'),
(4180000,360410,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Wyrmwarden''s Leggings of the Dalaran'),
(4180000,380224,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Dreambound Rune Band of Naxxramas'),
(4180000,380531,0,0,0,1,1,1,1,'Generated map_724_difficulty_0 boss_000887 | Waistband of the Deep Vault');

DELETE FROM `creature_loot_template` WHERE `Entry` = 39863 AND `Item` = 2010000619 AND `Reference` = 4180000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(39863,2010000619,4180000,2,0,1,0,1,1,'Generated encounter attachment | map_724_difficulty_0 | boss_000887');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4190000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4190000,220593,0,0,0,2,1,1,1,'Generated map_724_difficulty_1 boss_000887 | Silversteel War Leggings of Violet Citadel'),
(4190000,300607,0,0,0,2,1,1,1,'Generated map_724_difficulty_1 boss_000887 | Sable Brand Chestplate'),
(4190000,300682,0,0,0,2,1,1,1,'Generated map_724_difficulty_1 boss_000887 | The Consecrated Girdle'),
(4190000,340018,0,0,0,2,1,1,1,'Generated map_724_difficulty_1 boss_000887 | Northborn Grips of the Valiance Keep');

DELETE FROM `creature_loot_template` WHERE `Entry` = 39864 AND `Item` = 2010000620 AND `Reference` = 4190000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(39864,2010000620,4190000,2,0,2,0,1,1,'Generated encounter attachment | map_724_difficulty_1 | boss_000887');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4200000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4200000,260268,0,0,0,4,1,1,1,'Generated map_724_difficulty_2 boss_000887 | Wyrmcaller''s Trousers'),
(4200000,300061,0,0,0,4,1,1,1,'Generated map_724_difficulty_2 boss_000887 | Sorcerous Great Gauntlets'),
(4200000,300592,0,0,0,4,1,1,1,'Generated map_724_difficulty_2 boss_000887 | Winterwarden''s Battleplate Legguards'),
(4200000,300752,0,0,0,4,1,1,1,'Generated map_724_difficulty_2 boss_000887 | Visor of the Deep Hall'),
(4200000,320634,0,0,0,4,1,1,1,'Generated map_724_difficulty_2 boss_000887 | Firecaller''s Rampart of the Coldarra'),
(4200000,340601,0,0,0,4,1,1,1,'Generated map_724_difficulty_2 boss_000887 | Ironthane''s Wyrmscale Spell Stave'),
(4200000,380369,0,0,0,4,1,1,1,'Generated map_724_difficulty_2 boss_000887 | Sun Queen''s Timeworn Talisman');

DELETE FROM `creature_loot_template` WHERE `Entry` = 39944 AND `Item` = 2010000621 AND `Reference` = 4200000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(39944,2010000621,4200000,2,0,4,0,1,1,'Generated encounter attachment | map_724_difficulty_2 | boss_000887');

COMMIT;

-- Generated encounter loot; existing loot rows remain independent.

START TRANSACTION;

DELETE FROM `reference_loot_template` WHERE `Entry` = 4210000;

INSERT INTO `reference_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(4210000,320085,0,0,0,8,1,1,1,'Generated map_724_difficulty_3 boss_000887 | Soul Ripper Surcoat');

DELETE FROM `creature_loot_template` WHERE `Entry` = 39945 AND `Item` = 2010000622 AND `Reference` = 4210000;

INSERT INTO `creature_loot_template`
(
    `Entry`,
    `Item`,
    `Reference`,
    `Chance`,
    `QuestRequired`,
    `LootMode`,
    `GroupId`,
    `MinCount`,
    `MaxCount`,
    `Comment`
)
VALUES
(39945,2010000622,4210000,2,0,8,0,1,1,'Generated encounter attachment | map_724_difficulty_3 | boss_000887');

COMMIT;
