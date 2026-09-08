# mod-corpse-respawn

An AzerothCore module that spawns a player's ghost at their corpse after releasing spirit, with an optional graveyard marker on the minimap.

## Description

When enabled, players who die and click "Release Spirit" become a ghost at their corpse location instead of being teleported to the nearest graveyard.

The module can optionally show the spirit-healer marker on the minimap so players can still choose to run to the graveyard if they prefer.

## Installation

1. Clone or copy this module into your `azerothcore-wotlk/modules/` directory as `mod-corpse-respawn`.
2. Re-run CMake and rebuild the `worldserver` target.
3. Copy `conf/mod-corpse-respawn.conf.dist` to `mod-corpse-respawn.conf` and adjust settings as needed.

## Configuration

| Setting | Default | Description |
|---|---|---|
| `CorpseRespawn.Enable` | 1 | Spawn the ghost at the corpse after releasing spirit. |
| `CorpseRespawn.SendGraveyardMarker` | 1 | Show the nearest graveyard marker on the minimap. |

## Notes

- Battlegrounds and arenas are unaffected.
- Instances and open-world PvP are affected.
- The normal corpse-reclaim delay still applies.
