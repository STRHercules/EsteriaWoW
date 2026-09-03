# Module status

`Installed` means the module or system is present in the checkout and included in the current server setup. `Enabled` means it is configured for runtime. Live gameplay, client, addon, Discord, and multiplayer smoke tests remain separate gates.

The checkout uses the `playerbots/Playerbot` fork with standard Eluna active; ALE is not installed. The working client is `R:\Users\Zach\Downloads\World.of.Warcraft.3.3.5a.Truewow\`. It currently contains the pre-existing `Patch-A.MPQ`, `patch-enUS-M.MPQ`, and `Patch-O.mpq`, plus the staged progression patches `patch-P.mpq` and `Patch-Z.mpq`. The staged client addons are `EchoesOfTheWorldsoulBridge`, `PrestigeSystem`, and `SeasonPassUI`.

# INSTALLED

| Module | Current state / notes | Reference |
| --- | --- | --- |
| **mod-playerbots** | Enabled; PlayerBots fork/core baseline | — |
| **mod-autobalance** | Enabled | ([GitHub][4]) |
| **mod-ah-bot (AH Bot Plus)** | Enabled | ([GitHub][6]) |
| **mod-transmog** | Enabled | ([GitHub][3]) |
| **mod-solo-lfg** | Enabled | ([GitHub][16]) |
| **mod-individual-xp** | Enabled | ([GitHub][13]) |
| **mod-account-achievements** | Enabled | ([GitHub][10]) |
| **mod-improved-bank** | Enabled; account-wide storage enabled | ([GitHub][18]) |
| **mod-junk-to-gold** | Enabled | ([GitHub][19]) |
| **mod-world-chat** | Enabled | ([GitHub][29]) |
| **mod-better-item-reloading** | Enabled | ([GitHub][57]) |
| **mod-custom-server** | Enabled; local C++ module containing the Echoes stat bridge, per-instance scaling ownership, and Phase 8 progression-event bridge | — |
| **Echoes of the Worldsoul** | Installed/staged; C++ bridge, 20 standard Eluna scripts, SQL, `Patch-Z.mpq`, and `EchoesOfTheWorldsoulBridge`; gameplay unverified | ([GitHub][48]) |
| **Prestige-and-Draft-Mode** | Installed/staged; six Eluna scripts, SQL, server DBCs, `patch-P.mpq`, and `PrestigeSystem`; Standard/Draft gameplay unverified | ([GitHub][45]) |
| **mod-seasonpass (Dream Path)** | Enabled/staged; C++/SQL/`SeasonPassUI`, Dream Renown, weekly rotation, and dungeon-event consumer; internal Prestige, Paragon, and mob scaling disabled; gameplay unverified | ([GitHub][46]) |
| **mod-mythic-plus** | Enabled; C++/config/SQL applied and NPC `200005` staged; Keystone, timer, affix, reward, and leaderboard gameplay unverified | ([GitHub][36]) |
| **mod-dungeon-master** | Enabled; C++/config/SQL applied, NPC `500000` initialized, six difficulties, nine themes, and 45 dungeons loaded; early development and gameplay unverified | ([GitHub][37]) |
| **BMAH (Black Market Auction House)** | Enabled; Eluna/Lua script, NPC template `2069430`, and 4 seeded auctions; no world spawn | ([GitHub][44]) |
| **mod-arac** | Installed; server/core/DB integration complete; client MPQ/DBC patch remains for live client use | ([GitHub][51]) |
| **mod-worgoblin** | Installed; Mag'har Orc, Goblin, Worgen and High Elf Added | ([GitHub][52]) |
| **mod-aoe-loot** | Enabled; group-loot behavior still needs live testing | ([GitHub][8]) |
| **mod-npc-services** | Enabled; repair, bank, and mailbox only | ([GitHub][20]) |
| **mod-instance-reset** | Enabled | ([GitHub][23]) |
| **mod-anticheat** | Enabled | ([GitHub][55]) |
| **mod-npc-beastmaster** | Enabled | ([GitHub][53]) |
| **mod-account-mounts** | Enabled | ([GitHub][11]) |
| **mod-challenge-modes** | Enabled | ([GitHub][9]) |
| **mod-individual-progression** | Enabled | ([GitHub][2]) |
| **mod-random-enchants** | Enabled for loot, quest rewards, and group rolls at 20%/5%/1%; crafting disabled | ([GitHub][35]) |
| **mod-item-upgrade** | Enabled; rank 2 maximum, crafting upgrades enabled, 1,000 gold per weapon damage/speed rank | ([GitHub][38]) |
| **mod-dungeon-clear** | Installed; PlayerBots integration enabled | ([GitHub][50]) |
| **mod-congrats-on-level** | Enabled; milestone gold rewards at levels 10, 20, 30, 40, 50, 60, 70, and 80 | ([GitHub][39]) |
| **mod-no-hearthstone-cooldown** | Enabled | ([GitHub][25]) |
| **mod-fly-anywhere** | Enabled; patched server `AreaTable.dbc` and client `Patch-O.mpq` | ([GitHub][26]) |
| **mod-skip-dk-starting-area** | Enabled | ([GitHub][27]) |
| **mod-learn-spells** | Enabled | ([GitHub][28]) |
| **mod-starter-guild** | Enabled; Alliance guild 21 (`Immortal`) and Horde guild 22 (`Eternal`) | ([GitHub][21]) |
| **mod-guildhouse** | Installed; no enable switch; NPC entry `500030` is not spawned automatically | ([GitHub][22]) |
| **mod-chat-transmitter** | Installed; intentionally deferred pending external setup | ([GitHub][56]) |
| **mod-premium** | Installed; intentionally disabled | ([GitHub][42]) |
| **mod-reward-shop** | Installed; intentionally disabled | ([GitHub][41]) |
| **mod-reward-played-time** | Installed; intentionally disabled | ([GitHub][40]) |

The server build, database import, database health, worldserver readiness, Phase 1-8 static contracts, and `git diff --check` have been verified as recorded in `PROGRESSION.md`. Interactive progression, dungeon, client, restart-recovery, PlayerBots, and multiplayer checks remain open.

ARAC and Worgoblin remain deep client/server modifications. The selected Worgoblin source is `Medviten/mod-worgoblin-high-elf`; the original `heyitsbench/mod-worgoblin` is no longer maintained.

## Current state

The five roadmap systems are installed or staged in the server checkout. Phase 7 prevents Mythic+, Dungeon Master, and Roguelike ownership from stacking with AutoBalance, Challenge Modes, or Echoes World Threat scaling. Phase 8 publishes guarded dungeon lifecycle events to Dream Path and stores per-character event claims and database-defined weekly rotations.

The Echoes client patch hash is `93d2d7cc27f77fcd143a30b81a6e69e5b1147b8fedc8d62d5377f925a96ba05a`. The Prestige/Draft client patch hash is `e4454b83aaae2600a824dd51bf04481d8ea66d86d94d5ca96f9b6378d35437af`. The server-side `AreaTable.dbc`, `CharBaseInfo.dbc`, and `CharTitles.dbc` changes are staged in the persistent client-data volume.

The current runtime is not a production-readiness claim. Standard and Draft Prestige, Echoes attunement, Dream Path objectives and rewards, Mythic+ runs, Dungeon Master runs, Roguelike transitions, restart recovery, bot behavior, and multiplayer behavior still require live testing.



[2]: https://github.com/ZhengPeiRu21/mod-individual-progression "GitHub - ZhengPeiRu21/mod-individual-progression: AzerothCore Individual Progression Module · GitHub"
[3]: https://github.com/azerothcore/mod-transmog "GitHub - azerothcore/mod-transmog: Plug&Play transmog module for AzerothCore, based on Rochet2 works · GitHub"
[4]: https://github.com/azerothcore/mod-autobalance "GitHub - azerothcore/mod-autobalance: Module for AzerothCore(MaNGOS -> TrinityCore -> SunwellCore) · GitHub"
[6]: https://github.com/NathanHandley/mod-ah-bot-plus "GitHub - NathanHandley/mod-ah-bot-plus: Modified version of the AHBot for AzerothCore · GitHub"
[7]: https://github.com/azerothcore/mod-ale "GitHub - azerothcore/mod-ale: AzerothCore Lua Engine · GitHub"
[8]: https://github.com/azerothcore/mod-aoe-loot "GitHub - azerothcore/mod-aoe-loot: Loot all bodies at once! · GitHub"
[9]: https://github.com/ZhengPeiRu21/mod-challenge-modes "GitHub - ZhengPeiRu21/mod-challenge-modes: Challenge Modes Module for AzerothCore · GitHub"
[10]: https://github.com/azerothcore/mod-account-achievements "GitHub - azerothcore/mod-account-achievements: Share your characters achievements to all on your account. · GitHub"
[11]: https://github.com/azerothcore/mod-account-mounts "GitHub - azerothcore/mod-account-mounts · GitHub"
[12]: https://github.com/pangolp/mod-mounts-on-account "GitHub - pangolp/mod-mounts-on-account: This module allows to obtain all the mounts learned by a character of the account, possibly in exchange for gold, although it is not yet decided. · GitHub"
[13]: https://github.com/azerothcore/mod-individual-xp "GitHub - azerothcore/mod-individual-xp · GitHub"
[14]: https://github.com/azerothcore/mod-dynamic-xp "GitHub - azerothcore/mod-dynamic-xp: Dynamic XP per level range module for 3.3.5a · GitHub"
[15]: https://github.com/azerothcore/mod-solocraft "GitHub - azerothcore/mod-solocraft: Solocraft module for AzerothCore · GitHub"
[16]: https://github.com/azerothcore/mod-solo-lfg "GitHub - azerothcore/mod-solo-lfg: Solo LFG Module for use on AzerothCore 3.3.5a · GitHub"
[17]: https://github.com/ZhengPeiRu21/mod-reagent-bank "GitHub - ZhengPeiRu21/mod-reagent-bank: Reagent Bank Module for AzerothCore · GitHub"
[18]: https://github.com/silviu20092/mod-improved-bank "GitHub - silviu20092/mod-improved-bank: Improved bank module for AzerothCore. · GitHub"
[19]: https://github.com/noisiver/mod-junk-to-gold "GitHub - noisiver/mod-junk-to-gold: Automatically sells looted gray items · GitHub"
[20]: https://github.com/azerothcore/mod-npc-services "GitHub - azerothcore/mod-npc-services: AzerothCore Module · GitHub"
[21]: https://github.com/azerothcore/mod-starter-guild "GitHub - azerothcore/mod-starter-guild: This module automatically joins new players to a guild of your choice on first login. · GitHub"
[22]: https://github.com/azerothcore/mod-guildhouse "GitHub - azerothcore/mod-guildhouse: Custom guild house for AzerothCore · GitHub"
[23]: https://github.com/azerothcore/mod-instance-reset "GitHub - azerothcore/mod-instance-reset: A instance-reset module for AzerothCore. · GitHub"
[24]: https://github.com/sogladev/mod-reset-raid-cooldowns "GitHub - sogladev/mod-reset-raid-cooldowns: AzerothCore custom module hat removes Sated and Exhaustion debuffs, and resets player cooldowns after raid encounters · GitHub"
[25]: https://github.com/BytesGalore/mod-no-hearthstone-cooldown "GitHub - BytesGalore/mod-no-hearthstone-cooldown: AzerothCore module that immediately skips the cooldown of the Hearthstone after use · GitHub"
[26]: https://github.com/abracadaniel22/mod-fly-anywhere "GitHub - abracadaniel22/mod-fly-anywhere: AzerothCore mod that allows players to fly in Eastern Kingdoms and Kalimdor as soon as they can fly in Outlands · GitHub"
[27]: https://github.com/azerothcore/mod-skip-dk-starting-area "GitHub - azerothcore/mod-skip-dk-starting-area · GitHub"
[28]: https://github.com/azerothcore/mod-learn-spells "GitHub - azerothcore/mod-learn-spells: AzerothCore module to automatically teaches new spells on levelup · GitHub"
[29]: https://github.com/azerothcore/mod-world-chat "GitHub - azerothcore/mod-world-chat: Global (world) chat. · GitHub"
[30]: https://github.com/azerothcore/mod-cfbg "GitHub - azerothcore/mod-cfbg: Cross-faction Battleground for AzerothCore · GitHub"
[31]: https://github.com/azerothcore/mod-bg-auto-queue "GitHub - azerothcore/mod-bg-auto-queue: Module to let players auto-queue battlegrounds · GitHub"
[32]: https://github.com/azerothcore/mod-duel-reset "GitHub - azerothcore/mod-duel-reset: Duel reset module for AzerothCore · GitHub"
[33]: https://github.com/azerothcore/mod-pvp-titles "GitHub - azerothcore/mod-pvp-titles: Display old PVP titles depending on honorable kills (starts at 50) · GitHub"
[34]: https://github.com/azerothcore/mod-gain-honor-guard "GitHub - azerothcore/mod-gain-honor-guard: Allow Guards and/or Elites to give Honor when killed. · GitHub"
[35]: https://github.com/azerothcore/mod-random-enchants "GitHub - azerothcore/mod-random-enchants: Random Enchantments for any Looted, Created or Quest Reward items · GitHub"
[36]: https://github.com/silviu20092/mod-mythic-plus "GitHub - silviu20092/mod-mythic-plus: Mythic Plus system for Azerothcore. · GitHub"
[37]: https://github.com/InstanceForge/mod-dungeon-master "GitHub - InstanceForge/mod-dungeon-master: Randomly generated dungeons for AzerothCore · GitHub"
[38]: https://github.com/silviu20092/mod-item-upgrade "GitHub - silviu20092/mod-item-upgrade: Individual item upgrades for AzerothCore. · GitHub"
[39]: https://github.com/azerothcore/mod-congrats-on-level "GitHub - azerothcore/mod-congrats-on-level: This module rewards players when they reach specific levels · GitHub"
[40]: https://github.com/azerothcore/mod-reward-played-time "GitHub - azerothcore/mod-reward-played-time: Reward System for Azerothcore · GitHub"
[41]: https://github.com/azerothcore/mod-reward-shop "GitHub - azerothcore/mod-reward-shop: Ingame shop for Azerothcore · GitHub"
[42]: https://github.com/azerothcore/mod-premium "GitHub - azerothcore/mod-premium: This is a module for AzerothCore that adds Premium account features to players. · GitHub"
[44]: https://github.com/Youpeoples/Black-Market-Auction-House "GitHub - Youpeoples/Black-Market-Auction-House: A faithful backport of the Mists of Pandaria Black Market Auction House assets and functionality to AzerothCore 3.3.5 using the Eluna Lua engine · GitHub"
[45]: https://github.com/Youpeoples/Prestige-and-Draft-Mode "GitHub - Youpeoples/Prestige-and-Draft-Mode: This is a minimally invasive mod for ACore 3.3.5 WoW Servers. Allowing for Prestige & Prestige Drafting options at max level. · GitHub"
[46]: https://github.com/topics/azerothcore-module?l=lua&o=asc&s=stars&utm_source=chatgpt.com "azerothcore-module · GitHub Topics · GitHub"
[48]: https://github.com/vibecoder99-cmd/echoes-of-the-worldsoul "GitHub - vibecoder99-cmd/echoes-of-the-worldsoul: A long-term solo/self-paced progression module for AzerothCore WotLK 3.3.5a with gear attunement, permanent stat absorption, World Threat, Visage cosmetics, and extension APIs. · GitHub"
[49]: https://github.com/DustinHendrickson/mod-player-bot-level-brackets "GitHub - DustinHendrickson/mod-player-bot-level-brackets: The Bot Level Brackets module for AzerothCore ensures an even spread of player bots across configurable level ranges (brackets). It periodically monitors bot levels and automatically adjusts them by transferring bots from overpopulated brackets to those with a deficit. · GitHub"
[50]: https://github.com/jrad7/mod-dungeon-clear?utm_source=chatgpt.com "GitHub - jrad7/mod-dungeon-clear: A module for AzerothCore's playerbots to help them clear dungeons. · GitHub"
[51]: https://github.com/heyitsbench/mod-arac "GitHub - heyitsbench/mod-arac: Module & patches - \"All Races All Classes (ARAC)\" · GitHub"
[52]: https://github.com/Medviten/mod-worgoblin-high-elf "GitHub - Medviten/mod-worgoblin-high-elf: Worgoblin playable-race integration for AzerothCore. · GitHub"
[53]: https://github.com/azerothcore/mod-npc-beastmaster "GitHub - azerothcore/mod-npc-beastmaster: An NPC that lets you tame beasts. · GitHub"
[54]: https://github.com/heyitsbench/mod-worgoblin "GitHub - heyitsbench/mod-worgoblin: Module for AzerothCore that adds Worgen and Goblin as playable races. · GitHub"
[55]: https://github.com/azerothcore/mod-anticheat "GitHub - azerothcore/mod-anticheat: Port of PassiveAnticheat to Azerothcore · GitHub"
[56]: https://github.com/azerothcore/mod-chat-transmitter "GitHub - azerothcore/mod-chat-transmitter · GitHub"
[57]: https://github.com/azerothcore/mod-better-item-reloading "GitHub - azerothcore/mod-better-item-reloading: BetterItemReloading is a C++ Azerothcore module which allows to reload items on the server side and as much as possible on the client side of WoW 3.3.5. · GitHub"
[58]: https://github.com/sogladev/mod-caio "GitHub - sogladev/mod-caio: CAIO enables sending Lua addons and data from server to client and vice versa, while providing C++ handler bindings for server-side logic · GitHub"
