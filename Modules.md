# Esteria Modules and Modifications

Inventory date: 2026-09-08.

This document describes the current Esteria checkout, generated module
configuration, staged server data, and repository client stages. It separates
source-installed, configured, staged, and live-verified states. A module being
present here does not prove that the current worldserver binary was rebuilt or
that the feature passed an in-game test.

## Status meanings

- **Enabled** — The module is present and its generated configuration enables it,
  or it is integrated custom code without a separate switch.
- **Installed** — Source, SQL, or package content is present, but activation
  depends on a switch, spawn, manual deployment, or unresolved integration.
- **Disabled** — The module is present, but its generated configuration disables
  it.
- **Staged** — Client files, DBCs, SQL, or addons are present for deployment;
  client or gameplay validation is still separate.
- **Manual** — The package is not a normal CMake module and requires explicit
  core, database, Lua, DBC, or MPQ installation.

## Server foundation

- AzerothCore WotLK 3.3.5a, client build `12340`.
- `playerbots/Playerbot` is the core baseline.
- Standard Eluna is enabled; ALE is not installed.
- Docker Compose provides MySQL, database import, authserver, worldserver,
  and client-data initialization.
- The local Compose override bind-mounts
  `modules/mod-playerbots` and
  `modules/mod-worgoblin-high-elf/lua_scripts` into the worldserver.
- `modules/` currently contains 44 module directories. 43 have a `src/`
  directory and are candidates for automatic CMake module discovery. The
  exception is `mod-Faction-Free`, which is a manual replacement package.
- The generated `build/` directory is not a current runtime proof: its module
  cache predates some working-tree additions and no current
  `build/bin/worldserver.exe` was present during this inventory.

## Installed server modules

### Core, solo play, and progression

- `mod-playerbots` — **Enabled**. Player-like bots, random bots, altbots,
  party support, bot commands, and bot AI. The generated configuration enables
  PlayerBots.
- `mod-autobalance` — **Enabled**. Scales instance creatures for small groups.
  Global and normal/heroic instance families are enabled. Special-mode
  ownership guards live in `mod-custom-server`.
- `mod-solo-lfg` — **Enabled**. Solo and low-population dungeon queue support.
  `SoloLFG.Enable = 1`.
- `mod-individual-xp` — **Enabled**. Per-character XP rates. Current documented
  defaults are `1x`, with a maximum of `10x`.
- `mod-individual-progression` — **Enabled**. Per-character expansion, raid,
  spell, PvP, item, and content progression.
- `mod-challenge-modes` — **Enabled**. Character challenge rules such as
  Hardcore, Iron Man, slow XP, self-crafted items, and item-quality constraints.
  It is not the server's general enemy-stat scaler.
- `mod-dungeon-clear` — **Installed**. PlayerBots dungeon-clearing support with
  PlayerBots integration and a module configuration. Interactive clearing is
  unverified.
- `mod-dungeon-master` — **Enabled / staged**. Procedural dungeon runs with six
  configured difficulty tiers, nine themes, level scaling, rewards, leaderboards,
  and Roguelike mode. NPC entry `500000`. Early-development gameplay remains
  unverified.
- `mod-mythic-plus` — **Enabled / staged**. Keystone dungeons, timers, affixes,
  rewards, dungeon snapshots, and rankings. NPC entry `200005`; interactive runs
  and rewards remain unverified.
- `mod-seasonpass` — **Enabled / staged**. Dream Path seasonal progression,
  points, weekly goals, runes, chests, discoveries, mutators, world events,
  Dream Renown, and the `SeasonPassUI` addon. Season `1`, maximum tier `100`.
- `mod-custom-server` — **Enabled / integrated**. Local Esteria C++ bridge. Owns
  instance-mode claims, the Echoes stat/attunement bridge, guarded dungeon
  progression events, custom race data, and server-specific SQL.

### Account, economy, social, and quality of life

- `mod-account-achievements` — **Enabled**. Shares achievement progress across
  characters on an account.
- `mod-account-mounts` — **Enabled**. Shares learned mounts across an account.
  `Account.Mounts.Enable = 1`.
- `mod-ah-bot` — **Enabled**. Auction House seller and buyer bot behavior.
- `mod-anticheat` — **Enabled**. Passive anti-cheat tracking and GM commands.
  `Anticheat.Enabled = 1`; GM accounts are excluded by configuration.
- `mod-aoe-loot` — **Enabled**. Collects loot from nearby corpses through one
  loot action. `AOELoot.Enable = 1`; group-loot behavior still needs live testing.
- `mod-better-item-reloading` — **Enabled**. Improves server-side item reloads
  and client-side refreshes where the client allows it.
