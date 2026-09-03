# Dream Path — Season 1 Rewards and Change Guide

> Current repository reference for every configured Dream Path reward/content entry and the place to change it.
> Snapshot: 2026-08-28. English names are shown where the SQL provides `name_en`; the German names remain in the source rows.

## Scope and source of truth

The server-side SQL tables and `SeasonPass.cpp`/`SeasonPassSeason.cpp` are authoritative. The Lua files mirror server data for display, but a UI row is not a second reward definition. World tables are loaded when the module configuration is loaded; character tables persist progress.

| Area | Current inventory | Authoritative source |
| --- | --- | --- |
| Tier rewards | 174 rows across tiers 0–100; 109 Free/Adventure rows and 65 Hero/Free rows | [seasonpass_rewards.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_rewards.sql#L3) |
| Custom items | 58 custom `item_template` definitions | [seasonpass_items.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_items.sql#L1) |
| Dream Chest pool | 294 chest-tier rows grouped into 100 unique loot entries | [seasonpass_chest_loot.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_chest_loot.sql#L4) |
| Weekly goals | 40 base goals plus 14 Phase 8 event-filtered goals | [seasonpass_weekly.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_weekly.sql#L2) |
| Seasonal tables | 24 achievements, 8 bounties, 18 discoveries, 12 dungeons, 6 bosses, 12 zones, 24 runes, 21 supplies, 10 fish, 8 mutators, 12 teleports, 119 shop slots | [SeasonPassSeason.cpp](modules/mod-seasonpass/src/SeasonPassSeason.cpp#L243) |

This is Season 1 (`SeasonPass.Season = 1`) with 100 points per tier and a configured cap of tier 100. Both tracks are intentionally free; “Hero / Free” is the code’s historical name for the second track.

## Value conventions

| Value | Meaning |
| --- | --- |
| Item ID | A WoW `item_template.entry`; the item is mailed if the player’s bags cannot accept it. |
| Gold ID | Copper, not gold. For example, `50000` = 5 gold. |
| Title ID | A `CharTitlesEntry` ID; the server sets the title when it exists. |
| Chest ID | `0` means a normal Dream Chest whose quality is rolled on opening; IDs 1–3 are blue, mythic, and golden chest tiers. |
| Rarity | `1 Common`, `2 Rare`, `3 Epic`, `4 Legendary`. |
| Weight | Relative weight inside a selected rarity. Values are not percentages; a configured weight of 0 is clamped to 1 by the loader. |
| Promille | Per-thousand chance. `500` = 50%. |


## Reward row schema

The tier table uses these SQL columns:

| Column | Meaning |
| --- | --- |
| `season` | Season selector; the C++ loader filters to the configured season. |
| `tier` | 0 is the welcome package; 1–100 are normal pass tiers. |
| `track` | `0` Free / Adventure, `1` Hero / Free. |
| `classmask` | `0` all classes; otherwise a bitmask listed below. |
| `slot` | Ordering for multiple rewards at one tier. |
| `type` | `0` item, `1` gold, `2` title, `3` Dream Chest. |
| `id` / `count` | Reward identifier and quantity. Gold `id` is copper per unit. |
| `name` / `name_en` | German and English display labels. |


| Class | classmask |
| --- | --- |
| Warrior | `1` |
| Paladin | `2` |
| Hunter | `4` |
| Rogue | `8` |
| Priest | `16` |
| Death Knight | `32` |
| Shaman | `64` |
| Mage | `128` |
| Warlock | `256` |
| Druid | `1024` |

Reward rows are grouped below for readability; changing an entry means editing the corresponding SQL row, not the grouped Markdown representation.

## 1. Tier rewards

`ClaimDue` advances Free and Hero claim counters independently. It grants every row at or below the current tier whose classmask matches the character. Tier 0 is not part of the automatic tier loop; it is the one-time welcome package claimed separately.

| Tier | Free / Adventure path | Hero / Free path |
| --- | --- | --- |
| 0 | Item `900134` — Dream Cowl of the Illidari<br>Item `900135` — Tabard of the Dream Crusade<br>Item `900136` — Dream Orb of Deception<br>Gold `50000c` — 5 gold starting capital | — |
| 1 | Gold `30000c` — 3 gold | Item `900011` — Nightmare Blade<br>Item `900021` — Mace of the Hallowed Dream<br>Item `900031` — Nightmare Bow of the Marksman<br>Item `900041` — Nightmare Dagger of Shadows<br>Item `900051` — Staff of Silent Dreams<br>Item `900061` — Runeblade of the Eternal Nightmare<br>Item `900071` — Totem Hammer of the Dream Spirits<br>Item `900081` — Staff of the Arcane Nightmare<br>Item `900091` — Dagger of the Whispering Nightmare<br>Item `900111` — Staff of the Emerald Dream |
| 2 | Gold `40000c` — 4 gold | — |
| 3 | Gold `50000c` — 5 gold | — |
| 4 | Gold `60000c` — 6 gold | Gold `500000c` — 50 extra gold |
| 5 | Item `6657` ×5 — Savory Deviate Delight | Item `900012` — Shoulderguard of the Nightmare Walker<br>Item `900022` — Shoulderplates of the Dream Watch<br>Item `900032` — Spaulders of the Dream Stalker<br>Item `900042` — Shadowwoven Dream Spaulders<br>Item `900052` — Mantle of the Dream Seer<br>Item `900062` — Shoulderguard of the Frost Dreamer<br>Item `900072` — Spaulders of the Elemental Dream<br>Item `900082` — Mantle of the Dream Weaver<br>Item `900092` — Mantle of the Soul Dream<br>Item `900112` — Spaulders of the Dream Walker |
| 6 | Gold `80000c` — 8 gold | — |
| 7 | Gold `90000c` — 9 gold | — |
| 8 | Gold `100000c` — 10 gold | Item `21841` — Netherweave Bag (16 slots) |
| 9 | Gold `110000c` — 11 gold | — |
| 10 | Item `40752` ×10 — Emblem of Heroism<br>Dream Chest `0` — Dream Chest | Item `900013` — Breastplate of the Nightmare Walker<br>Item `900023` — Breastplate of the Dream Watch<br>Item `900033` — Harness of the Dream Stalker<br>Item `900043` — Vest of the Dream Creeper<br>Item `900053` — Robe of the Dream Seer<br>Item `900063` — Breastplate of the Frost Dreamer<br>Item `900073` — Vest of the Elemental Dream<br>Item `900083` — Robe of the Dream Weaver<br>Item `900093` — Robe of the Soul Dream<br>Item `900113` — Wildhide Vest of the Dream Walker |
| 11 | Gold `130000c` — 13 gold | — |
| 12 | Gold `140000c` — 14 gold | Dream Chest `0` — Dream Chest |
| 13 | Item `18660` — World Enlarger | — |
| 14 | Gold `160000c` — 16 gold | — |
| 15 | Item `23705` — Tabard of Flame | Item `900014` — Dreamshard of the Battlemaster<br>Item `900024` — Dreamshard of the Crusader<br>Item `900034` — Dreamshard of the Beast Lord<br>Item `900044` — Dreamshard of the Assassin<br>Item `900054` — Dreamshard of the Light<br>Item `900064` — Dreamshard of the Damned<br>Item `900074` — Dreamshard of the Seer<br>Item `900084` — Dreamshard of the Scholar<br>Item `900094` — Dreamshard of the Summoner<br>Item `900114` — Dreamshard of the Wilds |
| 16 | Gold `180000c` — 18 gold | Item `45624` ×10 — Emblem of Conquest |
| 17 | Gold `190000c` — 19 gold | — |
| 18 | Gold `200000c` — 20 gold | — |
| 19 | Gold `210000c` — 21 gold | — |
| 20 | Item `40753` ×10 — Emblem of Valor | Item `23713` — Hippogryph Hatchling |
| 21 | Gold `230000c` — 23 gold | — |
| 22 | Item `8500` — Parrot Cage (Cockatiel) | — |
| 23 | Gold `250000c` — 25 gold | — |
| 24 | Gold `260000c` — 26 gold | Dream Chest `0` — Dream Chest |
| 25 | Dream Chest `0` — Dream Chest | — |
| 26 | Gold `280000c` — 28 gold | — |
| 27 | Gold `290000c` — 29 gold | — |
| 28 | Gold `300000c` — 30 gold | Gold `1000000c` — 100 extra gold |
| 29 | Gold `310000c` — 31 gold | — |
| 30 | Item `8491` — Cat Carrier (Black Tabby)<br>Dream Chest `0` — Dream Chest | — |
| 31 | Gold `330000c` — 33 gold | — |
| 32 | Gold `340000c` — 34 gold | Item `47241` ×10 — Emblem of Triumph |
| 33 | Title `143` — Title: Jenkins | — |
| 34 | Gold `360000c` — 36 gold | — |
| 35 | Item `23709` — Tabard of Frost | — |
| 36 | Gold `380000c` — 38 gold | Dream Chest `0` — Dream Chest |
| 37 | Gold `390000c` — 39 gold | — |
| 38 | Gold `400000c` — 40 gold | — |
| 39 | Gold `410000c` — 41 gold | — |
| 40 | Item `45624` ×10 — Emblem of Conquest | Dream Chest `0` — Dream Chest |
| 41 | Gold `430000c` — 43 gold | — |
| 42 | Item `10360` — Black Kingsnake | — |
| 43 | Gold `450000c` — 45 gold | — |
| 44 | Gold `460000c` — 46 gold | Item `900102` — Tabard of the Nightmare |
| 45 | Item `13379` — Piccolo of the Flaming Fire | — |
| 46 | Gold `480000c` — 48 gold | — |
| 47 | Gold `490000c` — 49 gold | — |
| 48 | Gold `500000c` — 50 gold | Dream Chest `0` — Dream Chest |
| 49 | Gold `510000c` — 51 gold | — |
| 50 | Dream Chest `0` — Dream Chest<br>Dream Chest `0` — Dream Chest | — |
| 51 | Gold `530000c` — 53 gold | — |
| 52 | Gold `540000c` — 54 gold | Dream Chest `0` — Dream Chest |
| 53 | Gold `550000c` — 55 gold | — |
| 54 | Gold `560000c` — 56 gold | — |
| 55 | Item `38658` — Vampiric Batling | — |
| 56 | Gold `580000c` — 58 gold | Item `41599` — Frostweave Bag (20 slots) |
| 57 | Gold `590000c` — 59 gold | — |
| 58 | Gold `600000c` — 60 gold | — |
| 59 | Gold `610000c` — 61 gold | — |
| 60 | Item `47241` ×15 — Emblem of Triumph | Item `38628` — Nether Ray Fry |
| 61 | Gold `630000c` — 63 gold | — |
| 62 | Item `8494` — Hyacinth Macaw | — |
| 63 | Gold `650000c` — 65 gold | — |
| 64 | Gold `660000c` — 66 gold | Item `49426` ×10 — Emblem of Frost |
| 65 | Item `43154` — Tabard of the Argent Crusade | — |
| 66 | Title `168` — Title: the Patient | — |
| 67 | Gold `690000c` — 69 gold | — |
| 68 | Gold `700000c` — 70 gold | Gold `2000000c` — 200 extra gold |
| 69 | Gold `710000c` — 71 gold | — |
| 70 | Dream Chest `0` — Dream Chest<br>Dream Chest `0` — Dream Chest | — |
| 71 | Gold `730000c` — 73 gold | — |
| 72 | Gold `740000c` — 74 gold | Gold `3000000c` — 300 extra gold |
| 73 | Gold `750000c` — 75 gold | — |
| 74 | Gold `760000c` — 76 gold | — |
| 75 | Gold `2000000c` — 200 gold | — |
| 76 | Gold `780000c` — 78 gold | Gold `2500000c` — 250 extra gold |
| 77 | Gold `790000c` — 79 gold | — |
| 78 | Item `21540` — Elune's Lantern | — |
| 79 | Gold `810000c` — 81 gold | — |
| 80 | Item `49426` ×15 — Emblem of Frost | Item `49426` ×15 — Emblem of Frost |
| 81 | Gold `830000c` — 83 gold | — |
| 82 | Gold `840000c` — 84 gold | — |
| 83 | Gold `850000c` — 85 gold | — |
| 84 | Gold `860000c` — 86 gold | Dream Chest `0` — Dream Chest |
| 85 | Item `43157` — Tabard of the Kirin Tor | — |
| 86 | Gold `880000c` — 88 gold | — |
| 87 | Gold `890000c` — 89 gold | — |
| 88 | Gold `900000c` — 90 gold | Gold `5000000c` — 500 extra gold |
| 89 | Gold `910000c` — 91 gold | — |
| 90 | Dream Chest `0` — Dream Chest<br>Dream Chest `0` — Dream Chest | — |
| 91 | Gold `930000c` — 93 gold | — |
| 92 | Gold `940000c` — 94 gold | Dream Chest `0` — Dream Chest |
| 93 | Gold `950000c` — 95 gold | — |
| 94 | Gold `960000c` — 96 gold | — |
| 95 | Gold `5000000c` — 500 gold | — |
| 96 | Gold `980000c` — 98 gold | Gold `3000000c` — 300 extra gold |
| 97 | Gold `990000c` — 99 gold | — |
| 98 | Gold `1000000c` — 100 gold | — |
| 99 | Title `175` — Title: Kingslayer | — |
| 100 | Dream Chest `0` ×2 — Dream Chest | Dream Chest `0` ×2 — Dream Chest |

Source: [seasonpass_rewards.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_rewards.sql#L16)

### Tier 0 welcome package

| Reward | Source row |
| --- | --- |
| Item `900134` ×1 — Dream Cowl of the Illidari | Free row, tier 0, slot 0 |
| Item `900135` ×1 — Tabard of the Dream Crusade | Free row, tier 0, slot 1 |
| Item `900136` ×1 — Dream Orb of Deception | Free row, tier 0, slot 2 |
| Gold `50000c` — 5 gold starting capital | Free row, tier 0, slot 3 |

Change the four rows in `seasonpass_rewards.sql`; the click/claim behavior is in `ClaimWelcome` in `SeasonPass.cpp`.

### Class-set rows

The Hero / Free class rows use the classmask values above. Each of the ten supported classes receives a four-piece set at tiers 1, 5, 10, and 15.

| Tier | Class | classmask | Slot | Custom item ID | Item |
| --- | --- | --- | --- | --- | --- |
| 1 | Warrior | `1` | Weapon | `900011` | Nightmare Blade |
| 1 | Paladin | `2` | Weapon | `900021` | Mace of the Hallowed Dream |
| 1 | Hunter | `4` | Weapon | `900031` | Nightmare Bow of the Marksman |
| 1 | Rogue | `8` | Weapon | `900041` | Nightmare Dagger of Shadows |
| 1 | Priest | `16` | Weapon | `900051` | Staff of Silent Dreams |
| 1 | Death Knight | `32` | Weapon | `900061` | Runeblade of the Eternal Nightmare |
| 1 | Shaman | `64` | Weapon | `900071` | Totem Hammer of the Dream Spirits |
| 1 | Mage | `128` | Weapon | `900081` | Staff of the Arcane Nightmare |
| 1 | Warlock | `256` | Weapon | `900091` | Dagger of the Whispering Nightmare |
| 1 | Druid | `1024` | Weapon | `900111` | Staff of the Emerald Dream |
| 5 | Warrior | `1` | Shoulders | `900012` | Shoulderguard of the Nightmare Walker |
| 5 | Paladin | `2` | Shoulders | `900022` | Shoulderplates of the Dream Watch |
| 5 | Hunter | `4` | Shoulders | `900032` | Spaulders of the Dream Stalker |
| 5 | Rogue | `8` | Shoulders | `900042` | Shadowwoven Dream Spaulders |
| 5 | Priest | `16` | Shoulders | `900052` | Mantle of the Dream Seer |
| 5 | Death Knight | `32` | Shoulders | `900062` | Shoulderguard of the Frost Dreamer |
| 5 | Shaman | `64` | Shoulders | `900072` | Spaulders of the Elemental Dream |
| 5 | Mage | `128` | Shoulders | `900082` | Mantle of the Dream Weaver |
| 5 | Warlock | `256` | Shoulders | `900092` | Mantle of the Soul Dream |
| 5 | Druid | `1024` | Shoulders | `900112` | Spaulders of the Dream Walker |
| 10 | Warrior | `1` | Chest | `900013` | Breastplate of the Nightmare Walker |
| 10 | Paladin | `2` | Chest | `900023` | Breastplate of the Dream Watch |
| 10 | Hunter | `4` | Chest | `900033` | Harness of the Dream Stalker |
| 10 | Rogue | `8` | Chest | `900043` | Vest of the Dream Creeper |
| 10 | Priest | `16` | Chest | `900053` | Robe of the Dream Seer |
| 10 | Death Knight | `32` | Chest | `900063` | Breastplate of the Frost Dreamer |
| 10 | Shaman | `64` | Chest | `900073` | Vest of the Elemental Dream |
| 10 | Mage | `128` | Chest | `900083` | Robe of the Dream Weaver |
| 10 | Warlock | `256` | Chest | `900093` | Robe of the Soul Dream |
| 10 | Druid | `1024` | Chest | `900113` | Wildhide Vest of the Dream Walker |
| 15 | Warrior | `1` | Trinket | `900014` | Dreamshard of the Battlemaster |
| 15 | Paladin | `2` | Trinket | `900024` | Dreamshard of the Crusader |
| 15 | Hunter | `4` | Trinket | `900034` | Dreamshard of the Beast Lord |
| 15 | Rogue | `8` | Trinket | `900044` | Dreamshard of the Assassin |
| 15 | Priest | `16` | Trinket | `900054` | Dreamshard of the Light |
| 15 | Death Knight | `32` | Trinket | `900064` | Dreamshard of the Damned |
| 15 | Shaman | `64` | Trinket | `900074` | Dreamshard of the Seer |
| 15 | Mage | `128` | Trinket | `900084` | Dreamshard of the Scholar |
| 15 | Warlock | `256` | Trinket | `900094` | Dreamshard of the Summoner |
| 15 | Druid | `1024` | Trinket | `900114` | Dreamshard of the Wilds |

The row placement is controlled by `seasonpass_rewards.sql`; the item properties and base-template clones are controlled by `seasonpass_items.sql`.

### Custom item definitions

The item SQL creates 58 custom entries in the `900001–900199` range by cloning an existing item template and changing its name, quality, class restrictions, and requirements. Locale names/descriptions are inserted in the same file.

| Custom ID | Cloned template | Item name | Used by |
| --- | --- | --- | --- |
| `900011` | `44096` | Nightmare Blade | Free tier 1; Warrior class set |
| `900012` | `42949` | Shoulderguard of the Nightmare Walker | Free tier 5; Warrior class set |
| `900013` | `48677` | Breastplate of the Nightmare Walker | Free tier 10; Warrior class set |
| `900014` | `42991` | Dreamshard of the Battlemaster | Free tier 15; Warrior class set |
| `900021` | `42945` | Mace of the Hallowed Dream | Free tier 1; Paladin class set |
| `900022` | `42949` | Shoulderplates of the Dream Watch | Free tier 5; Paladin class set |
| `900023` | `48677` | Breastplate of the Dream Watch | Free tier 10; Paladin class set |
| `900024` | `42991` | Dreamshard of the Crusader | Free tier 15; Paladin class set |
| `900031` | `42946` | Nightmare Bow of the Marksman | Free tier 1; Hunter class set |
| `900032` | `42952` | Spaulders of the Dream Stalker | Free tier 5; Hunter class set |
| `900033` | `42984` | Harness of the Dream Stalker | Free tier 10; Hunter class set |
| `900034` | `42991` | Dreamshard of the Beast Lord | Free tier 15; Hunter class set |
| `900041` | `44091` | Nightmare Dagger of Shadows | Free tier 1; Rogue class set |
| `900042` | `42952` | Shadowwoven Dream Spaulders | Free tier 5; Rogue class set |
| `900043` | `42984` | Vest of the Dream Creeper | Free tier 10; Rogue class set |
| `900044` | `42991` | Dreamshard of the Assassin | Free tier 15; Rogue class set |
| `900051` | `42947` | Staff of Silent Dreams | Free tier 1; Priest class set |
| `900052` | `44098` | Mantle of the Dream Seer | Free tier 5; Priest class set |
| `900053` | `42985` | Robe of the Dream Seer | Free tier 10; Priest class set |
| `900054` | `42992` | Dreamshard of the Light | Free tier 15; Priest class set |
| `900061` | `42943` | Runeblade of the Eternal Nightmare | Free tier 1; Death Knight class set |
| `900062` | `42949` | Shoulderguard of the Frost Dreamer | Free tier 5; Death Knight class set |
| `900063` | `48677` | Breastplate of the Frost Dreamer | Free tier 10; Death Knight class set |
| `900064` | `42991` | Dreamshard of the Damned | Free tier 15; Death Knight class set |
| `900071` | `42948` | Totem Hammer of the Dream Spirits | Free tier 1; Shaman class set |
| `900072` | `42951` | Spaulders of the Elemental Dream | Free tier 5; Shaman class set |
| `900073` | `48683` | Vest of the Elemental Dream | Free tier 10; Shaman class set |
| `900074` | `42992` | Dreamshard of the Seer | Free tier 15; Shaman class set |
| `900081` | `44095` | Staff of the Arcane Nightmare | Free tier 1; Mage class set |
| `900082` | `44098` | Mantle of the Dream Weaver | Free tier 5; Mage class set |
| `900083` | `42985` | Robe of the Dream Weaver | Free tier 10; Mage class set |
| `900084` | `42992` | Dreamshard of the Scholar | Free tier 15; Mage class set |
| `900091` | `44091` | Dagger of the Whispering Nightmare | Free tier 1; Warlock class set |
| `900092` | `44098` | Mantle of the Soul Dream | Free tier 5; Warlock class set |
| `900093` | `42985` | Robe of the Soul Dream | Free tier 10; Warlock class set |
| `900094` | `42992` | Dreamshard of the Summoner | Free tier 15; Warlock class set |
| `900101` | `43954` | Reins of the Nightmare Drake | Chest pool |
| `900102` | `23709` | Tabard of the Nightmare | Free tier 44 |
| `900111` | `44095` | Staff of the Emerald Dream | Free tier 1; Druid class set |
| `900112` | `42952` | Spaulders of the Dream Walker | Free tier 5; Druid class set |
| `900113` | `42984` | Wildhide Vest of the Dream Walker | Free tier 10; Druid class set |
| `900114` | `42992` | Dreamshard of the Wilds | Free tier 15; Druid class set |
| `900121` | `43952` | Reins of the Azure Drake | Chest pool |
| `900122` | `43955` | Reins of the Bronze Drake | Chest pool |
| `900123` | `44160` | Reins of the Red Proto-Drake | Chest pool |
| `900124` | `38576` | Big Battle Bear | Chest pool |
| `900125` | `33225` | Reins of the Swift Astral Tiger | Chest pool |
| `900126` | `32458` | Ashes of Al''ar | Chest pool |
| `900127` | `50818` | Invincible''s Reins | Chest pool |
| `900128` | `43986` | Reins of the Black Drake | Chest pool |
| `900129` | `49636` | Reins of the Onyxian Drake | Chest pool |
| `900130` | `43959` | Grand Black War Mammoth | Chest pool |
| `900131` | `45693` | Mimiron''s Head | Chest pool |
| `900132` | `46778` | Magic Rooster Egg | Chest pool |
| `900133` | `13335` | Reins of the Dream Steed | Chest pool |
| `900134` | `32525` | Dream Cowl of the Illidari | Free tier 0 |
| `900135` | `23192` | Tabard of the Dream Crusade | Free tier 0 |
| `900136` | `1973` | Dream Orb of Deception | Free tier 0 |


## 2. Dream Chest rewards

A normal chest (`OpenChest(player, 0)`) first selects a chest tier. A blue chest makes 2 pulls, a mythic chest 3 pulls, and a golden chest 4 pulls. The first pull of a mythic chest has minimum rarity Rare; the first pull of a golden chest has minimum rarity Epic. Every later pull can use all available rarities.

### Chest-tier and rarity odds

| DB chest selector | Meaning | Common (1) | Rare (2) | Epic (3) | Legendary (4) |
| --- | --- | --- | --- | --- | --- |
| 0 | Normal chest tier-up roll (1/2/3); rarity 4 is ignored here | 500 | 350 | 150 | 0 |
| `1` | Blue loot chest | 700 | 240 | 55 | 5 |
| `2` | Mythic loot chest | 450 | 380 | 150 | 20 |
| `3` | Golden loot chest | 250 | 450 | 250 | 50 |

The odds are stored in `seasonpass_chest_rarity.chance` as promille. Chest selector 0 uses only rows 1–3 to choose Blue/Mythic/Golden; Chest Fever increases the Mythic and Golden upgrade weights. For an already selected chest tier, the loader applies the configured rarity rows and increases Epic/Legendary weights with pity.

### Complete 100-entry loot pool

| # | Rarity | Kind | ID | Count | Reward | Blue weight | Mythic weight | Golden weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 Common | Item | `929` | 1 | Item `929` — Healing Potion | 12 | 8 | 5 |
| 2 | 1 Common | Item | `1710` | 2 | Item `1710` — Greater Healing Potion | 12 | 8 | 5 |
| 3 | 1 Common | Item | `3928` | 2 | Item `3928` — Superior Healing Potion | 10 | 8 | 5 |
| 4 | 1 Common | Item | `13446` | 3 | Item `13446` — Major Healing Potion | 10 | 10 | 8 |
| 5 | 1 Common | Item | `33447` | 5 | Item `33447` — Runic Healing Potion | 8 | 10 | 10 |
| 6 | 1 Common | Item | `3827` | 2 | Item `3827` — Mana Potion | 10 | 8 | 5 |
| 7 | 1 Common | Item | `13444` | 3 | Item `13444` — Major Mana Potion | 10 | 10 | 8 |
| 8 | 1 Common | Item | `33448` | 5 | Item `33448` — Runic Mana Potion | 8 | 10 | 10 |
| 9 | 1 Common | Item | `2459` | 2 | Item `2459` — Swiftness Potion | 8 | 8 | 8 |
| 10 | 1 Common | Item | `5634` | 2 | Item `5634` — Free Action Potion | 6 | 8 | 8 |
| 11 | 1 Common | Item | `8529` | 5 | Item `8529` — Noggenfogger Elixir | 8 | 8 | 8 |
| 12 | 1 Common | Item | `6522` | 5 | Item `6522` — Deviate Fish | 8 | 8 | 6 |
| 13 | 1 Common | Item | `4536` | 5 | Item `4536` — Shiny Red Apple | 10 | 5 | 3 |
| 14 | 1 Common | Item | `117` | 5 | Item `117` — Tough Jerky | 10 | 5 | 3 |
| 15 | 1 Common | Item | `1179` | 5 | Item `1179` — Ice Cold Milk | 10 | 5 | 3 |
| 16 | 1 Common | Item | `8952` | 5 | Item `8952` — Roasted Quail | 8 | 6 | 4 |
| 17 | 1 Common | Item | `21215` | 3 | Item `21215` — Graccu's Mince Meat Fruitcake | 6 | 6 | 6 |
| 18 | 1 Common | Item | `17202` | 10 | Item `17202` — Snowball | 8 | 6 | 6 |
| 19 | 1 Common | Item | `21557` | 5 | Item `21557` — Small Red Rocket | 6 | 6 | 6 |
| 20 | 1 Common | Item | `21558` | 5 | Item `21558` — Small Blue Rocket | 6 | 6 | 6 |
| 21 | 1 Common | Item | `21559` | 5 | Item `21559` — Small Green Rocket | 6 | 6 | 6 |
| 22 | 1 Common | Item | `10305` | 3 | Item `10305` — Scroll of Protection IV | 6 | 6 | 4 |
| 23 | 1 Common | Item | `10307` | 3 | Item `10307` — Scroll of Stamina IV | 6 | 6 | 4 |
| 24 | 1 Common | Item | `10308` | 3 | Item `10308` — Scroll of Intellect IV | 6 | 6 | 4 |
| 25 | 1 Common | Item | `10309` | 3 | Item `10309` — Scroll of Strength IV | 6 | 6 | 4 |
| 26 | 1 Common | Item | `10310` | 3 | Item `10310` — Scroll of Agility IV | 6 | 6 | 4 |
| 27 | 1 Common | Item | `14530` | 5 | Item `14530` — Heavy Runecloth Bandage | 8 | 6 | 4 |
| 28 | 1 Common | Item | `21991` | 5 | Item `21991` — Heavy Netherweave Bandage | 6 | 8 | 6 |
| 29 | 1 Common | Item | `34722` | 5 | Item `34722` — Heavy Frostweave Bandage | 6 | 8 | 8 |
| 30 | 1 Common | Item | `2589` | 20 | Item `2589` — Linen Cloth | 10 | 4 | 2 |
| 31 | 1 Common | Item | `14047` | 20 | Item `14047` — Runecloth | 8 | 6 | 3 |
| 32 | 1 Common | Item | `21877` | 20 | Item `21877` — Netherweave Cloth | 6 | 8 | 4 |
| 33 | 1 Common | Item | `33470` | 20 | Item `33470` — Frostweave Cloth | 6 | 8 | 8 |
| 34 | 1 Common | Gold | `10000` | 1 | Gold `10000c` — 1 gold | 10 | 6 | 4 |
| 35 | 1 Common | Gold | `30000` | 1 | Gold `30000c` — 3 gold | 6 | 8 | 6 |
| 36 | 1 Common | Item | `6256` | 1 | Item `6256` — Fishing Pole (dud!) | 5 | 3 | 2 |
| 37 | 1 Common | Item | `2901` | 1 | Item `2901` — Mining Pick (dud!) | 5 | 3 | 2 |
| 38 | 1 Common | Item | `7005` | 1 | Item `7005` — Skinning Knife (dud!) | 5 | 3 | 2 |
| 39 | 2 Rare | Item | `21841` | 1 | Item `21841` — Netherweave Bag (16 slots) | 10 | 10 | 8 |
| 40 | 2 Rare | Item | `41599` | 1 | Item `41599` — Frostweave Bag (20 slots) | 5 | 8 | 10 |
| 41 | 2 Rare | Item | `4500` | 1 | Item `4500` — Traveler's Backpack | 10 | 6 | 4 |
| 42 | 2 Rare | Item | `46376` | 2 | Item `46376` — Flask of the Frost Wyrm | 6 | 8 | 10 |
| 43 | 2 Rare | Item | `46377` | 2 | Item `46377` — Flask of Endless Rage | 6 | 8 | 10 |
| 44 | 2 Rare | Item | `46379` | 2 | Item `46379` — Flask of Stoneblood | 6 | 8 | 10 |
| 45 | 2 Rare | Item | `9206` | 3 | Item `9206` — Elixir of Giants | 8 | 6 | 4 |
| 46 | 2 Rare | Item | `20749` | 3 | Item `20749` — Brilliant Wizard Oil | 6 | 6 | 4 |
| 47 | 2 Rare | Item | `18262` | 3 | Item `18262` — Elemental Sharpening Stone | 6 | 6 | 4 |
| 48 | 2 Rare | Item | `6657` | 3 | Item `6657` — Savory Deviate Delight | 8 | 8 | 6 |
| 49 | 2 Rare | Item | `8410` | 3 | Item `8410` — R.O.I.D.S. | 6 | 6 | 4 |
| 50 | 2 Rare | Item | `34754` | 5 | Item `34754` — Mega Mammoth Meal | 5 | 8 | 8 |
| 51 | 2 Rare | Gold | `100000` | 1 | Gold `100000c` — 10 gold | 10 | 10 | 8 |
| 52 | 2 Rare | Gold | `200000` | 1 | Gold `200000c` — 20 gold | 5 | 8 | 10 |
| 53 | 2 Rare | Item | `8485` | 1 | Item `8485` — Cat Carrier (Bombay) | 6 | 6 | 5 |
| 54 | 2 Rare | Item | `8486` | 1 | Item `8486` — Cat Carrier (Cornish Rex) | 6 | 6 | 5 |
| 55 | 2 Rare | Item | `8487` | 1 | Item `8487` — Cat Carrier (Orange Tabby) | 6 | 6 | 5 |
| 56 | 2 Rare | Item | `8488` | 1 | Item `8488` — Cat Carrier (Silver Tabby) | 6 | 6 | 5 |
| 57 | 2 Rare | Item | `8489` | 1 | Item `8489` — Cat Carrier (White Kitten) | 6 | 6 | 5 |
| 58 | 2 Rare | Item | `8490` | 1 | Item `8490` — Cat Carrier (Siamese) | 6 | 6 | 5 |
| 59 | 2 Rare | Item | `4401` | 1 | Item `4401` — Mechanical Squirrel Box | 6 | 6 | 5 |
| 60 | 2 Rare | Item | `11026` | 1 | Item `11026` — Tree Frog Box | 6 | 6 | 5 |
| 61 | 2 Rare | Item | `11027` | 1 | Item `11027` — Wood Frog Box | 6 | 6 | 5 |
| 62 | 2 Rare | Item | `10393` | 1 | Item `10393` — Cockroach | 6 | 6 | 5 |
| 63 | 2 Rare | Item | `8495` | 1 | Item `8495` — Parrot Cage (Green Wing Macaw) | 6 | 6 | 5 |
| 64 | 2 Rare | Item | `44228` | 1 | Item `44228` — Baby Blizzard Bear | 4 | 5 | 6 |
| 65 | 3 Epic | Item | `1973` | 1 | Item `1973` — Orb of Deception | 8 | 8 | 8 |
| 66 | 3 Epic | Item | `13379` | 1 | Item `13379` — Piccolo of the Flaming Fire | 8 | 8 | 8 |
| 67 | 3 Epic | Item | `18660` | 1 | Item `18660` — World Enlarger | 8 | 8 | 8 |
| 68 | 3 Epic | Item | `38506` | 1 | Item `38506` — Don Carlos' Famous Hat | 6 | 8 | 8 |
| 69 | 3 Epic | Item | `38578` | 1 | Item `38578` — The Flag of Ownership | 6 | 8 | 8 |
| 70 | 3 Epic | Item | `36863` | 1 | Item `36863` — Decahedral Dwarven Dice | 6 | 8 | 8 |
| 71 | 3 Epic | Item | `19970` | 1 | Item `19970` — Arcanite Fishing Pole | 5 | 6 | 8 |
| 72 | 3 Epic | Item | `23705` | 1 | Item `23705` — Tabard of Flame | 6 | 6 | 6 |
| 73 | 3 Epic | Item | `23709` | 1 | Item `23709` — Tabard of Frost | 6 | 6 | 6 |
| 74 | 3 Epic | Item | `43154` | 1 | Item `43154` — Tabard of the Argent Crusade | 6 | 6 | 6 |
| 75 | 3 Epic | Item | `43157` | 1 | Item `43157` — Tabard of the Kirin Tor | 6 | 6 | 6 |
| 76 | 3 Epic | Item | `8494` | 1 | Item `8494` — Hyacinth Macaw | 4 | 6 | 8 |
| 77 | 3 Epic | Item | `8491` | 1 | Item `8491` — Cat Carrier (Black Tabby) | 5 | 6 | 6 |
| 78 | 3 Epic | Item | `38658` | 1 | Item `38658` — Vampiric Batling | 5 | 6 | 6 |
| 79 | 3 Epic | Item | `23713` | 1 | Item `23713` — Hippogryph Hatchling | 5 | 6 | 6 |
| 80 | 3 Epic | Item | `38628` | 1 | Item `38628` — Nether Ray Fry | 5 | 6 | 6 |
| 81 | 3 Epic | Item | `34499` | 1 | Item `34499` — Paper Zeppelin Kit | 5 | 6 | 6 |
| 82 | 3 Epic | Gold | `500000` | 1 | Gold `500000c` — 50 gold | 8 | 8 | 8 |
| 83 | 3 Epic | Gold | `1000000` | 1 | Gold `1000000c` — 100 gold | 4 | 6 | 8 |
| 84 | 3 Epic | Lost Rune | `0` | 1 | Lost Rune — teaches a random unknown ability | 8 | 10 | 12 |
| 85 | 4 Legendary | Item | `900133` | 1 | Item `900133` — Reins of the Dream Steed | 30 | 20 | 12 |
| 86 | 4 Legendary | Item | `900124` | 1 | Item `900124` — Big Battle Bear | 20 | 18 | 12 |
| 87 | 4 Legendary | Item | `900125` | 1 | Item `900125` — Reins of the Swift Astral Tiger | 18 | 16 | 12 |
| 88 | 4 Legendary | Item | `900122` | 1 | Item `900122` — Reins of the Bronze Drake | 14 | 14 | 12 |
| 89 | 4 Legendary | Item | `900128` | 1 | Item `900128` — Reins of the Black Drake | 12 | 14 | 12 |
| 90 | 4 Legendary | Item | `900121` | 1 | Item `900121` — Reins of the Azure Drake | 10 | 12 | 12 |
| 91 | 4 Legendary | Item | `900123` | 1 | Item `900123` — Reins of the Red Proto-Drake | 8 | 10 | 10 |
| 92 | 4 Legendary | Item | `900129` | 1 | Item `900129` — Reins of the Onyxian Drake | 6 | 9 | 10 |
| 93 | 4 Legendary | Item | `900130` | 1 | Item `900130` — Grand Black War Mammoth | 6 | 9 | 10 |
| 94 | 4 Legendary | Item | `900132` | 1 | Item `900132` — Magic Rooster Egg | 4 | 7 | 8 |
| 95 | 4 Legendary | Item | `900126` | 1 | Item `900126` — Ashes of Al'ar | 0 | 4 | 6 |
| 96 | 4 Legendary | Item | `900131` | 1 | Item `900131` — Mimiron's Head | 0 | 3 | 5 |
| 97 | 4 Legendary | Item | `900127` | 1 | Item `900127` — Invincible's Reins | 0 | 2 | 4 |
| 98 | 4 Legendary | Item | `900101` | 1 | Item `900101` — Reins of the Nightmare Drake | 0 | 0 | 3 |
| 99 | 4 Legendary | Gold | `2500000` | 1 | Gold `2500000c` — 250 gold jackpot | 15 | 12 | 8 |
| 100 | 4 Legendary | Gold | `5000000` | 1 | Gold `5000000c` — 500 gold jackpot | 0 | 8 | 8 |

Source: [seasonpass_chest_loot.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_chest_loot.sql#L16)

### Chest behavior

- Chest Fever is stored per character as `chest_pity`. Each chest with no Epic-or-better result adds one stack, capped at 50; any Epic or Legendary result resets it to 0.
- The default pity step is 5% per stack. It scales rarity 3/4 weights for selected chest tiers and scales the normal chest’s Mythic/Golden upgrade weights.
- Each chest opening grants 10 Dream Path points and one chest-achievement progress event.
- Item rewards use the item table and go by mail when bags are full. Gold is credited directly. A Lost Rune teaches a random unknown ability; if all ability runes are known, it pays 25 gold.
- If no valid loot row remains, the fallback is 5 gold.
- `SeasonPass.Chest.LegendaryFromBossPct` and `SeasonPass.Chest.EpicChanceBasePct` are loaded into C++ variables but are not used by the current chest algorithm. Boss kills currently use the normal chest selector and the configured boss chest-drop chance.

## 3. Weekly objectives

Three weekly slots are assigned per character. Base objectives use `type` with `event_type = 255`; Phase 8 objectives use a `Progression::DungeonEvent` `event_type` plus optional filters. A valid database rotation in `seasonpass_weekly_rotation` wins; otherwise the server picks definitions deterministically from the enabled pool.

| ID | Tracked type | Goal | Points | Objective |
| --- | --- | --- | --- | --- |
| `1` | Kills | 150 | 150 | Slaughterfest: Slay 150 enemies |
| `2` | Elite kills | 30 | 150 | Elite Hunter: Slay 30 elites |
| `3` | Boss kills | 5 | 200 | Boss Killer: Slay 5 bosses |
| `4` | Quests | 25 | 150 | Diligent Hero: Complete 25 quests |
| `5` | Level-ups | 3 | 150 | Climber: Gain 3 levels |
| `6` | PvP kills | 10 | 200 | Honor Hunt: Defeat 10 players |
| `7` | Duel wins | 3 | 100 | Duelist: Win 3 duels |
| `8` | Rare kills | 3 | 250 | Rare Hunter: Slay 3 rare enemies |
| `9` | Points | 500 | 150 | Point Collector: Earn 500 points |
| `10` | Kills | 300 | 300 | Mass Battle: Slay 300 enemies |
| `11` | Elite kills | 60 | 300 | Elite Squad: Slay 60 elites |
| `12` | Boss kills | 10 | 400 | Boss Marathon: Slay 10 bosses |
| `13` | Quests | 50 | 300 | Quest Hero: Complete 50 quests |
| `14` | Level-ups | 5 | 250 | Power Leveler: Gain 5 levels |
| `15` | PvP kills | 25 | 400 | Battle Glory: Defeat 25 players |
| `16` | Duel wins | 10 | 250 | Duel Master: Win 10 duels |
| `17` | Rare kills | 5 | 400 | Legend Hunter: Slay 5 rare enemies |
| `18` | Points | 1000 | 300 | Grand Collector: Earn 1000 points |
| `19` | Kills | 500 | 500 | Weekly Quota: Slay 500 enemies |
| `20` | Quests | 75 | 500 | Globetrotter: Complete 75 quests |
| `21` | Discoveries | 2 | 200 | Dream Wanderer: Discover 2 lost places |
| `22` | Discoveries | 5 | 400 | Cartographer: Discover 5 lost places |
| `23` | Active-zone kills | 50 | 200 | Zone Ruler: 50 enemies in the event zone |
| `24` | Active-zone kills | 150 | 400 | Event Marathon: 150 enemies in the event zone |
| `25` | Bounties | 1 | 200 | Bounty Hunter: Claim a daily bounty |
| `26` | Bounties | 3 | 500 | Wanted Poster Collector: 3 bounties this week |
| `27` | Season world bosses | 1 | 300 | Dragon Watch: Defeat a season world boss |
| `28` | Season world bosses | 3 | 600 | Nightmare Conqueror: 3 season world bosses |
| `29` | Kills | 1000 | 600 | Battle Legend: Slay 1000 enemies |
| `30` | Quests | 100 | 600 | Quest Marathon: Complete 100 quests |
| `31` | Elite kills | 100 | 400 | Elite Slayer: Slay 100 elites |
| `32` | Boss kills | 20 | 500 | Boss Tour: Slay 20 bosses |
| `33` | Level-ups | 10 | 400 | Ascension Week: Gain 10 levels |
| `34` | PvP kills | 50 | 500 | Warmonger: Defeat 50 players |
| `35` | Duel wins | 20 | 350 | Duel Lord: Win 20 duels |
| `36` | Rare kills | 10 | 600 | Rare Legend: Slay 10 rare enemies |
| `37` | Points | 2000 | 500 | Point Flood: Earn 2000 points |
| `38` | Points | 3000 | 700 | Point Avalanche: Earn 3000 points |
| `39` | Kills | 750 | 550 | Legions: Slay 750 enemies |
| `40` | Quests | 150 | 700 | Quest God: Complete 150 quests |

Source: [seasonpass_weekly.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_weekly.sql#L12)

### Phase 8 dungeon/event objectives

| ID | Progression event | Goal | Points | Filters | Chest on completion | Enabled |
| --- | --- | --- | --- | --- | --- | --- |
| `1001` | MYTHIC_PLUS_COMPLETE | 1 | 300 | none | — | yes |
| `1002` | MYTHIC_PLUS_COMPLETE | 3 | 450 | none | Blue chest | yes |
| `1003` | MYTHIC_PLUS_TIMER_BEAT | 1 | 300 | none | Blue chest | yes |
| `1004` | MYTHIC_PLUS_BOSS_KILL | 5 | 250 | none | — | yes |
| `1005` | MYTHIC_PLUS_COMPLETE | 1 | 400 | tier ≥3 | Blue chest | yes |
| `1011` | DUNGEON_MASTER_COMPLETE | 1 | 300 | none | — | yes |
| `1012` | DUNGEON_MASTER_COMPLETE | 3 | 600 | none | Blue chest | yes |
| `1013` | DUNGEON_MASTER_COMPLETE | 1 | 600 | difficulty ≥6 | Blue chest | yes |
| `1014` | DUNGEON_MASTER_COMPLETE | 1 | 400 | theme=6 | Blue chest | yes |
| `1015` | DUNGEON_MASTER_COMPLETE | 1 | 400 | theme=9 | Blue chest | yes |
| `1021` | ROGUELIKE_FLOOR_COMPLETE | 1 | 300 | floor ≥3 | — | yes |
| `1022` | ROGUELIKE_FLOOR_COMPLETE | 1 | 500 | floor ≥5 | Blue chest | yes |
| `1023` | ROGUELIKE_FLOOR_COMPLETE | 1 | 700 | floor ≥10 | Mythic chest | yes |
| `1024` | ROGUELIKE_FLOOR_COMPLETE | 25 | 500 | none | Blue chest | yes |

The Phase 8 world update adds the filter columns and `seasonpass_weekly_rotation`; the server matching logic is in `Matches` and event handling is registered by `SeasonPass_loader.cpp`.
Source: [Phase 8 world update](data/sql/updates/pending_db_world/rev_1787850000002_phase8_dream_path_dungeon.sql#L1)

## 4. Achievements

| ID | Kind | Goal | Points | Achievement |
| --- | --- | --- | --- | --- |
| `1` | Tier high-water mark | 10 | 100 | The Beginning: Reach tier 10 |
| `2` | Tier high-water mark | 25 | 200 | Quarter Master: Reach tier 25 |
| `3` | Tier high-water mark | 50 | 300 | Halftime Hero: Reach tier 50 |
| `4` | Tier high-water mark | 75 | 400 | Persister: Reach tier 75 |
| `5` | Tier high-water mark | 100 | 500 | Completionist: Reach tier 100 |
| `6` | Boss | 1 | 150 | Nightmare Baptism: Defeat 1 season world boss |
| `7` | Boss | 10 | 400 | Dragon Terror: Defeat 10 season world bosses |
| `8` | Boss | 25 | 800 | World Savior: Defeat 25 season world bosses |
| `9` | Bounty | 1 | 100 | Wanted: Claim 1 bounty |
| `10` | Bounty | 10 | 400 | Bounty King: Claim 10 bounties |
| `11` | Rune | 3 | 100 | Rune Apprentice: Engrave 3 runes |
| `12` | Rune | 10 | 300 | Rune Master: Engrave 10 runes |
| `13` | Weekly | 10 | 200 | Weekly Hero: Complete 10 weekly goals |
| `14` | Weekly | 50 | 600 | Weekly Legend: Complete 50 weekly goals |
| `15` | Duel | 25 | 200 | Duel King: Win 25 duels |
| `16` | Rare | 25 | 300 | Rarity Hunter: Slay 25 rare enemies |
| `17` | Dungeon | 5 | 300 | Dungeon Wanderer: 5x dungeon of the week |
| `18` | Prestige high-water mark | 1 | 500 | Revenant: Reach prestige 1 |
| `19` | Login streak high-water mark | 7 | 200 | Regular: 7 login days in a row |
| `20` | Discovery | 18 | 500 | Explorer of Azeroth: Find all lost places |
| `21` | Supply | 10 | 200 | Supplier: Complete 10 supply runs |
| `22` | Supply | 50 | 600 | Trade Prince: Complete 50 supply runs |
| `23` | Chest | 10 | 200 | Chest Cracker: Open 10 dream chests |
| `24` | Chest | 50 | 600 | Dream Hoarder: Open 50 dream chests |

Achievement points are added to the pass when an achievement completes; they therefore also receive the normal weekend, zone, storm, and legacy multipliers in `AddPoints`.

## 5. Bounties

| ID | Creature entry | Points | Target | Zone |
| --- | --- | --- | --- | --- |
| `1` | `448` | 150 | Hogger | Elwynn Forest |
| `2` | `522` | 150 | Mor'Ladim | Duskwood |
| `3` | `5828` | 150 | Humar the Pridelord | The Barrens |
| `4` | `5827` | 150 | The Rake | Mulgore |
| `5` | `6584` | 200 | King Mosh | Un'Goro Crater |
| `6` | `3581` | 150 | Sewer Beast | Stormwind |
| `7` | `7846` | 250 | Teremus the Devourer | Blasted Lands |
| `8` | `14445` | 200 | Giant Grizzly | Dun Morogh |

The active bounty is `CurrentDay() % bounty_count`; the active target grants its row points, weekly bounty progress, and bounty-achievement progress.

## 6. Discoveries

| ID | Zone ID | Points | Lost place |
| --- | --- | --- | --- |
| `1` | `41` | 25 | Deadwind Pass |
| `2` | `618` | 25 | Winterspring |
| `3` | `1377` | 25 | Silithus |
| `4` | `490` | 25 | Un'Goro Crater |
| `5` | `361` | 25 | Felwood |
| `6` | `16` | 25 | Azshara |
| `7` | `493` | 25 | Moonglade |
| `8` | `47` | 25 | The Hinterlands |
| `9` | `357` | 25 | Feralas |
| `10` | `4` | 25 | Blasted Lands |
| `11` | `51` | 25 | Searing Gorge |
| `12` | `46` | 25 | Burning Steppes |
| `13` | `3` | 25 | Badlands |
| `14` | `8` | 25 | Swamp of Sorrows |
| `15` | `139` | 25 | Eastern Plaguelands |
| `16` | `28` | 25 | Western Plaguelands |
| `17` | `440` | 25 | Tanaris |
| `18` | `400` | 25 | Thousand Needles |

A character receives a discovery once per zone. Entering the configured zone triggers the row; the Wanderers mutator can multiply its points.

## 7. Dungeon of the week

| ID | Map ID | Points | Dungeon |
| --- | --- | --- | --- |
| `1` | `389` | 300 | Ragefire Chasm |
| `2` | `36` | 300 | The Deadmines |
| `3` | `43` | 300 | Wailing Caverns |
| `4` | `33` | 300 | Shadowfang Keep |
| `5` | `48` | 300 | Blackfathom Deeps |
| `6` | `90` | 300 | Gnomeregan |
| `7` | `189` | 300 | Scarlet Monastery |
| `8` | `209` | 300 | Zul'Farrak |
| `9` | `109` | 350 | The Temple of Atal'Hakkar |
| `10` | `230` | 350 | Blackrock Depths |
| `11` | `329` | 400 | Stratholme |
| `12` | `289` | 400 | Scholomance |

The active row is `CurrentWeek() % dungeon_count`. Killing a dungeon boss in that map completes the weekly dungeon activity, grants the row points, and progresses the dungeon achievement.

## 8. Season world bosses

| ID | Creature entry | Map | Coordinates (x, y, z, o) | Boss | Spawn zone |
| --- | --- | --- | --- | --- | --- |
| `1` | `14890` | `0` | -10432.0, -392.0, 43.0, 0.0 | Taerar | Duskwood (Twilight Grove) |
| `2` | `14888` | `0` | 815.0, -510.0, 180.0, 0.0 | Lethon | The Hinterlands (Seradane) |
| `3` | `14887` | `1` | -2882.0, 1930.0, 60.0, 0.0 | Ysondre | Feralas (Dream Bough) |
| `4` | `14889` | `1` | 3050.0, -3460.0, 140.0, 0.0 | Emeriss | Ashenvale (Bough Shadow) |
| `5` | `12397` | `0` | -11800.0, -3190.0, 6.0, 0.0 | Lord Kazzak | Blasted Lands |
| `6` | `6109` | `1` | 2550.0, -5670.0, 100.0, 0.0 | Azuregos | Azshara |

Default behavior: one row rotates every 6 hours, the spawned boss despawns after 120 minutes, and the active boss kill grants 250 bonus points plus weekly/achievement progress. The configured world-buff spell is 22888 by default and is applied to tracked players who are online when the active boss dies.

## 9. Rotating event zones

| ID | Zone ID | Zone |
| --- | --- | --- |
| `1` | `33` | Stranglethorn Vale (Blood Moon!) |
| `2` | `331` | Ashenvale (Battle for Ashenvale!) |
| `3` | `40` | Westfall |
| `4` | `267` | Hillsbrad Foothills |
| `5` | `490` | Un'Goro Crater |
| `6` | `618` | Winterspring |
| `7` | `3` | Badlands |
| `8` | `47` | The Hinterlands |
| `9` | `400` | Thousand Needles |
| `10` | `139` | Eastern Plaguelands |
| `11` | `357` | Feralas |
| `12` | `65` | Dragonblight |

The active zone rotates every 3 hours by default. Points earned while the player is in that zone are multiplied by 200%; kills there also progress the active-zone weekly objective.

## 10. Seasonal runes

The first 12 rows are permanent aura buffs (`kind = 0`); the last 12 are ability runes (`kind = 1`). All current rows have classmask 0, so they are available to every tracked class. Base slots default to 3, with one extra slot at tiers 25, 50, and 75.

| ID | classmask | Kind | Spell ID | Cost | Rune |
| --- | --- | --- | --- | --- | --- |
| `1` | `0` | Permanent aura | `1126` | 500000c (50g) | Rune of the Wild |
| `2` | `0` | Permanent aura | `1243` | 500000c (50g) | Rune of Fortitude |
| `3` | `0` | Permanent aura | `1459` | 500000c (50g) | Rune of Intellect |
| `4` | `0` | Permanent aura | `14752` | 500000c (50g) | Rune of Spirit |
| `5` | `0` | Permanent aura | `20217` | 1000000c (100g) | Rune of Kings |
| `6` | `0` | Permanent aura | `19740` | 1000000c (100g) | Rune of Might |
| `7` | `0` | Permanent aura | `19742` | 1000000c (100g) | Rune of Wisdom |
| `8` | `0` | Permanent aura | `467` | 750000c (75g) | Rune of Thorns |
| `9` | `0` | Permanent aura | `976` | 750000c (75g) | Rune of Shadow Protection |
| `10` | `0` | Permanent aura | `20911` | 1500000c (150g) | Rune of Sanctuary |
| `11` | `0` | Permanent aura | `19506` | 1500000c (150g) | Rune of Trueshot |
| `12` | `0` | Permanent aura | `24932` | 1500000c (150g) | Rune of the Pack |
| `13` | `0` | Ability | `355` | 1000000c (100g) | Rune of Taunt |
| `14` | `0` | Ability | `25780` | 1000000c (100g) | Rune of Righteous Fury |
| `15` | `0` | Ability | `6346` | 1000000c (100g) | Rune of Fear Ward |
| `16` | `0` | Ability | `1953` | 1500000c (150g) | Rune of Blink |
| `17` | `0` | Ability | `11305` | 1500000c (150g) | Rune of Sprint |
| `18` | `0` | Ability | `1787` | 2000000c (200g) | Rune of Stealth |
| `19` | `0` | Ability | `556` | 1000000c (100g) | Rune of Astral Recall |
| `20` | `0` | Ability | `546` | 750000c (75g) | Rune of Water Walking |
| `21` | `0` | Ability | `5697` | 750000c (75g) | Rune of Water Breathing |
| `22` | `0` | Ability | `48788` | 2000000c (200g) | Rune of Lay on Hands |
| `23` | `0` | Ability | `6197` | 750000c (75g) | Rune of Eagle Eye |
| `24` | `0` | Ability | `2825` | 2500000c (250g) | Rune of Bloodlust |

Engraving/removing a rune persists in `character_seasonpass_runes`. Permanent buff runes also contribute to the optional Runic Resonance bonus.

## 11. Supply contracts

Each row requires the item and count shown, then pays the configured points and copper. The active contract is daily and is persisted by `supply_day`.

| ID | Required item ID | Count | Points | Gold |
| --- | --- | --- | --- | --- |
| `1` | `2589` | 20 | 150 | 5000c (0.5g) |
| `2` | `2592` | 20 | 150 | 8000c (0.8g) |
| `3` | `4306` | 20 | 150 | 12000c (1.2g) |
| `4` | `4338` | 20 | 150 | 16000c (1.6g) |
| `5` | `14047` | 20 | 150 | 25000c (2.5g) |
| `6` | `21877` | 20 | 150 | 35000c (3.5g) |
| `7` | `33470` | 20 | 150 | 50000c (5g) |
| `8` | `2770` | 20 | 150 | 5000c (0.5g) |
| `9` | `2771` | 20 | 150 | 8000c (0.8g) |
| `10` | `2772` | 20 | 150 | 12000c (1.2g) |
| `11` | `3858` | 20 | 150 | 20000c (2g) |
| `12` | `10620` | 20 | 150 | 30000c (3g) |
| `13` | `23424` | 20 | 150 | 40000c (4g) |
| `14` | `36909` | 20 | 150 | 50000c (5g) |
| `15` | `2318` | 20 | 150 | 5000c (0.5g) |
| `16` | `2319` | 20 | 150 | 8000c (0.8g) |
| `17` | `4234` | 20 | 150 | 12000c (1.2g) |
| `18` | `4304` | 20 | 150 | 20000c (2g) |
| `19` | `8170` | 20 | 150 | 30000c (3g) |
| `20` | `21887` | 20 | 150 | 40000c (4g) |
| `21` | `33568` | 20 | 150 | 50000c (5g) |


## 12. Fishing contracts

The active fish rotates daily. Looting the active fish counts toward the contract; completion pays the row reward and opens one normal Dream Chest.

| ID | Required fish item ID | Count | Points | Gold |
| --- | --- | --- | --- | --- |
| `1` | `6291` | 10 | 150 | 100000c (10g) |
| `2` | `6289` | 10 | 150 | 100000c (10g) |
| `3` | `6308` | 10 | 150 | 100000c (10g) |
| `4` | `6358` | 10 | 150 | 100000c (10g) |
| `5` | `6359` | 10 | 150 | 100000c (10g) |
| `6` | `4603` | 10 | 150 | 100000c (10g) |
| `7` | `6362` | 10 | 150 | 100000c (10g) |
| `8` | `13754` | 10 | 150 | 100000c (10g) |
| `9` | `27422` | 10 | 150 | 100000c (10g) |
| `10` | `41800` | 10 | 150 | 100000c (10g) |


## 13. Weekly mutators

| ID | Kind | Value | Mutator |
| --- | --- | --- | --- |
| `1` | Quest points | 200% | Week of Scholars: quest points x2 |
| `2` | Elite points | 200% | Week of Giants: elite points x2 |
| `3` | Rare points | 200% | Week of Hunters: rare points x2 |
| `4` | PvP/duel points | 200% | Week of Blood: PvP and duel points x2 |
| `5` | XP | 125% | Week of Wisdom: +25% experience |
| `6` | Chest chance | 200% | Chest Week: double chest chance |
| `7` | Weekly-goal points | 200% | Week of Duty: weekly goal points x2 |
| `8` | Discovery points | 200% | Week of Wanderers: discovery points x2 |

The active row is selected from `CurrentWeek() % mutator_count`. Mutator value affects only the matching source kind; chest-week modifies chest-drop chance, not the chest loot rarity table.

## 14. Teleports

| ID | Destination | Map | Coordinates (x, y, z, o) |
| --- | --- | --- | --- |
| `1` | Stormwind | 0 | -8833.4, 628.6, 94.0, 1.06 |
| `2` | Ironforge | 0 | -4981.3, -881.5, 501.7, 5.40 |
| `3` | Darnassus | 1 | 9947.5, 2482.7, 1316.2, 0.00 |
| `4` | The Exodar | 530 | -3965.7, -11653.6, -138.8, 0.85 |
| `5` | Orgrimmar | 1 | 1601.1, -4378.7, 10.0, 2.14 |
| `6` | Undercity | 0 | 1633.8, 240.2, -43.1, 6.26 |
| `7` | Thunder Bluff | 1 | -1277.4, 124.8, 131.3, 5.22 |
| `8` | Silvermoon | 530 | 9738.3, -7454.2, 13.6, 0.04 |
| `9` | Shattrath | 530 | -1887.6, 5359.1, -12.4, 4.40 |
| `10` | Dalaran | 571 | 5809.6, 448.9, 658.8, 5.26 |
| `11` | Gadgetzan | 1 | -7176.6, -3785.3, 8.4, 5.80 |
| `12` | Booty Bay | 0 | -14297.2, 518.0, 8.8, 3.90 |

Teleporting is blocked in combat. Destination 999 is reserved for the currently active season world boss and is not a SQL teleport row.

## 15. Season vendor

The logical shop has 119 slots. `kind = 0` sells an item; `kind = 1` opens the chest tier in `item` (slot 1 is a normal chest with item 0). Prices are copper.

| Slot | Category | Kind | Item / chest ID | Count | Price |
| --- | --- | --- | --- | --- | --- |
| `1` | Dream Chest & Fun | Mystery box | `0` | 1 | 1000000c (100g) |
| `2` | Dream Chest & Fun | Item | `8529` | 3 | 37500c (3.75g) |
| `3` | Dream Chest & Fun | Item | `17202` | 10 | 750c (0.075g) |
| `4` | Dream Chest & Fun | Item | `18662` | 1 | 15000c (1.5g) |
| `5` | Dream Chest & Fun | Item | `4365` | 5 | 7500c (0.75g) |
| `6` | Dream Chest & Fun | Item | `4390` | 5 | 12000c (1.2g) |
| `7` | Dream Chest & Fun | Item | `10646` | 3 | 120000c (12g) |
| `8` | Potions & Bandages | Item | `118` | 5 | 750c (0.075g) |
| `9` | Potions & Bandages | Item | `858` | 5 | 3000c (0.3g) |
| `10` | Potions & Bandages | Item | `929` | 5 | 7500c (0.75g) |
| `11` | Potions & Bandages | Item | `1710` | 5 | 18000c (1.8g) |
| `12` | Potions & Bandages | Item | `3928` | 5 | 45000c (4.5g) |
| `13` | Potions & Bandages | Item | `13446` | 5 | 112500c (11.25g) |
| `14` | Potions & Bandages | Item | `22829` | 5 | 225000c (22.5g) |
| `15` | Potions & Bandages | Item | `33447` | 5 | 375000c (37.5g) |
| `16` | Potions & Bandages | Item | `2455` | 5 | 750c (0.075g) |
| `17` | Potions & Bandages | Item | `3385` | 5 | 3000c (0.3g) |
| `18` | Potions & Bandages | Item | `3827` | 5 | 7500c (0.75g) |
| `19` | Potions & Bandages | Item | `6149` | 5 | 18000c (1.8g) |
| `20` | Potions & Bandages | Item | `13443` | 5 | 45000c (4.5g) |
| `21` | Potions & Bandages | Item | `13444` | 5 | 112500c (11.25g) |
| `22` | Potions & Bandages | Item | `22832` | 5 | 225000c (22.5g) |
| `23` | Potions & Bandages | Item | `33448` | 5 | 375000c (37.5g) |
| `24` | Potions & Bandages | Item | `1251` | 5 | 375c (0.0375g) |
| `25` | Potions & Bandages | Item | `2581` | 5 | 750c (0.075g) |
| `26` | Potions & Bandages | Item | `3530` | 5 | 1500c (0.15g) |
| `27` | Potions & Bandages | Item | `3531` | 5 | 3000c (0.3g) |
| `28` | Potions & Bandages | Item | `6450` | 5 | 6000c (0.6g) |
| `29` | Potions & Bandages | Item | `6451` | 5 | 10500c (1.05g) |
| `30` | Potions & Bandages | Item | `8544` | 5 | 18000c (1.8g) |
| `31` | Potions & Bandages | Item | `8545` | 5 | 30000c (3g) |
| `32` | Potions & Bandages | Item | `14529` | 5 | 52500c (5.25g) |
| `33` | Potions & Bandages | Item | `14530` | 5 | 75000c (7.5g) |
| `34` | Potions & Bandages | Item | `21990` | 5 | 120000c (12g) |
| `35` | Potions & Bandages | Item | `21991` | 5 | 180000c (18g) |
| `36` | Potions & Bandages | Item | `34721` | 5 | 270000c (27g) |
| `37` | Potions & Bandages | Item | `34722` | 5 | 375000c (37.5g) |
| `38` | Food & Drink | Item | `117` | 5 | 150c (0.015g) |
| `39` | Food & Drink | Item | `4540` | 5 | 150c (0.015g) |
| `40` | Food & Drink | Item | `2287` | 5 | 450c (0.045g) |
| `41` | Food & Drink | Item | `4541` | 5 | 450c (0.045g) |
| `42` | Food & Drink | Item | `3770` | 5 | 1200c (0.12g) |
| `43` | Food & Drink | Item | `4542` | 5 | 1200c (0.12g) |
| `44` | Food & Drink | Item | `3771` | 5 | 3000c (0.3g) |
| `45` | Food & Drink | Item | `4544` | 5 | 3000c (0.3g) |
| `46` | Food & Drink | Item | `4599` | 5 | 7500c (0.75g) |
| `47` | Food & Drink | Item | `8952` | 5 | 15000c (1.5g) |
| `48` | Food & Drink | Item | `4536` | 5 | 225c (0.0225g) |
| `49` | Food & Drink | Item | `159` | 5 | 150c (0.015g) |
| `50` | Food & Drink | Item | `1179` | 5 | 450c (0.045g) |
| `51` | Food & Drink | Item | `1205` | 5 | 1200c (0.12g) |
| `52` | Food & Drink | Item | `1708` | 5 | 3000c (0.3g) |
| `53` | Food & Drink | Item | `8766` | 5 | 7500c (0.75g) |
| `54` | Food & Drink | Item | `28399` | 5 | 15000c (1.5g) |
| `55` | Food & Drink | Item | `33445` | 5 | 30000c (3g) |
| `56` | Elixirs & Buffs | Item | `2454` | 3 | 2250c (0.225g) |
| `57` | Elixirs & Buffs | Item | `3390` | 3 | 3750c (0.375g) |
| `58` | Elixirs & Buffs | Item | `2457` | 3 | 3000c (0.3g) |
| `59` | Elixirs & Buffs | Item | `5997` | 3 | 3750c (0.375g) |
| `60` | Elixirs & Buffs | Item | `6373` | 3 | 7500c (0.75g) |
| `61` | Elixirs & Buffs | Item | `3825` | 3 | 12000c (1.2g) |
| `62` | Elixirs & Buffs | Item | `8949` | 3 | 15000c (1.5g) |
| `63` | Elixirs & Buffs | Item | `9187` | 3 | 30000c (3g) |
| `64` | Elixirs & Buffs | Item | `9206` | 3 | 60000c (6g) |
| `65` | Elixirs & Buffs | Item | `13452` | 3 | 90000c (9g) |
| `66` | Elixirs & Buffs | Item | `13454` | 3 | 90000c (9g) |
| `67` | Elixirs & Buffs | Item | `9088` | 3 | 75000c (7.5g) |
| `68` | Elixirs & Buffs | Item | `9036` | 3 | 22500c (2.25g) |
| `69` | Elixirs & Buffs | Item | `2459` | 3 | 30000c (3g) |
| `70` | Elixirs & Buffs | Item | `5634` | 3 | 75000c (7.5g) |
| `71` | Elixirs & Buffs | Item | `5631` | 3 | 15000c (1.5g) |
| `72` | Elixirs & Buffs | Item | `5633` | 3 | 45000c (4.5g) |
| `73` | Elixirs & Buffs | Item | `6049` | 3 | 37500c (3.75g) |
| `74` | Elixirs & Buffs | Item | `6048` | 3 | 37500c (3.75g) |
| `75` | Elixirs & Buffs | Item | `6050` | 3 | 37500c (3.75g) |
| `76` | Elixirs & Buffs | Item | `4623` | 3 | 22500c (2.25g) |
| `77` | Elixirs & Buffs | Item | `9172` | 3 | 90000c (9g) |
| `78` | Elixirs & Buffs | Item | `3387` | 1 | 225000c (22.5g) |
| `79` | Bags & Ammo | Item | `954` | 5 | 7500c (0.75g) |
| `80` | Bags & Ammo | Item | `955` | 5 | 7500c (0.75g) |
| `81` | Bags & Ammo | Item | `1180` | 5 | 7500c (0.75g) |
| `82` | Bags & Ammo | Item | `3012` | 5 | 7500c (0.75g) |
| `83` | Bags & Ammo | Item | `4496` | 1 | 3000c (0.3g) |
| `84` | Bags & Ammo | Item | `4498` | 1 | 9000c (0.9g) |
| `85` | Bags & Ammo | Item | `4497` | 1 | 22500c (2.25g) |
| `86` | Bags & Ammo | Item | `4499` | 1 | 52500c (5.25g) |
| `87` | Bags & Ammo | Item | `21841` | 1 | 225000c (22.5g) |
| `88` | Bags & Ammo | Item | `41599` | 1 | 750000c (75g) |
| `89` | Bags & Ammo | Item | `2512` | 200 | 750c (0.075g) |
| `90` | Bags & Ammo | Item | `3030` | 200 | 7500c (0.75g) |
| `91` | Bags & Ammo | Item | `11285` | 200 | 30000c (3g) |
| `92` | Bags & Ammo | Item | `2516` | 200 | 750c (0.075g) |
| `93` | Bags & Ammo | Item | `3033` | 200 | 7500c (0.75g) |
| `94` | Bags & Ammo | Item | `11284` | 200 | 30000c (3g) |
| `95` | Reagents & Professions | Item | `17056` | 10 | 3000c (0.3g) |
| `96` | Reagents & Professions | Item | `17057` | 10 | 3000c (0.3g) |
| `97` | Reagents & Professions | Item | `17058` | 10 | 3000c (0.3g) |
| `98` | Reagents & Professions | Item | `17021` | 10 | 7500c (0.75g) |
| `99` | Reagents & Professions | Item | `17026` | 10 | 15000c (1.5g) |
| `100` | Reagents & Professions | Item | `17029` | 10 | 22500c (2.25g) |
| `101` | Reagents & Professions | Item | `17030` | 3 | 30000c (3g) |
| `102` | Reagents & Professions | Item | `17031` | 10 | 15000c (1.5g) |
| `103` | Reagents & Professions | Item | `17032` | 10 | 30000c (3g) |
| `104` | Reagents & Professions | Item | `16583` | 3 | 22500c (2.25g) |
| `105` | Reagents & Professions | Item | `5565` | 3 | 15000c (1.5g) |
| `106` | Reagents & Professions | Item | `21177` | 10 | 22500c (2.25g) |
| `107` | Reagents & Professions | Item | `17033` | 3 | 30000c (3g) |
| `108` | Reagents & Professions | Item | `6529` | 10 | 1500c (0.15g) |
| `109` | Reagents & Professions | Item | `6530` | 10 | 3750c (0.375g) |
| `110` | Reagents & Professions | Item | `2320` | 10 | 750c (0.075g) |
| `111` | Reagents & Professions | Item | `2321` | 10 | 2250c (0.225g) |
| `112` | Reagents & Professions | Item | `4291` | 10 | 6000c (0.6g) |
| `113` | Reagents & Professions | Item | `8343` | 10 | 12000c (1.2g) |
| `114` | Reagents & Professions | Item | `14341` | 10 | 22500c (2.25g) |
| `115` | Reagents & Professions | Item | `2324` | 5 | 1500c (0.15g) |
| `116` | Reagents & Professions | Item | `2325` | 5 | 3750c (0.375g) |
| `117` | Reagents & Professions | Item | `6260` | 5 | 3750c (0.375g) |
| `118` | Reagents & Professions | Item | `2604` | 5 | 3750c (0.375g) |
| `119` | Reagents & Professions | Item | `4340` | 5 | 3750c (0.375g) |

The same SQL file also mirrors the catalog into the `npc_vendor` table for vendor entry 987002. Change the logical shop rows first; update the mirror if the vendor presentation must change.

## 16. Runtime progression and non-table rewards

### Default point sources

| Source | Default points | Notes |
| --- | --- | --- |
| Quest completion | 10 | Can be modified by the quest mutator. |
| Normal creature kill | 1 | Kills more than 8 levels below the player are ignored. |
| Elite kill | 5 | Can be modified by the elite mutator. |
| Boss kill | 100 | Dungeon/world-boss classification also progresses boss objectives. |
| Rare kill | 25 | Can be modified by the rare mutator. |
| Level-up | 50 | Awarded when the player gains a level. |
| Daily login | 50 + streak bonus | First login starts the streak silently; later consecutive days add `min(streak - 1, 10) × 5` by default. |
| PvP kill | 10 | The same victim is rate-limited for 300 seconds by default. |
| Duel win | 5 | Can be modified by the PvP/duel mutator. |
| Chest opening | 10 | Added after all chest pulls resolve. |
| Supply/fishing/dungeon/bounty/discovery | SQL row value | The corresponding table row controls the amount. |
| Weekly goal | SQL row value | The weekly-points mutator can multiply it. |
| Achievement | SQL row value | Added when that achievement completes. |


### Multipliers and extra rewards

- Bonus weekend: Saturday and Sunday in server local time; default 200% Dream Path points and 150% XP.
- Active event zone: default 200% points for tracked players in the active zone.
- Dream Storm: a deterministic random 15-minute window within selected hours; default 300% points.
- After internal Prestige is active, Season Legacy adds `prestige × PointsPercentPerPrestige` to point gain.
- At every 10th character level, the level chest pays `GoldPer10Levels × (level / 10)`; from level 20 onward it mails `BagItem` (21841 by default).
- After tier 100, normal point overflow becomes Dream Renown cycles. With internal Prestige mode enabled, a completed point bar after the first Prestige becomes another Prestige instead of another normal tier.

### Prestige and Dream Forge

Prestige is disabled by default in the effective runtime because `InternalPrestige.Enable = 0`; `SeasonPass.Prestige.Enable = 1` alone does not enable it. When enabled, the character must reach the max tier, claim due rewards, and confirm Prestige. Points and claim counters reset, rewards remain owned, Prestige increments, and the character receives:

| Reward | Default | Change point |
| --- | --- | --- |
| Prestige gold | 500000 copper at Prestige 1, then +100000 copper per prior Prestige | [SeasonPass.cpp](modules/mod-seasonpass/src/SeasonPass.cpp#L168) |
| Dream Forge points | 2 per Prestige | [SeasonPass.cpp](modules/mod-seasonpass/src/SeasonPass.cpp#L173) |
| Automatic Prestige gold | 100000 copper per bar in Prestige mode | [SeasonPass.cpp](modules/mod-seasonpass/src/SeasonPass.cpp#L170) |
| Optional mob scaling | +1% damage/effective health per Prestige | [SeasonPass.cpp](modules/mod-seasonpass/src/SeasonPass.cpp#L174) |

Dream Forge stats are persisted in `character_seasonpass_paragon`; each stat has its own cap (75 by default). The eight stats are Power, Spellcraft, Area effect, Toxins, Vitality, Soul Power, Healing, and Wisdom.

### Hardcore status

The character schema contains a `hardcore` state and the UI contains Hardcore labels, but the current Season Pass C++ source has no active Hardcore start/death/completion handler. Do not treat the `ACH_HARDCORE` kind or the UI text as an implemented reward path until that behavior is added.

## 17. Persistence and UI

| State | What it stores | Schema/source |
| --- | --- | --- |
| Core character progress | Season, points, Free/Hero claim counters, login/streak, prestige, XP rate, language, Chest Fever, welcome claimed, Hardcore state, supply/fishing day and count, Renown | [seasonpass_progress.sql](modules/mod-seasonpass/data/sql/db-characters/seasonpass_progress.sql#L24) |
| Weekly state | Three displayed slots; slot 8 is the Dream Swap marker and slot 9 is the dungeon marker | [seasonpass_progress.sql](modules/mod-seasonpass/data/sql/db-characters/seasonpass_progress.sql#L108) |
| Runes | Engraved rune IDs per character | [seasonpass_progress.sql](modules/mod-seasonpass/data/sql/db-characters/seasonpass_progress.sql#L118) |
| Achievements | Progress and completion per achievement | [seasonpass_progress.sql](modules/mod-seasonpass/data/sql/db-characters/seasonpass_progress.sql#L126) |
| Discoveries | Discovered zone IDs per character | [seasonpass_progress.sql](modules/mod-seasonpass/data/sql/db-characters/seasonpass_progress.sql#L134) |
| Dream Forge | Allocated points for stats 1–8 | [seasonpass_paragon.sql](modules/mod-seasonpass/data/sql/db-characters/seasonpass_paragon.sql#L4) |
| Phase 8 event credit | Per-event deduplication key: character, season, event type, source, start time, and detail | [Phase 8 character update](data/sql/updates/pending_db_characters/rev_1787850000002_phase8_dream_path_dungeon.sql#L4) |


The UI display mirror is split across:

- [SeasonPassData.lua](modules/mod-seasonpass/SeasonPassUI/SeasonPassData.lua#L1) — generated tier/chest/supporting-data mirror and the season label.
- [SeasonPass.lua](modules/mod-seasonpass/SeasonPassUI/SeasonPass.lua#L1) — main window, reward rendering, weekly/supply/fishing/shop/rune/event panels, and server-message parsing.
- [SeasonPassHUD.lua](modules/mod-seasonpass/SeasonPassUI/SeasonPassHUD.lua#L1) — HUD strings and status display.
Phase 8 objective rows are not currently mirrored in `SeasonPassData.lua`; SQL plus server-side C++ are authoritative for those objectives.

## 18. Where to change it

Use this table as the edit map. Change the data row first; only change C++ when the behavior itself needs to change.

| What to change | Edit here | Notes |
| --- | --- | --- |
| Free or Hero tier reward, count, title, gold, chest, or classmask | [seasonpass_rewards.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_rewards.sql#L16) | Edit the matching `season/tier/track/classmask/slot` row. `GrantTier`/`ClaimDue` consume it. |
| Custom reward item stats, requirements, English name, or German locale | [seasonpass_items.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_items.sql#L1) | Edit the clone/update block for the custom entry. Keep the reward row’s item ID aligned. |
| Chest item/gold/rune, rarity, count, or per-chest weight | [seasonpass_chest_loot.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_chest_loot.sql#L16) | Edit `seasonpass_chest_loot`; weights are relative within rarity. |
| Chest rarity odds and normal-chest upgrade odds | [seasonpass_chest_loot.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_chest_loot.sql#L319) | Edit `seasonpass_chest_rarity`; selector 0’s rarity-4 row is not used for normal tier selection. |
| Base weekly objective | [seasonpass_weekly.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_weekly.sql#L12) | Edit `id/type/goal/points/name/name_en`. |
| Phase 8 weekly filters or event objective | [Phase 8 weekly update](data/sql/updates/pending_db_world/rev_1787850000002_phase8_dream_path_dungeon.sql#L70) | Edit the objective row and its filter columns; `Matches` enforces them. |
| Which three weekly goals are active | [weekly rotation schema](data/sql/updates/pending_db_world/rev_1787850000002_phase8_dream_path_dungeon.sql#L61) | Populate `seasonpass_weekly_rotation` for a season/week/slot; slots are 0–2. |
| Achievement definition and points | [seasonpass_achievements.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_achievements.sql#L3) | Edit `kind/goal/points/name/name_en`. |
| Daily bounty target, zone, and points | [seasonpass_bounty.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_bounty.sql#L3) | Edit the row; active selection is day modulo row count. |
| Discovery zone and points | [seasonpass_discoveries.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_discoveries.sql#L3) | Edit `zone/points/name/name_en`. |
| Dungeon-of-the-week map and points | [seasonpass_dungeons.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_dungeons.sql#L3) | Edit `map/points/name/name_en`. |
| Season world boss entry, map, spawn point, and label | [seasonpass_worldboss.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_worldboss.sql#L3) | Edit the row; rotation/bonus/despawn behavior is config. |
| Rotating event zone | [seasonpass_zones.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_zones.sql#L3) | Edit zone ID/labels; rotation interval and multiplier are config. |
| Rune spell, kind, classmask, and cost | [seasonpass_runes.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_runes.sql#L3) | Edit the rune row; slot count and resonance are config/C++. |
| Supply contract | [seasonpass_supplies.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_supplies.sql#L3) | Edit required item/count/points/gold. |
| Fishing contract | [seasonpass_fish.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_fish.sql#L3) | Edit active fish/count/points/gold. |
| Weekly mutator | [seasonpass_mutators.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_mutators.sql#L3) | Edit kind/value/labels; selection is week modulo row count. |
| Teleport destination and coordinates | [seasonpass_teleports.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_teleports.sql#L3) | Edit map and x/y/z/o. |
| Season vendor shop slot, item, quantity, or price | [seasonpass_vendor.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_vendor.sql#L3) | Edit `seasonpass_shop`; synchronize the `npc_vendor` mirror if needed. |
| NPC entries, names, scripts, or display models | [seasonpass_npc.sql](modules/mod-seasonpass/data/sql/db-world/seasonpass_npc.sql#L7) | NPCs 987000–987003 expose the pass, runes, shop, and teleporter. |
| Point values, multipliers, drop chances, level chest, Storm, or enable flags | [seasonpass.conf.dist](modules/mod-seasonpass/conf/seasonpass.conf.dist#L8) | Edit the distributed defaults; runtime config must contain the same keys. |
| Prestige/Dream Forge values | [SeasonPass.cpp](modules/mod-seasonpass/src/SeasonPass.cpp#L964) | Several advanced keys are loaded with C++ defaults even though they are not present in the distributed template; see the config table below. |
| Chest algorithm, claim handling, level chest, points, or prestige behavior | [SeasonPass.cpp](modules/mod-seasonpass/src/SeasonPass.cpp#L436) | Change `RollChestLoot`, `OpenChest`, `AddPoints`, `GrantTier`, `ClaimDue`, or the relevant hook. |
| Weekly/event matching, rotations, runes, bosses, zones, and supporting table loaders | [SeasonPassSeason.cpp](modules/mod-seasonpass/src/SeasonPassSeason.cpp#L168) | Change loader/selection/event behavior only when SQL/config cannot express the desired rule. |
| Dungeon event registration | [SeasonPass_loader.cpp](modules/mod-seasonpass/src/SeasonPass_loader.cpp#L8) | The loader connects `Progression::DungeonEvent` to `HandleDungeonEvent`. |
| Client reward panels, labels, and display mirror | [SeasonPassData.lua](modules/mod-seasonpass/SeasonPassUI/SeasonPassData.lua#L1) | Update the generated mirror and the matching panel/parser in `SeasonPass.lua`; server data remains authoritative. |
| Persistent progress/state schema | [seasonpass_progress.sql](modules/mod-seasonpass/data/sql/db-characters/seasonpass_progress.sql#L24) | Change only for new persisted fields/migrations; core state is written by `SaveData`. |
| Phase 8 event deduplication persistence | [Phase 8 character update](data/sql/updates/pending_db_characters/rev_1787850000002_phase8_dream_path_dungeon.sql#L4) | Change only if the event-credit identity or retention policy changes. |


## 19. Configuration reference

The distributed template is the intended default source. `env/dist/etc/modules/seasonpass.conf` is the effective generated runtime copy in this checkout. Values below are the current defaults read by C++.

| Key | Default | Effect |
| --- | --- | --- |
| SeasonPass.Enable | 1 | Master switch. |
| SeasonPass.Season | 1 | World-table season selector. |
| SeasonPass.PointsPerTier | 100 | Points required per tier/renown cycle. |
| SeasonPass.MaxTier | 100 | Normal pass cap. |
| SeasonPass.Points.Quest / Kill / EliteKill / BossKill / RareKill | 10 / 1 / 5 / 100 / 25 | Base point sources. |
| SeasonPass.Points.LevelUp / DailyLogin / PvPKill / DuelWin | 50 / 50 / 10 / 5 | Base point sources. |
| SeasonPass.PvP.VictimCooldown | 300 | Seconds before the same PvP victim can count again. |
| SeasonPass.Streak.BonusPerDay | 5 | Extra daily-login points, capped at 10 added streak steps. |
| SeasonPass.Prestige.Enable | 1 | Only effective when InternalPrestige.Enable is also 1. |
| SeasonPass.InternalPrestige.Enable | 0 | Owns/enables Prestige mode. |
| SeasonPass.InternalParagon.Enable | 0 | Owns/enables Dream Forge effects. |
| SeasonPass.PrestigeMobScaling.Enable | 0 | Enables optional Prestige mob scaling. |
| SeasonPass.Weekend.Enable / PointsPercent / XPPercent | 1 / 200 / 150 | Weekend point and XP multipliers. |
| SeasonPass.LevelChest.Enable / GoldPer10Levels / BagItem | 1 / 50000 / 21841 | Level-chest switch, copper formula base, and mailed bag. |
| SeasonPass.Weekly.Enable | 1 | Base weekly progress/UI. |
| SeasonPass.DungeonObjectives.Enable | 1 | Phase 8 progression-event objectives. |
| SeasonPass.Weekly.RerollEnable | 1 | One weekly Dream Swap. |
| SeasonPass.Runes.Enable / BaseSlots | 1 / 3 | Rune system and starting slots. |
| SeasonPass.Runes.ResonancePct | 2 | Loaded C++ default; bonus per permanent buff rune. |
| SeasonPass.WorldBoss.Enable / IntervalHours / DespawnMinutes / BonusPoints | 1 / 6 / 120 / 250 | Boss rotation and active-boss reward. |
| SeasonPass.WorldBoss.WorldBuffSpell | 22888 | Spell applied to tracked online players after active boss kill; 0 disables. |
| SeasonPass.ZoneEvent.Enable / RotationHours / PointsPercent | 1 / 3 / 200 | Active-zone behavior. |
| SeasonPass.Bounty / DungeonWeek / Discoveries / Achievements.Enable | 1 / 1 / 1 / 1 | Supporting systems. |
| SeasonPass.Chest.Enable | 1 | Chest drops/opening. |
| SeasonPass.Chest.DropChanceKillPct / ElitePct / BossPct | 2 / 10 / 100 | Post-cap/prestige normal-chest drop chances. |
| SeasonPass.Chest.LegendaryFromBossPct | 10 | Loaded but currently unused. |
| SeasonPass.Chest.EpicChanceBasePct | 15 | Loaded but currently unused. |
| SeasonPass.Chest.PityStepPct | 5 | Pity percent per no-Epic chest. |
| SeasonPass.Storm.Enable / PointsPercent | 1 / 300 | Random 15-minute triple-point window. |
| SeasonPass.Legacy.PointsPercentPerPrestige | 2 | Post-Prestige point bonus. |
| SeasonPass.Mutators.Enable | 1 | Weekly mutator selection/effects. |
| SeasonPass.AnnounceTier / AnnounceRareKill | 1 / 1 | Chat announcements. |
| SeasonPass.IgnoreBots / BotAccountPrefixes | 1 / RNDBOT,ADDCLASS | Exclude matching bot accounts. |
| SeasonPass.Prestige.Max | 300 | Loaded C++ default; not present in the distributed template. |
| SeasonPass.Prestige.GoldBase / GoldPerLevel / XPPctPerLevel / AutoGold | 500000 / 100000 / 3 / 100000 | Loaded C++ defaults; Prestige reward, XP, and automatic-mode values. |
| SeasonPass.Paragon.CapPerStat / PointsPerPrestige / MobScalePctPerPrestige | 75 / 2 / 1 | Loaded C++ defaults; Dream Forge cap, earnings, and scaling. |


## 20. Current-state caveats

- Treat SQL plus server C++ as authoritative. `SeasonPassData.lua` is a UI mirror and does not currently contain the 14 Phase 8 objective definitions.
- The chest config names `LegendaryFromBossPct` and `EpicChanceBasePct` imply behavior that the current `OpenChest`/`RollChestLoot` code does not implement.
- The `hardcore` character field, `ACH_HARDCORE` enum value, and UI labels exist, but no active C++ Hardcore flow is currently present.
- Changing a world SQL row affects the server after the relevant database update/config reload; it does not automatically regenerate the Lua mirror.

