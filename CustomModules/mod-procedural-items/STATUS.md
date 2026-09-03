# Status

## Working in this scaffold

- Current AzerothCore module loader/world startup skeleton.
- C++20 deterministic PRNG.
- Deterministic role-aware starter stat generation.
- Verified-display-only appearance catalog contract.
- Non-overlapping, client-compatible permanent ID pools.
- SQL metadata schema and starter pool reservations.
- Client pool validator and manifest expander.
- Standalone C++ tests for deterministic generation, allocation exhaustion, and visual safety.

## Deliberately not active yet

- Live `ObjectMgr` runtime `ItemTemplate` insertion.
- Writing generated drafts into the full `item_template` schema.
- GM generation commands.
- Creature/quest/chest/crafting loot hooks.
- Weapon damage, armor, sockets, procs, suffixes, and affix budget tuning.
- Automatic DBC editing or MPQ packaging.

The next engineering milestone is the safe runtime registry core hook. The module already isolates that dependency behind `IRuntimeItemRegistry`.
