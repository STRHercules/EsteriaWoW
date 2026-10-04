# AGENTS.md

Instructions for Codex and other coding agents working in this repository.

## Mission

Build and maintain a reproducible automation pipeline that fetches only the Retail World of Warcraft race data required for a requested race, retroports it to WotLK 3.3.5a formats, and generates AzerothCore/client integration outputs.

## Critical source architecture

A complete Retail client **does not live in this repository and is not required in the default workflow**.

The default Retail source profile is:

```text
sources/retail/build.yaml
mode: online
product: wow
region: us
locale: enUS
```

Online adapters should retrieve only required DB2/FileDataID dependencies and cache them under:

```text
sources/retail/db2/
sources/retail/races/<race>/
cache/casc/
```

`mode: local` is an optional offline fallback. `local_client_root` may point to a Retail CASC installation outside the repository.

## NEVER

- require a complete Retail installation when `mode: online` is configured;
- recursively download or copy the entire Retail product when targeted FileDataID retrieval is sufficient;
- patch, repair, update, or mutate a local Retail installation;
- commit raw Blizzard assets from `sources/` or CASC blocks from `cache/`;
- include `sources/`, `cache/`, or local tool binaries in generated race packages;
- overwrite a completed source cache without `--force` or an explicit reset policy;
- silently switch Retail builds after a race has been cached;
- invent DBC IDs, display IDs, spell IDs, race IDs, or customization mappings.

## ALWAYS

- load source settings from `sources/retail/build.yaml` through project configuration;
- distinguish `retail_race_id` from `target_race_id`;
- record the actual Retail build/build key in source manifests once resolved;
- preserve FileDataIDs, logical names when available, hashes, and dependency relationships in inventories;
- fetch only dependencies reachable from the selected race/model/customization graph;
- keep source assets immutable after a successful fetch; conversion happens under `workspace/`;
- make external tool calls reproducible and logged;
- stop with an actionable checkpoint when a third-party tool cannot be automated safely;
- make every pipeline stage independently resumable.

## Source data boundaries

Tracked and shareable:

```text
sources/retail/build.yaml
sources/retail/README.md
sources/retail/db2/README.md
sources/retail/races/README.md
```

Local and ignored:

```text
sources/retail/db2/<downloaded DB2s>
sources/retail/races/<race>/<raw source assets>
cache/casc/<temporary data>
```

Derived work belongs under `workspace/`.

## Development principles

1. Python orchestration should be small and testable.
2. Source acquisition and conversion tools belong behind adapters.
3. The online source backend and local CASC backend must expose the same logical fetch interface.
4. A source fetch is successful only when its dependency inventory is complete and pinned to a build.
5. Race-specific target behavior belongs in `races/*.yaml`.
6. Shared target race IDs belong in `config/race_ids.yaml`.
7. Retail DB2 discovery should follow relationships rather than filename guesses.
8. Never use a Retail race ID directly as an AzerothCore target ID without explicit mapping.

## Testing

Run:

```bash
pytest -q
python -m raceporter doctor
python -m raceporter fetch maghar_orc --dry-run
python -m raceporter plan maghar_orc
python -m raceporter build maghar_orc --dry-run
```

Tests must not require internet access, a Retail client, downloaded Blizzard assets, or installed third-party tools.

## Documentation responsibilities

If source behavior or paths change, update the matching docs in the same change:

- architecture: `ARCHITECTURE.md`
- operator workflow: `GUIDE.md`
- source contract: `docs/RETAIL-SOURCES.md`
- tool integration: `TOOLS.md`
- manifest schema: `docs/RACE-MANIFEST.md`
- Retail data graph: `docs/RETAIL-DB2.md`
- model conversion: `docs/MODEL-CONVERSION.md`
- pipeline stages: `docs/PIPELINE.md`
- packaging safety: `docs/PACKAGING.md`
