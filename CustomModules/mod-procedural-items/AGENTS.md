# AGENTS.md

This repository is an AzerothCore WotLK 3.3.5a module for persistent procedural equipment.

## Source of truth

Read `README.md`, `STATUS.md`, `docs/RUNTIME_REGISTRY.md`, `docs/DATABASE_CONTRACT.md`, and the current design/plan under `docs/superpowers/` before changing architecture.

## Safety invariants

1. Never allocate an item entry outside a pre-registered client pool.
2. Never recycle an entry after allocation.
3. Never invent or guess `displayid`, spell IDs, socket bonus IDs, or other DBC-backed identifiers.
4. Pool static identity (`class`, `subclass`, `inventory_type`) must match client `Item.dbc` data.
5. No generated item may be delivered before canonical persistence succeeds.
6. Do not use `const_cast` to mutate AzerothCore `ObjectMgr` item stores.
7. Do not invoke a full `LoadItemTemplates()` reload per generated drop.
8. Generation for the same `(generation_version, seed, request)` must be deterministic.
9. If a compatible verified appearance does not exist, fail generation cleanly.
10. New core hooks must be kept minimal and handled according to AzerothCore's core license/contribution requirements.

## Development

Use C++20. Keep the pure generator under `src/core` free of AzerothCore dependencies so it can be tested without building the entire server.

Run:

```bash
./tools/run_core_tests.sh
python3 tools/validate_client_pool.py client/item_pool_ranges.csv
python3 tools/generate_client_pool_manifest.py client/item_pool_ranges.csv --output /tmp/item_pool_manifest.csv
```

Use tests first for generator behavior. Treat balance numbers in v0.1 as scaffolding, not finalized Esteria balance.
