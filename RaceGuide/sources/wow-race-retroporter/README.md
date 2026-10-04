# WoW Race Retroporter

A Windows-first automation scaffold for turning modern World of Warcraft playable-race assets into a reproducible **WotLK 3.3.5a + AzerothCore** integration workspace.

The project follows two rules:

1. **Fetch only the Retail data a race actually needs.** A complete Retail client is not required by default.
2. **Automate what is reliably automatable and expose explicit, resumable checkpoints for conversion work that still needs specialist tools.**

## What this project is for

Use it to build race ports such as:

- Mag'har Orc
- Highmountain Tauren
- Kul Tiran
- Mechagnome
- Earthen
- Dracthyr
- other Retail/custom races that do not already have a clean 3.3.5a package

The reference implementation begins with **Mag'har Orc**, using Retail race ID `36` and a separately assigned WotLK/AzerothCore target race ID.

## Retail source strategy

The default source mode is **online**. The project is structured so a future Retail CDN/CASC adapter can resolve and download only the DB2 rows and FileDataIDs required for the requested race.

```text
Blizzard Retail CDN/CASC
        ↓
required Retail DB2 tables
        ↓
race/model/customization relationships
        ↓
required FileDataIDs only
        ↓
sources/retail/races/<race>/
```

No `retail/World of Warcraft/` directory is required.

If fully offline extraction is preferred, set `mode: local` in `sources/retail/build.yaml` and point `local_client_root` at an existing Retail CASC installation. That path may be outside this repository.

## Source cache layout

```text
sources/
└── retail/
    ├── build.yaml              # tracked source/build profile
    ├── db2/                    # targeted Retail DB2 cache, ignored
    └── races/                  # targeted per-race assets, ignored
        └── maghar_orc/
            ├── manifest.json
            ├── inventory.json
            ├── male/
            └── female/

cache/
└── casc/                       # disposable online CASC/CDN cache, ignored
```

Raw Retail assets remain local and are excluded from generated packages.

## Pipeline

```text
Retail online CDN/CASC OR optional local CASC
    ↓
preflight
    ↓
discover race/model/customization records
    ↓
extract only required DB2 + FileDataID dependencies
    ↓
inventory and cache per-race source assets
    ↓
convert model + textures
    ↓
flatten Retail customization for WotLK
    ↓
generate DBC records
    ↓
generate AzerothCore SQL
    ↓
generate GlueXML scaffolding
    ↓
validate
    ↓
package derived files
```

The source acquisition portion can be run independently:

```bash
raceporter fetch maghar_orc
```

Once a race source cache is complete, later build stages operate from the cached race data rather than depending on a full Retail installation.

## Quick start

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

raceporter doctor
raceporter fetch maghar_orc --dry-run
raceporter plan maghar_orc
raceporter build maghar_orc --dry-run
```

Configure the source profile in `sources/retail/build.yaml` and external tools in `config/tools.yaml`.

## Important commands

```text
raceporter doctor                 Validate source profile, repository paths, and tools
raceporter fetch <race>           Discover/cache only Retail source dependencies
raceporter fetch <race> --dry-run Show source-acquisition stages without downloading
raceporter plan <race>            Show the complete pipeline and saved stage state
raceporter build <race>           Run/resume the complete retroport pipeline
raceporter build <race> --force   Re-run completed stages
raceporter build <race> --dry-run Show intended work without converters
raceporter status <race>          Show saved stage state
raceporter reset <race>           Clear saved state for that race
```

## Repository map

```text
config/      project/tool/race-ID policy
races/       one YAML manifest per target race
sources/     targeted Retail source profile and local extraction caches
cache/       disposable CDN/CASC caches
tools/       local external utilities, binaries ignored
src/         Python orchestration
workspace/   extracted/converted/generated/state/log output
templates/   SQL/Glue/DBC output templates
docs/        technical/reference documentation
```

See `ARCHITECTURE.md` for the full design.

## What the scaffold does not do yet

This scaffold defines the source architecture, CLI contracts, state model, safety rules, and adapter boundaries. The real Retail CDN/FileDataID resolver and M2 conversion integrations are intentionally explicit implementation checkpoints rather than fake one-button behavior.

The intended next source milestone is:

```text
raceporter fetch maghar_orc
    ↓
connect to selected Retail build
    ↓
resolve race 36
    ↓
resolve ChrModel/customization dependencies
    ↓
download only required DB2/M2/SKIN/SKEL/ANIM/BLP files
    ↓
write sources/retail/races/maghar_orc/
```

See `ROADMAP.md` for the implementation sequence.

## Asset and licensing note

The automation code is MIT licensed. World of Warcraft assets and third-party tools remain subject to their respective owners/licenses. Raw Retail source assets under `sources/` and temporary CASC data under `cache/` are intentionally ignored by Git and excluded from generated packages.

## Deeper documentation

- `docs/RETAIL-SOURCES.md` - online/local Retail source contract
- `docs/RETAIL-DB2.md` - race/customization discovery tables
- `docs/PIPELINE.md` - stage-by-stage data flow
- `docs/RACE-MANIFEST.md` - race configuration format
- `docs/MODEL-CONVERSION.md` - model retroport boundaries
- `docs/CUSTOMIZATION.md` - Retail-to-WotLK customization strategy
- `docs/DBC-MAPPING.md` - WotLK DBC surface
- `docs/AZEROTHCORE.md` - server integration rules
- `docs/GLUEXML.md` - character-creation integration
- `docs/TOOL-ADAPTERS.md` - external tool contract
- `docs/PACKAGING.md` - asset/package safety policy
