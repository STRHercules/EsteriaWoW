# AzerothCore Custom Server

This repository is a self-hosted World of Warcraft 3.3.5a (WotLK, client
build `12340`) server built on AzerothCore with the PlayerBots fork, standard
Eluna, Docker Compose, MySQL, and a staged custom progression ecosystem.

The progression systems are intended to work together:

```text
Prestige / Draft  ->  Dungeon Master  ->  Mythic+
        \                 |                 /
                 Dream Path
                      |
             Echoes of the Worldsoul
```

This is an active development server. Server build, database import,
worldserver readiness, and static integration checks are recorded; live
client, gameplay, restart-recovery, PlayerBots, and multiplayer validation are
not complete. See [PROGRESSION.md](PROGRESSION.md) for the authoritative phase
record.

## Server foundation

- Core: AzerothCore WotLK 3.3.5a.
- Working branch: `custom-server`.
- Core baseline: `playerbots/azerothcore-wotlk` with the PlayerBots module.
- Scripting: standard Eluna enabled; ALE is not installed.
- Database: MySQL 8.4 with a persistent Docker volume containing the
  `acore_auth`, `acore_characters`, and `acore_world` databases.
- Custom code: `modules/mod-custom-server/`.
- Custom Lua: `lua_scripts/custom/`, bind-mounted into the worldserver by the
  local Compose override.

The repository keeps upstream core changes and server-specific extensions
separate where possible. New custom C++ belongs in `mod-custom-server` when a
module hook is sufficient. The active remotes are preserved in Git; fetch or
merge upstream deliberately rather than rewriting the branch.

## Docker runtime

Docker Desktop must be running. From PowerShell:

```powershell
Set-Location 'R:\Users\Zach\Documents\GitHub\Azeroth'
docker compose up -d
docker compose ps
```

Rebuild after a core or C++ module change:

```powershell
docker compose up -d --build
```

The Compose stack contains:

| Service | Purpose |
| --- | --- |
| `ac-database` | MySQL 8.4 and persistent database volume |
| `ac-db-import` | Applies AzerothCore and module database updates |
| `ac-client-data-init` | Initializes the persistent extracted client-data volume |
| `ac-authserver` | Login/authentication service |
| `ac-worldserver` | Worldserver, Eluna, PlayerBots, and gameplay modules |
| `ac-tools` | Optional client-data extraction profile |

The current `docker-compose.override.yml` exposes the game endpoints and keeps
MySQL loopback-only:

| Endpoint | Binding | Use |
| --- | --- | --- |
| Auth | `0.0.0.0:3724` | Client authentication |
| World | `0.0.0.0:8085` | Realm/game connection |
| MySQL | `127.0.0.1:3306` | Local administration only |
| SOAP | Not published by the local override | Internal server interface |

For remote players, the realm advertisement, Windows firewall, and client
`realmlist.wtf` must all use the same reachable host address. Do not expose
MySQL publicly.

Useful operational commands:

```powershell
docker compose config --quiet
docker compose ps -a
docker compose logs --tail 100 ac-worldserver
docker compose logs --tail 100 ac-authserver
docker compose logs --tail 100 ac-db-import
docker compose restart ac-worldserver ac-authserver
docker compose down
```

`docker compose down` preserves the database volume. Use
`docker compose down -v` only when intentionally discarding local server and
client-data volumes.

Attach to the worldserver console with `docker attach ac-worldserver`. Detach
without stopping it with `Ctrl+P`, then `Ctrl+Q`; do not use `Ctrl+C` merely to
detach.

Create an administrator interactively with private values:

```text
account create <username> <password>
account set gmlevel <username> 3 -1
```

Never commit or print database/account passwords. More commands are in
[COMMANDS.md](COMMANDS.md), and the Docker/server boundaries are summarized in
[CUSTOM_SERVER.md](CUSTOM_SERVER.md).

## Installed modules and systems

### Core, solo play, and progression support

| Module | Role | Effective state |
| --- | --- | --- |
| `mod-playerbots` | PlayerBots fork/module; random bots, altbots, and party support | Enabled; random-bot autologin is configured |
| `mod-autobalance` | Scales normal instance content for small groups | Enabled; special-mode ownership guards are installed |
| `mod-solo-lfg` | Solo/low-population dungeon queue support | Enabled |
| `mod-individual-xp` | Per-character XP rates | Enabled; default `1x`, maximum `10x` |
| `mod-individual-progression` | Individual raid, spell, PvP, and content progression | Enabled |
| `mod-challenge-modes` | Optional character challenge rules | Enabled; it is not an enemy-stat scaler |
| `mod-dungeon-clear` | PlayerBots dungeon-clearing support | Installed; PlayerBots integration enabled |

### Account, economy, social, and utility modules

The installed baseline also includes:

`mod-ah-bot` (AH Bot Plus), `mod-transmog`, `mod-account-achievements`,
`mod-account-mounts`, `mod-improved-bank` (account-wide storage),
`mod-world-chat`, `mod-better-item-reloading`,
`mod-aoe-loot`, `mod-npc-services` (repair, bank, mailbox),
`mod-instance-reset`, `mod-anticheat`, `mod-npc-beastmaster`,
`mod-random-enchants`, `mod-item-upgrade`, `mod-congrats-on-level`,
`mod-no-hearthstone-cooldown`, `mod-fly-anywhere`,
`mod-starter-guild`, and
`mod-guildhouse`.