- `mod-corpse-respawn` — **Enabled**. Releases a player's ghost at the corpse
  instead of immediately sending it to the graveyard, with a graveyard marker.
- `mod-congrats-on-level` — **Disabled**. Level milestone rewards for gold,
  spells, or items. Both `Congrats.Enable` and `CongratsPerLevel.Enable` are `0`.
- `mod-improved-bank` — **Enabled**. Account-wide bank/storage behavior. It also
  supplies storage used by Loyal Steed saddlebags.
- `mod-instance-reset` — **Enabled**. Instance reset utilities.
  `instanceReset.Enable = true`.
- `mod-item-upgrade` — **Enabled**. Item upgrade ranks and crafting upgrades.
  Current documented configuration caps rank at `2`.
- `mod-learn-spells` — **Enabled**. Automatically teaches configured spells as
  characters level. `LearnSpells.Enable = 1`.
- `mod-loyal-steed` — **Enabled / staged**. Race-specific persistent companion
  with follow, mount, camp, saddlebag storage, appearance, and up to 20
  continental fast-travel locations. Its client files are not confirmed in the
  current developer client.
- `mod-no-hearthstone-cooldown` — **Enabled**. Removes the normal Hearthstone
  cooldown.
- `mod-no-profession-limit` — **Enabled**. Raises the primary-profession cap to
  11 in the current config. Optional account-wide replication is disabled.
- `mod-npc-beastmaster` — **Enabled**. Beastmaster NPC services for taming
  beasts. `BeastMaster.Enable = 1`.
- `mod-npc-services` — **Enabled / integrated**. NPC repair, bank, and mailbox
  services. It has no separate master switch in the generated module directory.
- `mod-profession-experience` — **Enabled**. Profession experience from
  gathering and crafting. Lockpicking experience is disabled.
- `mod-random-enchants` — **Enabled**. Random enchantment rolls for configured
  loot, quest rewards, and group rolls. Crafting randomization is disabled.
- `mod-reward-played-time` — **Disabled**. Played-time reward system.
  `RewardSystemEnable = 0`.
- `mod-reward-shop` — **Disabled**. In-game reward shop. `RewardShopEnable = 0`.
- `mod-starter-guild` — **Enabled**. Assigns new characters to faction-specific
  starter guilds: Alliance `Immortal` (21), Horde `Eternal` (22).
- `mod-transmog` — **Enabled / working-tree rewrite**. Transmog service and
  collection UI with custom server code, SQL, protocol bridge, and matching
  client addons.
- `mod-world-chat` — **Enabled**. Global world chat. `WorldChat.Enable = true`.

### Races, factions, and custom-world systems

- `mod-worgoblin-high-elf` — **Enabled / client-dependent**. Adds Goblin,
  Worgen, High Elf, and related race data, starting data, models, SQL/DBC
  content, PlayerBots compatibility, and Lua. The Worgoblin Lua directory is
  mounted by Compose. Full race creation and login still require unified client
  assets and live testing.
- `mod-custom-server/data/races/race_registry.json` is the broader Esteria
  race contract. It currently describes playable IDs through `28`, including
  Goblin (`9`), Worgen (`12`), High Elf (`13`), Broken (`14`, `24`, `27`),
  Sethrak (`15`), and the additional imported race rows. This registry is
  source/configuration state, not proof that every row is selectable in the
  current client.
- `mod-attunement-plus` — **Installed / superseded**. Legacy standalone Echoes
  stat-application source. Its old stat APIs are incompatible with the current
  core path; the maintained implementation is in `mod-custom-server`.
- `mod-nemesis-system` — **Enabled / staged**. Persistent open-world revenge
  targets with rank scaling, affixes, rewards, decay, GM commands, character
  storage, monthly statistics, and the `NemesisTracker` addon.
  `NemesisSystem.Enable = 1`; the addon bridge is unverified.
- `mod-Faction-Free` — **Manual / staged**. Cross-faction player-to-NPC
  behavior, faction/achievement DBC replacements, world SQL, teleport Lua, and
  `Patch-F.mpq`. It has no `src/` directory, so it is not a normal CMake module.
- `mod-fly-anywhere` — **Enabled / client-dependent**. Allows flying in Eastern
  Kingdoms and Kalimdor. The module supplies `AreaTable.dbc` and `Patch-O.mpq`,
  but the patch is not in the current `3.3.5a - Dev\Data` listing.
- `mod-guildhouse` — **Installed**. Guildhouse content with NPC entry `500030`.
  It has no enable switch and does not automatically spawn the NPC.
