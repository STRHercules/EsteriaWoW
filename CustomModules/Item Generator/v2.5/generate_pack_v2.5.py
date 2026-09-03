#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, math, os, re, shutil, struct, uuid, zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
USER_GUID_FILE = Path.home() / '.azerothcore-item-generator-guid'
SEED = None
OUT = None
SQLDIR = None
LOOT_CHANCE = None
WORLD_LOOT_SOURCE = None
REFERENCE_LOOT_SOURCE = None
ITEM_TEMPLATE_SOURCE = None
ITEM_DBC_SOURCES = None
ITEM_DBC_OVERWRITE = False
REFERENCE_CATALOG_AUDIT = None
BATCH_SIZE = 500
DEFAULT_TOTAL_ITEMS = 100_000
DEFAULT_ITEMS_PER_CLASS = 10_000
MAX_ITEMS_PER_CLASS = 20_000
MAX_TOTAL_ITEMS = 200_000
DEFAULT_WORLD_LOOT_SOURCE = REPO_ROOT / 'data' / 'sql' / 'base' / 'db_world' / 'creature_loot_template.sql'
DEFAULT_REFERENCE_LOOT_SOURCE = REPO_ROOT / 'data' / 'sql' / 'base' / 'db_world' / 'reference_loot_template.sql'
DEFAULT_ITEM_TEMPLATE_SOURCE = REPO_ROOT / 'data' / 'sql' / 'base' / 'db_world' / 'item_template.sql'
DEFAULT_ITEM_DBC_SOURCE = ROOT / 'Item.dbc'
DEFAULT_ITEM_DBC_CUSTOM_SOURCE = ROOT / 'Item.custom.dbc'
GENERATED_LOOT_POOL_BASE = 3_000_000
GENERATED_LOOT_ATTACHMENT_ITEM_BASE = 2_000_000_000
LOOT_BRACKETS = [
    ('01-19', 1, 19), ('20-39', 20, 39), ('40-59', 40, 59),
    ('60-69', 60, 69), ('70-79', 70, 79), ('80', 80, 80),
]
ACTIVE_CLASSES = None
TARGET_ITEM_COUNT = None
CLASS_ITEM_COUNTS = None

CLASSES = [
    ('Warrior',1,200000),('Paladin',2,220000),('Hunter',4,240000),('Rogue',8,260000),
    ('Priest',16,280000),('Death Knight',32,300000),('Shaman',64,320000),
    ('Mage',128,340000),('Warlock',256,360000),('Druid',1024,380000)
]

CLASS_ENTRY_START = {cname:start for cname,_,start in CLASSES}

def entry_for_class(cname, local_index):
    if not (0 <= local_index < MAX_ITEMS_PER_CLASS):
        raise ValueError(f'local item index out of range for {cname}: {local_index}')
    return CLASS_ENTRY_START[cname] + local_index
ROLE_WEIGHTS = {
    'Warrior': [('strength_dps',60),('tank',40)],
    'Paladin': [('strength_dps',45),('tank',30),('healer',25)],
    'Hunter': [('hunter',100)], 'Rogue': [('agility_dps',100)],
    'Priest': [('caster_dps',55),('healer',45)],
    'Death Knight': [('strength_dps',60),('tank',40)],
    'Shaman': [('agility_dps',40),('caster_dps',30),('healer',30)],
    'Mage': [('caster_dps',100)], 'Warlock': [('caster_dps',100)],
    'Druid': [('agility_dps',30),('caster_dps',25),('healer',25),('tank',20)],
}
SLOT_BASE = [('head',8),('neck',6),('shoulder',8),('back',6),('chest',10),('wrists',6),
             ('hands',8),('waist',8),('legs',10),('feet',8),('finger',7),('trinket',5),('weapon',10)]
STAT_ID = {'agi':3,'str':4,'int':5,'spirit':6,'stam':7,'def':12,'dodge':13,'parry':14,'block':15,
           'hit':31,'crit':32,'resil':35,'haste':36,'expertise':37,'ap':38,'rap':39,'mp5':43,
           'arp':44,'sp':45,'spellpen':47,'blockvalue':48}
STAT_COST = {'ap':0.5,'rap':0.5,'sp':0.8,'mp5':2.5,'blockvalue':0.65}
QUALITY_POWER={2:0.82,3:0.92,4:1.0,5:1.12}
QUALITY_NAME={2:'Uncommon',3:'Rare',4:'Epic',5:'Legendary'}
SLOT_BUDGET={'head':1.00,'neck':0.70,'shoulder':0.80,'back':0.65,'chest':1.15,'wrists':0.60,
             'hands':0.80,'waist':0.80,'legs':1.10,'feet':0.80,'finger':0.70,'trinket':0.85,
             'one_hand':0.75,'two_hand':1.10,'ranged':0.90,'shield':0.90,'relic':0.50}
INV={'head':1,'neck':2,'shoulder':3,'chest':5,'waist':6,'legs':7,'feet':8,'wrists':9,'hands':10,
     'finger':11,'trinket':12,'one_hand':13,'shield':14,'ranged':15,'back':16,'two_hand':17,
     'robe':20,'main_hand':21,'off_hand_weapon':22,'held_offhand':23,'thrown':25,'ranged_right':26,'relic':28}

# Curated display catalog: every (entry, displayid) pair below was read from the official
# AzerothCore WotLK item_template base table during construction of this pack.
# Format: entry, displayid, reference item level, reference quality.
A = {}
def add(key,*rows): A.setdefault(key,[]).extend(rows)
# Cloth armor
add(('armor',1,1),(7996,16548,20,1),(27488,44409,115,3))
add(('armor',1,3),(11310,5116,47,3),(41513,53090,134,2),(39719,55324,213,4))
add(('armor',1,20),(2572,12687,10,2),(2585,12669,21,2),(41515,53084,134,2),(41525,53084,150,3))
add(('armor',1,9),(3607,14161,10,1),(18337,30693,59,2),(41512,53082,134,2),(41528,53082,146,3))
add(('armor',1,10),(41516,55367,187,3))
add(('armor',1,6),(3606,14456,10,1),(4436,9912,21,2),(18327,30688,59,3))
add(('armor',1,7),(3834,16839,8,1),(27948,42448,115,3),(37189,52328,200,3),(39720,54703,213,4))
add(('armor',1,8),(2583,13524,19,2),(25957,43192,97,3),(27919,43003,112,3))
# Leather
add(('armor',2,1),(5753,8753,31,2),(22407,42208,61,3),(38437,52906,150,2))
add(('armor',2,3),(38402,49246,142,2))
add(('armor',2,5),(2300,9502,12,2),(2311,17233,13,2),(2314,9531,24,3),(4455,14261,33,2),(38400,52902,142,2),(38592,52938,175,3))
add(('armor',2,9),(18710,31159,50,3),(27483,42965,115,3),(38433,49256,150,2))
add(('armor',2,10),(2312,5406,15,2),(4239,9503,13,2),(4247,2362,29,2),(38403,49253,146,2))
add(('armor',2,6),(4237,9501,10,1),(4246,9513,16,2),(4456,17231,33,2),(38405,52584,146,2),(40205,54792,213,4))
add(('armor',2,7),(2303,9500,10,1),(4242,9505,15,2),(10410,28385,23,3),(38401,49794,146,2))
add(('armor',2,8),(2302,4713,8,1),(2307,17163,18,2),(2315,9530,20,2),(10411,27949,23,3),(18716,31166,61,3),(27914,42972,112,3),(38404,52901,142,2))
# Mail
add(('armor',3,1),(3836,25658,34,2),(11729,28826,57,3),(25955,45175,97,3),(37188,59543,200,3),(38439,51293,150,2),(38440,57541,150,2))
add(('armor',3,3),(3480,23531,22,2),(3840,9422,32,2),(4443,11327,36,2),(38424,52151,142,2))
add(('armor',3,5),(3844,13088,36,3),(3845,9425,40,2),(4448,4723,27,2),(7914,16080,32,2),(7963,16184,40,2),(8367,16729,51,3),(22985,33322,15,2),(27912,42944,115,3),(38414,57751,138,2),(44437,55018,171,3))
add(('armor',3,9),(3835,9417,33,2),(18711,31160,50,3),(25959,39485,96,2),(38435,56687,150,2),(38436,57750,150,2),(40209,57075,213,4))
add(('armor',3,10),(3483,9406,27,2),(3485,9414,30,2),(4465,6844,32,2),(11730,28723,57,3),(38415,52951,142,2),(39718,54622,213,4))
add(('armor',3,6),(5750,8749,23,2),(24388,43159,88,3),(38412,55193,138,2))
add(('armor',3,7),(3842,9415,31,2),(7920,3409,42,2),(7929,23538,42,2),(10423,19201,31,2),(11728,21694,57,3),(38416,51213,142,2),(44436,56673,167,3))
add(('armor',3,8),(3482,9404,26,2),(3484,9412,29,2),(3846,23537,37,2),(3847,9426,40,2),(4464,7002,32,2),(11731,28666,57,3),(25951,22680,99,2),(27915,42894,112,3),(38413,52950,146,2),(44438,56675,175,3))
# Plate
add(('armor',4,1),(7922,16093,43,3),(7934,16115,47,2),(7937,16119,49,2),(11746,21717,56,3),(18718,31167,63,3),(41344,52304,187,3))
add(('armor',4,3),(7918,16089,45,2),(7928,16106,45,2),(41351,51604,187,3))
add(('armor',4,5),(7930,16109,46,2),(7935,16117,48,2),(7939,24393,49,3),(41353,50991,187,3),(40203,54767,213,4),(40210,54768,213,4))
add(('armor',4,9),(18712,31161,50,3),(25956,43141,97,3),(25958,27420,96,2),(27489,42851,115,3),(27918,42847,112,3),(41354,51710,187,3))
add(('armor',4,10),(7919,16091,45,2),(7927,16105,45,2),(7938,16124,45,3),(11745,28740,56,3),(24387,43134,88,3),(41349,53110,187,3))
add(('armor',4,6),(27985,43042,115,3),(41352,53005,187,3),(40688,54051,200,4),(40689,54050,200,4))
add(('armor',4,7),(7921,16092,45,2),(7926,16103,45,2),(27487,42839,115,3),(41345,52996,187,3),(41347,53003,187,3),(37193,53810,200,4),(40204,51008,213,4))
add(('armor',4,8),(7933,16113,47,2),(7936,16118,49,2),(41348,53004,187,3),(39717,55393,213,4),(40206,55394,213,4))
# Cloak, jewelry, trinkets
add(('misc',1,16),(2310,23025,13,2),(2580,23133,12,2),(3833,23089,8,1),(5751,23078,25,2),(11311,28731,46,3),(18328,30689,59,3),(27485,15163,115,3),(27946,43099,115,3),(27981,31351,115,3),(27988,43100,112,3),(28371,43115,115,3),(28373,23119,115,3),(38441,56696,159,3),(44429,27088,156,4))
add(('misc',0,2),(5754,7093,31,2),(22403,9858,61,3),(22981,35373,83,4),(24385,31899,88,3),(40679,35437,200,4),(40680,35373,200,4),(40681,35359,200,4))
add(('misc',0,11),(5743,9842,40,2),(22979,6011,21,2),(37186,33808,200,3),(37192,49005,200,4),(37195,39122,200,3),(40717,33728,213,4),(40718,38541,213,4),(40719,44358,213,4),(40720,44086,213,4))
add(('misc',0,12),(11302,6515,52,3),(40682,53630,200,4),(40683,54045,200,4),(40684,29947,200,4),(40685,54046,200,4))
# Shields
add(('shield',6,14),(4444,18694,24,2),(4652,18789,45,2),(39716,56656,213,4))
# Relics
add(('relic',7,28),(22400,34961,57,3),(22401,34960,62,3),(22402,34959,78,4),(23006,34959,83,4),(23201,34960,65,3),(23203,34961,65,3),(24386,36578,88,3),(27484,5563,115,3),(27917,34961,112,3),(27949,34961,91,3))
add(('relic',8,28),(22397,34955,57,3),(22398,34954,62,3),(22399,34953,78,4),(23004,34953,83,4),(23197,34954,65,3),(23198,34955,65,3),(28372,43117,115,3),(40711,54481,200,4),(40712,54483,200,4),(40713,54484,200,4))
add(('relic',9,28),(22395,34957,57,3),(22396,34956,78,4),(23005,34956,83,4),(23199,34957,65,3),(23200,34956,65,3),(27947,25246,91,3),(40709,34956,200,4),(40710,34958,200,4))
add(('relic',10,28),(39208,51913,70,3),(40207,51913,213,4),(40714,51913,200,4),(40715,51913,200,4))

# Weapon appearance catalog and DPS anchors. Damage anchors are derived only from verified stock rows.
W = {}
def wadd(kind,*rows): W.setdefault(kind,[]).extend(rows)
# entry, display, ilvl, ref quality, ref delay (ms), min dmg, max dmg, school
wadd('1h_sword',(2131,22075,3,1,2600,2,4,0),(7943,16128,45,2,2600,48,90,0),(25952,39228,97,3,1500,61,114,0))
wadd('2h_sword',(3853,7324,36,2,2800,55,83,0),(28367,41789,115,3,3500,261,392,0))
wadd('1h_axe',(2134,22101,4,1,2000,2,4,0),(7941,16126,42,2,2700,45,85,0),(4445,19398,23,2,2300,18,35,0))
wadd('2h_axe',(3855,8528,37,2,3500,71,108,0),(27986,39958,115,3,3400,253,381,0))
wadd('1h_mace',(2492,12992,7,1,1800,3,7,0),(5757,8803,20,2,2600,18,34,0),(7945,5223,46,2,2400,46,86,0),(27980,41871,115,3,2000,100,187,0))
wadd('2h_mace',(5761,19544,5,1,3100,6,10,0),(41257,52966,200,4,3400,507,761,0))
wadd('polearm',(40208,54772,213,4,3600,586,880,0))
wadd('dagger',(4449,20439,27,2,1600,15,29,0),(5756,20591,37,3,1400,24,46,0),(7947,16130,51,2,1500,32,59,0),(27913,43097,115,3,1900,109,164,0),(39714,54757,213,4,1400,153,285,0))
wadd('staff',(35,472,2,1,2900,3,5,0),(4437,20390,20,2,3400,35,54,0),(22406,20384,61,3,2100,87,132,0),(25950,39226,97,3,2100,92,156,0),(44423,60816,245,4,2000,243,448,0),(44424,60804,245,4,2000,243,448,0))
wadd('fist',(11743,21714,55,3,1400,35,66,0),(11744,21715,56,3,1500,38,72,0))
wadd('bow',(25953,43202,97,3,2700,120,181,0),(27987,41791,112,3,3000,135,252,0))
wadd('gun',(24389,41427,88,3,3000,110,205,0))
wadd('crossbow',(24381,39059,91,3,2900,124,187,0))
wadd('wand',(18338,21016,59,3,1600,65,122,6),(23009,35262,83,4,1500,119,222,5),(28783,43915,125,4,1500,177,330,6),(39712,54697,213,4,1800,362,674,5),(44214,9063,187,3,1600,247,459,6))

WEAPON_META={
 '1h_sword':(7,13,'one_hand'), '2h_sword':(8,17,'two_hand'), '1h_axe':(0,13,'one_hand'), '2h_axe':(1,17,'two_hand'),
 '1h_mace':(4,13,'one_hand'),'2h_mace':(5,17,'two_hand'),'polearm':(6,17,'two_hand'),'dagger':(15,13,'one_hand'),
 'staff':(10,17,'two_hand'),'fist':(13,13,'one_hand'),'bow':(2,15,'ranged'),'gun':(3,26,'ranged'),
 'crossbow':(18,26,'ranged'),'wand':(19,26,'ranged')
}

THEMES = [
    'frost','scourge','titan','dragon','shadow','holy','arcane','nature',
    'dwarven','vrykul','nerubian','blood','argent','ebon','scarlet',
    'northrend','icecrown','ulduar','stormpeak','dragonblight','borean',
    'howling','grizzly','sholazar','zuldrak','wintergrasp','dalaran',
    'nexus','utgarde','gundrak','drakkari','frostborn','iron',
    'saronite','runic','plague','undead','crypt','bone','death',
    'spirit','storm','lightning','fire','ember','flame','earth',
    'stone','wild','moon','sun','star','twilight','dawn','dusk',
    'night','void','fel','demonic','abyssal','celestial','astral',
    'emerald','verdant','thorn','beast','wolf','bear','eagle','raven',
    'serpent','wyrm','drake','phoenix','lion','boar','mammoth','yak',
    'spider','scarab','mantid','troll','orcish','human','gnomish',
    'tauren','forsaken','kaldorei','sindorei','draenei','highborne',
    'stormwind','ironforge','orgrimmar','undercity','silvermoon',
    'exodar','darnassian','thunderbluff','gilnean','arathian',
    'lordaeron','quelthalas','khazmodan','alterac','stromgarde',
    'frostwolf','warsong','silverhand','kirintor','violet','sunreaver',
    'windrunner','wildhammer','bronzebeard','darkiron','earthen',
    'mechagnome','keeper','watcher','valkyr','runeblade','deathknight',
    'paladin','ranger','warden','shamanic','druidic','necromantic',
    'warlock','mage','priestly','berserker','gladiator','champion',
    'guardian','sentinel','crusader','inquisitor','templar','mystic',
    'prophet','oracle','seer','witch','ritual','ancestral','forgotten',
    'ancient','lost','cursed','haunted','hallowed','sacred','primeval',
    'primordial','relic','ruin','citadel','fortress','vault','temple',
    'sanctum','catacomb','barrow','tomb','sepulcher','forge','anvil',
    'mountain','glacier','tundra','wastes','fjord','forest','jungle',
    'swamp','desert','ocean','deep','sky','thunder','blizzard'
]

