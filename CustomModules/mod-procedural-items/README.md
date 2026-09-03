# mod-procedural-items

AzerothCore WotLK 3.3.5a starter module for **persistent, client-safe procedural equipment**.

This scaffold is built around one rule: procedural loot is only useful if WoW still treats it like a real item. Generated items must have stable IDs, correct names/stats/tooltips, valid icons/models, and normal persistence through restart/trade/mail/AH flows.

## What v0.1 contains

- AzerothCore module loader + config/startup script.
- Deterministic C++20 generation core.
- Role-aware starter stat generation for Hunter, Melee, Caster, Healer, and Tank items.
- Permanent client-prepared ID pools keyed by static item identity.
- Verified-display-only appearance catalog that fails closed.
- World DB schema for ranges, display allow-list, and generated-item provenance.
- Python tools to validate/expand the client Item.dbc reservation manifest.
- Standalone core tests.
- Architecture, runtime-registry, database, task, and agent docs.

## Important: runtime generation boundary

This repo **does not pretend** AzerothCore currently gives a module a safe public API to insert a new `ItemTemplate` into the live `ObjectMgr` stores. v0.1 intentionally stops at that boundary. `src/core/RuntimeContracts.h` defines the seam; `docs/RUNTIME_REGISTRY.md` describes the tiny core extension to implement next.

Persisting a generated row alone makes it available on the next normal item-template load/restart. True create-and-use-immediately behavior needs the runtime registry milestone.

## Install as an AzerothCore module

Clone/copy this folder under your AzerothCore source tree:

```text
azerothcore-wotlk/
└── modules/
    └── mod-procedural-items/
```

Then reconfigure/rebuild AzerothCore normally. Copy/enable the generated module config as appropriate for your deployment and apply the world DB SQL under `data/sql/db-world/base/` through your normal module DB update flow.

For header hygiene during module testing, AzerothCore recommends compiling with precompiled headers disabled (`-DNOPCH=1`).

## Standalone tests

You can test the generator without compiling AzerothCore:

```bash
./tools/run_core_tests.sh
```

Client reservation safety:

```bash
python3 tools/validate_client_pool.py client/item_pool_ranges.csv
python3 tools/generate_client_pool_manifest.py \
  client/item_pool_ranges.csv \
  --output /tmp/item_pool_manifest.csv
```

## Client patch model

The starter ranges reserve entries beginning at `2,000,000`. Every reserved entry must be represented in Esteria's client-side `Item.dbc` with matching static identity. Server generation may then assign a persistent item definition to an unused prepared entry.

The module will never invent a display ID. Operators populate `mod_procedural_display_pool` only with IDs verified in the exact client `ItemDisplayInfo.dbc`. See `client/README.md`.

## Repository map

```text
src/core/                 Pure deterministic generator, no AzerothCore dependency
src/acore/                AzerothCore hooks/adapters
data/sql/db-world/base/   Module world DB schema
conf/                     Module config
client/                   Client Item.dbc reservation contract
tools/                    Validation/test tooling
tests/                    Standalone C++ tests
docs/                     Architecture and implementation notes
```

## Next milestone

Implement a small, tested AzerothCore core API that can register exactly one validated `ItemTemplate` into the live stores. Once that exists, the persistence mapper, `.pitem generate` command, and actual loot hook can all sit on top of the same transactional generation service.

## License

MIT for this module scaffold. Any required changes to AzerothCore core must follow AzerothCore's own licensing/contribution requirements.
