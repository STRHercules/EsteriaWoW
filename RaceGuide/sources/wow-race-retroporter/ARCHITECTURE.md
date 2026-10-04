# Architecture

## Goal

WoW Race Retroporter is a staged orchestration project for converting a selected modern Retail playable race into WotLK 3.3.5a/AzerothCore-compatible assets and data without keeping or scanning an entire Retail client by default.

## Design principles

- **CDN-first source acquisition.** Default source mode is `online`.
- **Targeted dependency closure.** Fetch only DB2 rows and FileDataIDs required by the selected race.
- **Local CASC fallback.** Offline users can point at an existing Retail CASC installation.
- **Immutable source cache.** Raw fetched assets live under `sources/`; conversion works on copies under `workspace/`.
- **Config-driven target identity.** Retail IDs and WotLK target IDs are separate.
- **Resumable stages.** Work can stop at any external-tool boundary and resume later.
- **Safe packaging.** `sources/`, `cache/`, and `tools/` are never package inputs.

## Source configuration

`config/project.yaml` owns repository-relative paths. `sources/retail/build.yaml` owns Retail source selection:

```yaml
mode: online
product: wow
region: us
locale: enUS
build:
  version: auto
  build_key: auto
local_client_root:
```

When online mode resolves `auto`, the fetch implementation must write the actual build identity into the race source manifest so later stages remain reproducible.

For offline use:

```yaml
mode: local
local_client_root: D:/Games/World of Warcraft
```

The local directory is an input only. It is not copied wholesale into the repository.

## Core data flow

```text
sources/retail/build.yaml
          │
          ▼
   Retail source backend
     ┌────┴────┐
     │         │
  online     local
 CDN/CASC   CASC install
     │         │
     └────┬────┘
          ▼
      preflight
          ▼
       discover
          │
          ├── ChrRaces
          ├── ChrRaceXChrModel
          ├── ChrModel
          └── customization graph
          ▼
        extract
          │
          ├── targeted DB2s
          └── required FileDataIDs only
          ▼
       inventory
          ▼
sources/retail/races/<race>/
          ▼
     convert-model
          ▼
    convert-textures
          ▼
 build-customization
          ▼
      generate-dbc
          ▼
 generate-acore-sql
          ▼
    generate-glue
          ▼
       validate
          ▼
       package
```

`raceporter fetch <race>` runs the source half through `inventory`. `raceporter build <race>` runs the full pipeline and reuses completed source stages.

## Source backend interface

The future backend should expose equivalent logical operations regardless of where bytes come from:

```text
resolve_build()
fetch_db2(table)
resolve_file(file_data_id)
fetch_file(file_data_id)
```

The orchestration layer should not care whether the backend uses WoW.Export, CASCLib, TACTSharp, or another compatible implementation.

## Dependency discovery

Discovery begins with `retail_race_id` from the race manifest and follows Retail DB2 relationships to:

1. race identity;
2. male/female character model records;
3. customization options and choices;
4. geosets, skinned models, materials, display overrides, bone sets, and conditional models;
5. referenced model/texture/skeleton/animation FileDataIDs.

The output is a normalized discovery document. Extraction consumes that document rather than guessing file names.

## Source cache

```text
sources/retail/
├── build.yaml
├── db2/
└── races/
    └── <race>/
        ├── manifest.json
        ├── inventory.json
        ├── male/
        └── female/
```

The manifest should capture at minimum product, region, locale, actual Retail build, build key, Retail race ID, target race ID, fetch timestamp, and dependency inventory version.

## Conversion workspace

Converters never operate on `sources/` in place.

```text
workspace/
├── extracted/      # normalized copies/staging
├── converted/      # WotLK-compatible models/textures
├── generated/      # DBC/SQL/Glue outputs
├── packages/       # validated deliverables
├── state/          # resumable stage state
└── logs/           # adapter command/output logs
```

## Target race identity

Retail race IDs can exceed WotLK's practical 32-bit race-mask range. `races/*.yaml` therefore carries both:

```text
retail_race_id -> source discovery identity
target_race_id -> WotLK/AzerothCore identity
```

For example, Mag'har Orc uses Retail ID `36` and Esteria target RaceID `45`.

## Safety boundaries

Package collection rejects all paths under:

```text
sources/
cache/
tools/
```

Only validated derived outputs from `workspace/converted/` and `workspace/generated/` should become package inputs.