ADJ = [
    'Ashen','Runebound','Frostworn','Gilded','Grim','Silent','Ancient',
    'Hallowed','Blackened','Rimebound','Titanforged','Stormwrought',
    'Scarlet','Hollow','Sable','Ironbound','Moonlit','Dread','Wyrmhide',
    'Glacial','Stalwart','Shattered','Veiled','Radiant','Umbral','Rugged',
    'Tempered','Vengeful','Watchful','Serrated','Frozen','Duskwoven',
    'Sunblessed','Oathbound','Wild','Ebon','Crimson','Ivory','Azure',
    'Earthen','Runed','Gloomed','Savage','Haunted','Splintered',
    'Starforged','Mistbound','Boneclad','Winterborn','Emberwrought',
    'Stormbound','Thorned','Tarnished','Primal','Fel','Cryptborn',
    'Drakeforged','Saronite','Nerubian','Vrykul','Dalaran','Twilight',
    'Dawnforged','Kingsworn','Northwind','Icebound','Deathless',
    'Skyforged','Deepdelver','Stonehewn','Nightwoven','Brightsteel',
    'Coldbound','Warden','Ravenous','Soulbound','Wyrmbound','Ironclad',
    'Duskbound','Snowforged',
    'Adamant','Aged','Ancestral','Argent','Armored','Astral','Austere',
    'Baleful','Baneful','Barbed','Battleworn','Beastmarked','Blacksteel',
    'Blazing','Blessed','Blighted','Bloodied','Bloodforged','Bloodsoaked',
    'Bloodstained','Bonebound','Boneforged','Brassbound','Brazen',
    'Bright','Brilliant','Broken','Bronzed','Brutal','Burial','Burnished',
    'Cabalistic','Carved','Celestial','Charred','Chilled','Clouded',
    'Coldforged','Colossal','Consecrated','Corroded','Corrupted','Cracked',
    'Cruel','Cursed','Darkened','Darkforged','Darksteel','Dawnlit',
    'Deathforged','Deathmarked','Deepforged','Desecrated','Dire',
    'Dragonbound','Dragonforged','Dragonmarked','Drakescale','Dreadforged',
    'Dreambound','Dreamwoven','Dusklit','Earthbound','Earthforged',
    'Emberforged','Enchanted','Engraved','Eternal','Everfrost',
    'Faded','Fanged','Feral','Fireforged','Flamebound','Flameforged',
    'Flawless','Forsaken','Frostbitten','Frostbound','Frostforged',
    'Frostmarked','Frostscarred','Frostveined','Ghostly','Glittering',
    'Goldbound','Golden','Gravebound','Graveforged','Graven','Gray',
    'Greenwood','Hardened','Harsh','Heavenforged','Heavy','Hellforged',
    'Hexed','Highborne','Hoarfrost','Holy','Howling','Iceforged',
    'Icetouched','Infused','Ironforged','Jagged','Jeweled','Kingsguard',
    'Lightbound','Lightforged','Lightwoven','Living','Luminous',
    'Magebound','Moonbound','Moonforged','Moonwoven','Mournful',
    'Mystic','Nightbound','Nightforged','Nightmare','Nightshrouded',
    'Northborn','Northforged','Oathforged','Obsidian','Ornate',
    'Pale','Plaguebound','Plagueforged','Plaguetouched','Polished',
    'Primeval','Profane','Purified','Ravenbound','Razor-edged',
    'Reinforced','Relentless','Relicbound','Rimeforged','Ritual',
    'Royal','Rune-carved','Rune-etched','Runeforged','Runemarked',
    'Sacred','Sanctified','Scourgebound','Scourged','Shadowbound',
    'Shadowforged','Shadowmarked','Shadowwoven','Silvered','Silverforged',
    'Skullbound','Soulforged','Soulmarked','Spectral','Spellbound',
    'Spellforged','Spiritbound','Spiritforged','Starbound','Starlit',
    'Steelbound','Steelforged','Stonebound','Stoneforged','Stormforged',
    'Stormmarked','Stormscarred','Sunbound','Sunforged','Sunlit',
    'Thunderforged','Thunderous','Titanbound','Titanic','Tombbound',
    'Twilight-forged','Unbroken','Unhallowed','Unholy','Unyielding',
    'Valiant','Verdant','Voidbound','Voidforged','Warborn','Warforged',
    'Warmarked','Warscarred','Whispering','Whitegold','Wildforged',
    'Windbound','Windforged','Winterforged','Winterworn','Witchbound',
    'Witchforged','Wolfbound','Wolfhide','Wolfsworn','Worldforged',
    'Wyrmforged','Zealous',
    'Arctic','Bitter','Bleak','Blighted','Borean','Brittle','Cerulean',
    'Chillborn','Coal-black','Coldhearted','Deepfrost','Frost-rimed',
    'Glasslike','Hoary','Icy','Pale-blue','Permafrost','Rime-coated',
    'Snowbound','Snowy','Whitefrost','Wintertouched',
    'Arcane','Arcanized','Dreaming','Ethereal','Gleaming','Illusory',
    'Manaforged','Manawoven','Mystwoven','Runewoven','Sorcerous',
    'Spellscarred','Starwoven','Violet','Warped',
    'Bloodbound','Bloodmarked','Carrion','Corpsebound','Deathbound',
    'Deathly','Graveborn','Grimdark','Necrotic','Plagueborn',
    'Rotting','Scourgeforged','Sepulchral','Skullforged','Tombforged',
    'Undying','Unquiet',
    'Bearhide','Beastbound','Briarbound','Briarwoven','Clawmarked',
    'Earthwoven','Feathered','Fernwoven','Leafbound','Leafwoven',
    'Mossbound','Rootbound','Rootwoven','Thornbound','Thornwoven',
    'Wildbound','Wildwoven','Wolfmarked',
    'Crusader','Devout','Divine','Faithful','Lightblessed','Prayerbound',
    'Sainted','Silverblessed','Sunhallowed','Virtuous',
    'Berserker','Conqueror','Gladiatorial','Heroic','Marauding',
    'Merciless','Raider','Siegebound','Soldierly','Veteran','Warlord',
    'Warmaster','Warrior-forged',
    'Dwarven','Earthen-forged','Forgeblessed','Hammered','Ironthane',
    'Mountainborn','Runic','Stonecarved','Stoneward','Titan-carved',
    'Draconic','Drakebound','Dragonhide','Dragonsteel','Scale-bound',
    'Scalebound','Wyrmcarved','Wyrmscale',
    'Forgotten','Forsworn','Lost','Nameless','Old','Timeworn',
    'Weathered','Worldworn','Age-darkened','Dustbound','Dusty',
    'Brutish','Fierce','Ferocious','Hateful','Merciless','Pitiless',
    'Ruthless','Vicious','Wrathful','Furious','Murderous','Defiant',
    'Calm','Resolute','Solemn','Steadfast','Stoic','Unwavering',
    'Vigilant','Watchful','Patient','Enduring','Faithful',
    'Doomed','Doomforged','Dreadbound','Fearsome','Griefbound',
    'Mournbound','Ominous','Sinister','Sorrowful','Terrible',
    'Woe-bound','Woeful',
    'Brightmoon','Coldfire','Darkmoon','Dawnsteel','Duskrun',
    'Embersteel','Froststeel','Ghoststeel','Goldsteel','Moonsteel',
    'Nightsteel','Runesteel','Shadowsteel','Silversteel','Starsteel',
    'Stormsteel','Sunsteel','Thundersteel','Voidsteel','Wintersteel'
]
SUFFIX = [
    'Frozen Watch','Hollow King','North Wind','Last Vigil','Fallen Star',
    'Silent Crypt','Broken Crown','Winter Court','Old Gods','Storm Peaks',
    'Dragon Wastes','Ashen Oath','Raven Queen','Titan Vault','Dead March',
    'Crimson Dawn','Dusk Watch','Cold Hearth','Deep Forge','Moon Guard',
    'Scarlet Keep','Black Ice','Lost Vanguard','Iron Council','Shadow Vault',
    'Ancient Grove','Frostborn','Unquiet Dead','Sable Moon','Bone Wastes',
    'High Citadel','Runed Path','Final Watch','Frozen Throne','Twilight Reach',
    'Wild Hunt','Star Caller','Blood Moon','Silver Hand','Drowned Hall',
    'Storm Crown','Hallowed Flame','Emerald Dream','Dark Rider','Pale Winter',
    'Broken Spear','Long Night','Rimefang','Northwatch','Grim Host',
    'Deep Roads','Wyrmrest','Blue Dragon','Red Dragon','Black Dragon',
    'Bronze Dragon','Green Dragon','Forgotten Depths','Stone Fathers',
    'Frost Giant','Hearthguard','Icecrown','Howling Fjord','Borean Expanse',
    'Grizzly Hills','Dragonblight','Sholazar','Zul Drak','Wintergrasp',
    'Ulduar','Dalaran','Argent Watch','Ebon Hold','Nexus','Oculus',
    'Violet Hold','Gundrak','Azjol Nerub','Utgarde','Drak Tharon',
    'Old Kingdom','Frozen Sea','Stormcaller','Runekeeper','Soul Reaper',
    'Dread Wyrm','Bone Lord','Moonwarden','Earthshaper','Wildheart',
    'Spellweaver','Shadowbinder','Bloodguard','Frostguard','Dawnwatch',
    'Nightwatch','Crypt Watch',
    'Ancient Watch','Argent Dawn','Argent Vanguard','Ashen March',
    'Ashen Vale','Astral Gate','Autumn Wind','Azure Flame','Azure Moon',
    'Black Anvil','Black Citadel','Black Forge','Black Moon','Blackened Sky',
    'Bleak Shore','Blighted Land','Blood Crown','Blood Oath','Blood Price',
    'Blood Tide','Blood Watch','Blue Flame','Bone Crown','Bone Gate',
    'Bone March','Bone Throne','Broken Banner','Broken Blade','Broken Gate',
    'Broken Hall','Broken Oath','Broken Shield','Burning Crown',
    'Burning Sky','Burning Star','Celestial Gate','Cold Flame',
    'Cold Moon','Cold Watch','Crimson Crown','Crimson Flame','Crimson Moon',
    'Crimson Watch','Dark Crown','Dark Forge','Dark Moon','Dark Oath',
    'Dark Star','Darkened Sun','Dawn Guard','Dawn Oath','Dawn Star',
    'Dawn Vanguard','Dead King','Dead Watch','Death Gate','Death March',
    'Death Oath','Death Watch','Deep Anvil','Deep Earth','Deep Hall',
    'Deep Mountain','Deep Vault','Dragon Crown','Dragon Flame',
    'Dragon Forge','Dragon Guard','Dragon Oath','Dragon Queen','Dragon Throne',
    'Dread Crown','Dread Host','Dread March','Dread Watch','Drowned King',
    'Dying Light','Ebon Blade','Ebon Crown','Ebon Flame','Ebon March',
    'Ebon Watch','Emerald Grove','Emerald Moon','Emerald Star',
    'Endless Night','Endless Vigil','Eternal Flame','Eternal Watch',
    'Fallen Crown','Fallen King','Fallen Lord','Fallen Watch',
    'Far North','Final Dawn','Final Oath','Final Stand','First Flame',
    'First King','Forgotten King','Forgotten Oath','Forgotten Watch',
    'Frozen Crown','Frozen Forge','Frozen Gate','Frozen Heart',
    'Frozen King','Frozen Moon','Frozen North','Frozen Oath','Frozen Star',
    'Frost Crown','Frost Forge','Frost King','Frost Moon','Frost Oath',
    'Frost Queen','Frost Watch','Ghost King','Ghost Moon','Ghost Watch',
    'Gilded Crown','Golden Dawn','Golden Flame','Golden King','Golden Moon',
    'Grave King','Grave Watch','Great Forge','Great Hunt','Great North',
    'Green Flame','Grim Crown','Grim Dawn','Grim King','Grim March',
    'Grim Oath','Grim Watch','Hallowed Crown','Hallowed Ground',
    'Hallowed Oath','Hallowed Watch','Hidden Forge','Hidden King',
    'Hidden Path','Hidden Vault','High King','High Watch','Holy Flame',
    'Holy Oath','Howling North','Howling Wind','Ice Crown','Ice Forge',
    'Ice King','Ice Moon','Ice Queen','Iron Banner','Iron Crown',
    'Iron Forge','Iron Gate','Iron King','Iron March','Iron Oath',
    'Iron Watch','Ivory Crown','Last Dawn','Last King','Last Light',
    'Last Oath','Last Stand','Last Watch','Light Crown','Light Eternal',
    'Light Watch','Lost Crown','Lost King','Lost Oath','Lost Watch',
    'Midnight Crown','Midnight Flame','Midnight Moon','Midnight Watch',
    'Moon Crown','Moon Flame','Moon Oath','Moon Watch','Northern Crown',
    'Northern Forge','Northern King','Northern Light','Northern Watch',
    'Pale Crown','Pale Flame','Pale King','Pale Moon','Pale Watch',
    'Red Dawn','Red Dragonflight','Red Moon','Rime Crown','Rime Forge',
    'Rime King','Rime Watch','Rune Crown','Rune Forge','Rune King',
    'Rune Watch','Sacred Flame','Sacred Oath','Sable Crown','Sable Watch',
    'Scarlet Dawn','Scarlet Flame','Scarlet Oath','Scarlet Watch',
    'Shadow Crown','Shadow Forge','Shadow King','Shadow Moon',
    'Shadow Oath','Shadow Watch','Shattered Crown','Shattered Gate',
    'Shattered Oath','Silent Crown','Silent King','Silent Moon',
    'Silent Watch','Silver Crown','Silver Dawn','Silver Flame',
    'Silver Moon','Silver Oath','Silver Watch','Sky Crown','Sky Forge',
    'Sky King','Sky Watch','Soul Crown','Soul Forge','Soul King',
    'Soul Watch','Star Crown','Star Forge','Star King','Star Watch',
    'Stone Crown','Stone Forge','Stone King','Stone Watch','Storm Forge',
    'Storm King','Storm Oath','Storm Queen','Storm Watch','Sun Crown',
    'Sun Flame','Sun King','Sun Oath','Sun Watch','Thunder Crown',
    'Thunder Forge','Thunder King','Thunder Watch','Titan Crown',
    'Titan Forge','Titan King','Titan Watch','Twilight Crown',
    'Twilight Flame','Twilight Oath','Twilight Watch','Unbroken Oath',
    'Unending Watch','Unquiet King','Violet Crown','Violet Flame',
    'Violet Watch','Void Crown','Void Flame','Void King','Void Watch',
    'War Crown','War Forge','War King','War Oath','War Watch',
    'White Crown','White Flame','White Moon','Wild Crown','Wild King',
    'Wild Moon','Wild Watch','Wind Crown','Wind King','Wind Watch',
    'Winter Crown','Winter Forge','Winter King','Winter Moon',
    'Winter Oath','Winter Watch','Wyrm Crown','Wyrm Forge','Wyrm King',
    'Wyrm Oath','Wyrm Watch',
    'Argent Crusade','Ebon Vanguard','Violet Citadel','Kirin Tor',
    'Sunreaver Host','Silver Covenant','Frostwolf Clan','Warsong Clan',
    'Wildhammer Clan','Bronzebeard Clan','Dark Iron Clan',
    'Scarlet Crusade','Scarlet Monastery','Scarlet Bastion',
    'Stormwind Guard','Ironforge Guard','Orgrimmar Guard',
    'Dalaran Watch','Lordaeron Guard','Quel Thalas','Khaz Modan',
    'Arathi Highlands','Alterac Mountains','Stormwind Keep',
    'Ironforge Mountain','Undercity Depths','Silvermoon Spires',
    'Thunder Bluff','Exodar Crystal','Tirisfal Glades','Eastern Plaguelands',
    'Western Plaguelands','Stratholme','Scholomance','Blackrock Mountain',
    'Burning Steppes','Searing Gorge','Deadwind Pass','Dark Portal',
    'Hellfire Citadel','Shadowmoon Valley','Netherstorm','Blade Edge',
    'Nagrand','Terokkar','Zangarmarsh','Sunwell','Tempest Keep',
    'Black Temple','Karazhan','Mount Hyjal',
    'Borean Tundra','Coldarra','Amber Ledge','Warsong Hold',
    'Valiance Keep','Nesingwary Camp','Kaskala','Taunka Village',
    'Westguard Keep','Valgarde','New Agamand','Gjalerbron','Skorn',
    'Utgarde Keep','Utgarde Pinnacle','Kamagua','Wyrmskull',
    'Amberpine Lodge','Conquest Hold','Venture Bay','Drak Tharon Keep',
    'Grizzlemaw','Thor Modan','Voldrune','Light Breach','Ebon Watch',
    'Zim Torga','Altar of Sseratus','Gundrak Temple','Amphitheater',
    'Makers Terrace','Makers Overlook','River Heart','Frenzyheart Hill',
    'Rainspeaker Canopy','Avalanche','K3','Brunnhildar Village',
    'Sons of Hodir','Temple of Storms','Engine of Makers',
    'Halls of Stone','Halls of Lightning','Mimiron Forge','Freya Garden',
    'Thorim Arena','Hodir Hall','Yogg Prison','Titan Archive',
    'Argent Tournament','Crusaders Coliseum','Shadow Vault',
    'Death Rise','Onslaught Harbor','Sindragosa Fall','Corpse Scar',
    'Icecrown Citadel','Frozen Halls','Pit of Saron','Forge of Souls',
    'Halls of Reflection','Wrathgate','Wintergarde','Naxxramas',
    'Obsidian Sanctum','Ruby Sanctum','Eye of Eternity',
    'Blue Flight','Bronze Flight','Green Flight','Red Flight',
    'Black Flight','Infinite Flight','Dragon Queen','Dragon Aspect',
    'Wyrm Queen','Wyrm King','Drake Rider','Dragon Rider',
    'Scale Lord','Scale Queen','Wyrm Lord',
    'Ancient Earth','Ancient Flame','Ancient Frost','Ancient Night',
    'Ancient Storm','Ancient Titan','Ancient Watcher','Earthen King',
    'Earthen Watch','Iron Dwarf','Iron Giant','Stone Giant',
    'Titan Keeper','Titan Watcher','Prime Design','Makers Hand',
    'Makers Will','Makers Forge','Makers Vault',
    'Plague Lord','Plague Wing','Construct Wing','Military Wing',
    'Spider Wing','Frozen Heart','Death Knight','Death Lord',
    'Lich King','Crypt Lord','Bone Lord','Grave Lord','Scourge Lord',
    'Scourge Host','Scourge March','Scourge Watch','Plague Watch',
    'Damned Host','Restless Dead','Walking Dead','Nameless Dead',
    'Forgotten Dead','Frozen Dead',
    'Bear Spirit','Wolf Spirit','Eagle Spirit','Raven Spirit',
    'Serpent Spirit','Dragon Spirit','Earth Spirit','Fire Spirit',
    'Water Spirit','Wind Spirit','Storm Spirit','Ancestor Spirit',
    'Ancient Spirit','Wild Spirit','Moon Spirit','Sun Spirit',
    'Emerald Wilds','Emerald Grove','Emerald Path','Emerald Watch',
    'Ancient Oak','Ancient Thorn','Great Bear','Great Wolf',
    'Great Eagle','Wild Grove','Wild Path','Wild Heart',
    'Moon Grove','Moon Path','Moonwell','Star Grove',
    'Arcane Eye','Arcane Gate','Arcane Moon','Arcane Star',
    'Arcane Watch','Mana Forge','Mana Tide','Mana Wyrm',
    'Violet Eye','Violet Gate','Violet Star','Spellweaver',
    'Mage Lord','Mage Tower','Mystic Eye','Mystic Gate',
    'Astral Crown','Astral Gate','Astral Watch',
    'Light Dawn','Light Oath','Light Guard','Sacred Dawn',
    'Sacred Watch','Holy Crown','Holy Guard','Holy Watch',
    'Silver Light','Golden Light','Dawn Light','Divine Watch',
    'Crusader Oath','Crusader Watch','Paladin Oath',
    'Black Harvest','Black Ritual','Dark Ritual','Blood Ritual',
    'Bone Ritual','Fel Ritual','Shadow Ritual','Void Ritual',
    'Demon Lord','Demon Watch','Abyssal Flame','Abyssal Gate',
    'Burning Shadow','Burning Blood','Fel Flame','Fel Watch',
    'First Watch','Second Dawn','Final March','Endless March',
    'Endless Road','Endless Path','Long Road','Lost Road',
    'Silent Road','Forgotten Road','North Road','Frozen Road',
    'Kings Road','Old Road','Hidden Road','Broken Road',
    'Ancient Banner','Broken Banner','Crimson Banner','Ebon Banner',
    'Frozen Banner','Golden Banner','Iron Banner','Scarlet Banner',
    'Silver Banner','Storm Banner','War Banner','White Banner',
    'Ancient Pact','Ashen Pact','Blood Pact','Broken Pact',
    'Dragon Pact','Ebon Pact','Frozen Pact','Iron Pact','Moon Pact',
    'Shadow Pact','Silver Pact','Storm Pact','Titan Pact','Wild Pact',
    'Ancient Promise','Blood Promise','Broken Promise','Dying Promise',
    'Final Promise','Frozen Promise','Kings Promise','Last Promise',
    'Lost Promise','Silver Promise','Warriors Promise',
    'Ancient Memory','Bitter Memory','Blood Memory','Cold Memory',
    'Dead Memory','Distant Memory','Forgotten Memory','Frozen Memory',
    'Last Memory','Lost Memory','Old Memory','Winter Memory'
]
OWNER = [
    'Vanguard','Watchkeeper','Runesmith','Wyrmguard','Gravewarden',
    'Frostcaller','Stormcaller','Highborn','Wayfarer','Pathfinder',
    'Deathguard','Lightwarden','Spellbinder','Moonwarden','Earthwarden',
    'Ironthane','Shieldbearer','Cryptkeeper','Dawnkeeper','Nightwatcher',
    'Dragonstalker','Rimewalker','Boneguard','Starcaller','Ashen Lord',
    'Winter King','Pale Lady','Runemaster','Battlemage','Wildkeeper',
    'Soulwarden','Grim Warden','Northman','Titan Keeper','Violet Mage',
    'Argent Defender','Ebon Knight','Ice Witch','Blood Prince','Stonefather',

    'Ancestor','Anvilkeeper','Arcanist','Archmage','Armorsmith',
    'Ashcaller','Ashkeeper','Ashwarden','Battlelord','Battlemaiden',
    'Battlesage','Bearwarden','Blackguard','Blacksmith','Bladeguard',
    'Blademaster','Bloodcaller','Bloodguard','Bloodkeeper','Bloodknight',
    'Bloodmage','Bloodwarden','Bonecaller','Bonekeeper','Bonewarden',
    'Brightwarden','Crusader','Cryptlord','Darkcaller','Darkkeeper',
    'Darkrider','Darkwarden','Dawncaller','Dawnwarden','Deathcaller',
    'Deathkeeper','Deathknight','Deathlord','Deathwarden','Deepwarden',
    'Dragoncaller','Dragonkeeper','Dragonlord','Dragonwarden',
    'Drakecaller','Drakekeeper','Drakelord','Drakewarden','Dreamcaller',
    'Dreamkeeper','Dreamwarden','Duskcaller','Duskkeeper','Duskwarden',
    'Earthcaller','Earthkeeper','Embercaller','Emberkeeper','Emberwarden',
    'Farseer','Firecaller','Firekeeper','Firewarden','Flamecaller',
    'Flamekeeper','Flamewarden','Forgekeeper','Forgemaster','Frostguard',
    'Frostkeeper','Frostlord','Frostmage','Frostwarden','Ghostcaller',
    'Ghostkeeper','Ghostwarden','Gravecaller','Gravekeeper','Gravelord',
    'Grimkeeper','Grimlord','Hammerlord','Hearthkeeper','Hearthwarden',
    'Highguard','Highkeeper','Highlord','Icecaller','Icekeeper','Icewarden',
    'Ironcaller','Ironkeeper','Ironlord','Ironwarden','Kingsguard',
    'Kingskeeper','Lightcaller','Lightkeeper','Lightlord','Magekeeper',
    'Mooncaller','Moonkeeper','Moonlord','Nightcaller','Nightkeeper',
    'Nightlord','Northguard','Northkeeper','Northwarden','Oathkeeper',
    'Oathwarden','Plaguecaller','Plaguekeeper','Plaguelord','Plaguewarden',
    'Rangemaster','Ravenkeeper','Ravenlord','Ravenwarden','Rimecaller',
    'Rimekeeper','Rimelord','Rimewarden','Runecaller','Runeguard',
    'Runekeeper','Runelord','Runewarden','Seer','Shadowcaller',
    'Shadowguard','Shadowkeeper','Shadowlord','Shadowmage','Shadowwarden',
    'Shieldguard','Shieldmaster','Silverguard','Silverkeeper',
    'Silverwarden','Skullkeeper','Skullwarden','Soulcaller','Soulkeeper',
    'Soullord','Spiritcaller','Spiritkeeper','Spiritwarden','Starcaller',
    'Stargazer','Starkeeper','Starwarden','Stonecaller','Stoneguard',
    'Stonekeeper','Stonelord','Stonewarden','Stormguard','Stormkeeper',
    'Stormlord','Stormwarden','Sunkeeper','Sunwarden','Thunderkeeper',
    'Thunderlord','Thunderwarden','Titanforger','Titanguard','Titanwarden',
    'Tombkeeper','Tombwarden','Twilightcaller','Twilightkeeper',
    'Twilightwarden','Voidcaller','Voidkeeper','Voidlord','Voidwarden',
    'Warcaller','Warchief','Warden','Warguard','Warlord','Warmaster',
    'Warpriest','Warsage','Warwarden','Wildcaller','Wildguard',
    'Wildlord','Wildwarden','Windcaller','Windkeeper','Windlord',
    'Windwarden','Wintercaller','Winterguard','Winterkeeper',
    'Winterlord','Winterwarden','Witchcaller','Witchkeeper',
    'Witchlord','Wolfcaller','Wolfguard','Wolfkeeper','Wolfwarden',
    'Worldkeeper','Worldwarden','Wyrmcaller','Wyrmkeeper','Wyrmlord',
    'Wyrmwarden',

    'Argent Champion','Argent Crusader','Argent Knight','Argent Marshal',
    'Argent Templar','Ebon Champion','Ebon Crusader','Ebon Marshal',
    'Ebon Warden','Scarlet Champion','Scarlet Inquisitor',
    'Scarlet Marshal','Scarlet Templar','Violet Guardian',
    'Violet Keeper','Violet Warden',

    'Ancient King','Ancient Queen','Ashen King','Ashen Queen',
    'Blood King','Blood Queen','Dragon King','Dragon Queen',
    'Frost King','Frost Queen','Iron King','Iron Queen',
    'Moon King','Moon Queen','Rune King','Rune Queen',
    'Shadow King','Shadow Queen','Silver King','Silver Queen',
    'Storm King','Storm Queen','Sun King','Sun Queen',
    'Titan King','Titan Queen','Wyrm King','Wyrm Queen',

    'First Warden','Last Warden','Old Warden','Lost Warden',
    'Forgotten Warden','Nameless Warden','Silent Warden',
    'Frozen Warden','Ancient Warden','Broken Warden',

    'First Knight','Last Knight','Old Knight','Lost Knight',
    'Forgotten Knight','Silent Knight','Frozen Knight','Ancient Knight',

    'First Keeper','Last Keeper','Old Keeper','Lost Keeper',
    'Forgotten Keeper','Silent Keeper','Frozen Keeper','Ancient Keeper',

    'First King','Last King','Old King','Lost King','Forgotten King',
    'Silent King','Frozen King','Ancient King',

    'First Queen','Last Queen','Old Queen','Lost Queen','Forgotten Queen',
    'Silent Queen','Frozen Queen','Ancient Queen'
]
PROPER_A = [
    'Dread','Frost','Rime','Soul','Blood','Night','Star','Storm','Ash','Rune',
    'Ice','Bone','Moon','Dawn','Grim','Wyrm','Shadow','Iron','Stone','Winter',
    'Dragon','Crypt','Sky','Wild','Black','White','Silver','Gold','Ember',
    'Thunder','Void','Light','Earth','Death','Mist','North','Deep','Hollow',
    'Pale','Scarlet',

    'Argent','Azure','Bright','Bronze','Crimson','Dark','Dusk','Ebon',
    'Emerald','Fel','Fire','Flame','Ghost','Grave','Green','Holy','Ivory',
    'Obsidian','Red','Sable','Sun','Twilight','Violet','Wind',

    'Ancient','Broken','Cold','Doom','Dream','Eternal','Fallen','Forgotten',
    'Frozen','Hallowed','Hidden','Last','Lost','Prime','Primal','Sacred',
    'Shattered','Silent','Titan','Unbroken','Unholy','Unquiet',

    'Bear','Boar','Drake','Eagle','Falcon','Lion','Raven','Serpent',
    'Spider','Wolf',

    'Blade','Crown','Forge','Hammer','Oath','Shield','Skull','Spear',
    'Steel','Thorn',

    'Arcane','Astral','Celestial','Mystic','Spirit','Spell','Mana',
    'Plague','Scourge','Necro','Demon','Abyss','Nether',

    'North','South','East','West','High','Low','Far','Deep','Long',
    'Grey','Gray','Bright','Bleak','Bitter','Dire','Fierce','Savage',

    'Sunfire','Moonfire','Coldfire','Darkfire','Starfire','Soulfire',
    'Bloodfire','Ghostfire','Frostfire','Wildfire',

    'Earthshard','Stormshard','Soulshard','Voidshard','Icefang',
    'Bloodfang','Nightfang','Starfang','Wolfheart','Lionheart'
]
PROPER_B = [
    'fang','song','reaver','caller','breaker','watch','edge','guard','bane',
    'heart','spire','claw','bite','ward','oath','brand','whisper','howl',
    'strike','fall','shard','grip','veil','crown','doom','keeper','march',
    'wrath','vigil','reach','thorn','gaze','lament','wake','echo','talon',
    'fury','promise','rebuke','memory',

    'blade','blood','bolt','brand','breath','bringerless','carver','cleaver',
    'cry','dancer','dawn','death','dream','fire','flame','forge','frost',
    'glaive','grasp','hammer','hand','hide','horn','hunter','keeper',
    'light','lord','maw','moon','night','oath','piercer','rage','rend',
    'rider','ripper','roar','scar','scream','shade','shadow','shield',
    'singer','skull','slayer','sorrow','spear','spell','spirit','star',
    'steel','storm','sun','thirst','tongue','tooth','vengeance','voice',
    'walker','warden','wind','wing','winter','wolf','wound','wyrm',

    'ash','bloom','branch','briar','ember','feather','leaf','root','seed',
    'vine',

    'chain','crush','guard','helm','mail','plate','wall',

    'curse','hex','ritual','sigil','rune','glyph','mark','seal',

    'dusk','gloom','grave','mist','rime','snow','thunder','twilight',
    'void',

    'banner','covenant','creed','decree','legacy','pact','pledge',
    'vow','will',

    'chill','cold','freeze','glacier','hail','ice','storm','snowfall',

    'beacon','flare','glow','ray','shine','spark','starfall',

    'doom','fate','judgment','reckoning','ruin','torment','woe',

    'anchor','anvil','forge','hammer','stone','vault',

    'arrow','bolt','shot','string','quarrel',

    'clutch','fist','knuckle','punch','talon',

    'dirge','hymn','requiem','song','verse','whisper'
]
BASE_BY_SLOT = {
    'head': [
        'Helm','Cowl','Crown','Hood','Faceguard','Circlet','Greathelm',
        'Warhelm','Visor','Mask','Headguard','Coif','Cap','Headdress',
        'Diadem','Skullcap','Headpiece','Casque','Browguard','Crest',
        'Headplate','War Hood','Battlehelm','Deathmask','Tiara'
    ],

    'neck': [
        'Pendant','Choker','Amulet','Gorget','Necklace','Chain','Torc',
        'Locket','Collar','Medallion','Talisman','Charm','Beads',
        'Neckguard','Clasp','Charmstone','Torque','Neckchain','Brooch',
        'Pendant Chain'
    ],

    'shoulder': [
        'Pauldrons','Mantle','Spaulders','Shoulderguards','Shoulderpads',
        'Epaulets','Shoulderplates','Shoulder Guards','War Pauldrons',
        'Battle Mantle','Shoulder Armor','Great Pauldrons','Armplates',
        'Shoulderwraps','Shoulder Cape','Mantleplates','Wings',
        'War Mantle','Great Spaulders','Shoulderward'
    ],

    'back': [
        'Cloak','Cape','Shroud','Drape','Mantle','Wrap','Veil',
        'Greatcloak','Warcloak','Shawl','Capelet','Great Cape',
        'Battlecloak','Longcloak','Nightcloak','Traveling Cloak',
        'Shoulder Drape','Backcloth','Warder Cloak','Royal Cloak'
    ],

    'chest': [
        'Breastplate','Chestguard','Tunic','Hauberk','Robe','Vestments',
        'Jerkin','Chestpiece','Carapace','Cuirass','Armor','Mail',
        'Coat','Raiment','Regalia','Plate','Chainmail','Battleplate',
        'Warplate','Chestplate','Greatcoat','Surcoat','Harness',
        'Battle Harness','War Tunic','Robes','Battle Robes','Vest',
        'Chestwrap','Great Hauberk'
    ],

    'wrists': [
        'Bracers','Wristguards','Bindings','Vambraces','Cuffs','Armbands',
        'Wristwraps','Manacles','Wristplates','Wristbands','Bracelets',
        'Armguards','Forearm Guards','Wrist Armor','Battle Bracers',
        'Runebands','Warbracers','Wrist Chains','Armlets','Wristward'
    ],

    'hands': [
        'Gauntlets','Gloves','Handguards','Grips','Fists','Handwraps',
        'Graspers','Clutches','Mitts','Knuckles','Handplates',
        'Battle Gloves','War Gloves','Great Gauntlets','Claws',
        'Hand Armor','Grasp','Wargrips','Fingerguards','Handward'
    ],

    'waist': [
        'Girdle','Belt','Waistguard','Cord','Sash','Chain','Cinch',
        'Waistband','Buckle','Strap','Binding','Warbelt','Greatbelt',
        'Battle Girdle','Waistplate','Waistwrap','War Girdle',
        'Battle Belt','Hipguard','Waistchain'
    ],

    'legs': [
        'Legplates','Legguards','Leggings','Trousers','Kilt','Pants',
        'Breeches','Chausses','Legwraps','Leg Armor','Battle Leggings',
        'War Leggings','Greaves','Legplates','Legmail','Leggings',
        'Legguards','Battleplate Legguards','War Trousers','Legward',
        'Skirt','War Kilt','Battle Kilt','Leg Harness'
    ],

    'feet': [
        'Sabatons','Boots','Greaves','Treads','Footguards','Sollerets',
        'Stompers','Walkers','Footwraps','Sandals','Warboots','Striders',
        'Battle Boots','Greatboots','Footplates','War Treads',
        'Battle Treads','Shoes','Stalkers','Footward','Marching Boots',
        'Iron Boots','Riding Boots','War Greaves'
    ],

    'finger': [
        'Band','Signet','Ring','Seal','Loop','Hoop','Circle','Coil',
        'Promise','Mark','Ringlet','Fingerband','Oathring','Runering',
        'Signet Ring','Seal Ring','Warband','Gemmed Band','Royal Band',
        'Rune Band'
    ],

    'trinket': [
        'Talisman','Charm','Medallion','Token','Icon','Emblem','Figurine',
        'Keepsake','Badge','Insignia','Shard','Stone','Lens','Compass',
        'Hourglass','Coin','Seal','Charmstone','Runestone','Crystal',
        'Orb','Idol','Totem','Relic','Fetish','Effigy','Mirror',
        'Phylactery','Vial','Flask','Horn','Bell','Key','Tablet',
        'Scarab','Eye','Heart','Skull','Bone','Feather','Scale'
    ],

    'shield': [
        'Bulwark','Shield','Aegis','Buckler','Barrier','Guard','Defender',
        'Wall','Tower Shield','Ward','Protector','Targe','Warshield',
        'Greatshield','Battle Shield','Wallshield','Shieldwall',
        'Rampart','Barricade','Pavise','Battlewall','Great Aegis'
    ],

    'relic': [
        'Relic','Idol','Totem','Libram','Sigil','Runestone','Tablet',
        'Icon','Effigy','Symbol','Inscription','Rune','Fetish',
        'Sacred Relic','Ancient Relic','War Relic','Spirit Relic',
        'Runed Relic','Stone Relic','Carved Relic','Ritual Relic'
    ]
}
BASE_BY_WEAPON = {
    '1h_sword': [
        'Blade','Longsword','Saber','Scimitar','Broadsword','Falchion',
        'Shortsword','Runeblade','Warblade','Edge','Brand','Spellblade',
        'Reaver','Slasher','Cutlass','Warsword','Battleblade',
        'Runesword','Knightblade','Kingsblade','Steelblade','Sword',
        'War Sword','Rider Blade'
    ],

    '2h_sword': [
        'Greatsword','Claymore','Warblade','Greatblade','Zweihander',
        'Runeblade','War Sword','Great Warblade','Longblade',
        'Execution Blade','Battle Greatsword','Runesword','Kingsblade',
        'Colossal Blade','Highblade','Great Claymore','War Cleaver',
        'Titanblade','Great Runeblade','Champion Blade'
    ],

    '1h_axe': [
        'Axe','Hatchet','Cleaver','Handaxe','Chopper','Tomahawk',
        'Battle Axe','War Axe','Bearded Axe','Hand Cleaver',
        'Runic Axe','Raider Axe','Skull Axe','War Hatchet',
        'Headsman Axe','Fang Axe','Runeaxe','Broad Axe','Iron Axe',
        'Battle Hatchet'
    ],

    '2h_axe': [
        'Greataxe','War Axe','Decapitator','Battleaxe','Executioner',
        'Great Cleaver','Reaver','Headsman','Bearded Axe','War Cleaver',
        'Great Battleaxe','Runic Greataxe','Titan Axe','Skullsplitter',
        'Great Chopper','Execution Axe','Raider Greataxe','War Reaver',
        'Grand Axe','Great Runeaxe'
    ],

    '1h_mace': [
        'Mace','Hammer','Warhammer','Cudgel','Mallet','Scepter',
        'Morningstar','Flanged Mace','Crusher','Battle Mace',
        'War Mace','Runehammer','Stonehammer','Skullcrusher',
        'Clublike Mace','Iron Mace','Battlehammer','Hand Hammer',
        'Maul','Knobbed Mace'
    ],

    '2h_mace': [
        'Maul','Sledge','Great Hammer','War Maul','Earthshaker',
        'Crusher','Grand Mace','Stonehammer','Runemaul','Battle Hammer',
        'Great Maul','Titan Hammer','Great Warhammer','Skullcrusher',
        'Bonecrusher','Siege Hammer','Forgehammer','Thunder Hammer',
        'Grand Warhammer','Colossal Maul'
    ],

    'polearm': [
        'Glaive','Halberd','Spear','Pike','Lance','Partisan','Trident',
        'War Spear','Ranseur','Harpoon','Longspear','Voulge','Scythe',
        'Battle Glaive','War Halberd','Runespear','Dragon Spear',
        'Great Lance','War Pike','Poleblade','Long Glaive','War Scythe'
    ],

    'dagger': [
        'Dagger','Dirk','Shiv','Knife','Stiletto','Blade','Shanker',
        'Pricker','Ritual Knife','Tooth','Fang','Spike','Kris','Bodkin',
        'Poniard','Rondel','Skinner','Carver','Assassin Blade',
        'War Dagger','Rune Dagger','Spellknife','Shadowblade','Piercer'
    ],

    'staff': [
        'Staff','Stave','Spire','Quarterstaff','Warstaff','Runestaff',
        'Walking Staff','Greatstaff','Crook','Rod','Branch','Pillar',
        'Mage Staff','Battle Staff','Spellstaff','Spirit Staff',
        'Runed Staff','Longstaff','Archmage Staff','Seer Staff',
        'Druid Staff','Shaman Staff','Great Stave','Spell Stave'
    ],

    'fist': [
        'Claw','Fist','Knuckle','Talon','Cestus','Handblade',
        'Punchblade','Clawblade','Knuckles','Gauntlet','Jaw','Scratcher',
        'War Claw','Battle Fist','Hand Claw','Fang','Ripper',
        'Steel Fist','Iron Claw','Bladefist','War Talon','Battle Claw'
    ],

    'bow': [
        'Longbow','Recurve','Warbow','Shortbow','Greatbow','Composite Bow',
        'Hornbow','Longshot','Hunting Bow','Battle Bow','War Bow',
        'Ranger Bow','Runebow','Bone Bow','Dragonbow','Great Warbow',
        'Siegebow','Long Recurve','Hunter Bow','Scout Bow','Warden Bow'
    ],

    'gun': [
        'Rifle','Musket','Hand Cannon','Blunderbuss','Long Rifle',
        'Scattergun','Carbine','Firearm','Thunderstick','Boomstick',
        'War Rifle','Hunting Rifle','Battle Rifle','Long Gun',
        'Repeating Rifle','Great Rifle','Marksman Rifle','Dwarven Rifle',
        'Iron Rifle','Siege Gun','Runegun','War Musket'
    ],

    'crossbow': [
        'Crossbow','Arbalest','Repeater','Heavy Crossbow','Siege Crossbow',
        'Bolt Thrower','Windlass','War Crossbow','Sniper Crossbow',
        'Crankbow','Great Crossbow','Battle Crossbow','Hunter Crossbow',
        'Repeating Crossbow','Bone Crossbow','Runed Crossbow',
        'Steel Crossbow','Long Crossbow','Marksman Crossbow','War Arbalest'
    ],

    'wand': [
        'Wand','Rod','Scepter','Spellwand','Focus','Channeling Rod',
        'Runewand','Arcane Rod','Hexing Rod','Conduit','Spellrod',
        'Runed Wand','Mage Wand','Mystic Wand','Spirit Wand',
        'Bone Wand','Crystal Wand','Star Wand','Moon Wand','Ritual Wand',
        'Sorcerer Rod','Runic Rod','Spell Scepter','Arcane Scepter'
    ]
}

