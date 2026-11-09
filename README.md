# EsteriaWoW

A self-hosted World of Warcraft 3.3.5a (WotLK, client build `12340`) server built on
AzerothCore with the PlayerBots fork, standard Eluna, Docker Compose and MySQL. Esteria
extends the stock game with dozens of new playable races, a third player faction, a
rebuilt client interface, a classless character system with every Conquest of Azeroth ability and talent, and a stack of progression and quality-of-life modules.

It is the server half of a matched pair. The client half is the
[wowdecomp Esteria fork](https://github.com/STRHercules/wowdecomp), which supplies the
native extensions (64-slot race table, Retail-style appearance, digital inventory) that
this server's packets and data assume.

Most of this is opt-in per module or needs the matching client. Status words follow
[Modules.md](docs/status/Modules.md): **enabled**, **installed**, **staged** (data present, not
validated in game) and **manual** (not a normal CMake module). A feature listed here is
not proof that it passed a live test; each section says what is known.

**Jump to:** [Features](#what-esteria-adds) · [Quick start](#running) · [Repository map](#repository-map) · [Where to look](#where-to-look) · [Status](#status)

| Section | Contents |
| --- | --- |
| [Playable races](#playable-races) | 64-slot race table, registry, server support |
| [Freeborn](#freeborn-a-third-faction) | Third faction |
| [Housing](#housing) | Plots, houses, decor, shops, collections, pets |
| [Client interface](#client-interface-and-customization) | Character select, Glue, inventory, satchel |
| [Gameplay modules](#content-and-gameplay-modules) | Battlemon, Dream Path, Mythic+, Nemesis and more |
| [Admin and tooling](#admin-and-tooling) | GM Tool Chest, launcher API, chat bridge |
| [Core changes](#core-changes) | What needed the core instead of a module |
| [Planned work](#planned-and-design-stage-work) | Design documents, not shipped |
| [Requirements](#requirements) and [Running](#running) | Docker setup, commands, SQL rules |

---

## What Esteria adds

### Playable races

Esteria widens the race table from 10 to 64 slots and ships a registry-driven set of
playable races. The registry is
[`race_registry.json`](modules/mod-custom-server/data/races/race_registry.json). Each row
records faction, start zone, asset owner, and the stock race it borrows for legacy
eligibility masks (there are no free 32-bit mask bits left).

| Family | Race IDs | Notes |
| --- | --- | --- |
| Original ten | 1-8, 10, 11 | Plus 435 skin, 56 face and 220 hair-color additions from the Ascension customization pack |
| Worgoblin baseline | 9 Goblin, 12 Worgen, 13 High Elf | Worgen and Dracthyr use saved alternate forms |
| Custom races | 14/24/27 Broken, 15/62 Sethrak, 25 Forsaken | Broken has its own racial runtime effects |
| Imported player models | 16 Eredar, 17 Nightborne, 18/26 Pandaren, 19 Void Elf, 21 Lightforged, 22 Zandalari, 23 Dark Iron, 28 Dracthyr, 29 Kul Tiran, 30/31 Illidari | |
| Darkfallen | 43 Alliance, 44 Horde | Own identity; shares the high mask bit |
| Retail ports | 20 Vulpera, 45 Mag'har, 46 Highmountain, 47 Mechagnome, 48/49 Earthen, 50/51 Haranir, 52/53 Skyborne | Expanded creator controls for six families |
| Creature and Wrath ports | 54 Naga, 55 Tuskarr, 56/57 Vrykul, 58/59 Forgotten, 60/61 Ogre | Female Vrykul and Alliance Ogre included |
| Newer additions | 63 Gnoll, 64 Saberon, 65 Jinyu, 66 Drakkin, 68 Arakkoa, 69/70 Drakonid, 72 Slime Giant, 73 Centaur, 75 Kyrian, 76 Venthyr | Several are hidden in the creator |
| NPC-only | 32-42, 67, 71, 74 | Reserved so NPC race rows never collide with players |

Server-side support for this lives in:

| Piece | What it does |
| --- | --- |
| `RaceMgr` and `SharedDefines.h` | Bounded race helpers; masks come from `GetRaceMaskForRace`, never an unchecked shift |
| Appearance codecs | `Highmountain`, `Earthen`, `Haranir`, `Vulpera` and `CreatureAppearance` headers validate and carry extra appearance bytes through create, save, enumerate and login |
| Character wire extensions | Extra appearance bytes ride in `HXE1` / `HXE2` roster trailers and `HRC1` create trailers that the client strips before stock parsing |
| `mod-custom-server` racials | Racial spells and cast visuals per race: `race_racials`, `drakkin`, `drakonid`, `darkfallen`, `slime_centaur` and `donor` racials, plus Centaur travel |
| Retail look save and broadcast | Body sliders and the full Retail look are stored per character and sent to nearby players |
| Playable-bot policy | PlayerBots follow the same race, visibility and appearance rules |

The developer handoff in [RaceGuide/](RaceGuide/) covers the pipeline, per-race recipes,
runtime DLLs, server changes and the validation checklist. Start at
[RaceGuide/README.md](RaceGuide/README.md). Race racial design is in
[RACIALS.md](docs/design/RACIALS.md).

### Freeborn: a third faction

`TEAM_FREEBORN` is a persistent third `TeamId`, not an alignment layer on top of
Alliance and Horde. It is specified in
[Freeborn_Third_TeamId_Implementation_Specification.md](docs/design/Freeborn_Third_TeamId_Implementation_Specification.md),
with core hooks, a classless wildcard path and unit tests in
`src/test/server/game/Combat/FreebornTeamTest.cpp`.

### Housing

`mod-esteria-housing` adds player housing with a matching client addon
(`Addons/EsteriaHousing` in wowdecomp). Server rules, SQL order and known limits are in
[modules/mod-esteria-housing/README.md](modules/mod-esteria-housing/README.md). It is off
until `EsteriaHousing.Enable = 1`. All of it is built and running on the Live stack, but
not yet checked in game.

| Feature | What it does |
| --- | --- |
| Houses and plots | Claim a house from the Housing Steward. Each house is its own instance of map 35; group members can visit, only the owner edits. Restyle or move a house, including retail exteriors such as the Grimtide Manse |
| Neighborhoods | Account and guild neighborhoods in Founder's Point, multiple homes, and a first-time map choice per account. Founder's Point and the house interior have world map tiles, loading screens and zone names |
| Growth | Buy more floors, a larger decor budget and a higher room limit with gold. Decor can go outdoors on your plot, with wall and roof spots for towers, dormers and chimneys |
| Decor catalog | Thousands of retail decor pieces with retail names, thumbnails and WMO pieces, placed with scale, height and rotation. Edits are validated server-side and persisted in one transaction |
| Shops and commissions | Player shops with merchants that keep a customizable look, labelled cases, shelves, racks, counters and signs, and commissions. A shop with goods for sale cannot be removed |
| Adventure pieces | Training hall dummies (tank and boss), portals, meeting stones, and Teleport/Portal: Home spells. Decor can be bought outside the house too |
| Collections and display | 16 pieces in a Collections category: achievement and item trophies, mount stalls, paddocks and pedestals, mannequins with saved outfits, a four-tab library (books, exploration, achievements, storylines) and a pet sanctuary with beds, toys and feeding stations. Nothing on display is taken from your collection |

Mounts and pets that move are capped at 12 per house or neighborhood
(`EsteriaHousing.MaxAnimatedDisplays`). The collections checklist is
`docs/housing/collections-checklist.md` in the wowdecomp repository.

### Client interface and customization

| Feature | What it does |
| --- | --- |
| Esteria Character Select (ECS) | Virtualised roster with race portraits, search, drag reorder, notes and a detail tooltip. See [docs/CHARACTER_SELECT.md](docs/CHARACTER_SELECT.md) |
| Retail-style Glue | Login screen, race creator, 64-race buttons and portraits from [UI.md](docs/design/UI.md) and [tools/](tools/) |
| Digital inventory | Carried inventory window with server-side search and pagination, negotiated by an `ESTERIADI` handshake so older cores keep normal bags. See [client-customization/EsteriaInventory/](client-customization/EsteriaInventory/README.md) |
| Grand Satchel | 237-slot bag support. See [client-customization/EsteriaSatchel/](client-customization/EsteriaSatchel/README.md) |
| Native appearance | Hair, skin, geoset, cosmetic wing and material handling in [client-customization/](client-customization/README.md) |
| Barber and creator limits | Race-capacity and archive-capacity patches, with tests under `client-customization/Test*.cpp` |

All barbers still use the legacy combined-value interface. Expanded creator controls do
not imply an expanded barber.

### Content and gameplay modules

| System | Status | Summary |
| --- | --- | --- |
| Battlemon (`mod-battlemon`) | Enabled | Pokemon-style collection, wild encounters, world pet battles, human and bot duels, breeding with a Day Care and eggs, Pokemon trading, held items, following Pokemon, mainline move learning, and zone-aware wild spawns with an admin panel. 980 converted 3D models. See [Battlemon.md](docs/status/Battlemon.md) and [modules/mod-battlemon/README.md](modules/mod-battlemon/README.md) |
| `mod-wxl-dbc` | Enabled | Server DBC continuation files, so large custom tables (Battlemon, Freeborn) load without replacing base DBCs |
| Echoes of the Worldsoul | Staged | Permanent attunement and stat bridge, in `mod-custom-server/src/mod_attunement_plus.cpp` |
| Prestige and Draft | Staged | Character replay, ranks and draft choices through Eluna |
| Dream Path (`mod-seasonpass`) | Staged | Seasonal tiers, weekly goals, chests, Dream Renown. Reward tables are in [Season.md](docs/status/Season.md) |
| Mythic+ (`mod-mythic-plus`) | Staged | Keystones, timers, affixes and rankings |
| Dungeon Master (`mod-dungeon-master`) | Staged | Procedural dungeons with six tiers, nine themes and Roguelike mode |
| Instance ownership | Enabled | `InstanceMode` keeps Mythic+, Dungeon Master and Roguelike scaling from stacking with AutoBalance |
| Nemesis (`mod-nemesis-system`) | Staged | Persistent revenge targets with ranks, affixes and the `NemesisTracker` addon |
| Loyal Steed (`mod-loyal-steed`) | Staged | Persistent companion with saddlebags and fast travel |
| Transmog (`mod-transmog`) | Enabled | Rewritten service, collection UI and protocol bridge |
| Mounts | Staged | About 111 novelty and car mounts, packed by `tools/cars_mount_pack.py` and `mount_pack_batch2.py` |
| Faction-Free (`mod-Faction-Free`) | Manual | Cross-faction player-to-NPC behavior with replacement faction DBCs |
| Fly Anywhere (`mod-fly-anywhere`) | Enabled | Flying in Eastern Kingdoms and Kalimdor, with a matching `AreaTable.dbc` |
| Loot Beam (`mod-loot-beam`) | Installed | Server half of the `wxl-loot-beam` client extension. Writes the best item quality in a corpse's loot into an update field, so the loot beacon is the right colour before the loot window opens |
| Mana Speedflying (`mod-mana-speedflying`) | Installed | Flying mount speed follows how it flies: 220% climbing, 320% level, 600% diving, blended smoothly. Companion to the client's `wxl-mana-speedflying` |
| Mana Loot Pet (`mod-mana-loot-pet`) | Installed | Your vanity companion walks to a fresh solo kill and loots it. Group loot rules and rolls are never bypassed; overflow is mailed |
| Adaptive Auto-Attack (`mod-adaptive-autoattack`) | Installed | Automatically switches between melee and ranged basic attacks, so Auto Shot need not cost an ability pick in Free Pick or Wildcard systems |
| Classless Wildcard (`mod-classless-wildcard`) | Installed | **Esteria is classless.** Character creation offers races only, and every character is a Hero whose abilities and talents come from the whole game, including all of the Conquest of Azeroth abilities and talents. A Hero spends essence currencies on chosen abilities or lets the dice decide. Has a client addon |
| AzerothPlex (`mod-azeroth-plex`) | Installed | Server half of a client extension that plays a Plex stream in a world-space screen and broadcasts it to nearby players over its own TCP port |

The full list, including the stock quality-of-life modules (AH bot, account-wide
achievements and mounts, AOE loot, random enchants, item upgrade, corpse respawn and
others), is in [Modules.md](docs/status/Modules.md) and [ModuleStatus.md](docs/status/ModuleStatus.md).

### Admin and tooling

| Module | What it does |
| --- | --- |
| GM Tool Chest (`mod-esteria-toolchest`) | Addon interface for searching and editing creature and game object templates, spawn data and related rows, with cloning, lookups and applying changes to the running server. `EsteriaToolChest.MinSecurity` sets the lowest account level allowed (default 2) |
| Launcher API (`mod-launcher-api`) | HTTP API for a game launcher: account creation and management, character list and services, a read-only armory and world database, and presence. See [its README](modules/mod-launcher-api/README.md) |
| Chat bridge (`mod-esteria-chat`) | Bridges in-game chat to an external API. Disabled until linked accounts and a private API are configured |

### Core changes

Esteria prefers module hooks. Some things need the core:

| Area | Change |
| --- | --- |
| Eluna | Standard Eluna integrated as core callbacks, with spell and aura hooks and quest-reward prevention |
| Races | 64-slot race handling, legacy-mask aliasing and race/faction compatibility in `Player` and `Unit` |
| Persistence | `extraAppearance BIGINT UNSIGNED` on characters, plus per-character Retail look and slider storage |
| Handlers | `CharacterHandler` create and enumerate extensions, digital inventory packets |
| DBC | `DBCStore` continuation support used by `mod-wxl-dbc` |
| Teams | Third `TeamId` and the code paths that read it |
| Housing | Opcodes `0x537`-`0x53E`, a packet handler and instance picker hook, and `MapInstanced::CreateInstanceForPlayer` asking the picker first. No-ops unless the module sets its hooks |

The exact core delta since the September 2 import is captured in
[RaceGuide/05-SERVER.md](RaceGuide/05-SERVER.md).

### Planned and design-stage work

These are documents, not shipped features:

| Document | Scope |
| --- | --- |
| [ConquestOfEsteria.md](docs/design/ConquestOfEsteria.md) | Audit and transport plan for the Ascension custom classes. The current core still has class IDs 1-11 |
| [ESTERIA_LIVING_WORLD_IMPLEMENTATION.md](docs/design/ESTERIA_LIVING_WORLD_IMPLEMENTATION.md) | Persistent simulation of towns, businesses, crime, trade and government |
| [EsteriaGameplayExpansion.md](docs/design/EsteriaGameplayExpansion.md) | Expanded hunter taming (drake, dragonkin, elemental, undead, mechanical), animal companion, custom Hearthstone |
| [FORSAKEN_TAUNKA.md](docs/design/FORSAKEN_TAUNKA.md), [HALFELVES.md](docs/design/HALFELVES.md) | Race implementation plans |
| [WODMODELS.md](docs/design/WODMODELS.md) | Analysis of Warlords of Draenor character models |
| [IDEAS.md](docs/design/IDEAS.md) | Backlog |

---

## Requirements

- Docker Desktop with Compose.
- A separately obtained 3.3.5a build `12340` client. The repository does not ship or
  redistribute it.
- The matching wowdecomp Esteria client build, for the native race, appearance and
  inventory extensions.
- Blizzard-derived converted assets (MPQs, DBCs, textures) are not in Git. The
  repository stores manifests, generators, tests, SQL and docs.

## Running

Docker Desktop must be running. From the repository root in PowerShell:

```powershell
docker compose up -d
docker compose ps
```

Rebuild after a core or C++ module change:

```powershell
docker compose up -d --build
```

| Service | Purpose |
| --- | --- |
| `ac-database` | MySQL 8.4 and persistent database volume |
| `ac-db-import` | Applies AzerothCore and module database updates |
| `ac-client-data-init` | Initializes the persistent extracted client-data volume |
| `ac-authserver` | Login service |
| `ac-worldserver` | Worldserver, Eluna, PlayerBots and gameplay modules |
| `ac-tools` | Optional client-data extraction profile |

`docker-compose.override.yml` publishes auth (`3724`) and world (`8085`) and keeps
MySQL on loopback (`127.0.0.1:3306`). For remote players, the realm address, firewall
and client `realmlist.wtf` must all use the same reachable host. Do not expose MySQL.

```powershell
docker compose logs --tail 100 ac-worldserver
docker compose restart ac-worldserver ac-authserver
docker compose down
```

`docker compose down` keeps the database volume; `down -v` discards it. Attach to the
worldserver console with `docker attach ac-worldserver` and detach with `Ctrl+P`,
`Ctrl+Q`. Create an administrator interactively:

```text
account create <username> <password>
account set gmlevel <username> 3 -1
```

Never commit or print database or account passwords. More commands are in
`COMMANDS.md` (not yet written).

### SQL rules

Put new local SQL in `data/sql/updates/pending_db_*` or the owning module's database
directory. Do not edit `data/sql/base/`, `data/sql/archive/` or merged
`data/sql/updates/db_*/`. Back up the database before changing live data.

## Repository map

```text
EsteriaWoW/
|-- src/                     AzerothCore core, with Esteria changes
|-- modules/                 55 modules; mod-custom-server holds Esteria's own C++, SQL, race registry
|                            (Eluna scripts are mounted from mod-worgoblin-high-elf/lua_scripts)
|-- data/
|   |-- sql/                 base, merged and pending database updates
|   `-- retroported-races/   per-race manifests used by the packers
|-- conf/                    configuration templates (dist)
|-- env/                     generated runtime config and logs (mostly ignored)
|-- apps/  bin/  deps/       upstream build helpers, scripts and vendored dependencies
|-- docker-compose*.yml      stack definition, local override, Two Forms image pin
|
|-- tools/                   race packers, deploy scripts, UI patchers, tests, loose SQL (tools/sql/)
|-- client-customization/    native client appearance, digital inventory, satchel (sources and tests)
|-- wxl-races-patcher/       character-select DLL source; build-artifacts/ holds stray .obj/.lib
|-- e2e/                     protocol-level live-stack tests
|
|-- RaceGuide/               race and custom-content developer handoff, with evidence and indexes
|-- Harvested/               extracted donor models and race material
|-- exports/                 generated deliverables and packaged race exports
|
|-- docs/
|   |-- design/              specs and plans: races, Freeborn, Living World, classes, taming, UI
|   |-- status/              module inventory, progression, Dream Path, Battlemon status
|   |-- images/              reference screenshots used by the design docs
|   `-- (guides)             character select, retroported races, 100-character support
|-- assets/
|   |-- Arakkoa-race/  SlimeSkeleton/  Vehicles/  CustomModules/
|   |-- archives/            race zips and the patch-Z MPQ copies
|   `-- dbc/                 reference Spell, ItemSet and SpellItemEnchantment DBCs
`-- reference/
    `-- azerothcore-wotlk-coa/   donor class tree used by the Conquest audit
```

### Where to look

| Looking for | Go to |
| --- | --- |
| Which races exist and their IDs | `modules/mod-custom-server/data/races/race_registry.json` |
| How a race is built | [RaceGuide/](RaceGuide/README.md) and `tools/*_race_pack.py` |
| What a module does and whether it is on | [docs/status/Modules.md](docs/status/Modules.md) |
| Progression ownership and acceptance | [docs/status/PROGRESSION.md](docs/status/PROGRESSION.md) |
| A planned feature | [docs/design/](docs/design/) |
| Server SQL to apply | `data/sql/updates/pending_db_*` or a module's `data/sql/` |
| Housing rules, SQL order, tools | [modules/mod-esteria-housing/README.md](modules/mod-esteria-housing/README.md) |
| Client-side addon or native code | `client-customization/`, `modules/*/addon/` |

Local-only folders such as `BinaryWork/`, `DBCs/`, `NewModels/`, `VulperaDBC/` and `var/`
are git-ignored working directories, not part of the repository.

## Status

Server build, database import and worldserver readiness are recorded. Several races,
the creator, the digital inventory and the Vrykul and Ogre ports have been checked in
game by the developer. Live validation of the progression modules, PlayerBots with
every race, restart recovery and multiplayer is not complete. See
[PROGRESSION.md](docs/status/PROGRESSION.md) and [RaceGuide/10-VALIDATION.md](RaceGuide/10-VALIDATION.md).

## License

Server and module licensing follows the repository and each upstream module's license.
AzerothCore is AGPL-licensed; see [LICENSE](LICENSE). World of Warcraft client files,
MPQs, DBCs and extracted data are not distributed here.
