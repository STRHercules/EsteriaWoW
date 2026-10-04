# Retail Source Contract

## Default mode: online

The project should obtain Retail race data through a targeted online CASC/CDN source backend. A full Retail installation is not a project prerequisite.

Configuration lives in:

```text
sources/retail/build.yaml
```

Example:

```yaml
mode: online
product: wow
region: us
locale: enUS
build:
  version: auto
  build_key: auto
```

`auto` is a discovery policy, not a reproducibility guarantee. Once a fetch begins, the backend should resolve the actual build identity and record it in the per-race source manifest.

## Optional mode: local

For offline work:

```yaml
mode: local
product: wow
region: us
locale: enUS
local_client_root: D:/Games/World of Warcraft
```

The local source should contain CASC data, normally `Data/` plus build/config metadata. The project reads the source and extracts only selected files. It does not copy or modify the full installation.

## Why partial `data.NNN` archives are not the project model

CASC storage is content-addressed. One race's model, animations, textures, and customization assets can be spread across many storage containers alongside unrelated data. Keeping selected large CASC archives is therefore a poor substitute for extracting the exact FileDataIDs needed by a race.

The project stores logical source assets instead:

```text
sources/retail/db2/
sources/retail/races/<race>/
```

## Per-race source manifest

A successful fetch should write `sources/retail/races/<race>/manifest.json` containing at least:

- source product, region, locale;
- resolved Retail version/build key;
- Retail race ID and WotLK target race ID;
- DB2 tables/records used for discovery;
- dependency inventory version;
- requested and resolved FileDataIDs;
- hashes/sizes for downloaded source assets;
- backend/tool versions.

## Immutability

Once inventory completes, treat the source cache as immutable input. Model conversion, texture modification, and DBC generation happen under `workspace/`.

A build change should invalidate or create a new source snapshot instead of mixing files from multiple Retail builds.