FLAVOR = [
    'It carries the chill of the northern wastes.',
    'Runes along its edge are cold to the touch.',
    'Its maker left no name behind.',
    'The metal hums softly beneath an open sky.',
    'A relic of a war no bard remembers.',
    'Frost clings to it even beside a warm hearth.',
    'The workmanship bears the marks of an old northern forge.',
    'Its surface is scarred by years of hard fighting.',
    'A faint blue light lingers within the metal.',
    'The runes have been worn smooth by countless hands.',
    'Something about it recalls distant thunder.',
    'A cold wind seems to follow in its wake.',

    'Tiny runes pulse beneath its weathered surface.',
    'No hammer marks can be found anywhere upon it.',
    'Its surface remains strangely warm despite the cold.',
    'A thin layer of frost returns whenever it is wiped away.',
    'The metal bears scars from battles long forgotten.',
    'A faint ringing can be heard when moonlight strikes it.',
    'Its edges have been polished by decades of use.',
    'A nearly forgotten crest remains visible beneath the scratches.',
    'The craftsmanship suggests a forge far older than its owner.',
    'A scent of smoke and pine clings stubbornly to it.',
    'Its runes glow briefly whenever thunder rolls nearby.',
    'A faint shimmer passes across its surface at dusk.',
    'The metal seems heavier than its size would suggest.',
    'The metal seems lighter than its size would suggest.',
    'A chill runs through the hand of anyone who first touches it.',
    'Its surface reflects stars that are not visible overhead.',
    'Fine silver threads form ancient patterns across its surface.',
    'The craftsmanship is unmistakably northern.',
    'The markings resemble those found in forgotten titan ruins.',
    'A fragment of an old oath has been carved into its surface.',
    'Time has worn most of its inscription beyond recognition.',
    'Someone carefully scratched a tally of victories into it.',
    'A shallow gouge marks where a killing blow once landed.',
    'Its original owner appears to have removed every identifying mark.',
    'The leather still smells faintly of cedar and smoke.',
    'Faint claw marks run along one side.',
    'Its metalwork bears the unmistakable touch of a master smith.',
    'The final rune remains unfinished.',
    'A single black feather is tied to it with faded cord.',
    'A tiny silver bell hangs from a worn leather thong.',
    'Its surface is covered in nearly invisible prayer marks.',
    'A faded battlefield blessing remains etched into the metal.',
    'A dark stain refuses every attempt to polish it away.',
    'The metal glitters as though dusted with fresh snow.',
    'The runes become clearer beneath starlight.',
    'A faint heartbeat seems to echo from somewhere within.',
    'The leather has been repaired many times by different hands.',
    'Its clasp bears the symbol of a long-dead household.',
    'A tiny maker mark is hidden beneath one edge.',
    'Someone has carefully filed away the maker mark.',
    'Its surface is unnaturally smooth.',
    'A thin crack runs through the oldest rune.',
    'The metal produces a low note when struck.',
    'The engraving depicts mountains beneath a winter moon.',
    'Its engraving shows a dragon circling a distant tower.',
    'Its engraving shows warriors marching beneath falling snow.',
    'Its engraving depicts an ancient tree surrounded by stars.',
    'Its engraving shows a lone rider crossing a frozen plain.',
    'Its engraving depicts a hammer resting upon an anvil.',
    'Its engraving depicts a raven perched upon a broken crown.',
    'Its engraving depicts a wolf beneath the northern lights.',
    'Its engraving depicts an eye surrounded by runes.',
    'Its engraving depicts a shattered fortress beneath a dark moon.',
    'Its engraving depicts a ship lost among frozen waves.',
    'Its engraving depicts a serpent wrapped around a spear.',
    'Its engraving depicts a bear standing before a mountain.',
    'Its engraving depicts a dragon sleeping beneath the earth.',
    'Its engraving depicts seven stars surrounding a single flame.',

    'The runes whisper softly when no one else is nearby.',
    'A faint whisper follows anyone who carries it for too long.',
    'It occasionally feels as though someone else is holding it.',
    'Its shadow does not always fall in the expected direction.',
    'The air around it smells briefly of fresh snow.',
    'The air around it smells briefly of rain.',
    'The air around it smells faintly of old parchment.',
    'The air around it smells faintly of burning cedar.',
    'The air around it carries the scent of a distant forge.',
    'The air grows noticeably colder when it is drawn.',
    'Nearby candle flames bend slightly toward it.',
    'Nearby candle flames briefly turn pale blue.',
    'Dust never seems to settle upon its surface.',
    'Snow melts slowly when it lands upon the metal.',
    'Snow refuses to melt upon the metal.',
    'Small sparks occasionally dance across its runes.',
    'A dim golden glow appears along its edges at sunrise.',
    'A dim violet glow appears along its edges at midnight.',
    'Its runes glow faintly during storms.',
    'Its runes glow faintly beneath a full moon.',
    'Its runes glow faintly near ancient ruins.',
    'Its runes briefly flare when battle begins.',
    'Its surface grows warm when danger is near.',
    'Its surface grows cold when danger is near.',

    'The inscription reads, "Stand until the last."',
    'The inscription reads, "The north remembers."',
    'The inscription reads, "No oath dies willingly."',
    'The inscription reads, "Steel outlives kings."',
    'The inscription reads, "Carry the flame forward."',
    'The inscription reads, "Watch the dark places."',
    'The inscription reads, "Hold fast against winter."',
    'The inscription reads, "The mountain does not kneel."',
    'The inscription reads, "Remember those who stood before."',
    'The inscription reads, "Fear no road beneath the stars."',
    'The inscription reads, "Let the storm answer."',
    'The inscription reads, "By stone and steel."',
    'The inscription reads, "Until the final watch."',
    'The inscription reads, "For those who never returned."',
    'The inscription reads, "Guard what remains."',
    'The inscription reads, "No crown lasts forever."',
    'The inscription reads, "The dead keep their promises."',
    'The inscription reads, "Walk where others falter."',
    'The inscription reads, "The forge remembers every blow."',
    'The inscription reads, "Winter tests all things."',

    'A name has been scratched out beneath the inscription.',
    'Several names have been carved along the inner edge.',
    'The oldest name carved into it can no longer be read.',
    'Someone added a second inscription many years after the first.',
    'A childlike carving has been hidden beneath the grip.',
    'Its owner once marked every campaign with a small notch.',
    'A final notch appears deeper than all the others.',
    'One rune has been deliberately carved backward.',
    'The central rune appears newer than the others.',
    'The oldest repairs are almost works of art themselves.',

    'It was clearly made to survive more than one lifetime.',
    'Whoever forged it expected war to last a very long time.',
    'Whoever carried it before did not surrender it willingly.',
    'Its previous owner took exceptional care of it.',
    'Its previous owner cared little for appearances.',
    'It appears to have crossed half the world before reaching you.',
    'It has survived fire, frost, and something far worse.',
    'Its history is written more clearly in scars than in runes.',
    'Despite its age, every moving piece still works perfectly.',
    'Despite countless repairs, the original craftsmanship still shows.',

    'The metal is flecked with tiny blue crystals.',
    'The metal is flecked with tiny red crystals.',
    'The metal is flecked with tiny golden crystals.',
    'Fine veins of silver run naturally through the material.',
    'Fine veins of black metal run beneath its surface.',
    'A pale gem rests within a simple iron setting.',
    'A dark gem seems to swallow the light around it.',
    'A cloudy crystal has been carefully set into its center.',
    'A tiny piece of amber has been worked into the handle.',
    'A smooth river stone has been mounted where a jewel should be.',
    'Several tiny teeth have been worked into the decoration.',
    'A strip of faded red cloth is wrapped around the grip.',
    'A strip of faded blue cloth is wrapped around the grip.',
    'A strip of faded white cloth is wrapped around the grip.',
    'A braided leather cord has been tied around it for luck.',
    'A weathered prayer ribbon hangs from one edge.',

    'A raven feather has been pressed beneath the binding.',
    'A wolf tooth hangs from a short leather cord.',
    'A bear claw has been worked into the decoration.',
    'A polished dragon scale forms part of its ornamentation.',
    'A tiny carved serpent coils around the central setting.',
    'A stylized eagle is worked into the metal.',
    'A snarling wolf decorates the oldest plate.',
    'A sleeping dragon is carved beneath the guard.',
    'A crowned raven appears upon the clasp.',
    'A mountain goat is carved into the pommel.',

    'Old blood remains trapped deep within the engraving.',
    'The blade has been sharpened so many times that its shape has changed.',
    'The grip has molded itself to the hand of a long-dead warrior.',
    'Several repairs use metal from completely different eras.',
    'One plate appears to have been replaced with titan-forged metal.',
    'The leather straps are newer than the rest of the item.',
    'The gemstone setting is clearly older than the item surrounding it.',
    'Its oldest component may predate the kingdom that discovered it.',
    'The inner surface carries marks invisible while it is worn.',
    'The final craftsman left a tiny hammer mark inside the clasp.',

    'A forgotten prayer seems to linger within it.',
    'The faint warmth of a campfire seems trapped inside.',
    'The silence around it feels deeper than ordinary silence.',
    'For a moment, holding it feels like standing beneath a winter sky.',
    'For a moment, holding it feels like hearing distant war drums.',
    'For a moment, holding it feels like standing inside an ancient forge.',
    'For a moment, holding it feels like walking beneath towering pines.',
    'For a moment, holding it feels like watching snow fall over a battlefield.',
    'For a moment, holding it feels like remembering a place you have never seen.',
    'Whatever story this relic once told, only fragments remain.'
]

