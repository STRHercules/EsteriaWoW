# WoW Race Retroporter Design

## Goal

Create a reproducible automation project that acquires only the Retail race data needed for a selected race, converts the assets and customization model for WotLK 3.3.5a, and generates AzerothCore plus GlueXML integration outputs.

## Retail source decision

The project does **not** house a complete Retail client. The default source is an online Retail CDN/CASC backend configured by `sources/retail/build.yaml`.

```yaml
mode: online
product: wow
region: us
locale: enUS
build:
  version: auto
  build_key: auto
```

An optional `mode: local` points to an existing CASC installation without copying it into the repository.

## Source storage

Targeted raw inputs are cached under:

```text
sources/retail/db2/
sources/retail/races/<race>/
```

Disposable transfer/cache data belongs in `cache/casc/`. Raw source assets and cache data are ignored by Git and excluded from packages.

## Pipeline

1. `preflight` validates project, manifest, source mode, and optional local CASC.
2. `discover` resolves the actual Retail build and follows race/model/customization DB2 relationships.
3. `extract` downloads only required DB2/FileDataID dependencies.
4. `inventory` records build identity, hashes, and dependency closure.
5. `convert-model` converts modern character model assets for WotLK.
6. `convert-textures` stages/normalizes required textures.
7. `build-customization` flattens Retail customization into WotLK concepts.
8. `generate-dbc` produces target DBC record inputs.
9. `generate-acore-sql` produces AzerothCore creation data.
10. `generate-glue` produces character-creation integration fragments.
11. `validate` checks cross-file references and completeness.
12. `package` assembles validated derived outputs only.

`raceporter fetch <race>` runs stages 1 through 4. `raceporter build <race>` runs the full pipeline and resumes from saved state.

## Identity model

Each race stores both `retail_race_id` and `target_race_id`. Retail IDs are discovery identities. Target IDs are WotLK/AzerothCore identities constrained by the project race-mask policy.

## Safety

- Never mutate source caches or a local CASC installation.
- Never recursively fetch a full Retail product when dependency-targeted retrieval is possible.
- Never package `sources/`, `cache/`, or `tools/`.
- Never mix assets from different Retail builds in one race source snapshot.
- Never claim source acquisition succeeded until a complete inventory is written.
