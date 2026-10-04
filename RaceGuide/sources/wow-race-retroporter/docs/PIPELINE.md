# Pipeline

Earthen's Esteria integration uses `races/earthen.yaml`, Retail IDs 84/85 and target IDs 48/49. The operator
tool is `EsteriaWoW/tools/earthen_race_pack.py`: `acquire`, `portraits`, `prepare`, `stage`, followed by
`EsteriaWoW/tools/test_earthen_race_pack.py`. It adds only reachable source dependencies to the pinned
`sources/retail/races/earthen` cache, stages derived output in `G:\RetroPorterWork\earthen\integration`, and
merges into copies of the current Esteria client archives. Native/server compilation and installation
remain separate steps. The initial port retains ordinary player choices and ten face textures; BONE face
shape morphs exceed the static Wrath SKIN budget with complete accessories and remain unimplemented.

Every race build uses the same stable stage sequence:

| Stage | Purpose | Primary output |
|---|---|---|
| preflight | Validate race IDs, source profile, paths, and optional local CASC | report |
| discover | Resolve Retail build plus race/model/customization graph | discovery JSON |
| extract | Fetch required DB2/FileDataID dependencies only | `sources/retail/races/<race>` |
| inventory | Record source dependency closure, hashes, build identity | inventory JSON |
| convert-model | Produce WotLK-compatible model assets from source copies | `workspace/converted/<race>/models` |
| convert-textures | Produce/copy required textures | `workspace/converted/<race>/textures` |
| build-customization | Flatten Retail customization model | normalized JSON |
| generate-dbc | Produce WotLK DBC record inputs | `workspace/generated/<race>/dbc` |
| generate-acore-sql | Produce AzerothCore SQL | `workspace/generated/<race>/sql` |
| generate-glue | Produce character creation integration files | `workspace/generated/<race>/glue` |
| validate | Validate references/completeness | validation report |
| package | Assemble derived files only | `workspace/packages/<race>` |

## Fetch pipeline

`raceporter fetch <race>` runs only:

```text
preflight
  ↓
discover
  ↓
extract
  ↓
inventory
```

This creates the self-contained per-race source cache. A later `build` resumes from the saved stage state.

## Build identity

If the source profile uses `build.version: auto`, the discover stage must resolve and record the actual build before source data is considered complete. Resuming against a different build must not silently reuse stale stage state.

## State

Completed stages are recorded in `workspace/state/<race>.json` and skipped on resume. `--force` re-runs selected work, but source adapters should still prevent accidental build mixing.