def _seed_arg(value):
    value=str(value).strip()
    if not value or not value.isdigit():
        raise argparse.ArgumentTypeError('seed must contain digits only')
    return value

def _number_arg(value):
    try:
        value=int(value)
    except (TypeError,ValueError) as exc:
        raise argparse.ArgumentTypeError('number must be a positive integer') from exc
    if value < 1:
        raise argparse.ArgumentTypeError('number must be at least 1')
    if value > MAX_TOTAL_ITEMS:
        raise argparse.ArgumentTypeError(f'number cannot exceed {MAX_TOTAL_ITEMS}')
    return value

def _loot_chance_arg(value):
    try:
        chance=float(value)
    except (TypeError,ValueError) as exc:
        raise argparse.ArgumentTypeError('loot chance must be a number between 0 and 100') from exc
    if not math.isfinite(chance) or not 0 < chance <= 100:
        raise argparse.ArgumentTypeError('loot chance must be greater than 0 and at most 100')
    return chance

CLASS_ALIASES = {
    'warrior':'Warrior','paladin':'Paladin','hunter':'Hunter','rogue':'Rogue',
    'priest':'Priest','deathknight':'Death Knight','dk':'Death Knight',
    'shaman':'Shaman','mage':'Mage','warlock':'Warlock','druid':'Druid'
}

def _class_arg(value):
    raw=str(value).strip().lower()
    key=''.join(ch for ch in raw if ch.isalnum())
    if key not in CLASS_ALIASES:
        valid=', '.join(c[0].lower() for c in CLASSES)
        raise argparse.ArgumentTypeError(f'unknown class {value!r}; choose one of: {valid}')
    return CLASS_ALIASES[key]

