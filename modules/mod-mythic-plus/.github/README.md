# Mythic Plus system for AzerothCore

Adds the possibility to transform configured dungeons into Mythic Plus dungeons with selectable
levels, affixes, timers, rewards, and completion tracking.

## Source

- Repository: https://github.com/silviu20092/mod-mythic-plus
- Revision: `e2a487d358c1c1c562d686f53a3e269b2cf1b8c5`

## Installation

1. Keep this directory at `modules/mod-mythic-plus`.
2. Re-run CMake and rebuild AzerothCore.
3. Copy `conf/mod_mythic_plus.conf.dist` into the generated module configuration directory.
4. Let the database importer apply the SQL files, or apply them manually.
5. Spawn the Mythic Plus NPC with `.npc add 200005`.

## Runtime

Players choose a Mythic Plus level and affixes through NPC `200005`. A group leader uses the
Mythic Keystone inside a capable dungeon. After the activation delay, the timer starts; beating
the time limit grants the configured rewards. The capable-dungeon, level, affix, reward, map-scale,
and spell-override tables define the available content.

Use `.mythic info` for the current run and `.mythic reload` to reload reloadable Mythic Plus data.

## Configuration

The module is disabled or enabled with `MythicPlus.Enable`. `MythicPlus.Penalty.OnDeath`,
`MythicPlus.KeystoneBuyTimer`, and `MythicPlus.DropKeystoneOnDungeonComplete` control the main
timer, purchase, and completion behavior. See `conf/mod_mythic_plus.conf.dist` for defaults.