- `mod-skip-dk-starting-area` — **Enabled**. Death Knight starting-area skip
  and optional cleanup settings.
- `mod-premium` — **Disabled**. Premium account features are present but the
  current configuration has `PremiumAccount = 0`.
- `mod-chat-transmitter` — **Disabled**. Worldserver-to-external-bot/WebSocket
  and Discord bridge. `ChatTransmitter.Enabled = 0` pending external setup.

## Custom server modifications

These are server changes that are broader than a single upstream module:

- `mod-custom-server/src/InstanceMode.*` provides mutually exclusive
  `Normal`, `MythicPlus`, `DungeonMaster`, and `Roguelike` instance ownership.
- `mod-custom-server/src/progression_events.*` publishes guarded dungeon
  lifecycle events to Dream Path and prevents duplicate seasonal credits.
- The local attunement implementation in
  `mod-custom-server/src/mod_attunement_plus.cpp` applies Echoes-derived
  stats through the current `HandleStatFlatModifier` path.
- `mod-custom-server/data/races/race_registry.json` and its SQL/DBC updates
  define the current custom-race/start-data contract.
- `mod-custom-server/data/sql/` contains custom auth, character, world,
  race, instance, BMAH, and Worldsoul progression data.
- The working tree currently contains additional core edits in
  `src/server/game/Entities/Player/Player.cpp`,
  `src/server/game/Entities/Player/PlayerUpdates.cpp`,
  `src/server/game/Entities/Unit/Unit.cpp`, and
  `src/server/shared/SharedDefines.h`. These cover race/faction compatibility,
  collision-dimension safety, and current stat/race integration seams, but
  remain working-tree changes rather than freshly rebuilt runtime evidence.
- `data/sql/updates/` and `data/sql/updates/pending_db_world/` contain the
  current local database migrations. Do not treat pending or working-tree SQL
  as proof that a live database has applied it.

## Client modifications and staged assets

The repository does not distribute the copyrighted WoW client. It contains
client stages and module-provided assets that must be assembled into a clean,
signature-compatible 3.3.5a build `12340`.

### Repository client stages

`3.3.5a - Dev` is the most complete repository client stage inspected here.
Its custom addon directories are:

- `Ace3` — shared addon libraries.
- `NemesisTracker` — Nemesis target list, map markers, server/addon protocol,
  and cached tracking data.
- `SeasonPassUI` — Dream Path HUD, seasonal progress, rewards, chests,
  weekly goals, and bilingual UI.
- `Transmog` — transmog service UI.
- `TransmogCollection` — account/character collection UI.

It also contains Blizzard UI folders and the following patch files under
`3.3.5a - Dev\Data`:

- `patch.MPQ`, `patch-2.MPQ`, `patch-3.MPQ` — Base or pre-existing client
  stage files; feature ownership is not assigned in this inventory.
- `PATCH-A.MPQ` — Existing combined/custom patch stage. Its exact merged
  provenance is not treated as verified. It is the staged patch that carries
  the custom race Glue/UI and race assets described below.
- `Patch-B.MPQ` — Existing small patch stage; feature ownership is not
  independently verified.
- `Patch-C.MPQ` — Existing custom patch stage; feature ownership is not
  independently verified.
- `Patch-F.MPQ` — Faction-Free client patch staged in the developer client;
  matching server-side manual integration remains unverified.