def parse_args(argv=None):
    parser=argparse.ArgumentParser(description='Generate randomized AzerothCore WotLK items.')
    parser.add_argument('--seed',type=_seed_arg,help='Use this exact numeric seed instead of generating one automatically.')
    parser.add_argument('--number',type=_number_arg,help=f'Generate exactly this many items (max {MAX_TOTAL_ITEMS:,} total; max {MAX_ITEMS_PER_CLASS:,} per class).')
    parser.add_argument('--class',dest='class_name',type=_class_arg,help='Generate items for only this class (case-insensitive).')
    parser.add_argument('--loot-chance',type=_loot_chance_arg,default=10.0,metavar='PERCENT',help='Independent generated-item roll on each existing world-loot reference (default: 10).')
    parser.add_argument('--world-loot-source',type=Path,default=DEFAULT_WORLD_LOOT_SOURCE,metavar='PATH',help=f'creature_loot_template.sql to map world-loot levels (default: {DEFAULT_WORLD_LOOT_SOURCE}).')
    parser.add_argument('--reference-loot-source',type=Path,default=DEFAULT_REFERENCE_LOOT_SOURCE,metavar='PATH',help=f'reference_loot_template.sql used to verify shared references (default: {DEFAULT_REFERENCE_LOOT_SOURCE}).')
    parser.add_argument('--item-template-source',type=Path,default=DEFAULT_ITEM_TEMPLATE_SOURCE,metavar='PATH',help=f'item_template.sql used to audit catalog display and type references (default: {DEFAULT_ITEM_TEMPLATE_SOURCE}).')
    parser.add_argument('--item-dbc-source',dest='item_dbc_sources',type=Path,action='append',default=None,metavar='PATH',help=f'Complete or additive WotLK Item.dbc source; repeat for every client DBC baseline (default: {DEFAULT_ITEM_DBC_SOURCE}, {DEFAULT_ITEM_DBC_CUSTOM_SOURCE}).')
    parser.add_argument('--item-dbc-overwrite',action='store_true',help='Replace conflicting generated-ID rows in --item-dbc-source instead of failing.')
    return parser.parse_args(argv)

def get_or_create_user_guid(path=None):
    path=Path(path) if path is not None else USER_GUID_FILE
    if path.exists():
        raw=path.read_text(encoding='utf-8').strip()
        try:
            return str(uuid.UUID(raw))
        except ValueError as exc:
            raise RuntimeError(f'Invalid generator GUID file: {path}') from exc
    guid=str(uuid.uuid4())
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(guid+'\n',encoding='utf-8')
    return guid

def derive_auto_seed(user_guid,now=None):
    now=now if now is not None else datetime.now().astimezone()
    date_value=int(now.strftime('%Y%m%d'))
    time_value=int(now.strftime('%H%M%S%f'))
    payload=f'{user_guid}|{date_value}|{time_value}'.encode('utf-8')
    value=int.from_bytes(hashlib.blake2b(payload,digest_size=8).digest(),'big') % 10_000_000_000
    return f'{value:010d}'

def configure_runtime(argv=None,now=None,guid_path=None):
    global SEED, OUT, SQLDIR, LOOT_CHANCE, WORLD_LOOT_SOURCE, REFERENCE_LOOT_SOURCE, ITEM_TEMPLATE_SOURCE, ITEM_DBC_SOURCES, ITEM_DBC_OVERWRITE, REFERENCE_CATALOG_AUDIT
    global ACTIVE_CLASSES, TARGET_ITEM_COUNT, CLASS_ITEM_COUNTS
    args=parse_args(argv)
    world_loot_source=Path(args.world_loot_source).expanduser().resolve()
    reference_loot_source=Path(args.reference_loot_source).expanduser().resolve()
    item_template_source=Path(args.item_template_source).expanduser().resolve()
    item_dbc_sources=[Path(path).expanduser().resolve() for path in (args.item_dbc_sources or [DEFAULT_ITEM_DBC_SOURCE, DEFAULT_ITEM_DBC_CUSTOM_SOURCE])]
    for label,path in (('world-loot source',world_loot_source),('reference-loot source',reference_loot_source),('item-template source',item_template_source)):
        if not path.is_file():
            raise FileNotFoundError(f'{label} not found: {path}')
    for item_dbc_source in item_dbc_sources:
        if not item_dbc_source.is_file():
            raise FileNotFoundError(f'item-dbc source not found: {item_dbc_source}')
    catalog_audit=validate_reference_catalog(item_template_source)
    if catalog_audit['errors']:
        details='\n'.join(f' - {error}' for error in catalog_audit['errors'][:20])
        raise ValueError(f'item-template reference catalog audit failed ({len(catalog_audit["errors"])} errors):\n{details}')
    if args.seed is not None:
        seed=args.seed
        source='command-line'
    else:
        user_guid=get_or_create_user_guid(guid_path)
        seed=derive_auto_seed(user_guid,now)
        source='automatic'

    if args.class_name is not None:
        selected=[row for row in CLASSES if row[0]==args.class_name]
        number=args.number if args.number is not None else DEFAULT_ITEMS_PER_CLASS
        if number > MAX_ITEMS_PER_CLASS:
            raise ValueError(f'--number cannot exceed {MAX_ITEMS_PER_CLASS} when --class is used')
        counts={args.class_name:number}
    else:
        selected=list(CLASSES)
        number=args.number if args.number is not None else DEFAULT_TOTAL_ITEMS
        if number > MAX_TOTAL_ITEMS:
            raise ValueError(f'--number cannot exceed {MAX_TOTAL_ITEMS}')
        base,remainder=divmod(number,len(CLASSES))
        if base > MAX_ITEMS_PER_CLASS or (base == MAX_ITEMS_PER_CLASS and remainder):
            raise ValueError(f'--number would exceed the per-class cap of {MAX_ITEMS_PER_CLASS}')
        counts={cname:base+(1 if i<remainder else 0) for i,(cname,_,_) in enumerate(CLASSES)}
        selected=[row for row in selected if counts[row[0]]>0]

    SEED=seed
    LOOT_CHANCE=args.loot_chance
    WORLD_LOOT_SOURCE=world_loot_source
    REFERENCE_LOOT_SOURCE=reference_loot_source
    ITEM_TEMPLATE_SOURCE=item_template_source
    ITEM_DBC_SOURCES=item_dbc_sources
    ITEM_DBC_OVERWRITE=args.item_dbc_overwrite
    REFERENCE_CATALOG_AUDIT=catalog_audit
    ACTIVE_CLASSES=selected
    TARGET_ITEM_COUNT=number
    CLASS_ITEM_COUNTS=counts
    OUT=ROOT / f'generated-{SEED}'
    SQLDIR=OUT / 'sql'
    return {
        'seed':SEED,'source':source,'output_dir':OUT,'number':TARGET_ITEM_COUNT,
        'class_name':args.class_name,'classes':[row[0] for row in ACTIVE_CLASSES],
        'class_counts':dict(CLASS_ITEM_COUNTS),'loot_chance':LOOT_CHANCE,
        'world_loot_source':WORLD_LOOT_SOURCE,'reference_loot_source':REFERENCE_LOOT_SOURCE,
        'item_template_source':ITEM_TEMPLATE_SOURCE,'item_dbc_sources':ITEM_DBC_SOURCES,
        'item_dbc_overwrite':ITEM_DBC_OVERWRITE,'reference_catalog_audit':REFERENCE_CATALOG_AUDIT
    }

ITEM_DBC_HEADER=struct.Struct('<4s4I')
ITEM_DBC_RECORD=struct.Struct('<Iiiiiiii')
ITEM_DBC_MAGIC=b'WDBC'
ITEM_DBC_FIELD_COUNT=8
ITEM_DBC_COLUMNS=['ID','ClassID','SubclassID','SoundOverrideSubclassID','Material','DisplayInfoID','InventoryType','SheatheType']

def item_dbc_row(item):
    return (int(item['entry']),int(item['item_class']),int(item['subclass']),-1,int(item['Material']),
            int(item['displayid']),int(item['InventoryType']),int(item['sheath']))

def _normalise_item_dbc_row(row):
    if len(row)!=ITEM_DBC_FIELD_COUNT:
        raise ValueError(f'Item.dbc row must contain {ITEM_DBC_FIELD_COUNT} fields: {row!r}')
    try:
        values=tuple(int(value) for value in row)
    except (TypeError,ValueError) as exc:
        raise ValueError(f'Item.dbc row contains a non-integer value: {row!r}') from exc
    if not 0<=values[0]<=0xFFFFFFFF or any(not -0x80000000<=value<=0x7FFFFFFF for value in values[1:]):
        raise ValueError(f'Item.dbc row contains an out-of-range value: {row!r}')
    return values

def _read_item_dbc(path):
    path=Path(path)
    data=path.read_bytes()
    if len(data)<ITEM_DBC_HEADER.size:
        raise ValueError(f'Item.dbc is shorter than its header: {path}')
    magic,record_count,field_count,record_size,string_block_size=ITEM_DBC_HEADER.unpack_from(data)
    if magic!=ITEM_DBC_MAGIC:
        raise ValueError(f'unsupported Item.dbc magic {magic!r}: {path}')
    if field_count!=ITEM_DBC_FIELD_COUNT:
        raise ValueError(f'Item.dbc field count is {field_count}, expected {ITEM_DBC_FIELD_COUNT}: {path}')
    if record_size!=ITEM_DBC_RECORD.size:
        raise ValueError(f'Item.dbc record size is {record_size}, expected {ITEM_DBC_RECORD.size}: {path}')
    expected_size=ITEM_DBC_HEADER.size+record_count*record_size+string_block_size
    if len(data)!=expected_size:
        raise ValueError(f'Item.dbc size is {len(data)}, expected {expected_size}: {path}')
    rows={}
    offset=ITEM_DBC_HEADER.size
    for index in range(record_count):
        row=ITEM_DBC_RECORD.unpack_from(data,offset)
        offset+=record_size
        if row[0] in rows:
            raise ValueError(f'Item.dbc contains duplicate entry {row[0]}: {path}')
        rows[row[0]]=row
    return rows,data[offset:]

def merge_item_dbcs(source_paths,generated_rows,output_path,overwrite=False):
    if isinstance(source_paths,(str,Path)):
        source_paths=[source_paths]
    source_paths=[Path(path).expanduser().resolve() for path in source_paths]
    if not source_paths:
        raise ValueError('at least one Item.dbc source is required')
    output_path=Path(output_path).expanduser().resolve()
    if output_path in source_paths:
        raise ValueError('Item.dbc output must not replace a source file')
    existing={}
    string_block=None
    source_overlap_count=0
    for source_path in source_paths:
        rows,source_string_block=_read_item_dbc(source_path)
        if string_block is None:
            string_block=source_string_block
        elif source_string_block!=string_block:
            raise ValueError(f'Item.dbc sources have different string blocks: {source_paths[0]} and {source_path}')
        for entry,row in rows.items():
            if entry in existing:
                source_overlap_count+=1
                if existing[entry]!=row:
                    raise ValueError(f'conflicting Item.dbc source rows for entry {entry}: {source_path}')
            else:
                existing[entry]=row
    generated={}
    for raw_row in generated_rows:
        row=_normalise_item_dbc_row(raw_row)
        if row[0] in generated:
            raise ValueError(f'generated Item.dbc rows contain duplicate entry {row[0]}')
        generated[row[0]]=row
    conflicts=sorted(entry for entry,row in generated.items() if entry in existing and existing[entry]!=row)
    if conflicts and not overwrite:
        sample=', '.join(map(str,conflicts[:20]))
        suffix='...' if len(conflicts)>20 else ''
        raise ValueError(f'Item.dbc contains conflicting generated entries ({len(conflicts)}): {sample}{suffix}; use --item-dbc-overwrite to replace them')
    merged=dict(existing)
    merged.update(generated)
    payload=b''.join(ITEM_DBC_RECORD.pack(*merged[entry]) for entry in sorted(merged))
    header=ITEM_DBC_HEADER.pack(ITEM_DBC_MAGIC,len(merged),ITEM_DBC_FIELD_COUNT,ITEM_DBC_RECORD.size,len(string_block))
    output_path.parent.mkdir(parents=True,exist_ok=True)
    output_path.write_bytes(header+payload+string_block)
    return {'source_file_count':len(source_paths),'source_paths':[str(path) for path in source_paths],
            'source_row_count':len(existing),'source_overlap_count':source_overlap_count,
            'generated_row_count':len(generated),'merged_row_count':len(merged),
            'overwritten_row_count':len(conflicts),'string_block_size':len(string_block)}

def merge_item_dbc(source_path,generated_rows,output_path,overwrite=False):
    return merge_item_dbcs([source_path],generated_rows,output_path,overwrite)

WORLD_LOOT_ROW_RE=re.compile(r'^\s*\(\s*\d+\s*,\s*\d+\s*,\s*(-?\d+)\s*,.*?World Loot Level\s+(\d+)\b',re.IGNORECASE)
REFERENCE_ENTRY_RE=re.compile(r'^\s*\(\s*(\d+)\s*,')

def _load_reference_entries(path):
    entries={}
    for line in path.read_text(encoding='utf-8').splitlines():
        match=REFERENCE_ENTRY_RE.match(line)
        if match: entries[int(match.group(1))]=True
    if not entries:
        raise ValueError(f'no reference loot rows found in {path}')
    return entries

def _catalog_reference_contexts():
    contexts=defaultdict(list)
    for (kind,subclass,inventory_type),rows in A.items():
        for row in rows:
            contexts[row[0]].append((row[1],4,subclass,inventory_type,row[2],row[3],f'{kind}[{subclass},{inventory_type}]'))
    for weapon_kind,rows in W.items():
        subclass,inventory_type,_=WEAPON_META[weapon_kind]
        for row in rows:
            contexts[row[0]].append((row[1],2,subclass,inventory_type,row[2],row[3],weapon_kind))
    return contexts

def _split_sql_tuple(line):
    text=line.strip()
    if not text.startswith('('): return None
    if text.endswith(';'): text=text[:-1]
    if text.endswith(','): text=text[:-1]
    if not text.endswith(')'): return None
    text=text[1:-1]
    values=[]; value=[]; quoted=False; index=0
    while index<len(text):
        char=text[index]
        if quoted:
            value.append(char)
            if char=='\\' and index+1<len(text):
                index+=1; value.append(text[index])
            elif char=="'":
                if index+1<len(text) and text[index+1]=="'":
                    index+=1; value.append(text[index])
                else:
                    quoted=False
        elif char=="'":
            quoted=True; value.append(char)
        elif char==',':
            values.append(''.join(value).strip()); value=[]
        else:
            value.append(char)
        index+=1
    if quoted: raise ValueError('unterminated SQL string')
    values.append(''.join(value).strip())
    return values

def _load_item_template_rows(path,entries):
    wanted=set(entries)
    if not wanted: raise ValueError('item-template reference catalog is empty')
    rows={}
    with path.open(encoding='utf-8') as source:
        for line_number,line in enumerate(source,1):
            match=REFERENCE_ENTRY_RE.match(line)
            if not match: continue
            entry=int(match.group(1))
            if entry not in wanted: continue
            fields=_split_sql_tuple(line)
            if fields is None or len(fields)<=12:
                raise ValueError(f'unparseable item-template row at {path}:{line_number}')
            try:
                row=(int(fields[1]),int(fields[2]),int(fields[5]),int(fields[12]),int(fields[15]),int(fields[6]))
            except (TypeError,ValueError) as exc:
                raise ValueError(f'unparseable item-template fields at {path}:{line_number}') from exc
            previous=rows.get(entry)
            if previous is not None and previous!=row:
                raise ValueError(f'item-template entry {entry} has conflicting rows in {path}')
            rows[entry]=row
    missing=sorted(wanted-set(rows))
    if missing: raise ValueError(f'catalog references missing from {path}: {missing[:10]}')
    return rows

def validate_reference_catalog(path=None):
    path=Path(DEFAULT_ITEM_TEMPLATE_SOURCE if path is None else path).expanduser().resolve()
    contexts=_catalog_reference_contexts()
    actual=_load_item_template_rows(path,contexts)
    display_mismatches=[]; metadata_mismatches=[]; inventory_mismatches=[]; template_mismatches=[]
    for entry in sorted(contexts):
        row=actual[entry]
        expected_displayids={context[0] for context in contexts[entry]}
        if len(expected_displayids)!=1:
            display_mismatches.append(f'{entry}: catalog has conflicting displayids {sorted(expected_displayids)}')
        elif row[2] not in expected_displayids:
            display_mismatches.append(f'{entry}: catalog displayid {sorted(expected_displayids)[0]} != item_template displayid {row[2]}')
        for displayid,item_class,subclass,inventory_type,item_level,quality,label in contexts[entry]:
            if row[0]!=item_class or row[1]!=subclass:
                metadata_mismatches.append(f'{entry}: catalog {label} expects class/subclass {item_class}/{subclass}, item_template has {row[0]}/{row[1]}')
            if row[3]!=inventory_type:
                inventory_mismatches.append(f'{entry}: catalog {label} expects InventoryType {inventory_type}, item_template has {row[3]}')
            if row[4]!=item_level or row[5]!=quality:
                template_mismatches.append(f'{entry}: catalog {label} expects ItemLevel/Quality {item_level}/{quality}, item_template has {row[4]}/{row[5]}')
    errors=display_mismatches+metadata_mismatches+inventory_mismatches+template_mismatches
    return {'source':str(path),'reference_count':len(contexts),'errors':errors,
            'display_mismatches':display_mismatches,'metadata_mismatches':metadata_mismatches,
            'inventory_type_mismatches':inventory_mismatches,'template_mismatches':template_mismatches}