`mod-custom-server` is the local extension module for the Echoes stat bridge,
instance-mode ownership, and progression-event bridge. `mod-chat-transmitter`
is installed but disabled pending external bot/database setup. `mod-premium`,
`mod-reward-shop`, and `mod-reward-played-time` are installed but intentionally
disabled.

Additional server content includes the Eluna/Lua BMAH script with NPC
template `2069430` and four seeded auctions. The BMAH NPC is not spawned into
the world automatically. `mod-guildhouse` uses NPC entry `500030` and also
requires an explicit spawn.

### Races and client-dependent content

- `mod-arac` is installed with server/core/database integration; its required
  client MPQ/DBC and signature handling still need live validation.
- `mod-worgoblin` is installed from `Medviten/mod-worgoblin-high-elf` and adds
  Mag'har Orc, Goblin, Worgen, and High Elf content. Its client readiness is
  also conditional.
- The standalone ignored `mod-attunement-plus` source is not part of the
  active runtime image; it was excluded from recent builds because it still
  calls the removed `Player::ApplyStatBuffMod` API.

### Unified progression ecosystem

| System | Server-side pieces | Current boundary |
| --- | --- | --- |
| Echoes of the Worldsoul | Custom C++ stat bridge, 20 Eluna scripts, character/world SQL | SQL/Lua/C++ and client assets staged; gameplay unverified |
| Prestige and Draft | Six Eluna scripts, character/world SQL, server DBCs | Staged; Standard/Draft behavior, mail, and spell learning unverified |
| Dream Path (`mod-seasonpass`) | C++ module, SQL, weekly rotation, Dream Renown, `SeasonPassUI` | Configured/staged; live load and gameplay unverified |
| Mythic+ (`mod-mythic-plus`) | C++ module, config, keystone/affix/reward SQL, NPC `200005` | Built and imported; keystones, timers, rewards, and leaderboards unverified |
| Dungeon Master (`mod-dungeon-master`) | C++ module, config, run/stat SQL, NPC `500000` | Built and imported; early-development gameplay unverified |
| Phase 7/8 integration | `mod-custom-server` instance ownership and progression-event bridge | Static contracts pass; live dungeon and duplicate-credit checks remain |

The ownership boundary is deliberate:

- Prestige/Draft owns character replay, Prestige rank, and Draft choices.
- Dungeon Master owns procedural and Roguelike runs.
- Mythic+ owns keystones, timed runs, affixes, and rankings.
- Dream Path owns seasonal points, weekly goals, rotations, runes, chests, and
  Dream Renown.
- Echoes owns permanent attunement and Worldsoul progression.
- Phase 7 prevents Mythic+, Dungeon Master, and Roguelike scaling from stacking
  with AutoBalance, Challenge Modes, or Echoes World Threat behavior.
- Phase 8 sends guarded dungeon lifecycle events to Dream Path and persists
  per-character event claims, so duplicate callbacks do not grant duplicate
  seasonal rewards.

## Configuration

Configuration is database/admin configurable through the normal AzerothCore
configuration and SQL paths. The source defaults are in `conf/dist/` and each
module's `conf/` directory. The effective Docker-mounted files are under the
ignored generated path `env/dist/etc/`:

| Location | Responsibility |
| --- | --- |
| `conf/dist/worldserver.conf.dist` | Core worldserver defaults |
| `env/dist/etc/worldserver.conf` | Active worldserver configuration |
| `modules/*/conf/*.conf.dist` | Versioned module defaults |
| `env/dist/etc/modules/*.conf` | Active module configuration |
| `lua_scripts/custom/` | Custom Eluna scripts loaded by the worldserver |
| `modules/*/data/sql/` | Module-owned database updates |
| `data/sql/updates/pending_db_characters/` and `pending_db_world/` | In-flight local updates |

Important effective settings include:

| Area | Current values |
| --- | --- |
| Eluna | `Eluna.Enabled = 1` |
| PlayerBots | Enabled; random-bot autologin; `300-500` random bots; bots wait for a real player; up to `40` added bots |
| AutoBalance | Global and normal/heroic instance families enabled; minimum players `1`; no static per-instance exclusions |
| Challenge Modes | `ChallengeModes.Enable = 1` |
| Individual XP | Enabled; default `1x`; maximum `10x` |
| Dream Path | `SeasonPass.Enable = 1`, season `1`, max tier `100`, weekly goals/runes/chests/events enabled, `IgnoreBots = 1` |
| Dream Path ownership | `SeasonPass.InternalPrestige.Enable = 0`, `InternalParagon.Enable = 0`, `PrestigeMobScaling.Enable = 0` |
| Mythic+ | Enabled; death penalty `15` seconds; keystone purchase cooldown `1440` minutes; completion keystone drop enabled |
| Dungeon Master | Enabled; NPC `500000`; six tiers; level band `3`; solo multiplier `0.5`; Roguelike enabled; time limit disabled; maximum `20` concurrent runs |
| Chat Transmitter | Installed but disabled until external bot/database setup is approved |

