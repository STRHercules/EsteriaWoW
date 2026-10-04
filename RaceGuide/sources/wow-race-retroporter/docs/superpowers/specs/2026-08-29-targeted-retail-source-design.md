# Targeted Retail Source Architecture

## Requirement

Replace the original full-client-in-repository assumption with a source system that can fetch only the Retail DB2 and asset dependencies required for a selected playable race.

## Selected approach

Use a tracked source profile at `sources/retail/build.yaml` and two interchangeable source modes:

- `online`: default CDN/CASC-backed retrieval, no local Retail install required;
- `local`: optional read-only CASC installation path.

Both modes must eventually provide the same logical operations: resolve build, fetch DB2, resolve FileDataID, fetch FileDataID.

## Persistence

Durable raw inputs are per-race caches in `sources/retail/`. Temporary transfer data is in `cache/casc/`. Neither is package-safe or committed by default.

## CLI

`raceporter fetch <race>` is the source acquisition workflow and maps to `preflight`, `discover`, `extract`, and `inventory`.