def load_world_loot_references(world_path=None,reference_path=None):
    world_path=Path(DEFAULT_WORLD_LOOT_SOURCE if world_path is None else world_path)
    reference_path=Path(DEFAULT_REFERENCE_LOOT_SOURCE if reference_path is None else reference_path)
    levels={}
    for line_number,line in enumerate(world_path.read_text(encoding='utf-8').splitlines(),1):
        if 'world loot level' not in line.lower(): continue
        match=WORLD_LOOT_ROW_RE.match(line)
        if not match:
            raise ValueError(f'unparseable world-loot row at {world_path}:{line_number}')
        reference_id=int(match.group(1)); level=int(match.group(2))
        if reference_id<=0 or level<1:
            raise ValueError(f'invalid world-loot mapping at {world_path}:{line_number}')
        previous=levels.get(reference_id)
        if previous is not None and previous!=level:
            raise ValueError(f'world-loot reference {reference_id} maps to both levels {previous} and {level}')
        levels[reference_id]=level
    if not levels:
        raise ValueError(f'no World Loot Level rows found in {world_path}')
    missing=sorted(set(levels)-set(_load_reference_entries(reference_path)))
    if missing:
        raise ValueError(f'world-loot references missing from {reference_path}: {missing[:10]}')
    return dict(sorted(levels.items()))

def _loot_bracket_index(level):
    if level<1: raise ValueError(f'loot level must be positive: {level}')
    for index,(_label,lo,hi) in enumerate(LOOT_BRACKETS):
        if lo<=min(level,80)<=hi: return index
    raise ValueError(f'loot level has no bracket: {level}')

def _loot_attachment_item(parent_reference):
    item=GENERATED_LOOT_ATTACHMENT_ITEM_BASE+parent_reference
    if item>0xFFFFFFFF:
        raise ValueError(f'generated loot attachment key exceeds uint32: {parent_reference}')
    return item

def build_loot_records(items,world_references):
    grouped=defaultdict(list)
    for item in items: grouped[_loot_bracket_index(item['RequiredLevel'])].append(item)

    pools=[]; pool_rows=[]; active_indexes=set()
    for index,(label,lo,hi) in enumerate(LOOT_BRACKETS):
        group=grouped.get(index,[])
        if not group: continue
        pool_id=GENERATED_LOOT_POOL_BASE+index; active_indexes.add(index)
        pools.append({'pool_id':pool_id,'bracket':label,'level_min':lo,'level_max':hi,'item_count':len(group)})
        for item in group:
            pool_rows.append({'pool_id':pool_id,'item':item['entry'],'bracket':label,'comment':f'Generated item pool {label} | {item["name"]}'})

    attachments=[]
    for parent_reference,world_level in sorted(world_references.items()):
        index=_loot_bracket_index(world_level)
        if index not in active_indexes: continue
        label=LOOT_BRACKETS[index][0]; pool_id=GENERATED_LOOT_POOL_BASE+index
        attachments.append({'parent_reference':parent_reference,'item':_loot_attachment_item(parent_reference),
                            'pool_id':pool_id,'world_level':world_level,'bracket':label})

    item_pool_counts=Counter(row['item'] for row in pool_rows)
    if len(pool_rows)!=len(items) or any(item_pool_counts[item['entry']]!=1 for item in items):
        raise RuntimeError('every generated item must appear in exactly one generated loot pool')
    if len({row['item'] for row in pool_rows})!=len(pool_rows):
        raise RuntimeError('generated loot pool contains duplicate item keys')
    if len({row['item'] for row in attachments})!=len(attachments):
        raise RuntimeError('generated loot attachments contain duplicate keys')
    return {'pools':pools,'pool_rows':pool_rows,'attachments':attachments}

def h64(*parts):
    if SEED is None:
        raise RuntimeError('Runtime seed is not configured. Call configure_runtime() first.')
    s='|'.join(map(str,(SEED,)+parts)).encode()
    return int.from_bytes(hashlib.blake2b(s,digest_size=8).digest(),'big')
def r01(*parts): return h64(*parts)/18446744073709551616

def weighted(rows,*key):
    total=sum(w for _,w in rows); x=r01(*key)*total; acc=0
    for v,w in rows:
        acc+=w
        if x < acc: return v
    return rows[-1][0]

def _level_cycle(cname, cycle):
    levels=[l for l in range(1,81) for _ in range(100)]
    weights=[]
    for l in range(1,81):
        w=0.5 if l<20 else 0.8 if l<40 else 1.0 if l<60 else 1.5 if l<70 else 2.5 if l<75 else 5.0 if l<80 else 20.0
        weights.append((l,w))

    # Cycle zero deliberately preserves the original 10,000-item sequence exactly.
    if cycle == 0:
        for i in range(2000): levels.append(weighted(weights,cname,'extra_level',i))
        return [x for _,x in sorted((h64(cname,'level_shuffle',i,l),l) for i,l in enumerate(levels))]

    for i in range(2000): levels.append(weighted(weights,cname,'extra_level_ext',cycle,i))
    return [x for _,x in sorted((h64(cname,'level_shuffle_ext',cycle,i,l),l) for i,l in enumerate(levels))]

def level_list(cname, count=DEFAULT_ITEMS_PER_CLASS):
    if not (1 <= count <= MAX_ITEMS_PER_CLASS):
        raise ValueError(f'count for {cname} must be between 1 and {MAX_ITEMS_PER_CLASS}')
    cycles=(count + DEFAULT_ITEMS_PER_CLASS - 1)//DEFAULT_ITEMS_PER_CLASS
    levels=[]
    for cycle in range(cycles):
        levels.extend(_level_cycle(cname,cycle))
    return levels[:count]

def item_level(req,entry):
    if req < 58: return max(req+1, req + 1 + int(r01(entry,'ilvl')*7))
    if req < 68: return int(80 + (req-58)*3.8 + r01(entry,'ilvl')*6)
    if req < 75: return int(112 + (req-68)*7 + r01(entry,'ilvl')*9)
    if req < 80: return int(160 + (req-75)*7 + r01(entry,'ilvl')*11)
    vals=[(187,8),(200,15),(213,15),(219,10),(226,10),(232,10),(239,7),(245,7),(251,5),(258,5),(264,4),(271,2),(277,1.5),(284,.5)]
    return weighted(vals,entry,'ilvl80')

def quality(req,ilvl,entry):
    if req<20: rows=[(2,82),(3,17.8),(4,.2)]
    elif req<40: rows=[(2,72),(3,27.5),(4,.5)]
    elif req<60: rows=[(2,60),(3,38.5),(4,1.5)]
    elif req<70: rows=[(2,50),(3,45),(4,5)]
    elif req<75: rows=[(2,38),(3,50),(4,12)]
    elif req<80: rows=[(2,25),(3,50),(4,25)]
    elif ilvl<213: rows=[(2,10),(3,55),(4,35)]
    elif ilvl<245: rows=[(2,4),(3,32),(4,64)]
    else: rows=[(2,1),(3,15),(4,84)]
    return weighted(rows,entry,'quality')

