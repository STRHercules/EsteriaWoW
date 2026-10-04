# Changelog

## 0.2.0 - Source architecture revision

- Replaced the repository-local full Retail client assumption with a CDN-first Retail source profile.
- Added optional local CASC fallback through `sources/retail/build.yaml`.
- Added `sources/retail/db2/`, `sources/retail/races/`, and disposable `cache/casc/` paths.
- Added `raceporter fetch <race>` for the source-only `preflight -> discover -> extract -> inventory` workflow.
- Updated preflight and doctor so online mode does not require a local Retail installation.
- Excluded `sources/`, `cache/`, and `tools/` from package-safe paths.
- Expanded tests for source configuration, online/local preflight, fetch stages, and packaging safety.

## 0.1.0 - Initial scaffold

- Python pipeline scaffold and resumable stage state.
- Mag'har Orc reference manifest.
- AzerothCore/DBC/GlueXML documentation and conversion tool boundaries.