`mod-seasonpass` also exposes its own post-cap season-pass prestige toggle;
that is distinct from the disabled internal Prestige/Paragon/mob-scaling gates
above. Do not add another permanent Prestige or Paragon owner without updating
the ownership rules in [PROGRESSION.md](PROGRESSION.md).

Most module configuration changes require a worldserver restart. Mythic+
explicitly treats its enable switch as non-hot-reloadable. Use the module's
native reload command only where its configuration documents support it.

### SQL rules

The database importer applies AzerothCore and module SQL during startup. Before
changing live data, take a database backup outside the repository. Keep new
local update SQL in `data/sql/updates/pending_db_*` or the owning module's
database directory.

Do not edit `data/sql/base/`, `data/sql/archive/`, or merged
`data/sql/updates/db_*/` files. Do not put credentials in SQL, scripts, or
documentation.

## Client package

Use a separately obtained WoW 3.3.5a build `12340`. The server does not ship
or redistribute the copyrighted client.

The current working client is:

```text
R:\Users\Zach\Downloads\World.of.Warcraft.3.3.5a.Truewow\
```

Set the locale-specific `Data/<locale>/realmlist.wtf` to the server address.
For a local client, the usual value is:

```text
set realmlist 127.0.0.1
```

The client currently contains these patch files:

| File | Purpose/status | SHA-256 |
| --- | --- | --- |
| `Data\Patch-A.MPQ` | Pre-existing external client patch; provenance and compatibility are not managed by this repository | Not recorded |
| `Data\patch-enUS-M.MPQ` | Pre-existing external client patch; preserve when assembling a clean pack | Not recorded |
| `Data\Patch-O.mpq` | Fly Anywhere client patch paired with the patched server `AreaTable.dbc` | Not recorded |
| `Data\patch-P.mpq` | Prestige/Draft client content | `e4454b83aaae2600a824dd51bf04481d8ea66d86d94d5ca96f9b6378d35437af` |
| `Data\patch-W.mpq` | Echoes custom item/client content | `93d2d7cc27f77fcd143a30b81a6e69e5b1147b8fedc8d62d5377f925a96ba05a` |

Staged addons under `Interface\AddOns` are:

- `EchoesOfTheWorldsoulBridge`
- `PrestigeSystem`
- `SeasonPassUI`

The persistent server client-data volume also contains the staged server-side
DBC changes for Fly Anywhere (`AreaTable.dbc`) and Prestige/Draft
(`CharBaseInfo.dbc` and `CharTitles.dbc`). Echoes custom item definitions
`900010` and `900011` are included in its staged Item.dbc/MPQ path.

Do not treat the current client as a clean unified distribution. ARAC/Worgoblin
client data, patch ordering, signatures, and a conflict-free merged DBC/MPQ
pack remain Phase 12 work.

## Verification status

The current evidence is intentionally split between server installation and
player-facing validation:

- Phases 1-4: source, SQL, Lua, configuration, DBC, and addon staging is
  recorded; live progression behavior remains open.
- Phase 5: Mythic+ was rebuilt, configured, imported, initialized, and given a
  staged NPC `200005`; interactive Keystone and dungeon checks remain open.
- Phase 6: Dungeon Master was rebuilt, configured, imported, and initialized;
  runtime logs found six difficulties, nine themes, 45 dungeons, and five
  Roguelike affixes; interactive runs remain open.
- Phase 7: per-instance scaling ownership and conflict guards are statically
  verified.
- Phase 8: dungeon event producers, Dream Path consumption, weekly rotation
  filters, persistent claims, and duplicate-credit guards are statically
  verified.
- `git diff --check` and the focused phase contracts pass in the recorded
  staging work. Full repository style checks still report pre-existing issues,
  and no live client/gameplay/auth/multiplayer smoke has been completed for
  the progression ecosystem.

The remaining acceptance work is listed in the unchecked sections of
[PROGRESSION.md](PROGRESSION.md), especially live Prestige/Draft,
attunement, Dream Path objectives, Mythic+, Dungeon Master/Roguelike runs,
PlayerBots, restart recovery, and the unified client pack.

## Repository guide

- [COMMANDS.md](COMMANDS.md) — PowerShell, Docker, database, console, and
  account operations.
- [CUSTOM_SERVER.md](CUSTOM_SERVER.md) — server architecture and custom-module
  boundaries.
- [TASK.md](TASK.md) — installed, deferred, and candidate module status.
- [PROGRESSION.md](PROGRESSION.md) — progression ownership, phase records, and
  acceptance matrix.
- `modules/mod-custom-server/` — local C++ bridge and custom SQL.
- `lua_scripts/custom/` — local Eluna scripts and integration probes.

## License and client boundary

Server and module licensing follows the repository and each upstream module's
license files. AzerothCore is AGPL-licensed; see [LICENSE](LICENSE) and the
individual module `LICENSE` files. World of Warcraft client files, MPQs, DBCs,
and extracted data are not distributed by this repository.