- `Patch-Housing.MPQ\` — Housing patch source directory, not a verified final
  MPQ deployment.

The alternate `3.3.5a` repository client stage contains `SeasonPassUI` and a
smaller patch set. It should not be treated as a clean merge with
`3.3.5a - Dev`.

### Module-provided client assets

- **Fly Anywhere** — `modules/mod-fly-anywhere/data/patch/client/Patch-O.mpq`
  and server `AreaTable.dbc`. Supplied in the module, but not in the current
  developer client listing.
- **Worgoblin / High Elf** — `data/patch-A.MPQ`, DBCs, GlueXML, race models,
  and signature-sensitive client data under `mod-worgoblin-high-elf`. Supplied
  and staged; Docker excludes the large patch source, and client creation/login
  remain open.
- **Faction-Free** — `Patch-F.mpq`, `Faction.dbc`, `FactionTemplate.dbc`, and
  `Achievement.dbc` under `mod-Faction-Free`. The patch is in the developer
  client, but server-side integration is not confirmed.
- **Loyal Steed** — `Spell.dbc` and `patch-LoyalSteed.mpq` under
  `mod-loyal-steed`. Supplied by the module; not confirmed in a client install.
- **Nemesis** — `mod-nemesis-system/ClientAddon/NemesisTracker`. Copied into
  the developer client stage; in-client bridge behavior is unverified.
- **Dream Path** — `mod-seasonpass/SeasonPassUI` and the developer-client
  `SeasonPassUI` addon. Staged; server/client gameplay remains unverified.
- **Transmog** — `mod-transmog/addon` and developer-client `Transmog`/
  `TransmogCollection`. Custom addon stage is present; in-client runtime is
  unverified.

### Custom race, Glue UI, and native client extension

The custom race path is more than a server module. It is a coordinated client
contract:

- `modules/mod-worgoblin-high-elf/data/patch-A.MPQ/` contains the custom race
  DBCs, models, textures, Glue assets, and GlueXML. Its
  `Interface/GlueXML/GlueParent.lua` routes the login, character-select, and
  character-creation screens and supplies custom backgrounds/lighting for the
  added race names. `CharacterCreate.lua`, `CharacterCreate.xml`, and
  `GlueStrings.lua` provide the race buttons, presentation data, and race/
  ability text. `patch-Asource-20260904/` is the corresponding unpacked patch
  source. The active developer client stores the assembled version as
  `3.3.5a - Dev/Data/PATCH-A.MPQ`; its top-level `Interface` directory was
  empty during this inventory, so the MPQ is the relevant client stage.
- The Esteria client foundation modified the executable/client boundary to
  load a project-owned `Client.dll` beside the executable. The DLL version-
  locks against the Esteria host marker and registers the native Glue function
  `GetAvailableRaceIDs()`; the function exposes the Esteria race IDs to Glue
  Lua so the UI can use actual IDs instead of assuming UI position equals race
  ID. The foundation preserves the `WarcraftXL.dll` import/wildcard-MPQ path
  and allows modified `Interface/GlueXML/FrameXML` content.
- The current documented foundation artifacts are
  `BinaryWork/Esteria_Client_Foundation_v4_WarcraftXL/Wow.exe`, its
  `manifest.json` and `Client.dll`, plus `3.3.5a - Dev/Client.dll` and
  `3.3.5a - Dev/WarcraftXL.dll`. The v4 foundation has a native capacity of
  `32` race slots and exposes IDs `1-27`;
  the client manifest labels ID `14` as Mag'har while the server registry
  currently labels ID `14` as Broken. That ID contract must be reconciled
  before claiming the affected race is live-ready.
- The limits are currently different at each layer: the native foundation is
  `32` slots, its manifest exposes `1-27`, the server registry reaches `28`,
  and the Worgoblin character-creation Glue still declares `MAX_RACES = 15`.
  This means the client was extended beyond the stock race limit, but the
  existing 15-slot creator is not yet a complete UI for every registry row.
- The optional Worgoblin `patch-J.MPQ` includes an alternate
  `CharacterCreate.xml` that can hide extra races. It is an override/rollback
  path, not evidence that the full custom-race creator is active.

`BinaryWork/` contains patch inspection/backup material rather than a
verified active client installation. `CustomModules/` contains additional
procedural-item and item-generator assets, but it is excluded from the Docker
build context and is not counted as active server/client content here.

The documented external client path
`R:\Users\Zach\Downloads\World.of.Warcraft.3.3.5a.Truewow\` currently exists
but was empty of `Data` and `Interface` contents during this inventory. No
populated external client could therefore be confirmed from the checkout.

## Configuration and verification boundary

- Versioned defaults live under `conf/dist/` and each module's `conf/`
  directory.
- The effective generated configuration is under
  `env/dist/etc/modules/` and `env/dist/etc/worldserver.conf`.
- Module SQL is owned by the module or by `mod-custom-server`; local pending
  migrations are separate from already-merged AzerothCore updates.
- Static source, configuration, SQL, DBC, addon, and MPQ presence is recorded
  here. It does not replace a CMake configure, a fresh server build, database
  import, worldserver startup check, client launch, character creation, or
  gameplay smoke test.
- The current open validation areas are custom-race client creation/login,
  Echoes attunement, Dream Path rewards, Mythic+ runs, Dungeon Master and
  Roguelike runs, Nemesis addon transport, Loyal Steed client spell display,
  Transmog UI, PlayerBots behavior, restart recovery, and multiplayer behavior.

Related records:

- [ModuleStatus.md](ModuleStatus.md) — shorter status table.
- [README.md](README.md) — server/runtime and client-package overview.
- [PROGRESSION.md](PROGRESSION.md) — progression ownership and acceptance
  matrix.
- [CUSTOM_SERVER.md](CUSTOM_SERVER.md) — custom-server architecture and
  operations.
