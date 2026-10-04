# Esteria appearance expansion analysis brief

The package supplies four complete appearance DBC tables and a Classic `patch-Z.MPQ` with appearance assets. Esteria's current client has the same four DBC paths in both the root and enUS Z archives, so both archives are winning inputs and both must receive the same merged tables. The live server tables are in the `esteriawow_ac-client-data` Docker volume mounted at `/azerothcore/env/dist/data/dbc`; repository `DBCs/` files are not authoritative.

The merge is additive. Existing rows are never replaced. Donor rows that reuse an existing selection key are retained only when their effective bytes are already represented; different donor bytes are reported and left out. Donor row IDs are not trusted: new IDs are allocated above the complete existing ID set. String-bearing rows are rebuilt with offsets into the merged pool. Blood Elf (10) rows are cloned to High Elf (13) after the same collision/key checks, while any existing High Elf rows remain the base.

The existing Playerbot factory already includes `RACE_HIGHELF` and selects face/hair/facial values from `sCharSectionsStore`; no C++ or SQL change is required. Existing bots are not rewritten. The optional package refresher is deliberately not run because it mutates character appearance rows and would require a separate character-database backup and opt-in.
