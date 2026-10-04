# RetroPorter

Repeatable tooling and documentation for retroporting modern World of Warcraft player-race assets into Esteria's 3.3.5a client.

Completed art-port targets: **Mag'har Orc**, **Highmountain Tauren**, **Mechagnome**, **Earthen**, **Haranir**, and **Skyborne**.

## Current machine defaults

- Retail WoW CASC root: `G:\Blizzard\World of Warcraft`
- Retail product: `wow`
- Current verified Retail build: `12.1.0.69933` (`WOW-69933patch12.1.0_Retail`)
- Forever beta CASC root: `D:\Blizzard\World of Warcraft`
- Forever beta product: `wow_classic_beta`
- Forever beta build: `1.60.1.70009` (`WOW-70009patch1.60.1_ForeverBeta`)
- Esteria 3.3.5a dev client: `G:\3.3.5a - Dev`
- External working area for extracted Blizzard data: `G:\RetroPorterWork`
- Converter: <https://github.com/Bar3b0n3s/Converter>

`wotlkconv` expects the **World of Warcraft parent directory**, not `_retail_`, because `.build.info` and `Data` are stored at the parent level.

## Repository policy

This repository contains tooling, small identifier manifests, and documentation. Blizzard binaries, extracted client databases, generated reports, and converted client assets are deliberately excluded from Git and should remain in `G:\RetroPorterWork` or another local working directory.

## Setup

Python 3.10+ is required. Install the converter and this repository:

```powershell
python -m pip install --user "git+https://github.com/Bar3b0n3s/Converter.git"
python -m pip install -e "R:\Users\Zach\Documents\GitHub\RetroPorter"
```

Fetch the community listfile, WoWDBDefs, and TACT keys through Converter:

```powershell
python -c "from wotlkconv.fetch import fetch_listfile, fetch_definitions, fetch_keys; print(fetch_listfile()); print(fetch_definitions()); print(fetch_keys())"
```

Then verify the environment:

```powershell
python -m retroporter doctor
```

## Race workflow

The same commands are now race-aware. For example:

```powershell
python -m retroporter extract-db2 --race haranir
python -m retroporter discover --race haranir
python -m retroporter plan-assets --race haranir
python -m retroporter convert-assets --race haranir --dry-run
python -m retroporter convert-assets --race haranir
```

Discovery writes a machine-readable JSON report under the configured work directory. All six current targets have completed with zero failed asset conversions. Canonical patch staging roots are namespaced under `G:\RetroPorterWork\<race>\output\patch-root\custom\<race>\...`.

For a source outside the installed Retail `wow` product, extraction and conversion can override the CASC source explicitly. Skyborne uses the installed Forever beta:

```powershell
python -m retroporter extract-db2 --race skyborne --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
python -m retroporter discover --race skyborne
python -m retroporter plan-assets --race skyborne
python -m retroporter convert-assets --race skyborne --dry-run --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
python -m retroporter convert-assets --race skyborne --source-root "D:\Blizzard\World of Warcraft" --source-product wow_classic_beta
```

The converted art is not yet a playable race by itself. The next phase is generating and merging the required 3.3.5a character DBC rows against Esteria's current DBC templates.

See:

- `docs/PIPELINE.md` for the complete architecture.
- `docs/MAGHAR.md` for the Mag'har findings.
- `docs/HIGHMOUNTAIN.md` for the Highmountain Tauren findings.
- `docs/MECHAGNOME.md` for the Mechagnome base-body and collection-model findings.
- `docs/EARTHEN.md` for the Earthen dual-race-row, collection-model, and conversion findings.
- `docs/HARANIR.md` for the Haranir dual-faction, collection-model, and conversion findings.
- `docs/VULPERA.md` for the Vulpera source graph, complete art stage, texture layouts, and verified CASC recovery.
- `docs/SKYBORNE.md` for the completed World of Warcraft: Forever Skyborne findings.
- `docs/SKYBORNE_PREP.md` for the earlier source-preparation notes.
- `docs/DBC_STRATEGY.md` for how modern `ChrCustomization*` data will be flattened into 3.3.5a DBCs.
- `docs/HANDOFF.md` for the exact resume point and next actions.
- `docs/TROUBLESHOOTING.md` for known Converter/CASC issues and safe recovery steps.