def slot_weights(req,cname):
    rows=[]
    for s,w in SLOT_BASE:
        if req<10:
            if s=='shoulder' or s=='trinket': w=0
            elif s in ('head','neck','finger'): w=max(1,w//4)
        elif req<20:
            if s=='shoulder': w=2
            if s=='trinket': w=1
        rows.append((s,w))
    if cname in ('Paladin','Death Knight','Shaman','Druid') and req>=50: rows.append(('relic',2))
    return [(s,w) for s,w in rows if w>0]

def armor_subclass(cname,req):
    if cname in ('Warrior','Paladin'): return 3 if req<40 else 4
    if cname in ('Hunter','Shaman'): return 2 if req<40 else 3
    if cname in ('Rogue','Druid'): return 2
    if cname in ('Priest','Mage','Warlock'): return 1
    if cname=='Death Knight': return 4
    raise ValueError(cname)

def weapon_choices(cname,role):
    if cname=='Warrior': rows=[('1h_sword',15),('1h_axe',15),('1h_mace',12),('2h_sword',18),('2h_axe',18),('2h_mace',12),('polearm',10),('bow',2),('gun',2),('crossbow',2)]
    elif cname=='Paladin': rows=[('1h_sword',18),('1h_mace',20),('1h_axe',8),('2h_sword',18),('2h_mace',18),('2h_axe',10),('polearm',8)]
    elif cname=='Hunter': rows=[('bow',30),('gun',17),('crossbow',18),('polearm',12),('2h_axe',9),('2h_sword',8),('1h_axe',3),('1h_sword',3)]
    elif cname=='Rogue': rows=[('dagger',38),('1h_sword',25),('1h_mace',14),('fist',15),('bow',3),('gun',2),('crossbow',3)]
    elif cname=='Priest': rows=[('staff',48),('1h_mace',25),('wand',27)]
    elif cname=='Death Knight': rows=[('1h_sword',14),('1h_axe',14),('1h_mace',10),('2h_sword',22),('2h_axe',22),('2h_mace',18)]
    elif cname=='Shaman':
        rows=[('1h_axe',20),('1h_mace',20),('dagger',12),('fist',12),('staff',20),('2h_axe',8),('2h_mace',8)] if role=='agility_dps' else [('1h_mace',32),('dagger',18),('staff',38),('1h_axe',12)]
    elif cname in ('Mage','Warlock'): rows=[('staff',45),('dagger',20),('1h_sword',15),('wand',20)]
    elif cname=='Druid': rows=[('staff',45),('1h_mace',20),('2h_mace',20),('dagger',10),('polearm',5)]
    else: raise ValueError(cname)
    return rows

def choose_ref(rows,ilvl,q,entry,tag):
    scored=[]
    for row in rows:
        ref_ilvl=row[2]; rq=row[3]
        score=abs(ref_ilvl-ilvl) + abs(rq-q)*10 + r01(entry,tag,row[0])*7
        scored.append((score,row))
    scored.sort(key=lambda x:x[0]); top=[r for _,r in scored[:min(5,len(scored))]]
    idx=min(len(top)-1,int((r01(entry,tag,'pick')**1.8)*len(top)))
    return top[idx]

def role_stats(cname,role,req,is_shield=False):
    if role=='strength_dps': primary=['str','stam']; sec=['crit','hit','haste','expertise','arp','ap']
    elif role=='agility_dps': primary=['agi','stam']; sec=['crit','hit','haste','expertise','arp','ap']
    elif role=='hunter': primary=['agi','stam']; sec=['crit','hit','haste','arp','ap','rap']
    elif role=='caster_dps': primary=['int','stam']; sec=['sp','hit','crit','haste','spirit','spellpen']
    elif role=='healer':
        primary=['int','stam']; sec=['sp','haste','crit','spirit','mp5']
        if cname in ('Paladin','Shaman'): sec=[x for x in sec if x!='spirit']
    elif role=='tank':
        if cname=='Druid': primary=['stam','agi']; sec=['dodge','expertise','hit','crit']
        else: primary=['stam','str']; sec=['def','dodge','parry','expertise','hit']
        if is_shield: sec += ['block','blockvalue']
    else: raise ValueError(role)
    if req<20:
        allowed={'str','agi','int','stam','spirit','ap','rap','sp','def','dodge','mp5'}
        sec=[x for x in sec if x in allowed]
    elif req<40:
        blocked={'haste','expertise','arp','spellpen','blockvalue'}
        sec=[x for x in sec if x not in blocked]
    return primary,sec

def stat_count(req,entry,slot):
    if req<10: rows=[(1,70),(2,30)]
    elif req<30: rows=[(1,15),(2,55),(3,30)]
    elif req<60: rows=[(2,30),(3,55),(4,15)]
    elif req<70: rows=[(2,15),(3,45),(4,40)]
    elif req<80: rows=[(3,35),(4,50),(5,15)]
    else: rows=[(3,20),(4,45),(5,35)]
    if slot=='relic': rows=[(1,20),(2,50),(3,30)] if req<80 else [(2,35),(3,65)]
    return weighted(rows,entry,'stat_count')

def make_stats(cname,role,req,ilvl,q,entry,budget_key,sockets,is_shield=False):
    n=stat_count(req,entry,budget_key)
    prim,sec=role_stats(cname,role,req,is_shield)
    picks=[]
    for p in prim:
        if len(picks)<n: picks.append(p)
    pool=[x for x in sec if x not in picks]
    while len(picks)<n and pool:
        idx=int(r01(entry,'stat_pick',len(picks))*len(pool)); picks.append(pool.pop(idx))
    # If n=1, prefer the class-defining primary rather than always stamina for tanks.
    if n==1 and role=='tank' and len(prim)>1: picks=[prim[int(r01(entry,'tank_primary')*len(prim))]]
    slotmult=SLOT_BUDGET.get(budget_key,.8)
    curve=.28 + 1.20*((max(1,ilvl)/213.0)**.85)
    budget=max(n, ilvl*slotmult*curve*QUALITY_POWER[q]*(1-0.035*sockets))
    weights=[]
    for i,p in enumerate(picks):
        base=1.16 if p in prim else 1.0
        weights.append(base*(.86+r01(entry,'stat_weight',i)*.28))
    sw=sum(weights)
    out=[]
    for i,(p,w) in enumerate(zip(picks,weights)):
        share=budget*w/sw
        cost=STAT_COST.get(p,1.0)
        val=max(1,int(round((share/cost)*(0.95+r01(entry,'stat_var',i)*.10))))
        out.append((STAT_ID[p],val,p))
    return out

MAX_NAME_CHARS = 42
MAX_NAME_WORDS = 7

def valid_item_name(name):
    return len(name) <= MAX_NAME_CHARS and len(name.split()) <= MAX_NAME_WORDS

def make_name(entry,slot,weapon_kind=None,legendary=False):
    base_pool=BASE_BY_WEAPON[weapon_kind] if weapon_kind else BASE_BY_SLOT[slot]

    # Generate compact Blizzard-like names and reject anything that exceeds
    # the hard display budget. Never truncate; reroll instead.
    for attempt in range(2000):
        base=base_pool[h64(entry,'base',attempt)%len(base_pool)]
        adj=ADJ[h64(entry,'adj',attempt)%len(ADJ)]
        suf=SUFFIX[h64(entry,'suf',attempt)%len(SUFFIX)]
        owner=OWNER[h64(entry,'owner',attempt)%len(OWNER)]
        a=PROPER_A[h64(entry,'pa',attempt)%len(PROPER_A)]
        b=PROPER_B[h64(entry,'pb',attempt)%len(PROPER_B)]

        if legendary:
            candidates=[
                f'{a}{b.capitalize()}',
                f"{owner}'s {a}{b.capitalize()}",
                f'{a}{b.capitalize()}, {base}',
            ]
        else:
            pat=h64(entry,'pat',attempt)%12
            if pat==0: name=f'{adj} {base}'
            elif pat==1: name=f'{base} of the {suf}'
            elif pat==2: name=f"{owner}'s {base}"
            elif pat==3: name=f'{adj} {base} of the {suf}'
            elif pat==4: name=f"{owner}'s {adj} {base}"
            elif pat==5: name=f'{base} of {suf}'
            elif pat==6: name=f'The {adj} {base}'
            elif pat==7: name=f'{adj} {base}, {owner}\'s Oath'
            elif pat==8: name=f'{a}{b.capitalize()} {base}'
            elif pat==9: name=f'{base}, {a}{b.capitalize()}'
            elif pat==10: name=f"{owner}'s {base} of the {suf}"
            else: name=f'{adj} {base} of {suf}'
            candidates=[name]

        for candidate in candidates:
            if valid_item_name(candidate):
                yield candidate

def qpick(entry): return THEMES[h64(entry,'theme')%len(THEMES)]

def sqlq(s): return "'"+str(s).replace('\\','\\\\').replace("'","''")+"'"

def armor_formula(sub,slot,ilvl,q,entry):
    # Calibrated from ordinary WotLK stock armor rows, used only for gameplay numbers, never IDs.
    base={1:1.15,2:2.35,3:4.65,4:8.5}[sub]
    sm={'head':.75,'shoulder':.64,'chest':1.0,'wrists':.30,'hands':.50,'waist':.50,'legs':.88,'feet':.58}[slot]
    low=.48+.52*min(1,(ilvl/213.0)**.48)
    return max(1,int(round(ilvl*base*sm*low*QUALITY_POWER[q]*(.96+r01(entry,'armor')*.08))))

def durability(slot,weapon_kind=None):
    if weapon_kind: return 75 if WEAPON_META[weapon_kind][2] in ('one_hand','ranged') else 100
    return {'head':60,'shoulder':60,'chest':100,'wrists':35,'hands':50,'waist':45,'legs':100,'feet':60,'back':0,'neck':0,'finger':0,'trinket':0,'relic':0,'shield':100}.get(slot,0)

def vendor_values(ilvl,q,budget_key,entry):
    sm=SLOT_BUDGET.get(budget_key,.75)
    # Copper; smooth leveling curve, roughly fivefold buy:sell like many stock rows.
    sell=max(1,int(round((max(2,ilvl)**2.15)*sm*QUALITY_POWER[q]*1.55)))
    ratio=3+int(r01(entry,'vendor_ratio')*3)
    return sell*ratio,sell

def weapon_damage(kind,ilvl,q,entry):
    rows=W[kind]
    ref=choose_ref(rows,ilvl,q,entry,'weapon_ref')
    ref_dps=((ref[5]+ref[6])/2)/(ref[4]/1000)
    target=ref_dps*((ilvl/max(1,ref[2]))**1.12)*(QUALITY_POWER[q]/QUALITY_POWER.get(ref[3],.92))*(.97+r01(entry,'dpsvar')*.06)
    # Speed stays within documented 3.3.5 generation profiles and near the chosen stock reference.
    speed_ranges={'dagger':(1400,2000),'fist':(1600,2700),'1h_sword':(1800,2800),'1h_axe':(1800,2800),'1h_mace':(1800,2800),
                  '2h_sword':(3200,3800),'2h_axe':(3200,3800),'2h_mace':(3200,3800),'polearm':(3200,3800),'staff':(2800,3600),
                  'bow':(2400,3200),'gun':(2400,3200),'crossbow':(2600,3400),'wand':(1400,2000)}
    lo,hi=speed_ranges[kind]
    refspeed=min(hi,max(lo,ref[4]))
    speed=int(round((refspeed + (r01(entry,'speed')-.5)*200)/100))*100
    speed=min(hi,max(lo,speed))
    avg=target*(speed/1000)
    spread=.10 + r01(entry,'spread')*.07
    dmin=max(1,int(round(avg*(1-spread)))); dmax=max(dmin+1,int(round(avg*(1+spread))))
    school=ref[7] if kind=='wand' else 0
    actual=((dmin+dmax)/2)/(speed/1000)
    return ref,dmin,dmax,school,speed,actual

def socket_colors(req,ilvl,q,entry,slot,ref_q):
    if req<60: return []
    # Conservative progression, no generated socket bonus ID.
    chance = .06 if req<70 else .14 if req<75 else .24 if req<80 else (.24 if q==2 else .36 if q==3 else .50 if q==4 else .66)
    if r01(entry,'socket_chance')>=chance: return []
    maxn=1 if req<70 else 2 if req<80 else 3
    n=1
    if maxn>=2 and r01(entry,'socket2') < (.16 if req<80 else .34): n=2
    if maxn>=3 and r01(entry,'socket3') < .09: n=3
    colors=[]
    if slot=='head' and req>=70 and q>=3 and r01(entry,'meta')<.10:
        colors.append(1)
    while len(colors)<n:
        x=r01(entry,'socket_color',len(colors)); colors.append(2 if x<.40 else 4 if x<.75 else 8)
    return colors

def choose_structure(cname,role,req,ilvl,q,entry):
    slot=weighted(slot_weights(req,cname),entry,'slot')
    if slot=='weapon':
        # Shield substitution only for classes/roles that normally use one.
        shield_ok=(cname in ('Warrior','Paladin') and role=='tank') or (cname=='Paladin' and role=='healer') or (cname=='Shaman' and role in ('caster_dps','healer'))
        if shield_ok and r01(entry,'shield') < .18:
            ref=choose_ref(A[('shield',6,14)],ilvl,q,entry,'shield_ref')
            return dict(slot='shield',cls=4,sub=6,inv=14,kind='shield',budget_key='shield',ref=ref)
        kind=weighted(weapon_choices(cname,role),entry,'weapon_kind')
        sub,inv,bkey=WEAPON_META[kind]
        return dict(slot='weapon',cls=2,sub=sub,inv=inv,kind=kind,budget_key=bkey,ref=None)
    if slot=='relic':
        sub={'Paladin':7,'Druid':8,'Shaman':9,'Death Knight':10}[cname]
        ref=choose_ref(A[('relic',sub,28)],ilvl,q,entry,'relic_ref')
        return dict(slot='relic',cls=4,sub=sub,inv=28,kind='relic',budget_key='relic',ref=ref)
    if slot=='back':
        ref=choose_ref(A[('misc',1,16)],ilvl,q,entry,'back_ref')
        return dict(slot='back',cls=4,sub=1,inv=16,kind='back',budget_key='back',ref=ref)
    if slot in ('neck','finger','trinket'):
        inv={'neck':2,'finger':11,'trinket':12}[slot]
        ref=choose_ref(A[('misc',0,inv)],ilvl,q,entry,slot+'_ref')
        return dict(slot=slot,cls=4,sub=0,inv=inv,kind=slot,budget_key=slot,ref=ref)
    sub=armor_subclass(cname,req)
    inv=20 if (sub==1 and slot=='chest') else INV[slot]
    ref=choose_ref(A[('armor',sub,inv)],ilvl,q,entry,'armor_ref')
    return dict(slot=slot,cls=4,sub=sub,inv=inv,kind='armor',budget_key=slot,ref=ref)

def expected_legendary_count(item_count):
    # Preserve the original rarity: three Legendaries per 100,000 generated items.
    return (item_count*3)//100000

def build_skeletons():
    if ACTIVE_CLASSES is None or CLASS_ITEM_COUNTS is None or TARGET_ITEM_COUNT is None:
        raise RuntimeError('Runtime generation plan is not configured. Call configure_runtime() first.')
    sk=[]
    for cname,mask,_legacy_start in ACTIVE_CLASSES:
        count=CLASS_ITEM_COUNTS.get(cname,0)
        levels=level_list(cname,count)
        assert len(levels)==count
        for i,req in enumerate(levels):
            entry=entry_for_class(cname,i); ilvl=item_level(req,entry); q=quality(req,ilvl,entry); role=weighted(ROLE_WEIGHTS[cname],entry,'role')
            st=choose_structure(cname,role,req,ilvl,q,entry)
            sk.append(dict(entry=entry,class_name=cname,class_mask=mask,required_level=req,item_level=ilvl,quality=q,role=role,**st))
    if len(sk)!=TARGET_ITEM_COUNT:
        raise RuntimeError(f'generation plan produced {len(sk)} skeletons, expected {TARGET_ITEM_COUNT}')
    eligible=[x for x in sk if x['required_level']==80 and x['item_level']>=264 and x['quality']==4]
    eligible.sort(key=lambda x:h64(x['entry'],'legendary'))
    for x in eligible[:expected_legendary_count(len(sk))]: x['quality']=5
    return sk

def finish_items(sk):
    names=set(); items=[]
    for idx,x in enumerate(sk):
        entry=x['entry']; q=x['quality']; ilvl=x['item_level']; req=x['required_level']; cname=x['class_name']; role=x['role']; slot=x['slot']
        theme=qpick(entry)
        weapon_kind=x['kind'] if x['cls']==2 else None
        # choose appearance/damage ref after legendary promotion so quality proximity is final
        if x['cls']==2:
            ref,dmin,dmax,school,delay,dps=weapon_damage(weapon_kind,ilvl,q,entry)
            x['ref']=ref; displayid=ref[1]; armor=0; block=0
        else:
            ref=x['ref']; displayid=ref[1]; dmin=dmax=0; school=0; delay=0; dps=0.0
            if x['kind']=='armor': armor=armor_formula(x['sub'],slot,ilvl,q,entry); block=0
            elif x['kind']=='back': armor=max(1,int(round(ilvl*.65*(.65+.35*min(1,ilvl/200))*QUALITY_POWER[q]))); block=0
            elif x['kind']=='shield':
                armor=max(20,int(round(ilvl*35*(.60+.40*min(1,ilvl/213))*QUALITY_POWER[q])))
                block=max(3,int(round(ilvl*1.0*(.55+.45*min(1,ilvl/213))*QUALITY_POWER[q])))
            else: armor=0; block=0
        colors=socket_colors(req,ilvl,q,entry,slot,ref[3])
        stats=make_stats(cname,role,req,ilvl,q,entry,x['budget_key'],len(colors),x['kind']=='shield')
        # Name uniqueness over the entire generated collection.
        name=None
        for cand in make_name(entry,'shield' if x['kind']=='shield' else 'relic' if x['kind']=='relic' else slot,weapon_kind,q==5):
            if cand not in names:
                name=cand; break
        if name is None:
            raise RuntimeError(f'name exhaustion {entry}')
        names.add(name)
        bkey=x['budget_key']; buy,sell=vendor_values(ilvl,q,bkey,entry)
        bonding=1 if q==5 or (req==80 and q>=4 and ilvl>=232) else 2
        material = 6 if x['sub']==4 and x['cls']==4 else 5 if x['sub']==3 and x['cls']==4 else 8 if x['sub']==2 and x['cls']==4 else 7 if x['sub']==1 and x['cls']==4 else 4 if slot in ('neck','finger','trinket') else 1 if x['kind']=='shield' else 0
        sheath=4 if x['kind']=='shield' else 1 if x['cls']==2 and x['budget_key']=='two_hand' and weapon_kind!='staff' else 2 if weapon_kind=='staff' else 3 if x['cls']==2 and x['budget_key']=='one_hand' else 0
        maxdur=durability('shield' if x['kind']=='shield' else slot,weapon_kind)
        desc=FLAVOR[h64(entry,'flavor')%len(FLAVOR)] if r01(entry,'flavor_chance')<.24 else ''
        item=dict(entry=entry,class_name=cname,class_mask=x['class_mask'],role=role,theme=theme,name=name,Quality=q,
                  ItemLevel=ilvl,RequiredLevel=req,item_class=x['cls'],subclass=x['sub'],InventoryType=x['inv'],displayid=displayid,
                  reference_entry=ref[0],reference_item_level=ref[2],reference_quality=ref[3],stats=stats,
                  dmg_min1=dmin,dmg_max1=dmax,dmg_type1=school,delay=delay,dps=round(dps,3),armor=armor,block=block,
                  sockets=colors,bonding=bonding,BuyPrice=buy,SellPrice=sell,Material=material,sheath=sheath,
                  MaxDurability=maxdur,description=desc,kind=x['kind'],weapon_kind=weapon_kind or '')
        items.append(item)
    return items

def validate(items):
    errors=[]
    entries=[x['entry'] for x in items]; names=[x['name'] for x in items]
    expected_total=TARGET_ITEM_COUNT if TARGET_ITEM_COUNT is not None else len(items)
    expected_counts=CLASS_ITEM_COUNTS or Counter(x['class_name'] for x in items)
    if len(items)!=expected_total: errors.append(f'count={len(items)} expected={expected_total}')

    expected_entries=[]
    for cname,_,_start in CLASSES:
        for i in range(expected_counts.get(cname,0)):
            expected_entries.append(entry_for_class(cname,i))
    if entries!=expected_entries: errors.append('entry allocation does not match the configured class/item plan')
    if len(set(entries))!=len(entries): errors.append('duplicate entries')
    if len(set(names))!=len(names): errors.append('duplicate names')
    for x in items:
        if not valid_item_name(x['name']):
            errors.append(f"{x['entry']} name too long: {x['name']}")

    class_counts=Counter(x['class_name'] for x in items)
    for cname,_,_ in CLASSES:
        expected=expected_counts.get(cname,0)
        if class_counts[cname]!=expected: errors.append(f'{cname} count {class_counts[cname]} expected {expected}')
        if expected==10000:
            lv=Counter(x['RequiredLevel'] for x in items if x['class_name']==cname)
            if any(lv[l]<100 for l in range(1,81)): errors.append(f'{cname} missing base level coverage')

    legends=[x for x in items if x['Quality']==5]
    expected_legends=expected_legendary_count(expected_total)
    if len(legends)!=expected_legends or any(x['RequiredLevel']!=80 or x['ItemLevel']<264 for x in legends):
        errors.append(f'legendary policy violation: {len(legends)} expected {expected_legends}')

    for x in items:
        if not (1<=x['RequiredLevel']<=80): errors.append(f"{x['entry']} bad req")
        if x['ItemLevel']<x['RequiredLevel']: errors.append(f"{x['entry']} ilvl<req")
        if x['Quality'] not in (2,3,4,5): errors.append(f"{x['entry']} quality")
        if x['displayid']<=0 or x['reference_entry']<=0: errors.append(f"{x['entry']} display/ref")
        ids=[s[0] for s in x['stats']]
        if not (1<=len(ids)<=5) or len(ids)!=len(set(ids)) or 0 in ids: errors.append(f"{x['entry']} stats")
        if len(x['sockets'])>3 or any(c not in (1,2,4,8) for c in x['sockets']): errors.append(f"{x['entry']} sockets")
        if x['item_class']==2:
            if not (x['dmg_min1']>0 and x['dmg_max1']>=x['dmg_min1'] and x['delay']>0 and x['armor']==0): errors.append(f"{x['entry']} weapon")
            calc=((x['dmg_min1']+x['dmg_max1'])/2)/(x['delay']/1000)
            if abs(calc-x['dps'])/max(1,x['dps'])>.02: errors.append(f"{x['entry']} dps")
        if x['kind']=='armor' and x['armor']<=0: errors.append(f"{x['entry']} armor")
        if x['kind']=='shield' and (x['armor']<=0 or x['block']<=0 or x['subclass']!=6 or x['InventoryType']!=14): errors.append(f"{x['entry']} shield")
        if x['kind']=='relic':
            expected={'Paladin':7,'Druid':8,'Shaman':9,'Death Knight':10}.get(x['class_name'])
            if expected!=x['subclass'] or x['InventoryType']!=28: errors.append(f"{x['entry']} relic")
        if x['kind']=='armor':
            expected=armor_subclass(x['class_name'],x['RequiredLevel'])
            if x['subclass']!=expected: errors.append(f"{x['entry']} armor compatibility")
    return errors

SQL_COLUMNS=['entry','class','subclass','SoundOverrideSubclass','name','displayid','Quality','Flags','FlagsExtra','BuyCount','BuyPrice','SellPrice','InventoryType','AllowableClass','AllowableRace','ItemLevel','RequiredLevel']
for i in range(1,11): SQL_COLUMNS += [f'stat_type{i}',f'stat_value{i}']
SQL_COLUMNS += ['dmg_min1','dmg_max1','dmg_type1','armor','delay','ammo_type','RangedModRange','bonding','description','Material','sheath','RandomProperty','RandomSuffix','block','MaxDurability','socketColor_1','socketContent_1','socketColor_2','socketContent_2','socketColor_3','socketContent_3','socketBonus','RequiredDisenchantSkill','DisenchantID','flagsCustom','VerifiedBuild']
LOOT_SQL_COLUMNS=['Entry','Item','Reference','Chance','QuestRequired','LootMode','GroupId','MinCount','MaxCount','Comment']

def sql_values(x):
    vals=[x['entry'],x['item_class'],x['subclass'],-1,sqlq(x['name']),x['displayid'],x['Quality'],0,0,1,x['BuyPrice'],x['SellPrice'],x['InventoryType'],x['class_mask'],-1,x['ItemLevel'],x['RequiredLevel']]
    ss=x['stats']+[(0,0,'')]*(10-len(x['stats']))
    for sid,v,_ in ss: vals += [sid,v]
    ammo=2 if x['weapon_kind'] in ('bow','crossbow') else 3 if x['weapon_kind']=='gun' else 0
    rng=100 if x['weapon_kind'] in ('bow','crossbow','gun','wand') else 0
    vals += [x['dmg_min1'],x['dmg_max1'],x['dmg_type1'],x['armor'],x['delay'],ammo,rng,x['bonding'],sqlq(x['description']),x['Material'],x['sheath'],0,0,x['block'],x['MaxDurability']]
    cs=x['sockets']+[0]*(3-len(x['sockets']))
    vals += [cs[0],0,cs[1],0,cs[2],0,0,-1,0,0,12340]
    assert len(vals)==len(SQL_COLUMNS),(len(vals),len(SQL_COLUMNS),x['entry'])
    return vals

def fmt(v):
    if isinstance(v,str) and v.startswith("'"): return v
    if isinstance(v,float): return f'{v:.3f}'.rstrip('0').rstrip('.')
    return str(v)

def _contiguous_ranges(values):
    values=sorted(set(values))
    if not values: return []
    ranges=[]
    start=prev=values[0]
    for value in values[1:]:
        if value == prev + 1:
            prev=value
            continue
        ranges.append((start,prev))
        start=prev=value
    ranges.append((start,prev))
    return ranges

def _entry_filter_sql(items):
    ranges=_contiguous_ranges(x['entry'] for x in items)
    parts=[]
    for lo,hi in ranges:
        if lo==hi: parts.append(f'`entry` = {lo}')
        else: parts.append(f'`entry` BETWEEN {lo} AND {hi}')
    if not parts: return '1 = 0'
    if len(parts)==1: return parts[0]
    return '('+' OR '.join(parts)+')'

def _format_entry_ranges(items):
    return ', '.join(str(lo) if lo==hi else f'{lo}-{hi}' for lo,hi in _contiguous_ranges(x['entry'] for x in items))

def _loot_sql_row(values):
    return '('+','.join(fmt(v) for v in values)+')'

def write_outputs(items):
    if (OUT is None or SQLDIR is None or LOOT_CHANCE is None or WORLD_LOOT_SOURCE is None or
            REFERENCE_LOOT_SOURCE is None or ITEM_TEMPLATE_SOURCE is None or ITEM_DBC_SOURCES is None or
            REFERENCE_CATALOG_AUDIT is None):
        raise RuntimeError('Runtime output directory is not configured. Call configure_runtime() first.')
    world_references=load_world_loot_references(WORLD_LOOT_SOURCE,REFERENCE_LOOT_SOURCE)
    loot=build_loot_records(items,world_references)
    item_dbc_rows=[item_dbc_row(x) for x in items]
    for item_dbc_source in ITEM_DBC_SOURCES:
        try:
            item_dbc_source.relative_to(OUT)
        except ValueError:
            pass
        else:
            raise ValueError('item-dbc source cannot be inside the output directory being replaced')
    if OUT.exists(): shutil.rmtree(OUT)
    SQLDIR.mkdir(parents=True)
    client_dir=OUT/'client'; client_dir.mkdir()
    with (client_dir/'item_dbc_rows.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(ITEM_DBC_COLUMNS); w.writerows(item_dbc_rows)
    item_dbc_info={'source_file_count':0,'source_paths':[],'source_row_count':0,'source_overlap_count':0,
                   'generated_row_count':len(item_dbc_rows),'merged_row_count':0,'overwritten_row_count':0,
                   'string_block_size':0,'output':None}
    merged_item_dbc_rows=None
    if ITEM_DBC_SOURCES:
        item_dbc_info.update(merge_item_dbcs(ITEM_DBC_SOURCES,item_dbc_rows,client_dir/'Item.dbc',ITEM_DBC_OVERWRITE))
        item_dbc_info['output']='client/Item.dbc'
        merged_item_dbc_rows,_=_read_item_dbc(client_dir/'Item.dbc')
        with (client_dir/'item_dbc_merged_rows.csv').open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f); w.writerow(ITEM_DBC_COLUMNS)
            w.writerows(merged_item_dbc_rows[entry] for entry in sorted(merged_item_dbc_rows))
        item_dbc_info['merged_manifest']='client/item_dbc_merged_rows.csv'
    with (OUT/'items.ndjson').open('w',encoding='utf-8') as f:
        for x in items:
            y=dict(x); y['stats']=[{'id':a,'value':b,'name':c} for a,b,c in x['stats']]
            f.write(json.dumps(y,ensure_ascii=False,separators=(',',':'))+'\n')
    manifest_cols=['entry','class_name','name','Quality','RequiredLevel','ItemLevel','role','kind','weapon_kind','InventoryType','subclass','displayid','reference_entry','reference_item_level','armor','dps','sockets']
    with (OUT/'manifest.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(manifest_cols)
        for x in items: w.writerow([x[k] if k!='sockets' else '|'.join(map(str,x['sockets'])) for k in manifest_cols])
    refs={}
    for x in items: refs[(x['reference_entry'],x['displayid'])]=(x['reference_entry'],x['displayid'],x['reference_item_level'],x['reference_quality'])
    with (OUT/'reference_catalog_used.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['reference_entry','displayid','item_level','quality']); w.writerows(sorted(refs.values()))

    import_order=[]
    generated_class_names=[]
    for cname,_,_ in CLASSES:
        subset=[x for x in items if x['class_name']==cname]
        if not subset: continue
        generated_class_names.append(cname)
        cdir=SQLDIR/cname.lower().replace(' ','_'); cdir.mkdir()
        for label,lo,hi in LOOT_BRACKETS:
            group=[x for x in subset if lo<=x['RequiredLevel']<=hi]
            for part in range(0,len(group),BATCH_SIZE):
                batch=group[part:part+BATCH_SIZE]
                if not batch: continue
                path=cdir/f'{label}_part_{part//BATCH_SIZE+1:02d}.sql'; import_order.append(path.relative_to(OUT).as_posix())
                with path.open('w',encoding='utf-8') as f:
                    f.write(f'-- {cname} | Required Level {label} | {len(batch)} finalized items\n')
                    f.write(f'-- Generator seed: {SEED}\nSTART TRANSACTION;\n\n')
                    f.write('DELETE FROM `item_template` WHERE `entry` IN (\n    '+', '.join(str(x['entry']) for x in batch)+'\n);\n\n')
                    f.write('INSERT INTO `item_template`\n(\n    '+',\n    '.join(f'`{c}`' for c in SQL_COLUMNS)+'\n)\nVALUES\n')
                    rows=['('+','.join(fmt(v) for v in sql_values(x))+')' for x in batch]
                    f.write(',\n'.join(rows)+';\n\nCOMMIT;\n')

    loot_dir=SQLDIR/'loot'; loot_dir.mkdir()
    loot_columns=',\n    '.join(f'`{c}`' for c in LOOT_SQL_COLUMNS)
    pool_ids=[GENERATED_LOOT_POOL_BASE+i for i in range(len(LOOT_BRACKETS))]
    pool_id_list=', '.join(map(str,pool_ids))
    cleanup_path=loot_dir/'00_generated_loot_cleanup.sql'; import_order.append(cleanup_path.relative_to(OUT).as_posix())
    cleanup_path.write_text(
        '-- Removes generated reference pools and any rows pointing at them.\n'
        'START TRANSACTION;\n'
        f'DELETE FROM `reference_loot_template` WHERE `Entry` IN ({pool_id_list}) OR `Reference` IN ({pool_id_list});\n'
        'COMMIT;\n',encoding='utf-8')

    for pool in loot['pools']:
        rows=[_loot_sql_row((row['pool_id'],row['item'],0,0,0,1,1,1,1,sqlq(row['comment'])))
              for row in loot['pool_rows'] if row['pool_id']==pool['pool_id']]
        path=loot_dir/f'{pool["bracket"]}_pool.sql'; import_order.append(path.relative_to(OUT).as_posix())
        with path.open('w',encoding='utf-8') as f:
            f.write(f'-- Generated item pool | Required Level {pool["bracket"]} | {pool["item_count"]} items\n')
            f.write(f'-- Generator seed: {SEED}\nSTART TRANSACTION;\n\n')
            f.write(f'DELETE FROM `reference_loot_template` WHERE `Entry` = {pool["pool_id"]};\n\n')
            f.write(f'INSERT INTO `reference_loot_template`\n(\n    {loot_columns}\n)\nVALUES\n')
            f.write(',\n'.join(rows)+';\n\nCOMMIT;\n')

    attachment_conditions=' OR '.join(f'(`Entry` = {row["parent_reference"]} AND `Item` = {row["item"]})' for row in loot['attachments']) or '1 = 0'
    if loot['attachments']:
        path=loot_dir/'world_loot_attachments.sql'; import_order.append(path.relative_to(OUT).as_posix())
        with path.open('w',encoding='utf-8') as f:
            f.write('-- Generated item pools attached to existing shared world-loot references.\n')
            f.write(f'-- Generator seed: {SEED}\nSTART TRANSACTION;\n\n')
            f.write('DELETE FROM `reference_loot_template` WHERE '+attachment_conditions+';\n\n')
            f.write(f'INSERT INTO `reference_loot_template`\n(\n    {loot_columns}\n)\nVALUES\n')
            rows=[_loot_sql_row((row['parent_reference'],row['item'],row['pool_id'],LOOT_CHANCE,0,1,0,1,1,
                                 sqlq(f'Generated item pool attachment | World Loot Level {row["world_level"]} -> {row["bracket"]}')))
                  for row in loot['attachments']]
            f.write(',\n'.join(rows)+';\n\nCOMMIT;\n')

    with (OUT/'loot_pools.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['pool_id','bracket','level_min','level_max','item_count','chance','group_id'])
        for pool in loot['pools']: w.writerow([pool['pool_id'],pool['bracket'],pool['level_min'],pool['level_max'],pool['item_count'],0,1])
    with (OUT/'loot_attachments.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['parent_reference','world_loot_level','bracket','pool_id','synthetic_item_key','chance','group_id'])
        for row in loot['attachments']:
            w.writerow([row['parent_reference'],row['world_level'],row['bracket'],row['pool_id'],row['item'],LOOT_CHANCE,0])

    (OUT/'sql'/'IMPORT_ORDER.txt').write_text('\n'.join(import_order)+'\n',encoding='utf-8')

    cmd=OUT/'additem_commands'; cmd.mkdir()
    for cname in generated_class_names:
        with (cmd/(cname.lower().replace(' ','_')+'.txt')).open('w',encoding='utf-8') as f:
            for x in items:
                if x['class_name']==cname: f.write(f".additem {x['entry']} 1 -- {x['name']}\n")

    entry_filter=_entry_filter_sql(items)
    pool_filter=f'`Entry` IN ({pool_id_list})'
    pool_reference_filter=f'`Reference` IN ({pool_id_list})'
    (OUT/'00_PREIMPORT_COLLISION_CHECK.sql').write_text(
        '-- MUST return 0 before import. This generator cannot inspect your live database.\n'
        'SELECT COUNT(*) AS collision_count\nFROM `item_template`\nWHERE '+entry_filter+';\n\n'
        '-- If non-zero, inspect collisions before importing:\n'
        'SELECT `entry`,`name` FROM `item_template`\nWHERE '+entry_filter+'\nORDER BY `entry`;\n\n'
        'SELECT COUNT(*) AS generated_loot_pool_collision_count\nFROM `reference_loot_template`\nWHERE '+pool_filter+';\n'
        'SELECT `Entry`,`Item`,`Reference`,`Comment` FROM `reference_loot_template`\nWHERE '+pool_filter+'\nORDER BY `Entry`,`Item`;\n\n'
        'SELECT COUNT(*) AS generated_loot_reference_collision_count\nFROM `reference_loot_template`\nWHERE '+pool_reference_filter+';\n'
        'SELECT `Entry`,`Item`,`Reference`,`Comment` FROM `reference_loot_template`\nWHERE '+pool_reference_filter+'\nORDER BY `Entry`,`Item`;\n\n'
        'SELECT COUNT(*) AS generated_loot_attachment_collision_count\nFROM `reference_loot_template`\nWHERE '+attachment_conditions+';\n'
        'SELECT `Entry`,`Item`,`Reference`,`Comment` FROM `reference_loot_template`\nWHERE '+attachment_conditions+'\nORDER BY `Entry`,`Item`;\n',encoding='utf-8')
    (OUT/'99_REMOVE_GENERATED_ITEMS.sql').write_text(
        'START TRANSACTION;\n'
        f'DELETE FROM `reference_loot_template` WHERE `Entry` IN ({pool_id_list}) OR `Reference` IN ({pool_id_list});\n'
        'DELETE FROM `item_template` WHERE '+entry_filter+';\n'
        'COMMIT;\n',encoding='utf-8')
    (OUT/'00_SCHEMA_CHECK.sql').write_text(
        "SHOW COLUMNS FROM `acore_world`.`item_template`;\n"
        "SHOW COLUMNS FROM `acore_world`.`reference_loot_template`;\n",encoding='utf-8')

    q=Counter(QUALITY_NAME[x['Quality']] for x in items); roles=Counter(x['role'] for x in items); kinds=Counter(x['kind'] for x in items)
    loot_bracket_distribution={label:next((pool['item_count'] for pool in loot['pools'] if pool['bracket']==label),0) for label,_,_ in LOOT_BRACKETS}
    world_loot_bracket_distribution={label:sum(row['bracket']==label for row in loot['attachments']) for label,_,_ in LOOT_BRACKETS}
    classes={}
    for cname in generated_class_names:
        xs=[x for x in items if x['class_name']==cname]
        classes[cname]={'count':len(xs),'entry_min':min(x['entry'] for x in xs),'entry_max':max(x['entry'] for x in xs),
                        'unique_names':len({x['name'] for x in xs}),'unique_displayids':len({x['displayid'] for x in xs}),
                        'level_min':min(x['RequiredLevel'] for x in xs),'level_max':max(x['RequiredLevel'] for x in xs)}
    item_dbc_report=dict(item_dbc_info)
    item_dbc_report['source']=str(ITEM_DBC_SOURCES[0]) if len(ITEM_DBC_SOURCES)==1 else None
    item_dbc_report['manifest']='client/item_dbc_rows.csv'
    report={'seed':SEED,'requested_number':TARGET_ITEM_COUNT,'selected_classes':generated_class_names,
            'total_items':len(items),'entry_min':min(x['entry'] for x in items),'entry_max':max(x['entry'] for x in items),
            'unique_entries':len({x['entry'] for x in items}),'unique_names':len({x['name'] for x in items}),
            'unique_displayids':len({x['displayid'] for x in items}),'unique_reference_entries':len({x['reference_entry'] for x in items}),
            'quality_counts':dict(q),'role_counts':dict(roles),'kind_counts':dict(kinds),'classes':classes,
            'loot_pool_count':len(loot['pools']),'loot_pool_row_count':len(loot['pool_rows']),
            'loot_attachment_count':len(loot['attachments']),'loot_chance':LOOT_CHANCE,
            'world_loot_source':str(WORLD_LOOT_SOURCE),'reference_loot_source':str(REFERENCE_LOOT_SOURCE),
            'item_template_source':str(ITEM_TEMPLATE_SOURCE),
            'item_dbc':item_dbc_report,
            'reference_catalog_count':REFERENCE_CATALOG_AUDIT['reference_count'],
            'reference_catalog_inventory_type_mismatch_count':len(REFERENCE_CATALOG_AUDIT['inventory_type_mismatches']),
            'world_loot_reference_count':len(world_references),'loot_bracket_distribution':loot_bracket_distribution,
            'world_loot_bracket_distribution':world_loot_bracket_distribution,
            'generated_loot_pool_ids':[pool['pool_id'] for pool in loot['pools']],
            'random_effects_enabled':False,'socket_bonus_ids_generated':False,'disenchant_ids_generated':False,
            'random_property_or_suffix_enabled':False,'validation_errors':0}
    (OUT/'validation_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    digest=hashlib.sha256((OUT/'items.ndjson').read_bytes()).hexdigest()
    (OUT/'CHECKSUMS.txt').write_text(f'{digest}  items.ndjson\n',encoding='utf-8')

    class_summary=', '.join(generated_class_names)
    entry_summary='; '.join(f"{c}: {_format_entry_ranges([x for x in items if x['class_name']==c])}" for c in generated_class_names)
    readme=f"""# AzerothCore Random WotLK Item Pack

Deterministic seed: `{SEED}`  
Output directory: `generated-{SEED}`  
Generated items: `{len(items)}`  
Classes: `{class_summary}`  
Generated entry ranges: `{entry_summary}`  
Generated loot pools: `{len(loot['pools'])}` (`{len(loot['pool_rows'])}` item rows)  
World-loot attachments: `{len(loot['attachments'])}` at `{LOOT_CHANCE}%`  
World-loot source: `{WORLD_LOOT_SOURCE}`  
Reference-loot source: `{REFERENCE_LOOT_SOURCE}`  
Item-template source: `{ITEM_TEMPLATE_SOURCE}`  
Client Item.dbc sources: `{', '.join(map(str, ITEM_DBC_SOURCES))}`  
Target: AzerothCore / WotLK 3.3.5a

## Generator CLI

- `py generate_pack.py` - default 100,000-item pack (10,000 per class).
- `py generate_pack.py --number 10` - exactly 10 items total, distributed across classes.
- `py generate_pack.py --class warrior` - default 10,000-item Warrior block.
- `py generate_pack.py --seed 12311523 --number 20 --class warlock` - exactly 20 deterministic Warlock items.
- `py generate_pack.py --number 200000` - maximum pack: 200,000 items total, 20,000 per class.
- `py generate_pack.py --class warrior --number 20000` - maximum single-class pack: 20,000 Warrior items.
- `py generate_pack.py --loot-chance 5` - use a 5% independent roll on each shared world-loot reference.
- `py generate_pack.py --world-loot-source PATH --reference-loot-source PATH` - use alternate base loot SQL sources.
- `py generate_pack.py --item-template-source PATH` - use an alternate item-template source for catalog auditing.
- `py generate_pack.py` - merges the vanilla `Item.dbc` and the additive custom baseline beside this generator, then writes the merged copy under `client/`.
- `py generate_pack.py --item-dbc-source PATH --item-dbc-source PATH` - merge every complete or additive WotLK `Item.dbc` source supplied; repeat the option for each client baseline.
- Add `--item-dbc-overwrite` only when intentionally replacing conflicting generated-ID rows in that source DBC.

Flags can be combined in any order. The default remains 100,000 total. Explicit `--number` is capped at 200,000 total and 20,000 per selected class.

## Safety / generation policy

- Final values are generated and validated before SQL is emitted.
- Static stats are packed contiguously from stat slot 1.
- `RandomProperty` and `RandomSuffix` are zero.
- No random item spells/procs are generated.
- No socket bonus ID is generated (`socketBonus = 0`).
- No disenchant ID is invented (`DisenchantID = 0`, `RequiredDisenchantSkill = -1`).
- Every catalog `displayid`, class, subclass, and inventory type is checked against the selected `item_template.sql` before generation.
- SQL uses explicit column lists and transactions.
- Generated items are placed into up to six centralized `reference_loot_template` pools by required-level bracket.
- Pool rows use `Chance = 0`, `GroupId = 1` to select one generated item; attachments use `GroupId = 0` and the configured independent roll.
- Existing creature loot rows are not rewritten. World-loot levels 81–82 use the level-80 pool, and the generated pool is shared across classes.
- Generated reference pool IDs are reserved at `3000000`–`3000005`; attachment keys use the reserved `2000000000 + parent_reference` range.
- Item entries use the `200000-399999` namespace, split into 20,000-ID blocks per class.
- The default 100,000-item pack uses the first 10,000 IDs of each class block; larger runs fill those blocks up to 200,000 items.

## Import

1. Run `00_SCHEMA_CHECK.sql` and confirm the columns match your AzerothCore schema.
2. Run `00_PREIMPORT_COLLISION_CHECK.sql`. Do not import unless every reported collision count is 0.
3. Import files in `sql/IMPORT_ORDER.txt`.
4. Restart worldserver after import.
5. With the client closed, clear `Cache/WDB/<locale>/itemcache.wdb` if item names/icons are stale, then retest.
6. `client/item_dbc_rows.csv` contains only this run's generated rows; `client/item_dbc_merged_rows.csv` contains the complete final client table.
7. All configured DBC sources are merged additively. Identical duplicate rows are accepted; conflicting rows stop generation instead of silently overwriting client data.
8. Package only the final `client/Item.dbc` externally as `DBFilesClient\\Item.dbc` (for example with `var/pack_phase1_mpq.py`) and keep other custom client assets/DBC rows in the effective source set.

`00_PREIMPORT_COLLISION_CHECK.sql` checks item IDs, reserved pool IDs, pool references, and attachment keys. `99_REMOVE_GENERATED_ITEMS.sql` removes this run's generated items, pools, and pool attachments.
"""
    (OUT/'README.md').write_text(readme,encoding='utf-8')
    return report

def main(argv=None):
    runtime=configure_runtime(argv)
    print(f"Generator seed: {runtime['seed']} ({runtime['source']})")
    print(f"Items requested: {runtime['number']}")
    print(f"Classes: {', '.join(runtime['classes'])}")
    print(f"Output directory: {runtime['output_dir']}")
    sk=build_skeletons()
    items=finish_items(sk)
    errs=validate(items)
    if errs:
        print('VALIDATION FAILED',len(errs)); print('\n'.join(errs[:50])); raise SystemExit(1)
    report=write_outputs(items)
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
