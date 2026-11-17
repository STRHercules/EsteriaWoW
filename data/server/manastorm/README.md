# Recovered Manastorm item dataset

`items-20261117.sql.gz` supplies **134,042 actual item templates**, compressed to
about 4.4 MB. These include cache containers, reconstructed cache gear pools,
materials, currencies and every item referenced by the module's authored reward
snapshot. That snapshot's Greedy Demon loot pool alone names 126,325 items.

This package was recovered on 2026-11-17 by reading only `item_template` from the
preserved `coa_live_world` reference database. The original full-table export
contains 573,145 templates; its SHA-256 is recorded in `manifest.json`.
The package contains no accounts, characters, balances or player history.
It is not claimed to be a byte-identical copy of the original September dump.

Selection comes from:

- The module's authored `ManastormWorldDBExport-RUNTHIS.sql`: item columns in cache
  brackets/unlocks, Greedy Demon, material pools, reward rules, potential rewards
  and Treasure Keeper rules.
- Leaf items resolved by the existing Black Temple, Molten Core and Classic cache
  reconstruction migrations, including Normal, Heroic, Mythic, ranked and
  Ascended pools.
- The recovered cache container catalogue.

The package preserves actual stats, spells, descriptions, display IDs and other
item fields. The existing module cache ownership and label migrations were
applied before export; this is recorded in the manifest. It uses explicit-column
upserts for selected IDs, preserving unrelated item rows and references. It
**does update an existing item with a selected ID**; do not import it into an
unrelated live realm without reviewing those collisions.

## Verify and unpack

From the repository root:

```powershell
python tools/server_install/unpack_manastorm_items.py
python tools/server_install/unpack_manastorm_items.py --output manastorm-items.sql
```

The second command creates a new file and refuses to overwrite an existing one.
Both compressed and decompressed SHA-256 hashes are checked. Import that SQL
into a backed-up or disposable world database **after the stock world schema and
before Manastorm's module migrations**. It includes widening guards for long
item descriptions and unsigned 32-bit ItemLimitCategory IDs. The corresponding
core reader must also use `Get<uint32>()`; the repository includes that change.

The Docker server image verifies and expands this package into Manastorm's module
foundation SQL. The baseline excludes Manastorm, so its importer does not apply
these rows. Do not copy them into `data/sql/base/` or replace the whole
world database. The package contains prerequisites, not the module migrations:
those must still run in their supported order.

## Verification performed

Imported this subset alone into a new database using Esteria's stock item schema.
The package's schema guards applied successfully. The unchanged module migrations
then passed Black Temple and Molten Core reconstruction plus all Classic cache
dataset checks (SQL 15, 20, 48, 49, 50, 53-55, 57-64). No preflight was removed or
expected count changed. Re-running the existing cache migrations also passed.

The item table was exported from a working CoA reference installation, not inferred
from appearance placeholders or converted from the partial public website export.
For provenance context, the CoA source is at
`https://github.com/STRHercules/azerothcore-wotlk-coa`; the module carries its own
catalogue and reconstruction evidence under `docs/`.

The complete repository SQL sequence has also passed from empty MySQL 8.4
databases with Manastorm enabled, including both authored snapshots and the later
Esteria level-80/endgame migrations. Compiled native-mode startup also passes:
296 segments load and the shared backend initializes. Its migrations include
three core persistence tables, endgame depth/group scaling and 21 additional
private route actors needed by a clean progression world. The terminal Esteria
compatibility migration disables 173 reward-pool entries whose final item
definition was removed or changed quality; it preserves item stats and the
remaining authored tiers and weights. Runtime validation is unchanged.

Still separate: complete creature/spell/display dependency validation, custom
terrain and client gameplay acceptance. Existing content/model warnings remain.
